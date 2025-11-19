# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import math
import numpy as np
import networkx as nx
# from .onnx.onnx_ml_pb2 import TensorProto, ModelProto
from .onnx.onnx_ml_pb2 import TensorProto, ModelProto
from .converter.abstract_graph import AGLayer, LayerFormat

onnx_type_map = {
    int(TensorProto.FLOAT): np.dtype('float32'),
    int(TensorProto.UINT8): np.dtype('uint8'),
    int(TensorProto.INT8): np.dtype('int8'),
    int(TensorProto.UINT16): np.dtype('uint16'),
    int(TensorProto.INT16): np.dtype('int16'),
    int(TensorProto.INT32): np.dtype('int32'),
    int(TensorProto.INT64): np.dtype('int64'),
    int(TensorProto.BOOL): np.dtype('bool'),
    int(TensorProto.FLOAT16): np.dtype('float16'),
    int(TensorProto.DOUBLE): np.dtype('float64'),
    int(TensorProto.COMPLEX64): np.dtype('complex64'),
    int(TensorProto.COMPLEX128): np.dtype('complex128'),
    int(TensorProto.UINT32): np.dtype('uint32'),
    int(TensorProto.UINT64): np.dtype('uint64'),
    int(TensorProto.STRING): np.dtype(object)
}

layer_format_map = {LayerFormat.NHWC: 'nhwc',
                    LayerFormat.UNKNOWN: 'none',
                    LayerFormat.NCD: 'none',
                    LayerFormat.NCHW: 'nchw'}

dtype_map = {np.float32: np.dtype('float32'),
             np.float64: np.dtype('float64'),
             np.int32: np.dtype('int32'),
             np.int64: np.dtype('int64'),
             np.int8: np.dtype('int8'),
             np.uint8: np.dtype('uint8')}

class ONNXImporter:
    def __init__(self, input_model, input_format=LayerFormat.UNKNOWN, batch=1, default_shape=None, subgraph_names=None,
                 model_input_type=np.float32):
        if subgraph_names is None:
            subgraph_names = []
        if type(input_model) == str:
            with open(input_model, 'rb') as f:
                input_model = f.read()
        if default_shape is None:
            default_shape = [1, 224, 224, 3]
        onnx_model = ModelProto()
        onnx_model.ParseFromString(input_model)
        self.onnx_graph = onnx_model.graph
        self.nxgraph = nx.DiGraph()
        self.import_nxgraph = nx.DiGraph()
        self.input_format=input_format
        if input_format == 'none':
            self.input_format = LayerFormat.UNKNOWN
        self.input_names = []
        self.output_names = []
        self.onnx_nodes = 0
        self.orig_nodes = 0
        self.opt_nodes = 0
        self.default_shape = default_shape
        self.batch = batch
        self.trim_input_names = []
        self.trim_output_names = []
        self.model_input_type = model_input_type
        if subgraph_names:
            self.trim_input_names = subgraph_names[0]
            self.trim_output_names = subgraph_names[1]

    def run(self):
        for i in range(len(self.onnx_graph.output)):
            self.output_names.append(self.onnx_graph.output[i].name)
        self.generate_import_graph()
        self.import_inputs()
        self.import_constants()
        self.import_nodes()
        self.onnx_nodes = len(self.onnx_graph.input) + len(self.onnx_graph.initializer) + len(self.onnx_graph.node)
        print("ONNX model has %d nodes" % self.onnx_nodes)
        self.orig_nodes = len(self.nxgraph.nodes)
        print("Imported model has %d nodes" % self.orig_nodes)
        self.clean_graph()
        self.opt_nodes = len(self.nxgraph.nodes)
        print("Cleaned model has %d nodes" % self.opt_nodes)
        self.set_batch()
        self.convert_to_old()
        self.clean_quant_dequant()
        self.prune_graph()

        return self.nxgraph, self.input_names, self.output_names
        
    def generate_import_graph(self):
        for i in range(len(self.onnx_graph.input)):
            onnx_input = self.onnx_graph.input[i]
            self.import_nxgraph.add_node(onnx_input.name)

        for i in range(len(self.onnx_graph.initializer)):
            onnx_const = self.onnx_graph.initializer[i]
            self.import_nxgraph.add_node(onnx_const.name)

        for i in range(len(self.onnx_graph.node)):
            onnx_node = self.onnx_graph.node[i]
            for j in range(len(onnx_node.output)):
                self.import_nxgraph.add_node(onnx_node.output[j])
                for k in range(len(onnx_node.input)):
                    self.import_nxgraph.add_edge(onnx_node.input[k], onnx_node.output[j], op=onnx_node.op_type)

        if self.trim_output_names:
            all_exist = True
            for name in self.trim_output_names:
                if name not in self.import_nxgraph.nodes:
                    all_exist = False
                    break
            if not all_exist:
                print("WARNING: Provided output names do not exist in the graph, unable to trim outputs.")
            else:
                self.output_names = self.trim_output_names[:]
                remove_nodes = []
                for node_name in self.import_nxgraph.nodes:
                    if node_name in self.output_names:
                        continue
                    path_exists = False
                    for output_name in self.output_names:
                        if nx.has_path(self.import_nxgraph, node_name, output_name):
                            path_exists = True
                            break
                    if not path_exists:
                        remove_nodes.append(node_name)
                self.import_nxgraph.remove_nodes_from(remove_nodes)

    def import_inputs(self):
        for i in range(len(self.onnx_graph.input)):
            onnx_input = self.onnx_graph.input[i]
            name = onnx_input.name
            if name not in self.import_nxgraph.nodes:
                continue
            self.input_names.append(name)
            datatype = onnx_type_map[onnx_input.type.tensor_type.elem_type]
            onnx_dims = onnx_input.type.tensor_type.shape.dim
            dims = []
            for j in range(len(onnx_dims)):
                if onnx_dims[j].dim_param != '':
                    dims.append(-1)
                else:
                    dims.append(onnx_dims[j].dim_value)
            if len(dims) == 4:
                layer_format = self.input_format
            else:
                layer_format = LayerFormat.UNKNOWN
            if len(dims) == len(self.default_shape) and -1 in dims[1:]:
                print("The ONNX model does not have a definitive input shape for "
                    "input %s, using default shape provided of [" + 
                    ','.join(str(def_dim) for def_dim in self.default_shape) + "].")
                dims = self.default_shape

            layer = AGLayer(name, op='external', datatype=datatype,
                            shape=dims)
            self.nxgraph.add_node(name, info=layer)
            
    def import_constants(self):
        for i in range(len(self.onnx_graph.initializer)):
            onnx_const = self.onnx_graph.initializer[i]
            name = onnx_const.name
            if name not in self.import_nxgraph.nodes:
                continue
            datatype = onnx_type_map[onnx_const.data_type]
            dims = list(onnx_const.dims)
            if onnx_const.raw_data != b'':
                np_tensor = np.frombuffer(onnx_const.raw_data, dtype=datatype)
            else:
                np_tensor = []
                if datatype == np.float32:
                    for i in range(len(onnx_const.float_data)):
                        np_tensor.append(onnx_const.float_data[i])
                    np_tensor = np.asarray(np_tensor, dtype=datatype)
                elif datatype == np.float64:
                    for i in range(len(onnx_const.double_data)):
                        np_tensor.append(onnx_const.double_data[i])
                    np_tensor = np.asarray(np_tensor, dtype=datatype)
                elif datatype in [np.int32, np.int8, np.uint8]:
                    for i in range(len(onnx_const.int32_data)):
                        np_tensor.append(onnx_const.int32_data[i])
                    np_tensor = np.asarray(np_tensor, dtype=datatype)
                elif datatype == np.int64:
                    for i in range(len(onnx_const.int64_data)):
                        np_tensor.append(onnx_const.int64_data[i])
                    np_tensor = np.asarray(np_tensor, dtype=datatype)
                elif datatype == np.uint64:
                    for i in range(len(onnx_const.uint64_data)):
                        np_tensor.append(onnx_const.uint64_data[i])
                    np_tensor = np.asarray(np_tensor, dtype=datatype)
            if dims != []:
                np_tensor = np_tensor.reshape(dims)
            else:
                dims = list(np_tensor.shape)
            np_tensor = np_tensor.reshape(dims)
            if dims == []:
                dims = list(np_tensor.shape)
            
            layer = AGLayer(name, op='constant', datatype=datatype,
                            shape=dims, tensor=np_tensor)
            self.nxgraph.add_node(name, info=layer)

            if len(dims) > 4:
                if dims[0] == 1:
                    new_shape = dims[1:]
                    self.nxgraph.nodes[name]['base_shape'] = dims
                    self.nxgraph.nodes[name]['output_shape'] = new_shape
                    new_np_tensor = np.reshape(np_tensor.copy(), new_shape)
                    self.nxgraph.nodes[name]['np_tensor'] = new_np_tensor
                else:
                    raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

    def import_nodes(self):
        for i in range(len(self.onnx_graph.node)):
            onnx_node = self.onnx_graph.node[i]
            import_layer = False
            for j in range(len(onnx_node.output)):
                if onnx_node.output[j] in self.import_nxgraph.nodes:
                    import_layer = True
                    break
            if not import_layer:
                continue

            node_op = onnx_node.op_type
            node_fun = self.import_unknown
            if hasattr(self, 'import_' + node_op):
                node_fun = getattr(self, 'import_' + node_op)
            node_fun(onnx_node)

    def set_batch(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if -1 in node_info.shape:
                node_info.shape[node_info.shape.index(-1)] = self.batch
            if 'begin' in node_info.params and -1 in node_info.params['begin']:
                node_info.params['begin'][node_info.params['begin'].index(-1)] = self.batch
            if 'end' in node_info.params and -1 in node_info.params['end']:
                node_info.params['end'][node_info.params['end'].index(-1)] = self.batch

    def convert_to_old(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            data['op'] = node_info.op
            if node_info.datatype in dtype_map:
                data['datatype'] = dtype_map[node_info.datatype]
            else:
                data['datatype'] = node_info.datatype
            data['format'] = layer_format_map[node_info.format]
            data['output_shape'] = node_info.shape[:]
            for key, val in node_info.params.items():
                data[key] = val
            if node_info.quant_scale is not None:
                data['quant_scale'] = node_info.quant_scale.copy()
            if node_info.zero_point is not None:
                data['zero_point'] = node_info.zero_point.copy()
                data['quant_axis'] = node_info.quant_axis
            if node_info.tensor is not None:
                data['np_tensor'] = node_info.tensor.copy()

            if node_info.op in ['external', 'constant']:
                continue
            elif node_info.op in ['add']:
                data['x'] = node_info.inputs[0]
                data['y'] = node_info.inputs[1]
            elif node_info.op in ['quant', 'dequant', 'abs', 'relu']:
                data['x'] = node_info.inputs[0]
            elif node_info.op in ['conv']:
                data['input'] = node_info.inputs[0]
                data['filter'] = node_info.inputs[1]
                if len(node_info.inputs) == 3:
                    data['bias'] = node_info.inputs[2]
            elif node_info.op in ['max_pool', 'reshape', 'mean_reduce', 'transpose', 'avg_pool']:
                data['input'] = node_info.inputs[0]
            elif node_info.op in ['concat']:
                data['values'] = node_info.inputs[:]
            elif node_info.op in ['linear']:
                data['A'] = node_info.inputs[0]
                data['B'] = node_info.inputs[1]
                if len(node_info.inputs) == 3:
                    data['bias'] = node_info.inputs[2]
            
            else:
                print(node_name)
                print(node_info)
                print(data)
                raise NotImplementedError("Unable to convert node listed above")

    def calc_binary_shape(self, x, y):
        if len(x) > len(y):
            return x[:]
        if len(y) > len(x):
            return y[:]
        x_vol = 1
        for dim in x:
            if dim > 0:
                x_vol *= dim
        y_vol = 1
        for dim in y:
            if dim > 0:
                y_vol *= dim
        
        if x_vol > y_vol:
            return x[:]
        else:
            return y[:]

    def import_unary(self, node, op):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]['info']
        datatype = x_node.datatype
        layer_format = x_node.format
        if 'base_shape' in x_node.params:
            output_shape = x_node.params['base_shape'][:]
        else:
            output_shape = x_node.shape[:]

        layer = AGLayer(name, op=op, inputs=[x_name],
                        datatype=datatype, layer_format=layer_format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(x_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)


    def import_binary(self, node, op):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]['info']
        if 'base_shape' in x_node.params:
            x_shape = x_node['base_shape']
        else:
            x_shape = x_node.shape
        y_name = node.input[1]
        y_node = self.nxgraph.nodes[y_name]['info']
        if 'base_shape' in y_node.params:
            y_shape = y_node['base_shape']
        else:
            y_shape = y_node.shape
        datatype = x_node.datatype
        output_shape = self.calc_binary_shape(x_shape, y_shape)
        if x_node.shape == output_shape:
            layer_format = x_node.format
        else:
            layer_format = y_node.format

        layer = AGLayer(name, op=op, inputs=[x_name, y_name],
                        datatype=datatype, layer_format=layer_format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)
            
        if x_node.tensor is not None and y_node.tensor is not None and op == 'add':
                self.nxgraph.nodes[name]['info'].tensor = x_node.tensor + y_node.tensor

    def import_Abs(self, node):
        self.import_unary(node, 'abs')

    def import_Add(self, node):
        self.import_binary(node, 'add')

    def import_AveragePool(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        dims = len(input_shape) - 2
        size = [1] * dims
        strides = [1] * dims
        head = [0] * dims
        tail = [0] * dims

        for attrib in node.attribute:
            if attrib.name == 'kernel_shape':
                for i in range(len(attrib.ints)):
                    size[i] = attrib.ints[i]
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    strides[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                for i in range(len(attrib.ints)):
                    pad_length = len(attrib.ints)
                    ht_split = pad_length // 2
                    for i in range(0, len(attrib.ints)):
                        if i < ht_split:
                            head[i] = attrib.ints[i]
                        else:
                            tail[i-ht_split] = attrib.ints[i]

        output_shape = input_shape[:]
        for i in range(2, len(output_shape)):
            output_shape[i] = math.floor((input_shape[i] + head[i-2] + tail[i-2] - size[i-2]) / strides[i-2] + 1)

        params = {'size': size,
                  'stride': strides,
                  'head': head,
                  'tail': tail}
        layer = AGLayer(name, op='avg_pool', inputs=[input_name],
                        params=params, datatype=datatype, layer_format=input_node.format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(input_name, name)

    def import_BatchNormalization(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        scale_name = node.input[1]
        offset_name = node.input[2]
        mean_name = node.input[3]
        var_name = node.input[4]
        datatype = input_node.datatype
        layer_format = input_node.format
        output_shape = input_node.shape[:]

        eps = 1e-5
        for attrib in node.attribute:
            if attrib.name == 'epsilon':
                eps = attrib.f

        self.nxgraph.add_node(name + '_bn_epsilon_dv',
                              op='constant',
                              datatype=np.float32,
                              format='none',
                              output_shape=[1],
                              np_tensor=np.asarray([eps]), dtype=np.float32)

        self.nxgraph.add_node(name,
                              op='batch_normalization',
                              input=input_name,
                              scale=scale_name,
                              offset=offset_name,
                              mean=mean_name,
                              variance=var_name,
                              epsilon=name + '_bn_epsilon_dv',
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(scale_name, name)
        self.nxgraph.add_edge(offset_name, name)
        self.nxgraph.add_edge(mean_name, name)
        self.nxgraph.add_edge(var_name, name)
        self.nxgraph.add_edge(name + '_bn_epsilon_dv', name)

    def import_Cast(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        datatype = input_node['datatype']
        output_shape = input_node['output_shape'][:]

        for attrib in node.attribute:
            if attrib.name == 'to':
                datatype = onnx_type_map[attrib.i]
        
        self.nxgraph.add_node(name,
                              op='cast',
                              x=input_name,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        if 'np_tensor' in input_node:
            out_tensor = input_node['np_tensor'].copy().astype(datatype)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_Clip(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        if len(node.input) == 1:
            min_value = None
            max_value = None
            for attrib in node.attribute:
                if attrib.name == 'min':
                    min_value = attrib.f
                if attrib.name == 'max':
                    max_value = attrib.f
            if min_value is None:
                print("WARNING: attribute min not detected. Using default values of negative infinity.")
                min_value = float("-inf")
            if max_value is None:
                print("WARNING: attribute max not detected. Using default values of positive infinity.")
                max_value = float("inf")

            self.nxgraph.add_node(name + '_dv_min',
                                  op='constant',
                                  datatype=np.float32,
                                  format='none',
                                  output_shape=[1],
                                  np_tensor=np.asarray([min_value]).astype(np.float32))

            self.nxgraph.add_node(name + '_dv_max',
                                  op='constant',
                                  datatype=np.float32,
                                  format='none',
                                  output_shape=[1],
                                  np_tensor=np.asarray([max_value]).astype(np.float32))
            min_name = name + '_dv_min'
            max_name = name + '_dv_max'
        else:
            min_name = node.input[1]
            max_name = node.input[2]

        datatype = input_node['datatype']
        output_shape = input_node['output_shape'][:]

        self.nxgraph.add_node(name,
                              op='clip',
                              input=input_name,
                              min=min_name,
                              max=max_name,
                              datatype=datatype,
                              format=input_node['format'],
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(min_name, name)
        self.nxgraph.add_edge(max_name, name)

    def import_Concat(self, node):
        name = node.output[0]
        value_names = []
        value_nodes = []
        for i in range(len(node.input)):
            value_names.append(node.input[i])
            value_nodes.append(self.nxgraph.nodes[value_names[i]]['info'])
        datatype = value_nodes[0].datatype
        axis = 0

        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i

        if 'base_shape' in value_nodes[0].params:
            output_shape = value_nodes[0].params['base_shape'][:]
        else:
            output_shape = value_nodes[0].shape[:]
        if axis < 0:
            axis += len(output_shape)
        for i in range(1, len(value_nodes)):
            if 'base_shape' in value_nodes[i].params:
                output_shape[axis] += value_nodes[i].params['base_shape'][axis]
            else:
                output_shape[axis] += value_nodes[i].shape[axis]

        layer_format = value_nodes[0].format
        for i in range(1, len(value_nodes)):
            if layer_format == LayerFormat.UNKNOWN:
                layer_format = value_nodes[i].format
            else:
                if value_nodes[i].format != LayerFormat.UNKNOWN and \
                    value_nodes[i].format != layer_format:
                    layer_format = LayerFormat.UNKNOWN
                    break
        
        params = {'axis': axis}
        layer = AGLayer(name, op='concat', inputs=value_names,
                        params=params, datatype=datatype,
                        layer_format=layer_format, shape=output_shape)

        self.nxgraph.add_node(name, info=layer)
        # self.nxgraph.add_node(name,
        #                       op='concat',
        #                       values=value_names,
        #                       axis=axis,
        #                       datatype=datatype,
        #                       format=conc_format,
        #                       output_shape=output_shape)
        for in_name in value_names:
            self.nxgraph.add_edge(in_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1 and axis != 0:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
                self.nxgraph.nodes[name]['base_axis'] = axis
                self.nxgraph.nodes[name]['axis'] = axis - 1
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        calc_node = True
        for node in value_nodes:
            # if 'np_tensor' not in node:
            if node.tensor is None:
                calc_node = False
                break
        
        if calc_node:
            value_tensors = []
            for node in value_nodes:
                value_tensors.append(node['np_tensor'].copy())
            out_tensor = np.concatenate(value_tensors, axis=axis)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_Constant(self, node):
        # TODO: need to support all of the other attributes
        name = node.output[0]
        for attrib in node.attribute:
            if attrib.name == 'value':
                dims = list(attrib.t.dims)
                datatype = onnx_type_map[attrib.t.data_type]
                if attrib.t.raw_data != b'':
                    np_tensor = np.frombuffer(attrib.t.raw_data, dtype=datatype)
                else:
                    np_tensor = []
                    if datatype == np.float32:
                        for i in range(len(attrib.t.float_data)):
                            np_tensor.append(attrib.t.float_data[i])
                        np_tensor = np.asarray(np_tensor, dtype=datatype)
                    elif datatype == np.float64:
                        for i in range(len(attrib.t.double_data)):
                            np_tensor.append(attrib.t.double_data[i])
                        np_tensor = np.asarray(np_tensor, dtype=datatype)
                    elif datatype in [np.int32, np.int8, np.uint8]:
                        for i in range(len(attrib.t.int32_data)):
                            np_tensor.append(attrib.t.int32_data[i])
                        np_tensor = np.asarray(np_tensor, dtype=datatype)
                    elif datatype == np.int64:
                        for i in range(len(attrib.t.int64_data)):
                            np_tensor.append(attrib.t.int64_data[i])
                        np_tensor = np.asarray(np_tensor, dtype=datatype)
                    elif datatype == np.uint64:
                        for i in range(len(attrib.t.uint64_data)):
                            np_tensor.append(attrib.t.uint64_data[i])
                        np_tensor = np.asarray(np_tensor, dtype=datatype)
                if dims != []:
                    np_tensor = np_tensor.reshape(dims)
                else:
                    dims = list(np_tensor.shape)
                np_tensor = np_tensor.reshape(dims)
                if dims == []:
                    dims = list(np_tensor.shape)

        layer = AGLayer(name, op='constant', datatype=datatype,
                            shape=dims, tensor=np_tensor)
        self.nxgraph.add_node(name, info=layer)
        
    def import_ConstantOfShape(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        if 'np_tensor' not in input_node:
            raise ValueError("Unable to import ConstantOfShape, cannot determine shape")
        output_shape = list(input_node['np_tensor'])

        for attrib in node.attribute:
            if attrib.name == 'value':
                datatype = onnx_type_map[attrib.t.data_type]
                values = np.frombuffer(attrib.t.raw_data, datatype)

        if -1 in output_shape:
            while -1 in output_shape:
                output_shape[output_shape.index(-1)] = self.batch
        np_tensor = np.full(output_shape, values, dtype=datatype)

        self.nxgraph.add_node(name,
                              op='constant',
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape,
                              np_tensor=np_tensor)

    def import_Conv(self, node):
        name = node.output[0]
        orig_name = name
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        filt_name = node.input[1]
        filt_shape = self.nxgraph.nodes[filt_name]['info'].shape
        dims = len(input_shape) - 2
        if len(node.input) == 3:
            bias_name = node.input[2]
        else:
            bias_name = None

        datatype = input_node.datatype
        dilation = [1] * dims
        stride = [1] * dims
        head = [0] * dims
        tail = [0] * dims
        groups = 1
        autopad = 'NOTSET'

        for attrib in node.attribute:
            if attrib.name == 'dilations':
                for i in range(len(attrib.ints)):
                    dilation[i] = attrib.ints[i]
            elif attrib.name == 'group':
                groups = attrib.i
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    stride[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                pad_length = len(attrib.ints)
                ht_split = pad_length // 2
                for i in range(0, len(attrib.ints)):
                    if i < ht_split:
                        head[i] = attrib.ints[i]
                    else:
                        tail[i-ht_split] = attrib.ints[i]
            elif attrib.name == 'auto_pad':
                autopad = attrib.s.decode('utf-8')

        if autopad in ['SAME_UPPER', 'SAME_LOWER']:
            filt_size = filt_shape[2:2+dims]
            dim_out = []
            dim_in = []
            for i in range(dims):
                dim_out.append(math.ceil(input_shape[2+i] / stride[i]))
                dim_in.append(input_node.shape[2+i])
            for i in range(dims):
                fd = (filt_size[i] - 1) * dilation[i] + 1
                t = (dim_out[i] - 1) * stride[i] + fd - dim_in[i]
                if t > 0:
                    if autopad == 'SAME_UPPER':
                        head[i] = (math.floor(t / 2))
                        tail[i] = (math.ceil(t / 2))
                    else:
                        head[i] = (math.ceil(t / 2))
                        tail[i] = (math.floor(t / 2))

        dim_fd = []
        for i in range(dims):
            dim_fd.append((filt_shape[2+i] - 1) * dilation[i] + 1)

        dim_out_shape = []
        for i in range(dims):
            dim_out_shape.append(int((input_shape[2+i] + head[i] + tail[i] - dim_fd[i]) / stride[i]) + 1) 
        output_shape = [input_shape[0], filt_shape[0]] + dim_out_shape
        conv_format = LayerFormat.NCHW
        if len(output_shape) == 3:
            conv_format = LayerFormat.NCD

        params = {'dilation': dilation,
                  'stride': stride,
                  'head': head,
                  'tail': tail,
                  'groups': groups}
        
        layer = AGLayer(name, op='conv', inputs=[input_name, filt_name],
                        params=params, datatype=datatype, layer_format=conv_format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)

        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(filt_name, name)
        if bias_name != None:
            self.nxgraph.nodes[name]['info'].inputs.append(bias_name)
            self.nxgraph.add_edge(bias_name, name)

    def import_ConvTranspose(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        filt_name = node.input[1]
        filt_shape = self.nxgraph.nodes[filt_name]['output_shape']
        if len(node.input) == 3:
            bias_name = node.input[2]
        else:
            bias_name = None
        datatype = input_node['datatype']
        dilation = [1, 1]
        stride = [1, 1]
        head = [0, 0]
        tail = [0, 0]
        groups = 1
        autopad = 'NOTSET'

        for attrib in node.attribute:
            if attrib.name == 'dilations':
                for i in range(len(attrib.ints)):
                    dilation[i] = attrib.ints[i]
            elif attrib.name == 'group':
                groups = attrib.i
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    stride[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                for i in range(len(attrib.ints)):
                    if i < 2:
                        head[i] = attrib.ints[i]
                    else:
                        tail[i-2] = attrib.ints[i]
            elif attrib.name == 'auto_pad':
                autopad = attrib.s.decode('utf-8')

        if autopad in ['SAME_UPPER', 'SAME_LOWER']:
            filt_size = filt_shape[2:4]
            hw_out = [math.ceil(input_shape[2] / stride[0]), 
                math.ceil(input_shape[3] / stride[1])]
            hw_in = input_node['output_shape'][2:4]
            for i in range(2):
                fd = (filt_size[i] - 1) * dilation[i] + 1
                t = (hw_out[i] - 1) * stride[i] + fd - hw_in[i]
                if t > 0:
                    if autopad == 'SAME_UPPER':
                        head[i] = (math.floor(t / 2))
                        tail[i] = (math.ceil(t / 2))
                    else:
                        head[i] = (math.ceil(t / 2))
                        tail[i] = (math.floor(t / 2))

        w_fd = (filt_shape[2] - 1) * dilation[0] + 1
        h_fd = (filt_shape[3] - 1) * dilation[1] + 1   
        output_width = (stride[0] * (input_shape[2] - 1)) + w_fd - head[0] - tail[0]
        output_height = (stride[1] * (input_shape[3] - 1)) + h_fd - head[1] - tail[1]
        output_shape = [input_shape[0], filt_shape[1], output_width, output_height]

        self.nxgraph.add_node(name,
                              op='transpose_conv',
                              input=input_name,
                              filter=filt_name,
                              dilation=dilation,
                              stride=stride,
                              head=head,
                              tail=tail,
                              groups=groups,
                              datatype=datatype,
                              format='nchw',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(filt_name, name)
        if bias_name != None:
            self.nxgraph.nodes[name]['bias'] = bias_name
            self.nxgraph.add_edge(bias_name, name)

    def import_DequantizeLinear(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        scale_name = node.input[1]
        scale_node = self.nxgraph.nodes[scale_name]['info']
        if 'base_shape' in input_node.params:
            output_shape = input_node['base_shape'][:]
        else:
            # output_shape = input_node['output_shape'][:]
            output_shape = input_node.shape[:]
        # layer_format = input_node['format']
        layer_format = input_node.format
        if len(node.input) == 3:
            zero_name = node.input[2]
            zero_node = self.nxgraph.nodes[zero_name]['info']
            # if 'np_tensor' not in zero_node:
            if zero_node.tensor is None:
                raise ValueError("Cannot retrieve zero point for node %s." % name)
            # zero_point = zero_node['np_tensor']
            zero_point = zero_node.tensor
        else:
            zero_point = np.asarray([0]).astype(np.int32)

        # if 'np_tensor' not in scale_node:
        if scale_node.tensor is None:
            raise ValueError("Cannot retrieve scale for node %s." % name)
        # scale = scale_node['np_tensor']
        scale = scale_node.tensor

        axis = 1
        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i
        if axis < 0:
            axis += len(output_shape)

        layer = AGLayer(name, op='dequant', inputs=[input_name],
                        datatype=np.float32, layer_format=layer_format,
                        shape=output_shape, scale=scale,
                        zero_point=zero_point, quant_axis=axis)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(input_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

    def import_Div(self, node):
        self.import_binary(node, 'div')

    def import_Exp(self, node):
        self.import_unary(node, 'exp')

    def import_Pow(self, node):
        self.import_binary(node, 'pow')

    def import_Expand(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        shape_name = node.input[1]
        shape_node = self.nxgraph.nodes[shape_name]
        datatype = input_node['datatype']
        layer_format = input_node['format']
        ones_shape = list(shape_node['np_tensor'])
        ones_tensor = np.ones(ones_shape).astype(datatype)
        
        self.nxgraph.add_node(name + '_dv_ones',
                              op='constant',
                              datatype=datatype,
                              format='none',
                              output_shape=ones_shape,
                              np_tensor=ones_tensor)

        self.nxgraph.add_node(name,
                              op='mul',
                              x=input_name,
                              y=name + '_dv_ones',
                              datatype=datatype,
                              format=layer_format,
                              output_shape=ones_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(name + '_dv_ones', name)

    def import_Flatten(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        datatype = input_node.datatype
        input_shape = input_node.shape

        axis = 1
        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i
        if axis < 0:
            axis += len(input_shape)
        axis_0 = 1
        axis_1 = 1
        
        for i in range(0, axis):
            axis_0 *= input_shape[i]
        for i in range(axis, len(input_shape)):
            axis_1 *= input_shape[i]
        output_shape = [axis_0, axis_1]

        layer = AGLayer(name, op='reshape', inputs=[input_name],
                        datatype=datatype, shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(input_name, name)

        if input_node.quant_scale is not None and input_node.zero_point is not None:
            self.nxgraph.nodes[name]['info'].quant_scale = input_node.quant_scale
            self.nxgraph.nodes[name]['info'].zero_point = input_node.zero_point
            self.nxgraph.nodes[name]['info'].quant_axis = input_node.quant_axis

        if input_node.tensor is not None:
            out_tensor = np.reshape(input_node.tensor, output_shape)
            self.nxgraph.nodes[name]['info'].tensor = out_tensor

    def import_Gather(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        indices_name = node.input[1]
        indices_node = self.nxgraph.nodes[indices_name]
        datatype = input_node['datatype']

        axis = 0
        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i

        if 'np_tensor' not in indices_node:
            raise ValueError("Unable to determine Gather op output.")
        
        if 'np_tensor' in input_node:
            # TODO: Fix as this does not fully represent Gather
            np_tensor = np.take(input_node['np_tensor'], indices_node['np_tensor'], axis)

            self.nxgraph.add_node(name,
                                op='constant',
                                datatype=datatype,
                                output_shape=list(np_tensor.shape),
                                format='none',
                                np_tensor=np_tensor)
            
        else:
            if 'base_shape' in input_node:
                input_shape = input_node['base_shape']
            else:
                input_shape = input_node['output_shape']

            if axis == 0:
                if len(indices_node['output_shape']) == 1 and indices_node['output_shape'][0] == 1:
                    axes = list(range(len(input_shape)))
                    begin = [0] * len(input_shape)
                    begin[0] = indices_node['np_tensor'][0]
                    end = input_shape[:]
                    end[0] = begin[0] + 1
                    output_shape = input_shape[:]
                    output_shape[0] = 1
                    self.nxgraph.add_node(name + '_slice',
                                          op='slice',
                                          input=input_name,
                                          axes=axes,
                                          begin=begin,
                                          end=end,
                                          datatype=datatype,
                                          format='none',
                                          output_shape=output_shape)
                    self.nxgraph.add_edge(input_name, name + '_slice')

                    self.nxgraph.add_node(name,
                                          op='reshape',
                                          input=name + '_slice',
                                          datatype=datatype,
                                          format='none',
                                          output_shape=output_shape[1:])
                    self.nxgraph.add_edge(name + '_slice', name)

    def import_Gemm(self, node):
        name = node.output[0]
        a_name = node.input[0]
        a_node = self.nxgraph.nodes[a_name]['info']
        a_shape = a_node.shape
        b_name = node.input[1]
        b_node = self.nxgraph.nodes[b_name]['info']
        b_shape = b_node.shape
        if len(node.input) == 3:
            bias_name = node.input[2]
        else:
            bias_name = None
        datatype = a_node.datatype

        trans_a = False
        trans_b = False
        for attrib in node.attribute:
            if attrib.name == 'transA':
                trans_a = bool(attrib.i)
            if attrib.name == 'transB':
                trans_b = bool(attrib.i)

        output_shape = []
        if trans_a:
            output_shape.append(a_shape[-1])
        else:
            output_shape.append(a_shape[0])
        if trans_b:
            output_shape.append(b_shape[0])
        else:
            output_shape.append(b_shape[-1])

        op = 'dense'
        if not trans_a and trans_b:
            op = 'linear'

        params = {'transposeA': trans_a,
                  'transposeB': trans_b}
        layer = AGLayer(name, op=op, inputs=[a_name, b_name],
                        params=params, datatype=datatype,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(a_name, name)
        self.nxgraph.add_edge(b_name, name)
        if bias_name != None:
            self.nxgraph.nodes[name]['info'].inputs.append(bias_name)
            self.nxgraph.add_edge(bias_name, name)
        
    def import_GlobalAveragePool(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        size = input_shape[2:]
        strides = [1] * (len(input_shape) - 2)
        output_shape = input_shape[:]
        for i in range(2, len(output_shape)):
            output_shape[i] = 1
        head = [0] * (len(output_shape) - 2)
        tail = [0] * (len(output_shape) - 2)

        params = {'size': size,
                  'stride': strides,
                  'head': head,
                  'tail': tail}
        layer = AGLayer(name, op='avg_pool', inputs=[input_name],
                        params=params, datatype=datatype, layer_format=input_node.format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(input_name, name)

    def import_GRU(self, node):
        concat_name = node.output[0]
        name = node.output[1]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = input_node['datatype']
        w_name = node.input[1]
        w_node = self.nxgraph.nodes[w_name]
        r_name = node.input[2]
        r_node = self.nxgraph.nodes[r_name]
        b_name = node.input[3]
        b_node = self.nxgraph.nodes[b_name]
        h_name = node.input[5]
        h_node = self.nxgraph.nodes[h_name]
        hidden_size = h_node['output_shape'][-1]
        linear_before_reset = 0
        batch_size = input_shape[1]
        seq_len = input_shape[0]

        for attrib in node.attribute:
            if attrib.name == 'hidden_size':
                hidden_size = attrib.i
            if attrib.name == 'linear_before_reset':
                linear_before_reset = attrib.i

        ones_name = name + '_dv_gru_ones'
        gru_ones = np.ones([1,hidden_size]).astype(np.float32)
        self.nxgraph.add_node(ones_name,
                              op='constant',
                              datatype=datatype,
                              format='none',
                              output_shape=list(gru_ones.shape),
                              np_tensor=gru_ones)

        self.nxgraph.add_node(name + '_dv_gru_init_h',
                              op='reshape',
                              input=h_name,
                              datatype=datatype,
                              format='none',
                              output_shape=[h_node['output_shape'][0] * h_node['output_shape'][1], 
                                            h_node['output_shape'][2]]
                             )
        self.nxgraph.add_edge(h_name, name + '_dv_gru_init_h')
        h_list = [name + '_dv_gru_init_h']

        w_tensor = w_node['np_tensor']
        w_tensor = np.squeeze(w_tensor)
        w_z = w_tensor[:hidden_size]
        w_z = np.transpose(w_z, [1,0])
        w_r = w_tensor[hidden_size:2*hidden_size]
        w_r = np.transpose(w_r, [1,0])
        w_h = w_tensor[2*hidden_size:]
        w_h = np.transpose(w_h, [1,0])

        w_z_name = name + '_dv_wz'
        w_r_name = name + '_dv_wr'
        w_h_name = name + '_dv_wh'

        self.nxgraph.add_node(w_z_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(w_z.shape),
                              np_tensor=w_z)
        
        self.nxgraph.add_node(w_r_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(w_r.shape),
                              np_tensor=w_r)
        
        self.nxgraph.add_node(w_h_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(w_h.shape),
                              np_tensor=w_h)
        
        r_tensor = r_node['np_tensor']
        r_tensor = np.squeeze(r_tensor)
        r_z = r_tensor[:hidden_size]
        r_z = np.transpose(r_z, [1,0])
        r_r = r_tensor[hidden_size:2*hidden_size]
        r_r = np.transpose(r_r, [1,0])
        r_h = r_tensor[2*hidden_size:]
        r_h = np.transpose(r_h, [1,0])

        r_z_name = name + '_dv_rz'
        r_r_name = name + '_dv_rr'
        r_h_name = name + '_dv_rh'

        self.nxgraph.add_node(r_z_name,
                              op='constant',
                              datatype=r_node['datatype'],
                              format='none',
                              output_shape=list(r_z.shape),
                              np_tensor=r_z)
        
        self.nxgraph.add_node(r_r_name,
                              op='constant',
                              datatype=r_node['datatype'],
                              format='none',
                              output_shape=list(r_r.shape),
                              np_tensor=r_r)
        
        self.nxgraph.add_node(r_h_name,
                              op='constant',
                              datatype=r_node['datatype'],
                              format='none',
                              output_shape=list(r_h.shape),
                              np_tensor=r_h)
        
        b_tensor = b_node['np_tensor']
        b_tensor = np.squeeze(b_tensor)
        wb_z = b_tensor[:hidden_size]
        wb_r = b_tensor[hidden_size:2*hidden_size]
        wb_h = b_tensor[2*hidden_size:3*hidden_size]
        rb_z = b_tensor[3*hidden_size:4*hidden_size]
        rb_r = b_tensor[4*hidden_size:5*hidden_size]
        rb_h = b_tensor[5*hidden_size:]

        b_z = wb_z + rb_z
        b_r = wb_r + rb_r
        b_h = wb_h + rb_h

        b_z_name = name + '_dv_bz'
        b_r_name = name + '_dv_br'
        b_wh_name = name + '_dv_bwh'
        b_rh_name = name + '_dv_brh'
        b_h_name = name + '_dv_bh'

        self.nxgraph.add_node(b_z_name,
                              op='constant',
                              datatype=b_node['datatype'],
                              format='none',
                              output_shape=list(b_z.shape),
                              np_tensor=b_z)
        
        self.nxgraph.add_node(b_r_name,
                              op='constant',
                              datatype=b_node['datatype'],
                              format='none',
                              output_shape=list(b_r.shape),
                              np_tensor=b_r)
        
        self.nxgraph.add_node(b_h_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(b_h.shape),
                              np_tensor=b_h)
        
        self.nxgraph.add_node(b_wh_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(wb_h.shape),
                              np_tensor=wb_h)
        
        self.nxgraph.add_node(b_rh_name,
                              op='constant',
                              datatype=w_node['datatype'],
                              format='none',
                              output_shape=list(rb_h.shape),
                              np_tensor=rb_h)

        for i in range(seq_len):
            slice_name = name + '_dv_gru_inp_slice_' + str(i)
            self.nxgraph.add_node(slice_name,
                                  op='slice',
                                  input=input_name,
                                  axes=[0,1,2],
                                  begin=[i,0,0],
                                  end=[i+1,input_shape[1], input_shape[2]],
                                  strides=[1,1,1],
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[1, batch_size, input_shape[2]])
            self.nxgraph.add_edge(input_name, slice_name)

            reshape_name = name + '_dv_gru_inp_reshape_' + str(i)
            self.nxgraph.add_node(reshape_name,
                                  op='reshape',
                                  input=slice_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, input_shape[2]])
            self.nxgraph.add_edge(slice_name, reshape_name)

            # zt = f(Xt*(Wz^T) + Ht-1*(Rz^T) + Wbz + Rbz)
            zt1_name = name + '_dv_gru_zt1_' + str(i)
            self.nxgraph.add_node(zt1_name,
                                  op='dense',
                                  A=reshape_name,
                                  B=w_z_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(reshape_name, zt1_name)
            self.nxgraph.add_edge(w_z_name, zt1_name)

            zt2_name = name + '_dv_gru_zt2_' + str(i)
            self.nxgraph.add_node(zt2_name,
                                  op='dense',
                                  A=h_list[-1],
                                  B=r_z_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(h_list[-1], zt2_name)
            self.nxgraph.add_edge(r_z_name, zt2_name)

            zt3_name = name + '_dv_gru_zt3_' + str(i)
            self.nxgraph.add_node(zt3_name,
                                  op='add',
                                  x=zt1_name,
                                  y=zt2_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(zt1_name, zt3_name)
            self.nxgraph.add_edge(zt2_name, zt3_name)

            zt4_name = name + '_dv_gru_zt4_' + str(i)
            self.nxgraph.add_node(zt4_name,
                                  op='add',
                                  x=zt3_name,
                                  y=b_z_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(zt3_name, zt4_name)
            self.nxgraph.add_edge(b_z_name, zt4_name)

            zt_name = name + '_dv_gru_zt_' + str(i)
            self.nxgraph.add_node(zt_name,
                                  op='sigmoid',
                                  x=zt4_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(zt4_name, zt_name)

            # rt = f(Xt*(Wr^T) + Ht-1*(Rr^T) + Wbr + Rbr)
            rt1_name = name + '_dv_gru_rt1_' + str(i)
            self.nxgraph.add_node(rt1_name,
                                  op='dense',
                                  A=reshape_name,
                                  B=w_r_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(reshape_name, rt1_name)
            self.nxgraph.add_edge(w_r_name, rt1_name)

            rt2_name = name + '_dv_gru_rt2_' + str(i)
            self.nxgraph.add_node(rt2_name,
                                  op='dense',
                                  A=h_list[-1],
                                  B=r_r_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(h_list[-1], rt2_name)
            self.nxgraph.add_edge(r_r_name, rt2_name)

            rt3_name = name + '_dv_gru_rt3_' + str(i)
            self.nxgraph.add_node(rt3_name,
                                  op='add',
                                  x=rt1_name,
                                  y=rt2_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(rt1_name, rt3_name)
            self.nxgraph.add_edge(rt2_name, rt3_name)

            rt4_name = name + '_dv_gru_rt4_' + str(i)
            self.nxgraph.add_node(rt4_name,
                                  op='add',
                                  x=rt3_name,
                                  y=b_r_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(rt3_name, rt4_name)
            self.nxgraph.add_edge(b_r_name, rt4_name)

            rt_name = name + '_dv_gru_rt_' + str(i)
            self.nxgraph.add_node(rt_name,
                                  op='sigmoid',
                                  x=rt4_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(rt4_name, rt_name)

            ht1_name = name + '_dv_gru_ht1_' + str(i)
            self.nxgraph.add_node(ht1_name,
                                  op='dense',
                                  A=reshape_name,
                                  B=w_h_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(reshape_name, ht1_name)
            self.nxgraph.add_edge(w_h_name, ht1_name)

            ht_name = name + '_dv_gru_ht_' + str(i)
            
            if linear_before_reset:
                # ht = g(Xt*(Wh^T) + (rt (.) (Ht-1*(Rh^T) + Rbh)) + Wbh)
                ht2_name = name + '_dv_gru_ht2_' + str(i)
                self.nxgraph.add_node(ht2_name,
                                      op='dense',
                                      A=h_list[-1],
                                      B=r_h_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(h_list[-1], ht2_name)
                self.nxgraph.add_edge(r_h_name, ht2_name)

                ht3_name = name + '_dv_gru_ht3_' + str(i)
                self.nxgraph.add_node(ht3_name,
                                      op='add',
                                      x=ht2_name,
                                      y=b_rh_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht2_name, ht3_name)
                self.nxgraph.add_edge(b_rh_name, ht3_name)

                ht4_name = name + '_dv_gru_ht4_' + str(i)
                self.nxgraph.add_node(ht4_name,
                                      op='mul',
                                      x=rt_name,
                                      y=ht3_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(rt_name, ht4_name)
                self.nxgraph.add_edge(ht3_name, ht4_name)

                ht5_name = name + '_dv_gru_ht5_' + str(i)
                self.nxgraph.add_node(ht5_name,
                                      op='add',
                                      x=ht1_name,
                                      y=ht4_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht1_name, ht5_name)
                self.nxgraph.add_edge(ht4_name, ht5_name)

                ht6_name = name + '_dv_gru_ht6_' + str(i)
                self.nxgraph.add_node(ht6_name,
                                      op='add',
                                      x=ht5_name,
                                      y=b_wh_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht5_name, ht6_name)
                self.nxgraph.add_edge(b_wh_name, ht6_name)

                self.nxgraph.add_node(ht_name,
                                      op='tanh',
                                      x=ht6_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht6_name, ht_name)
            else:
                # ht = g(Xt*(Wh^T) + (rt (.) Ht-1)*(Rh^T) + Rbh + Wbh)
                ht2_name = name + '_dv_gru_ht2_' + str(i)
                self.nxgraph.add_node(ht2_name,
                                      op='mul',
                                      x=rt_name,
                                      y=h_list[-1],
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(rt_name, ht2_name)
                self.nxgraph.add_edge(h_list[-1], ht2_name)

                ht3_name = name + '_dv_gru_ht3_' + str(i)
                self.nxgraph.add_node(ht3_name,
                                      op='dense',
                                      A=ht2_name,
                                      B=r_h_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht2_name, ht3_name)
                self.nxgraph.add_edge(r_h_name, ht3_name)

                ht4_name = name + '_dv_gru_ht4_' + str(i)
                self.nxgraph.add_node(ht4_name,
                                      op='add',
                                      x=ht3_name,
                                      y=b_rh_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht3_name, ht4_name)
                self.nxgraph.add_edge(b_rh_name, ht4_name)

                ht5_name = name + '_dv_gru_ht5_' + str(i)
                self.nxgraph.add_node(ht5_name,
                                      op='add',
                                      x=ht1_name,
                                      y=ht4_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht1_name, ht5_name)
                self.nxgraph.add_edge(ht4_name, ht5_name)

                ht6_name = name + '_dv_gru_ht6_' + str(i)
                self.nxgraph.add_node(ht6_name,
                                      op='add',
                                      x=ht5_name,
                                      y=b_wh_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht5_name, ht6_name)
                self.nxgraph.add_edge(b_wh_name, ht6_name)

                self.nxgraph.add_node(ht_name,
                                      op='tanh',
                                      x=ht6_name,
                                      datatype=datatype,
                                      format='none',
                                      output_shape=[batch_size, hidden_size])
                self.nxgraph.add_edge(ht6_name, ht_name)

            # Ht = (1 - zt) (.) ht + zt (.) Ht-1
            bigHt_name = name + '_dv_gru_Ht_' + str(i)
            bigHt1_name = name + '_dv_gru_Ht1_' + str(i)
            self.nxgraph.add_node(bigHt1_name,
                                  op='sub',
                                  x=ones_name,
                                  y=zt_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(ones_name, bigHt1_name)
            self.nxgraph.add_edge(zt_name, bigHt1_name)

            bigHt2_name = name + '_dv_gru_Ht2_' + str(i)
            self.nxgraph.add_node(bigHt2_name,
                                  op='mul',
                                  x=bigHt1_name,
                                  y=ht_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(bigHt1_name, bigHt2_name)
            self.nxgraph.add_edge(ht_name, bigHt2_name)

            bigHt3_name = name + '_dv_gru_Ht3_' + str(i)
            self.nxgraph.add_node(bigHt3_name,
                                  op='mul',
                                  x=zt_name,
                                  y=h_list[-1],
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(zt_name, bigHt3_name)
            self.nxgraph.add_edge(h_list[-1], bigHt3_name)

            self.nxgraph.add_node(bigHt_name,
                                  op='add',
                                  x=bigHt2_name,
                                  y=bigHt3_name,
                                  datatype=datatype,
                                  format='none',
                                  output_shape=[batch_size, hidden_size])
            self.nxgraph.add_edge(bigHt2_name, bigHt_name)
            self.nxgraph.add_edge(bigHt3_name, bigHt_name)
            h_list.append(bigHt_name)

        self.nxgraph.add_node(name,
                              op='reshape',
                              input=bigHt_name,
                              datatype=datatype,
                              format='none',
                              output_shape=[1, batch_size, hidden_size])
        self.nxgraph.add_edge(bigHt_name, name)

        if len(h_list) > 2:
            self.nxgraph.add_node(concat_name + '_dv_gru_concat',
                                op='concat',
                                values=h_list[:-1],
                                axis=0,
                                datatype=datatype,
                                format='none',
                                output_shape=[len(h_list)-1,hidden_size])
            for conc_val in h_list[:-1]:
                self.nxgraph.add_edge(conc_val, concat_name + '_dv_gru_concat')
            
            self.nxgraph.add_node(concat_name,
                                op='reshape',
                                input=concat_name + '_dv_gru_concat',
                                datatype=datatype,
                                format='none',
                                output_shape=[len(h_list)-1, 1, batch_size, hidden_size])
            self.nxgraph.add_edge(concat_name + '_dv_gru_concat', concat_name)
        
        else:
            self.nxgraph.add_node(concat_name,
                                op='reshape',
                                input=h_list[0],
                                datatype=datatype,
                                format='none',
                                output_shape=[1, 1, batch_size, hidden_size])
            self.nxgraph.add_edge(h_list[0], concat_name)

    def import_Identity(self, node):
        name = node.output[0]
        input_name = node.input[0]

        self.nxgraph.add_node(name)
        for key, val in self.nxgraph.nodes[input_name].items():
            self.nxgraph.nodes[name][key] = val
        for in_edge in self.nxgraph.in_edges(input_name):
            self.nxgraph.add_edge(in_edge[0], name)

    def import_Log(self, node):
        self.import_unary(node, 'log')

    def import_LeakyRelu(self, node):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]
        datatype = x_node['datatype']
        layer_format = x_node['format']
        output_shape = x_node['output_shape'][:]

        alpha = 0.01
        for attrib in node.attribute:
            if attrib.name == 'alpha':
                alpha = attrib.f

        self.nxgraph.add_node(name,
                              op='leaky_relu',
                              x=x_name,
                              alpha=alpha,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, name)

    def import_MatMul(self, node):
        name = node.output[0]
        a_name = node.input[0]
        b_name = node.input[1]
        a_shape = self.nxgraph.nodes[a_name]['output_shape']
        b_shape = self.nxgraph.nodes[b_name]['output_shape']
        datatype = self.nxgraph.nodes[a_name]['datatype']
        output_shape = a_shape[:-1] + [b_shape[-1]]
        
        self.nxgraph.add_node(name,
                              op='matmul',
                              A=a_name,
                              B=b_name,
                              transposeA=False,
                              transposeB=False,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(a_name, name)
        self.nxgraph.add_edge(b_name, name)

    def import_MaxPool(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        dims = len(input_shape) - 2
        size = [1] * dims
        strides = [1] * dims
        head = [0] * dims
        tail = [0] * dims

        for attrib in node.attribute:
            if attrib.name == 'kernel_shape':
                for i in range(len(attrib.ints)):
                    size[i] = attrib.ints[i]
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    strides[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                for i in range(len(attrib.ints)):
                    pad_length = len(attrib.ints)
                    ht_split = pad_length // 2
                    for i in range(0, len(attrib.ints)):
                        if i < ht_split:
                            head[i] = attrib.ints[i]
                        else:
                            tail[i-ht_split] = attrib.ints[i]

        output_shape = input_shape[:]
        for i in range(2, len(output_shape)):
            output_shape[i] = math.floor((input_shape[i] + head[i-2] + tail[i-2] - size[i-2]) / strides[i-2] + 1)

        params = {'size': size,
                  'stride': strides,
                  'head': head,
                  'tail': tail}
        layer = AGLayer(name, op='max_pool', inputs=[input_name],
                        params=params, datatype=datatype, layer_format=input_node.format,
                        shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        self.nxgraph.add_edge(input_name, name)

    def import_Mod(self, node):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]
        m_name = node.input[1]
        m_node = self.nxgraph.nodes[m_name]
        x_val = x_node['np_tensor'][0]
        m_val = m_node['np_tensor'][0]
        result_array = np.asarray([x_val % m_val]).astype(np.int64)

        self.nxgraph.add_node(name,
                              op='constant',
                              datatype=np.int64,
                              format='none',
                              output_shape=[1],
                              np_tensor=result_array)

    def import_Mul(self, node):
        self.import_binary(node, 'mul')

    def import_Pad(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        pad_amount = None
        if len(node.input) == 1:
            pad_amount = [0]*len(input_node['output_shape'])*2
        else:
            pad_name = node.input[1]
            pad_node = self.nxgraph.nodes[pad_name]
            pad_amount = pad_node['np_tensor']
        layer_format = input_node['format']
        
        pad_value = 0
        if len(node.input) == 3:
            pad_val_node = self.nxgraph.nodes[node.input[2]]
            if 'np_tensor' not in pad_val_node:
                print("WARNING: Unable to determine pad value. "
                    "Defaulting to 0.")
            else:
                pad_value = pad_val_node['np_tensor'][0]
        pad_type = 'constant'

        for attrib in node.attribute:   
            if attrib.name == 'mode':
                pad_type = attrib.s.decode('utf-8')
            if attrib.name == 'pads':
                pad_amount = list(attrib.ints)
        
        if pad_type != 'constant':
            raise ValueError("Unable to support pad type %s." % pad_type)

        if pad_amount is None:
            raise ValueError("Cannot get pad shapes for node %s." % name)
        head = [0] * len(input_node['output_shape'])
        tail = [0] * len(input_node['output_shape'])
        for i in range(len(pad_amount)):
            if i < len(input_node['output_shape']):
                head[i] = pad_amount[i]
            else:
                tail[i - len(input_node['output_shape'])] = pad_amount[i]

        output_shape = []
        i = 0
        for dim in input_node['output_shape']:
            output_shape.append(dim + head[i] + tail[i])
            i += 1

        self.nxgraph.add_node(name,
                              op='pad',
                              input=input_name,
                              head=head,
                              tail=tail,
                              value=pad_value,
                              datatype=input_node['datatype'],
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

    def import_QGemm(self, node):
        name = node.output[0]
        a_name = node.input[0]
        a_node = self.nxgraph.nodes[a_name]
        a_shape = a_node['output_shape']
        b_name = node.input[3]
        b_node = self.nxgraph.nodes[b_name]
        b_shape = b_node['output_shape']
        if len(node.input) == 9:
            bias_name = node.input[6]
        else:
            bias_name = None
        datatype = a_node['datatype']

        alpha = 1
        trans_a = False
        trans_b = False
        for attrib in node.attribute:
            if attrib.name == 'transA':
                trans_a = bool(attrib.i)
            if attrib.name == 'transB':
                trans_b = bool(attrib.i)
            if attrib.name == 'alpha':
                alpha = attrib.f

        if alpha != 1:
            raise ValueError("Support not implemented for scaled QGemm calls")

        output_shape = []
        if trans_a:
            output_shape.append(a_shape[-1])
        else:
            output_shape.append(a_shape[0])
        if trans_b:
            output_shape.append(b_shape[0])
        else:
            output_shape.append(b_shape[-1])

        self.nxgraph.add_node(name,
                              op='matmul',
                              A=a_name,
                              B=b_name,
                              transposeA=trans_a,
                              transposeB=trans_b,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(a_name, name)
        self.nxgraph.add_edge(b_name, name)
        if bias_name != None:
            self.nxgraph.nodes[name]['bias'] = bias_name
            self.nxgraph.add_edge(bias_name, name)
            bias_node = self.nxgraph.nodes[bias_name]
            bias_node['quant_scale'] = self.nxgraph.nodes[node.input[7]]['np_tensor']
            bias_node['zero_point'] = self.nxgraph.nodes[node.input[8]]['np_tensor']
            bias_node['quant_axis'] = 0


        a_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        a_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        a_node['quant_axis'] = 0
        b_node['quant_scale'] = self.nxgraph.nodes[node.input[4]]['np_tensor']
        b_node['zero_point'] = self.nxgraph.nodes[node.input[5]]['np_tensor']
        b_node['quant_axis'] = 0

    def import_QLinearAdd(self, node):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]
        if 'base_shape' in x_node:
            x_shape = x_node['base_shape']
        else:
            x_shape = x_node['output_shape']
        y_name = node.input[3]
        y_node = self.nxgraph.nodes[y_name]
        if 'base_shape' in y_node:
            y_shape = y_node['base_shape']
        else:
            y_shape = y_node['output_shape']
        if x_node['op'] != 'constant':
            datatype = x_node['datatype']
        else:
            datatype = y_node['datatype']
        output_shape = self.calc_binary_shape(x_shape, y_shape)
        if x_node['output_shape'] == output_shape:
            layer_format = x_node['format']
        else:
            layer_format = y_node['format']

        self.nxgraph.add_node(name,
                              op='add',
                              x=x_name,
                              y=y_name,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[6]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[7]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        x_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        x_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        x_node['quant_axis'] = 0
        y_node['quant_scale'] = self.nxgraph.nodes[node.input[4]]['np_tensor']
        y_node['zero_point'] = self.nxgraph.nodes[node.input[5]]['np_tensor']
        y_node['quant_axis'] = 0

    def import_QLinearAveragePool(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = input_node['datatype']
        size = [1, 1]
        strides = [1, 1]
        head = [0, 0]
        tail = [0, 0]
        autopad = 'NOTSET'

        for attrib in node.attribute:
            if attrib.name == 'kernel_shape':
                for i in range(len(attrib.ints)):
                    size[i] = attrib.ints[i]
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    strides[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                for i in range(len(attrib.ints)):
                    if i < 2:
                        head[i] = attrib.ints[i]
                    else:
                        tail[i-2] = attrib.ints[i]
            elif attrib.name == 'auto_pad':
                autopad = attrib.s.decode('utf-8')

        if autopad != 'NOTSET':
            print("WARNING: Auto Padding not currently supported for QLinearAveragePool")

        output_shape = input_shape[:]
        output_shape[2] = math.floor((input_shape[2] + head[0] + tail[0] - size[0]) / strides[0] + 1)
        output_shape[3] = math.floor((input_shape[3] + head[1] + tail[1] - size[1]) / strides[1] + 1)

        self.nxgraph.add_node(name,
                              op='avg_pool',
                              input=input_name,
                              size=size,
                              stride=strides,
                              head=head,
                              tail=tail,
                              datatype=datatype,
                              format=input_node['format'],
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[3]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[4]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(input_name, name)

        input_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        input_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        input_node['quant_axis'] = 0

    def import_QLinearGlobalAveragePool(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = input_node['datatype']

        channels_last = False
        for attrib in node.attribute:
            if attrib.name == 'channels_last' and attrib.i != 0:
                channels_last = True

        strides = [1, 1]
        output_shape = input_shape[:]
        if channels_last:
            size = input_shape[1:3]
            output_shape[1] = 1
            output_shape[2] = 1
        else:
            size = input_shape[2:]
            output_shape[2] = 1
            output_shape[3] = 1

        self.nxgraph.add_node(name,
                              op='avg_pool',
                              input=input_name,
                              size=size,
                              stride=strides,
                              head=[0,0],
                              tail=[0,0],
                              datatype=datatype,
                              format=input_node['format'],
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[3]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[4]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(input_name, name)

        input_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        input_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        input_node['quant_axis'] = 0

    def import_QLinearConcat(self, node):
        name = node.output[0]
        value_names = []
        value_nodes = []
        for i in range(2, len(node.input), 3):
            value_names.append(node.input[i])
            val_node = self.nxgraph.nodes[value_names[-1]]
            if 'quant_scale' not in val_node:
                scale_node = self.nxgraph.nodes[node.input[i+1]]
                val_node['quant_scale'] = scale_node['np_tensor']
            if 'zero_point' not in val_node:
                zero_node = self.nxgraph.nodes[node.input[i+2]]
                val_node['zero_point'] = zero_node['np_tensor']
            if 'quant_axis' not in val_node:
                val_node['quant_axis'] = 0
            value_nodes.append(self.nxgraph.nodes[node.input[i]])
        datatype = value_nodes[0]['datatype']
        axis = 0

        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i

        if 'base_shape' in value_nodes[0]:
            output_shape = value_nodes[0]['base_shape'][:]
        else:
            output_shape = value_nodes[0]['output_shape'][:]
        if axis < 0:
            axis += len(output_shape)
        for i in range(1, len(value_nodes)):
            if 'base_shape' in value_nodes[i]:
                output_shape[axis] += value_nodes[i]['base_shape'][axis]
            else:
                output_shape[axis] += value_nodes[i]['output_shape'][axis]

        all_nchw = True
        all_nhwc = True
        for val_node in value_nodes:
            if val_node['format'] != 'nchw':
                all_nchw = False
            if val_node['format'] != 'nhwc':
                all_nhwc = False
        if all_nchw:
            conc_format = 'nchw'
        elif all_nhwc:
            conc_format = 'nhwc'
        else:
            conc_format = 'none'

        self.nxgraph.add_node(name,
                              op='concat',
                              values=value_names,
                              axis=axis,
                              datatype=datatype,
                              format=conc_format,
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[0]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[1]]['np_tensor'],
                              quant_axis=0)
        for in_name in value_names:
            self.nxgraph.add_edge(in_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1 and axis != 0:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
                self.nxgraph.nodes[name]['base_axis'] = axis
                self.nxgraph.nodes[name]['axis'] = axis - 1
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        calc_node = True
        for val_node in value_nodes:
            if 'np_tensor' not in val_node:
                calc_node = False
                break

        if calc_node:
            value_tensors = []
            for val_node in value_nodes:
                value_tensors.append(val_node['np_tensor'].copy())
            out_tensor = np.concatenate(value_tensors, axis=axis)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor


    def import_QLinearConv(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        filt_name = node.input[3]
        filt_node = self.nxgraph.nodes[filt_name]
        filt_shape = filt_node['output_shape']
        if len(node.input) == 9:
            bias_name = node.input[8]
        else:
            bias_name = None
        datatype = input_node['datatype']
        dilation = [1, 1]
        stride = [1, 1]
        head = [0, 0]
        tail = [0, 0]
        groups = 1
        autopad = 'NOTSET'

        for attrib in node.attribute:
            if attrib.name == 'dilations':
                for i in range(len(attrib.ints)):
                    dilation[i] = attrib.ints[i]
            elif attrib.name == 'group':
                groups = attrib.i
            elif attrib.name == 'strides':
                for i in range(len(attrib.ints)):
                    stride[i] = attrib.ints[i]
            elif attrib.name == 'pads':
                for i in range(len(attrib.ints)):
                    if i < 2:
                        head[i] = attrib.ints[i]
                    else:
                        tail[i-2] = attrib.ints[i]
            elif attrib.name == 'auto_pad':
                autopad = attrib.s.decode('utf-8')

        if autopad in ['SAME_UPPER', 'SAME_LOWER']:
            filt_size = filt_shape[2:4]
            hw_out = [math.ceil(input_shape[2] / stride[0]), 
                math.ceil(input_shape[3] / stride[1])]
            hw_in = input_node['output_shape'][2:4]
            for i in range(2):
                fd = (filt_size[i] - 1) * dilation[i] + 1
                t = (hw_out[i] - 1) * stride[i] + fd - hw_in[i]
                if t > 0:
                    if autopad == 'SAME_UPPER':
                        head[i] = (math.floor(t / 2))
                        tail[i] = (math.ceil(t / 2))
                    else:
                        head[i] = (math.ceil(t / 2))
                        tail[i] = (math.floor(t / 2))
            

        w_fd = (filt_shape[2] - 1) * dilation[0] + 1
        h_fd = (filt_shape[3] - 1) * dilation[1] + 1   
        output_width = int((input_shape[2] + head[0] + tail[0] - w_fd) / stride[0]) + 1
        output_height = int((input_shape[3] + head[1] + tail[1] - h_fd) / stride[1]) + 1
        output_shape = [input_shape[0], filt_shape[0], output_width, output_height]

        self.nxgraph.add_node(name,
                              op='conv',
                              input=input_name,
                              filter=filt_name,
                              dilation=dilation,
                              stride=stride,
                              head=head,
                              tail=tail,
                              groups=groups,
                              datatype=datatype,
                              format='nchw',
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[6]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[7]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(filt_name, name)
        if bias_name != None:
            bias_node = self.nxgraph.nodes[bias_name]
            bias_out_edges = list(self.nxgraph.out_edges(bias_name))
            if len(bias_out_edges) >= 1:
                counter = 1
                while (bias_name + '_' + str(counter)) in self.nxgraph.nodes:
                    counter += 1
                bias_name += '_' + str(counter)
                self.nxgraph.add_node(bias_name)
                for key, val in bias_node.items():
                    self.nxgraph.nodes[bias_name][key] = val
                bias_node = self.nxgraph.nodes[bias_name]

            self.nxgraph.nodes[name]['bias'] = bias_name
            self.nxgraph.add_edge(bias_name, name)
            bias_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor'] * \
                self.nxgraph.nodes[node.input[4]]['np_tensor']
            bias_node['zero_point'] = np.asarray([0] * len(bias_node['quant_scale'])).astype(bias_node['datatype'])
            bias_node['quant_axis'] = 0

        input_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        input_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        input_node['quant_axis'] = 0
        filt_node['quant_scale'] = self.nxgraph.nodes[node.input[4]]['np_tensor']
        filt_node['zero_point'] = self.nxgraph.nodes[node.input[5]]['np_tensor']
        filt_node['quant_axis'] = 0

    def import_QLinearLeakyRelu(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        output_shape = input_node['output_shape'][:]
        datatype = input_node['datatype']

        alpha = 0.1
        for attrib in node.attribute:
            if attrib.name == 'alpha':
                alpha = attrib.f

        self.nxgraph.add_node(name,
                              op='leaky_relu',
                              x=input_name,
                              alpha=alpha,
                              datatype=datatype,
                              format=input_node['format'],
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[3]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[4]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(input_name, name)

        input_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        input_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        input_node['quant_axis'] = 0

    def import_QLinearMatMul(self, node):
        name = node.output[0]
        a_name = node.input[0]
        a_node = self.nxgraph.nodes[a_name]
        b_name = node.input[3]
        b_node = self.nxgraph.nodes[b_name]
        a_shape = self.nxgraph.nodes[a_name]['output_shape']
        b_shape = self.nxgraph.nodes[b_name]['output_shape']
        datatype = self.nxgraph.nodes[a_name]['datatype']

        orig_output_shape = a_shape[:-1] + [b_shape[-1]]

        reshape_a = True
        if len(a_shape) > 2:
            for i in range(len(a_shape) - 2):
                if a_shape[i] != 1:
                    reshape_a = False
                    break
        else:
            reshape_a = False
        
        if reshape_a:
            self.nxgraph.add_node(a_name + '_dv_matmul_reshape',
                                op='reshape',
                                input=a_name,
                                datatype=a_node['datatype'],
                                format='none',
                                output_shape=a_shape[-2:])
            self.nxgraph.add_edge(a_name, a_name + '_dv_matmul_reshape')
            a_name = a_name + '_dv_matmul_reshape'
            a_shape = a_shape[-2:]
            a_node = self.nxgraph.nodes[a_name]

        output_shape = a_shape[:-1] + [b_shape[-1]]

        
        self.nxgraph.add_node(name + '_dv_batch_matmul',
                              op='matmul',
                              A=a_name,
                              B=b_name,
                              transposeA=False,
                              transposeB=False,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[6]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[7]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(a_name, name + '_dv_batch_matmul')
        self.nxgraph.add_edge(b_name, name + '_dv_batch_matmul')

        a_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        a_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        a_node['quant_axis'] = 0
        b_node['quant_scale'] = self.nxgraph.nodes[node.input[4]]['np_tensor']
        b_node['zero_point'] = self.nxgraph.nodes[node.input[5]]['np_tensor']
        b_node['quant_axis'] = 0

        self.nxgraph.add_node(name,
                              op='reshape',
                              input=name + '_dv_batch_matmul',
                              datatype=datatype,
                              format='none',
                              output_shape=orig_output_shape[:2] + [orig_output_shape[-1]],
                              quant_scale=self.nxgraph.nodes[node.input[6]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[7]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(name + '_dv_batch_matmul', name)

    def import_QLinearMul(self, node):
        name = node.output[0]
        x_name = node.input[0]
        x_node = self.nxgraph.nodes[x_name]
        y_name = node.input[3]
        y_node = self.nxgraph.nodes[y_name]
        if 'base_shape' in x_node:
            x_shape = self.nxgraph.nodes[x_name]['base_shape']
        else:
            x_shape = self.nxgraph.nodes[x_name]['output_shape']
        if 'base_shape' in y_node:
            y_shape = self.nxgraph.nodes[y_name]['base_shape']
        else:
            y_shape = self.nxgraph.nodes[y_name]['output_shape']
        
        if x_node['op'] != 'constant':
            datatype = x_node['datatype']
        else:
            datatype = y_node['datatype']
        output_shape = self.calc_binary_shape(x_shape, y_shape)
        layer_format = 'none'
        if x_node['format'] != 'none':
            layer_format = x_node['format']
        elif y_node['format'] != 'none':
            layer_format = y_node['format']
        
        self.nxgraph.add_node(name,
                              op='mul',
                              x=x_name,
                              y=y_name,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[6]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[7]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        x_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        x_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        x_node['quant_axis'] = 0
        y_node['quant_scale'] = self.nxgraph.nodes[node.input[4]]['np_tensor']
        y_node['zero_point'] = self.nxgraph.nodes[node.input[5]]['np_tensor']
        y_node['quant_axis'] = 0

    def import_QLinearSigmoid(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        if 'base_shape' in input_node:
            output_shape = input_node['base_shape'][:]
        else:
            output_shape = input_node['output_shape'][:]
        datatype = input_node['datatype']

        self.nxgraph.add_node(name,
                              op='sigmoid',
                              x=input_name,
                              datatype=datatype,
                              format=input_node['format'],
                              output_shape=output_shape,
                              quant_scale=self.nxgraph.nodes[node.input[3]]['np_tensor'],
                              zero_point=self.nxgraph.nodes[node.input[4]]['np_tensor'],
                              quant_axis=0)
        self.nxgraph.add_edge(input_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        input_node['quant_scale'] = self.nxgraph.nodes[node.input[1]]['np_tensor']
        input_node['zero_point'] = self.nxgraph.nodes[node.input[2]]['np_tensor']
        input_node['quant_axis'] = 0

    def import_QuantizeLinear(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        scale_name = node.input[1]
        scale_node = self.nxgraph.nodes[scale_name]['info']
        if 'base_shape' in input_node.params:
            output_shape = input_node['base_shape'][:]
        else:
            output_shape = input_node.shape[:]
        layer_format = input_node.format
        if len(node.input) == 3:
            zero_name = node.input[2]
            zero_node = self.nxgraph.nodes[zero_name]['info']
            # if 'np_tensor' not in zero_node:
            if zero_node.tensor is None:
                raise ValueError("Cannot retrieve zero point for node %s." % name)
            zero_point = zero_node.tensor
            datatype = zero_node.datatype
        else:
            zero_point = np.asarray([0]).astype(np.uint8)
            datatype = np.dtype('uint8')

        # if 'np_tensor' not in scale_node:
        if scale_node.tensor is None:
            raise ValueError("Cannot retrieve scale for node %s." % name)
        scale = scale_node.tensor

        axis = 1
        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i
        if axis < 0:
            axis += len(output_shape)

        layer = AGLayer(name, op='quant', inputs=[input_name],
                        datatype=datatype, layer_format=layer_format,
                        shape=output_shape, scale=scale, zero_point=zero_point,
                        quant_axis=axis)
        self.nxgraph.add_node(name, info=layer)
        # self.nxgraph.add_node(name,
        #                       op='quant',
        #                       x=input_name,
        #                       quant_scale=scale,
        #                       zero_point=zero_point,
        #                       quant_axis=axis,
        #                       datatype=datatype,
        #                       format=layer_format,
        #                       output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

    def import_ReduceMean(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        layer_format = input_node.format
        keep_dims = True
        axes = []
        
        for attrib in node.attribute:
            if attrib.name == 'axes':
                for i in range(len(attrib.ints)):
                    if attrib.ints[i] < 0:
                        axes.append(attrib.ints[i] + len(input_shape))
                    else:
                        axes.append(attrib.ints[i])
            if attrib.name == 'keepdims' and attrib.i == 0:
                keep_dims = False

        if len(node.input) == 2:
            axes_name = node.input[1]
            axes_node = self.nxgraph.nodes[axes_name]['info']
            axes = list(axes_node.tensor)
            for i in range(len(axes)):
                if axes[i] < 0:
                    axes[i] += len(input_shape)

        axes.sort()
        output_shape = input_shape[:]
        params = {'axes': axes}
        if keep_dims:
            reduce_out = output_shape[:]
            for axis in reversed(axes):
                reduce_out.pop(axis)
            for axis in axes:
                output_shape[axis] = 1
            
            reduce_layer = AGLayer(name + '_dv_mean_reduce', op='mean_reduce', 
                                   inputs=[input_name], params=params, 
                                   datatype=datatype, layer_format=layer_format, 
                                   shape=reduce_out)
            self.nxgraph.add_node(name + '_dv_mean_reduce', info=reduce_layer)
            self.nxgraph.add_edge(input_name, name + '_dv_mean_reduce')

            reshape_layer = AGLayer(name, op='reshape', inputs=[name + '_dv_mean_reduce'],
                                    datatype=datatype, layer_format=layer_format,
                                    shape=output_shape)
            self.nxgraph.add_node(name, info=reshape_layer)
            self.nxgraph.add_edge(name + '_dv_mean_reduce', name)
        else:
            layer_format=LayerFormat.UNKNOWN
            for axis in reversed(axes):
                output_shape.pop(axis)

            layer = AGLayer(name, op='mean_reduce', inputs=[input_name],
                            params=params, datatype=datatype, 
                            layer_format=LayerFormat.UNKNOWN, shape=output_shape)
            self.nxgraph.add_node(name, info=layer)
            self.nxgraph.add_edge(input_name, name)
        # self.nxgraph.add_node(name,
        #                       op='mean_reduce',
        #                       input=input_name,
        #                       axes=axes,
        #                       keep_dims=keep_dims,
        #                       datatype=datatype,
        #                       format=layer_format,
        #                       output_shape=output_shape)
        

    def import_Relu(self, node):
        self.import_unary(node, 'relu')

    def import_Reshape(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        if 'base_shape' in input_node.params:
            input_shape = input_node.params['base_shape']
        else:
            input_shape = input_node.shape
        datatype = input_node.datatype
        out_shape = list(self.nxgraph.nodes[node.input[1]]['info'].tensor)
        output_shape = [0] * len(out_shape)

        in_vol = 1
        for dim in input_shape:
            if dim != -1:
                in_vol *= dim
        out_vol = 1
        for dim in out_shape:
            if dim > 0:
                out_vol *= dim
        if in_vol % out_vol != 0:
            raise ValueError("Improper Reshape")
        neg_shape = in_vol // out_vol

        negative_replaced = False
        for i in reversed(range(len(out_shape))):
            if out_shape[i] == 0:
                output_shape[i] = input_shape[i]
            elif out_shape[i] == -1:
                if negative_replaced:
                    output_shape[i] = -1
                else:
                    output_shape[i] = neg_shape
                    negative_replaced = True
            else:
                output_shape[i] = out_shape[i]

        layer = AGLayer(name, op='reshape', inputs=[input_name],
                        datatype=datatype, shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        # self.nxgraph.add_node(name,
        #                       op='reshape',
        #                       input=input_name,
        #                       datatype=datatype,
        #                       format='none',
        #                       output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        
        if len(output_shape) > 4:
            if output_shape[0] == 1:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        if input_node.quant_scale is not None and input_node.zero_point is not None:
            self.nxgraph.nodes[name]['info'].quant_scale = input_node.quant_scale
            self.nxgraph.nodes[name]['info'].zero_point = input_node.zero_point
            self.nxgraph.nodes[name]['info'].quant_axis = input_node.quant_axis

        if input_node.tensor is not None:
            out_tensor = np.reshape(input_node.tensor, output_shape)
            self.nxgraph.nodes[name]['info'].tensor = out_tensor

    def import_Resize(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        layer_format = input_node['format']
        datatype = input_node['datatype']

        coord_trans_mode = 'half_pixel'
        cubic_coeff_a = -0.75
        exclude_outside = 0
        extrap_value = 0.0
        mode = 'nearest'
        nearest_mode = 'round_prefer_floor'

        for attrib in node.attribute:
            if attrib.name == 'coordinate_transformation_mode':
                coord_trans_mode = attrib.s.decode('utf-8')
            if attrib.name == 'cubic_coeff_a':
                cubic_coeff_a = attrib.f
            if attrib.name == 'exclude_outside':
                exclude_outside = attrib.i
            if attrib.name == 'extrapolation_value':
                extrap_value = attrib.f
            if attrib.name == 'mode':
                mode = attrib.s.decode('utf-8')
            if attrib.name == 'nearest_mode':
                nearest_mode = attrib.s.decode('utf-8')
        
        if coord_trans_mode == 'tf_crop_and_resize':
            print("WARNING: We do not currently support \
                crop and resize.")
            return

        size_name = node.input[-1]
        size_node = self.nxgraph.nodes[size_name]

        if size_node['datatype'] == np.float32:
            scales = list(size_node['np_tensor'])
            output_shape = []
            for i in range(len(scales)):
                output_shape.append(int(scales[i] * input_shape[i]))
        else:
            if 'np_tensor' not in size_node:
                print("WARNING: Unable to determine sizes tensor. Please contact support.")
                return
            output_shape = list(size_node['np_tensor'])
            
        if mode == 'nearest':
            mode = 0
        elif mode == 'linear':
            mode = 1
        else:
            print("WARNING: Mode %s is unsupported, \
                defaulting to NEAREST" % mode)
            mode = 0

        align_corners = False
        half_pixel_centers = False
        if coord_trans_mode == 'half_pixel':
            align_corners = False
            half_pixel_centers = True
        elif coord_trans_mode == 'align_corners':
            align_corners = True
            half_pixel_centers = False
        elif coord_trans_mode == 'asymmetric':
            align_corners = False
            half_pixel_centers = False

        self.nxgraph.add_node(name,
                              op='resize',
                              input=input_name,
                              mode=mode,
                              align_corners=align_corners,
                              half_pixel_centers=half_pixel_centers,
                              cubic_coeff_a=cubic_coeff_a,
                              exclude_outside=exclude_outside,
                              extrap_value=extrap_value,
                              nearest_mode=nearest_mode,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

    def import_Shape(self, node):
        name = node.output[0]
        input_name = node.input[0]
        if input_name != 'input':
            input_node = self.nxgraph.nodes[input_name]
            datatype = np.int64
            np_tensor = np.asarray(input_node['output_shape'][:], dtype=np.int64)
            output_shape = [len(input_node['output_shape'])]
        else:
            datatype = np.int64
            np_tensor = np.asarray([1,10,3,224,224], dtype=np.int64)
            output_shape = [5]

        self.nxgraph.add_node(name,
                              op='constant',
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape,
                              np_tensor=np_tensor)
    
    def import_Sigmoid(self, node):
        self.import_unary(node, 'sigmoid')

    def import_Slice(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = input_node['datatype']
        layer_format = input_node['format']

        if len(node.input) > 1:
            start_name = node.input[1]
            start_node = self.nxgraph.nodes[start_name]
            end_name = node.input[2]
            end_node = self.nxgraph.nodes[end_name]

            if 'np_tensor' not in start_node:
                print("WARNING: Cannot determine start tensor for slice node %s. "
                    "Cannot generate slice node." % name)
                return
            begin = list(start_node['np_tensor'])
            if 'np_tensor' not in end_node:
                print("WARNING: Cannot determine end tensor for slice node %s. "
                    "Cannot generate slice node." % name)
                return
            end = list(end_node['np_tensor'])

            axes = list(range(len(input_shape)))
            if len(node.input) > 3:
                axes_name = node.input[3]
                axes_node = self.nxgraph.nodes[axes_name]
                if 'np_tensor' not in axes_node:
                    print("WARNING: Cannot determine axes tensor. Defaulting")
                else:
                    axes = list(axes_node['np_tensor'])
            strides = [1] * len(axes)
            if len(node.input) > 4:
                stride_name = node.input[4]
                stride_node = self.nxgraph.nodes[stride_name]
                if 'np_tensor' not in stride_node:
                    print("WARNING: Cannot determine stride values. Defaulting to 1")
                else:
                    strides = list(stride_node['np_tensor'])
        else:
            axes = []
            begin = []
            end = []
            for attrib in node.attribute:
                if attrib.name == 'axes':
                    axes = attrib.ints
                elif attrib.name == 'starts':
                    begin = attrib.ints
                elif attrib.name == 'ends':
                    end = attrib.ints
            strides = [1] * len(axes)    
        
        for i in range(len(axes)):
            if end[i] > input_shape[axes[i]]:
                end[i] = input_shape[axes[i]]
        
                # for stride_val in strides:
                #     if stride_val != 1:
                #         print(name)
                #         print("WARNING: Strided slices are not supported currently.")
                #         break

        for i in range(len(begin)):
            if begin[i] < 0:
                begin[i] += input_shape[i]
        for i in range(len(end)):
            if end[i] < 0:
                end[i] += input_shape[i]

        output_shape = input_shape[:]
        for i in range(len(axes)):
            output_shape[axes[i]] = math.ceil((end[i] - begin[i]) / strides[i])

        for i in range(len(input_shape)):
            if i in axes:
                continue
            axes.insert(i, i)
            begin.insert(i, 0)
            end.insert(i, input_shape[i])
            strides.insert(i, 1)

        self.nxgraph.add_node(name,
                              op='slice',
                              input=input_name,
                              axes=axes,
                              begin=begin,
                              end=end,
                              strides=strides,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        if 'np_tensor' in input_node:
            slice_obj = []
            for i in range(len(axes)):
                slice_obj.append(slice(begin[i], end[i]))
            slice_obj = tuple(slice_obj)
            out_tensor = input_node['np_tensor'].copy()[slice_obj]
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_Softmax(self, node):
        name = node.output[0]
        input_name = node.input[0]
        datatype = self.nxgraph.nodes[input_name]['datatype']
        output_shape = self.nxgraph.nodes[input_name]['output_shape']
        axes = []

        for attrib in node.attribute:
            if attrib.name == 'axis':
                if attrib.i == -1:
                    axes = [len(output_shape) - 1]
                else:
                    axes = [attrib.i]
        
        self.nxgraph.add_node(name,
                              op='softmax',
                              x=input_name,
                              axes=axes,
                              datatype=datatype,
                              format=self.nxgraph.nodes[input_name]['format'],
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

    def import_Split(self, node):
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        if 'base_shape' in input_node:
            input_shape = input_node['base_shape']
        else:
            input_shape = input_node['output_shape']
        datatype = input_node['datatype']
        layer_format = input_node['format']

        axis = 0
        split_vals = []
        for attrib in node.attribute:
            if attrib.name == 'axis':
                axis = attrib.i
            if attrib.name == 'split':
                split_vals = attrib.ints
        if axis < 0:
            axis += len(input_shape)

        if not split_vals:
            split_vals = [int(input_shape[axis] / len(node.output))] * len(node.output)
            if len(node.input) == 2:
                split_node = self.nxgraph.nodes[node.input[1]]
                split_vals = list(split_node['np_tensor'])

        start_index = 0
        axes = list(range(len(input_shape)))
        begin = [0] * len(input_shape)
        end = input_shape[:]
        for i in range(len(node.output)):
            out_name = node.output[i]
            begin[axis] = start_index
            end[axis] = start_index + split_vals[i]
            output_shape = input_shape[:]
            output_shape[axis] = end[axis] - begin[axis]
            self.nxgraph.add_node(out_name,
                                  op='slice',
                                  input=input_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=datatype,
                                  format=layer_format,
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, out_name)
            start_index += split_vals[i]

            if len(output_shape) > 4:
                if output_shape[0] == 1:
                    new_shape = output_shape[1:]
                    self.nxgraph.nodes[out_name]['base_shape'] = output_shape
                    self.nxgraph.nodes[out_name]['output_shape'] = new_shape
                    self.nxgraph.nodes[out_name]['base_axes'] = axes[:]
                    new_axes = axes[:]
                    if 0 in axes:
                        zeroth_index = axes.index(0)
                        new_axes.pop(zeroth_index)
                        new_begin = begin[:]
                        new_begin.pop(zeroth_index)
                        new_end = end[:]
                        new_end.pop(zeroth_index)
                        self.nxgraph.nodes[out_name]['base_begin'] = begin
                        self.nxgraph.nodes[out_name]['begin'] = new_begin
                        self.nxgraph.nodes[out_name]['base_end'] = end
                        self.nxgraph.nodes[out_name]['end'] = new_end
                    for i in range(len(new_axes)):
                        new_axes[i] = new_axes[i] - 1
                    self.nxgraph.nodes[out_name]['axes'] = new_axes
                else:
                    raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % out_name)


            if 'np_tensor' in input_node:
                slice_obj = []
                for i in range(len(axes)):
                    slice_obj.append(slice(begin[i], end[i]))
                slice_obj = tuple(slice_obj)
                out_tensor = input_node['np_tensor'].copy()[slice_obj]
                self.nxgraph.nodes[out_name]['np_tensor'] = out_tensor

    def import_Squeeze(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        axes = []
        if len(node.input) > 1:
            axes_name = node.input[1]
            axes_node = self.nxgraph.nodes[axes_name]['info']
            axes = axes_node.tensor
        else:
            for attrib in node.attribute:
                if attrib.name == 'axes':
                    axes = attrib.ints

        axes = [int(x) for x in axes]
        if axes == []:
            for i in range(len(input_shape)):
                if input_shape[i] == 1:
                    axes.append(i)
        
        for i in range(len(axes)):
            if axes[i] < 0:
                axes[i] += len(input_shape)
        axes = sorted(axes)

        output_shape = input_shape[:]
        for axis in reversed(axes):
            output_shape.pop(axis)

        layer = AGLayer(name, op='reshape', inputs=[input_name],
                        datatype=datatype, shape=output_shape)
        self.nxgraph.add_node(name, info=layer)
        # self.nxgraph.add_node(name,
        #                       op='reshape',
        #                       input=input_name,
        #                       datatype=datatype,
        #                       format='none',
        #                       output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        if input_node.tensor is not None:
            out_tensor = np.reshape(input_node.tensor, output_shape)
            self.nxgraph.nodes[name]['info'].tensor = out_tensor

    def import_Sub(self, node):
        self.import_binary(node, 'sub')

    def import_Tanh(self, node):
        self.import_unary(node, 'tanh')

    def import_TFL_HARD_SWISH(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        output_shape = input_node['output_shape'][:]
        datatype = input_node['datatype']
        layer_format = input_node['format']

        if datatype != np.float32:
            self.nxgraph.add_node(name,
                                op='swish',
                                x=input_name,
                                hard=1,
                                beta=1,
                                datatype=datatype,
                                format=layer_format,
                                output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name)
            return
        
        three_name = name + "_dv_3"
        self.nxgraph.add_node(three_name,
                              op='constant',
                              output_shape=[1],
                              datatype=datatype,
                              format='none',
                              np_tensor=np.array([3.0]).astype(datatype))
        add_name = name + '_dv_plus_3'
        self.nxgraph.add_node(add_name,
                              op='add',
                              x=input_name,
                              y=three_name,
                              output_shape=output_shape,
                              format=layer_format,
                              datatype=datatype)
        self.nxgraph.add_edge(input_name, add_name)
        self.nxgraph.add_edge(three_name, add_name)

        # ReLU6(x + 3)
        relu_name = name + "_dv_relu6"
        self.nxgraph.add_node(relu_name,
                              op='relu6',
                              x=add_name,
                              output_shape=output_shape,
                              format=layer_format,
                              datatype=datatype)
        self.nxgraph.add_edge(add_name, relu_name)

        # ReLU6(x + 3) / 6
        div_name = name + "_dv_div6"
        six_name = name + "_dv_6"
        self.nxgraph.add_node(six_name,
                              op='constant',
                              output_shape=[1],
                              datatype=datatype,
                              format='none',
                              np_tensor=np.array([6.0]).astype(datatype))
        self.nxgraph.add_node(div_name,
                              op='div',
                              x=relu_name,
                              y=six_name,
                              output_shape=output_shape,
                              format=layer_format,
                              datatype=datatype)
        self.nxgraph.add_edge(relu_name, div_name)
        self.nxgraph.add_edge(six_name, div_name)
        # x * (ReLU6(x + 3) / 6)

        self.nxgraph.add_node(name,
                              op='mul',
                              x=input_name,
                              y=div_name,
                              output_shape=output_shape,
                              format=layer_format,
                              datatype=datatype)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(div_name, name)

    def import_Transpose(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]
        if 'base_shape' in input_node:
            input_shape = input_node['base_shape'][:]
        else:
            input_shape = input_node['output_shape'][:]
        datatype = input_node['datatype']
        axes = list(range(len(input_shape)))

        for attrib in node.attribute:
            if attrib.name == 'perm':
                for i in range(len(attrib.ints)):
                    axes[i] = attrib.ints[i]
        output_shape = []
        orig_format = list(input_node['format'])

        for axis in axes:
            output_shape.append(input_shape[axis])

        if input_node['format'] == 'none':
            layer_format = 'none'
        else:
            new_format = []
            for axis in axes:
                new_format.append(orig_format[axis])
            new_format = ''.join(new_format)
            layer_format = new_format 
        

        self.nxgraph.add_node(name,
                              op='transpose',
                              input=input_name,
                              axes=axes,
                              datatype=datatype,
                              format=layer_format,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        
        if len(output_shape) > 4:
            if output_shape[0] == 1 and axes[0] == 0:
                new_shape = output_shape[1:]
                self.nxgraph.nodes[name]['base_shape'] = output_shape
                self.nxgraph.nodes[name]['output_shape'] = new_shape
                self.nxgraph.nodes[name]['base_axes'] = axes[:]
                new_axes = axes[1:]
                for i in range(len(new_axes)):
                    new_axes[i] = new_axes[i] - 1
                self.nxgraph.nodes[name]['axes'] = new_axes
            else:
                raise ValueError("Unable to handle, 5-dim layer %s, please trim the model before this node." % name)

        if 'quant_scale' in input_node and 'zero_point' in input_node:
            self.nxgraph.nodes[name]['quant_scale'] = input_node['quant_scale']
            self.nxgraph.nodes[name]['zero_point'] = input_node['zero_point']
            self.nxgraph.nodes[name]['quant_axis'] = input_node['quant_axis']

        if 'np_tensor' in input_node:
            out_tensor = np.transpose(input_node['np_tensor'], axes)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_Unsqueeze(self, node):
        name = node.output[0]
        input_name = node.input[0]
        input_node = self.nxgraph.nodes[input_name]['info']
        input_shape = input_node.shape
        datatype = input_node.datatype
        axes = []
        if len(node.input) > 1:
            axes_name = node.input[1]
            axes_node = self.nxgraph.nodes[axes_name]['info']
            axes = axes_node.tensor
        else:
            for attrib in node.attribute:
                if attrib.name == 'axes':
                    axes = attrib.ints
        
        axes = [int(x) for x in axes]
        for i in range(len(axes)):
            if axes[i] < 0:
                axes[i] += len(input_shape) + len(axes)
        axes = sorted(axes)

        if input_node.format == LayerFormat.NCD and len(axes) == 1 and axes[0] in [2,3]:
            layer_format = LayerFormat.NCHW
        else:
            layer_format = LayerFormat.UNKNOWN

        if len(input_shape) == 1 and len(axes) == 1 and axes[0] == 0:
            output_shape = input_shape[:]
        else:
            output_shape = input_shape[:]
            for axis in axes:
                output_shape.insert(axis, 1)

        layer = AGLayer(name, op='reshape', inputs=[input_name],
                        shape=output_shape, datatype=datatype,
                        layer_format=layer_format)
        self.nxgraph.add_node(name, info=layer)
        # self.nxgraph.add_node(name,
        #                       op='reshape',
        #                       input=input_name,
        #                       datatype=datatype,
        #                       format='none',
        #                       output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        if input_node.tensor is not None:
            out_tensor = np.reshape(input_node.tensor, output_shape)
            self.nxgraph.nodes[name]['info'].tensor = out_tensor

    def import_unknown(self, node):
        print(node)
        print("Unsupported Op Type: " + node.op_type)

    def clean_graph(self):
        # self.qdq_resolver()
        self.qdq_resolver_v2()
        
        # self.back_propagate_format()
        self.back_propogate_format_v2()
        # self.clean_pad()
        self.clean_pad_v2()
        self.clean_clip_to_relu6() # Updated
        # self.clean_expand_mul_to_resize_quant() Investigate use case
        self.clean_ncd_to_ndc()
        # self.clean_nchw_to_nhwc()
        self.clean_nchw_to_nhwc_v2()
        self.clean_constants()
        # self.clean_quant_dequant()
        # self.find_subgraph_inputs()
        # self.prune_graph()

    def back_propogate_format_v2(self):
        for node_name in reversed(list(nx.topological_sort(self.nxgraph))):
            node_info = self.nxgraph.nodes[node_name]['info']
            if node_info.format == LayerFormat.UNKNOWN:
                continue
            if node_info.op == 'reshape':
                continue

            # TODO: Add support for transpose

            # TODO: Examine what ops will maintain format
            if node_info.op in ['max_pool', 'conv', 'quant', 'dequant']:
                input_name = node_info.inputs[0]
                input_node = self.nxgraph.nodes[input_name]['info']
                if input_node.format != LayerFormat.UNKNOWN:
                    continue
                input_node.format = node_info.format
            
            elif node_info.op in ['add', 'sub', 'mul', 'div']:
                x_node = self.nxgraph.nodes[node_info.inputs[0]]['info']
                y_node = self.nxgraph.nodes[node_info.inputs[1]]['info']
                if len(x_node.shape) == len(node_info.shape) and x_node.format == LayerFormat.UNKNOWN:
                    x_node.format = node_info.format
                if len(y_node.shape) == len(node_info.shape) and y_node.format == LayerFormat.UNKNOWN:
                    y_node.format = node_info.format

    def back_propagate_format(self):
        for node_name in reversed(list(nx.topological_sort(self.nxgraph))):
            data = self.nxgraph.nodes[node_name]
            if data['format'] == 'none':
                continue
            if 'input' in data:
                input_node = self.nxgraph.nodes[data['input']]
                if input_node['format'] != 'none':
                    continue
                if data['op'] == 'reshape':
                    continue
                if data['op'] == 'transpose':
                    axes = data['axes']
                    out_format = data['format']
                    orig_format = [''] * len(out_format)
                    for i in range(len(out_format)):
                        orig_format[axes[i]] = out_format[i]
                    orig_format = ''.join(orig_format)
                    input_node['format'] = orig_format
                else:
                    input_node['format'] = data['format']
            if 'x' in data and 'y' in data:
                x_node = self.nxgraph.nodes[data['x']]
                y_node = self.nxgraph.nodes[data['y']]
                if x_node['format'] != 'none' and y_node['format'] != 'none':
                    continue
            if 'x' in data:
                x_node = self.nxgraph.nodes[data['x']]
                if x_node['format'] != 'none':
                    x_node['format'] = data['format']

    def clean_constants(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.op == 'constant':
                continue
            if node_info.tensor is None:
                continue

            node_info.op = 'constant'
            in_edges = list(self.nxgraph.in_edges(node_name))
            for edge in in_edges:
                self.nxgraph.remove_edge(edge[0], edge[1])

    def clean_pad_v2(self):
        remove_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.op != 'pad':
                continue
            # TODO: Need to fix clean_pad, need to see more examples
            raise NotImplementedError("Fixing issue with pad folding")
            out_edges = list(self.nxgraph.out_edges(node_name))
            if len(out_edges) > 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.nxgraph.nodes[out_name]['info']
            if out_node.op not in ['conv', 'transpose_conv']:
                continue
            out_node.params['head'][0] += data.params['head'][2]
            out_node['head'][1] += data['head'][3]
            out_node['tail'][0] += data['tail'][2]
            out_node['tail'][1] += data['tail'][3]

            out_node['input'] = data['input']
            self.nxgraph.add_edge(data['input'], out_name)
            remove_nodes.append(node_name)
        self.nxgraph.remove_nodes_from(remove_nodes)

    def clean_pad(self):
        remove_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] != 'pad':
                continue
            out_edges = list(self.nxgraph.out_edges(node_name))
            if len(out_edges) > 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.nxgraph.nodes[out_name]
            if out_node['op'] not in ['conv', 'transpose_conv']:
                continue
            out_node['head'][0] += data['head'][2]
            out_node['head'][1] += data['head'][3]
            out_node['tail'][0] += data['tail'][2]
            out_node['tail'][1] += data['tail'][3]

            out_node['input'] = data['input']
            self.nxgraph.add_edge(data['input'], out_name)
            remove_nodes.append(node_name)
        self.nxgraph.remove_nodes_from(remove_nodes)


    def clean_clip_to_relu6(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.op != 'clip':
                continue
            min_node = self.nxgraph.nodes[node_info.inputs[1]]['info']
            max_node = self.nxgraph.nodes[node_info.inputs[2]]['info']
            if min_node.op != 'constant' or max_node.op != 'constant':
                continue
            if min_node.shape != [1] or max_node.shape != [1]:
                continue
            if min_node.tensor[0] != 0 or max_node.tensor[0] != 6:
                continue

            node_info.op = 'relu6'
            self.nxgraph.remove_edge(node_info.inputs[1], node_name)
            self.nxgraph.remove_edge(node_info.inputs[2], node_name)
            node_info.inputs = [node_info.inputs[0]]

    def clean_expand_mul_to_resize_quant(self):
        exp_mul_to_resize = True
        while exp_mul_to_resize:
            exp_mul_to_resize = False
            for node1, data in self.nxgraph.nodes(data=True):
                if data['op'] != 'reshape':
                    continue
                input_node = self.nxgraph.nodes[data['input']]
                node1_input_shape = input_node['output_shape']
                if len(node1_input_shape) != 4:
                    continue
                expected_node1_out_shape = node1_input_shape[:]
                expected_node1_out_shape.insert(3,1)
                expected_node1_out_shape.append(1)
                if data['output_shape'] != expected_node1_out_shape:
                    continue
                out_edges1 = list(self.nxgraph.out_edges(node1))
                if len(out_edges1) != 1:
                    continue

                node2_name = out_edges1[0][1]
                node2_data = self.nxgraph.nodes[node2_name]
                if node2_data['op'] != 'dequant':
                    continue
                out_edges2 = list(self.nxgraph.out_edges(node2_name))
                if len(out_edges2) != 1:
                    continue

                node3_name = out_edges2[0][1]
                node3_data = self.nxgraph.nodes[node3_name]
                if node3_data['op'] != 'mul':
                    continue
                if not node3_data['y'].endswith('_dv_ones'):
                    continue
                out_edges3 = list(self.nxgraph.out_edges(node3_name))
                if len(out_edges3) != 1:
                    continue

                node4_name = out_edges3[0][1]
                node4_data = self.nxgraph.nodes[node4_name]
                if node4_data['op'] != 'reshape':
                    continue
                expected_node4_out_shape = node1_input_shape[:]
                expected_node4_out_shape[2] *= 2
                expected_node4_out_shape[3] *= 2
                if node4_data['output_shape'] != expected_node4_out_shape:
                    continue
                out_edges4 = list(self.nxgraph.out_edges(node4_name))
                if len(out_edges4) != 1:
                    continue

                node5_name = out_edges4[0][1]
                node5_data = self.nxgraph.nodes[node5_name]
                if node5_data['op'] != 'quant':
                    continue
                node5_data['input'] = data['input']
                del node5_data['x']
                node5_data['op'] = 'resize'
                node5_data['mode'] = 0
                node5_data['align_corners'] = False
                node5_data['half_pixel_centers'] = False
                node5_data['format'] = input_node['format']

                self.nxgraph.remove_node(node1)
                self.nxgraph.remove_node(node2_name)
                self.nxgraph.remove_node(node3_name)
                self.nxgraph.remove_node(node4_name)
                self.nxgraph.add_edge(node5_data['input'], node5_name)
                exp_mul_to_resize = True
                break

    def clean_ncd_to_ndc(self):
        nodes_to_explore = []
        explored_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.format != LayerFormat.NCD:
                continue
            all_unknown = True
            for input_name in node_info.inputs:
                input_node = self.nxgraph.nodes[input_name]['info']
                if input_node.format != LayerFormat.UNKNOWN:
                    all_unknown = False
                    break
            if all_unknown:
                nodes_to_explore.append(node_name)

        # TODO: Add check to add a reshape before starting nodes

        while nodes_to_explore:
            node_name = nodes_to_explore.pop(0)
            node_info = self.nxgraph.nodes[node_name]['info']
            ready_to_modify = True
            for input_name in node_info.inputs:
                if self.nxgraph.nodes[input_name]['info'].format != LayerFormat.UNKNOWN:
                    if input_name not in explored_nodes:
                        ready_to_modify = False
                        break
            if not ready_to_modify:
                nodes_to_explore.append(node_name)
                continue

            orig_shape = node_info.shape[:]
            if node_info.op in ['external', 'quant', 'dequant', 'add', 'concat', 'relu']:
                node_info.shape.append(1)
                node_info.format = LayerFormat.NCHW
            elif node_info.op in ['conv']:
                node_info.shape.append(1)
                node_info.format = LayerFormat.NCHW
                node_info.params['dilation'].append(1)
                node_info.params['stride'].append(1)
                node_info.params['head'].append(0)
                node_info.params['tail'].append(0)

                filter_name = node_info.inputs[1]
                filter_node = self.nxgraph.nodes[filter_name]['info']
                filter_node.shape.append(1)
                filter_node.tensor = np.reshape(filter_node.tensor, filter_node.shape)

            elif node_info.op in ['max_pool', 'avg_pool']:
                node_info.shape.append(1)
                node_info.format = LayerFormat.NCHW
                node_info.params['size'].append(1)
                node_info.params['stride'].append(1)
                node_info.params['head'].append(0)
                node_info.params['tail'].append(0)
            else:
                raise NotImplementedError("Op %s not handled in NCD to NCHW reformatting, " \
                                          "please contact support." % node_info.op)

            reshape_branch = []
            for out_edge in list(self.nxgraph.out_edges(node_name)):
                out_name = out_edge[1]
                out_node = self.nxgraph.nodes[out_name]['info']
                if out_node.format != LayerFormat.NCD:
                    reshape_branch.append(out_name)
                else:
                    if out_name not in nodes_to_explore:
                        nodes_to_explore.append(out_name)
            
            if reshape_branch:
                reshape_name = node_name + '_dv_ncd_reshape'
                reshape_layer = AGLayer(reshape_name, op='reshape',
                                        inputs=[node_name], datatype=node_info.datatype,
                                        shape=orig_shape, layer_format=LayerFormat.NCD,
                                        scale=node_info.quant_scale,
                                        zero_point=node_info.zero_point,
                                        quant_axis=node_info.quant_axis)
                self.nxgraph.add_node(reshape_name, info=reshape_layer)
                self.nxgraph.add_edge(node_name, reshape_name)

                for out_name in reshape_branch:
                    out_node = self.nxgraph.nodes[out_name]['info']
                    if out_node.format == LayerFormat.NCHW:
                        continue
                    for i in range(len(out_node.inputs)):
                        if out_node.inputs[i] == node_name:
                            out_node.inputs[i] = reshape_name
                        self.nxgraph.remove_edge(node_name, out_name)
                        self.nxgraph.add_edge(reshape_name, out_name)

            explored_nodes.append(node_name)

    def clean_nchw_to_nhwc_v2(self):
        nodes_to_explore = []
        explored_nodes = []
        quant_axis_map = {0: 0,
                          1: 3,
                          2: 1,
                          3: 2}
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.format != LayerFormat.NCHW:
                continue
            all_unknown = True
            for input_name in node_info.inputs:
                input_node = self.nxgraph.nodes[input_name]['info']
                if input_node.format == LayerFormat.NCHW:
                    all_unknown = False
                    break
            if all_unknown:
                nodes_to_explore.append(node_name)
        
        for node_name in nodes_to_explore:
            node_info = self.nxgraph.nodes[node_name]['info']
            if node_info.op != 'external':
                pass # TODO: Add support for pre-transpose to group section

        while nodes_to_explore:
            node_name = nodes_to_explore.pop(0)
            node_info = self.nxgraph.nodes[node_name]['info']

            ready_to_modify = True
            for input_name in node_info.inputs:
                if self.nxgraph.nodes[input_name]['info'].format == LayerFormat.NCHW:
                    if input_name not in explored_nodes:
                        ready_to_modify = False
                        break
            if not ready_to_modify:
                nodes_to_explore.append(node_name)
                continue
            
            orig_shape = node_info.shape[:]
            node_info.quant_axis = quant_axis_map[node_info.quant_axis]
            if node_info.op in ['external', 'quant', 'dequant', 'max_pool',
                                 'avg_pool', 'add', 'reshape', 'relu']:
                new_shape = [node_info.shape[0], node_info.shape[2], 
                             node_info.shape[3], node_info.shape[1]]
                node_info.shape = new_shape
                node_info.format = LayerFormat.NHWC

            elif node_info.op in ['conv']:
                # HWIO
                # OIHW is ONNX
                new_shape = [node_info.shape[0], node_info.shape[2], 
                             node_info.shape[3], node_info.shape[1]]
                node_info.shape = new_shape
                node_info.format = LayerFormat.NHWC

                filter_name = node_info.inputs[1]
                filter_node = self.nxgraph.nodes[filter_name]['info']
                new_filt_shape = [filter_node.shape[2], filter_node.shape[3], 
                                  filter_node.shape[1], filter_node.shape[0]]
                transpose_axis = [2,3,1,0]
                if node_info.params['groups'] != 1:
                    temp = new_filt_shape[2]
                    new_filt_shape[2] = new_filt_shape[3]
                    new_filt_shape[3] = temp
                    transpose_axis = [2,3,0,1]
                filter_node.shape = new_filt_shape
                filter_node.tensor = np.transpose(filter_node.tensor, transpose_axis)
                filter_node.quant_axis = quant_axis_map[filter_node.quant_axis]

            elif node_info.op in ['concat']:
                new_shape = [node_info.shape[0], node_info.shape[2], 
                             node_info.shape[3], node_info.shape[1]]
                node_info.shape = new_shape
                node_info.format = LayerFormat.NHWC
                node_info.params['axis'] = quant_axis_map[node_info.params['axis']]

            elif node_info.op in ['mean_reduce']:
                node_info.format = LayerFormat.NHWC
                new_axes = []
                for axis in node_info.params['axes']:
                    new_axes.append(quant_axis_map[axis])
                new_axes.sort()
                node_info.params['axes'] = new_axes
            else:
                print(node_info)
                raise NotImplementedError("Op %s not handled in NCHW to NHWC reformatting, " \
                                          "please contact support." % node_info.op)

            transpose_branch = []
            for out_edge in list(self.nxgraph.out_edges(node_name)):
                out_name = out_edge[1]
                out_node = self.nxgraph.nodes[out_name]['info']
                if out_node.format != LayerFormat.NCHW:
                    transpose_branch.append(out_name)
                else:
                    if out_name not in nodes_to_explore:
                        nodes_to_explore.append(out_name)
            
            if transpose_branch:
                transpose_name = node_name + '_dv_nchw_transpose'
                params = {'axes': [0, 3, 1, 2]}
                transpose_layer = AGLayer(transpose_name, op='transpose',
                                        inputs=[node_name], datatype=node_info.datatype,
                                        params=params, shape=orig_shape, 
                                        layer_format=LayerFormat.NCHW,
                                        scale=node_info.quant_scale,
                                        zero_point=node_info.zero_point,
                                        quant_axis=node_info.quant_axis)
                self.nxgraph.add_node(transpose_name, info=transpose_layer)
                self.nxgraph.add_edge(node_name, transpose_name)

                for out_name in transpose_branch:
                    out_node = self.nxgraph.nodes[out_name]['info']
                    for i in range(len(out_node.inputs)):
                        if out_node.inputs[i] == node_name:
                            out_node.inputs[i] = transpose_name
                        self.nxgraph.remove_edge(node_name, out_name)
                        self.nxgraph.add_edge(transpose_name, out_name)

            explored_nodes.append(node_name)

    def clean_nchw_to_nhwc(self):
        nchw = True
        while nchw:
            nchw = False
            for node_name, data in self.nxgraph.nodes(data=True):
                if data['format'] != 'nchw':
                    continue
                if data['op'] in ['transpose', 'external']:
                    continue
                nchw = True
                for input_val in ['x', 'y', 'input', 'values']:
                    if input_val not in data:
                        continue
                    if input_val == 'values':
                        for i in range(len(data[input_val])):
                            input_name = data[input_val][i]
                            input_node = self.nxgraph.nodes[input_name]
                            if input_node['format'] == 'nhwc' or \
                                len(input_node['output_shape']) != 4:
                                continue
                            pre_name = node_name + '_pre_nchw_transpose_dv_' + input_val + str(i)
                            pre_shape = []
                            for axis in [0,2,3,1]:
                                pre_shape.append(input_node['output_shape'][axis])
                            self.nxgraph.add_node(pre_name,
                                                op='transpose',
                                                input=input_name,
                                                axes=[0,2,3,1],
                                                datatype=input_node['datatype'],
                                                format='nhwc',
                                                output_shape=pre_shape)
                            self.nxgraph.add_edge(input_name, pre_name)
                            self.nxgraph.add_edge(pre_name, node_name)
                            self.nxgraph.remove_edge(input_name, node_name)

                            if 'quant_scale' in input_node and 'zero_point' in input_node:
                                self.nxgraph.nodes[pre_name]['quant_scale'] = input_node['quant_scale']
                                self.nxgraph.nodes[pre_name]['zero_point'] = input_node['zero_point']
                                self.nxgraph.nodes[pre_name]['quant_axis'] = input_node['quant_axis']

                            if 'np_tensor' in input_node:
                                out_tensor = np.transpose(input_node['np_tensor'], [0,2,3,1])
                                self.nxgraph.nodes[pre_name]['np_tensor'] = out_tensor
                            data[input_val][i] = pre_name
                    else:
                        input_name = data[input_val]
                        input_node = self.nxgraph.nodes[input_name]
                        if input_node['format'] == 'nhwc' or \
                            len(input_node['output_shape']) != 4:
                            continue
                        pre_name = node_name + '_pre_nchw_transpose_dv_' + input_val
                        pre_shape = []
                        for axis in [0,2,3,1]:
                            pre_shape.append(input_node['output_shape'][axis])
                        self.nxgraph.add_node(pre_name,
                                            op='transpose',
                                            input=input_name,
                                            axes=[0,2,3,1],
                                            datatype=input_node['datatype'],
                                            format='nhwc',
                                            output_shape=pre_shape)
                        self.nxgraph.add_edge(input_name, pre_name)
                        self.nxgraph.add_edge(pre_name, node_name)
                        self.nxgraph.remove_edge(input_name, node_name)

                        if 'quant_scale' in input_node and 'zero_point' in input_node:
                            self.nxgraph.nodes[pre_name]['quant_scale'] = input_node['quant_scale']
                            self.nxgraph.nodes[pre_name]['zero_point'] = input_node['zero_point']
                            self.nxgraph.nodes[pre_name]['quant_axis'] = input_node['quant_axis']

                        if 'np_tensor' in input_node:
                            out_tensor = np.transpose(input_node['np_tensor'], [0,2,3,1])
                            self.nxgraph.nodes[pre_name]['np_tensor'] = out_tensor
                        data[input_val] = pre_name

                post_name = node_name + '_post_nchw_transpose_dv'
                post_shape = data['output_shape'][:]
                self.nxgraph.add_node(post_name,
                                    op='transpose',
                                    input=node_name,
                                    axes=[0,3,1,2],
                                    datatype=data['datatype'],
                                    format='nchw',
                                    output_shape=post_shape)

                if 'quant_axis' in data:
                    new_axes = [0,2,3,1]
                    data['quant_axis'] = new_axes.index(data['quant_axis'])

                if 'quant_scale' in data and 'zero_point' in data:
                    self.nxgraph.nodes[post_name]['quant_scale'] = data['quant_scale']
                    self.nxgraph.nodes[post_name]['zero_point'] = data['zero_point']
                    self.nxgraph.nodes[post_name]['quant_axis'] = data['quant_axis']

                if 'np_tensor' in data:
                    out_tensor = np.transpose(data['np_tensor'], [0,3,1,2])
                    self.nxgraph.nodes[post_name]['np_tensor'] = out_tensor

                if 'axes' in data:
                    perm_axes = [0,2,3,1]
                    new_axes = []
                    for axis in data['axes']:
                        new_axes.append(perm_axes.index(axis))
                    new_axes.sort()
                    data['axes'] = new_axes
                if 'axis' in data:
                    data['axis'] = [0,2,3,1].index(data['axis'])

                if 'begin' in data and len(data['begin']) == 4:
                    begin = data['begin']
                    new_begin = [begin[0], begin[2], begin[3], begin[1]]
                    data['begin'] = new_begin

                if 'end' in data and len(data['end']) == 4:
                    end = data['end']
                    new_end = [end[0], end[2], end[3], end[1]]
                    data['end'] = new_end

                if 'strides' in data and len(data['strides']) == 4:
                    strides = data['strides']
                    new_str = [strides[0], strides[2], strides[3], strides[1]]
                    data['strides'] = new_str

                out_edges = list(self.nxgraph.out_edges(node_name))
                for edge in out_edges:
                    out_name = edge[1]
                    out_node = self.nxgraph.nodes[out_name]
                    if 'x' in out_node and out_node['x'] == node_name:
                        out_node['x'] = post_name
                    if 'y' in out_node and out_node['y'] == node_name:
                        out_node['y'] = post_name
                    if 'input' in out_node and out_node['input'] == node_name:
                        out_node['input'] = post_name
                    if 'values' in out_node:
                        for i in range(len(out_node['values'])):
                            if out_node['values'][i] == node_name:
                                out_node['values'][i] = post_name
                    self.nxgraph.add_edge(post_name, out_name)
                    self.nxgraph.remove_edge(node_name, out_name)
                self.nxgraph.add_edge(node_name, post_name)
                data['format'] = 'nhwc'
                tr_out_shape = []
                for axis in [0,2,3,1]:
                    tr_out_shape.append(post_shape[axis])
                data['output_shape'] = tr_out_shape
                break

    def qdq_resolver_v2(self):
        remove_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            node_info = data['info']
            if node_info.op in ['quant', 'dequant', 'external', 'constant']:
                continue

            out_edges = list(self.nxgraph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.nxgraph.nodes[out_name]['info']
            if out_node.op != 'quant':
                continue

            dequant_in = True
            for input_name in node_info.inputs:
                input_node = self.nxgraph.nodes[input_name]['info']
                if input_node.op != 'dequant':
                    dequant_in = False
                    break
            if not dequant_in:
                continue
            
            node_info.datatype = out_node.datatype
            node_info.quant_scale = out_node.quant_scale.copy()
            node_info.zero_point = out_node.zero_point.copy()
            node_info.quant_axis = out_node.quant_axis
            for out_out_edge in list(self.nxgraph.out_edges(out_name)):
                out_out_name = out_out_edge[1]
                out_out_node = self.nxgraph.nodes[out_out_name]['info']
                for i in range(len(out_out_node.inputs)):
                    if out_out_node.inputs[i] == out_name:
                        out_out_node.inputs[i] = node_name
                        self.nxgraph.remove_edge(out_name, out_out_name)
                        self.nxgraph.add_edge(node_name, out_out_name)    
            remove_nodes.append(out_name)

            for i in range(len(node_info.inputs)):
                input_name = node_info.inputs[i]
                input_node = self.nxgraph.nodes[input_name]['info']
                node_info.inputs[i] = input_node.inputs[0]
                in_in_node = self.nxgraph.nodes[input_node.inputs[0]]['info']
                in_in_node.quant_scale = input_node.quant_scale.copy()
                in_in_node.zero_point = input_node.zero_point.copy()
                in_in_node.quant_axis = input_node.quant_axis
                self.nxgraph.remove_edge(input_name, node_name)
                self.nxgraph.add_edge(node_info.inputs[i], node_name)
                if len(self.nxgraph.out_edges(input_name)) == 0:
                    remove_nodes.append(input_name)

        self.nxgraph.remove_nodes_from(remove_nodes)

    def qdq_resolver(self):
        remove_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] in ['conv', 'transpose_conv']:
                out_edges = list(self.nxgraph.out_edges(node_name))
                if len(out_edges) != 1:
                    continue
                out_name = out_edges[0][1]
                out_node = self.nxgraph.nodes[out_name]
                input_name = data['input']
                input_node = self.nxgraph.nodes[input_name]
                filter_name = data['filter']
                filter_node = self.nxgraph.nodes[filter_name]
                bias_name = None
                bias_node = None
                if 'bias' in data:
                    bias_name = data['bias']
                    bias_node = self.nxgraph.nodes[bias_name]

                if input_node['op'] != 'dequant' or filter_node['op'] != 'dequant' or \
                    out_node['op'] != 'quant':
                    continue
                if bias_node and bias_node['op'] != 'dequant':
                    continue
                
                new_input_node = self.nxgraph.nodes[input_node['x']]
                if 'quant_scale' not in new_input_node:
                    new_input_node['quant_scale'] = input_node['quant_scale'].copy()
                if 'zero_point' not in new_input_node:
                    new_input_node['zero_point'] = input_node['zero_point'].copy()
                if 'quant_axis' not in new_input_node:
                    new_input_node['quant_axis'] = input_node['quant_axis']
                new_filter_node = self.nxgraph.nodes[filter_node['x']]
                if 'quant_scale' not in new_filter_node:
                    new_filter_node['quant_scale'] = filter_node['quant_scale'].copy()
                if 'zero_point' not in new_filter_node:
                    new_filter_node['zero_point'] = filter_node['zero_point'].copy()
                if 'quant_axis' not in new_filter_node:
                    new_filter_node['quant_axis'] = filter_node['quant_axis']
                if bias_node:
                    new_bias_node = self.nxgraph.nodes[bias_node['x']]
                    if 'quant_scale' not in new_bias_node:
                        new_bias_node['quant_scale'] = bias_node['quant_scale'].copy()
                    if 'zero_point' not in new_bias_node:
                        new_bias_node['zero_point'] = bias_node['zero_point'].copy()
                    if 'quant_axis' not in new_bias_node:
                        new_bias_node['quant_axis'] = bias_node['quant_axis']

                data['input'] = input_node['x']
                self.nxgraph.remove_edge(input_name, node_name)
                self.nxgraph.add_edge(input_node['x'], node_name)
                data['filter'] = filter_node['x']
                self.nxgraph.remove_edge(filter_name, node_name)
                self.nxgraph.add_edge(filter_node['x'], node_name)
                if bias_node:
                    data['bias'] = bias_node['x']
                    self.nxgraph.remove_edge(bias_name, node_name)
                    self.nxgraph.add_edge(bias_node['x'], node_name)
                
                data['datatype'] = out_node['datatype']
                data['quant_scale'] = out_node['quant_scale'].copy()
                data['zero_point'] = out_node['zero_point'].copy()
                data['quant_axis'] = out_node['quant_axis']

                quant_out_edges = self.nxgraph.out_edges(out_name)
                edge_removals = []
                edge_adds = []
                for edge in quant_out_edges:
                    next_name = edge[1]
                    next_node = self.nxgraph.nodes[next_name]
                    for val in ['x', 'y', 'input']:
                        if val in next_node and next_node[val] == out_name:
                            next_node[val] = node_name
                        if 'values' in next_node:
                            for i in range(len(next_node['values'])):
                                if next_node['values'][i] == out_name:
                                    next_node['values'][i] = node_name
                    edge_removals.append((out_name, next_name))
                    edge_adds.append((node_name, next_name))

                for edge in edge_removals:
                    self.nxgraph.remove_edge(edge[0], edge[1])
                for edge in edge_adds:
                    self.nxgraph.add_edge(edge[0], edge[1])
                
                if len(self.nxgraph.out_edges(input_name)) == 0:
                    remove_nodes.append(input_name)
                if len(self.nxgraph.out_edges(filter_name)) == 0:
                    remove_nodes.append(filter_name)
                if bias_node and len(self.nxgraph.out_edges(bias_name)) == 0:
                    remove_nodes.append(bias_name)
                remove_nodes.append(out_name)

                if out_name in self.output_names:
                    self.output_names[self.output_names.index(out_name)] = node_name
                
            elif data['op'] in ['add', 'sub']:
                out_edges = list(self.nxgraph.out_edges(node_name))
                if len(out_edges) != 1:
                    continue
                out_name = out_edges[0][1]
                out_node = self.nxgraph.nodes[out_name]
                x_name = data['x']
                x_node = self.nxgraph.nodes[x_name]
                y_name = data['y']
                y_node = self.nxgraph.nodes[y_name]
                if x_node['op'] != 'dequant' or y_node['op'] != 'dequant' or \
                    out_node['op'] != 'quant':
                    continue

                new_x_node = self.nxgraph.nodes[x_node['x']]
                if 'quant_scale' not in new_x_node:
                    new_x_node['quant_scale'] = x_node['quant_scale'].copy()
                if 'zero_point' not in new_x_node:
                    new_x_node['zero_point'] = x_node['zero_point'].copy()
                if 'quant_axis' not in new_x_node:
                    new_x_node['quant_axis'] = x_node['quant_axis']
                new_y_node = self.nxgraph.nodes[y_node['x']]
                if 'quant_scale' not in new_y_node:
                    new_y_node['quant_scale'] = y_node['quant_scale'].copy()
                if 'zero_point' not in new_y_node:
                    new_y_node['zero_point'] = y_node['zero_point'].copy()
                if 'quant_axis' not in new_y_node:
                    new_y_node['quant_axis'] = y_node['quant_axis']

                data['x'] = x_node['x']
                self.nxgraph.remove_edge(x_name, node_name)
                self.nxgraph.add_edge(x_node['x'], node_name)
                data['y'] = y_node['x']
                self.nxgraph.remove_edge(y_name, node_name)
                self.nxgraph.add_edge(y_node['x'], node_name)
                
                data['datatype'] = out_node['datatype']
                data['quant_scale'] = out_node['quant_scale'].copy()
                data['zero_point'] = out_node['zero_point'].copy()
                data['quant_axis'] = out_node['quant_axis']

                quant_out_edges = self.nxgraph.out_edges(out_name)
                edge_removals = []
                edge_adds = []
                for edge in quant_out_edges:
                    next_name = edge[1]
                    next_node = self.nxgraph.nodes[next_name]
                    for val in ['x', 'y', 'input']:
                        if val in next_node and next_node[val] == out_name:
                            next_node[val] = node_name
                        if 'values' in next_node:
                            for i in range(len(next_node['values'])):
                                if next_node['values'][i] == out_name:
                                    next_node['values'][i] = node_name
                    edge_removals.append((out_name, next_name))
                    edge_adds.append((node_name, next_name))

                for edge in edge_removals:
                    self.nxgraph.remove_edge(edge[0], edge[1])
                for edge in edge_adds:
                    self.nxgraph.add_edge(edge[0], edge[1])

                if len(self.nxgraph.out_edges(x_name)) == 0:
                    remove_nodes.append(x_name)
                if len(self.nxgraph.out_edges(y_name)) == 0:
                    remove_nodes.append(y_name)
                remove_nodes.append(out_name)

            elif data['op'] in ['max_pool']:
                out_edges = list(self.nxgraph.out_edges(node_name))
                if len(out_edges) != 1:
                    continue
                out_name = out_edges[0][1]
                out_node = self.nxgraph.nodes[out_name]
                input_name = data['input']
                input_node = self.nxgraph.nodes[input_name]
                if input_node['op'] != 'dequant' or \
                    out_node['op'] != 'quant':
                    continue

                new_input_node = self.nxgraph.nodes[input_node['x']]
                if 'quant_scale' not in new_input_node:
                    new_input_node['quant_scale'] = input_node['quant_scale'].copy()
                if 'zero_point' not in new_input_node:
                    new_input_node['zero_point'] = input_node['zero_point'].copy()
                if 'quant_axis' not in new_input_node:
                    new_input_node['quant_axis'] = input_node['quant_axis']

                data['input'] = input_node['x']
                self.nxgraph.remove_edge(input_name, node_name)
                self.nxgraph.add_edge(input_node['x'], node_name)
                
                data['datatype'] = out_node['datatype']
                data['quant_scale'] = out_node['quant_scale'].copy()
                data['zero_point'] = out_node['zero_point'].copy()
                data['quant_axis'] = out_node['quant_axis']

                quant_out_edges = self.nxgraph.out_edges(out_name)
                edge_removals = []
                edge_adds = []
                for edge in quant_out_edges:
                    next_name = edge[1]
                    next_node = self.nxgraph.nodes[next_name]
                    for val in ['x', 'y', 'input']:
                        if val in next_node and next_node[val] == out_name:
                            next_node[val] = node_name
                        if 'values' in next_node:
                            for i in range(len(next_node['values'])):
                                if next_node['values'][i] == out_name:
                                    next_node['values'][i] = node_name
                    edge_removals.append((out_name, next_name))
                    edge_adds.append((node_name, next_name))

                for edge in edge_removals:
                    self.nxgraph.remove_edge(edge[0], edge[1])
                for edge in edge_adds:
                    self.nxgraph.add_edge(edge[0], edge[1])

                if len(self.nxgraph.out_edges(input_name)) == 0:
                    remove_nodes.append(input_name)

        self.nxgraph.remove_nodes_from(remove_nodes)

    def clean_quant_dequant(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] != 'dequant':
                continue
            in_node = self.nxgraph.nodes[data['x']]
            if data['quant_axis'] == 1:
                data['quant_axis'] = 0
            if 'quant_scale' in in_node and 'zero_point' in in_node:
                continue
            in_node['quant_scale'] = data['quant_scale']
            in_node['zero_point'] = data['zero_point']
            in_node['quant_axis'] = data['quant_axis']

        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] not in ['quant', 'reshape']:
                continue
            if 'quant_axis' not in data:
                continue
            if data['quant_axis'] == 1:
                data['quant_axis'] = 0

    def find_subgraph_inputs(self):
        inputs_in_graph = True
        outputs_in_graph = True
        for input_name in self.trim_input_names:
            if input_name not in self.nxgraph.nodes:
                inputs_in_graph = False
                break
        for output_name in self.trim_output_names:
            if output_name not in self.nxgraph.nodes:
                outputs_in_graph = False
                break
        if not inputs_in_graph:
            print("WARNING: Cannot find all provided subgraph input\
                names in the graph, using model defaults.")
        if not outputs_in_graph:
            print("WARNING: Cannot find all provided subgraph output\
                names in the graph, using model defaults.")
        if not inputs_in_graph:
            return

        if self.trim_input_names:
            self.input_names = self.trim_input_names[:]
        for name in self.input_names:
            node = self.nxgraph.nodes[name]
            if node['op'] == 'external':
                continue
            keep_params = ['op', 'datatype', 'output_shape',
                'quant_scale', 'zero_point', 'quant_scale', 'format']
            node['op'] = 'external'
            layer_params = list(node.keys())
            for param in layer_params:
                if param not in keep_params:
                    del node[param]

            for edge in list(self.nxgraph.in_edges(name)):
                self.nxgraph.remove_edge(edge[0], edge[1])

    def prune_graph(self):
        if self.trim_input_names:
            for name in self.trim_input_names:
                if name not in self.nxgraph.nodes:
                    raise KeyError("Unable to find %s in the graph, please verify it exists" % name)
                self.nxgraph.nodes[name]['op'] = 'external'
                in_edges = list(self.nxgraph.in_edges(name))
                self.nxgraph.remove_edges_from(in_edges)
            self.input_names = self.trim_input_names

        remove_nodes = list(self.nxgraph.nodes)
        to_explore = self.output_names[:]
        explored = []
        while len(to_explore) > 0:
            exploring = to_explore.pop()
            if exploring in remove_nodes:
                remove_nodes.remove(exploring)
            for edge in self.nxgraph.in_edges(exploring):
                if edge[0] not in explored and edge[0] not in to_explore:
                    to_explore.append(edge[0])
            explored.append(exploring)
        self.nxgraph.remove_nodes_from(remove_nodes)
