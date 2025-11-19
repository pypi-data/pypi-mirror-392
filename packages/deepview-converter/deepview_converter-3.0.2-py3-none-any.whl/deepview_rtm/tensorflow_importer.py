# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import logging
import math

import deepview.rt as rt
import networkx as nx
import numpy as np
from deepview_rtm.utils import gen_ssd_output, pad_kernel, setup_logger
import deepview_rtm.calc_shapes as shape_help
from tensorflow.core.framework import graph_pb2


class TensorflowImporter:
    """
    Iterates through a Tensorflow graph def (from a frozen .pb file)
    and generates a networkx DiGraph representing the computation graph
     of the model.
    """

    # Constructor
    def __init__(self,
                 tf_graph,
                 default_shape=None,
                 user_ops=[],
                 subgraph_names=[]):
        """
        Constructor
        :param tf_graph: TF graph def
        :param default_shape: Fallback shape if no shape is specified
        :param mode: Pad mode
        """
        self.user_ops = []
        for user in user_ops:
            if hasattr(user, 'TensorflowImporter'):
                user_importer = user.TensorflowImporter(self)
                if hasattr(user_importer, 'process_graph'):
                    tf_graph = user_importer.process_graph(tf_graph)
                self.user_ops.append(user_importer)

        self.default_shape = default_shape
        self.node_alias = {}
        self.nxgraph = nx.DiGraph()
        self.log_path = setup_logger()
        self.read_ending = '/read'

        self.input_nodes = []
        self.output_nodes = []
        if subgraph_names:
            self.input_nodes = subgraph_names[0]
            self.output_nodes = subgraph_names[1]
            import tensorflow as tf
            # Handle Tensorflow 2.0
            if float(tf.__version__[:2]) >= 2.0:
                import tensorflow.compat.v1 as tf
            """
            Here we replace the nodes we're going to override as inputs with
            placeholders so that any unused nodes that are inputs to them are
            automatically stripped out by extract_sub_graph().
            """
            inputs_replaced_graph_def = graph_pb2.GraphDef()
            for node in tf_graph.node:
                if node.name in self.input_nodes:
                    placeholder_node = tf.NodeDef()
                    placeholder_node.op = "Placeholder"
                    placeholder_node.name = node.name
                    placeholder_node.attr["dtype"].CopyFrom(tf.AttrValue(
                        type=tf.float32.as_datatype_enum))
                    if node.op == "Reshape":
                        placeholder_node.input.extend([node.input[1]])
                    inputs_replaced_graph_def.node.extend([placeholder_node])
                else:
                    inputs_replaced_graph_def.node.extend([node])
            from deepview_rtm.tensorflow import extract_sub_graph
            tf_graph = extract_sub_graph(inputs_replaced_graph_def, self.output_nodes)

        self.graph = tf_graph

    def get_input_nodes(self):
        """
        Finds the input node(s) for the computation graph
        :return: Dict where keys are old input(s) names
         and values are new input(s) names
        """
        input_nodes = []
        for tfnode in self.graph.node:
            if hasattr(tfnode, 'op') and tfnode.op == 'Placeholder':
                input_nodes.append(tfnode.name)

        return input_nodes

    def get_output_nodes(self):
        """
        Finds the output node(s) for the computation graph
        and changes their names to 'output' or 'output_i'
        for the i'th output (if more than one)
        :return: Dict where keys are old output(s) names
         and values are new output(s) names
        """
        # Unable to use single loop for case of out of order nodes
        # (MobileNetV2 from Model Zoo)
        output_nodes_prelim = []
        output_list = []
        for tfnode in self.graph.node:
            if hasattr(tfnode, 'op'):
                output_nodes_prelim.append(tfnode.name)
                if tfnode.op == 'Split' or tfnode.op == 'SplitV':
                    # Handle Split being an output as Tensorflow only counts it as a single output
                    input_name = next(self.nxgraph.predecessors(tfnode.name))
                    for output in self.nxgraph.successors(input_name):
                        if output != tfnode.name:
                            output_nodes_prelim.append(output)
        for tfnode in self.graph.node:
            if hasattr(tfnode, 'op'):
                for input_val in tfnode.input:
                    if self.gen_name(input_val) in output_nodes_prelim:
                        output_nodes_prelim.remove(self.gen_name(input_val))
                    elif input_val in output_nodes_prelim:
                        output_nodes_prelim.remove(input_val)

        output_nodes = output_nodes_prelim[:]
        for node in output_nodes_prelim:
            if node not in self.nxgraph.nodes:
                output_nodes.remove(node)
            if node == "TFLite_Detection_PostProcess":
                output_nodes = [tfnode.input[1], 'ssd_post_process_corner_concat']

        for i in range(len(output_nodes)):
            # handle identity output
            if self.nxgraph.nodes[output_nodes[i]]['op'] == 'idn':
                node = self.nxgraph.nodes[output_nodes[i]]
                node['op'] = 'reshape'
                node['shape'] = node['output_shape']
                node['input'] = node['x']
                del node['x']
            output_list.append(output_nodes[i])

        return output_list

    def run(self):
        """
        Start point to generate nx graph
        :return: nxgraph representing TF model
        """
        return self.create_nodes()

    def create_nodes(self):
        """
        Loop through each node in graph and import to nxgraph
        :return: nxgraph representing TF model
        """
        for tfnode in self.graph.node:
            if hasattr(tfnode, 'op'):
                node_op = tfnode.op
                node_fun = self.import_unknown

                for user in self.user_ops:
                    if hasattr(user, 'import_' + node_op):
                        node_fun = getattr(user, 'import_' + node_op)
                        break
                if node_fun == self.import_unknown and hasattr(self, 'import_' + node_op):
                    node_fun = getattr(self, 'import_' + node_op)
                node_fun(tfnode)

        input_nodes, output_nodes = self.refactor_graph()
        print("Model imported successfully")
        return self.nxgraph, input_nodes, output_nodes

    def relabel_inputs(self):
        """
        Replace all slashes in node's inputs with underscores
        :return:
        """
        for node_name in self.nxgraph:
            node = self.nxgraph.nodes[node_name]

            for key, val in node.items():
                if isinstance(val, str) and key != 'op':
                    node[key] = node[key].replace('/', '_')

            if node['op'] == 'concat':
                for i in range(len(node['values'])):
                    node['values'][i] = node['values'][i].replace('/', '_')

            if node['op'] == 'cudnn_gru':
                for key, value in node.items():
                    if isinstance(value, str):
                        node[key] = value.replace('/', '_')

    def remove_preds(self, node_name):
        pred = self.nxgraph.predecessors(node_name)
        remove_list = [node_name]
        for pred_name in pred:
            if self.nxgraph.out_degree(pred_name) == 1:
                remove_list += self.remove_preds(pred_name)

        return remove_list

    def remove_identities(self, output_nodes):
        """
        Cleaning up identity nodes and trim hanging nodes
        :return:
        """
        remove_nodes = []
        relabelled_nodes = {}
        for node_name in self.nxgraph:
            if node_name[-5:] == self.read_ending or \
                    self.nxgraph.nodes[node_name]['op'] == 'idn':
                remove_nodes.append(node_name)
                removed_node = self.nxgraph.nodes[node_name]
                if removed_node['op'] == 'idn' and node_name in output_nodes:
                    relabelled_nodes[removed_node['x']] = node_name
            elif self.nxgraph.out_degree(node_name) == 0 \
                    and node_name not in output_nodes:
                remove_nodes += self.remove_preds(node_name)
        self.nxgraph.remove_nodes_from(remove_nodes)
        nx.relabel_nodes(self.nxgraph, relabelled_nodes, copy=False)

    def refactor_graph(self):
        self.refactor_upsamples()
        # Remove any isolated nodes
        self.nxgraph.remove_nodes_from(list(nx.isolates(self.nxgraph)))
        input_nodes = self.get_input_nodes() if not self.input_nodes else self.input_nodes
        output_nodes = self.get_output_nodes() if not self.output_nodes else self.output_nodes
        # Replace all slashes in node names with underscore to avoid
        # issues with modelrunner - not needed with latest modelrunner
        #nx.relabel_nodes(
            #self.nxgraph, lambda x: x.replace('/', '_'), copy=False)
        self.remove_identities(output_nodes)
        # nx graph's relabel nodes doesn't relabel inputs to nodes,
        # must manually do this - not needed with latest modelrunner
        #self.relabel_inputs()
        return input_nodes, output_nodes

    def refactor_upsamples(self):
        nodes_to_remove = []
        for node_name in self.nxgraph.nodes:
            node_data = self.nxgraph.nodes[node_name]
            if node_data['op'] == 'reshape' and len(node_data['output_shape']) > 4:
                mul_name = next(self.nxgraph.successors(node_name))
                mul_node = self.nxgraph.nodes[mul_name]
                assert mul_node['op'] == 'mul', "Invalid number of dimensions in reshape (greater than 4)"
                # Replace reshape and mul with concat
                upsample_input = node_data['input']
                first_concat_shape = self.nxgraph.nodes[upsample_input]['output_shape'][:]
                first_concat_shape[3] *= 2

                # Replace reshape
                node_data.clear()
                node_data['op'] = 'concat'
                node_data['axis'] = 3
                node_data['values'] = [upsample_input, upsample_input]
                node_data['output_shape'] = first_concat_shape

                # Replace mul
                second_concat_shape = first_concat_shape[:]
                second_concat_shape[2] *= 2
                nodes_to_remove.append(mul_node['y'])
                mul_node.clear()
                mul_node['op'] = 'concat'
                mul_node['axis'] = 2
                mul_node['values'] = [node_name, node_name]
                mul_node['output_shape'] = second_concat_shape
        self.nxgraph.remove_nodes_from(nodes_to_remove)

    """
    HELPER FUNCTIONS
    """

    @staticmethod
    def calc_hw_shape(in_shape, filter_shape, dilations,
                      strides, padding_algo):
        """
        Calculates shape for 2D Convolution
        :param in_shape: Input shape's height and width as list (Must be 2D)
        :param filter_shape: Filter shape's height and width as list (Must be 2D)
        :param dilations: Dilations for conv of length 2
        :param strides: Strides for conv of length 2
        :param padding_algo: Algorithm for padding
        :return: tuple containing output shape as list and padding as list of tuples
        """
        assert len(in_shape) == 2 and len(
            filter_shape) == 2, \
            "Input shape and filter shape must be 2D tensors"
        output_shape = 2 * [0]
        if not dilations:
            dilations = [1, 1]

        padding_shape = []  # Stores how much padding on each side

        if padding_algo == b'SAME':
            for i in range(len(in_shape)):
                output_shape[i] = math.ceil(in_shape[i] / strides[i])
                fd = (filter_shape[i] - 1) * dilations[i] + 1
                t = (output_shape[i] - 1) * strides[i] + fd - in_shape[i]
                if t > 0:
                    p = math.floor(t / 2)
                    q = math.ceil(t / 2)
                    padding_shape.append((p, q))
                else:
                    padding_shape.append((0, 0))
        else:
            for i in range(len(in_shape)):
                padding_shape.append((0, 0))
                fd = (filter_shape[i] - 1) * dilations[i] + 1
                output_shape[i] = math.floor(
                    (in_shape[i] - fd) / strides[i]) + 1

        return output_shape, padding_shape

    def get_pad_input(self, pad_node):
        """
        Helper function to fuse padding when there is an explicit pad node
        :param pad_node: input pad node to conv
        :return: head padding, tail padding,
                 pad node's input shape, and pad node's input name
        """
        head = pad_node['head']
        tail = pad_node['tail']
        new_input_name = pad_node['input']
        new_output_shape = self.nxgraph.nodes[new_input_name]['output_shape'][:]
        return head, tail, new_output_shape, new_input_name

    @staticmethod
    def get_tfnode_input(tfnode, idx):
        """
        Ensure index for input exits
        :param tfnode: Node to get input
        :param idx: Which input
        :return: input name
        """
        assert idx < len(tfnode.input), \
            "Bad index for accessing Tensorflow node " + \
            tfnode.name + "op input" + str(idx)
        return tfnode.input[idx]

    def get_node_by_name(self, node_name):
        """
        Get node from graph by name
        :param node_name:
        :return: Node from nxgraph
        """
        if node_name[-5:] == self.read_ending:
            node_name = node_name[:-5]

        if node_name in self.node_alias:
            node_name = self.node_alias[node_name]

        assert node_name in self.nxgraph, \
            "Graph doesn't contain required node: " + node_name
        return self.nxgraph.nodes[node_name]

    def get_node_from_graph(self, tfnode, idx):
        """
        Gets node from graph recursively
        :param tfnode: node to get
        :param idx: which input to get
        :return: input node
        """
        node_name = self.get_tfnode_input(tfnode, idx)

        if ':' in node_name:
            node_name = node_name[0:node_name.find(':')]
        if node_name[-5:] == self.read_ending:
            node_name = node_name[:-5]

        # Handles cases where nodes are out of order within Protocol Buffer
        try:
            node = self.get_node_by_name(node_name)
        except AssertionError:
            for new_node in self.graph.node:
                if new_node.name == node_name:
                    if hasattr(new_node, 'op'):
                        node_op = new_node.op
                        if hasattr(self, "import_" + node_op):
                            func = getattr(self, "import_" + node_op)
                            func(new_node)
                        else:
                            self.import_unknown(new_node)
                    break
            node = self.get_node_by_name(node_name)

        if node['op'] == 'idn':  # Pass through identity node's input
            node = self.get_node_by_name(node['x'])
        return node

    def get_numpy_from_tf_tensor(self, tf_tensor):
        """
        Gets tensor content, data type, and shape
        :param tf_tensor: Tensor to get info from
        :return: tensor content, np datatype, and tensor shape as list
        """

        tf_dtype = np.int32
        if tf_tensor.dtype == 1:
            tf_dtype = np.float32
        tf_shape = self.tensor_shape_to_list(tf_tensor.tensor_shape)

        if not tf_shape:
            assert False, "tf_shape is None!"

        np_tensor = np.reshape(
            np.frombuffer(tf_tensor.tensor_content, tf_dtype).astype(tf_dtype),
            tf_shape)

        return np_tensor, tf_dtype, tf_shape

    @staticmethod
    def tensor_shape_to_list(shapes):
        """
        :param shapes: Tensor shape from TF graph
        :return: Tensor shape as Python list
        """
        return [dim.size for dim in shapes.dim]

    """
    Find output shape values for different operations, primarily used for stack ops
    in import_Reshape
    """

    def get_value_stack(self, tfnode):
        values = []
        value_name = '_values' if tfnode['op'] == 'stack' else 'values'
        for i in range(len(tfnode[value_name])):
            if 'input' in tfnode[value_name][i]:
                node = self.get_node_by_name(tfnode[value_name][i]['input'])
                node_op = node['op']
                func = getattr(self, "get_value_" + node_op)
                values.append(func(node))
            else:
                values.append(self.nxgraph.nodes[tfnode[value_name][i]]['np_tensor'])

        return np.stack(values, tfnode['axis'])

    def get_value_constant(self, tfnode):
        return tfnode['np_tensor']

    def get_value_reshape(self, tfnode):
        node = self.get_node_by_name(tfnode['input'])
        node_op = node['op']
        func = getattr(self, "get_value_" + node_op)
        return func(node)

    def get_value_shape_of(self, tfnode):
        return tfnode['output_shape']

    def get_value_slice(self, tfnode):
        node = self.get_node_by_name(tfnode['input'])
        node_op = node['op']
        func = getattr(self, "get_value_" + node_op)
        init_val = func(node)
        output_val = init_val[:]
        axes = tfnode['axes']
        for i in range(len(axes)):
            if i in axes:
                if i == 0:
                    output_val = output_val[
                                 int(tfnode['begin'][axes.index(i)]):int(
                                     tfnode['end'][axes.index(i)])]
                elif i == 1:
                    output_val = output_val[:][
                                 int(tfnode['begin'][axes.index(i)]):int(
                                     tfnode['end'][axes.index(i)])]
                elif i == 2:
                    output_val = output_val[:][:][
                                 int(tfnode['begin'][axes.index(i)]):int(
                                     tfnode['end'][axes.index(i)])]
                elif i == 3:
                    output_val = output_val[:][:][:][
                                 int(tfnode['begin'][axes.index(i)]):int(
                                     tfnode['end'][axes.index(i)])]
                elif i == 4:
                    output_val = output_val[:][:][:][:][
                                 int(tfnode['begin'][axes.index(i)]):int(
                                     tfnode['end'][axes.index(i)])]
                else:
                    raise ValueError(
                        "Axes goes too high, currently not handled")

        return output_val

    def get_value_sub(self, tfnode):
        x_node = self.get_node_by_name(tfnode['x'])
        x_op = x_node['op']
        func_x = getattr(self, "get_value_" + x_op)
        x_val = func_x(x_node)

        y_node = self.get_node_by_name(tfnode['y'])
        y_op = y_node['op']
        func_y = getattr(self, "get_value_" + y_op)
        y_val = func_y(y_node)

        return np.subtract(x_val, y_val)

    def gen_name(self, name):
        """
        Cleans names from Tensorflow
        :param name: Original name
        :return: Cleaned name
        """
        if name in self.node_alias:
            name = self.node_alias[name]
        if name[-5:] == self.read_ending:
            name = name[:-5]

        if ':' in name:
            name = name[:name.index(':')]

        if name.startswith('^'):
            name = name.replace('^', '')

        # Pass through identity's input name
        if name in self.nxgraph.nodes and \
                self.nxgraph.nodes[name]['op'] == 'idn':
            name = self.nxgraph.nodes[name]['x']

        return name

    """
    IMPORT FUNCTIONS
    """

    def import_Abs(self, tfnode):
        self.import_unary(tfnode, 'abs')

    def import_Add(self, tfnode):
        self.import_binary(tfnode, 'add')

    def import_AddV2(self, tfnode):
        self.import_binary(tfnode, 'add')

    def import_AddN(self, tfnode):
        tf_inputs = {'x': 0, 'y': 1}
        node_name = tfnode.name
        op = 'add'

        x_name = self.gen_name(tfnode.input[tf_inputs['x']])
        for i in range(1, len(tfnode.input)):
            y_name = self.gen_name(tfnode.input[tf_inputs['y']])
            try:
                node_x = self.nxgraph.nodes[x_name]
            except KeyError:
                node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
            try:
                node_y = self.nxgraph.nodes[y_name]
            except KeyError:
                node_y = self.get_node_from_graph(tfnode, tf_inputs['y'])
            if i == len(tfnode.input) - 1:
                add_name = node_name
            else:
                add_name = node_name + "_pair_" + str(i)

            output_shape = shape_help.calc_binary_output(node_x, node_y)
            self.nxgraph.add_node(add_name,
                                  op=op,
                                  x=x_name,
                                  y=y_name,
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(x_name, add_name)
            self.nxgraph.add_edge(y_name, add_name)
            x_name = add_name

    def import_AvgPool(self, tfnode):
        self.import_pool(tfnode, 'avg_pool')

    def import_BiasAdd(self, tfnode):
        self.import_Add(tfnode)

    def import_binary(self, tfnode, op_name):
        tf_inputs = {'x': 0, 'y': 1}
        node_name = tfnode.name

        node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
        node_y = self.get_node_from_graph(tfnode, tf_inputs['y'])

        x_name = self.gen_name(tfnode.input[tf_inputs['x']])
        y_name = self.gen_name(tfnode.input[tf_inputs['y']])
        try:
            output_shape = shape_help.calc_binary_output(node_x, node_y)
        except (AssertionError, KeyError):
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(x_name, node_name)
            self.nxgraph.add_edge(y_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        self.nxgraph.add_node(node_name,
                              op=op_name,
                              x=x_name,
                              y=y_name,
                              output_shape=output_shape,
                              datatype=np.dtype('float32'),
                              data_format=tfnode.attr['data_format'])
        self.nxgraph.add_edge(x_name, node_name)
        self.nxgraph.add_edge(y_name, node_name)

    def import_ConcatV2(self, tfnode):
        tf_inputs = {}
        op = 'concat'
        node_name = tfnode.name

        nodes = []
        node_names = []
        for i in range(len(tfnode.input) - 1):  # Get each concat input
            self.get_node_from_graph(tfnode, i)
            nodes.append(self.get_node_from_graph(tfnode, i))
            node_names.append(self.gen_name(tfnode.input[i]))
            tf_inputs['value_' + str(i)] = i

        node_axis = self.get_node_from_graph(tfnode, len(tfnode.input) - 1)
        tf_inputs['value_' + str(len(tfnode.input) - 1)
                  ] = len(tfnode.input) - 1
        axis = int(node_axis['np_tensor'][0])

        # Shape propagation error checking
        try:
            for i in range(len(nodes[0]['output_shape'])):
                if i != axis:
                    assert all(
                        elem['output_shape'][i] == nodes[0]['output_shape'][i]
                        for elem in nodes), \
                        "The shapes of values[i] for all dimensions other " \
                        "than axis must be the same"

            assert all(
                len(elem['output_shape']) == len(nodes[0]['output_shape']) for
                elem in nodes), \
                "The rank of values[i] must all be the same"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            for i in range(len(tfnode.input) - 1):
                self.nxgraph.add_edge(tfnode.input[i], node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        self.nxgraph.remove_node(
            tfnode.input[len(tfnode.input) - 1])  # Clean axis node

        # Calculate output shape
        output_shape = shape_help.concat_shape(nodes, axis)

        self.nxgraph.add_node(node_name,
                              op=op,
                              axis=axis,
                              values=node_names,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        for i in range(len(tfnode.input) - 1):
            self.nxgraph.add_edge(self.gen_name(tfnode.input[i]), node_name)

    def import_Const(self, tfnode):
        node_name = self.gen_name(tfnode.name)
        op = 'constant'

        if tfnode.attr['value'].tensor.tensor_content == b'':
            shape = self.tensor_shape_to_list(
                tfnode.attr['value'].tensor.tensor_shape)

            if tfnode.attr['value'].tensor.dtype == 3:
                if tfnode.attr['value'].tensor.int_val:
                    value = np.array([
                        float(tfnode.attr['value'].tensor.int_val[i])
                        for i in
                        range(len(tfnode.attr['value'].tensor.int_val))]
                    ).astype(np.int32)
                    np_dtype = np.int32
                else:
                    print("empty const: " + node_name)
                    return
            elif tfnode.attr['value'].tensor.dtype == 1:
                if tfnode.attr['value'].tensor.float_val:
                    value = np.array([
                        float(tfnode.attr['value'].tensor.float_val[i])
                        for i in
                        range(len(tfnode.attr['value'].tensor.float_val))]
                    ).astype(np.float32)
                    np_dtype = np.float32
                else:
                    print("empty const: " + node_name)
                    return
            else:
                raise ValueError(
                    "Type " + str(tfnode.attr['value'].tensor.dtype) +
                    " is not currently supported")

            if np.prod(value.shape) != np.prod(
                    shape):  # Handle single value tensor
                value = np.full(shape, value[0], dtype=np_dtype)
            if shape:
                value = value.reshape(shape)
            self.nxgraph.add_node(node_name,
                                  op=op,
                                  np_tensor=value,
                                  shape=shape,
                                  datatype=np_dtype,
                                  output_shape=shape)
        else:
            np_tensor, np_dtype, shape = self.get_numpy_from_tf_tensor(
                tfnode.attr['value'].tensor)
            self.nxgraph.add_node(node_name,
                                  op=op,
                                  shape=shape,
                                  datatype=np_dtype,
                                  np_tensor=np_tensor,
                                  output_shape=shape)

    def import_Conv2D(self, tfnode):
        node_name = tfnode.name
        op = 'conv'
        tf_inputs = {'input': 0, 'filter': 1}
        padding = tfnode.attr['padding'].s

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        node_filter = self.get_node_from_graph(tfnode, tf_inputs['filter'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        filter_name = self.gen_name(tfnode.input[tf_inputs['filter']])

        strides = tfnode.attr['strides'].list.i
        strides = [int(v) for v in strides][1:3]
        dilations = tfnode.attr['dilations'].list.i
        dilations = [int(v) for v in dilations][1:3]

        if not dilations:
            dilations = [1, 1]

        # Calculate output shape
        in_shape = node_input['output_shape'][:]
        filter_shape = node_filter['output_shape']
        try:
            output_shape, padding = self.calc_hw_shape(in_shape[1:3],
                                                       filter_shape[:2],
                                                       dilations,
                                                       strides,
                                                       padding)
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            self.nxgraph.add_edge(filter_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape = [in_shape[0]] + output_shape + [filter_shape[3]]
        head = [0] + [padding[0][0]] + [padding[1][0]] + [0]
        tail = [0] + [padding[0][1]] + [padding[1][1]] + [0]
        assert (node_filter['output_shape'][2] == node_input['output_shape'][3] or
                node_filter['output_shape'][2] == 1
                and node_input['output_shape'][3] == node_filter['output_shape'][3]), \
            "DeepView does not support grouped convolutions " \
            "that are not depthwise."

        # Workaround for dilations other than one
        if any(dilation != 1 for dilation in dilations):
            node_filter['np_tensor'] = pad_kernel(node_filter['np_tensor'],
                                                  dilations[0],
                                                  dilations[1])
            node_filter['output_shape'] = node_filter['shape'] = node_filter['np_tensor'].shape

        padded = False
        for i in range(len(head)):
            if head[i] != 0 or tail[i] != 0:
                padded = True
                break

        if not padded and node_input['op'] == 'pad':
            padded = True
            head, tail, pad_out_shape, input_name = self.get_pad_input(node_input)

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              filter=filter_name,
                              stride=strides,
                              dilation=dilations,
                              head=head,
                              tail=tail,
                              groups=1,
                              bias=0.0,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)
        self.nxgraph.add_edge(filter_name, node_name)

    def import_Cos(self, tfnode):
        self.import_unary(tfnode, 'cos')

    def import_CudnnRNN(self, tfnode):
        assert tfnode.attr['rnn_mode'].s.decode('ascii') == 'gru', \
            "CudnnRNN import only supports GRU"
        tf_inputs = {'input': 0, 'h': 1, 'mem_blob': 3}
        node_name = tfnode.name
        op = 'cudnn_gru'
        from .cudnn_weights_converter import GRUWeightsConverter

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_blob = self.get_node_from_graph(tfnode, tf_inputs['mem_blob'])
        blob_name = self.gen_name(tfnode.input[tf_inputs['mem_blob']])
        in_units = node_input['output_shape'][2]
        sqrt_val = math.sqrt(9 * in_units * in_units + 36 * in_units +
                             36 + 12 * node_blob['output_shape'][0]) / 6
        b_val = -0.5 * in_units - 1
        num_units = int(b_val + sqrt_val)

        try:
            node_h = self.get_node_from_graph(tfnode, tf_inputs['h'])
            if node_h['op'] == 'constant':
                node_h['op'] = 'variable'
            h_name = self.gen_name(tfnode.input[tf_inputs['h']])
        except Exception:
            h_name = node_name + '_h'
            node_shape = [1, 1, num_units]
            np_tensor = np.full(node_shape, 0.0, dtype=np.float32)
            self.nxgraph.add_node(h_name,
                                  op='variable',
                                  shape=node_shape,
                                  np_tensor=np_tensor,
                                  datatype=np.dtype('float32'),
                                  output_shape=node_shape)

        blob_tensor = node_blob['np_tensor']
        gru_weights_conv = GRUWeightsConverter(in_units, num_units)
        gru_weights = gru_weights_conv.convert_cudnn_memblob_to_tf(
            blob_tensor, num_units, in_units)
        output_shape = node_input['output_shape'][:2] + [num_units]

        self.nxgraph.remove_node(blob_name)

        variable_nodes = {}
        for key, val in gru_weights.items():
            self.nxgraph.add_node(node_name + '_' + key.lower(),
                                  op='constant',
                                  label=node_name + '/' + key,
                                  shape=list(val.shape),
                                  datatype=val.dtype,
                                  np_tensor=val,
                                  output_shape=list(val.shape))
            variable_nodes[key.lower()] = node_name + '_' + key.lower()
        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              h=h_name,
                              w_ir=variable_nodes['w_ir'],
                              b_ir=variable_nodes['b_ir'],
                              w_h=variable_nodes['w_h'],
                              b_wh=variable_nodes['b_wh'],
                              r_h=variable_nodes['r_h'],
                              b_rh=variable_nodes['b_rh'],
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)
        self.nxgraph.add_edge(h_name, node_name)
        for name in variable_nodes.values():
            self.nxgraph.add_edge(name, node_name)

    def import_DepthwiseConv2dNative(self, tfnode):
        node_name = tfnode.name
        op = 'conv'
        tf_inputs = {'input': 0, 'filter': 1}
        data_format = tfnode.attr['data_format'].s.decode('ascii')
        padding = tfnode.attr['padding'].s

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        node_filter = self.get_node_from_graph(tfnode, tf_inputs['filter'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        filter_name = self.gen_name(tfnode.input[tf_inputs['filter']])
        groups = node_input['output_shape'][data_format.index('C')]
        strides = tfnode.attr['strides'].list.i
        strides = [int(v) for v in strides][1:3]
        dilations = tfnode.attr['dilations'].list.i
        dilations = [int(v) for v in dilations][1:3]

        if not dilations:
            dilations = [1,1]

        # Calculate output shape
        in_shape = node_input['output_shape']
        filter_shape = node_filter['shape']
        try:
            output_shape, padding = self.calc_hw_shape(in_shape[1:3],
                                                       filter_shape[:2],
                                                       dilations,
                                                       strides,
                                                       padding)
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            self.nxgraph.add_edge(filter_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape = [in_shape[0]] + output_shape + \
                       [filter_shape[2] * filter_shape[3]]
        assert groups == 1 or (groups != 1 and output_shape[3] == groups), \
            "DeepView does not support grouped convolutions " \
            "that are not depthwise."

        head = [0] + [padding[0][0]] + [padding[1][0]] + [0]
        tail = [0] + [padding[0][1]] + [padding[1][1]] + [0]

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              filter=filter_name,
                              stride=strides,
                              dilation=dilations,
                              head=head,
                              tail=tail,
                              groups=groups,
                              bias=0.0,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)
        self.nxgraph.add_edge(filter_name, node_name)

    def import_Div(self, tfnode):
        self.import_unary(tfnode, 'div')

    def import_Elu(self, tfnode):
        self.import_unary(tfnode, 'elu')

    def import_Exp(self, tfnode):
        self.import_unary(tfnode, 'exp')

    def import_ExpandDims(self, tfnode):
        tf_inputs = {'input': 0}
        node_name = tfnode.name
        op = 'reshape'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        output_shape = node_input['output_shape'][:]
        axis = int(self.get_node_from_graph(tfnode, 1)['np_tensor'][0])

        # Check axis is valid
        if not (-1 - len(output_shape) <= axis <= len(output_shape)):
            print("Invalid axis in Expand Dims")
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape.insert(axis, 1)

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              shape=output_shape,
                              output_shape=output_shape,
                              datatype=np.dtype('float32'),
                              maintain_format=True)
        self.nxgraph.add_edge(input_name, node_name)

    def import_Fill(self, tfnode):
        tf_inputs = {'dims': 0, 'value': 1}
        node_name = self.gen_name(tfnode.name)
        op = 'constant'

        node_dims = self.get_node_from_graph(tfnode, tf_inputs['dims'])
        dims_name = self.gen_name(tfnode.input[tf_inputs['dims']])
        node_value = self.get_node_from_graph(tfnode, tf_inputs['value'])
        value_name = self.gen_name(tfnode.input[tf_inputs['value']])

        # Check input shapes
        try:
            assert not node_value['output_shape'] or node_value[
                'output_shape'] == [1], \
                "Fill value must be a scalar"
            assert np.array(node_dims['output_shape']).ndim == 1, \
                "Fill dims must be 1D"
        except AssertionError:
            self.nxgraph.add_node(node_name, op=op)
            self.nxgraph.add_edge(dims_name, node_name)
            self.nxgraph.add_edge(value_name, node_name)

        # Get dims tensor values
        output_shape = []
        for val in node_dims['_values']:
            func = getattr(self, "get_value_" + val['op'])
            output_shape.append(int(func(val)[0]))

        # Generate a constant tensor filled with value
        np_tensor = np.full(
            output_shape, node_value['np_tensor'][0], dtype=np.float32)

        # Recursively remove predecessor nodes of fill
        def remove_nodes(node_name, nodes_to_remove):
            pred = self.nxgraph.predecessors(node_name)
            for node in pred:
                nodes_to_remove.append(node)
                nodes_to_remove += remove_nodes(node, nodes_to_remove)

            return nodes_to_remove

        remove = remove_nodes(node_name, [])
        self.nxgraph.remove_nodes_from(remove)

        self.nxgraph.add_node(node_name,
                              op=op,
                              output_shape=output_shape,
                              shape=output_shape,
                              datatype=node_value['dtype'],
                              np_tensor=np_tensor)

    def import_Fully_connected(self, tfnode):
        tf_inputs = {'input': 0, 'weights': 1, 'bias': 2}
        node_name = tfnode.name

        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        # Flatten if input node has rank greater than 2
        if len(node_input['output_shape']) > 2:
            shape = [1, np.prod(node_input['output_shape'])]
            reshape_name = node_name + '_reshape'
            self.nxgraph.add_node(reshape_name,
                                  op='reshape',
                                  input=input_name,
                                  shape=shape,
                                  output_shape=shape,
                                  datatype=np.dtype('float32'),
                                  maintain_format=False)
            self.nxgraph.add_edge(input_name, reshape_name)
            input_name = reshape_name

        weights_name = self.gen_name(tfnode.input[tf_inputs['weights']])
        node_weights = self.get_node_from_graph(tfnode, tf_inputs['weights'])
        node_weights['output_shape'] = node_weights['shape'] = \
            [node_weights['shape'][i] for i in [1, 0]]
        node_weights['np_tensor'] = np.transpose(node_weights['np_tensor'])

        bias_name = self.gen_name(tfnode.input[tf_inputs['bias']])
        self.get_node_from_graph(tfnode, tf_inputs['bias'])

        # Add fully connected as matmul and bias add
        # Matmul
        output_shape = shape_help.fully_connected_shape(node_input, node_weights)

        matmul_name = node_name + '_mul'
        self.nxgraph.add_node(matmul_name,
                              op='matmul',
                              A=input_name,
                              B=weights_name,
                              transposeA=False,
                              transposeB=False,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, matmul_name)
        self.nxgraph.add_edge(weights_name, matmul_name)

        # Get cast options
        activation = tfnode.attr['activation_fn'].lower()
        if activation != 'none':
            activation_node_name = node_name
            node_name = node_name + '_pre_act'

        # Bias add
        self.nxgraph.add_node(node_name,
                              op='add',
                              x=matmul_name,
                              y=bias_name,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(matmul_name, node_name)
        self.nxgraph.add_edge(bias_name, node_name)

        # Handle fused activation
        if activation != 'none':
            self.nxgraph.add_node(activation_node_name,
                                  op=activation,
                                  x=node_name,
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(node_name, activation_node_name)

    def import_FusedBatchNormV3(self, tfnode):
        self.import_FusedBatchNorm(tfnode)

    def import_FusedBatchNorm(self, tfnode):
        tf_inputs = {'input': 0, 'scale': 1,
                     'offset': 2, 'mean': 3, 'variance': 4}
        node_name = tfnode.name
        op = 'batch_normalization'
        data_format = tfnode.attr['data_format'].s

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        # Not keeping references to nodes as they are unused,
        # but must ensure they exist in graph
        self.get_node_from_graph(tfnode, tf_inputs['scale'])
        scale_name = self.gen_name(tfnode.input[tf_inputs['scale']])

        self.get_node_from_graph(tfnode, tf_inputs['offset'])
        offset_name = self.gen_name(tfnode.input[tf_inputs['offset']])

        self.get_node_from_graph(tfnode, tf_inputs['mean'])
        mean_name = self.gen_name(tfnode.input[tf_inputs['mean']])

        self.get_node_from_graph(tfnode, tf_inputs['variance'])
        variance_name = self.gen_name(tfnode.input[tf_inputs['variance']])

        epsilon = tfnode.attr['epsilon'].f
        eps_name = node_name + '_eps'
        # Make epsilon node
        self.nxgraph.add_node(eps_name,
                              op='constant',
                              shape=[1],
                              datatype=np.dtype('float32'),
                              np_tensor=np.asarray([epsilon]),
                              output_shape=[1])
        output_shape = node_input['output_shape'][:]

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              mean=mean_name,
                              variance=variance_name,
                              offset=offset_name,
                              scale=scale_name,
                              epsilon=eps_name,
                              output_shape=output_shape,
                              datatype=np.dtype('float32'),
                              data_format=data_format)
        self.nxgraph.add_edge(eps_name, node_name)
        for tf_input in tfnode.input:
            self.nxgraph.add_edge(self.gen_name(tf_input), node_name)

    def import_IdentityN(self, tfnode):
        self.import_Identity(tfnode)

    def import_Identity(self, tfnode):
        node_name = tfnode.name
        if node_name[-5:] == self.read_ending:
            node_name = node_name[:-5]
        if node_name == tfnode.input[0]:
            return
        else:
            tf_inputs = {'x': 0}
            op = 'idn'

            node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
            x_name = self.gen_name(tfnode.input[tf_inputs['x']])
            output_shape = node_x['output_shape'][:]

            self.nxgraph.add_node(
                node_name, op=op, x=x_name, datatype=np.dtype('float32'), output_shape=output_shape)
            self.nxgraph.add_edge(x_name, node_name)

    def import_Leaky_relu(self, tfnode):
        self.import_unary(tfnode, 'leaky_relu')

    def import_LeakyRelu(self, tfnode):
        self.import_unary(tfnode, 'leaky_relu')

    def import_Log(self, tfnode):
        self.import_unary(tfnode, 'log')

    def import_Log_softmax(self, tfnode):
        node_name = tfnode.name
        # log(softmax(input))
        self.import_Softmax(tfnode)
        output_shape = self.get_node_by_name(node_name)['output_shape'][:]

        self.nxgraph.add_node(node_name + '_log',
                              op='log',
                              x=node_name,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(node_name, node_name + '_log')

    def import_MatMul(self, tfnode):
        tf_inputs = {'A': 0, 'B': 1}
        node_name = tfnode.name
        op = 'matmul'

        node_a = self.get_node_from_graph(tfnode, tf_inputs['A'])
        a_name = self.gen_name(tfnode.input[tf_inputs['A']])
        node_b = self.get_node_from_graph(tfnode, tf_inputs['B'])
        b_name = self.gen_name(tfnode.input[tf_inputs['B']])
        tr_a = tfnode.attr['transpose_a'].b
        tr_b = tfnode.attr['transpose_b'].b

        if tr_b and node_b['op'] == 'constant':
            node_b['np_tensor'] = np.transpose(node_b['np_tensor'], [1, 0])
            node_b['output_shape'] = [node_b['output_shape'][i]
                                      for i in [1, 0]]
            node_b['shape'] = node_b['output_shape']
            tr_b = False

        try:
            assert len(node_a['output_shape']) >= 2 and len(
                node_b['output_shape']) >= 2
            if tr_a and tr_b:
                assert node_a['output_shape'][0] == node_b['output_shape'][1]
            elif tr_a and not tr_b:
                assert node_a['output_shape'][0] == node_b['output_shape'][0]
            elif tr_b and not tr_a:
                assert node_a['output_shape'][1] == node_b['output_shape'][1]
            else:
                assert node_a['output_shape'][1] == node_b['output_shape'][0]
        except AssertionError:
            print("node_a shape" + str(node_a['output_shape']),
                  "node_b shape" + str(node_b['output_shape']))
            print(tfnode.attr['transpose_a'].b)
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(a_name, node_name)
            self.nxgraph.add_edge(b_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        a_shape = node_a['output_shape'][:]
        if tr_a:
            a_shape.reverse()

        b_shape = node_b['output_shape'][:]
        if tr_b:
            b_shape.reverse()

        output_shape = []
        for i in a_shape[0:-1]:
            output_shape.append(i)
        for i in b_shape[len(a_shape) - 1:]:
            output_shape.append(i)

        self.nxgraph.add_node(node_name,
                              op=op,
                              A=a_name,
                              B=b_name,
                              transposeA=tr_a,
                              transposeB=tr_b,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(a_name, node_name)
        self.nxgraph.add_edge(b_name, node_name)

    def import_Max(self, operator):
        self.import_reduce(operator, 'max_reduce')

    def import_MaxPool(self, tfnode):
        self.import_pool(tfnode, 'max_pool')

    def import_MaxPoolWithArgmax(self, tfnode):
        tf_inputs = {'input': 0}
        node_name = tfnode.name
        op = 'avg_pool'

        padding = tfnode.attr['padding'].s
        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        sizes = tfnode.attr['ksize'].list.i
        sizes = [int(v) for v in sizes]
        strides = tfnode.attr['strides'].list.i
        strides = [int(v) for v in strides]
        dilations = [1, 1, 1, 1]

        if len(node_input['output_shape']) != 4:
            print("Input to AvgPool is not 4D")
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        # Calculate output shape
        in_shape = node_input['output_shape'][:]
        out_shape, padding_shape = self.calc_hw_shape(in_shape[1:3],
                                                      sizes[1:3],
                                                      dilations[1:3],
                                                      strides[1:3],
                                                      padding)

        output_shape = [in_shape[0]] + out_shape + [in_shape[3]]
        padding_shape = [(0, 0)] + padding_shape + [(0, 0)]

        head = []
        tail = []

        for pad in padding_shape:
            head.append(int(pad[0]))
            tail.append(int(pad[1]))

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              size=sizes,
                              stride=strides,
                              dilation=dilations,
                              head=head,
                              tail=tail,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)

    def import_Mean(self, tfnode):
        self.import_reduce(tfnode, 'mean_reduce')

    def import_Min(self, tfnode):
        self.import_reduce(tfnode, 'min_reduce')

    def import_Mul(self, tfnode):
        self.import_binary(tfnode, 'mul')

    def import_Neg(self, tfnode):
        self.import_unary(tfnode, 'neg')

    def import_Pack(self, tfnode):
        tf_inputs = {}
        node_name = self.gen_name(tfnode.name)

        nodes = []
        node_names = []
        for i in range(len(tfnode.input)):
            node_val = self.get_node_from_graph(tfnode, i)
            nodes.append(node_val)
            node_names.append(self.gen_name(tfnode.input[i]))
            tf_inputs['value_' + str(i)] = i

        axis = tfnode.attr['axis'].i

        # Shape propagation error checking
        try:
            assert all(
                len(elem['output_shape']) == len(nodes[0]['output_shape']) or
                (len(elem['output_shape']) == 0 and len(
                    nodes[0]['output_shape']) == 1) or
                (len(elem['output_shape']) == 1 and len(
                    nodes[0]['output_shape']) == 0)
                for elem in nodes), \
                "The rank of values[i] must all be the same"
            input_rank = len(nodes[0]['output_shape'])
            assert -(input_rank + 1) <= axis < input_rank + \
                   1, "Invalid axis for pack"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            for input_name in tfnode.input:
                self.nxgraph.add_edge(self.gen_name(input_name), node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        # Stack/Pack is just a concatenate along a new axis
        output_shape = nodes[0]['output_shape'][:]
        if len(output_shape) < 4:
            if not output_shape:
                output_shape = [1]
            output_shape.insert(axis, 1)

            # Reshape to add a new dimension to each node
            reshaped_node_names = []
            id_count = 1
            for input_node_name, node_info in zip(node_names, nodes):
                reshape_name = input_node_name + "_reshaped"
                if reshaped_node_names and reshaped_node_names[
                    -1] == reshape_name:  # Handle packing same node multiple times (resnet_ssd)
                    reshape_name += str(id_count)
                    id_count += 1
                self.nxgraph.add_node(reshape_name,
                                      op='reshape',
                                      input=input_node_name,
                                      shape=output_shape,
                                      output_shape=output_shape,
                                      datatype=np.dtype('float32'),
                                      maintain_format=False)
                self.nxgraph.add_edge(input_node_name, reshape_name)
                reshaped_node_names.append(reshape_name)

            # Concatenate along the new dimension
            concat_output_shape = output_shape[:]
            concat_output_shape[axis] += tfnode.attr["N"].i - 1
        else:
            concat_output_shape = output_shape[:]
            concat_output_shape[axis] *= tfnode.attr["N"].i

        self.nxgraph.add_node(node_name,
                              op='concat',
                              axis=axis,
                              values=node_names,
                              datatype=np.dtype('float32'),
                              output_shape=concat_output_shape)
        for input_name in tfnode.input:
            self.nxgraph.add_edge(self.gen_name(input_name), node_name)

    def import_Pad(self, tfnode):
        tf_inputs = {'input': 0, 'pads': 1}
        node_name = tfnode.name
        op = 'pad'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_pad = self.get_node_from_graph(tfnode, tf_inputs['pads'])
        pad_name = self.gen_name(tfnode.input[tf_inputs['pads']])

        padding = node_pad['np_tensor'].tolist()
        head = [padding[0][0], padding[1][0], padding[2][0], padding[3][0]]
        tail = [padding[0][1], padding[1][1], padding[2][1], padding[3][1]]

        head = tuple([int(x) for x in head])
        tail = tuple([int(x) for x in tail])

        output_shape = node_input['output_shape'][:]

        try:
            assert len(output_shape) == len(
                padding), "Dimensions of padding and input do not match"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            self.nxgraph.add_edge(pad_name, node_name)

        for i in range(len(node_input['output_shape'])):
            output_shape[i] += padding[i][0]
            output_shape[i] += padding[i][1]

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              padding=padding,
                              head=head,
                              tail=tail,
                              value=0,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)
        self.nxgraph.add_edge(pad_name, node_name)

    def import_Placeholder(self, tfnode):
        node_name = tfnode.name
        op = 'external'
        size = []

        shape = None
        if 'shape' in tfnode.attr:
            shape = tfnode.attr['shape'].shape
        if shape is None or 'unknown_rank: true' in str(shape):
            if len(tfnode.input) >= 1:
                node_shape = self.get_node_from_graph(tfnode, 0)
                size = list(node_shape['np_tensor'])
            else:
                print("Unknown input shape, using default shape: " +
                      str(self.default_shape))
                size = self.default_shape
        else:
            for dimen in shape.dim:
                size.append(dimen.size)

        append_size = True
        if size.count(-1) > 1:
            shape = self.default_shape
            append_size = False
        elif size[0] < 0:
            shape = [1]
        else:
            shape = [size[0]]
        if append_size:
            for i in range(1, len(size)):
                shape.append(size[i])

        self.nxgraph.add_node(
            node_name, op=op, shape=shape, datatype=np.dtype('float32'),
             output_shape=shape)

    def import_PlaceholderWithDefault(self, tfnode):
        self.node_alias[tfnode.name] = tfnode.input[0]

    def import_pool(self, tfnode, op_name):
        """
        Generic pooling function
        :param tfnode: Tensorflow node
        :param op_name: Name of pool operation
        :return:
        """
        tf_inputs = {'input': 0}
        padding = tfnode.attr['padding'].s
        node_name = tfnode.name

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        sizes = tfnode.attr['ksize'].list.i
        sizes = [int(v) for v in sizes]
        strides = tfnode.attr['strides'].list.i
        strides = [int(v) for v in strides]
        dilations = [1, 1, 1, 1]

        if len(node_input['output_shape']) != 4:
            print("Input to AvgPool is not 4D")
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        # Calculate output shape
        in_shape = node_input['output_shape'][:]
        try:
            out_shape, padding_shape = self.calc_hw_shape(in_shape[1:3],
                                                          sizes[1:3],
                                                          dilations[1:3],
                                                          strides[1:3],
                                                          padding)

        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        # Add pad node if applicable
        output_shape = [in_shape[0]] + out_shape + [in_shape[3]]
        padding_shape = [(0, 0)] + padding_shape + [(0, 0)]

        head = []
        tail = []

        for pad in padding_shape:
            head.append(int(pad[0]))
            tail.append(int(pad[1]))

        self.nxgraph.add_node(node_name,
                              op=op_name,
                              input=input_name,
                              size=sizes,
                              stride=strides,
                              dilation=dilations,
                              head=head,
                              tail=tail,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)

    def import_Pow(self, tfnode):
        self.import_binary(tfnode, 'pow')

    def import_Prod(self, tfnode):
        self.import_reduce(tfnode, 'prod_reduce')

    def import_RealDiv(self, tfnode):
        self.import_binary(tfnode, 'div')

    def import_reduce(self, tfnode, op_name):
        tf_inputs = {'input': 0, 'axis': 1}
        node_name = tfnode.name
        suffix = "_" + str(tfnode.op).lower()

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_axis = self.get_node_from_graph(tfnode, tf_inputs['axis'])
        axis_name = self.gen_name(tfnode.input[tf_inputs['axis']])

        input_shape = node_input['output_shape'][:]
        shape = node_axis['np_tensor']
        # Check axes are valid
        try:
            assert all(abs(axis) < len(input_shape) for axis in shape), \
                "All items in axes must be in the range (-rank(input), rank(input))"
            assert len(shape) == len(
                set(shape)), "All items in axes must be unique"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        axes = []
        for i in shape:
            axis = i
            if axis < 0:
                axis = len(node_input['output_shape']) + axis
            if axis not in axes:
                axes.append(int(axis))
        axes.sort()
        self.nxgraph.remove_node(axis_name)

        output_shape = input_shape[:]
        axes.sort(reverse=True)
        if tfnode.attr['keep_dims'].b or tfnode.attr['keepdims'].b:
            for i in axes:
                output_shape[i] = 1
        else:
            for i in axes:
                output_shape.pop(i)
            if not output_shape:
                output_shape = [1]
        axes.sort()

        add_reshape = False
        if len(input_shape) != len(output_shape):
            add_reshape = True
            orig_shape = output_shape[:]
            output_shape = [output_shape[0], 1, 1, output_shape[1]]
            orig_name = node_name
            node_name = node_name + suffix

        if (op_name == "mean_reduce" or op_name == "max_reduce") and axes == [1, 2]:
            # Equivalent to avg pool or max pool
            if op_name == "mean_reduce":
                op_name = 'avg_pool'
            else:
                op_name = "max_pool"

            self.nxgraph.add_node(node_name,
                                  op=op_name,
                                  input=input_name,
                                  size=[1, input_shape[1], input_shape[2], 1],
                                  stride=[1, 1, 1, 1],
                                  dilation=[1, 1, 1, 1],
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, node_name)
        else:
            self.nxgraph.add_node(node_name,
                                  op=op_name,
                                  input=input_name,
                                  axes=axes,
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, node_name)

        if add_reshape:
            # Reshape to remove dims
            self.nxgraph.add_node(orig_name,
                                  op="reshape",
                                  input=node_name,
                                  shape=orig_shape,
                                  output_shape=orig_shape,
                                  datatype=np.dtype('float32'),
                                  maintain_format=False)
            self.nxgraph.add_edge(node_name, orig_name)

    def import_Relu(self, tfnode):
        self.import_unary(tfnode, 'relu')

    def import_Relu6(self, tfnode):
        self.import_unary(tfnode, 'relu6')

    def import_Reshape(self, tfnode):
        tf_inputs = {'input': 0, 'shape': 1}
        node_name = tfnode.name
        op = 'reshape'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        node_shape = self.get_node_from_graph(tfnode, tf_inputs['shape'])

        if node_shape['op'] == 'shape_of':
            shape = node_shape['output_shape'][:]
        elif node_shape['op'] == 'stack' or node_shape['op'] == 'concat':
            shape = np.reshape(np.asarray(
                self.get_value_stack(node_shape), dtype=np.int32), [-1])
        else:
            shape = node_shape['np_tensor']
            shape = shape if type(
                shape) == list else node_shape['np_tensor'].tolist()

        self.nxgraph.remove_node(tfnode.input[tf_inputs['shape']])

        in_shape = node_input['output_shape'][:]
        output_shape = []
        for i in shape:
            output_shape.append(i)
        if -1 in output_shape:
            in_size = 1
            for i in in_shape:
                in_size *= i
            neg_index = -1
            for i in range(len(output_shape)):
                if output_shape[i] == -1:
                    neg_index = i
                else:
                    in_size = in_size / output_shape[i]
            output_shape[neg_index] = int(in_size)
            shape[neg_index] = int(in_size)

        output_shape = [int(v) for v in output_shape]

        # Check if reshape is valid
        if len(in_shape) != 6 and np.prod(node_input['output_shape']) != np.prod(output_shape):
            print(
                "Invalid reshape, number of elements "
                "in reshape does not match original shape")
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              shape=output_shape,
                              output_shape=output_shape,
                              datatype=np.dtype('float32'),
                              maintain_format=False)
        self.nxgraph.add_edge(input_name, node_name)

    def import_ResizeNearestNeighbor(self, tfnode):
        tf_inputs = {'input': 0, 'size': 1}
        node_name = tfnode.name

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_size = self.get_node_from_graph(tfnode, tf_inputs['size'])
        size_name = self.gen_name(tfnode.input[tf_inputs['size']])
        input_shape = node_input['output_shape'][:]

        if len(input_shape) != 4:
            print("Resize input is not 4D")
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            self.nxgraph.add_edge(size_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        size = node_size['np_tensor']
        scale_factor = size / input_shape[1:3]
        try:
            assert not tfnode.attr['align_corners'].b, \
                "Align Corners must be false for native import, please use DeepView Extra's resize"
            assert not tfnode.attr['half_pixel_centers'].b, \
                "Half pixel centers must be false for native import, please use DeepView Extra's resize"
            assert scale_factor[0] % 2 == 0, \
                "Only even scale factors are supported for native import, please use DeepView Extra's resize"
        except AssertionError as e:
            logging.warning(str(e))
            self.import_unknown(tfnode)

        scale_factor = int(scale_factor[0])
        output_shape = input_shape[:]
        output_shape[1] *= scale_factor
        output_shape[2] *= scale_factor

        if scale_factor > 1:
            rank = len(input_shape)
            concat_input = input_name
            concat_shape = input_shape[:]
            for i in range(scale_factor // 2):
                for j in range(rank - 2):
                    axis = rank - 1 - j
                    concat_name = node_name + "_concat_" + str(i) + "_" + str(j)
                    concat_shape = concat_shape[:]
                    concat_shape[axis] *= 2
                    self.nxgraph.add_node(concat_name,
                                          op='concat',
                                          axis=axis,
                                          values=[concat_input, concat_input],
                                          datatype=np.dtype('float32'),
                                          output_shape=concat_shape)
                    self.nxgraph.add_edge(concat_input, concat_name)
                    concat_input = concat_name

                if i == (scale_factor // 2) - 1:
                    concat_shape = output_shape
                    reshape_name = node_name
                else:
                    reshape_name = node_name + "_reshape" + str(i)

                self.nxgraph.add_node(reshape_name,
                                      op='reshape',
                                      input=concat_name,
                                      shape=concat_shape,
                                      datatype=np.dtype('float32'),
                                      output_shape=concat_shape)
                self.nxgraph.add_edge(concat_name, reshape_name)
                concat_input = reshape_name

    def import_Rsqrt(self, tfnode):
        self.import_unary(tfnode, 'rsqrt')

    def import_Shape(self, tfnode):
        tf_inputs = {'x': 0}
        node_name = tfnode.name
        op = 'constant'

        node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
        output_shape = np.array(node_x['output_shape'])

        self.nxgraph.add_node(node_name,
                              op=op,
                              np_tensor=output_shape,
                              shape=[len(output_shape)],
                              output_shape=[len(output_shape)],
                              datatype=np.dtype('int32'))

    def import_Sigmoid(self, tfnode):
        self.import_unary(tfnode, 'sigmoid')

    def import_Sin(self, tfnode):
        self.import_unary(tfnode, 'sin')

    def import_Slice(self, tfnode):
        tf_inputs = {'input': 0, 'begin': 1, 'size': 2}
        node_name = tfnode.name
        op = 'slice'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        begin_name = self.gen_name(tfnode.input[tf_inputs['begin']])
        node_begin = self.get_node_from_graph(tfnode, tf_inputs['begin'])

        size_name = self.gen_name(tfnode.input[tf_inputs['size']])
        node_size = self.get_node_from_graph(tfnode, tf_inputs['size'])

        begin = np.reshape(np.asarray(
            node_begin['np_tensor'], dtype=np.int32), [-1])
        size = np.reshape(np.asarray(
            node_size['np_tensor'], dtype=np.int32), [-1])
        end = []
        for i in range(len(size)):
            end.append(begin[i] + size[i] if size[i] != -1 else 0)
        self.nxgraph.remove_node(size_name)
        self.nxgraph.remove_node(begin_name)
        axes = list(range(len(begin)))

        # Check axes are valid
        try:
            assert all(axis >= 0 for axis in axes), \
                "All items in axes must be non-negative"
            assert all(
                axis < len(node_input['output_shape']) for axis in axes), \
                "All items in axes must be less than the rank of input"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape = shape_help.slice_shape(node_input['output_shape'],
                                   axes,
                                   begin,
                                   end)

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              axes=axes,
                              begin=list(begin),
                              end=list(end),
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)

    def import_Softmax(self, tfnode):
        tf_inputs = {'x': 0}
        node_name = tfnode.name
        op = 'softmax'

        node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
        x_name = self.gen_name(tfnode.input[tf_inputs['x']])
        output_shape = node_x['output_shape'][:]

        self.nxgraph.add_node(node_name,
                              op=op,
                              x=x_name,
                              output_shape=output_shape,
                              datatype=np.dtype('float32'),
                              axes=[1])
        self.nxgraph.add_edge(x_name, node_name)

    def import_Split(self, tfnode, is_split_v=False):
        node_name = self.gen_name(tfnode.name)
        if is_split_v:
            tf_inputs = {'value': 0, 'size_splits': 1, 'axis': 2}
        else:
            tf_inputs = {'value': 1, 'axis': 0}

        node_value = self.get_node_from_graph(tfnode, tf_inputs['value'])
        value_name = self.gen_name(tfnode.input[tf_inputs['value']])
        node_axis = self.get_node_from_graph(tfnode, tf_inputs['axis'])
        axis_name = self.gen_name(tfnode.input[tf_inputs['axis']])
        self.nxgraph.remove_node(axis_name)

        split_axis = int(node_axis['np_tensor'][0])

        num_split = tfnode.attr['num_split'].i

        try:
            assert split_axis < len(node_value['output_shape']), \
                "Split axis must be less than the rank of value"
            assert not node_value['output_shape'][split_axis] % num_split, \
                "num_split does not evenly divide value[axis]"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(value_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        names = []
        if num_split >= 1:
            for i in range(num_split):
                if i == 0:
                    names.append(tfnode.name)
                else:
                    names.append(tfnode.name + '_' + str(i))

        input_shape = node_value['output_shape'][:]
        if split_axis == -1:
            split_axis = len(input_shape) - 1
        ratio = math.floor(input_shape[split_axis] / num_split)
        if is_split_v:
            size_splits_name = self.gen_name(tfnode.input[tf_inputs['size_splits']])
            node_size_splits = self.nxgraph.nodes[size_splits_name]
            ratios = list(node_size_splits['np_tensor'])
            ratios_copy = ratios[:]
            ratios_copy.pop(split_axis)
            ratios[split_axis] = input_shape[split_axis] - sum(ratios_copy)
        else:
            modu = input_shape[split_axis] % num_split

            ratios = []
            for i in range(num_split):
                rat_val = ratio
                if modu != 0:
                    rat_val += 1
                    modu -= 1
                ratios.append(int(rat_val))

        axes = list(range(len(input_shape)))
        for i in range(num_split):
            begin = len(input_shape) * [0]
            begin[split_axis] = ratio * i
            end = input_shape[:]
            end[split_axis] = ratio * (i + 1)
            output_shape = shape_help.split_shape(begin, end, split_axis)

            self.nxgraph.add_node(names[i],
                                  op='slice',
                                  input=value_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(value_name, names[i])

    def import_SplitV(self, tfnode):
        self.import_Split(tfnode, is_split_v=True)

    def import_Square(self, tfnode):
        self.import_unary(tfnode, 'sqr')

    def import_Sqrt(self, tfnode):
        self.import_unary(tfnode, 'sqrt')

    def import_Squeeze(self, tfnode):
        tf_inputs = {'input': 0}
        node_name = tfnode.name
        op = 'reshape'
        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[0])

        input_shape = node_input['output_shape']
        output_shape = []
        try:
            if tfnode.attr['squeeze_dims'].list.i:
                for i in range(len(input_shape)):
                    if i not in tfnode.attr['squeeze_dims'].list.i:
                        output_shape.append(input_shape[i])
                    else:
                        assert input_shape[i] == 1, \
                            "Cannot select an axis to squeeze which " \
                            "has size not equal to one"
            else:
                for i in input_shape:
                    if i != 1:
                        output_shape.append(i)
        except AttributeError:
            print(
                "Could not find 'squeeze_dims' argument,"
                " possibly using 'axis' arg instead.")
        except IndexError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape = [int(v) for v in output_shape]

        self.nxgraph.add_node(node_name, op=op, input=input_name,
                              shape=output_shape, datatype=np.dtype('float32'),
                              output_shape=output_shape,
                              maintain_format=False)
        self.nxgraph.add_edge(input_name, node_name)

    def import_StridedSlice(self, tfnode):
        tf_inputs = {'input': 0, 'begin': 1, 'end': 2, 'strides': 3}
        node_name = tfnode.name
        op = 'slice'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])

        node_begin = self.get_node_from_graph(tfnode, tf_inputs['begin'])
        begin_name = self.gen_name(tfnode.input[tf_inputs['begin']])

        node_end = self.get_node_from_graph(tfnode, tf_inputs['end'])
        end_name = self.gen_name(tfnode.input[tf_inputs['end']])

        node_strides = self.get_node_from_graph(tfnode, tf_inputs['strides'])
        strides_name = self.gen_name(tfnode.input[tf_inputs['strides']])

        begin = np.reshape(np.asarray(
            node_begin['np_tensor'], dtype=np.int32), [-1])
        end = np.reshape(np.asarray(
            node_end['np_tensor'], dtype=np.int32), [-1])
        strides = np.reshape(np.asarray(
            node_strides['np_tensor'], dtype=np.int32), [-1])

        shrink_mask = tfnode.attr['shrink_axis_mask'].i

        if node_input['op'] == 'constant' and len(begin) == 1 and len(end) == 1 and len(strides) == 1:
            # Try to fold in constant
            # TODO make this more general
            value = node_input['np_tensor']
            begin = begin[0]
            end = end[0]
            strides = strides[0]
            value = value[begin:end:strides]
            shape = list(value.shape)
            self.nxgraph.add_node(node_name,
                                  op='constant',
                                  np_tensor=value,
                                  shape=shape,
                                  datatype=value.dtype,
                                  output_shape=shape)
            return

        self.nxgraph.remove_nodes_from([begin_name, end_name, strides_name])
        for stride in strides:
            assert stride == 1, \
                "Slice operation uses a stride that is not one, " \
                "currently unsupported."

        axes = list(range(len(begin)))

        # Check axes are valid
        try:
            assert all(axis >= 0 for axis in axes), \
                "All items in axes must be non-negative"
            assert all(
                axis < len(node_input['output_shape']) for axis in axes), \
                "All items in axes must be less than the rank of input"
        except AssertionError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        output_shape = len(axes) * [0]
        for i in range(len(axes)):
            if end[i] == 0:
                output_shape[i] = node_input['output_shape'][i]
            elif end[i] > 0:
                output_shape[i] = end[i]
            elif end[i] < 0:
                output_shape[i] = node_input['output_shape'][i] + end[i]
            if begin[i] >= 0:
                output_shape[i] = output_shape[i] - begin[i]
            elif begin[i] < 0:
                output_shape[i] = output_shape[i] - \
                                  (node_input['output_shape'][i] + begin[i])
            else:
                output_shape[i] = output_shape[i] - begin[i]

        if shrink_mask != 0:
            self.nxgraph.add_node(node_name + '_slice',
                                  op=op,
                                  input=input_name,
                                  axes=axes,
                                  begin=list(begin),
                                  end=list(end),
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, node_name + '_slice')

            squeeze_shape = []
            for i in axes:
                if shrink_mask & (1 << i):
                    continue
                else:
                    squeeze_shape.append(output_shape[i])
            if not squeeze_shape:
                squeeze_shape = [1]

            self.nxgraph.add_node(node_name,
                                  op='reshape',
                                  input=node_name + '_slice',
                                  shape=squeeze_shape,
                                  output_shape=squeeze_shape,
                                  datatype=np.dtype('float32'),
                                  maintain_format=False)
            self.nxgraph.add_edge(node_name + '_slice', node_name)
        else:
            self.nxgraph.add_node(node_name,
                                  op=op,
                                  input=input_name,
                                  axes=axes,
                                  begin=list(begin),
                                  end=list(end),
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, node_name)

    def import_Sub(self, tfnode):
        self.import_binary(tfnode, 'sub')

    def import_Sum(self, tfnode):
        self.import_reduce(tfnode, 'sum_reduce')

    def import_Tanh(self, tfnode):
        self.import_unary(tfnode, 'tanh')

    def import_TFLite_Detection_PostProcess(self, tfnode):
        tf_inputs = {'boxes': 0, 'scores': 1, 'anchors': 2}
        node_name = "ssd_post_process"

        scales = [tfnode.attr["y_scale"].f,
                  tfnode.attr["x_scale"].f,
                  tfnode.attr["w_scale"].f,
                  tfnode.attr["h_scale"].f]
        node_anchors = self.get_node_from_graph(tfnode, tf_inputs['anchors'])
        anchors_name = self.gen_name(tfnode.input[tf_inputs['anchors']])
        anchors_numpy = node_anchors['np_tensor']
        self.nxgraph.remove_node(anchors_name)

        node_boxes = self.get_node_from_graph(tfnode, tf_inputs['boxes'])
        boxes_name = self.gen_name(tfnode.input[tf_inputs['boxes']])
        input_shape = node_boxes['output_shape']
        gen_ssd_output(self, boxes_name, input_shape, node_name, anchors_numpy, scales)

    def import_Transpose(self, tfnode):
        tf_inputs = {'input': 0, 'axes': 1}
        node_name = tfnode.name
        op = 'transpose'

        node_input = self.get_node_from_graph(tfnode, tf_inputs['input'])
        input_name = self.gen_name(tfnode.input[tf_inputs['input']])
        node_axes = self.get_node_from_graph(tfnode, tf_inputs['axes'])
        axes_name = self.gen_name(tfnode.input[tf_inputs['axes']])

        axes = node_axes['np_tensor'].tolist()
        self.nxgraph.remove_node(axes_name)

        output_shape = []
        try:
            for i in range(len(node_input['output_shape'])):
                output_shape.append(node_input['output_shape'][axes[i]])
        except IndexError:
            self.nxgraph.add_node(node_name)
            self.nxgraph.add_edge(input_name, node_name)
            raise rt.errors.ShapePropagationError(
                self.nxgraph, node_name)

        self.nxgraph.add_node(node_name,
                              op=op,
                              input=input_name,
                              axes=axes,
                              datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, node_name)

    def import_unary(self, tfnode, op_name):
        """
        Generic unary op import function
        :param tfnode: Tensorflow node
        :param op_name: Name of unary operation
        :return:
        """
        tf_inputs = {'x': 0}
        node_name = tfnode.name

        node_x = self.get_node_from_graph(tfnode, tf_inputs['x'])
        x_name = self.gen_name(tfnode.input[tf_inputs['x']])
        output_shape = node_x['output_shape'][:]

        self.nxgraph.add_node(node_name, op=op_name,
                              x=x_name, datatype=np.dtype('float32'),
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, node_name)

    def import_unknown(self, tfnode):
        node_name = tfnode.name

        # Log node info
        logging.info("Unsupported operation: " + tfnode.op)
        logging.info("Generating log for unsupported node: {node_name}. Log is located at {log_path}".format(
            node_name=node_name, log_path=self.log_path))
        logging.warning("Attempting to add unsupported node to graph")
        logging.info("Node name: " + node_name)
        logging.info("Operation type: " + str(tfnode.op))
        logging.info("Input(s): " + str(tfnode.input))
        logging.info("Attributes: \n" + str(tfnode.attr) + "\n")

        if tfnode.op == 'VariableV2':
            print(
                "Found Variable in graph, graph may not be trained."
                " Try exporting a trained frozen graph or"
                " convert variables to constants")
            raise SystemExit(-1)

        # Add unknown node to graph and attempt to continue
        if tfnode.input:
            node_input = self.get_node_from_graph(tfnode, 0)

            if 'output_shape' in node_input:
                output_shape = node_input['output_shape'][:]
            else:
                output_shape = []

            input_name = self.gen_name(tfnode.input[0])
            self.nxgraph.add_node(tfnode.name,
                                  op='reshape',
                                  input=input_name,
                                  shape=output_shape,
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, tfnode.name)
        else:
            self.nxgraph.add_node(tfnode.name,
                                  shape=[1],
                                  datatype=np.dtype('float32'),
                                  output_shape=[1],
                                  op='reshape')

    def import_Unpack(self, tfnode):
        tf_inputs = {'value': 0}
        node_name = tfnode.name

        val_name = self.gen_name(tfnode.input[tf_inputs['value']])
        node_val = self.get_node_from_graph(tfnode, tf_inputs['value'])

        num = int(tfnode.attr['num'].i)
        axis = int(tfnode.attr['axis'].i)

        input_shape = node_val['output_shape'][:]

        for i in range(num):
            slice_name = node_name + ':' + str(i) if i != 0 else node_name
            output_shape = [input_shape[dim] for dim in range(len(input_shape))
                            if dim != axis]
            self.nxgraph.add_node(slice_name,
                                  op='slice',
                                  input=val_name,
                                  axes=[axis],
                                  begin=[i],
                                  end=[0],
                                  datatype=np.dtype('float32'),
                                  output_shape=output_shape)
