# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import math
import networkx as nx
import numpy as np
from deepview_rtm.tflite.Model import Model

tflite_type_map = {
    0: np.dtype('float32'),
    1: np.dtype('float16'),
    2: np.dtype('int32'),
    3: np.dtype('uint8'),
    4: np.dtype('int64'),
    5: np.dtype(object),
    6: np.dtype('bool'),
    7: np.dtype('int16'),
    8: np.dtype('complex64'),
    9: np.dtype('int8'),
    10: np.dtype('float64')
}

activation_map = {
    0: 'linear',
    1: 'relu',
    3: 'relu6',
    4: 'tanh'
}

class TFLiteImporter:
    def __init__(self, input_model, input_format='none', batch=1, subgraph_names=None):
        self.tflite_model = None
        if subgraph_names is None:
            subgraph_names = []
        if type(input_model) == str:
            with open(input_model, 'rb') as f:
                self.tflite_model = Model.GetRootAsModel(f.read(), 0)
        else:
            self.tflite_model = Model.GetRootAsModel(input_model, 0)
        if self.tflite_model.SubgraphsLength() > 1:
            print("WARNING: The TFLite Importer does not support \
                multiple subgraphs, the first subgraph will be imported")
        self.tflite_graph = self.tflite_model.Subgraphs(0)
        self.nxgraph = nx.DiGraph()
        self.import_nxgraph = nx.DiGraph()
        self.input_names = []
        self.output_names = []
        self.input_format = input_format
        self.batch = batch
        self.opcode_dict = {}
        self.gen_opcode_dict()
        self.tensor_map = {}
        self.trim_input_names = []
        self.trim_output_names = []
        if subgraph_names:
            self.trim_input_names = subgraph_names[0]
            self.trim_output_names = subgraph_names[1]
        self.calc_warning_message = "WARNING: Calculations are unable to provide \
                output shape, using tensor shape, which may \
                be incorrect in specific cases."
        self.fuse_act_warning_message = "WARNING: Fused Activation Code %d not supported \
                defaulting to no activation."
        self.calc_not_implemented_message = "Calculation not implemented for %s"
        self.op_not_supported_message = "Operation %s not supported"
    def gen_opcode_dict(self):
        from deepview_rtm.tflite.BuiltinOperator import BuiltinOperator
        overall_dict = {}
        self.gen_enum_dict(BuiltinOperator, overall_dict)
        for i in range(self.tflite_model.OperatorCodesLength()):
            self.opcode_dict[i] = overall_dict[self.tflite_model.OperatorCodes(i).BuiltinCode()]

    @staticmethod
    def gen_enum_dict(source, dest_dict):
        """
        Maps source class to a dictionary
        :param source: Source class to map attributes
        :param dest_dict: Dictionary to map
        :return:
        """
        for attr in dir(source):
            if not attr.startswith('_'):
                dest_dict[getattr(source, attr)] = attr

    def run(self):
        self.generate_import_graph()
        self.import_inputs()
        self.import_constants()
        self.import_operations()
        print("Imported model has %d nodes" % len(self.nxgraph.nodes))
        self.clean_graph()
        print("Cleaned model has %d nodes" % len(self.nxgraph.nodes))

        return self.nxgraph, self.input_names, self.output_names

    def generate_import_graph(self):
        for input_code in self.tflite_graph.InputsAsNumpy():
            input_tensor = self.tflite_graph.Tensors(input_code)
            name = input_tensor.Name().decode('utf-8')
            self.import_nxgraph.add_node(name)
            self.input_names.append(name)

        for output_code in self.tflite_graph.OutputsAsNumpy():
            output_tensor = self.tflite_graph.Tensors(output_code)
            name = output_tensor.Name().decode('utf-8')
            self.output_names.append(name)

        for i in range(self.tflite_graph.TensorsLength()):
            tensor = self.tflite_graph.Tensors(i)
            name = tensor.Name().decode('utf-8')
            self.import_nxgraph.add_node(name)

        for i in range(self.tflite_graph.OperatorsLength()):
            operator = self.tflite_graph.Operators(i)
            for j in range(operator.OutputsLength()):
                otensor_id = operator.Outputs(j)
                otensor = self.tflite_graph.Tensors(otensor_id)
                output_name = otensor.Name().decode('utf-8')
                self.import_nxgraph.add_node(output_name)
                for k in range(operator.InputsLength()):
                    itensor_id = operator.Inputs(k)
                    itensor = self.tflite_graph.Tensors(itensor_id)
                    input_name = itensor.Name().decode('utf-8')
                    self.import_nxgraph.add_edge(input_name, output_name, op=self.opcode_dict[operator.OpcodeIndex()])

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

        if self.trim_input_names:
            all_exist = True
            for name in self.trim_input_names:
                if name not in self.import_nxgraph.nodes:
                    all_exist = False
                    break
            if not all_exist:
                print("WARNING: Provided input names do not exist in the graph, unable to trim inputs.")
            else:
                self.input_names = self.trim_input_names[:]
                remove_nodes = []
                for node_name in self.import_nxgraph.nodes:
                    if node_name in self.input_names:
                        continue
                    path_exists = False
                    for input_name in self.input_names:
                        if nx.has_path(self.import_nxgraph, node_name, input_name):
                            path_exists = True
                            break
                    if path_exists:
                        remove_nodes.append(node_name)
                self.import_nxgraph.remove_nodes_from(remove_nodes)

    def import_inputs(self):
        for input_code in self.tflite_graph.InputsAsNumpy():
            input_tensor = self.tflite_graph.Tensors(input_code)
            name = input_tensor.Name().decode('utf-8')
            if name not in self.import_nxgraph.nodes:
                continue
            datatype = tflite_type_map[input_tensor.Type()]
            output_shape = list(input_tensor.ShapeAsNumpy())

            self.nxgraph.add_node(name,
                                  op='external',
                                  datatype=datatype,
                                  output_shape=output_shape)
            self.tensor_map[input_code] = name

            quant_info = input_tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

    def import_constants(self):
        for i in range(self.tflite_graph.TensorsLength()):
            if i in self.tensor_map.keys():
                continue
            tensor = self.tflite_graph.Tensors(i)
            buf_idx = tensor.Buffer()
            buffer = self.tflite_model.Buffers(buf_idx)
            if buffer.DataLength() == 0:
                continue
            name = tensor.Name().decode('utf-8')
            if name not in self.import_nxgraph.nodes:
                continue
            datatype = tflite_type_map[tensor.Type()]
            if isinstance(tensor.ShapeAsNumpy(), int):
                output_shape = [1]
            else:
                output_shape = list(tensor.ShapeAsNumpy())
            data_buf = buffer.DataAsNumpy()
            if type(data_buf) == int:
                np_tensor = np.asarray([data_buf]).astype(datatype)
                output_shape = [1]
            else:
                np_tensor = np.frombuffer(data_buf,
                                          dtype=datatype)
                if not output_shape:
                    output_shape = list(np_tensor.shape)
            np_tensor = np.reshape(np_tensor, output_shape)
            output_shape = list(np_tensor.shape)

            self.nxgraph.add_node(name,
                                  op='constant',
                                  datatype=datatype,
                                  output_shape=output_shape,
                                  np_tensor=np_tensor)
            self.tensor_map[i] = name
            
            quant_info = tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

    def import_operations(self):
        for i in range(self.tflite_graph.OperatorsLength()):
            operator = self.tflite_graph.Operators(i)
            valid_op = False
            for j in range(operator.OutputsLength()):
                tensor_id = operator.Outputs(j)
                tensor = self.tflite_graph.Tensors(tensor_id)
                name = tensor.Name().decode('utf-8')
                if name in self.import_nxgraph.nodes:
                    valid_op = True
                    break
            if not valid_op:
                continue

            if self.trim_input_names:
                tensor_id = operator.Outputs(0)
                tensor = self.tflite_graph.Tensors(tensor_id)
                name = tensor.Name().decode('utf-8')
                if name in self.trim_input_names and name not in self.nxgraph.nodes:
                    output_shape = list(tensor.ShapeAsNumpy())
                    datatype = tflite_type_map[tensor.Type()]
                    self.nxgraph.add_node(name,
                                          op='external',
                                          datatype=datatype,
                                          output_shape=output_shape)

                    quant_info = tensor.Quantization()
                    if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                        isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                        self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                        self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                        self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()
                    self.tensor_map[tensor_id] = name
                    continue

            op = self.opcode_dict[operator.OpcodeIndex()]
            fun = self.import_unknown
            if hasattr(self, 'import_' + op):
                fun = getattr(self, 'import_' + op)
            fun(operator)

    def clean_graph(self):
        self.modify_to_constants()
        self.clean_filters()
        self.fold_padding()
        self.expand_activations()
        self.prune_graph()

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

    def import_ADD(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        x_name = self.tensor_map[operator.Inputs(0)]
        x_node = self.nxgraph.nodes[x_name]
        y_name = self.tensor_map[operator.Inputs(1)]
        y_node = self.nxgraph.nodes[y_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = self.calc_binary_shape(x_node['output_shape'], y_node['output_shape'])          

        from deepview_rtm.tflite.AddOptions import AddOptions
        options = AddOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'

        self.nxgraph.add_node(name,
                              op='add',
                              x=x_name,
                              y=y_name,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in x_node and 'np_tensor' in y_node:
            out_tensor = np.add(x_node['np_tensor'], y_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_AVERAGE_POOL_2D(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_shape[:]

        from deepview_rtm.tflite.Pool2DOptions import Pool2DOptions
        options = Pool2DOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'
        size = [options.FilterHeight(), options.FilterWidth()]
        stride = [options.StrideH(), options.StrideW()]
        head = [0, 0]
        tail = [0, 0]
        if options.Padding() == 0:
            output_shape[1] = math.ceil(input_shape[1] / stride[0])
            output_shape[2] = math.ceil(input_shape[2] / stride[1])
            hw_in = input_shape[1:3]
            hw_out = output_shape[1:3]
            for i in range(2):
                t = (hw_out[i] - 1) * stride[i] + size[i] - hw_in[i]
                if t > 0:
                    head[i] = (math.floor(t / 2))
                    tail[i] = (math.ceil(t / 2))
        else:
            output_shape[1] = int((input_shape[1] - size[0]) / stride[0]) + 1
            output_shape[2] = int((input_shape[2] - size[1]) / stride[1]) + 1
        size = [1] + size + [1]
        stride = [1] + stride + [1]
        head = [0] + head + [0]
        tail = [0] + tail + [0]

        self.nxgraph.add_node(name,
                              op='avg_pool',
                              input=input_name,
                              size=size,
                              stride=stride,
                              head=head,
                              tail=tail,
                              activation=activation,
                              datatype=datatype,
                              format='nhwc',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message %
                self.opcode_dict[operator.OpcodeIndex()])

    def import_CONCATENATION(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        values = []
        value_nodes = []
        for i in range(operator.InputsLength()):
            values.append(self.tensor_map[operator.Inputs(i)])
            value_nodes.append(self.nxgraph.nodes[values[i]])
        datatype = tflite_type_map[tensor.Type()]

        from deepview_rtm.tflite.ConcatenationOptions import ConcatenationOptions
        options = ConcatenationOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'
        axis = int(options.Axis())
        if axis < 0:
            axis += len(value_nodes[0]['output_shape'])

        output_shape = value_nodes[0]['output_shape'][:]
        for i in range(1, len(value_nodes)):
            output_shape[axis] += value_nodes[i]['output_shape'][axis]

        self.nxgraph.add_node(name,
                              op='concat',
                              values=values,
                              axis=axis,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        for input_name in values:
            self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        calc_node = True
        for node in value_nodes:
            if 'np_tensor' not in node:
                calc_node = False
                break
        
        if calc_node:
            value_tensors = []
            for node in value_nodes:
                value_tensors.append(node['np_tensor'].copy())
            out_tensor = np.concatenate(value_tensors, axis=axis)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_CONV(self, operator, depthwise=False):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        if input_node['op'] == 'space_to_batch':
            input_name = input_node['input']
        input_shape = input_node['output_shape']
        filt_name = self.tensor_map[operator.Inputs(1)]
        filt_node = self.nxgraph.nodes[filt_name]
        bias_name = self.tensor_map[operator.Inputs(2)]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_shape[:]

        if depthwise:
            from deepview_rtm.tflite.DepthwiseConv2DOptions import DepthwiseConv2DOptions
            options = DepthwiseConv2DOptions()
            output_shape[3] = filt_node['output_shape'][3]
        else:
            from deepview_rtm.tflite.Conv2DOptions import Conv2DOptions
            options = Conv2DOptions()
            output_shape[3] = filt_node['output_shape'][0]
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'
        if depthwise:
            if output_shape[3] % options.DepthMultiplier() != 0:
                raise ValueError("Improper depth multipler for input channels \
                    %d, output channels %d and depth multiplier %d" % (
                        input_node['output_shape'][3], output_shape[3],
                        options.DepthMultiplier()))
            groups = int(output_shape[3] // options.DepthMultiplier())
        else:
            groups = 1
        if input_node['op'] == 'space_to_batch':
            dilation = input_node['dilation'][:]
        else:
            dilation = [options.DilationHFactor(), options.DilationWFactor()]
        stride = [options.StrideH(), options.StrideW()]
        head = [0, 0]
        tail = [0, 0]
        if options.Padding() == 0 or input_node['op'] == 'space_to_batch':
            filt_size = filt_node['output_shape'][1:3]
            output_shape[1] = math.ceil(input_shape[1] / stride[0])
            output_shape[2] = math.ceil(input_shape[2] / stride[1])
            hw_in = input_node['output_shape'][1:3]
            hw_out = output_shape[1:3]
            for i in range(2):
                fd = (filt_size[i] - 1) * dilation[i] + 1
                t = (hw_out[i] - 1) * stride[i] + fd - hw_in[i]
                if t > 0:
                    head[i] = (math.floor(t / 2))
                    tail[i] = (math.ceil(t / 2))
        else:
            size = filt_node['output_shape'][1:3]
            h_fd = (size[0] - 1) * dilation[0] + 1
            w_fd = (size[1] - 1) * dilation[1] + 1
            output_shape[1] = int((input_shape[1] - h_fd) / stride[0]) + 1
            output_shape[2] = int((input_shape[2] - w_fd) / stride[1]) + 1
        dilation = [1] + dilation + [1]
        stride = [1] + stride + [1]
        head = [0] + head + [0]
        tail = [0] + tail + [0]

        self.nxgraph.add_node(name,
                              op='conv',
                              input=input_name,
                              filter=filt_name,
                              bias=bias_name,
                              dilation=dilation,
                              stride=stride,
                              head=head,
                              tail=tail,
                              groups=groups,
                              activation=activation,
                              datatype=datatype,
                              format='nhwc',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(filt_name, name)
        self.nxgraph.add_edge(bias_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message %
                self.opcode_dict[operator.OpcodeIndex()])

        if input_node['op'] == 'space_to_batch':
            self.nxgraph.remove_node(self.tensor_map[operator.Inputs(0)])

    def import_CONV_2D(self, operator):
        self.import_CONV(operator)

    def import_DEPTHWISE_CONV_2D(self, operator):
        self.import_CONV(operator, True)

    def import_DEPTH_TO_SPACE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_DEQUANTIZE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape'][:]

        scale = input_node['quant_scale']
        zero_point = input_node['zero_point']

        self.nxgraph.add_node(name,
                              op='dequant',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            scale = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            zero_point = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = ((input_node['np_tensor'] - zero_point) * scale).astype(datatype)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor
    
    def import_EMBEDDING_LOOKUP(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_FLOOR(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='floor',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.floor(input_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_FULLY_CONNECTED(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        a_name = self.tensor_map[operator.Inputs(0)]
        a_node = self.nxgraph.nodes[a_name]
        b_name = self.tensor_map[operator.Inputs(1)]
        b_node = self.nxgraph.nodes[b_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = [a_node['output_shape'][0], b_node['output_shape'][0]]

        if operator.Inputs(2) >= 0:
            bias_name = self.tensor_map[operator.Inputs(2)]
            bias_node = self.nxgraph.nodes[bias_name]
        else:
            bias_shape = [output_shape[-1]]
            np_tensor = np.zeros(bias_shape, dtype=datatype)
            bias_name = name + '_dv_linear_zeros_bias'
            self.nxgraph.add_node(bias_name,
                                  op='constant',
                                  datatype=datatype,
                                  output_shape=bias_shape,
                                  np_tensor=np_tensor)
            
            if datatype in [np.int8, np.int32, np.uint8]:
                self.nxgraph.nodes[bias_name]['quant_scale'] = np.asarray([1]).astype(np.float32)
                self.nxgraph.nodes[bias_name]['zero_point'] = np.asarray([0]).astype(datatype)
                self.nxgraph.nodes[bias_name]['quant_axis'] = 0

        from deepview_rtm.tflite.FullyConnectedOptions import FullyConnectedOptions
        options = FullyConnectedOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'

        self.nxgraph.add_node(name,
                              op='linear',
                              A=a_name,
                              B=b_name,
                              bias=bias_name,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(a_name, name)
        self.nxgraph.add_edge(b_name, name)
        self.nxgraph.add_edge(bias_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in a_node and 'np_tensor' in b_node and 'np_tensor' in bias_node:
            out_tensor = np.matmul(a_node['np_tensor'], b_node['np_tensor'])
            out_tensor = np.add(out_tensor, bias_node['np_tensor'])
            self.nxgraph.nodes[name] = out_tensor

    def import_HASHTABLE_LOOKUP(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_L2_NORMALIZATION(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape'][:]

        self.nxgraph.add_node(name,
                              op='l2_normalization',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_L2_POOL_2D(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LOCAL_RESPONSE_NORMALIZATION(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LOGISTIC(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='sigmoid',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = 1 / (1 + np.exp(-1 * input_node['np_tensor']))
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor
    
    def import_LSH_PROJECTION(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LSTM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_MAX_POOL_2D(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_shape[:]

        from deepview_rtm.tflite.Pool2DOptions import Pool2DOptions
        options = Pool2DOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'
        size = [options.FilterHeight(), options.FilterWidth()]
        stride = [options.StrideH(), options.StrideW()]
        head = [0, 0]
        tail = [0, 0]
        if options.Padding() == 0:
            output_shape[1] = math.ceil(input_shape[1] / stride[0])
            output_shape[2] = math.ceil(input_shape[2] / stride[1])
            hw_in = input_shape[1:3]
            hw_out = output_shape[1:3]
            for i in range(2):
                t = (hw_out[i] - 1) * stride[i] + size[i] - hw_in[i]
                if t > 0:
                    head[i] = (math.floor(t / 2))
                    tail[i] = (math.ceil(t / 2))
        else:
            output_shape[1] = int((input_shape[1] - size[0]) / stride[0]) + 1
            output_shape[2] = int((input_shape[2] - size[1]) / stride[1]) + 1
        size = [1] + size + [1]
        stride = [1] + stride + [1]
        head = [0] + head + [0]
        tail = [0] + tail + [0]

        self.nxgraph.add_node(name,
                              op='max_pool',
                              input=input_name,
                              size=size,
                              stride=stride,
                              head=head,
                              tail=tail,
                              activation=activation,
                              datatype=datatype,
                              format='nhwc',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_MUL(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        x_name = self.tensor_map[operator.Inputs(0)]
        x_node = self.nxgraph.nodes[x_name]
        y_name = self.tensor_map[operator.Inputs(1)]
        y_node = self.nxgraph.nodes[y_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = self.calc_binary_shape(x_node['output_shape'], y_node['output_shape'])

        from deepview_rtm.tflite.MulOptions import MulOptions
        options = MulOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'

        self.nxgraph.add_node(name,
                              op='mul',
                              x=x_name,
                              y=y_name,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in x_node and 'np_tensor' in y_node:
            out_tensor = np.multiply(x_node['np_tensor'], y_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_RELU(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='relu',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_RELU_N1_TO_1(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_RELU6(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='relu6',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_RESHAPE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        shape_name = self.tensor_map[operator.Inputs(1)]
        shape_node = self.nxgraph.nodes[shape_name]
        datatype = tflite_type_map[tensor.Type()]

        if 'np_tensor' in shape_node:
            out_shape = list(np.reshape(shape_node['np_tensor'], [-1]))
        else:
            print(self.calc_warning_message)
            out_shape = list(tensor.ShapeAsNumpy())
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

        for i in range(len(out_shape)):
            if out_shape[i] == 0:
                output_shape[i] = input_shape[i]
            elif out_shape[i] == -1:
                output_shape[i] = neg_shape
            else:
                output_shape[i] = out_shape[i]

        self.nxgraph.add_node(name,
                              op='reshape',
                              input=input_name,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.reshape(input_node['np_tensor'], output_shape)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_RESIZE_BILINEAR(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        shape_name = self.tensor_map[operator.Inputs(1)]
        shape = list(self.nxgraph.nodes[shape_name]['np_tensor'])
        datatype = tflite_type_map[tensor.Type()]
        output_shape = [input_shape[0]] + shape + [input_shape[-1]]

        from deepview_rtm.tflite.ResizeBilinearOptions import ResizeBilinearOptions
        options = ResizeBilinearOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        align_corners = options.AlignCorners()
        half_pixel_centers = options.HalfPixelCenters()

        self.nxgraph.add_node(name,
                              op='resize',
                              input=input_name,
                              mode=1,
                              align_corners=align_corners,
                              half_pixel_centers=half_pixel_centers,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name
        
        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_RNN(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SOFTMAX(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape'][:]

        from deepview_rtm.tflite.SoftmaxOptions import SoftmaxOptions
        options = SoftmaxOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        axes = [1]
        beta = options.Beta()

        self.nxgraph.add_node(name,
                              op='softmax',
                              x=input_name,
                              axes=axes,
                              beta=beta,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            num_tensor = np.exp(input_node['np_tensor'])
            den_tensor = np.sum(np.exp(input_node['np_tensor'] * beta), axes=tuple(axes))
            out_tensor = np.divide(num_tensor, den_tensor)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_SPACE_TO_DEPTH(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SVDF(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_TANH(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='tanh',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.tanh(input_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_CONCAT_EMBEDDINGS(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SKIP_GRAM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_CALL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_CUSTOM(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        print(name)
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_EMBEDDING_LOOKUP_SPARSE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_PAD(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape'][:]
        pad_name = self.tensor_map[operator.Inputs(1)]
        pad_node = self.nxgraph.nodes[pad_name]
        datatype = tflite_type_map[tensor.Type()]
        pad_value = pad_node['np_tensor']
        output_shape = []
        head = []
        tail = []

        for i in range(len(pad_value)):
            head.append(pad_value[i][0])
            tail.append(pad_value[i][1])
            output_shape.append(head[i] + input_shape[i] + tail[i])

        self.nxgraph.add_node(name,
                              op='pad',
                              input=input_name,
                              head=head,
                              tail=tail,
                              value=0,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()
        self.tensor_map[tensor_id] = name

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_UNIDIRECTIONAL_SEQUENCE_RNN(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_GATHER(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_BATCH_TO_SPACE_ND(self, operator):
        tensor_id = operator.Outputs(0)
        input_name = self.tensor_map[operator.Inputs(0)]
        self.tensor_map[tensor_id] = input_name

    def import_SPACE_TO_BATCH_ND(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        output_shape = input_node['output_shape'][:]
        datatype = input_node['datatype']
        dilation_name = self.tensor_map[operator.Inputs(1)]
        dilation_node = self.nxgraph.nodes[dilation_name]
        dilation = list(dilation_node['np_tensor'])

        self.nxgraph.add_node(name,
                              op='space_to_batch',
                              input=input_name,
                              dilation=dilation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

    def import_TRANSPOSE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        perm_name = self.tensor_map[operator.Inputs(1)]
        perm_node = self.nxgraph.nodes[perm_name]
        datatype = tflite_type_map[tensor.Type()]

        if 'np_tensor' in perm_node:
            perms = list(np.reshape(perm_node['np_tensor'], [-1]))
        else:
            raise ValueError("Unable to retrieve perm values from \
                node %s." % perm_name)

        output_shape = []
        for i in range(len(perms)):
            output_shape.append(input_shape[perms[i]])

        self.nxgraph.add_node(name,
                              op='transpose',
                              input=input_name,
                              axes=perms,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.transpose(input_node['np_tensor'], axes=perms)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_MEAN(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        axes_name = self.tensor_map[operator.Inputs(1)]
        axes_node = self.nxgraph.nodes[axes_name]
        datatype = tflite_type_map[tensor.Type()]

        axes = []
        for val in axes_node['np_tensor']:
            if val < 0:
                axes.append(int(val + len(input_shape)))
            else:
                axes.append(int(val))
        axes.sort()

        from deepview_rtm.tflite.ReducerOptions import ReducerOptions
        options = ReducerOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        keep_dims = options.KeepDims()

        reduced_shape = input_shape[:]
        for axis in axes:
            reduced_shape[axis] = 1
        output_shape = input_shape[:]
        for axis in reversed(axes):
            output_shape.pop(axis)

        quant_info = tensor.Quantization()        
        if keep_dims:
            self.nxgraph.add_node(name + '_mean_reduction_dv',
                                  op='mean_reduce',
                                  input=input_name,
                                  axes=axes,
                                  datatype=datatype,
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name + '_mean_reduction_dv')
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name + '_mean_reduction_dv']['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name + '_mean_reduction_dv']['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name + '_mean_reduction_dv']['quant_axis'] = quant_info.QuantizedDimension()
            self.nxgraph.add_node(name,
                                  op='reshape',
                                  input=name + '_mean_reduction_dv',
                                  datatype=datatype,
                                  output_shape=reduced_shape)
            self.nxgraph.add_edge(name + '_mean_reduction_dv', name)
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()
            self.tensor_map[tensor_id] = name
        else:
            self.nxgraph.add_node(name,
                                  op='mean_reduce',
                                  input=input_name,
                                  axes=axes,
                                  datatype=datatype,
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name)
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()
            self.tensor_map[tensor_id] = name

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_SUB(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        x_name = self.tensor_map[operator.Inputs(0)]
        x_node = self.nxgraph.nodes[x_name]
        y_name = self.tensor_map[operator.Inputs(1)]
        y_node = self.nxgraph.nodes[y_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = self.calc_binary_shape(x_node['output_shape'], y_node['output_shape'])          

        from deepview_rtm.tflite.SubOptions import SubOptions
        options = SubOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'

        self.nxgraph.add_node(name,
                              op='sub',
                              x=x_name,
                              y=y_name,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in x_node and 'np_tensor' in y_node:
            out_tensor = np.sub(x_node['np_tensor'], y_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_DIV(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        x_name = self.tensor_map[operator.Inputs(0)]
        x_node = self.nxgraph.nodes[x_name]
        y_name = self.tensor_map[operator.Inputs(1)]
        y_node = self.nxgraph.nodes[y_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = self.calc_binary_shape(x_node['output_shape'], y_node['output_shape'])          

        from deepview_rtm.tflite.DivOptions import DivOptions
        options = DivOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        if options.FusedActivationFunction() in activation_map.keys():
            activation = activation_map[options.FusedActivationFunction()]
        else:
            print(self.fuse_act_warning_message)
            activation = 'linear'

        self.nxgraph.add_node(name,
                              op='div',
                              x=x_name,
                              y=y_name,
                              activation=activation,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(x_name, name)
        self.nxgraph.add_edge(y_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in x_node and 'np_tensor' in y_node:
            out_tensor = np.divide(x_node['np_tensor'], y_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_SQUEEZE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        datatype = tflite_type_map[tensor.Type()]

        from deepview_rtm.tflite.SqueezeOptions import SqueezeOptions
        options = SqueezeOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)

        dims = options.SqueezeDimsAsNumpy()
        if type(dims) == int:
            dims = []
        else:
            dims = list(dims)

        output_shape = []
        for i in range(len(input_shape)):
            if i not in dims:
                output_shape.append(input_shape[i])

        self.nxgraph.add_node(name,
                              op='reshape',
                              input=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.reshape(input_node['np_tensor'], output_shape)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_UNIDIRECTIONAL_SEQUENCE_LSTM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_STRIDED_SLICE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        begin_name = self.tensor_map[operator.Inputs(1)]
        begin_node = self.nxgraph.nodes[begin_name]
        end_name = self.tensor_map[operator.Inputs(2)]
        end_node = self.nxgraph.nodes[end_name]
        stride_name = self.tensor_map[operator.Inputs(3)]
        strides = list(self.nxgraph.nodes[stride_name]['np_tensor'])
        for i in range(len(strides)):
            if strides[i] < 0:
                strides[i] += input_shape[i] + 1
        datatype = tflite_type_map[tensor.Type()]

        axes = list(range(len(input_shape)))
        begin_mask = len(axes) * [False]
        end_mask = len(axes) * [False]
        ellipsis_mask = len(axes) * [False]
        new_axis_mask = len(axes) * [False]
        shrink_axis_mask = len(axes) * [False]

        from deepview_rtm.tflite.StridedSliceOptions import StridedSliceOptions
        options = StridedSliceOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        for i in range(len(axes)):
            begin_mask[i] = bool((1 << i) & options.BeginMask())
            end_mask[i] = bool((1 << i) & options.EndMask())
            ellipsis_mask[i] = bool((1 << i) & options.EllipsisMask())
            new_axis_mask[i] = bool((1 << i) & options.NewAxisMask())
            shrink_axis_mask[i] = bool((1 << i) & options.ShrinkAxisMask())

        begin = []
        end = []
        output_shape = []
        assert(len(begin_node['np_tensor']) == 1,
            "The begin node does not have a valid shape")
        assert(len(end_node['np_tensor']) == 1,
            "The end node does not have a valid shape")
        for i in range(len(begin_node['np_tensor'])):
            if begin_mask[i]:
                begin.append(0)
            else:
                if begin_node['np_tensor'][i] < 0:
                    begin.append(int(begin_node['np_tensor'][i]) + input_shape[i])
                else:
                    begin.append(int(begin_node['np_tensor'][i]))
        for i in range(len(end_node['np_tensor'])):
            if end_mask[i]:
                end.append(input_shape[i])
            else:
                if end_node['np_tensor'][i] < 0:

                    end.append(int(end_node['np_tensor'][i]) + input_shape[i])
                else:
                    if int(end_node['np_tensor'][i]) < input_shape[i]:
                        end.append(int(end_node['np_tensor'][i]))
                    else:
                        end.append(int(input_shape[i]))
            output_shape.append(math.ceil((end[i] - begin[i]) / strides[i]))
            

        # TODO: Add support for all of the different masks
        
        self.nxgraph.add_node(name,
                              op='slice',
                              input=input_name,
                              axes=axes,
                              begin=begin,
                              end=end,
                              strides=strides,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            slice_obj = []
            for i in range(len(axes)):
                slice_obj.append(slice(begin[i], end[i]))
            slice_obj = tuple(slice_obj)
            out_tensor = input_node['np_tensor'].copy()[slice_obj]
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_BIDIRECTIONAL_SEQUENCE_RNN(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_EXP(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='exp',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.exp(input_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_TOPK_V2(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SPLIT(self, operator):
        input_name = self.tensor_map[operator.Inputs(1)]
        input_node = self.nxgraph.nodes[input_name]
        split_name = self.tensor_map[operator.Inputs(0)]
        split_axis = self.nxgraph.nodes[split_name]['np_tensor'][0]
        input_shape = input_node['output_shape']

        if split_axis < 0:
            split_axis += len(input_shape)
        if input_shape[split_axis] % operator.OutputsLength() != 0:
            raise ValueError("Cannot split node into equal segments.")
        split_shape = input_shape[split_axis] // operator.OutputsLength()
        output_shape = input_shape[:]
        output_shape[split_axis] = split_shape

        for i in range(operator.OutputsLength()):
            tensor_id = operator.Outputs(i)
            tensor = self.tflite_graph.Tensors(tensor_id)
            name = tensor.Name().decode('utf-8')
            datatype = tflite_type_map[tensor.Type()]
            axes = list(range(len(input_shape)))
            begin = len(input_shape) * [0]
            end = input_shape[:]
            begin[split_axis] = i * split_shape
            end[split_axis] = (i + 1) * split_shape

            self.nxgraph.add_node(name,
                                  op='slice',
                                  input=input_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=datatype,
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name)
            self.tensor_map[tensor_id] = name

            quant_info = tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

            if 'np_tensor' in input_node:
                slice_obj = []
                for i in range(len(axes)):
                    slice_obj.append(slice(begin[i], end[i]))
                slice_obj = tuple(slice_obj)
                out_tensor = input_node['np_tensor'].copy()[slice_obj]
                self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_LOG_SOFTMAX(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_DELEGATE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_BIDIRECTIONAL_SEQUENCE_LSTM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_CAST(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='cast',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_PRELU(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        scale_name = self.tensor_map[operator.Inputs(1)]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='prelu',
                              x=input_name,
                              scales=scale_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(scale_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_MAXIMUM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ARG_MAX(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_MINIMUM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LESS(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_NEG(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='neg',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_PADV2(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape'][:]
        pad_name = self.tensor_map[operator.Inputs(1)]
        pad_node = self.nxgraph.nodes[pad_name]
        datatype = tflite_type_map[tensor.Type()]
        pad_shape = pad_node['np_tensor']
        pad_value_name = self.tensor_map[operator.Inputs(2)]
        pad_value_node = self.nxgraph.nodes[pad_value_name]
        pad_value = pad_value_node['np_tensor'][0]
        output_shape = []
        head = []
        tail = []

        for i in range(len(pad_shape)):
            head.append(pad_shape[i][0])
            tail.append(pad_shape[i][1])
            output_shape.append(head[i] + input_shape[i] + tail[i])

        self.nxgraph.add_node(name,
                              op='pad',
                              input=input_name,
                              head=head,
                              tail=tail,
                              value=pad_value,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()
        self.tensor_map[tensor_id] = name

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_GREATER(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_GREATER_EQUAL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LESS_EQUAL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SELECT(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SLICE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        begin_name = self.tensor_map[operator.Inputs(1)]
        begin_node = self.nxgraph.nodes[begin_name]
        size_name = self.tensor_map[operator.Inputs(2)]
        size_node = self.nxgraph.nodes[size_name]
        datatype = tflite_type_map[tensor.Type()]

        axes = list(range(len(input_shape)))

        begin = []
        end = []
        output_shape = []
        assert(len(begin_node['np_tensor']) == 1,
            "The begin node does not have a valid shape")
        assert(len(size_node['np_tensor']) == 1,
            "The end node does not have a valid shape")
        for i in range(len(begin_node['np_tensor'])):
            if begin_node['np_tensor'][i] < 0:
                begin.append(int(begin_node['np_tensor'][i]) + input_shape[i])
            else:
                begin.append(int(begin_node['np_tensor'][i]))
        for i in range(len(size_node['np_tensor'])):
            if size_node['np_tensor'][i] < 0:
                end.append(input_shape[i])
            else:
                end.append(begin[i] + int(size_node['np_tensor'][i]))
            output_shape.append(end[i] - begin[i])
        
        self.nxgraph.add_node(name,
                              op='slice',
                              input=input_name,
                              axes=axes,
                              begin=begin,
                              end=end,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            slice_obj = []
            for i in range(len(axes)):
                slice_obj.append(slice(begin[i], end[i]))
            slice_obj = tuple(slice_obj)
            out_tensor = input_node['np_tensor'].copy()[slice_obj]
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_SIN(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='sin',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_TRANSPOSE_CONV(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(2)]
        input_node = self.nxgraph.nodes[input_name]
        filt_name = self.tensor_map[operator.Inputs(1)]
        filt_node = self.nxgraph.nodes[filt_name]
        datatype = tflite_type_map[tensor.Type()]
        shape_name = self.tensor_map[operator.Inputs(0)]
        shape_node = self.nxgraph.nodes[shape_name]

        if operator.Inputs(3) >= 0:
            bias_name = self.tensor_map[operator.Inputs(3)]
        else:
            bias_name = None

        if 'np_tensor' in shape_node:
            output_shape = list(np.reshape(shape_node['np_tensor'], [-1]))
        else:
            print(self.calc_warning_message)
            output_shape = list(tensor.ShapeAsNumpy())


        from deepview_rtm.tflite.TransposeConvOptions import TransposeConvOptions
        options = TransposeConvOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        activation = 'linear'
        dilation = [1, 1]
        stride = [options.StrideH(), options.StrideW()]
        head = [0, 0]
        tail = [0, 0]
        if options.Padding() == 0:
            filt_size = filt_node['output_shape'][1:3]
            hw_in = input_node['output_shape'][1:3]
            hw_out = output_shape[1:3]
            for i in range(2):
                head[i] = math.ceil((stride[i] * (hw_in[i] - 1) + filt_size[i] - hw_out[i]) / 2)
                tail[i] = (stride[i] * (hw_in[i] - 1) + filt_size[i] - hw_out[i]) // 2
        dilation = [1] + dilation + [1]
        stride = [1] + stride + [1]
        head = [0] + head + [0]
        tail = [0] + tail + [0]

        self.nxgraph.add_node(name,
                              op='transpose_conv',
                              input=input_name,
                              filter=filt_name,
                              dilation=dilation,
                              stride=stride,
                              head=head,
                              tail=tail,
                              activation=activation,
                              datatype=datatype,
                              format='nhwc',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(filt_name, name)
        if bias_name is not None:
            self.nxgraph.nodes[name]['bias'] = bias_name
            self.nxgraph.add_edge(bias_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_SPARSE_TO_DENSE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_TILE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_EXPAND_DIMS(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        expand_name = self.tensor_map[operator.Inputs(1)]
        expand_node = self.nxgraph.nodes[expand_name]
        datatype = tflite_type_map[tensor.Type()]

        expand_axis = 0
        if 'np_tensor' in expand_node:
            expand_axis = expand_node['np_tensor'][0]
        else:
            raise ValueError("Cannot determine dimension to expand: %s" % name)
        if expand_axis < 0:
            expand_axis += len(input_shape) + 1

        output_shape = input_shape[:]
        output_shape.insert(expand_axis, 1)

        self.nxgraph.add_node(name,
                              op='reshape',
                              input=input_name,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.reshape(input_node['np_tensor'], output_shape)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_EQUAL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_NOT_EQUAL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LOG(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SUM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SQRT(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='sqrt',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_RSQRT(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SHAPE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape'][:]
        datatype = tflite_type_map[tensor.Type()]

        np_tensor = np.asarray(input_shape).astype(datatype)
        output_shape = [len(input_shape)]

        self.nxgraph.add_node(name,
                              op='constant',
                              datatype=datatype,
                              output_shape=output_shape,
                              np_tensor=np_tensor)
        self.tensor_map[tensor_id] = name

    def import_POW(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ARG_MIN(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_FAKE_QUANT(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_REDUCE_PROD(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_REDUCE_MAX(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_PACK(self, operator):
        # TODO: Add support for the other versions of pack where it's not individual elements
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        values = []
        value_nodes = []
        single_val = False
        for i in range(operator.InputsLength()):
            values.append(self.tensor_map[operator.Inputs(i)])
            value_nodes.append(self.nxgraph.nodes[values[i]])
            if self.nxgraph.nodes[values[i]]['output_shape'] == [1]:
                single_val = True
        datatype = tflite_type_map[tensor.Type()]

        from deepview_rtm.tflite.PackOptions import PackOptions
        options = PackOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        axis = int(options.Axis())

        if single_val:
            output_shape = value_nodes[0]['output_shape'][:]
            for i in range(1, len(value_nodes)):
                output_shape[axis] += value_nodes[i]['output_shape'][axis]
        else:
            output_shape = value_nodes[0]['output_shape'][:]
            output_shape.insert(axis, len(value_nodes))
            unique_inputs = []
            for in_name in values:
                if in_name not in unique_inputs:
                    unique_inputs.append(in_name)
            
            reshape_shape = value_nodes[0]['output_shape'][:]
            reshape_shape.insert(axis, 1)
            for in_name in unique_inputs:
                self.nxgraph.add_node(in_name + '_dv_pack_reshape',
                                      op='reshape',
                                      input=in_name,
                                      datatype=self.nxgraph.nodes[in_name]['datatype'],
                                      output_shape=reshape_shape[:])
                if 'quant_scale' in self.nxgraph.nodes[in_name]:
                    reshape_node = self.nxgraph.nodes[in_name + '_dv_pack_reshape']
                    reshape_node['quant_scale'] = self.nxgraph.nodes[in_name]['quant_scale'].copy()
                    reshape_node['zero_point'] = self.nxgraph.nodes[in_name]['zero_point'].copy()
                    reshape_node['quant_axis'] = self.nxgraph.nodes[in_name]['quant_axis']
                self.nxgraph.add_edge(in_name, in_name + '_dv_pack_reshape')
                while in_name in values:
                    index = values.index(in_name)
                    values[index] = in_name + '_dv_pack_reshape'

        self.nxgraph.add_node(name,
                              op='concat',
                              values=values,
                              axis=axis,
                              activation='linear',
                              datatype=datatype,
                              output_shape=output_shape[:])

        for input_name in values:
            self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        calc_node = True
        for node in value_nodes:
            if 'np_tensor' not in node:
                calc_node = False
                break
        
        if calc_node:
            value_tensors = []
            for node in value_nodes:
                value_tensors.append(node['np_tensor'].copy())
            out_tensor = np.concatenate(value_tensors, axis=axis)
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_LOGICAL_OR(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ONE_HOT(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LOGICAL_AND(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_LOGICAL_NOT(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_UNPACK(self, operator):
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']

        from deepview_rtm.tflite.UnpackOptions import UnpackOptions
        options = UnpackOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        split_axis = options.Axis()

        if split_axis < 0:
            split_axis += len(input_shape)
        if input_shape[split_axis] % operator.OutputsLength() != 0:
            raise ValueError("Cannot split node into equal segments.")
        split_shape = input_shape[split_axis] // operator.OutputsLength()
        output_shape = input_shape[:]
        output_shape[split_axis] = split_shape
        unpack_shape = output_shape[:]
        unpack_shape.pop(split_axis)

        for i in range(operator.OutputsLength()):
            tensor_id = operator.Outputs(i)
            tensor = self.tflite_graph.Tensors(tensor_id)
            name = tensor.Name().decode('utf-8')
            datatype = tflite_type_map[tensor.Type()]
            axes = list(range(len(input_shape)))
            begin = len(input_shape) * [0]
            end = input_shape[:]
            begin[split_axis] = i * split_shape
            end[split_axis] = (i + 1) * split_shape

            self.nxgraph.add_node(name + '_dv_slice',
                                  op='slice',
                                  input=input_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=datatype,
                                  output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name + '_dv_slice')

            self.nxgraph.add_node(name,
                                  op='reshape',
                                  input=name + '_dv_slice',
                                  datatype=datatype,
                                  format='none',
                                  output_shape=unpack_shape)
            self.nxgraph.add_edge(name + '_dv_slice', name)
            self.tensor_map[tensor_id] = name

            quant_info = tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name + '_dv_slice']['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name + '_dv_slice']['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name + '_dv_slice']['quant_axis'] = quant_info.QuantizedDimension()
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

            if 'np_tensor' in input_node:
                slice_obj = []
                for i in range(len(axes)):
                    slice_obj.append(slice(begin[i], end[i]))
                slice_obj = tuple(slice_obj)
                out_tensor = input_node['np_tensor'].copy()[slice_obj]
                self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_REDUCE_MIN(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_FLOOR_DIV(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_REDUCE_ANY(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SQUARE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ZEROS_LIKE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_FILL(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        shape_name = self.tensor_map[operator.Inputs(0)]
        shape_node = self.nxgraph.nodes[shape_name]
        fill_name = self.tensor_map[operator.Inputs(1)]
        fill_node = self.nxgraph.nodes[fill_name]
        datatype = tflite_type_map[tensor.Type()]

        if 'np_tensor' in shape_node:
            out_shape = list(np.reshape(shape_node['np_tensor'], [-1]))
        else:
            print(self.calc_warning_message)
            out_shape = list(tensor.ShapeAsNumpy())

        if 'np_tensor' not in fill_node:
            raise ValueError("Unable to calculate fill value for node %s." % name)
        fill_value = fill_node['np_tensor'][0]
        
        np_tensor = np.zeros(out_shape).astype(datatype)
        np_tensor.fill(fill_value)

        self.nxgraph.add_node(name,
                              op='constant',
                              datatype=datatype,
                              output_shape=out_shape,
                              np_tensor=np_tensor)
        self.tensor_map[tensor_id] = name

    def import_FLOOR_MOD(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_RANGE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_RESIZE_NEAREST_NEIGHBOR(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        input_shape = input_node['output_shape']
        shape_name = self.tensor_map[operator.Inputs(1)]
        shape = list(self.nxgraph.nodes[shape_name]['np_tensor'])
        datatype = tflite_type_map[tensor.Type()]
        output_shape = [input_shape[0]] + shape + [input_shape[-1]]

        from deepview_rtm.tflite.ResizeNearestNeighborOptions import ResizeNearestNeighborOptions
        options = ResizeNearestNeighborOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        align_corners = options.AlignCorners()
        half_pixel_centers = options.HalfPixelCenters()

        self.nxgraph.add_node(name,
                              op='resize',
                              input=input_name,
                              mode=0,
                              align_corners=align_corners,
                              half_pixel_centers=half_pixel_centers,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name
        
        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_LEAKY_RELU(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        from deepview_rtm.tflite.LeakyReluOptions import LeakyReluOptions
        options = LeakyReluOptions()
        options.Init(operator.BuiltinOptions().Bytes, operator.BuiltinOptions().Pos)
        alpha = options.Alpha()

        self.nxgraph.add_node(name,
                              op='leaky_relu',
                              x=input_name,
                              alpha=alpha,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_SQUARED_DIFFERENCE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_MIRROR_PAD(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ABS(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='abs',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            out_tensor = np.absolute(input_node['np_tensor'])
            self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_SPLIT_V(self, operator):
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        end_name = self.tensor_map[operator.Inputs(1)]
        end_vals = list(self.nxgraph.nodes[end_name]['np_tensor'])
        split_name = self.tensor_map[operator.Inputs(2)]
        split_axis = self.nxgraph.nodes[split_name]['np_tensor'][0]
        input_shape = input_node['output_shape']
        output_shape = input_shape[:]

        for i in range(len(end_vals)):
            if end_vals[i] == -1:
                split_amt = 0
                for j in range(i):
                    split_amt += end_vals[j]
                end_vals[i] = input_shape[split_axis] - split_amt

        if split_axis < 0:
            split_axis += len(input_shape)

        start_val = 0
        for i in range(operator.OutputsLength()):
            tensor_id = operator.Outputs(i)
            tensor = self.tflite_graph.Tensors(tensor_id)
            name = tensor.Name().decode('utf-8')
            datatype = tflite_type_map[tensor.Type()]
            axes = list(range(len(input_shape)))
            begin = len(input_shape) * [0]
            end = input_shape[:]
            begin[split_axis] = start_val
            end[split_axis] = start_val + end_vals[i]
            start_val += end_vals[i]
            output_shape[split_axis] = end[split_axis] - begin[split_axis]

            self.nxgraph.add_node(name,
                                  op='slice',
                                  input=input_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=datatype,
                                  output_shape=output_shape[:])
            self.nxgraph.add_edge(input_name, name)
            self.tensor_map[tensor_id] = name

            quant_info = tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

            if 'np_tensor' in input_node:
                slice_obj = []
                for i in range(len(axes)):
                    slice_obj.append(slice(begin[i], end[i]))
                slice_obj = tuple(slice_obj)
                out_tensor = input_node['np_tensor'].copy()[slice_obj]
                self.nxgraph.nodes[name]['np_tensor'] = out_tensor

    def import_UNIQUE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_CEIL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_REVERSE_V2(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ADD_N(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_GATHER_ND(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_COS(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='cos',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_WHERE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_RANK(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ELU(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        self.nxgraph.add_node(name,
                              op='elu',
                              x=input_name,
                              datatype=datatype,
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_REVERSE_SEQUENCE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_MATRIX_DIAG(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_QUANTIZE(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        output_shape = input_node['output_shape'][:]
        datatype = tflite_type_map[tensor.Type()]

        self.nxgraph.add_node(name,
                              op='quant',
                              x=input_name,
                              datatype=datatype,
                              format='none',
                              output_shape=output_shape)
        self.nxgraph.add_edge(input_name, name)
        self.tensor_map[tensor_id] = name

        quant_info = tensor.Quantization()
        if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
            isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
            self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
            self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
            self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

        if 'np_tensor' in input_node:
            print(self.calc_not_implemented_message % 
                self.opcode_dict[operator.OpcodeIndex()])

    def import_MATRIX_SET_DIAG(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_ROUND(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_HARD_SWISH(self, operator):
        tensor_id = operator.Outputs(0)
        tensor = self.tflite_graph.Tensors(tensor_id)
        name = tensor.Name().decode('utf-8')
        input_name = self.tensor_map[operator.Inputs(0)]
        input_node = self.nxgraph.nodes[input_name]
        datatype = tflite_type_map[tensor.Type()]
        output_shape = input_node['output_shape']

        if datatype != np.float32:
            self.nxgraph.add_node(name,
                                op='swish',
                                x=input_name,
                                hard=1,
                                beta=1,
                                datatype=datatype,
                                output_shape=output_shape)
            self.nxgraph.add_edge(input_name, name)
            self.tensor_map[tensor_id] = name

            quant_info = tensor.Quantization()
            if quant_info and isinstance(quant_info.ScaleAsNumpy(), np.ndarray) and \
                isinstance(quant_info.ZeroPointAsNumpy(), np.ndarray):
                self.nxgraph.nodes[name]['quant_scale'] = quant_info.ScaleAsNumpy()
                self.nxgraph.nodes[name]['zero_point'] = quant_info.ZeroPointAsNumpy()
                self.nxgraph.nodes[name]['quant_axis'] = quant_info.QuantizedDimension()

            if 'np_tensor' in input_node:
                print(self.calc_not_implemented_message % 
                    self.opcode_dict[operator.OpcodeIndex()])
            return
        
        three_name = name + "_dv_3"
        self.nxgraph.add_node(three_name,
                              op='constant',
                              output_shape=[1],
                              datatype=datatype,
                              np_tensor=np.array([3.0]).astype(datatype))
        add_name = name + '_dv_plus_3'
        self.nxgraph.add_node(add_name,
                              op='add',
                              x=input_name,
                              y=three_name,
                              output_shape=output_shape,
                              datatype=datatype)
        self.nxgraph.add_edge(input_name, add_name)
        self.nxgraph.add_edge(three_name, add_name)

        # ReLU6(x + 3)
        relu_name = name + "_dv_relu6"
        self.nxgraph.add_node(relu_name,
                              op='relu6',
                              x=add_name,
                              output_shape=output_shape,
                              datatype=datatype)
        self.nxgraph.add_edge(add_name, relu_name)

        # ReLU6(x + 3) / 6
        div_name = name + "_dv_div6"
        six_name = name + "_dv_6"
        self.nxgraph.add_node(six_name,
                              op='constant',
                              output_shape=[1],
                              datatype=datatype,
                              np_tensor=np.array([6.0]).astype(datatype))
        self.nxgraph.add_node(div_name,
                              op='div',
                              x=relu_name,
                              y=six_name,
                              output_shape=output_shape,
                              datatype=datatype)
        self.nxgraph.add_edge(relu_name, div_name)
        self.nxgraph.add_edge(six_name, div_name)
        # x * (ReLU6(x + 3) / 6)

        self.nxgraph.add_node(name,
                              op='mul',
                              x=input_name,
                              y=div_name,
                              output_shape=output_shape,
                              datatype=datatype)
        self.nxgraph.add_edge(input_name, name)
        self.nxgraph.add_edge(div_name, name)
        self.tensor_map[tensor_id] = name

    def import_IF(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_WHILE(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_NON_MAX_SUPPRESSION_V4(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_NON_MAX_SUPPRESSION_V5(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SCATTER_ND(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SELECT_V2(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_DENSIFY(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_SEGMENT_SUM(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def import_BATCH_MATMUL(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])
    
    def import_unknown(self, operator):
        print(self.op_not_supported_message % self.opcode_dict[operator.OpcodeIndex()])

    def modify_to_constants(self):
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] == 'constant':
                continue
            if 'np_tensor' not in data:
                continue
            keep_params = ['op', 'datatype', 'np_tensor', 'output_shape',
                'quant_scale', 'zero_point', 'quant_scale', 'format']
            data['op'] = 'constant'
            layer_params = list(data.keys())
            for param in layer_params:
                if param not in keep_params:
                    del data[param]
            in_edges = list(self.nxgraph.in_edges(node_name))
            for edge in in_edges:
                self.nxgraph.remove_edge(edge[0], edge[1])

    def clean_filters(self):
        # Convert from O,H,W,I
        cleaned_filters = []
        for _, data in self.nxgraph.nodes(data=True):
            if data['op'] not in ['conv', 'transpose_conv']:
                continue

            filt_name = data['filter']
            filt_node = self.nxgraph.nodes[data['filter']]
            if filt_node['op'] != 'constant':
                print("WARNING: The filter for node %s is not a \
                    constant, so we cannot guarantee the correct \
                    filter shape. Additional op calculations may \
                    be needed.")
                continue
            if filt_name in cleaned_filters:
                continue

            if data['op'] == 'conv' or data['op'] == 'transpose_conv':
                t_axis = [1, 2, 3, 0]
            new_tensor = filt_node['np_tensor'].copy()
            new_tensor = np.transpose(new_tensor, t_axis)
            filt_node['np_tensor'] = new_tensor
            filt_node['output_shape'] = list(new_tensor.shape)
            if 'quant_axis' in filt_node:
                filt_node['quant_axis'] = t_axis.index(filt_node['quant_axis'])

            cleaned_filters.append(filt_name)

    def prune_graph(self):
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

    def fold_padding(self):
        remove_nodes = []
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] != 'pad':
                continue
            if len(self.nxgraph.out_edges(node_name)) > 1:
                continue
            out_name = list(self.nxgraph.out_edges(node_name))[0][1]
            out_node = self.nxgraph.nodes[out_name]
            if out_node['op'] not in ['conv']:
                continue
            for i in range(len(data['head'])):
                out_node['head'][i] += data['head'][i]
                out_node['tail'][i] += data['tail'][i]
            out_node['input'] = data['input']
            self.nxgraph.add_edge(data['input'], out_name)
            remove_nodes.append(node_name)
        self.nxgraph.remove_nodes_from(remove_nodes)

    def find_subgraph(self):
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
        if not (inputs_in_graph and outputs_in_graph):
            print("WARNING: Cannot find all provided subgraph input \
                and output names in the graph, using full graph.")
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
        if self.trim_output_names:
            self.output_names = self.trim_output_names[:]

    def expand_activations(self):
        add_nodes = []
        rename_map = {}
        for node_name, data in self.nxgraph.nodes(data=True):
            if data['op'] in ['conv']:
                continue
            if 'activation' not in data:
                continue
            if data['activation'] == 'linear':
                continue
            rename_map[node_name] = node_name + '_preact_dv'
            add_nodes.append([node_name, data['activation'],
                             data['datatype'], data['output_shape'][:], data])
            data['activation'] = 'linear'

        nx.relabel_nodes(self.nxgraph, rename_map, copy=False)
        for node in add_nodes:
            in_name = node[0] + '_preact_dv'
            in_node = self.nxgraph.nodes[in_name]
            self.nxgraph.add_node(node[0],
                                  op=node[1],
                                  x=node[0] + '_preact_dv',
                                  datatype=node[2],
                                  output_shape=node[3])
            if 'quant_scale' in in_node:
                self.nxgraph.nodes[node[0]]['quant_scale'] = in_node['quant_scale']
                self.nxgraph.nodes[node[0]]['zero_point'] = in_node['zero_point']
                self.nxgraph.nodes[node[0]]['quant_axis'] = in_node['quant_axis']

            out_edges = list(self.nxgraph.out_edges(in_name))
            for edge in out_edges:
                self.nxgraph.remove_edge(edge[0], edge[1])
                self.nxgraph.add_edge(node[0], edge[1])
            self.nxgraph.add_edge(node[0] + '_preact_dv', node[0])
