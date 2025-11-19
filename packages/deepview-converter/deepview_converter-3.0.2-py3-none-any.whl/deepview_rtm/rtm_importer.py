# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import networkx as nx
import numpy as np
import deepview.rtmx as rtmx


class RTMImporter:
    def __init__(self, filename):
        self.op_dict = {1: 'external',
                        2: 'constant',
                        3: 'variable',
                        10: 'pad',
                        11: 'concat',
                        12: 'slice',
                        13: 'transpose',
                        20: 'add',
                        21: 'sub',
                        22: 'mul',
                        23: 'div',
                        30: 'abs',
                        31: 'sqrt',
                        32: 'rsqrt',
                        40: 'sigmoid',
                        41: 'tanh',
                        42: 'relu',
                        43: 'relu6',
                        44: 'softmax',
                        50: 'matmul',
                        60: 'conv',
                        61: 'pool',
                        70: 'sum_reduce',
                        71: 'min_reduce',
                        72: 'max_reduce',
                        73: 'mean_reduce',
                        74: 'prod_reduce',
                        100: 'cudnn_gru',
                        101: 'reshape',
                        102: 'batch_normalization',
                        110: 'image_standardize',
                        120: 'svm',
                        121: 'svm_update_kernel',
                        122: 'svm_decision_stats',
                        123: 'svm_soft_probability',
                        124: 'final'}
        self.layer_names = {}
        self.nx_graph = nx.DiGraph()
        with open(filename, 'rb') as f:
            buf = f.read()
        self.model = rtmx.Model.GetRootAsModel(buf, 0)

    def run(self):
        self.create_nodes()
        return self.nx_graph

    def create_nodes(self):
        layer_length = self.model.LayersLength()
        for i in range(layer_length):
            layer = self.model.Layers(i)
            self.layer_names[i] = layer.Name().decode('utf-8')
            node_op = self.op_dict[layer.Type()]
            func = getattr(self, "import_" + node_op)
            func(layer)

    def import_external(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())

        self.nx_graph.add_node(layer_name,
                               op='external',
                               shape=output_shape,
                               output_shape=output_shape)

    def import_constant(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        data = layer.Params(0).DataF32AsNumpy()

        self.nx_graph.add_node(layer_name,
                               op='constant',
                               shape=output_shape,
                               np_tensor=data,
                               output_shape=output_shape,
                               dtype=np.float32)

    def import_variable(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        data = layer.Params(0).DataF32AsNumpy()

        self.nx_graph.add_node(layer_name,
                               op='variable',
                               shape=output_shape,
                               np_tensor=data,
                               output_shape=output_shape,
                               dtype=np.float32)

    def import_pad(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        head = list(layer.Params(0).ShapeAsNumpy())
        tail = list(layer.Params(1).ShapeAsNumpy())
        value = layer.Params(2).DataF32(0)

        self.nx_graph.add_node(layer_name,
                               op='pad',
                               input=input_name,
                               head=head,
                               tail=tail,
                               value=value,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

        if layer.ParamsLength() == 4:
            self.nx_graph.nodes[layer_name]['fusible'] = 1

    def import_concat(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        inputs = []
        for i in range(layer.InputsLength()):
            inputs.append(self.layer_names[layer.Inputs(i)])
        axis = layer.Params(0).DataI16()

        self.nx_graph.add_node(layer_name,
                               op='concat',
                               values=inputs,
                               axis=axis,
                               output_shape=output_shape)
        for input_name in inputs:
            self.nx_graph.add_edge(input_name, layer_name)

    def import_slice(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(0).ShapeAsNumpy())
        head = list(layer.Params(1).ShapeAsNumpy())
        tail = list(layer.Params(2).ShapeAsNumpy())

        self.nx_graph.add_node(layer_name,
                               op='slice',
                               input=input_name,
                               axes=axes,
                               begin=head,
                               end=tail,
                               output_shape=output_shape)

    def import_transpose(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(0).ShapeAsNumpy())

        self.nx_graph.add_node(layer_name,
                               op='transpose',
                               input=input_name,
                               axes=axes,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_add(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        x_name = self.layer_names[layer.Inputs(0)]
        y_name = self.layer_names[layer.Inputs(1)]

        self.nx_graph.add_node(layer_name,
                               op='add',
                               x=x_name,
                               y=y_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(x_name, layer_name)
        self.nx_graph.add_edge(y_name, layer_name)

    def import_sub(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        x_name = self.layer_names[layer.Inputs(0)]
        y_name = self.layer_names[layer.Inputs(1)]

        self.nx_graph.add_node(layer_name,
                               op='sub',
                               x=x_name,
                               y=y_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(x_name, layer_name)
        self.nx_graph.add_edge(y_name, layer_name)

    def import_mul(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        x_name = self.layer_names[layer.Inputs(0)]
        y_name = self.layer_names[layer.Inputs(1)]

        self.nx_graph.add_node(layer_name,
                               op='mul',
                               x=x_name,
                               y=y_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(x_name, layer_name)
        self.nx_graph.add_edge(y_name, layer_name)

    def import_div(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        x_name = self.layer_names[layer.Inputs(0)]
        y_name = self.layer_names[layer.Inputs(1)]

        self.nx_graph.add_node(layer_name,
                               op='div',
                               x=x_name,
                               y=y_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(x_name, layer_name)
        self.nx_graph.add_edge(y_name, layer_name)

    def import_abs(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='abs',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_sqrt(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='sqrt',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_rsqrt(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        epsilon = layer.Params(0).DataF32(0)

        self.nx_graph.add_node(layer_name,
                               op='rsqrt',
                               x=input_name,
                               epsilon=epsilon,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_sigmoid(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='sigmoid',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_tanh(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='tanh',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_relu(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='relu',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_relu6(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='relu6',
                               x=input_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_softmax(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(0).ShapeAsNumpy())

        self.nx_graph.add_node(layer_name,
                               op='softmax',
                               x=input_name,
                               axes=axes,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_matmul(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_a = self.layer_names[layer.Inputs(0)]
        input_b = self.layer_names[layer.Inputs(1)]

        transpose_a = 'False'
        transpose_b = 'False'

        for i in range(layer.ParamsLength()):
            param = layer.Params(i)
            param_name = param.Name().decode('utf-8')
            if param_name == 'transpose_a':
                transpose_a = 'True'
            if param_name == 'transpose_b':
                transpose_b = 'True'

        self.nx_graph.add_node(layer_name,
                               A=input_a,
                               B=input_b,
                               transpose_a=transpose_a,
                               transpose_b=transpose_b,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_a, layer_name)
        self.nx_graph.add_edge(input_b, layer_name)

    def import_conv(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        filter_name = self.layer_names[layer.Inputs(1)]
        if layer.InputsLength() == 3:
            bias_name = self.layer_names[layer.Inputs(2)]
        else:
            bias_name = None

        activation = None
        groups = None
        strides = None
        tail = None
        head = None
        alt_input = None

        self.nx_graph.add_node(layer_name,
                               op='conv',
                               input=input_name,
                               filter=filter_name,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)
        self.nx_graph.add_edge(filter_name, layer_name)

        for i in range(layer.ParamsLength()):
            param = layer.Params(i)
            param_name = param.Name().decode('utf-8')
            if param_name == 'activation':
                activation = param.DataStr(0).decode('utf-8')
                self.nx_graph.nodes[layer_name]['activation'] = activation
            elif param_name == 'groups':
                groups = param.DataI16(0)
                self.nx_graph.nodes[layer_name]['groups'] = groups
            elif param_name == 'strides':
                strides = list(param.ShapeAsNumpy())[1:3]
                self.nx_graph.nodes[layer_name]['stride'] = strides
            elif param_name == 'tail':
                tail = list(param.ShapeAsNumpy())
                self.nx_graph.nodes[layer_name]['tail'] = tail
            elif param_name == 'head':
                head = list(param.ShapeAsNumpy())
                self.nx_graph.nodes[layer_name]['head'] = head
            elif param_name == 'alt_input':
                alt_input = self.layer_names[param.DataI16(0)]
                self.nx_graph.nodes[layer_name]['alt_input'] = alt_input

        if bias_name:
            self.nx_graph.nodes[layer_name]['bias'] = bias_name
            self.nx_graph.add_edge(bias_name, layer_name)

    def import_pool(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        size = None
        strides = None
        pool_type = None
        tail = None
        head = None
        alt_input = None
        for i in range(layer.ParamsLength()):
            param = layer.Params(i)
            param_name = param.Name().decode('utf-8')
            if param_name == 'ksize':
                size = list(param.ShapeAsNumpy())
            elif param_name == 'pooling':
                pool_type = param.DataStr(0).decode('utf-8')
            elif param_name == 'strides':
                strides = list(param.ShapeAsNumpy())
            elif param_name == 'tail':
                tail = param.ShapeAsNumpy()
            elif param_name == 'head':
                head = param.ShapeAsNumpy()
            elif param_name == 'alt_input':
                alt_input = self.layer_names[param.DataI16(0)]

        self.nx_graph.add_node(layer_name,
                               input=input_name,
                               size=size,
                               stride=strides,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

        if pool_type == 'MAXIMUM':
            self.nx_graph.nodes[layer_name]['op'] = 'max_pool'
        else:
            self.nx_graph.nodes[layer_name]['op'] = 'avg_pool'
        if not tail.size == 0:
            self.nx_graph.nodes[layer_name]['tail'] = tail
        if not head.size == 0:
            self.nx_graph.nodes[layer_name]['head'] = head
        if alt_input:
            self.nx_graph.nodes[layer_name]['alt_input'] = alt_input

    def import_sum_reduce(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(1).ShapeAsNumpy())
        keep_dims = layer.Params(0).DataI16(0)

        self.nx_graph.add_node(layer_name,
                               op='sum_reduce',
                               input=input_name,
                               axes=axes,
                               keep_dims=keep_dims,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_min_reduce(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(1).ShapeAsNumpy())
        keep_dims = layer.Params(0).DataI16(0)

        self.nx_graph.add_node(layer_name,
                               op='min_reduce',
                               input=input_name,
                               axes=axes,
                               keep_dims=keep_dims,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_max_reduce(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(1).ShapeAsNumpy())
        keep_dims = layer.Params(0).DataI16(0)

        self.nx_graph.add_node(layer_name,
                               op='max_reduce',
                               input=input_name,
                               axes=axes,
                               keep_dims=keep_dims,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_mean_reduce(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(1).ShapeAsNumpy())
        keep_dims = layer.Params(0).DataI16(0)

        self.nx_graph.add_node(layer_name,
                               op='mean_reduce',
                               input=input_name,
                               axes=axes,
                               keep_dims=keep_dims,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_prod_reduce(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        axes = list(layer.Params(1).ShapeAsNumpy())
        keep_dims = layer.Params(0).DataI16(0)

        self.nx_graph.add_node(layer_name,
                               op='prod_reduce',
                               input=input_name,
                               axes=axes,
                               keep_dims=keep_dims,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_cudnn_gru(self, layer):
        # TODO: Add support for this function
        pass

    def import_reshape(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]

        self.nx_graph.add_node(layer_name,
                               op='reshape',
                               input=input_name,
                               shape=output_shape,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)

    def import_batch_normalization(self, layer):
        layer_name = layer.Name().decode('utf-8')
        output_shape = list(layer.ShapeAsNumpy())
        input_name = self.layer_names[layer.Inputs(0)]
        mean = self.layer_names[layer.Inputs(1)]
        variance = self.layer_names[layer.Inputs(2)]
        offset = self.layer_names[layer.Inputs(3)]
        scale = self.layer_names[layer.Inputs(4)]
        epsilon = self.layer_names[layer.Inputs(5)]

        self.nx_graph.add_node(layer_name,
                               op='batch_normalization',
                               input=input_name,
                               mean=mean,
                               variance=variance,
                               offset=offset,
                               scale=scale,
                               epsilon=epsilon,
                               output_shape=output_shape)
        self.nx_graph.add_edge(input_name, layer_name)
        self.nx_graph.add_edge(mean, layer_name)
        self.nx_graph.add_edge(variance, layer_name)
        self.nx_graph.add_edge(offset, layer_name)
        self.nx_graph.add_edge(scale, layer_name)
        self.nx_graph.add_edge(epsilon, layer_name)

    def import_image_standardize(self, layer):
        # TODO: Add support for this function
        pass

    def import_svm(self, layer):
        # TODO: Add support for this function
        pass

    def import_svm_update_kernel(self, layer):
        # TODO: Add support for this function
        pass

    def import_svm_decision_stats(self, layer):
        # TODO: Add support for this function
        pass

    def import_svm_soft_probability(self, layer):
        # TODO: Add support for this function
        pass

    def import_final(self, layer):
        # TODO: Add support for this function
        pass
