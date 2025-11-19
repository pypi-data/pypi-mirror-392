# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from __future__ import division
from deepview_rtm.tflite_importer import TFLiteImporter

import os
import math
import networkx as nx
import numpy as np
import tarfile

import deepview_rtm.utils as utils


def convert_format(convert_list, in_format='nhwc', out_format='nchw'):
    in_format = in_format.lower()
    out_format = out_format.lower()

    in_n_loc = in_format.find('n')
    out_n_loc = out_format.find('n')
    in_c_loc = in_format.find('c')
    out_c_loc = out_format.find('c')

    n = convert_list[in_n_loc]
    c = convert_list[in_c_loc]

    sizes = []
    for i in range(len(convert_list)):
        if (i != in_n_loc and i != in_c_loc):
            sizes.append(convert_list[i])

    out_list = [None] * len(convert_list)
    out_list[out_n_loc] = n
    out_list[out_c_loc] = c

    j = 0
    for i in range(len(out_list)):
        if (i != out_n_loc and i != out_c_loc):
            out_list[i] = sizes[j]
            j += 1

    return out_list


class DeepViewOptimizer:
    def __init__(self,
                 filename,
                 nnef_format='nhwc',
                 skip_optimizations=None,
                 panel_shuffle=None,
                 default_shape=None,
                 user_ops=[],
                 quantize=False,
                 input_type='none',
                 output_type='none',
                 samples=None,
                 num_samples=10,
                 model_input_type=np.float32,
                 subgraph_names=[],
                 quant_tensor=False,
                 quant_channel=False,
                 force_quant_tensor=False,
                 quant_norm='unsigned',
                 activation_datatype='none',
                 transpose_conv_filter_datatype='none',
                 onnx_input_format='none'):
        if default_shape is None:  # Make sure default shape is not mutable
            default_shape = [1, 224, 224, 3]
        if skip_optimizations is None:
            skip_optimizations = ['conv_mul4', 'concatN', 'sigmoid_expand', 'quantize_dequant_ops']
        self.in_format = 'nhwc'
        self.default_shape = default_shape
        self.quantize = quantize
        self.input_type = input_type
        self.output_type = output_type
        self.onnx_input_format = onnx_input_format
        self.importer = None
        filename = self.clean_filename(filename)
        if type(filename) != str:  # Ensure filename is a valid type
            from tensorflow.core.framework import graph_pb2
            if type(filename) != graph_pb2.GraphDef and type(filename) != bytes:
                raise ValueError(
                    'filename parameter must be a string, GraphDef, or TFLite flatbuffer: %s' % type(filename))

        self.get_importer(filename,
                          nnef_format,
                          user_ops,
                          subgraph_names,
                          quantize,
                          samples,
                          num_samples,
                          model_input_type,
                          quant_norm)
        if self.importer is None:
            raise ValueError(
                'Incorrect model format or file not found (If using SavedModel, please specify directory)')
        self.dz_nx_graph, self.orig_inputs, self.orig_outputs = self.importer.run()
        self.labels = {}
        self.tensor_dict = {}
        self.populate_tensors()
        self.optimized = False
        self.skip_optimizations = skip_optimizations
        self.panel_shuffle = panel_shuffle
        self.relabeled_names = {}
        self.quant_tensor = quant_tensor
        self.force_quant_tensor = force_quant_tensor
        self.quant_channel = quant_channel
        self.activation_datatype = activation_datatype
        self.transpose_conv_filter_datatype = transpose_conv_filter_datatype

    def clean_filename(self, filename):
        if type(filename) == str and \
            os.path.exists(filename) and \
            os.path.isfile(filename) and \
            tarfile.is_tarfile(filename):
            with tarfile.open(filename) as tar:
                filename = filename.replace(".tar.gz", "")
                filename = filename.replace(".tar.bz2", "")
                filename = filename.replace(".tar.xz", "")
                filename = filename.replace(".tgz", "")
                filename = filename.replace(".tar", "")
                print('EXTRACTING TAR FILE TO -> %s' % filename)
                tar.extractall(filename)
            if not os.path.exists(filename + '/saved_model.pb'):
                filename = filename + '/' + filename + '/saved_model'
            if not os.path.exists(filename + '/saved_model.pb'):
                raise ValueError("Unable to located 'saved_model.pb' file " \
                    "within the provided tarfile. Please manually unzip " \
                    "and convert using the directory that contains 'saved_model.pb'")
        return filename

    def get_importer(self,
                     filename,
                     nnef_format,
                     user_ops,
                     subgraph_names,
                     quantize,
                     samples,
                     num_samples=10,
                     model_input_type=np.float32,
                     quant_norm='unsigned'):
        """
        Determines the correct import format
        :param filename: Directory to model
        :param mode: Padding mode
        :param nnef_format: If NNEF file is in NCHW or NHWC format
        """
        if type(filename) != str:  # Handle loaded Tensorflow/TFLite graphs
            self.import_binary_model(filename, subgraph_names, user_ops)
        # Handle Keras models
        elif filename.endswith('.h5') or filename.endswith('.hdf5') or (
            os.path.exists(os.path.join(filename, "fingerprint.pb")) and \
            os.path.exists(os.path.join(filename, "keras_metadata.pb")) and \
            os.path.exists(os.path.join(filename, "saved_model.pb"))
        ):
            self.import_keras_model(filename, quantize, subgraph_names, samples, num_samples,
                                    model_input_type, quant_norm)
            # Handle saved model and TFHub input
        elif utils.saved_model_exists(filename) or filename.startswith('https://tfhub.dev'):
            self.import_saved_model(filename, quantize, subgraph_names, samples, num_samples,
                                    model_input_type, quant_norm)
        # Determine input model format by file extension
        elif filename.endswith('.rtm'):
            from .rtm_importer import RTMImporter
            self.importer = RTMImporter(filename)
        elif filename.endswith('.pb'):
            self.import_tf_1_x_model(filename, quantize, subgraph_names, samples, num_samples,
                                     model_input_type, quant_norm, user_ops)
        elif filename.endswith('.tflite'):
            from .tflite_importer import TFLiteImporter
            self.importer = TFLiteImporter(filename,
                                           subgraph_names=subgraph_names)
        elif filename.endswith('.onnx'):
            from .onnx_importer import ONNXImporter
            self.importer = ONNXImporter(filename, input_format=self.onnx_input_format,
                                         default_shape=self.default_shape, 
                                         subgraph_names=subgraph_names, 
                                         model_input_type=model_input_type)

    def import_binary_model(self, filename, subgraph_names, user_ops):
        from tensorflow.core.framework import graph_pb2
        if type(filename) == graph_pb2.GraphDef:
            from .tensorflow_importer import TensorflowImporter
            self.importer = TensorflowImporter(filename,
                                               default_shape=self.default_shape,
                                               user_ops=user_ops,
                                               subgraph_names=subgraph_names)
        elif type(filename) == bytes:
            from .tflite_importer import TFLiteImporter
            self.importer = TFLiteImporter(filename,
                                           subgraph_names=subgraph_names)

    def import_keras_model(self, filename, quantize, subgraph_names, samples, num_samples, 
                           model_input_type, quant_norm):
        import tensorflow as tf
        import tensorflow_hub as hub
        
        # Handle Tensorflow 2.0
        if float(tf.__version__[:2]) >= 2.0:
            from deepview_rtm.tensorflow import keras_models_load_model
            from deepview_rtm.tensorflow import tflite_converter_from_keras_model
            converter = tflite_converter_from_keras_model(
                keras_models_load_model(filename, False, {'KerasLayer': hub.KerasLayer}))
        else:
            from deepview_rtm.tensorflow import tflite_converter_from_keras_model_file
            converter = tflite_converter_from_keras_model_file(filename)

        h5_model = tf.keras.models.load_model(filename)
        input_tensor = h5_model.input
        
        multiple_shapes = False
        
        if isinstance(input_tensor, tuple) or isinstance(input_tensor, list):
            self.default_shape = [
                [1, s.shape[1], s.shape[2], s.shape[3]] for s in input_tensor
            ]
            multiple_shapes = True
        else:
            if len(input_tensor.shape) > len(self.default_shape):
                self.default_shape += ([1] * (len(input_tensor.shape) - len(self.default_shape)))
                
            for i in range(len(input_tensor.shape)):
                if input_tensor.shape[i] is not None and input_tensor.shape[i] != -1:
                    self.default_shape[i] = input_tensor.shape[i]
        
        if quantize:
            if multiple_shapes:
                raise ValueError("Currently unable to quantize multi-input models. Please contact Au-Zone support.")
            
            from converter.plugin_api.dataset import Dataset
            dataset = Dataset(samples,self.default_shape,quant_norm, num_samples, model_input_type)
            representative_dataset_gen = dataset.generator()
            
            converter.optimizations = [tf.lite.Optimize.DEFAULT, tf.lite.OpsSet.SELECT_TF_OPS]
            converter.representative_dataset = representative_dataset_gen
            if self.input_type == 'int8':
                converter.inference_input_type = tf.int8
            elif self.input_type == 'uint8':
                converter.inference_input_type = tf.uint8
            if self.output_type == 'int8':
                converter.inference_output_type = tf.int8
            elif self.output_type == 'uint8':
                converter.inference_output_type = tf.uint8
        try:
            filename = converter.convert()
        except Exception:
            if quantize:
                converter.experimental_new_quantizer = False
            else:
                converter.experimental_new_converter = False
            filename = converter.convert()

        from .tflite_importer import TFLiteImporter
        self.importer = TFLiteImporter(filename,
                                       subgraph_names=subgraph_names)

    def import_saved_model(self, filename, quantize, subgraph_names, samples, num_samples,
                           model_input_type, quant_norm):
        if quantize:
            from converter.plugin_api.dataset import Dataset
            dataset = Dataset(samples,self.default_shape,quant_norm, num_samples, model_input_type)
            representative_dataset_gen = dataset.generator()
        else:
            representative_dataset_gen = None
        if filename.startswith('https://tfhub.dev') or os.path.isfile(filename + '/tfhub_module.pb'):
            filename = utils.graph_def_from_tfhub_model(self.default_shape, filename,
                                                        quantize=quantize,
                                                        model_input_type=model_input_type,
                                                        input_type=self.input_type,
                                                        output_type=self.output_type,
                                                        dataset_gen=representative_dataset_gen)
        else:
            try:  # Saved Model
                filename = utils.graph_def_from_saved_model(self.default_shape, filename,
                                                            quantize=quantize,
                                                            model_input_type=model_input_type,
                                                            input_type=self.input_type,
                                                            output_type=self.output_type,
                                                            dataset_gen=representative_dataset_gen)
            except ValueError as e:  # TFHub
                if e.args[0] == "This converter can only convert a single ConcreteFunction. " \
                                "Converting multiple functions is under development.":
                    filename = utils.graph_def_from_tfhub_model(self.default_shape, filename,
                                                                quantize=quantize, input_type=self.input_type,
                                                                output_type=self.output_type,
                                                                dataset_gen=representative_dataset_gen)
                else:
                    raise e

        from .tflite_importer import TFLiteImporter
        self.importer = TFLiteImporter(filename,
                                       subgraph_names=subgraph_names)

    def import_tf_1_x_model(self, filename, quantize, subgraph_names,
                            samples, num_samples, model_input_type, quant_norm, user_ops):
        if quantize:
            if subgraph_names == []:
                raise ValueError("ERROR: To convert TensorFlow 1.x graphs to TFLite, "
                                "please provide the input and output names")
            input_names = subgraph_names[0]
            output_names = subgraph_names[1]
            if not input_names or not output_names:
                raise ValueError("ERROR: To convert TensorFlow 1.x graphs to TFLite, "
                                "please provide the input and output names")
            import tensorflow as tf
            # Handle Tensorflow 2.0
            from deepview_rtm.tensorflow import tflite_converter_from_frozen_graph
            converter = tflite_converter_from_frozen_graph(
                filename, input_names, output_names,
                {input_names[0]: self.default_shape})
            if quantize:
                converter.optimizations = [tf.lite.Optimize.DEFAULT]

                from converter.plugin_api.dataset import Dataset
                dataset = Dataset(samples,self.default_shape,quant_norm, num_samples, model_input_type)
                representative_dataset_gen = dataset.generator()
                converter.representative_dataset = representative_dataset_gen
                
                converter.experimental_new_converter = True
                if self.input_type == 'int8':
                    converter.inference_input_type = tf.int8
                elif self.input_type == 'uint8':
                    converter.inference_input_type = tf.uint8
                if self.output_type == 'int8':
                    converter.inference_output_type = tf.int8
                elif self.output_type == 'uint8':
                    converter.inference_output_type = tf.uint8
            try:
                tflite_model = converter.convert()
            except Exception:
                if quantize:
                    converter.experimental_new_converter = False
                else:
                    converter.experimental_new_quantizer = False
                tflite_model = converter.convert()
            self.importer = TFLiteImporter(tflite_model, subgraph_names=subgraph_names)
        else:
            from .tensorflow_importer import TensorflowImporter
            from tensorflow.core.framework import graph_pb2
            graph = graph_pb2.GraphDef()
            with open(filename, "rb") as f:
                graph.ParseFromString(f.read())
            self.importer = TensorflowImporter(graph,
                                               default_shape=self.default_shape,
                                               user_ops=user_ops,
                                               subgraph_names=subgraph_names)

    def optimize(self):
        if not self.optimized:
            self.optimize_network()
            self.optimized = True

    def print_network(self, print_constants=True, print_tensors=True):
        for node_name in nx.topological_sort(self.dz_nx_graph):
            if not print_constants and self.dz_nx_graph.nodes[node_name]['op'] == 'constant':
                continue
            print(node_name)
            print(self.dz_nx_graph.nodes[node_name])
            if print_tensors and node_name in self.tensor_dict:
                print(self.tensor_dict[node_name])
            print('\n')
            input()

    def populate_tensors(self):
        for node, data in self.dz_nx_graph.nodes(data=True):
            if 'np_tensor' in data:
                self.tensor_dict[node] = np.asarray(data['np_tensor'])
                del data['np_tensor']

    def optimize_network(self):
        if 'const_combine' not in self.skip_optimizations:
            self.const_unary_binary_optimization()
        self.scale_zero_to_list()
        if 'shared_const_split' not in self.skip_optimizations:
            self.shared_filter_split_optimization()
            self.shared_bias_split_optimization()
        self.conv_add_zero_bias()
        if 'prelu_relu' not in self.skip_optimizations:
            self.prelu_to_relu_optimization()
        if 'relu6' not in self.skip_optimizations:
            self.relu6_optimization()
        if 'rsqrt_eps' not in self.skip_optimizations:
            self.rsqrt_eps_optimization()
        if 'mm_bn' not in self.skip_optimizations:
            self.matmul_batchnorm_folding_optimization()
        if 'conv_mul' not in self.skip_optimizations:
            self.conv_mul_fold_optimization()
        if 'conv_bias' not in self.skip_optimizations:
            self.conv_add_bias_optimization()
        if 'conv_bn' not in self.skip_optimizations:
            self.conv_batchnorm_folding_optimization()
        if self.panel_shuffle:
            self.panel_shuffle_optimization()
        if 'conv_activ' not in self.skip_optimizations:
            self.conv_activation_folding_optimization()
        if 'transpose_conv_rotate' not in self.skip_optimizations:
            self.transpose_conv_rotation_optimization()
        if 'bn_remove' not in self.skip_optimizations:
            self.batchnorm_removal_optimization()
        if 'conv_mul4' not in self.skip_optimizations:
            self.conv_padding_slice_optimization()
        if 'matmul_dense' not in self.skip_optimizations:
            self.matmul_add_optimization()
            self.matmul_add_zero_bias()
            self.matmul_activation_folding_optimization()
        if 'pow_to_mul' not in self.skip_optimizations:
            self.pow_to_mult_optimization()
        # self.squish_constants_optimization()
        self.linear_to_dense_optimization()
        self.mean_reduce_to_avg_pool_optimization()
        self.concat_to_resize_optimization_form1()
        self.concat_to_resize_optimization_form2()
        self.replace_transpose_reshape_optimization()
        self.remove_additional_reshape_optimization()
        if 'quant_pool' not in self.skip_optimizations:
            self.quantize_pool()
        if 'fold_pad' not in self.skip_optimizations:
            self.fold_padding_optimization()
        if 'concatN' not in self.skip_optimizations:
            self.concat_n_split_optimization()
        if self.activation_datatype == 'uint8':
            self.force_activations_to_uint8()
        if 'sigmoid_expand' not in self.skip_optimizations:
            self.sigmoid_expansion_optimization()
        if 'quantize_dequant_ops' not in self.skip_optimizations:
            self.quantize_dequant_ops_optimization()
        if self.transpose_conv_filter_datatype != 'none':
            self.adjust_transpose_conv_filter_datatype()
        if self.input_type != 'none':
            self.adjust_input_type()
        if self.output_type != 'none':
            self.adjust_output_type()
        if self.quant_tensor:
            self.to_tensor_quant()
        if self.quant_channel:
            self.to_channel_quant()
        self.clean_zero_point()

    def to_tensor_quant(self):
        # ToDo: Ask to Zhe He when ZP are different
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] not in ['conv']:
                continue
            if data['groups'] != 1 and not self.force_quant_tensor:
                continue
            
            filter_name = data['filter']
            filter_node = self.dz_nx_graph.nodes[filter_name]
            if filter_node['op'] != 'constant':
                continue

            if filter_node['datatype'] != np.int8:
                continue
            pruned_channel_idx = []
            correct_channel_idx = np.where(filter_node['zero_point'] == 0)
            if np.count_nonzero(filter_node['zero_point']) > 1:
                print("[warning] irregular per-channel weights observed, might due to insufficient training for QAT")
                print("Trying to convert (pruning) ill-conditioned weights", filter_name)
                pruned_channel_idx = np.nonzero(filter_node['zero_point'])

            if not np.isfinite(filter_node['quant_scale']).all():
                raise ValueError('Model contains NaN/Inf scale values')

            if np.any(filter_node['quant_scale'] <= 0):
                raise ValueError('Model contains Negative/Zero scale values')

            if 'quant_scale' not in filter_node or 'zero_point' not in filter_node:
                continue
            if list(filter_node['zero_point'].shape) == [1] and \
                    list(filter_node['quant_scale'].shape) == [1]:
                continue

            filter_node['zero_point'] = np.expand_dims(
                self.dz_nx_graph.nodes[filter_name]['zero_point'][correct_channel_idx].astype(np.uint8)[0], 0)

            if filter_node['zero_point'][0] != 0:
                print("WARNING: Non-zero zp for weights observed")

            if self.force_quant_tensor:
                scale_max = np.max(self.dz_nx_graph.nodes[filter_name]['quant_scale'][correct_channel_idx])
            else:
                scale_max = np.max(filter_node['quant_scale'])
            max_idx = np.where(filter_node['quant_scale'] == scale_max)
            if scale_max != 0:
                scales = filter_node['quant_scale'] / scale_max
                filter_node['quant_scale'] = np.expand_dims(scale_max, 0)
            else:
                scales = np.ones(filter_node['quant_scale'])
                filter_node['quant_scale'] = np.expand_dims(0.0, 0)

            if self.tensor_dict[filter_name].shape[3] == 1:
                tensor = np.rint(self.tensor_dict[filter_name][:, :, :, 0].astype(np.float32) * scales)
                tensor = np.expand_dims(tensor, 3)
            else:
                tensor = np.rint(self.tensor_dict[filter_name].astype(np.float32) * scales)
                if self.force_quant_tensor:
                    weight_shape = tensor.shape
                    for channel_id in pruned_channel_idx:
                        tensor[:, :, :, channel_id] = np.zeros((weight_shape[0], weight_shape[1], weight_shape[2], 1))

            tensor = tensor.astype(np.int8)
            self.tensor_dict[filter_name] = tensor

            if 'bias' in data:
                bias_name = data['bias']
                bias_node = self.dz_nx_graph.nodes[bias_name]
                scale_max_bias = bias_node['quant_scale'][max_idx]
                bias_scales = bias_node['quant_scale'] / scale_max_bias
                bias_node['quant_scale'] = np.expand_dims(scale_max_bias, 0)
                bias_node['zero_point'] = np.expand_dims(bias_node['zero_point'][0], 0)
                bias_tensor = np.rint(self.tensor_dict[bias_name].astype(np.float32) * bias_scales)
                bias_tensor = bias_tensor.astype(np.int32)
                self.tensor_dict[bias_name] = bias_tensor

    def to_channel_quant(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] not in ['conv']:
                continue
            if data['groups'] != 1:
                continue

            filter_name = data['filter']
            dims = self.tensor_dict[filter_name].shape
            channel_num = dims[3]
            if channel_num == 1:
                continue

            filter_node = self.dz_nx_graph.nodes[filter_name]
            if 'quant_scale' not in filter_node or 'zero_point' not in filter_node:
                continue
            if list(filter_node['zero_point'].shape) != [1] and \
                    list(filter_node['quant_scale'].shape) != [1]:
                continue

            if filter_node['op'] != 'constant':
                continue
            if filter_node['datatype'] != np.int8:
                continue

            filter_node['zero_point'] = filter_node['zero_point'].astype(np.int16)
            filter_node['zero_point'] = np.repeat(filter_node['zero_point'], channel_num)
            scale_in = filter_node['quant_scale']

            new_scale = []
            tensor = self.tensor_dict[filter_name]
            for chan in range(channel_num):
                max_val = np.max(tensor[:, :, :, chan])
                min_val = np.min(tensor[:, :, :, chan])
                if min_val < 0:
                    if max_val == 0:
                        candidate_scale = -127.0 / min_val
                    else:
                        candidate_scale = np.max([-127.0 / min_val, 128.0 / max_val])
                else:
                    if max_val == 0:
                        candidate_scale = 0
                    else:
                        candidate_scale = 128.0 / max_val
                new_scale.append(candidate_scale)

            new_scale_array = np.array(new_scale)
            new_tensor = tensor * new_scale_array # .reshape((1, 2))[:, np.newaxis]
            self.tensor_dict[filter_name] = np.rint(new_tensor).astype(np.int8)
            filter_node['quant_scale'] = new_scale_array.astype(np.float32) * scale_in

    def rewire_out_edges(self, previous_node, new_node):
        out_edges = list(self.dz_nx_graph.out_edges(previous_node))
        for edge in out_edges:
            self.dz_nx_graph.add_edge(new_node, edge[1])
            for key, val in self.dz_nx_graph.nodes[edge[1]].items():
                if key == 'values':
                    new_val = []
                    for conc_name in val:
                        if conc_name == previous_node:
                            new_val.append(new_node)
                        else:
                            new_val.append(conc_name)
                    self.dz_nx_graph.nodes[edge[1]][key] = new_val
                if type(val) == str and val == previous_node:
                    self.dz_nx_graph.nodes[edge[1]
                    ][key] = new_node
            self.dz_nx_graph.remove_edge(edge[0], edge[1])

    # Updated and refactored
    def const_unary_binary_optimization(self):
        keep_going = True
        while keep_going:
            remove_nodes = []
            remove_edges = []
            keep_going = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] == 'rsqrt':
                    in_node = self.dz_nx_graph.nodes[data['x']]
                    if in_node['op'] != 'constant':
                        continue
                    keep_going = True
                    x_tensor = self.tensor_dict[data['x']]
                    z_tensor = 1 / np.sqrt(x_tensor)
                    self.tensor_dict[node_name] = z_tensor
                    data['output_shape'] = in_node['output_shape']
                    data['op'] = 'constant'
                    if len(list(self.dz_nx_graph.out_edges(data['x']))) == 1:
                        remove_nodes.append(data['x'])
                    else:
                        remove_edges.append((data['x'], node_name))

                elif data['op'] in ['add', 'mul', 'sub']:
                    in_node1 = self.dz_nx_graph.nodes[data['x']]
                    in_node2 = self.dz_nx_graph.nodes[data['y']]
                    if in_node1['op'] != 'constant' or in_node2['op'] != 'constant':
                        continue
                    keep_going = True
                    x_tensor = self.tensor_dict[data['x']]
                    y_tensor = self.tensor_dict[data['y']]
                    if data['op'] == 'add':
                        z_tensor = np.add(x_tensor, y_tensor)
                    elif data['op'] == 'sub':
                        z_tensor = np.subtract(x_tensor, y_tensor)
                    elif data['op'] == 'mul':
                        z_tensor = np.multiply(x_tensor, y_tensor)
                    x_tot_shape = 1
                    for val in x_tensor.shape:
                        x_tot_shape *= val
                    y_tot_shape = 1
                    for val in y_tensor.shape:
                        y_tot_shape *= val
                    self.tensor_dict[node_name] = z_tensor
                    if x_tot_shape > y_tot_shape:
                        data['output_shape'] = in_node1['output_shape']
                    else:
                        data['output_shape'] = in_node2['output_shape']
                    data['op'] = 'constant'
                    if len(list(self.dz_nx_graph.out_edges(data['x']))) == 1:
                        remove_nodes.append(data['x'])
                    else:
                        remove_edges.append((data['x'], node_name))
                    if len(list(self.dz_nx_graph.out_edges(data['y']))) == 1:
                        remove_nodes.append(data['y'])
                    else:
                        remove_edges.append((data['y'], node_name))

                elif data['op'] == 'reshape':
                    in_node = self.dz_nx_graph.nodes[data['input']]
                    if in_node['op'] != 'constant':
                        continue
                    keep_going = True
                    input_tensor = self.tensor_dict[data['input']]
                    out_tensor = np.reshape(input_tensor, data['output_shape'])
                    self.tensor_dict[node_name] = out_tensor
                    data['op'] = 'constant'
                    if len(list(self.dz_nx_graph.out_edges(data['input']))) != 1:
                        remove_nodes.append(data['input'])
                    else:
                        remove_edges.append((data['input'], node_name))

            self.dz_nx_graph.remove_nodes_from(remove_nodes)
            self.dz_nx_graph.remove_edges_from(remove_edges)

    def shared_filter_split_optimization(self):
        shared_filt_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            filt_out_edges = list(
                self.dz_nx_graph.out_edges(data['filter']))
            if len(filt_out_edges) != 1 and data['filter'] not in shared_filt_nodes:
                shared_filt_nodes.append(data['filter'])

        for shared_filt in shared_filt_nodes:
            out_edges = list(self.dz_nx_graph.out_edges(shared_filt))
            # Ensure the filters are only used for convolutions
            for out_edge in out_edges:
                out_node = out_edge[1]
                if self.dz_nx_graph.nodes[out_node]['op'] != 'conv':
                    return

            counter = 0
            for out_edge in out_edges:
                if counter == 0:
                    counter += 1
                    continue

                out_node_name = out_edge[1]
                out_node = self.dz_nx_graph.nodes[out_node_name]
                filt_node = self.dz_nx_graph.nodes[out_edge[0]]
                new_filt_name = out_edge[0] + '_copy' + str(counter)

                while new_filt_name in self.dz_nx_graph:
                    counter += 1
                    new_filt_name = out_edge[0] + '_copy' + str(counter)

                datatype = filt_node['datatype']
                self.dz_nx_graph.add_node(new_filt_name, op='constant',
                                          output_shape=filt_node['output_shape'][:],
                                          datatype=datatype)
                if 'quant_scale' in filt_node and 'zero_point' in filt_node:
                    self.dz_nx_graph.nodes[new_filt_name]['quant_scale'] = filt_node['quant_scale'].copy()
                    self.dz_nx_graph.nodes[new_filt_name]['zero_point'] = filt_node['zero_point'].copy()
                    self.dz_nx_graph.nodes[new_filt_name]['quant_axis'] = filt_node['quant_axis']
                out_node['filter'] = new_filt_name
                self.tensor_dict[new_filt_name] = self.tensor_dict[out_edge[0]].copy(
                )
                self.dz_nx_graph.add_edge(new_filt_name, out_node_name)
                self.dz_nx_graph.remove_edge(out_edge[0], out_edge[1])
                counter += 1

    def shared_bias_split_optimization(self):
        shared_bias_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            if 'bias' not in data:
                continue
            if data['bias'] == 0.0:
                continue
            bias_out_edges = list(self.dz_nx_graph.out_edges(data['bias']))
            if len(bias_out_edges) != 1 and data['bias'] not in shared_bias_nodes:
                shared_bias_nodes.append(data['bias'])

        for shared_bias in shared_bias_nodes:
            out_edges = list(self.dz_nx_graph.out_edges(shared_bias))
            # Ensure the filters are only used for convolutions
            for out_edge in out_edges:
                out_node = out_edge[1]
                if self.dz_nx_graph.nodes[out_node]['op'] != 'conv':
                    return

            counter = 0
            for out_edge in out_edges:
                if counter == 0:
                    counter += 1
                    continue

                out_node_name = out_edge[1]
                out_node = self.dz_nx_graph.nodes[out_node_name]
                bias_node = self.dz_nx_graph.nodes[out_edge[0]]
                new_bias_name = out_edge[0] + '_copy' + str(counter)

                while new_bias_name in self.dz_nx_graph:
                    counter += 1
                    new_bias_name = out_edge[0] + '_copy' + str(counter)

                datatype = bias_node['datatype']
                self.dz_nx_graph.add_node(new_bias_name, op='constant',
                                          output_shape=bias_node['output_shape'][:],
                                          datatype=datatype)
                if 'quant_scale' in bias_node and 'zero_point' in bias_node:
                    out_conv_node = self.dz_nx_graph.nodes[out_node_name]
                    input_scale = self.dz_nx_graph.nodes[out_conv_node['input']]['quant_scale'].copy()
                    filter_scale = self.dz_nx_graph.nodes[out_conv_node['filter']]['quant_scale'].copy()
                    self.dz_nx_graph.nodes[new_bias_name]['quant_scale'] = input_scale * filter_scale
                    self.dz_nx_graph.nodes[new_bias_name]['zero_point'] = bias_node['zero_point'].copy()
                    self.dz_nx_graph.nodes[new_bias_name]['quant_axis'] = bias_node['quant_axis']
                out_node['bias'] = new_bias_name
                self.tensor_dict[new_bias_name] = self.tensor_dict[out_edge[0]].copy(
                )
                self.dz_nx_graph.add_edge(new_bias_name, out_node_name)
                self.dz_nx_graph.remove_edge(out_edge[0], out_edge[1])
                counter += 1

    def pow_to_mult_optimization(self):
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):

            # Check if operator is a pow
            if data['op'] != 'pow':
                continue
            x_name = data['x']
            y_name = data['y']
            y_node = self.dz_nx_graph.nodes[y_name]

            # Check if the 2nd input is a constant with size 1
            if y_node['op'] != 'constant' or y_node['output_shape'] != [1]:
                continue
            pow_tensor = self.tensor_dict[y_name]

            # Check if it's a power of 2
            if len(pow_tensor) == 0 or pow_tensor[0] != 2:
                continue
            data['op'] = 'mul'
            data['y'] = x_name
            self.dz_nx_graph.remove_edge(y_name, node_name)

            y_out = list(self.dz_nx_graph.out_edges(y_name))
            if len(y_out) == 0:
                remove_nodes.append(y_name)
        self.dz_nx_graph.remove_nodes_from(remove_nodes)


    def prelu_to_relu_optimization(self):
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'prelu':
                continue
            scales_name = data['scales']
            scales_node = self.dz_nx_graph.nodes[scales_name]
            if scales_node['op'] != 'constant':
                continue
            scales_tensor = self.tensor_dict[scales_name]
            if np.any(scales_tensor):
                continue
            data['op'] = 'relu'
            self.dz_nx_graph.remove_edge(scales_name, node_name)
            scales_out = list(self.dz_nx_graph.out_edges(scales_name))
            if len(scales_out) == 0:
                remove_nodes.append(scales_name)
            del data['scales']

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    # Updated and refactored
    def relu6_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'relu':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            if out_node['op'] != 'min':
                continue
            if out_node['x'] == node_name:
                other_param = 'y'
            elif out_node['y'] == node_name:
                other_param = 'x'
            else:
                raise ValueError(
                    "Node %s does not exist as an input to the min node %s" % (node_name, out_name))

            other_node = self.dz_nx_graph.nodes[out_node[other_param]]
            if other_node['op'] != 'constant' or \
                    other_node['output_shape'] != [1] or \
                    self.tensor_dict[out_node[other_param]][0] != 6.0:
                continue
            self.dz_nx_graph.nodes[node_name]['op'] = 'relu6'
            const_edges = list(
                self.dz_nx_graph.out_edges(out_node[other_param]))
            if len(const_edges) == 1:
                remove_nodes.append(out_node[other_param])

            remove_nodes.append(out_name)
            self.relabeled_names[out_name] = node_name
            self.rewire_out_edges(out_name, node_name)

            if out_name in self.orig_outputs:
                relabel_nodes[node_name] = out_name

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def rsqrt_eps_optimization(self):
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'max':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue

            to_remove = None
            if data['x'] in self.dz_nx_graph.node:
                x_node = self.dz_nx_graph.nodes[data['x']]
                if x_node['op'] == 'constant' and x_node['output_shape'] == [1]:
                    to_remove = data['x']
                    to_keep = data['y']
                    eps_value = self.tensor_dict[data['x']][0]
            if data['y'] in self.dz_nx_graph.node:
                y_node = self.dz_nx_graph.nodes[data['y']]
                if y_node['op'] == 'constant' and y_node['output_shape'] == [1]:
                    to_remove = data['y']
                    to_keep = data['x']
                    eps_value = self.tensor_dict[data['y']][0]
            if to_remove is None:
                continue
            out_node = out_edges[0][1]
            if self.dz_nx_graph.nodes[out_node]['op'] == 'rsqrt' and \
                    data['y'] == to_remove:
                remove_nodes.append(to_remove)
                self.dz_nx_graph.nodes[out_node]['epsilon'] = eps_value
                self.dz_nx_graph.nodes[out_node]['x'] = to_keep
                self.dz_nx_graph.add_edge(to_keep, out_node)
                remove_nodes.append(node_name)

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    # Updated and refactored
    def matmul_batchnorm_folding_optimization(self):
        add_nodes = []
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'matmul':
                continue
            out_edges1 = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges1) != 1:
                continue
            out_node1 = out_edges1[0][1]
            if self.dz_nx_graph.nodes[out_node1]['op'] != 'reshape':
                continue
            out_edges2 = list(
                self.dz_nx_graph.out_edges(out_node1))
            if len(out_edges2) != 1:
                continue
            out_node2 = out_edges2[0][1]
            if self.dz_nx_graph.nodes[out_node2]['op'] != 'batch_normalization':
                continue
            bn_node = self.dz_nx_graph.nodes[out_node2]
            weight_tensor = self.tensor_dict[data['B']]
            mean_tensor = self.tensor_dict[bn_node['mean']]
            var_tensor = self.tensor_dict[bn_node['variance']]
            scale_tensor = self.tensor_dict[bn_node['scale']]
            offset_tensor = self.tensor_dict[bn_node['offset']]
            eps = self.tensor_dict[bn_node['epsilon']]

            out_edges3 = list(
                self.dz_nx_graph.out_edges(out_node2))
            if len(out_edges3) != 1:
                continue
            out_node3 = out_edges3[0][1]
            if self.dz_nx_graph.nodes[out_node3]['op'] != 'reshape':
                continue
            remove_nodes.append(out_node1)
            remove_nodes.append(out_node2)
            remove_nodes.append(bn_node['mean'])
            remove_nodes.append(
                bn_node['variance'])
            remove_nodes.append(bn_node['scale'])
            remove_nodes.append(bn_node['offset'])
            remove_nodes.append(bn_node['epsilon'])
            add_tensor = np.add(var_tensor, eps)
            sqrt_tensor = np.sqrt(add_tensor)
            div_tensor = np.divide(
                scale_tensor, sqrt_tensor)
            bn_tensor = np.diag(div_tensor)
            weight_tensor = np.matmul(
                weight_tensor, bn_tensor)
            self.tensor_dict[data['B']
            ] = weight_tensor

            mul_tensor = np.multiply(
                scale_tensor, np.divide(mean_tensor, sqrt_tensor))
            bias_tensor = np.subtract(
                offset_tensor, mul_tensor)

            bias_name = node_name + '_bias'
            add_nodes.append([bias_name,
                              list(bias_tensor.shape), out_node3])
            self.tensor_dict[bias_name] = bias_tensor

            node_3 = self.dz_nx_graph.nodes[out_node3]
            node_3['op'] = 'add'
            node_3['x'] = node_name
            node_3['y'] = bias_name
            del node_3['shape']
            del node_3['input']
            self.dz_nx_graph.add_edge(
                node_name, out_node3)

        for node in add_nodes:
            self.dz_nx_graph.add_node(
                node[0], op='constant', shape=node[1], output_shape=node[1])
            self.dz_nx_graph.add_edge(node[0], node[2])

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    def conv_mul_fold_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            if 'datatype' in data and data['datatype'] != np.float32:
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            filt_out_edges = list(
                self.dz_nx_graph.out_edges(data['filter']))
            if len(filt_out_edges) != 1:
                continue
            out_node = out_edges[0][1]
            if self.dz_nx_graph.nodes[out_node]['op'] != 'mul':
                continue
            mul_node = self.dz_nx_graph.nodes[out_node]
            if mul_node['x'] == node_name:
                mul_name = mul_node['y']
            else:
                mul_name = mul_node['x']
            if self.dz_nx_graph.nodes[mul_name]['op'] != 'constant':
                continue
            mul_tensor = self.tensor_dict[mul_name]
            if mul_tensor.shape[0] != data['output_shape'][3]:
                continue

            filter_tensor = self.tensor_dict[data['filter']]
            bn_tensor = np.diag(mul_tensor)
            filt_shape = filter_tensor.shape
            if data['groups'] == 1:
                if self.in_format == 'nhwc':
                    filter_tensor = np.reshape(
                        filter_tensor, [-1, filt_shape[3]])
                else:
                    filter_tensor = np.reshape(
                        filter_tensor, [-1, filt_shape[0]])
            else:
                if self.in_format == 'nhwc':
                    filter_tensor = np.reshape(
                        filter_tensor, [-1, filt_shape[2]])
                else:
                    filter_tensor = np.reshape(
                        filter_tensor, [-1, filt_shape[0]])
            filter_tensor = np.matmul(filter_tensor, bn_tensor)
            filter_tensor = np.reshape(filter_tensor, filt_shape)
            self.tensor_dict[data['filter']] = filter_tensor
            if len(list(self.dz_nx_graph.out_edges(mul_name))) == 1:
                remove_nodes.append(mul_name)

            remove_nodes.append(out_node)
            self.rewire_out_edges(out_node, node_name)
            if out_node[:6] in self.orig_outputs:
                relabel_nodes[node_name] = out_node

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    # Updated and refactored
    def conv_add_bias_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            if 'bias' not in data:
                continue
            if data['bias'] == 0.0:
                continue
            bias_out_edges = list(self.dz_nx_graph.out_edges(data['bias']))
            if len(bias_out_edges) != 1:
                continue
            if 'datatype' in data and data['datatype'] != np.float32:
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            if out_node['op'] != 'add':
                continue
            if out_node['x'] == node_name:
                bias_name = out_node['y']
            elif out_node['y'] == node_name:
                bias_name = out_node['x']
            else:
                raise ValueError(
                    "Node %s does not exist as an input to the add node %s" % (node_name, out_name))

            if self.dz_nx_graph.nodes[bias_name]['op'] != 'constant':
                continue
            bias_tensor = self.tensor_dict[bias_name]
            if data['bias'] == 0.0 or 'bias' not in data:
                data['bias'] = bias_name
                self.dz_nx_graph.add_edge(bias_name, node_name)
            else:
                orig_bias = self.tensor_dict[data['bias']]
                bias_tensor = np.add(orig_bias, bias_tensor)
                self.tensor_dict[data['bias']] = bias_tensor
                bias_edges = self.dz_nx_graph.out_edges(bias_name)
                if len(bias_edges) == 1:
                    remove_nodes.append(bias_name)

            remove_nodes.append(out_name)
            self.relabeled_names[out_name] = node_name
            self.rewire_out_edges(out_name, node_name)

            if out_name in self.orig_outputs:
                relabel_nodes[node_name] = out_name

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def fold_padding_optimization(self):
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'pad':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            if 'head' not in out_node or 'tail' not in out_node:
                continue
            
            for i in range(len(out_node['head'])):
                out_node['head'][i] += data['head'][i]
            for i in range(len(out_node['tail'])):
                out_node['tail'][i] += data['tail'][i]
            remove_nodes.append(node_name)
            self.rewire_out_edges(node_name, data['input'])

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    # Updated and refactored
    def conv_batchnorm_folding_optimization(self):
        add_nodes = []
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            if data['output_shape'][1] != data['output_shape'][2]:
                continue
            filt_out_edges = list(
                self.dz_nx_graph.out_edges(data['filter']))
            if len(filt_out_edges) != 1:
                continue
            out_name = out_edges[0][1]
            if self.dz_nx_graph.nodes[out_name]['op'] != 'batch_normalization':
                continue
            bn_node = self.dz_nx_graph.nodes[out_name]
            filter_tensor = self.tensor_dict[data['filter']]
            mean_tensor = self.tensor_dict[bn_node['mean']]
            remove_nodes.append(bn_node['mean'])
            var_tensor = self.tensor_dict[bn_node['variance']]
            remove_nodes.append(bn_node['variance'])
            scale_tensor = self.tensor_dict[bn_node['scale']]
            remove_nodes.append(bn_node['scale'])
            offset_tensor = self.tensor_dict[bn_node['offset']]
            remove_nodes.append(bn_node['offset'])
            eps = self.tensor_dict[bn_node['epsilon']]
            remove_nodes.append(bn_node['epsilon'])

            add_tensor = np.add(var_tensor, eps)
            sqrt_tensor = np.sqrt(add_tensor)
            div_tensor = np.divide(scale_tensor, sqrt_tensor)
            bn_tensor = np.diag(div_tensor)

            filt_shape = filter_tensor.shape
            if data['groups'] == 1:
                filter_tensor = np.reshape(
                    filter_tensor, [-1, filt_shape[3]])
            else:
                filter_tensor = np.reshape(
                    filter_tensor, [-1, filt_shape[2]])

            filter_tensor = np.matmul(filter_tensor, bn_tensor)
            filter_tensor = np.reshape(filter_tensor, filt_shape)
            self.tensor_dict[data['filter']] = filter_tensor

            mul_tensor = np.multiply(
                scale_tensor, np.divide(mean_tensor, sqrt_tensor))
            bias_tensor = np.subtract(offset_tensor, mul_tensor)

            if data['bias'] == 0.0:
                bias_name = node_name + '_bias'
                add_nodes.append(
                    [bias_name, list(bias_tensor.shape), node_name])
                data['bias'] = bias_name
                self.tensor_dict[data['bias']] = bias_tensor
            else:
                orig_bias = self.tensor_dict[data['bias']]
                bias_tensor = np.add(orig_bias, bias_tensor)
                self.tensor_dict[data['bias']] = bias_tensor

            remove_nodes.append(out_name)
            self.relabeled_names[out_name] = node_name
            self.rewire_out_edges(out_name, node_name)

            if out_name in self.orig_outputs:
                relabel_nodes[node_name] = out_name
                for add_node in add_nodes:
                    if add_node[2] == node_name:
                        add_node[2] = out_name

        for node in add_nodes:
            self.dz_nx_graph.add_node(
                node[0], op='constant', shape=node[1], output_shape=node[1])
            self.dz_nx_graph.add_edge(node[0], node[2])

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def panel_shuffle_optimization(self):
        panel_sizes = [4]
        if self.panel_shuffle == 'armv7':
            panel_sizes.append(8)
        elif self.panel_shuffle == 'armv8':
            panel_sizes.append(8)
            panel_sizes.append(16)
        elif self.panel_shuffle == 'avx2':
            panel_sizes.append(8)
            panel_sizes.append(16)
            panel_sizes.append(32)

        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'constant':
                continue

            port = next(iter(self.dz_nx_graph.out_edges(node_name)))
            layer = self.dz_nx_graph.nodes[port[1]]

            if layer['op'] != 'conv' or layer['filter'] != node_name:
                continue

            if len(data['output_shape']) != 4:
                print('Cannot panel optimize constant %s for layer %s which has shape %s' %
                      (node_name, layer, data['output_shape']))
                continue

            panel = 0
            for size in reversed(panel_sizes):
                if data['output_shape'][3] % size == 0:
                    panel = size
                    break

            if panel == 0:
                continue

            const_tensor = self.tensor_dict[node_name].copy()
            aux_shape = [1, data['output_shape'][0] * data['output_shape'][1] * data['output_shape'][2],
                         int(data['output_shape'][3] / panel), panel]
            const_tensor = const_tensor.reshape(aux_shape)
            const_tensor = const_tensor.transpose([0, 2, 1, 3])
            const_tensor = const_tensor.reshape(data['output_shape'])
            self.tensor_dict[node_name] = const_tensor
            data['panel'] = panel

    def conv_add_zero_bias(self):
        add_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] in ['conv', 'transpose_conv'] and \
                    ('bias' not in data or not isinstance(data['bias'], str)):
                add_nodes.append(
                    (node_name + '_zero_bias', data['output_shape'][-1], node_name, data['datatype']))
                data['bias'] = node_name + '_zero_bias'

        for node in add_nodes:
            self.dz_nx_graph.add_node(node[0], op='constant',
                                      shape=[node[1]], output_shape=[node[1]], datatype=node[3])
            self.dz_nx_graph.add_edge(node[0], node[2])
            if node[3] in [np.int8, np.uint8]:
                conv_node = self.dz_nx_graph.nodes[node[2]]
                input_node = self.dz_nx_graph.nodes[conv_node['input']]
                filter_node = self.dz_nx_graph.nodes[conv_node['filter']]
                scales = input_node['quant_scale'] * filter_node['quant_scale']
                zero_point = np.zeros([len(scales)]).astype(np.int32)
                self.dz_nx_graph.nodes[node[0]]['quant_scale'] = scales
                self.dz_nx_graph.nodes[node[0]]['zero_point'] = zero_point
                self.dz_nx_graph.nodes[node[0]]['quant_axis'] = 0
                self.tensor_dict[node[0]] = np.zeros([node[1]]).astype(np.int32)
            else:
                self.tensor_dict[node[0]] = np.zeros([node[1]]).astype(node[3])

    # Updated and refactored
    def conv_activation_folding_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            if 'activation' in data and data['activation'] != 'linear':
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            if 'datatype' in data and data['datatype'] in [np.int8, np.uint8] and \
                    out_node['op'] in ['tanh', 'sigmoid']:
                continue
            if out_node['op'] in ['relu', 'tanh', 'sigmoid', 'relu6']:
                data['activation'] = out_node['op']
                remove_nodes.append(out_name)
                self.relabeled_names[out_name] = node_name
                self.rewire_out_edges(out_name, node_name)
                if out_name in self.orig_outputs:
                    relabel_nodes[node_name] = out_name

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def transpose_conv_rotation_optimization(self):
        # hwio
        # HWio HW means rotate 180 degrees
        rotated = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'transpose_conv':
                continue
            if data['filter'] in rotated:
                continue
            filt_name = data['filter']
            filt_tensor = self.tensor_dict[filt_name].copy()
            dims = filt_tensor.shape
            for i in range(dims[2]):
                for o in range(dims[3]):
                    filt_tensor[:, :, i, o] = np.rot90(np.rot90(filt_tensor[:, :, i, o]))
            self.tensor_dict[filt_name] = filt_tensor
            rotated.append(filt_name)

    # Updated and refactored
    def batchnorm_removal_optimization(self):
        add_nodes = []
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'batch_normalization':
                continue
            data['op'] = 'mul'
            data['x'] = data['input']
            del data['input']
            mean_tensor = self.tensor_dict[data['mean']]
            remove_nodes.append(data['mean'])
            del data['mean']
            var_tensor = self.tensor_dict[data['variance']]
            remove_nodes.append(data['variance'])
            del data['variance']
            scale_tensor = self.tensor_dict[data['scale']]
            data['y'] = data['scale']
            del data['scale']
            offset_tensor = self.tensor_dict[data['offset']]
            bias_name = data['offset']
            del data['offset']
            eps = self.tensor_dict[data['epsilon']]
            remove_nodes.append(data['epsilon'])
            del data['epsilon']

            add_tensor = np.add(var_tensor, eps)
            sqrt_tensor = np.sqrt(add_tensor)
            div_tensor = np.divide(scale_tensor, sqrt_tensor)
            mul_tensor = np.multiply(div_tensor, mean_tensor)
            bias_tensor = np.subtract(offset_tensor, mul_tensor)

            self.tensor_dict[data['y']] = div_tensor
            self.tensor_dict[bias_name] = bias_tensor

            add_nodes.append([node_name + '_add', 'add',
                              data['output_shape'], node_name, bias_name])
            self.relabeled_names[node_name] = node_name + '_add'

            bn_edges = list(self.dz_nx_graph.out_edges(node_name))
            for edge in bn_edges:
                self.dz_nx_graph.add_edge(node_name, edge[1])
                for key, val in self.dz_nx_graph.nodes[edge[1]].items():
                    if key == 'values':
                        new_val = []
                        for conc_name in val:
                            if conc_name == node_name:
                                new_val.append(node_name + '_add')
                            else:
                                new_val.append(conc_name)
                        self.dz_nx_graph.nodes[edge[1]][key] = new_val
                    if type(val) == str and val == node_name:
                        self.dz_nx_graph.nodes[edge[1]
                        ][key] = node_name + '_add'

        for node in add_nodes:
            if node[1] == 'add':
                self.dz_nx_graph.add_node(node[0], op=node[1], output_shape=node[2],
                                          x=node[3], y=node[4])
                self.dz_nx_graph.add_edge(node[3], node[0])
                self.dz_nx_graph.add_edge(node[4], node[0])

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    def conv_padding_slice_optimization(self):
        add_nodes = []
        add_edges = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if not (data['op'] == 'conv' and \
                    (data['output_shape'][3] % 4 != 0 and data['output_shape'][3] > 4)):
                continue
            filt_node = self.dz_nx_graph.nodes[data['filter']]
            orig_shape = filt_node['output_shape']
            orig_tensor = self.tensor_dict[data['filter']]
            new_shape = orig_shape[:]
            new_shape[3] = new_shape[3] + (4 - (new_shape[3] % 4))
            new_filt_tensor = np.zeros(new_shape, dtype=np.float32)
            new_filt_tensor[:orig_shape[0], :orig_shape[1],
            :orig_shape[2], :orig_shape[3]] = orig_tensor
            self.tensor_dict[data['filter']] = new_filt_tensor
            filt_node['output_shape'] = new_shape[:]
            new_channels = new_shape[3]
            if 'bias' in data:
                bias_node = self.dz_nx_graph.nodes[data['bias']]
                orig_shape = bias_node['output_shape']
                orig_tensor = self.tensor_dict[data['bias']]
                new_shape = [new_channels]
                new_bias_tensor = np.zeros(new_shape, dtype=np.float32)
                new_bias_tensor[:orig_shape[0]] = orig_tensor
                self.tensor_dict[data['bias']] = new_bias_tensor
                bias_node['output_shape'] = new_shape[:]
            conv_orig_shape = data['output_shape'][:]
            data['output_shape'][3] = new_channels

            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) == 1 and 'pool' in self.dz_nx_graph.nodes[out_edges[0][1]]['op']:
                pool_name = out_edges[0][1]
                pool_node = self.dz_nx_graph.nodes[pool_name]
                pool_node['output_shape'][3] = new_channels

                pool_out_edges = list(
                    self.dz_nx_graph.out_edges(pool_name))
                add_edges.append((pool_name, node_name + '_slice'))
                for edge in pool_out_edges:
                    add_edges.append((node_name + '_slice', edge[1]))
                    self.dz_nx_graph.remove_edge(edge[0], edge[1])
                    out_node_name = edge[1]
                    out_node = self.dz_nx_graph.nodes[out_node_name]
                    for key, val in out_node.items():
                        if val == pool_name:
                            out_node[key] = node_name + '_slice'
                            add_edges.append(
                                (node_name + '_slice', out_node_name))

                add_nodes.append([node_name + '_slice', pool_name, [0, 1, 2, 3],
                                  [0, 0, 0, 0], [
                                      0, 0, 0, conv_orig_shape[3]],
                                  conv_orig_shape[:]])
            else:
                add_edges.append((node_name, node_name + '_slice'))
                for edge in out_edges:
                    add_edges.append((node_name + '_slice', edge[1]))
                    self.dz_nx_graph.remove_edge(edge[0], edge[1])
                    out_node_name = edge[1]
                    out_node = self.dz_nx_graph.nodes[out_node_name]

                    if out_node['op'] == 'concat':
                        for i in range(len(out_node['values'])):
                            if out_node['values'][i] == node_name:
                                out_node['values'][i] = node_name + \
                                                        '_slice'
                                break
                    else:
                        for key, val in out_node.items():
                            if val == node_name:
                                out_node[key] = node_name + '_slice'
                                add_edges.append(
                                    (node_name + '_slice', out_node_name))

                add_nodes.append([node_name + '_slice', node_name, [0, 1, 2, 3],
                                  [0, 0, 0, 0], [
                                      0, 0, 0, conv_orig_shape[3]],
                                  conv_orig_shape[:]])

        for node in add_nodes:
            self.dz_nx_graph.add_node(node[0], op='slice', input=node[1],
                                      axes=node[2], begin=node[3], end=node[4],
                                      output_shape=node[5])

        for edge in add_edges:
            self.dz_nx_graph.add_edge(edge[0], edge[1])

    def matmul_add_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        add_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'matmul':
                continue
            if data['transposeA'] != False:
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]

            if data['transposeB'] == True:
                data['op'] = 'linear'
            else:
                data['op'] = 'dense'

            if out_node['op'] != 'add':
                continue
            if out_node['x'] == node_name:
                bias_name = out_node['y']
            elif out_node['y'] == node_name:
                bias_name = out_node['x']
            else:
                raise ValueError(
                    "Node %s does not exist as an input to the add node %s" % (node_name, out_name))

            if self.dz_nx_graph.nodes[bias_name]['op'] != 'constant':
                continue

            if data['datatype'] == np.dtype('float32'):
                data['bias'] = bias_name
                self.dz_nx_graph.add_edge(bias_name, node_name)
                remove_nodes.append(out_name)
                self.rewire_out_edges(out_name, node_name)
                if out_name in self.orig_outputs:
                    relabel_nodes[node_name] = out_name
            else:
                bias_node = self.dz_nx_graph.nodes[bias_name]
                new_bias_tensor = np.asarray([0] * len(self.tensor_dict[bias_name])).astype(np.int32)
                new_quant_scale = self.dz_nx_graph.nodes[data['A']]['quant_scale'] * \
                                  self.dz_nx_graph.nodes[data['B']]['quant_scale']
                new_zero_point = np.asarray([0] * len(new_quant_scale)).astype(np.int32)
                add_nodes.append({'name': node_name + '_dv_quant_dense_bias',
                                  'op': 'constant',
                                  'datatype': np.dtype('int32'),
                                  'format': 'none',
                                  'output_shape': bias_node['output_shape'][:],
                                  'np_tensor': new_bias_tensor,
                                  'quant_scale': new_quant_scale,
                                  'zero_point': new_zero_point,
                                  'quant_axis': 0,
                                  'out_node': node_name})
                data['bias'] = node_name + '_dv_quant_dense_bias'

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        for node in add_nodes:
            self.dz_nx_graph.add_node(node['name'],
                                      op=node['op'],
                                      datatype=node['datatype'],
                                      format=node['format'],
                                      output_shape=node['output_shape'],
                                      quant_scale=node['quant_scale'],
                                      zero_point=node['zero_point'],
                                      quant_axis=node['quant_axis'])
            self.tensor_dict[node['name']] = node['np_tensor']
            self.dz_nx_graph.add_edge(node['name'], node['out_node'])
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def matmul_add_zero_bias(self):
        add_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] in ['dense', 'linear'] and \
                    ('bias' not in data or not isinstance(data['bias'], str)):
                add_nodes.append(
                    (node_name + '_zero_bias', data['output_shape'][-1], node_name, data['datatype']))
                data['bias'] = node_name + '_zero_bias'

        for node in add_nodes:
            self.dz_nx_graph.add_node(node[0], op='constant',
                                      shape=[node[1]], output_shape=[node[1]], datatype=node[3])
            self.dz_nx_graph.add_edge(node[0], node[2])
            if node[3] in [np.int8, np.uint8]:
                matmul_node = self.dz_nx_graph.nodes[node[2]]
                a_node = self.dz_nx_graph.nodes[matmul_node['A']]
                b_node = self.dz_nx_graph.nodes[matmul_node['B']]
                scales = a_node['quant_scale'] * b_node['quant_scale']
                zero_point = np.zeros([len(scales)]).astype(np.int32)
                self.dz_nx_graph.nodes[node[0]]['quant_scale'] = scales
                self.dz_nx_graph.nodes[node[0]]['zero_point'] = zero_point
                self.dz_nx_graph.nodes[node[0]]['quant_axis'] = 0
                self.tensor_dict[node[0]] = np.zeros([node[1]]).astype(np.int32)
            else:
                self.tensor_dict[node[0]] = np.zeros([node[1]]).astype(node[3])

    def matmul_activation_folding_optimization(self):
        remove_nodes = []
        relabel_nodes = {}
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'linear' and data['op'] != 'dense':
                continue
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            if len(out_edges) != 1:
                continue
            if 'activation' in data and data['activation'] != 'linear':
                continue
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            if out_node['op'] in ['relu', 'tanh', 'sigmoid', 'relu6']:
                data['activation'] = out_node['op']

                remove_nodes.append(out_name)
                self.relabeled_names[out_name] = node_name
                self.rewire_out_edges(out_name, node_name)
                if out_name in self.orig_outputs:
                    relabel_nodes[node_name] = out_name

        self.dz_nx_graph.remove_nodes_from(remove_nodes)
        if relabel_nodes:
            nx.relabel_nodes(self.dz_nx_graph, relabel_nodes, copy=False)

    def squish_constants_optimization(self):
        skip_filters = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'conv':
                continue
            if data['filter'] not in skip_filters:
                skip_filters.append(data['filter'])

        for node_name, data in self.dz_nx_graph.nodes(data=True):
            output_shape = data['output_shape']
            if data['op'] != 'constant' or \
                    len(output_shape) == 1 or \
                    node_name in skip_filters:
                continue
            non_one_count = 0
            non_one_size = 1
            for dim in output_shape:
                if dim != 1:
                    non_one_size = dim
                    non_one_count += 1
            if non_one_count > 1:
                continue

            valid_out_ops = True
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            for edge in out_edges:
                out_name = edge[1]
                out_node = self.dz_nx_graph.nodes[out_name]
                if out_node['op'] not in ['add', 'mul', 'sub', 'div']:
                    valid_out_ops = False
                    break
            if not valid_out_ops:
                continue

            new_tensor = self.tensor_dict[node_name].copy()
            new_shape = [non_one_size]
            new_tensor = np.reshape(new_tensor, new_shape)
            self.tensor_dict[node_name] = new_tensor
            data['output_shape'] = new_shape

    def linear_to_dense_optimization(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'linear':
                continue
            b_name = data['B']
            b_node = self.dz_nx_graph.nodes[b_name]
            if b_node['op'] != 'constant' or (len(list(self.dz_nx_graph.out_edges(b_name))) > 1):
                print("WARNING: Currently unable to modify linear to dense "
                      "for filters that are shared or are not constants.")
            else:
                b_tensor = self.tensor_dict[b_name]
                b_tensor = np.transpose(b_tensor, [1, 0])
                self.tensor_dict[b_name] = b_tensor
                b_node['output_shape'] = [b_node['output_shape'][1], b_node['output_shape'][0]]
                data['op'] = 'dense'

    def mean_reduce_to_avg_pool_optimization(self):
        add_reshape_node = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'mean_reduce':
                continue
            if len(data['output_shape']) != 2:
                continue
            if data['axes'] != [1, 2]:
                continue
            if len(list(self.dz_nx_graph.out_edges(node_name))) == 0:
                print("WARNING: Unable to change mean_reduce to avg_pool \
                    for an output layer.")
                continue

            data['op'] = 'avg_pool'
            del data['axes']
            data['stride'] = [1, 1, 1, 1]
            data['dilation'] = [1, 1, 1, 1]
            input_shape = self.dz_nx_graph.nodes[data['input']]['output_shape']
            data['size'] = [1, input_shape[1], input_shape[2], 1]
            data['output_shape'] = [input_shape[0], 1, 1, input_shape[3]]
            add_reshape_node.append(node_name)
        for name in add_reshape_node:
            avg_node = self.dz_nx_graph.nodes[name]
            new_name = name + '_dv_avg_reshape'
            self.dz_nx_graph.add_node(new_name,
                                      op='reshape',
                                      input=name,
                                      output_shape=[avg_node['output_shape'][0], avg_node['output_shape'][3]])
            if 'datatype' in avg_node:
                self.dz_nx_graph.nodes[new_name]['datatype'] = avg_node['datatype']
            if 'quant_scale' in avg_node:
                self.dz_nx_graph.nodes[new_name]['quant_scale'] = avg_node['quant_scale']
                self.dz_nx_graph.nodes[new_name]['zero_point'] = avg_node['zero_point']
                self.dz_nx_graph.nodes[new_name]['quant_axis'] = avg_node['quant_axis']

            self.rewire_out_edges(name, new_name)
            self.dz_nx_graph.add_edge(name, new_name)

    def quantize_pool(self):
        remove_nodes = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] not in ['max_pool', 'avg_pool']:
                continue
            in_edges = list(self.dz_nx_graph.out_edges(data['input']))
            out_edges = list(self.dz_nx_graph.out_edges(node_name))
            
            if len(out_edges) != 1:
                continue
            in_name = in_edges[0][0]
            in_node = self.dz_nx_graph.nodes[in_name]
            out_name = out_edges[0][1]
            out_node = self.dz_nx_graph.nodes[out_name]
            in_in_name = None
            in_in_node = None
            out_out_name = None
            out_out_node = None

            
            if in_node['op'] not in ['dequant', 'reshape']:
                continue
            if out_node['op'] not in ['quant', 'reshape']:
                continue

            if in_node['op'] == 'reshape':
                in_in_name = in_node['input']
                in_in_node = self.dz_nx_graph.nodes[in_in_name]
                if in_in_node['op'] != 'dequant':
                    continue
                if len(in_edges) != 1:
                    continue

            if out_node['op'] == 'reshape':
                out_out_edges = list(self.dz_nx_graph.out_edges(out_name))
                if len(out_out_edges) != 1:
                    continue
                out_out_name = out_out_edges[0][1]
                out_out_node = self.dz_nx_graph.nodes[out_out_name]
                if out_out_node['op'] != 'quant':
                    continue

            if out_node['op'] == 'quant':
                data['quant_scale'] = out_node['quant_scale'].copy()
                data['zero_point'] = out_node['zero_point'].copy()
                data['quant_axis'] = out_node['quant_axis']
                data['datatype'] = out_node['datatype']
                self.rewire_out_edges(out_name, node_name)
                remove_nodes.append(out_name)
            else:
                data['quant_scale'] = out_out_node['quant_scale'].copy()
                data['zero_point'] = out_out_node['zero_point'].copy()
                data['quant_axis'] = out_out_node['quant_axis']
                data['datatype'] = out_out_node['datatype']
                out_node['quant_scale'] = out_out_node['quant_scale'].copy()
                out_node['zero_point'] = out_out_node['zero_point'].copy()
                out_node['quant_axis'] = out_out_node['quant_axis']
                out_node['datatype'] = out_out_node['datatype']
                self.rewire_out_edges(out_out_name, out_name)
                remove_nodes.append(out_out_name)

            if in_node['op'] == 'dequant':
                data['input'] = in_node['x']
                self.dz_nx_graph.add_edge(in_node['x'], node_name)
                if len(in_edges) == 1:
                    remove_nodes.append(in_name)
                else:
                    self.dz_nx_graph.remove_edge(in_name, node_name)
            else:
                in_node['input'] = in_in_node['x']
                in_node['quant_scale'] = in_in_node['quant_scale'].copy()
                in_node['zero_point'] = in_in_node['zero_point'].copy()
                in_node['quant_axis'] = in_in_node['quant_axis']
                in_node['datatype'] = in_in_node['datatype']
                self.dz_nx_graph.add_edge(in_in_node['x'], in_name)
                if len(list(self.dz_nx_graph.out_edges(in_in_name))) == 1:
                    remove_nodes.append(in_in_name)
                else:
                    self.dz_nx_graph.remove_edge(in_in_name, in_name)

        self.dz_nx_graph.remove_nodes_from(remove_nodes)

    def concat_to_resize_optimization_form1(self):
        concat_replaced = True
        while concat_replaced:
            concat_replaced = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] != 'concat':
                    continue
                if len(data['output_shape']) != 4:
                    continue
                if len(data['values']) != 2:
                    continue
                if data['values'][0] != data['values'][1]:
                    continue
                if data['axis'] != 3:
                    continue
                in_node = self.dz_nx_graph.nodes[data['values'][0]]
                out_edges1 = list(self.dz_nx_graph.out_edges(node_name))
                if len(out_edges1) != 1:
                    continue
                node_name2 = out_edges1[0][1]
                node2 = self.dz_nx_graph.nodes[node_name2]
                if node2['op'] != 'concat':
                    continue
                if len(node2['values']) != 2:
                    continue
                if node2['values'][0] != node2['values'][1]:
                    continue
                if node2['axis'] != 2:
                    continue
                out_edges2 = list(self.dz_nx_graph.out_edges(node_name2))
                if len(out_edges2) != 1:
                    continue
                node_name3 = out_edges2[0][1]
                node3 = self.dz_nx_graph.nodes[node_name3]
                if node3['op'] != 'reshape':
                    continue
                if node3['output_shape'][1] != 2 * in_node['output_shape'][1] or \
                    node3['output_shape'][2] != 2 * in_node['output_shape'][2] or \
                    node3['output_shape'][3] != in_node['output_shape'][3] or \
                    node3['output_shape'][0] != in_node['output_shape'][0]:
                    continue
                node3['op'] = 'resize'
                node3['input'] = data['values'][0]
                node3['mode'] = 0
                node3['align_corners'] = False
                node3['half_pixel_centers'] = False
                self.dz_nx_graph.add_edge(data['values'][0], node_name3)
                self.dz_nx_graph.remove_node(node_name)
                self.dz_nx_graph.remove_node(node_name2)
                concat_replaced = True
                break

    def concat_to_resize_optimization_form2(self):
        concat_replaced = True
        while concat_replaced:
            concat_replaced = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] != 'reshape':
                    continue
                input_name = data['input']
                input_node = self.dz_nx_graph.nodes[input_name]
                input_shape = input_node['output_shape']
                if len(input_shape) != 4:
                    continue
                check_shape = input_node['output_shape'][:]
                check_shape.insert(3, 1)
                if data['output_shape'] != check_shape:
                    continue

                out_edges1 = list(self.dz_nx_graph.out_edges(node_name))
                if len(out_edges1) != 1:
                    continue
                node_name2 = out_edges1[0][1]
                node2 = self.dz_nx_graph.nodes[node_name2]
                if node2['op'] != 'concat':
                    continue
                if len(node2['values']) != 2:
                    continue
                if node2['values'][0] != node2['values'][1]:
                    continue
                if node2['axis'] != 3:
                    continue

                out_edges2 = list(self.dz_nx_graph.out_edges(node_name2))
                if len(out_edges2) != 1:
                    continue
                node_name3 = out_edges2[0][1]
                node3 = self.dz_nx_graph.nodes[node_name3]
                if data['op'] != 'reshape':
                    continue
                check_shape = node2['output_shape'][:]
                check_shape.insert(2, 1)
                if node3['output_shape'] != check_shape:
                    continue

                out_edges3 = list(self.dz_nx_graph.out_edges(node_name3))
                if len(out_edges1) != 1:
                    continue
                node_name4 = out_edges3[0][1]
                node4 = self.dz_nx_graph.nodes[node_name4]
                if node4['op'] != 'concat':
                    continue
                if len(node4['values']) != 2:
                    continue
                if node4['values'][0] != node4['values'][1]:
                    continue
                if node4['axis'] != 2:
                    continue
                out_edges4 = list(self.dz_nx_graph.out_edges(node_name4))
                if len(out_edges4) != 1:
                    continue
                node_name5 = out_edges4[0][1]
                node5 = self.dz_nx_graph.nodes[node_name5]
                if node5['op'] != 'reshape':
                    continue
                if node5['output_shape'][1] != 2 * input_shape[1] or \
                    node5['output_shape'][2] != 2 * input_shape[2] or \
                    node5['output_shape'][3] != input_shape[3] or \
                    node5['output_shape'][0] != input_shape[0]:
                    continue

                node5['op'] = 'resize'
                node5['input'] = input_name
                node5['mode'] = 0
                node5['align_corners'] = False
                node5['half_pixel_centers'] = False
                self.dz_nx_graph.add_edge(input_name, node_name5)
                self.dz_nx_graph.remove_node(node_name)
                self.dz_nx_graph.remove_node(node_name2)
                self.dz_nx_graph.remove_node(node_name3)
                self.dz_nx_graph.remove_node(node_name4)
                concat_replaced = True
                break

    def replace_transpose_reshape_optimization(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'transpose':
                continue
            changing_dims = []
            i = 0
            for axis in data['axes']:
                if axis != i:
                    changing_dims.append(i)
                i += 1
            
            output_shape = data['output_shape']
            non_one_count = 0
            for i in range(len(output_shape)):
                if i not in changing_dims:
                    continue
                dim = output_shape[i]
                if dim != 1:
                    non_one_count += 1
            if non_one_count > 1:
                continue

            del data['axes']
            data['op'] = 'reshape'

    def remove_additional_reshape_optimization(self):
        removed_layer = True
        while removed_layer:
            removed_layer = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] != 'reshape':
                    continue
                out_edges = list(self.dz_nx_graph.out_edges(node_name))
                if len(out_edges) != 1:
                    continue
                out_name = out_edges[0][1]
                out_node = self.dz_nx_graph.nodes[out_name]
                if out_node['op'] != 'reshape':
                    continue
                out_node['input'] = data['input']
                self.dz_nx_graph.add_edge(data['input'], out_name)
                self.dz_nx_graph.remove_node(node_name)
                removed_layer = True
                break

    def concat_n_split_optimization(self):
        N = 16
        conc_cont = True
        while conc_cont:
            conc_cont = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] != 'concat':
                    continue
                if len(data['values']) <= N:
                    continue
                conc_cont = True
                splits = []
                cur_split = []
                for val in data['values']:
                    cur_split.append(val)
                    if len(cur_split) == N:
                        splits.append(cur_split)
                        cur_split = []
                new_conc_vals = []
                for i in range(len(splits)):
                    split_name = node_name + '_split_' + str(i)
                    while split_name in self.dz_nx_graph.nodes:
                        split_name += '_split_' + str(i)
                    if len(splits[i]) > 1:
                        output_shape = self.dz_nx_graph.nodes[splits[i][0]]['output_shape'][:]
                        for j in range(1, len(splits[i])):
                            output_shape[data['axis']] += self.dz_nx_graph.nodes[splits[i][j]]['output_shape'][
                                data['axis']]
                        self.dz_nx_graph.add_node(split_name,
                                                  op='concat',
                                                  values=splits[i],
                                                  axis=data['axis'],
                                                  output_shape=output_shape)
                        if 'datatype' in data:
                            self.dz_nx_graph.nodes[split_name]['datatype'] = data['datatype']
                        if 'quant_scale' in data:
                            self.dz_nx_graph.nodes[split_name]['quant_scale'] = data['quant_scale']
                        if 'zero_point' in data:
                            self.dz_nx_graph.nodes[split_name]['zero_point'] = data['zero_point']
                        if 'quant_axis' in data:
                            self.dz_nx_graph.nodes[split_name]['quant_axis'] = data['quant_axis']
                        for j in range(0, len(splits[i])):
                            self.dz_nx_graph.add_edge(splits[i][j], split_name)
                            self.dz_nx_graph.remove_edge(splits[i][j], node_name)
                        new_conc_vals.append(split_name)
                        self.dz_nx_graph.add_edge(split_name, node_name)
                    else:
                        new_conc_vals.append(splits[i][0])
                data['values'] = new_conc_vals
                break

    def scale_zero_to_list(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if 'quant_scale' in data and not isinstance(data['quant_scale'], (np.ndarray, np.generic)):
                data['quant_scale'] = np.asarray([data['quant_scale']]).astype(np.float32)
            if 'zero_point' in data and not isinstance(data['zero_point'], (np.ndarray, np.generic)):
                data['zero_point'] = np.asarray([data['zero_point']]).astype(np.int64)

    def sigmoid_expansion_optimization(self):
        quant_sigmoid_exists = True
        while quant_sigmoid_exists:
            quant_sigmoid_exists = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] != 'sigmoid':
                    continue
                if 'quant_scale' not in data:
                    continue

                input_name = data['x']
                self.dz_nx_graph.remove_edge(input_name, node_name)
                dequant_name = node_name + '_dv_sig_expand_dequant'
                self.dz_nx_graph.add_node(dequant_name, op='dequant', x=input_name,
                                          datatype=np.dtype('float32'), output_shape=data['output_shape'][:])
                self.dz_nx_graph.add_edge(input_name, dequant_name)

                exp_name = node_name + '_dv_sig_expand_exp'
                self.dz_nx_graph.add_node(exp_name, op='exp', x=dequant_name,
                                          datatype=np.dtype('float32'), output_shape=data['output_shape'][:])
                self.dz_nx_graph.add_edge(dequant_name, exp_name)

                const_name = node_name + '_dv_sig_expand_one'
                self.dz_nx_graph.add_node(const_name, op='constant', datatype=np.dtype('float32'),
                                          output_shape=[1])
                self.tensor_dict[const_name] = np.asarray([1]).astype(np.float32)

                add_name = node_name + '_dv_sig_expand_add'
                self.dz_nx_graph.add_node(add_name, op='add', x=exp_name, y=const_name,
                                          datatype=np.dtype('float32'), output_shape=data['output_shape'][:])
                self.dz_nx_graph.add_edge(exp_name, add_name)
                self.dz_nx_graph.add_edge(const_name, add_name)

                div_name = node_name + '_dv_sig_expand_div'
                self.dz_nx_graph.add_node(div_name, op='div', x=exp_name, y=add_name,
                                          datatype=np.dtype('float32'), output_shape=data['output_shape'][:])
                self.dz_nx_graph.add_edge(exp_name, div_name)
                self.dz_nx_graph.add_edge(add_name, div_name)

                data['x'] = div_name
                data['op'] = 'quant'
                self.dz_nx_graph.add_edge(div_name, node_name)
                quant_sigmoid_exists = True
                break

    def quantize_dequant_ops_optimization(self):
        dequanted_op_exists = True
        while dequanted_op_exists:
            dequanted_op_exists = False
            for node_name, data in self.dz_nx_graph.nodes(data=True):
                if data['op'] not in ['exp']:
                    continue
                if data['datatype'] != np.dtype('float32'):
                    continue

                input_name = data['x']
                input_node = self.dz_nx_graph.nodes[input_name]
                if input_node['op'] != 'dequant':
                    continue

                out_edges = list(self.dz_nx_graph.out_edges(node_name))
                if len(out_edges) != 1:
                    continue
                out_name = out_edges[0][1]
                out_node = self.dz_nx_graph.nodes[out_name]
                if out_node['op'] != 'quant':
                    continue

                dequanted_op_exists = True
                data['datatype'] = out_node['datatype']
                data['quant_scale'] = out_node['quant_scale']
                data['zero_point'] = out_node['zero_point']
                data['quant_axis'] = out_node['quant_axis']
                data['x'] = input_node['x']
                self.dz_nx_graph.add_edge(data['x'], node_name)
                self.dz_nx_graph.remove_node(input_name)
                self.rewire_out_edges(out_name, node_name)
                self.dz_nx_graph.remove_node(out_name)
                if out_name in self.orig_outputs:
                    self.orig_outputs[self.orig_outputs.index(out_name)] = node_name
                break

    def adjust_transpose_conv_filter_datatype(self):
        if self.transpose_conv_filter_datatype != 'uint8':
            print("Cannot adjust transpose convolution filter to "
                  "%s currently." % self.transpose_conv_filter_datatype)
            return
        modified = []
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if data['op'] != 'transpose_conv':
                continue
            filt_name = data['filter']
            filt_node = self.dz_nx_graph.nodes[filt_name]
            if filt_name in modified:
                continue
            if filt_node['op'] != 'constant':
                continue
            if filt_node['datatype'] != np.dtype('int8'):
                continue

            new_tensor = self.tensor_dict[filt_name].copy()
            new_tensor = (new_tensor.astype(np.int32) + 128).astype(np.uint8)
            self.tensor_dict[filt_name] = new_tensor
            filt_node['datatype'] = np.dtype('uint8')
            filt_node['zero_point'] = filt_node['zero_point'] + 128
            modified.append(filt_name)

    def adjust_input_type(self):
        to_modify = self.orig_inputs[:]
        while len(to_modify) > 0:
            name = to_modify[0]
            data = self.dz_nx_graph.nodes[name]
            if (self.input_type == 'float32' and data['datatype'] == np.dtype('float32')) or \
                    (self.input_type == 'int8' and data['datatype'] == np.dtype('int8')) or \
                    (self.input_type == 'uint8' and data['datatype'] == np.dtype('uint8')):
                to_modify.pop(0)
                continue
            if data['datatype'] == np.dtype('float32'):
                out_edges = list(self.dz_nx_graph.out_edges(name))
                out_name = out_edges[0][1]
                out_node = self.dz_nx_graph.nodes[out_name]
                if out_node['op'] != 'quant':
                    data['quant_scale'] = np.asarray([0.0078125]).astype(np.float32)
                    data['quant_axis'] = 0
                    if self.input_type == 'int8':
                        data['datatype'] = np.dtype('int8')
                        data['zero_point'] = np.asarray([0]).astype(np.int8)
                    elif self.input_type == 'uint8':
                        data['datatype'] = np.dtype('uint8')
                        data['zero_point'] = np.asarray([128]).astype(np.uint8)
                    dequant_name = name + '_dv_post_dequant'
                    self.dz_nx_graph.add_node(dequant_name,
                                              op='dequant',
                                              x=name,
                                              datatype=np.dtype('float32'),
                                              output_shape=data['output_shape'][:])
                    self.rewire_out_edges(name, dequant_name)
                    self.dz_nx_graph.add_edge(name, dequant_name)
                    continue

                data['datatype'] = out_node['datatype']
                data['quant_scale'] = out_node['quant_scale']
                data['zero_point'] = out_node['zero_point']
                data['quant_axis'] = out_node['quant_axis']
                remove_node = True
                if data['datatype'] == np.dtype('int8') and self.input_type == 'uint8':
                    data['zero_point'] = data['zero_point'].astype(np.int32) + 128
                    data['zero_point'] = data['zero_point'].astype(np.uint8)
                    data['datatype'] = np.dtype('uint8')
                    remove_node = False
                elif data['datatype'] == np.dtype('uint8') and self.input_type == 'int8':
                    data['zero_point'] = data['zero_point'].astype(np.int32) - 128
                    data['zero_point'] = data['zero_point'].astype(np.int8)
                    data['datatype'] = np.dtype('int8')
                    remove_node = False
                if remove_node:
                    self.rewire_out_edges(out_name, name)
                    self.dz_nx_graph.remove_node(out_name)
            else:
                quant_name = name + '_dv_quant'
                self.dz_nx_graph.add_node(quant_name,
                                          op='quant',
                                          x=name,
                                          quant_scale=data['quant_scale'],
                                          zero_point=data['zero_point'],
                                          quant_axis=data['quant_axis'],
                                          datatype=data['datatype'],
                                          output_shape=data['output_shape'][:])
                if self.input_type == 'float32':
                    data['datatype'] = np.dtype('float32')
                    del data['quant_scale']
                    del data['zero_point']
                    del data['quant_axis']
                elif self.input_type == 'int8':
                    new_zero = (data['zero_point'].astype(np.int32) - 128).astype(np.int8)
                    data['datatype'] = np.dtype('int8')
                    data['zero_point'] = new_zero
                elif self.input_type == 'uint8':
                    new_zero = (data['zero_point'].astype(np.int32) + 128).astype(np.uint8)
                    data['datatype'] = np.dtype('uint8')
                    data['zero_point'] = new_zero
                self.rewire_out_edges(name, quant_name)
                self.dz_nx_graph.add_edge(name, quant_name)

    def adjust_output_type(self):
        to_modify = self.orig_outputs[:]
        while len(to_modify) > 0:
            name = to_modify[0]
            data = self.dz_nx_graph.nodes[name]
            if (self.output_type == 'float32' and data['datatype'] == np.dtype('float32')) or \
                    (self.output_type == 'int8' and data['datatype'] == np.dtype('int8')) or \
                    (self.output_type == 'uint8' and data['datatype'] == np.dtype('uint8')):
                to_modify.pop(0)
                continue
            if data['datatype'] == np.dtype('float32'):
                if data['op'] != 'dequant':
                    print("WARNING: We are unable to adjust " \
                          "output %s. Maintaining as float." % name)
                    to_modify.pop(0)
                    continue
                in_name = data['x']
                in_node = self.dz_nx_graph.nodes[in_name]
                if (self.output_type == 'int8' and in_node['datatype'] == np.dtype('int8')) or \
                        (self.output_type == 'uint8' and in_node['datatype'] == np.dtype('uint8')):
                    self.orig_outputs[self.orig_outputs.index(name)] = in_name
                    to_modify[to_modify.index(name)] = in_name
                    if len(list(self.dz_nx_graph.out_edges(name))) == 0:
                        self.dz_nx_graph.remove_node(name)
                else:
                    data['op'] = 'quant'
                    data['quant_scale'] = in_node['quant_scale']
                    data['quant_axis'] = in_node['quant_axis']
                    if self.output_type == 'int8':
                        data['zero_point'] = (in_node['zero_point'].astype(np.int32) - 128).astype(np.int8)
                        data['datatype'] = np.dtype('int8')
                    elif self.output_type == 'uint8':
                        data['zero_point'] = (in_node['zero_point'].astype(np.int32) + 128).astype(np.uint8)
                        data['datatype'] = np.dtype('uint8')
            else:
                if self.output_type == 'float32':
                    deq_name = name + '_dv_post_dequant'
                    self.dz_nx_graph.add_node(deq_name,
                                              op='dequant',
                                              x=name,
                                              datatype=np.dtype('float32'),
                                              output_shape=data['output_shape'][:])
                    self.dz_nx_graph.add_edge(name, deq_name)
                    self.orig_outputs[self.orig_outputs.index(name)] = deq_name
                    to_modify[to_modify.index(name)] = deq_name
                else:
                    quant_name = name + '_dv_post_quant'
                    self.dz_nx_graph.add_node(quant_name,
                                              op='quant',
                                              x=name,
                                              quant_scale=data['quant_scale'],
                                              quant_axis=data['quant_axis'],
                                              output_shape=data['output_shape'][:])
                    self.dz_nx_graph.add_edge(name, quant_name)
                    self.orig_outputs[self.orig_outputs.index(name)] = quant_name
                    to_modify[to_modify.index(name)] = quant_name
                    if self.output_type == 'int8':
                        new_zero = (data['zero_point'].astype(np.int32) - 128).astype(np.int8)
                        self.dz_nx_graph.nodes[quant_name]['zero_point'] = new_zero
                        self.dz_nx_graph.nodes[quant_name]['datatype'] = np.dtype('int8')
                    elif self.output_type == 'uint8':
                        new_zero = (data['zero_point'].astype(np.int32) + 128).astype(np.uint8)
                        self.dz_nx_graph.nodes[quant_name]['zero_point'] = new_zero
                        self.dz_nx_graph.nodes[quant_name]['datatype'] = np.dtype('uint8')

    def clean_zero_point(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if 'zero_point' not in data:
                continue
            data['zero_point'] = data['zero_point'].astype(np.int32)

    def update_alt_inputs(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if 'alt_input' in data:
                new_name = data['alt_input']
                while new_name in self.relabeled_names.keys():
                    new_name = self.relabeled_names[new_name]
                data['alt_input'] = new_name

    def force_activations_to_uint8(self):
        for node_name, data in self.dz_nx_graph.nodes(data=True):
            if 'activation' in data and data['datatype'] == np.int8:
                data['datatype'] = np.dtype('uint8')
                data['data_format'] = 'UINT8'
                data['zero_point'] = data['zero_point'].astype(np.int16) + 128
                data['zero_point'] = data['zero_point'].astype(np.uint8)
