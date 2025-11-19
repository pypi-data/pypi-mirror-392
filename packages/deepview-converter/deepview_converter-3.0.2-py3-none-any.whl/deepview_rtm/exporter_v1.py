# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from __future__ import division

import os
import sys
from collections.abc import Sequence

import networkx as nx
import numpy as np
import deepview.rtmx as rtmx

from deepview.flatbuffers import Builder
from deepview.flatbuffers import number_types as nt
from six import string_types
from itertools import count


type_flags = {
    np.dtype('int8'): nt.Int8Flags,
    np.dtype('uint8'): nt.Uint8Flags,
    np.dtype('int16'): nt.Int16Flags,
    np.dtype('uint16'): nt.Uint16Flags,
    np.dtype('int32'): nt.Int32Flags,
    np.dtype('uint32'): nt.Uint32Flags,
    np.dtype('int64'): nt.Int64Flags,
    np.dtype('uint64'): nt.Uint64Flags,
    np.dtype('float32'): nt.Float32Flags,
    np.dtype('float64'): nt.Float64Flags,
}

dtype_flags = {
    np.dtype('int8'): rtmx.Datatype.I8,
    np.dtype('uint8'): rtmx.Datatype.U8,
    np.dtype('int16'): rtmx.Datatype.I16,
    np.dtype('uint16'): rtmx.Datatype.U16,
    np.dtype('int32'): rtmx.Datatype.I32,
    np.dtype('uint32'): rtmx.Datatype.U32,
    np.dtype('int64'): rtmx.Datatype.I64,
    np.dtype('uint64'): rtmx.Datatype.U64,
    np.dtype('float32'): rtmx.Datatype.F32,
    np.dtype('float64'): rtmx.Datatype.F64,
}


class BetterBuilder(Builder):
    '''
    Python Flatbuffers do not currently support file identifiers so this
    sub-class adds this functionality based on the following pull request.

    https://github.com/google/flatbuffers/pull/4853
    '''

    def FinishWithFileIdentifierx(self, root_table, fid):
        from deepview.flatbuffers import number_types as N
        from deepview.flatbuffers import encode

        FILEIDENTIFIER_LENGTH = 4

        if (fid is None or len(fid) != FILEIDENTIFIER_LENGTH):
            raise ValueError('fid must be 4 chars')
        if sys.version_info[0] < 3:
            fid = [ord(x) for x in fid]
        else:
            fid = fid.encode()
        flags = N.Uint8Flags
        prep_size = N.Uint8Flags.bytewidth*len(fid)
        self.Prep(self.minalign, prep_size+len(fid))
        for i in range(len(fid)-1, -1, -1):
            self.head = self.head - flags.bytewidth
            encode.Write(flags.packer_type, self.Bytes, self.Head(), fid[i])
        return self.Finish(root_table)


class DeepViewExporter:
    def __init__(self, graph, name, mem_map=True, opt_map=True, save_map=None,
                 save_layers=None, copy_layers=None, svm=None, ext_constants=None,
                 labels=None, input_names=None, output_names=None, user_ops=[],
                 normalization="none", metadata=None):
        if save_layers is None:
            save_layers = []
        if copy_layers is None:
            copy_layers = []
        self.graph = graph
        self.name = name
        self.mem_map = mem_map
        self.opt_map = opt_map
        self.save_map = save_map
        self.save_layers = save_layers
        self.copy_layers = copy_layers
        self.svm = svm
        self.ext_constants = ext_constants
        self.labels = labels
        self.input_names = input_names
        self.output_names = output_names
        self.normalization = normalization
        self.alternate_input_error_message = "The alternate input has a value greater than 32768"
        if metadata is None:
            self.metadata = []
        else:
            self.metadata = metadata

        self.user_ops = []
        for user in user_ops:
            if hasattr(user, 'DeepViewExporter'):
                user_exporter = user.DeepViewExporter(self)
                self.user_ops.append(user_exporter)

    def add_copy(self):
        for copy in self.copy_layers:
            if copy[0] not in self.graph.dz_nx_graph.nodes:
                print(
                    "Unable to add copy for %s, it does not exist in the graph" % copy[0])
                continue
            if copy[1] not in self.graph.dz_nx_graph.nodes:
                print(
                    "Unable to add copy for %s, it does not exist in the graph" % copy[1])
                continue

            copy_node1 = self.graph.dz_nx_graph.nodes[copy[0]]
            copy_node2 = self.graph.dz_nx_graph.nodes[copy[1]]
            if copy_node2['op'] not in ['constant', 'external']:
                print(
                    "Unable to add copy for %s, target is not a constant or external" % copy[1])
                continue
            if copy_node1['output_shape'] != copy_node2['output_shape']:
                print("Unable to add copy for %s, shape mistmatch" % copy[0])
                continue

            copy_node2['op'] = 'variable'
            self.graph.tensor_dict[copy[1]] = np.asarray(
                np.zeros(copy_node2['output_shape'])).astype(np.float32)
            if copy[1] not in self.save_layers:
                self.save_layers.append(copy[1])
            self.graph.dz_nx_graph.add_node('dv_' + copy[0] + '_copy',
                                            op='copy',
                                            input=copy[0],
                                            target=copy[1],
                                            output_shape=copy_node1['output_shape'])
            self.graph.dz_nx_graph.add_edge(copy[0], 'dv_' + copy[0] + '_copy')

    def export_tensor(self,
                      builder,          # Type: fb.Builder
                      name,             # Type: str
                      shape=None,       # Type: Optional[Tuple[int, ...]]
                      data=None         # Type: Optional[np.ndarray]
                      ):
        # Type: (...) -> int
        '''
        Creates a RTMx tensor table with name and shape, shape can be None as long
        as data is a valid Numpy NDArray in which case its shape will be used.
        '''
        tensor_name = builder.CreateString(name)
        tensor_shape = None
        tensor_data = None
        tensor_data_type = None

        if shape is not None:
            builder.StartVector(4, len(shape), 4)
            for i in reversed(shape):
                builder.PrependInt32(i)
            tensor_shape = builder.EndVector(len(shape))

        if data is not None:
            if isinstance(data, string_types):
                builder.StartVector(4, 1, 4)
                builder.PrependInt32(1)
                tensor_shape = builder.EndVector(1)
                offset = builder.CreateString(data)
                tensor_data_type = string_types
                builder.StartVector(4, 1, 4)
                builder.PrependUOffsetTRelative(offset)
                tensor_data = builder.EndVector(1)
            elif isinstance(data, (int, float)):
                builder.StartVector(4, 1, 4)
                builder.PrependInt32(1)
                tensor_shape = builder.EndVector(1)
                if isinstance(data, int):
                    builder.StartVector(2, 1, 2)
                    tensor_data_type = nt.Int16Flags
                    builder.PrependInt16(data)
                elif isinstance(data, float):
                    builder.StartVector(4, 1, 4)
                    tensor_data_type = nt.Float32Flags
                    builder.PrependFloat32(data)
                else:
                    raise ValueError('Unsupported data type:', type(data))
                tensor_data = builder.EndVector(1)
            elif isinstance(data, np.ndarray):
                if data.dtype not in type_flags:
                    raise ValueError('Numpy NDArray has unsupported type:',
                                     data.dtype)
                tensor_data_type = type_flags[data.dtype]

                if shape is None:
                    builder.StartVector(4, len(data.shape), 4)
                    for i in reversed(data.shape):
                        builder.PrependInt32(i)
                    tensor_shape = builder.EndVector(len(data.shape))

                # Based on flatbuffers pull request
                # https://github.com/google/flatbuffers/pull/4829
                # FIXME: their implementation does an endian conversion but it
                #        causes our tests to fail so it was removed.
                data = data.flatten()
                builder.StartVector(data.itemsize,
                                    data.size,
                                    data.dtype.alignment)
                length = nt.UOffsetTFlags.py_type(data.itemsize * data.size)
                builder.head = nt.UOffsetTFlags.py_type(
                    builder.Head() - length)
                builder.Bytes[builder.Head():builder.Head() + length] \
                    = data.tobytes(order='C')
                tensor_data = builder.EndVector(data.size)
            elif isinstance(data, Sequence):
                builder.StartVector(4, 1, 4)
                builder.PrependInt32(len(data))
                tensor_shape = builder.EndVector(1)
                if all(isinstance(x, string_types) for x in data):
                    tensor_data_type = string_types
                    offsets = [builder.CreateString(x) for x in data]
                    builder.StartVector(4, len(offsets), 4)
                    for x in reversed(offsets):
                        builder.PrependUOffsetTRelative(x)
                    tensor_data = builder.EndVector(len(offsets))
                elif all(isinstance(x, int) for x in data):
                    tensor_data_type = nt.Int16Flags
                    builder.StartVector(2, len(data), 2)
                    for x in reversed(data):
                        builder.PrependInt16(x)
                    tensor_data = builder.EndVector(len(data))
                elif all(isinstance(x, float) for x in data):
                    tensor_data_type = nt.Float32Flags
                    builder.StartVector(4, len(data), 4)
                    for x in reversed(data):
                        builder.PrependFloat32(x)
                    tensor_data = builder.EndVector(len(data))
                else:
                    raise ValueError('Sequence has inconsistent or unsupported '
                                     'data:', type(data))
            else:
                raise ValueError('Unsupported data type:', type(data))

        rtmx.TensorStart(builder)
        rtmx.TensorAddName(builder, tensor_name)

        if tensor_shape is not None:
            rtmx.TensorAddShape(builder, tensor_shape)

        if tensor_data_type == string_types:
            rtmx.TensorAddDataStr(builder, tensor_data)
        elif tensor_data_type == nt.Uint8Flags:
            rtmx.TensorAddDataRaw(builder, tensor_data)
        elif tensor_data_type == nt.Int8Flags:
            rtmx.TensorAddDataI8(builder, tensor_data)
        elif tensor_data_type == nt.Int16Flags:
            rtmx.TensorAddDataI16(builder, tensor_data)
        elif tensor_data_type == nt.Int32Flags:
            rtmx.TensorAddDataI32(builder, tensor_data)
        elif tensor_data_type == nt.Float32Flags:
            rtmx.TensorAddDataF32(builder, tensor_data)
        elif tensor_data is not None:
            raise ValueError('Tensor data is unsupported:', type(data))

        return rtmx.TensorEnd(builder)

    def generate_layer(self,
                       builder,
                       node,
                       op,
                       name,
                       shape,
                       inputs=None,
                       params=None
                       ):
        if 'quant_scale' in node and 'zero_point' in node:
            rtmx.LayerStartScaleVector(builder, len(node['quant_scale']))
            for i in reversed(node['quant_scale']):
                builder.PrependFloat32(i)
            scale_vector = builder.EndVector(len(node['quant_scale']))

            rtmx.LayerStartZeroVector(builder, len(node['zero_point']))
            for i in reversed(node['zero_point'].astype(np.int32)):
                builder.PrependInt32(i)
            zero_vector = builder.EndVector(len(node['zero_point']))

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, op)
        rtmx.LayerAddName(builder, name)
        rtmx.LayerAddShape(builder, shape)
        if inputs:
            rtmx.LayerAddInputs(builder, inputs)
        if params:
            rtmx.LayerAddParams(builder, params)
        if 'block' in node:
            rtmx.LayerAddBlock(builder, node['block'])
        if 'datatype' in node:
            rtmx.LayerAddDatatype(builder, dtype_flags[node['datatype']])
        if 'quant_scale' in node and 'zero_point' in node:
            rtmx.LayerAddScale(builder, scale_vector)
            rtmx.LayerAddZero(builder, zero_vector)
        if 'quant_axis' in node:
            rtmx.LayerAddAxis(builder, node['quant_axis'])
        return rtmx.LayerEnd(builder)
        

    def export_external(self,
                        builder,        # Type: fb.Builder
                        graph,          # Type: DeepViewExecuter
                        layers,         # Type: Map
                        name,           # Type: str
                        node,           # Type: Map
                        alt_name=None   # Type: str
                        ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        shape = self.export_tensor(builder, 'shape', node['output_shape'])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(shape)
        layer_params = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.input,
                                   layer_name, layer_shape, 
                                   params=layer_params)

    def export_abs(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.abs,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_add(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['y']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.add,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_add_n(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        input_names = node['values']
        node_inputs = [layers[val] for val in input_names]

        rtmx.LayerStartInputsVector(builder, len(node_inputs))
        for index in reversed(node_inputs):
            builder.PrependUint32(index)
        layer_inputs = builder.EndVector(len(node_inputs))

        return self.generate_layer(builder, node, rtmx.Op.none,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_avg_pool(self,
                        builder,            # Type: fb.Builder
                        graph,              # Type: DeepViewExecuter
                        layers,             # Type: Map
                        name,               # Type: str
                        node,               # Type: Map
                        alt_name=None       # Type: str
                        ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        if len(node['size']) == len(node['output_shape']):
            size = self.export_tensor(builder, 'ksize', node['size'])
        else:
            size = self.export_tensor(builder, 'ksize', [1] + node['size'] + [1])
        if len(node['stride']) == len(node['output_shape']):
            stride = self.export_tensor(builder, 'strides', node['stride'])
        else:
            stride = self.export_tensor(builder, 'strides', [1] + node['stride'] + [1])
        pool_type = self.export_tensor(builder, 'pooling', data="AVERAGE")

        if 'head' in node and 'tail' in node:
            head = self.export_tensor(builder, 'head', shape=node['head'])
            tail = self.export_tensor(builder, 'tail', shape=node['tail'])
            rtmx.LayerStartParamsVector(builder, 5)
            builder.PrependUOffsetTRelative(head)
            builder.PrependUOffsetTRelative(tail)
        else:
            rtmx.LayerStartParamsVector(builder, 3)
        builder.PrependUOffsetTRelative(size)
        builder.PrependUOffsetTRelative(stride)
        builder.PrependUOffsetTRelative(pool_type)
        if 'head' in node and 'tail' in node:
            layer_params = builder.EndVector(5)
        else:
            layer_params = builder.EndVector(3)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.pool2d,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_batch_normalization(self,
                                   builder,            # Type: fb.Builder
                                   graph,              # Type: DeepViewExecuter
                                   layers,             # Type: Map
                                   name,               # Type: str
                                   node,               # Type: Map
                                   alt_name=None       # Type: str
                                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['input']]
        mean = layers[node['mean']]
        variance = layers[node['variance']]
        offset = layers[node['offset']]
        scale = layers[node['scale']]
        epsilon = layers[node['epsilon']]

        rtmx.LayerStartInputsVector(builder, 6)
        builder.PrependUint32(epsilon)
        builder.PrependUint32(scale)
        builder.PrependUint32(offset)
        builder.PrependUint32(variance)
        builder.PrependUint32(mean)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(6)

        return self.generate_layer(builder, node, rtmx.Op.batchnorm,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_concat(self,
                      builder,            # Type: fb.Builder
                      graph,              # Type: DeepViewExecuter
                      layers,             # Type: Map
                      name,               # Type: str
                      node,               # Type: Map
                      alt_name=None       # Type: str
                      ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        axis = self.export_tensor(builder, 'axis', data=int(node['axis']))

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(axis)
        layer_params = builder.EndVector(1)

        input_names = node['values']
        node_inputs = [layers[val] for val in input_names]

        rtmx.LayerStartInputsVector(builder, len(node_inputs))
        for index in reversed(node_inputs):
            builder.PrependUint32(index)
        layer_inputs = builder.EndVector(len(node_inputs))

        return self.generate_layer(builder, node, rtmx.Op.concat,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_constant(self,
                        builder,        # Type: fb.Builder
                        graph,          # Type: DeepViewExecuter
                        layers,         # Type: Map
                        name,           # Type: str
                        node            # Type: Map
                        ):
        # Type: (...) -> int
        layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))
        if graph.tensor_dict[name].dtype == np.dtype('float64'):
            graph.tensor_dict[name] = graph.tensor_dict[name].astype(
                np.float32)
            # Since many models use 64-bit float weights we should figure out a better way to log the precision warnings.
            # print("[WARNING] Loss of precision for node %s due to reduction from float64 to float32" % name)
        if graph.tensor_dict[name].dtype == np.dtype('int64'):
            graph.tensor_dict[name] = graph.tensor_dict[name].astype(np.int32)
        data = self.export_tensor(builder, 'data',
                                  data=graph.tensor_dict[name])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(data)
        layer_params = builder.EndVector(1)

        if 'quant_scale' in node and 'zero_point' in node:
            rtmx.LayerStartScaleVector(builder, len(node['quant_scale']))
            for i in reversed(node['quant_scale']):
                builder.PrependFloat32(i)
            scale_vector = builder.EndVector(len(node['quant_scale']))

            rtmx.LayerStartZeroVector(builder, len(node['zero_point']))
            for i in reversed(node['zero_point'].astype(np.int32)):
                builder.PrependInt32(i)
            zero_vector = builder.EndVector(len(node['zero_point']))

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.constant)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddDatatype(
            builder, dtype_flags[graph.tensor_dict[name].dtype])
        rtmx.LayerAddParams(builder, layer_params)
        if 'panel' in node and node['panel'] != 0:
            rtmx.LayerAddPanelSize(builder, node['panel'])
        if 'quant_scale' in node and 'zero_point' in node:
            rtmx.LayerAddScale(builder, scale_vector)
            rtmx.LayerAddZero(builder, zero_vector)
        if 'quant_axis' in node:
            rtmx.LayerAddAxis(builder, node['quant_axis'])
        return rtmx.LayerEnd(builder)

    def export_conv(self,
                    builder,            # Type: fb.Builder
                    graph,              # Type: DeepViewExecuter
                    layers,             # Type: Map
                    name,               # Type: str
                    node,               # Type: Map
                    alt_name=None       # Type: str
                    ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))
        if len(node['dilation']) == len(node['output_shape']):
            dilation = self.export_tensor(builder, 'dilations', node['dilation'])
        else:
            dilation_shape = [1, int(node['dilation'][0]), int(node['dilation'][1]), 1]
            dilation = self.export_tensor(builder, 'dilations', dilation_shape)
        if len(node['stride']) == len(node['output_shape']):
            stride = self.export_tensor(builder, 'strides', node['stride'])
        else:
            stride_shape = [1, int(node['stride'][0]), int(node['stride'][1]), 1]
            stride = self.export_tensor(builder, 'strides', stride_shape)
        groups = self.export_tensor(builder, 'groups', data=[node['groups']])
        if 'activation' in node:
            activation = self.export_tensor(
                builder, 'activation', data=node['activation'])
        else:
            activation = self.export_tensor(
                builder, 'activation', data='linear')

        if 'head' in node and 'tail' in node:
            if len(node['head']) == len(node['output_shape']):
                head = self.export_tensor(builder, 'head', shape=node['head'])
            else:
                new_head = [0, int(node['head'][0]), int(node['head'][1]), 0]
                head = self.export_tensor(builder, 'head', new_head)
            if len(node['tail']) == len(node['output_shape']):
                tail = self.export_tensor(builder, 'tail', shape=node['tail'])
            else:
                new_tail = [0, int(node['tail'][0]), int(node['tail'][1]), 0]
                tail = self.export_tensor(builder, 'tail', new_tail)
            rtmx.LayerStartParamsVector(builder, 6)
            builder.PrependUOffsetTRelative(head)
            builder.PrependUOffsetTRelative(tail)
        else:
            rtmx.LayerStartParamsVector(builder, 4)
        builder.PrependUOffsetTRelative(stride)
        builder.PrependUOffsetTRelative(dilation)
        builder.PrependUOffsetTRelative(groups)
        builder.PrependUOffsetTRelative(activation)
        if 'head' in node and 'tail' in node:
            layer_params = builder.EndVector(6)
        else:
            layer_params = builder.EndVector(4)

        x = layers[node['input']]
        k = layers[node['filter']]

        try:
            b = layers[node['bias']]
            rtmx.LayerStartInputsVector(builder, 3)
            builder.PrependUint32(b)
            builder.PrependUint32(k)
            builder.PrependUint32(x)
            layer_inputs = builder.EndVector(3)
        except KeyError:
            rtmx.LayerStartInputsVector(builder, 2)
            builder.PrependUint32(k)
            builder.PrependUint32(x)
            layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.conv2d,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_copy(self,
                    builder,            # Type: fb.Builder
                    graph,              # Type: DeepViewExecuter
                    layers,             # Type: Map
                    name,               # Type: str
                    node,               # Type: Map
                    alt_name=None       # Type: str
                    ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['input']]
        t = layers[node['target']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(x)
        builder.PrependUint32(t)
        layer_inputs = builder.EndVector(2)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.copy)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddInputs(builder, layer_inputs)
        if 'block' in node:
            rtmx.LayerAddBlock(builder, node['block'])
        return rtmx.LayerEnd(builder)

    def export_cos(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.none,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_cudnn_gru(self,
                         builder,            # Type: fb.Builder
                         graph,              # Type: DeepViewExecuter
                         layers,             # Type: Map
                         name,               # Type: str
                         node,               # Type: Map
                         alt_name=None       # Type: str
                         ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['input']]
        h = layers[node['h']]
        w_ir = layers[node['w_ir']]
        b_ir = layers[node['b_ir']]
        w_h = layers[node['w_h']]
        b_wh = layers[node['b_wh']]
        r_h = layers[node['r_h']]
        b_rh = layers[node['b_rh']]

        rtmx.LayerStartInputsVector(builder, 8)
        builder.PrependUint32(b_rh)
        builder.PrependUint32(r_h)
        builder.PrependUint32(b_wh)
        builder.PrependUint32(w_h)
        builder.PrependUint32(b_ir)
        builder.PrependUint32(w_ir)
        builder.PrependUint32(h)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(8)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.gru)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddInputs(builder, layer_inputs)
        if 'block' in node:
            rtmx.LayerAddBlock(builder, node['block'])
        return rtmx.LayerEnd(builder)

    def export_dense(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        if 'activation' in node:
            activation = self.export_tensor(
                builder, 'activation', data=node['activation'])
        else:
            activation = self.export_tensor(
                builder, 'activation', data='linear')

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(activation)
        layer_params = builder.EndVector(1)

        a = layers[node['A']]
        b = layers[node['B']]
        c = layers[node['bias']]

        rtmx.LayerStartInputsVector(builder, 3)
        builder.PrependUint32(c)
        builder.PrependUint32(b)
        builder.PrependUint32(a)
        layer_inputs = builder.EndVector(3)

        return self.generate_layer(builder, node, rtmx.Op.dense,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_dequant(self,
                       builder,            # Type: fb.Builder
                       graph,              # Type: DeepViewExecuter
                       layers,             # Type: Map
                       name,               # Type: str
                       node,               # Type: Map
                       alt_name=None       # Type: str
                       ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.dequant,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_div(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['y']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.divide,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_elu(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.none,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_exp(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.exp,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_log(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.log,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_leaky_relu(self,
                          builder,            # Type: fb.Builder
                          graph,              # Type: DeepViewExecuter
                          layers,             # Type: Map
                          name,               # Type: str
                          node,               # Type: Map
                          alt_name=None       # Type: str
                          ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        alpha = self.export_tensor(builder, 'alpha', data=node['alpha'])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(alpha)
        layer_params = builder.EndVector(1)

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.leaky_relu,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_linear(self,
                      builder,            # Type: fb.Builder
                      graph,              # Type: DeepViewExecuter
                      layers,             # Type: Map
                      name,               # Type: str
                      node,               # Type: Map
                      alt_name=None       # Type: str
                      ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        if 'activation' in node:
            activation = self.export_tensor(
                builder, 'activation', data=node['activation'])
        else:
            activation = self.export_tensor(
                builder, 'activation', data='linear')

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(activation)
        layer_params = builder.EndVector(1)

        a = layers[node['A']]
        b = layers[node['B']]
        c = layers[node['bias']]

        rtmx.LayerStartInputsVector(builder, 3)
        builder.PrependUint32(c)
        builder.PrependUint32(b)
        builder.PrependUint32(a)
        layer_inputs = builder.EndVector(3)

        return self.generate_layer(builder, node, rtmx.Op.linear,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_matmul(self,
                      builder,            # Type: fb.Builder
                      graph,              # Type: DeepViewExecuter
                      layers,             # Type: Map
                      name,               # Type: str
                      node,               # Type: Map
                      alt_name=None       # Type: str
                      ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        count = 0
        if node['transposeA'] == 'True':
            trans_a_bool = True
            transpose_a = self.export_tensor(
                builder, 'transpose_a', data='true')
            count += 1
        else:
            trans_a_bool = False
        if node['transposeB'] == 'True':
            trans_b_bool = True
            transpose_b = self.export_tensor(
                builder, 'transpose_b', data='true')
            count += 1
        else:
            trans_b_bool = False

        rtmx.LayerStartParamsVector(builder, count)
        if trans_a_bool:
            builder.PrependUOffsetTRelative(transpose_a)
        if trans_b_bool:
            builder.PrependUOffsetTRelative(transpose_b)
        layer_params = builder.EndVector(count)

        a = layers[node['A']]
        b = layers[node['B']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(b)
        builder.PrependUint32(a)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.matmul,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_max_pool(self,
                        builder,            # Type: fb.Builder
                        graph,              # Type: DeepViewExecuter
                        layers,             # Type: Map
                        name,               # Type: str
                        node,               # Type: Map
                        alt_name=None       # Type: str
                        ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        if len(node['size']) == len(node['output_shape']):
            size = self.export_tensor(builder, 'ksize', node['size'])
        else:
            size = self.export_tensor(builder, 'ksize', [1, node['size'][0], node['size'][1], 1])

        if len(node['stride']) == len(node['output_shape']):
            stride = self.export_tensor(builder, 'strides', node['stride'])
        else:
            stride_shape = [1, int(node['stride'][0]), int(node['stride'][1]), 1]
            stride = self.export_tensor(builder, 'strides', stride_shape)

        pool_type = self.export_tensor(builder, 'pooling', data="MAXIMUM")

        if 'head' in node and 'tail' in node:
            if len(node['head']) == len(node['output_shape']):
                head = self.export_tensor(builder, 'head', shape=node['head'])
            else:
                new_head = [0, int(node['head'][0]), int(node['head'][1]), 0]
                head = self.export_tensor(builder, 'head', new_head)
            if len(node['tail']) == len(node['output_shape']):
                tail = self.export_tensor(builder, 'tail', shape=node['tail'])
            else:
                new_tail = [0, int(node['tail'][0]), int(node['tail'][1]), 0]
                tail = self.export_tensor(builder, 'tail', new_tail)
            rtmx.LayerStartParamsVector(builder, 5)
            builder.PrependUOffsetTRelative(head)
            builder.PrependUOffsetTRelative(tail)
        else:
            rtmx.LayerStartParamsVector(builder, 3)
        builder.PrependUOffsetTRelative(size)
        builder.PrependUOffsetTRelative(stride)
        builder.PrependUOffsetTRelative(pool_type)
        if 'head' in node and 'tail' in node:
            layer_params = builder.EndVector(5)
        else:
            layer_params = builder.EndVector(3)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.pool2d,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_max_reduce(self,
                          builder,            # Type: fb.Builder
                          graph,              # Type: DeepViewExecuter
                          layers,             # Type: Map
                          name,               # Type: str
                          node,               # Type: Map
                          alt_name=None       # Type: str
                          ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        node['axes'].sort()
        axes = self.export_tensor(builder, 'axes', node['axes'])
        keep_dims = self.export_tensor(builder, 'keep_dims', data=0)

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(axes)
        builder.PrependUOffsetTRelative(keep_dims)
        layer_params = builder.EndVector(2)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reduce_max,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_mean_reduce(self,
                           builder,            # Type: fb.Builder
                           graph,              # Type: DeepViewExecuter
                           layers,             # Type: Map
                           name,               # Type: str
                           node,               # Type: Map
                           alt_name=None       # Type: str
                           ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        node['axes'].sort()
        axes = self.export_tensor(builder, 'axes', node['axes'])
        keep_dims = self.export_tensor(builder, 'keep_dims', data=0)

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(axes)
        builder.PrependUOffsetTRelative(keep_dims)
        layer_params = builder.EndVector(2)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reduce_mean,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_min_reduce(self,
                          builder,            # Type: fb.Builder
                          graph,              # Type: DeepViewExecuter
                          layers,             # Type: Map
                          name,               # Type: str
                          node,               # Type: Map
                          alt_name=None       # Type: str
                          ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        node['axes'].sort()
        axes = self.export_tensor(builder, 'axes', node['axes'])
        keep_dims = self.export_tensor(builder, 'keep_dims', data=0)

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(axes)
        builder.PrependUOffsetTRelative(keep_dims)
        layer_params = builder.EndVector(2)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reduce_min,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_mul(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['y']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.multiply,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_neg(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.none,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_pad(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        head = self.export_tensor(builder, 'head', list(node['head'])[:])
        tail = self.export_tensor(builder, 'tail', list(node['tail'])[:])
        value = self.export_tensor(builder, 'value', data=node['value'])
        if 'fusible' in node:
            fusible = self.export_tensor(builder, 'fusible', [])
            rtmx.LayerStartParamsVector(builder, 4)
            builder.PrependUOffsetTRelative(fusible)
        else:
            rtmx.LayerStartParamsVector(builder, 3)
        builder.PrependUOffsetTRelative(value)
        builder.PrependUOffsetTRelative(tail)
        builder.PrependUOffsetTRelative(head)
        if 'fusible' in node:
            layer_params = builder.EndVector(4)
        else:
            layer_params = builder.EndVector(3)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.pad,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_pow(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['y']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.pow,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_prelu(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        scales = layers[node['scales']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(scales)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.prelu,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_prod_reduce(self,
                           builder,            # Type: fb.Builder
                           graph,              # Type: DeepViewExecuter
                           layers,             # Type: Map
                           name,               # Type: str
                           node,               # Type: Map
                           alt_name=None       # Type: str
                           ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        node['axes'].sort()
        axes = self.export_tensor(builder, 'axes', node['axes'])
        keep_dims = self.export_tensor(builder, 'keep_dims', data=0)

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(axes)
        builder.PrependUOffsetTRelative(keep_dims)
        layer_params = builder.EndVector(2)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reduce_product,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_quant(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.quant,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_relu(self,
                    builder,            # Type: fb.Builder
                    graph,              # Type: DeepViewExecuter
                    layers,             # Type: Map
                    name,               # Type: str
                    node,               # Type: Map
                    alt_name=None       # Type: str
                    ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.relu,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_relu6(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.relu6,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_reshape(self,
                       builder,            # Type: fb.Builder
                       graph,              # Type: DeepViewExecuter
                       layers,             # Type: Map
                       name,               # Type: str
                       node,               # Type: Map
                       alt_name=None       # Type: str
                       ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        shape = self.export_tensor(builder, 'shape', node['output_shape'])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(shape)
        layer_params = builder.EndVector(1)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reshape,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_resize(self,
                      builder,            # Type: fb.Builder
                      graph,              # Type: DeepViewExecuter
                      layers,             # Type: Map
                      name,               # Type: str
                      node,               # Type: Map
                      alt_name=None       # Type: str
                      ):
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        mode = self.export_tensor(builder, 'mode', data=int(node['mode']))
        if node['align_corners']:
            align_corners = self.export_tensor(builder, 'align_corners', data=1)
        else:
            align_corners = self.export_tensor(builder, 'align_corners', data=0)
        if node['half_pixel_centers']:
            half_pixel_centers = self.export_tensor(builder, 'half_pixel_centers', data=1)
        else:
            half_pixel_centers = self.export_tensor(builder, 'half_pixel_centers', data=0)

        rtmx.LayerStartParamsVector(builder, 3)
        builder.PrependUOffsetTRelative(half_pixel_centers)
        builder.PrependUOffsetTRelative(align_corners)
        builder.PrependUOffsetTRelative(mode)
        layer_params = builder.EndVector(3)

        return self.generate_layer(builder, node, rtmx.Op.resize,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)        

    def export_rsqrt(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        if 'epsilon' in node:
            eps = self.export_tensor(builder, 'epsilon', data=node['epsilon'])
        else:
            eps = self.export_tensor(builder, 'epsilon', data=float(0))

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(eps)
        layer_params = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.rsqrt,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_sigmoid(self,
                       builder,            # Type: fb.Builder
                       graph,              # Type: DeepViewExecuter
                       layers,             # Type: Map
                       name,               # Type: str
                       node,               # Type: Map
                       alt_name=None       # Type: str
                       ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.sigmoid,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_sin(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.none,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_slice(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        axes = self.export_tensor(builder, 'axes', node['axes'])
        head = self.export_tensor(builder, 'head', node['begin'])
        tail = self.export_tensor(builder, 'tail', node['end'])
        if 'strides' in node:
            strides = self.export_tensor(builder, 'strides', node['strides'])
        else:
            strides = self.export_tensor(builder, 'strides', [1]*len(node['axes']))

        rtmx.LayerStartParamsVector(builder, 4)
        builder.PrependUOffsetTRelative(strides)
        builder.PrependUOffsetTRelative(tail)
        builder.PrependUOffsetTRelative(head)
        builder.PrependUOffsetTRelative(axes)
        layer_params = builder.EndVector(4)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.slice,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_softmax(self,
                       builder,            # Type: fb.Builder
                       graph,              # Type: DeepViewExecuter
                       layers,             # Type: Map
                       name,               # Type: str
                       node,               # Type: Map
                       alt_name=None       # Type: str
                       ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        axes = self.export_tensor(builder, 'axes', node['axes'])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(axes)
        layer_params = builder.EndVector(1)

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.softmax,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_sqr(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.multiply,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_sqrt(self,
                    builder,            # Type: fb.Builder
                    graph,              # Type: DeepViewExecuter
                    layers,             # Type: Map
                    name,               # Type: str
                    node,               # Type: Map
                    alt_name=None       # Type: str
                    ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.sqrt,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_sub(self,
                   builder,            # Type: fb.Builder
                   graph,              # Type: DeepViewExecuter
                   layers,             # Type: Map
                   name,               # Type: str
                   node,               # Type: Map
                   alt_name=None       # Type: str
                   ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]
        y = layers[node['y']]

        rtmx.LayerStartInputsVector(builder, 2)
        builder.PrependUint32(y)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.subtract,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_sum_reduce(self,
                          builder,            # Type: fb.Builder
                          graph,              # Type: DeepViewExecuter
                          layers,             # Type: Map
                          name,               # Type: str
                          node,               # Type: Map
                          alt_name=None       # Type: str
                          ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        node['axes'].sort()
        axes = self.export_tensor(builder, 'axes', node['axes'])
        keep_dims = self.export_tensor(builder, 'keep_dims', data=0)

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(axes)
        builder.PrependUOffsetTRelative(keep_dims)
        layer_params = builder.EndVector(2)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.reduce_sum,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_swish(self,
                     builder,            # Type: fb.Builder
                     graph,              # Type: DeepViewExecuter
                     layers,             # Type: Map
                     name,               # Type: str
                     node,               # Type: Map
                     alt_name=None       # Type: str
                     ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        hard = self.export_tensor(builder, 'hard', data=node['hard'])
        beta = self.export_tensor(builder, 'beta', data=node['beta'])

        rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(hard)
        builder.PrependUOffsetTRelative(beta)
        layer_params = builder.EndVector(2)

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.swish,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_tanh(self,
                    builder,            # Type: fb.Builder
                    graph,              # Type: DeepViewExecuter
                    layers,             # Type: Map
                    name,               # Type: str
                    node,               # Type: Map
                    alt_name=None       # Type: str
                    ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        x = layers[node['x']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.tanh,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs)

    def export_transpose(self,
                         builder,            # Type: fb.Builder
                         graph,              # Type: DeepViewExecuter
                         layers,             # Type: Map
                         name,               # Type: str
                         node,               # Type: Map
                         alt_name=None       # Type: str
                         ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        axes = self.export_tensor(builder, 'axes', node['axes'])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(axes)
        layer_params = builder.EndVector(1)

        x = layers[node['input']]

        rtmx.LayerStartInputsVector(builder, 1)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.shuffle,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_transpose_conv(self,
                              builder,            # Type: fb.Builder
                              graph,              # Type: DeepViewExecuter
                              layers,             # Type: Map
                              name,               # Type: str
                              node,               # Type: Map
                              alt_name=None       # Type: str
                              ):
        # Type: (...) -> int
        if alt_name:
            layer_name = builder.CreateString(alt_name)
        else:
            layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        if len(node['stride']) == len(node['output_shape']):
            stride = self.export_tensor(builder, 'strides', node['stride'])
        else:
            stride_shape = [1, int(node['stride'][0]), int(node['stride'][1]), 1]
            stride = self.export_tensor(builder, 'strides', stride_shape)
        if 'activation' in node:
            activation = self.export_tensor(
                builder, 'activation', data=node['activation'])
        else:
            activation = self.export_tensor(
                builder, 'activation', data='linear')

        if 'head' in node and 'tail' in node:
            head = self.export_tensor(builder, 'head', shape=node['head'])
            tail = self.export_tensor(builder, 'tail', shape=node['tail'])
            rtmx.LayerStartParamsVector(builder, 4)
            builder.PrependUOffsetTRelative(head)
            builder.PrependUOffsetTRelative(tail)
        else:
            rtmx.LayerStartParamsVector(builder, 2)
        builder.PrependUOffsetTRelative(stride)
        builder.PrependUOffsetTRelative(activation)
        if 'head' in node and 'tail' in node:
            layer_params = builder.EndVector(4)
        else:
            layer_params = builder.EndVector(2)

        x = layers[node['input']]
        k = layers[node['filter']]

        try:
            b = layers[node['bias']]
            rtmx.LayerStartInputsVector(builder, 3)
            builder.PrependUint32(b)
            builder.PrependUint32(k)
            builder.PrependUint32(x)
            layer_inputs = builder.EndVector(3)
        except KeyError:
            rtmx.LayerStartInputsVector(builder, 2)
            builder.PrependUint32(k)
            builder.PrependUint32(x)
            layer_inputs = builder.EndVector(2)

        return self.generate_layer(builder, node, rtmx.Op.deconv2d,
                                   layer_name, layer_shape, 
                                   inputs=layer_inputs,
                                   params=layer_params)

    def export_variable(self,
                        builder,        # Type: fb.Builder
                        graph,          # Type: DeepViewExecuter
                        layers,         # Type: Map
                        name,           # Type: str
                        node,           # Type: Map
                        alt_name=None   # Type: str
                        ):
        # Type: (...) -> int
        layer_name = builder.CreateString(name)

        rtmx.LayerStartShapeVector(builder, len(node['output_shape']))
        for i in reversed(node['output_shape']):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(node['output_shape']))

        data = self.export_tensor(builder, 'data',
                                  data=graph.tensor_dict[name])

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(data)
        layer_params = builder.EndVector(1)

        return self.generate_layer(builder, node, rtmx.Op.variable,
                                   layer_name, layer_shape,
                                   params=layer_params)

    def export_svm(self,
                   builder,            # Type: fb.Builder
                   graph,             # Type: DeepViewExecuter
                   layers_map,        # Type: Map
                   layer_index,       # Type: count
                   layers,            # Type: list
                   svm,               # Type: String
                   ):
        # Type: (...) -> int
        import json

        if svm[-1] != '/':
            svm = svm + '/'
        with open(svm + 'kld.json', 'r') as f:
            json_data = f.read()
        kld = json.loads(json_data)

        K = kld['K']
        L = kld['L']
        D = kld['D']
        P = int((K - 1) * K / 2)

        svm_shapes = {}
        svm_shapes['alpha'] = [K-1, L]
        svm_shapes['a'] = [P, 1]
        svm_shapes['b'] = [P, 1]
        svm_shapes['sv'] = [L, D]
        svm_shapes['nsv'] = [K, 1]
        svm_shapes['rho'] = [P, 1]
        svm_shapes['label'] = [K, 1]

        for key, val in svm_shapes.items():
            layer_name = builder.CreateString('svm_' + key)

            rtmx.LayerStartShapeVector(builder, len(svm_shapes[key]))
            for i in reversed(svm_shapes[key]):
                builder.PrependInt32(i)
            layer_shape = builder.EndVector(len(svm_shapes[key]))

            with open(svm + key + '.bin', 'rb') as f:
                var_buffer = f.read()
            np_array = np.frombuffer(var_buffer, dtype=np.float32)
            np_array = np.reshape(np_array, svm_shapes[key])
            data = self.export_tensor(builder, 'data', data=np_array)

            rtmx.LayerStartParamsVector(builder, 1)
            builder.PrependUOffsetTRelative(data)
            layer_params = builder.EndVector(1)

            rtmx.LayerStart(builder)
            rtmx.LayerAddType(builder, rtmx.Op.constant)
            rtmx.LayerAddName(builder, layer_name)
            rtmx.LayerAddShape(builder, layer_shape)
            rtmx.LayerAddParams(builder, layer_params)
            layers.append(rtmx.LayerEnd(builder))
            layers_map['svm_' + key] = next(layer_index)

        alpha = layers_map['svm_alpha']
        a = layers_map['svm_a']
        b = layers_map['svm_b']
        sv = layers_map['svm_sv']
        nsv = layers_map['svm_nsv']
        rho = layers_map['svm_rho']

        # First Layer, Computes the kernel
        layer_name = builder.CreateString('svm_kernel')

        output_shape = [K, L]
        rtmx.LayerStartShapeVector(builder, len(output_shape))
        for i in reversed(output_shape):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(output_shape))

        x = layers_map['output']

        rtmx.LayerStartInputsVector(builder, 3)
        builder.PrependUint32(nsv)
        builder.PrependUint32(sv)
        builder.PrependUint32(x)
        layer_inputs = builder.EndVector(3)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.svm_update_kernel)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddInputs(builder, layer_inputs)
        layers.append(rtmx.LayerEnd(builder))
        layers_map['svm_kernel'] = next(layer_index)

        # Second Layer, Computes the decision stats
        layer_name = builder.CreateString('svm_decision')

        output_shape = [P, 1]
        rtmx.LayerStartShapeVector(builder, len(output_shape))
        for i in reversed(output_shape):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(output_shape))

        kernel = layers_map['svm_kernel']

        rtmx.LayerStartInputsVector(builder, 3)
        builder.PrependUint32(rho)
        builder.PrependUint32(alpha)
        builder.PrependUint32(kernel)
        layer_inputs = builder.EndVector(3)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.svm_decision_stats)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddInputs(builder, layer_inputs)
        layers.append(rtmx.LayerEnd(builder))
        layers_map['svm_decision'] = next(layer_index)

        # Third Layer, Computes the posterior probabilities
        layer_name = builder.CreateString('svm_output')

        output_shape = [K, 1]
        rtmx.LayerStartShapeVector(builder, len(output_shape))
        for i in reversed(output_shape):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(output_shape))

        decision = layers_map['svm_decision']

        rtmx.LayerStartInputsVector(builder, 3)
        builder.PrependUint32(b)
        builder.PrependUint32(a)
        builder.PrependUint32(decision)
        layer_inputs = builder.EndVector(3)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.svm_soft_probability)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddInputs(builder, layer_inputs)
        layers.append(rtmx.LayerEnd(builder))
        layers_map['svm_output'] = next(layer_index)

    def export_external_constant(self, builder, name, np_array):
        layer_name = builder.CreateString(name)
        tensor = np_array.copy()

        rtmx.LayerStartShapeVector(builder, len(tensor.shape))
        for i in reversed(list(tensor.shape)):
            builder.PrependInt32(i)
        layer_shape = builder.EndVector(len(tensor.shape))

        data = self.export_tensor(builder, 'data',
                                  data=tensor.astype(np.float32))

        rtmx.LayerStartParamsVector(builder, 1)
        builder.PrependUOffsetTRelative(data)
        layer_params = builder.EndVector(1)

        rtmx.LayerStart(builder)
        rtmx.LayerAddType(builder, rtmx.Op.constant)
        rtmx.LayerAddName(builder, layer_name)
        rtmx.LayerAddShape(builder, layer_shape)
        rtmx.LayerAddParams(builder, layer_params)
        return rtmx.LayerEnd(builder)

    def greedy_step_map(self, layer_steps, layer_blocks, total_blocks):
        layer_block_starts = {}
        set_layers = []

        for step in layer_steps:
            unmapped_layers = []
            open_blocks = [(0, total_blocks)]
            for layer in step:
                if layer in set_layers:
                    start_block = layer_block_starts[layer]
                    end_block = start_block + layer_blocks[layer] - 1
                    i = 0
                    for block in open_blocks:
                        if start_block >= block[0] and end_block <= block[1]:
                            if block[0] == start_block:
                                new_block_0 = []
                            else:
                                new_block_0 = [(block[0], start_block - 1)]
                            if block[1] == end_block:
                                new_block_1 = []
                            else:
                                new_block_1 = [(end_block + 1, block[1])]
                            new_block = new_block_0 + new_block_1
                            open_blocks = open_blocks[:i] + \
                                new_block + open_blocks[i+1:]
                            break
                        i += 1
                else:
                    unmapped_layers.append(layer)

            while unmapped_layers:
                i = 0
                for block in open_blocks:
                    open_space = block[1] - block[0] + 1
                    current_block_fill = 0
                    current_layer_fill = None
                    for layer in unmapped_layers:
                        if layer_blocks[layer] <= open_space and layer_blocks[layer] > current_block_fill:
                            current_block_fill = layer_blocks[layer]
                            current_layer_fill = layer

                    if current_layer_fill is not None:
                        start_block = block[0]
                        end_block = start_block + layer_blocks[layer]
                        if block[1] == end_block:
                            new_block = []
                        else:
                            new_block = [(end_block, block[1])]
                        open_blocks = open_blocks[:i] + \
                            new_block + open_blocks[i+1:]
                        layer_block_starts[current_layer_fill] = start_block
                        unmapped_layers.pop(
                            unmapped_layers.index(current_layer_fill))
                        set_layers.append(current_layer_fill)
                        continue
                    i += 1

        return layer_block_starts

    def largest_first_map(self, layer_steps, layer_blocks, total_blocks):
        set_layers = []
        layer_block_starts = {}

        for i in range(len(layer_blocks.keys())):
            largest_layer = None
            largest_layer_blocks = 0

            for key, val in layer_blocks.items():
                if val > largest_layer_blocks and key not in set_layers:
                    largest_layer = key
                    largest_layer_blocks = val

            layer_step_blocks = []
            start_positions = []
            for step in layer_steps:
                if largest_layer in step:
                    open_blocks = [(0, total_blocks)]
                    for layer in step:
                        if layer in set_layers:
                            start_block = layer_block_starts[layer]
                            end_block = start_block + layer_blocks[layer] - 1
                            i = 0
                            for block in open_blocks:
                                if start_block >= block[0] and end_block <= block[1]:
                                    if block[0] == start_block:
                                        new_block_0 = []
                                    else:
                                        new_block_0 = [
                                            (block[0], start_block - 1)]
                                    if block[1] == end_block:
                                        new_block_1 = []
                                    else:
                                        new_block_1 = [
                                            (end_block + 1, block[1])]
                                    new_block = new_block_0 + new_block_1
                                    open_blocks = open_blocks[:i] + \
                                        new_block + open_blocks[i+1:]
                                    break
                                i += 1

                    for block in open_blocks:
                        if block[1] - block[0] + 1 > largest_layer_blocks and block[0] not in start_positions:
                            start_positions.append(block[0])

                    layer_step_blocks.append(open_blocks)

            start_positions.sort()
            if len(start_positions) == 1:
                layer_block_starts[largest_layer] = start_positions[0]
                set_layers.append(largest_layer)
            else:
                for pos in start_positions:
                    layer_fits = True
                    for step in layer_step_blocks:
                        step_fit = False
                        for block in step:
                            if pos >= block[0] and pos + largest_layer_blocks - 1 <= block[1]:
                                step_fit = True
                                break
                        if not step_fit:
                            layer_fits = False
                            break
                    if layer_fits:
                        layer_block_starts[largest_layer] = pos
                        set_layers.append(largest_layer)
                        break

        return layer_block_starts

    def memory_map(self, graph, block_size, opt_map, save_map, save_layers):
        new_save_layers = []
        for layer in save_layers:
            if layer not in graph.nodes:
                print("WARNING: specified saved layer \'" +
                      str(layer) + "\' is not in graph")
            else:
                new_save_layers.append(layer)
        save_layers = new_save_layers
        reshape_in_save = True
        while reshape_in_save:
            reshape_in_save = False
            for i in range(len(save_layers)):
                if graph.nodes[save_layers[i]]['op'] == 'reshape':
                    reshape_in_save = True
                    save_layers[i] = graph.nodes[save_layers[i]]['input']
                    
        total_blocks = 0
        layer_blocks = {}
        total_layers = 0
        layer_steps = []
        reshape_dict = {}
        for node_name in nx.topological_sort(graph):
            node = graph.nodes[node_name]
            if node['op'] in ['constant', 'copy']:
                continue
            elif node['op'] == 'reshape':
                orig_layer = node['input']
                while graph.nodes[orig_layer]['op'] == 'reshape':
                    orig_layer = graph.nodes[orig_layer]['input']
                reshape_dict[node_name] = orig_layer
                continue

            total_layers += 1
            output_shape = node['output_shape'][:]
            shape_vol = 1
            for val in output_shape:
                if val <= 0:
                    raise ValueError("Found negative value for output shape in node %s. "
                        "Check that you are using the correct default shape." % node_name)
                shape_vol *= val
            if 'datatype' in node:
                if node['datatype'] in [np.dtype('int8'), np.dtype('uint8')]:
                    layer_blocks[node_name] = int(np.ceil(shape_vol/block_size))
                    total_blocks += int(np.ceil(shape_vol/block_size))
                else:
                    layer_blocks[node_name] = int(np.ceil(shape_vol*4/block_size))
                    total_blocks += int(np.ceil(shape_vol*4/block_size))
            else:
                layer_blocks[node_name] = int(np.ceil(shape_vol*4/block_size))
                total_blocks += int(np.ceil(shape_vol*4/block_size))
            if len(layer_steps) == 0:
                if node_name in reshape_dict:
                    layer_steps.append([reshape_dict[node_name]])
                else:
                    layer_steps.append([node_name])
            else:
                prev_layer = layer_steps[-1][:]
                if node_name in reshape_dict:
                    prev_layer.append(reshape_dict[node_name])
                else:
                    prev_layer.append(node_name)
                layer_steps.append(prev_layer)

        if opt_map:
            for i in range(len(layer_steps)-1, -1, -1):
                node = graph.nodes[layer_steps[i][-1]]
                keep_layers = [layer_steps[i][-1]]
                for key, val in node.items():
                    if key in ['op', 'quant_axis', 'quant_scale', 'zero_point']:
                        continue
                    if key == 'values':
                        node_values = val[:]
                        for node_val in node_values:
                            if node_val in layer_blocks.keys() or node_val in reshape_dict.keys():
                                if node_val in reshape_dict:
                                    keep_layers.append(reshape_dict[node_val])
                                else:
                                    keep_layers.append(node_val)
                    if str(val) in layer_blocks.keys() or str(val) in reshape_dict.keys():
                        if val in reshape_dict:
                            keep_layers.append(reshape_dict[val])
                        elif val not in keep_layers:
                            keep_layers.append(val)
                if i != len(layer_steps) - 1:
                    for layer in layer_steps[i+1]:
                        if layer in layer_steps[i] and layer not in keep_layers:
                            keep_layers.append(layer)
                else:
                    for output_name in self.graph.orig_outputs:
                        if output_name in layer_blocks and output_name not in keep_layers:
                            keep_layers.append(output_name)
                for sl in save_layers:
                    if sl not in keep_layers and sl in layer_blocks:
                        keep_layers.append(sl)
                layer_steps[i] = keep_layers

        opt_min_blocks = 0
        for step in layer_steps:
            min_layer_blocks = 0
            for layer in step:
                min_layer_blocks += layer_blocks[layer]
            if min_layer_blocks > opt_min_blocks:
                opt_min_blocks = min_layer_blocks

        if opt_map:
            block_starts_large = self.largest_first_map(layer_steps, layer_blocks,
                                                        total_blocks)
            block_count_large = 0
            for key, val in block_starts_large.items():
                if val + layer_blocks[key] > block_count_large:
                    block_count_large = val + layer_blocks[key]

        layer_block_starts = self.greedy_step_map(layer_steps, layer_blocks,
                                                  total_blocks)

        block_count = 0
        for key, val in layer_block_starts.items():
            if val + layer_blocks[key] > block_count:
                block_count = val + layer_blocks[key]

        used_large = False
        if opt_map and block_count > block_count_large:
            layer_block_starts = block_starts_large
            block_count = block_count_large
            used_large = True

        mapped_layers = len(graph.nodes)
        offset_blocks = int(np.ceil(((mapped_layers + 1) * 128)/block_size))

        for key, val in layer_block_starts.items():
            graph.nodes[key]['block'] = val + offset_blocks

        if opt_map:
            if used_large:
                print("Used Largest First Planning")
            else:
                print("Used Greedy Planning")
            print("Max Blocks: %d" % total_blocks)
            print("Min Blocks: %d" % opt_min_blocks)
            print("Current Blocks: %d" % block_count)
            print("Memory Saved: %.2f" % (((total_blocks - block_count)
                                           / total_blocks * 100) if total_blocks != 0 else 0))
            print("Percent Above Min: %.2f" % (((block_count / opt_min_blocks)
                                                * 100 - 100) if opt_min_blocks != 0 else 0))

        if save_map is not None:
            import matplotlib.pyplot as plt
            print("Saving Map...")
            colour_map = {}
            num_layers = len(layer_blocks.keys())
            if num_layers > 768:
                print("Too many layers to generate the memory map image")
                return block_count
            np.random.seed(3)
            for step in layer_steps:
                for layer in step:
                    if layer not in colour_map:
                        new_colour = list(np.random.randint(20, 255, 3))
                        while new_colour in colour_map.values():
                            new_colour = list(np.random.randint(20, 255, 3))
                        colour_map[layer] = new_colour
            mem_map = np.zeros([num_layers, block_count, 3], dtype=int)
            for i in range(len(layer_steps)):
                for layer in layer_steps[i]:
                    start_block = layer_block_starts[layer]
                    mem_map[i][start_block:start_block
                               + layer_blocks[layer]] = colour_map[layer]

            mem_map = np.transpose(mem_map, [1, 0, 2])
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.set_xlabel('Time Step')
            ax.set_ylabel('Kilobytes')
            if os.path.isdir(save_map):
                save_map = os.path.join(save_map, "mem_map.png")
            ax.imshow(mem_map, aspect='auto', extent=[0, num_layers,
                                                      block_count, 0])
            fig.savefig(save_map)
            print("Saved")

        return block_count

    def validate_model(self):
        for _, data in self.graph.dz_nx_graph.nodes(data=True):
            if 'quant_scale' in data:
                if not np.isfinite(data['quant_scale']).all():
                    raise ValueError('Model contains NaN/Inf scale values')

                if np.any(data['quant_scale'] < 0):
                    raise ValueError('Model contains negative scale values')

    def run(self):
        rename_map = {}
        self.graph.optimize()
        if self.copy_layers:
            self.add_copy()
        self.validate_model()
        builder = BetterBuilder(0)
        layers = []
        layers_map = {}
        layer_index = count(0)

        block_size = 1024
        if self.mem_map:
            block_count = self.memory_map(self.graph.dz_nx_graph, block_size,
                                          self.opt_map, self.save_map, self.save_layers)

        if self.input_names:
            input_names_valid = True
            if len(self.input_names) != len(self.graph.orig_inputs):
                print("Number of alternative input names does not match "
                      "number of input nodes in model. Using default.")
                input_names_valid = False

            for in_name in self.input_names:
                if in_name in self.graph.dz_nx_graph.nodes:
                    print("Alternative input name %s already exists "
                          "in the model. Using default." % in_name)
                    input_names_valid = False
                    break

            if input_names_valid:
                for i in range(len(self.input_names)):
                    rename_map[self.graph.orig_inputs[i]] = self.input_names[i]
        else:
            self.input_names = self.graph.orig_inputs[:]

        if self.output_names:
            output_names_valid = True
            if len(self.output_names) != len(self.graph.orig_outputs):
                print("Number of alternative output names does not match "
                      "number of output nodes in model. Using default.")
                output_names_valid = False

            for out_name in self.output_names:
                if out_name in self.graph.dz_nx_graph.nodes:
                    print("Alternative output name %s already exists "
                          "in the model. Using default." % out_name)
                    output_names_valid = False
                    break

            if output_names_valid:
                for i in range(len(self.output_names)):
                    rename_map[self.graph.orig_outputs[i]
                               ] = self.output_names[i]
        else:
            self.output_names = self.graph.orig_outputs[:]

        if self.ext_constants is not None:
            for key, val in self.ext_constants.items():
                if key in self.graph.dz_nx_graph.nodes:
                    print("WARNING: Unable to add %s to RTM, name already in use." % key)
                    continue
                layers.append(self.export_external_constant(builder, key, val))
                layers_map[key] = next(layer_index)

        for node_name in nx.topological_sort(self.graph.dz_nx_graph):
            node = self.graph.dz_nx_graph.nodes[node_name]
            node_fun = None

            for user in self.user_ops:
                if hasattr(user, 'export_' + node['op']):
                    node_fun = getattr(user, 'export_' + node['op'])
                    break
            if node_fun is None:
                if hasattr(self, 'export_' + node['op']):
                    node_fun = getattr(self, 'export_' + node['op'])
                else:
                    print('WARNING: unsupported op', node['op'])
                    continue

            if node_name in rename_map:
                layers.append(node_fun(builder,
                                       self.graph,
                                       layers_map,
                                       node_name,
                                       node,
                                       rename_map[node_name]))
            else:
                layers.append(node_fun(builder,
                                       self.graph,
                                       layers_map,
                                       node_name,
                                       node))
            layers_map[node_name] = next(layer_index)

        if self.svm is not None:
            self.export_svm(builder, self.graph, layers_map,
                            layer_index, layers, self.svm)

        rtmx.ModelStartLayersVector(builder, len(layers))
        for i in reversed(layers):
            builder.PrependUOffsetTRelative(i)
        model_layers = builder.EndVector(len(layers))

        model_name = builder.CreateString(self.name)
        model_creator = builder.CreateString(
            'RTM Converter Version: {}'.format("0.0.0")) # TODO Insert actual version

        if self.labels is not None:
            labels_ser = []
            for name in self.labels:
                labels_ser.append(builder.CreateString(name))
            rtmx.ModelStartLabelsVector(builder, len(self.labels))
            for i in reversed(labels_ser):
                builder.PrependSOffsetTRelative(i)
            labels_vec = builder.EndVector(len(self.labels))

        # Create model outputs buffer
        outputs_str = builder.CreateString("\n".join(self.output_names))
        outputs_meta = builder.CreateString("outputs")

        rtmx.ResourceStart(builder)
        rtmx.ResourceAddName(builder, outputs_meta)
        rtmx.ResourceAddMeta(builder, outputs_str)
        model_outputs = rtmx.ResourceEnd(builder)

        # Create model normalization buffer
        normalization_str = builder.CreateString(self.normalization)
        normalization_meta = builder.CreateString("image_normalization")

        rtmx.ResourceStart(builder)
        rtmx.ResourceAddName(builder, normalization_meta)
        rtmx.ResourceAddMeta(builder, normalization_str)
        model_normalization = rtmx.ResourceEnd(builder)

        # Create model aliases buffer
        # If output names differ from original graph names,
        # create a meta with name of the original graph name, pointing to it's corresponding output
        aliases = []
        if len(rename_map) > 0:
            for orig_name in self.graph.orig_outputs:
                name = builder.CreateString("alias_" + orig_name)
                alias_idx = layers_map[orig_name].to_bytes(
                    4, byteorder='little', signed=False)
                rtmx.ResourceStartDataVector(builder, 4)
                for b in reversed(alias_idx):
                    builder.PrependByte(b)
                idx = builder.EndVector(4)
                rtmx.ResourceStart(builder)
                rtmx.ResourceAddName(builder, name)
                rtmx.ResourceAddData(builder, idx)
                aliases.append(rtmx.ResourceEnd(builder))

        metadata = []
        for mdata in self.metadata:
            mdata_list = mdata.split(',')
            mdata_file = mdata_list[0]
            mdata_extension = mdata_file[mdata_file.rfind('.') + 1:]
            mdata_name = mdata_file[:mdata_file.rfind('.')]
            mdata_mime = 'application/octet-stream'
            if mdata_extension == 'txt':
                mdata_mime = 'text/plain'            
            if len(mdata_list) > 1:
                mdata_name = mdata_list[1]
            if len(mdata_list) > 2:
                mdata_mime = mdata_list[2]

            builder_mdata_name = builder.CreateString(mdata_name)
            builder_mdata_mime = builder.CreateString(mdata_mime)
            builder_mdata_data = None
            if mdata_mime == 'text/plain':
                with open(mdata_file, 'r', encoding='utf-8') as f:
                    file_string = f.read()
                    builder_mdata_data = builder.CreateString(file_string)
            else:
                with open(mdata_file, "rb") as f:
                    file_bytes = f.read()
                    builder_mdata_data = builder.CreateByteVector(file_bytes)

            rtmx.ResourceStart(builder)
            rtmx.ResourceAddName(builder, builder_mdata_name)
            rtmx.ResourceAddData(builder, builder_mdata_data)
            rtmx.ResourceAddMime(builder, builder_mdata_mime)
            metadata.append(rtmx.ResourceEnd(builder))

        # Add meta info to model
        rtmx.ModelStartMetaVector(builder, 2 + len(aliases) + len(metadata))
        builder.PrependUOffsetTRelative(model_outputs)
        builder.PrependUOffsetTRelative(model_normalization)
        for alias in aliases:
            builder.PrependUOffsetTRelative(alias)
        for mdata in metadata:
            builder.PrependUOffsetTRelative(mdata)
        meta_vec = builder.EndVector(2 + len(aliases) + len(metadata))

        rtmx.ModelStartInputsVector(builder, len(self.graph.orig_inputs))
        for i in reversed(self.graph.orig_inputs):
            builder.PrependUint32(layers_map[i])
        input_layers = builder.EndVector(len(self.graph.orig_inputs))

        rtmx.ModelStartOutputsVector(builder, len(self.graph.orig_outputs))
        for i in reversed(self.graph.orig_outputs):
            builder.PrependUint32(layers_map[i])
        output_layers = builder.EndVector(len(self.graph.orig_outputs))

        rtmx.ModelStart(builder)
        rtmx.ModelAddLayers(builder, model_layers)
        rtmx.ModelAddName(builder, model_name)
        rtmx.ModelAddCreator(builder, model_creator)
        if self.mem_map:
            rtmx.ModelAddBlockCount(builder, block_count)
            rtmx.ModelAddBlockSize(builder, block_size)
        if self.labels is not None:
            rtmx.ModelAddLabels(builder, labels_vec)
        rtmx.ModelAddMeta(builder, meta_vec)
        rtmx.ModelAddInputs(builder, input_layers)
        rtmx.ModelAddOutputs(builder, output_layers)
        model = rtmx.ModelEnd(builder)
        builder.FinishWithFileIdentifierx(model, 'RTMx')
        return builder.Output()
