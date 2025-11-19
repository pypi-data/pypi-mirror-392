# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import numpy as np
import os
import sys
import tarfile
from PIL import Image

png = '.png'
jpg = '.jpg'
jpeg = '.jpeg'
onnx_file = '.onnx'
tflite_file = '.tflite'
h5_file = '.h5'
tfhub_ext = 'https://tfhub.dev/'
convert_message = "Converted from "
signed = 'signed'
unsigned = 'unsigned'


def pad_kernel(kernel, dilation_h, dilation_w):
    """
    Kernel layout is HWIO, we insert a column of zeroes at
    every dilation_w and a row of zeroes at every dilation_h
    to simulate dilation.
    :param kernel: The kernel to pad to simulate dilation
    :param dilation_w: Dilation for width dimension
    :param dilation_h: Dilation for height dimension
    """
    new_height = kernel.shape[0] + (kernel.shape[0] - 1) * (dilation_h - 1)
    new_width = kernel.shape[1] + (kernel.shape[1] - 1) * (dilation_w - 1)
    new_kernel = np.zeros((new_height,
                           new_width,
                           kernel.shape[2],
                           kernel.shape[3]))
    new_kernel[::dilation_h, ::dilation_w, :, :] = kernel
    return new_kernel

def gen_constant(input_file, default_shape, layer_name):
    if input_file.endswith('.pb'):
        return gen_tf_1_x_constant(input_file, default_shape, layer_name)
    elif input_file.endswith('.onnx'):
        return gen_onnx_constant(input_file, layer_name)
    elif input_file.endswith('.tflite'):
        return gen_tflite_constant(input_file, layer_name)

def gen_tf_1_x_constant(input_file, default_shape, layer_name):
    import tensorflow as tf
    if float(tf.__version__[:2]) >= 2.0:
        import tensorflow.compat.v1 as tf

    input_dict = {}
    tf.reset_default_graph()
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(open(input_file, 'rb').read())
    tf.import_graph_def(graph_def)
    for op in tf.get_default_graph().get_operations():
        if op.type != 'Placeholder':
            continue
        print(op.outputs[0])
        placeholder_name = op._outputs[0]._name
        placeholder_shape = list(op._outputs[0]._shape_val)
        for i in range(len(placeholder_shape)):
            if placeholder_shape[i] is None:
                placeholder_shape[i] = default_shape[i]
        if op._outputs[0]._dtype == tf.float32:
            input_dict[placeholder_name] = np.random.random(placeholder_shape)
        else:
            input_dict[placeholder_name] = np.random.randint(0,128, placeholder_shape)
    if not layer_name.endswith(':0'):
        layer_name += ':0'
    with tf.Session() as sess:
        tf_output = sess.run([layer_name], feed_dict=input_dict)
    return tf_output[0]

def gen_onnx_constant(input_file, layer_name):
    import numpy as np
    from deepview_rtm.onnx.onnx_ml_pb2 import TensorProto, ModelProto

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
        int(TensorProto.STRING): np.dtype(np.object)
    }

    with open(input_file, 'rb') as f:
        input_model = f.read()

    onnx_model = ModelProto()
    onnx_model.ParseFromString(input_model)
    onnx_graph = onnx_model.graph

    layer_found = False
    for i in range(len(onnx_graph.initializer)):
        onnx_const = onnx_graph.initializer[i]
        name = onnx_const.name
        if name != layer_name:
            continue
        layer_found = True
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
        
    if not layer_found:
        raise ValueError("Layer %s is not a constant in the model. Cannot generate constant." % layer_name)
    return np_tensor

def gen_tflite_constant(input_file, layer_name):
    tflite_type_map = {
        0: np.dtype('float32'),
        1: np.dtype('float16'),
        2: np.dtype('int32'),
        3: np.dtype('uint8'),
        4: np.dtype('int64'),
        5: np.dtype(np.object),
        6: np.dtype('bool'),
        7: np.dtype('int16'),
        8: np.dtype('complex64'),
        9: np.dtype('int8'),
        10: np.dtype('float64')
    }
    from deepview_rtm.tflite.Model import Model

    with open(input_file, 'rb') as f:
        tflite_model = Model.GetRootAsModel(f.read(), 0)
    tflite_graph = tflite_model.Subgraphs(0)

    layer_found = False
    for i in range(tflite_graph.TensorsLength()):
        tensor = tflite_graph.Tensors(i)
        name = tensor.Name().decode('utf-8')
        if name != layer_name:
            continue
        layer_found = True
        buf_idx = tensor.Buffer()
        buffer = tflite_model.Buffers(buf_idx)
        if buffer.DataLength() == 0:
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
    
    if not layer_found:
        raise ValueError("Layer %s is not a constant in the model. Cannot generate constant." % layer_name)
    return np_tensor

def gen_ssd_output(importer,
                   boxes_name,
                   input_shape,
                   node_name,
                   anchors_numpy,
                   scales):
    # Pre-slice anchors and add 4 new constants
    # anchors[:, :2], anchors[:, 2:], anchors[:, :2] / scales[:2], 1 / scales[2:]
    left_slice = anchors_numpy[..., :2]
    right_slice = anchors_numpy[..., 2:]
    centre_slice = right_slice / scales[:2]
    importer.nxgraph.add_node("anchors_left",
                              op='constant',
                              np_tensor=left_slice,
                              shape=left_slice.shape,
                              dtype=left_slice.dtype,
                              output_shape=left_slice.shape)
    importer.nxgraph.add_node("anchors_centre",
                              op='constant',
                              np_tensor=centre_slice,
                              shape=centre_slice.shape,
                              dtype=centre_slice.dtype,
                              output_shape=centre_slice.shape)
    importer.nxgraph.add_node("anchors_right",
                              op='constant',
                              np_tensor=right_slice,
                              shape=right_slice.shape,
                              dtype=right_slice.dtype,
                              output_shape=right_slice.shape)
    size_variance = np.expand_dims(1 / np.array(scales[2:]), 0)
    importer.nxgraph.add_node("size_variance",
                              op='constant',
                              np_tensor=size_variance,
                              shape=[1, 2],
                              dtype=size_variance.dtype,
                              output_shape=[1, 2])

    half_input = [input_shape[0], input_shape[1], 2]
    """
    Left side
    """
    # left slice
    l_slice_name = node_name + "_lslice"
    importer.nxgraph.add_node(l_slice_name,
                              op='slice',
                              input=boxes_name,
                              axes=[0, 1, 2],
                              begin=[0, 0, 0],
                              end=[0, 0, 2],
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(boxes_name, l_slice_name)
    # left mul
    l_mul_name = node_name + "_lmul"
    importer.nxgraph.add_node(l_mul_name,
                              op='mul',
                              x=l_slice_name,
                              y="anchors_centre",
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(l_slice_name, l_mul_name)
    importer.nxgraph.add_edge("anchors_centre", l_mul_name)
    # left add
    l_add_name = node_name + "_ladd"
    importer.nxgraph.add_node(l_add_name,
                              op='add',
                              x=l_mul_name,
                              y="anchors_left",
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(l_mul_name, l_add_name)
    importer.nxgraph.add_edge("anchors_left", l_add_name)

    """
    Right side
    """
    # right slice
    r_slice_name = node_name + "_rslice"
    importer.nxgraph.add_node(r_slice_name,
                              op='slice',
                              input=boxes_name,
                              axes=[0, 1, 2],
                              begin=[0, 0, 2],
                              end=[0, 0, 0],
                              datatype=right_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(boxes_name, r_slice_name)

    # right mul
    r_mul_name = node_name + "_rmul"
    importer.nxgraph.add_node(r_mul_name,
                              op='mul',
                              x=r_slice_name,
                              y="size_variance",
                              datatype=right_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(r_slice_name, r_mul_name)
    importer.nxgraph.add_edge("size_variance", r_mul_name)
    # right exp
    r_exp_name = node_name + "_exp"
    importer.nxgraph.add_node(r_exp_name,
                              op='exp',
                              x=r_mul_name,
                              datatype=right_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(r_mul_name, r_exp_name)
    # right prior mul
    r_mul_priors_name = node_name + "_rmul_priors"
    importer.nxgraph.add_node(r_mul_priors_name,
                              op="mul",
                              x=r_exp_name,
                              y="anchors_right",
                              datatype=right_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(r_exp_name, r_mul_priors_name)
    importer.nxgraph.add_edge("anchors_right", r_mul_priors_name)

    """
    Concatenate left and right
    """
    boxes_concat_name = node_name + "_boxes_concat"
    importer.nxgraph.add_node(boxes_concat_name,
                              op='concat',
                              axis=2,
                              values=[l_add_name,
                                      r_mul_priors_name],
                              datatype=left_slice.dtype,
                              output_shape=input_shape)
    importer.nxgraph.add_edge(l_add_name, boxes_concat_name)
    importer.nxgraph.add_edge(r_mul_priors_name, boxes_concat_name)
    """
    Rearrange from [centre_y, centre_x, width, height] to [centre_x, centre_y, height, width]
    """
    # Slice each coordinate
    axes = [0, 1, 2]
    split_names = []
    for i in range(4):
        begin = 3 * [0]
        begin[2] = i
        end = input_shape[:]
        end[2] = i + 1
        split_shape = [input_shape[0], input_shape[1], 1]
        split_names.append(node_name + "_split_" + str(i))
        importer.nxgraph.add_node(split_names[i],
                                  op="slice",
                                  input=boxes_concat_name,
                                  axes=axes,
                                  begin=begin,
                                  end=end,
                                  datatype=left_slice.dtype,
                                  output_shape=split_shape)
        importer.nxgraph.add_edge(boxes_concat_name, split_names[i])
    # Concatenate back in desired order
    reorder_concat_name = node_name + "_reorder_concat"
    importer.nxgraph.add_node(reorder_concat_name,
                              op='concat',
                              axis=2,
                              values=[split_names[1],
                                      split_names[0],
                                      split_names[3],
                                      split_names[2]],
                              datatype=left_slice.dtype,
                              output_shape=input_shape)
    for name in split_names:
        importer.nxgraph.add_edge(name, reorder_concat_name)

    # Centre form to corner form
    corner_slice_l_name = node_name + "_corner_slice_l"
    importer.nxgraph.add_node(corner_slice_l_name,
                              op='slice',
                              input=reorder_concat_name,
                              axes=[0, 1, 2],
                              begin=[0, 0, 0],
                              end=[0, 0, 2],
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(reorder_concat_name, corner_slice_l_name)

    corner_slice_r_name = node_name + "_corner_slice_r"
    importer.nxgraph.add_node(corner_slice_r_name,
                              op='slice',
                              input=reorder_concat_name,
                              axes=[0, 1, 2],
                              begin=[0, 0, 2],
                              end=[0, 0, 0],
                              datatype=right_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(reorder_concat_name, corner_slice_r_name)

    # Add constant to div by 2
    corner_half_name = node_name + "_half_constant"
    importer.nxgraph.add_node(corner_half_name,
                              op='constant',
                              shape=[1],
                              dtype=np.float32,
                              np_tensor=np.array([0.5]),
                              output_shape=[1])

    corner_mul_name = node_name + "_corner_mul"
    importer.nxgraph.add_node(corner_mul_name,
                              op='mul',
                              x=corner_slice_r_name,
                              y=corner_half_name,
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(corner_slice_r_name, corner_mul_name)
    importer.nxgraph.add_edge(corner_half_name, corner_mul_name)

    corner_sub_name = node_name + "_corner_sub"
    importer.nxgraph.add_node(corner_sub_name,
                              op='sub',
                              x=corner_slice_l_name,
                              y=corner_mul_name,
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(corner_slice_l_name, corner_sub_name)
    importer.nxgraph.add_edge(corner_mul_name, corner_sub_name)

    corner_add_name = node_name + "_corner_add"
    importer.nxgraph.add_node(corner_add_name,
                              op='add',
                              x=corner_slice_l_name,
                              y=corner_mul_name,
                              datatype=left_slice.dtype,
                              output_shape=half_input)
    importer.nxgraph.add_edge(corner_slice_l_name, corner_add_name)
    importer.nxgraph.add_edge(corner_mul_name, corner_add_name)

    corner_concat_name = node_name + "_corner_concat"
    importer.nxgraph.add_node(corner_concat_name,
                              op='concat',
                              axis=2,
                              values=[corner_sub_name,
                                      corner_add_name],
                              datatype=left_slice.dtype,
                              output_shape=input_shape)
    importer.nxgraph.add_edge(corner_sub_name, corner_concat_name)
    importer.nxgraph.add_edge(corner_add_name, corner_concat_name)


def graph_def_from_saved_model(default_shape, model_dir, experimental_new_converter=True, allow_custom_ops=False,
                               quantize=False, model_input_type=np.float32, input_type='float32', output_type='float32',
                               dataset_gen=None, dequantize=False):
    import tensorflow as tf
    import tempfile
    if not os.path.isdir(model_dir):
        model_dir = os.path.dirname(model_dir)
    loaded = tf.saved_model.load(model_dir)
    in_shape_provided = False
    if (list(loaded.signatures.keys())):
        in_shape = list(loaded.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY].inputs[0].get_shape())
        if None not in in_shape:
            in_shape_provided = True
    if not in_shape_provided:
        print("WARNING, signature key not found or input shape not provided. \n"
              "Default shape is set to " + str(default_shape) + "\n"
                                                                "Change default shape using --default_shape")
        with tempfile.TemporaryDirectory() as temp:
            module_with_signature_path = temp
            if not os.path.exists(module_with_signature_path):
                os.mkdir(module_with_signature_path)
                
            if model_input_type == np.float32:
                call = loaded.__call__.get_concrete_function(tf.TensorSpec(default_shape, tf.float32))
            elif model_input_type == np.int8:
                call = loaded.__call__.get_concrete_function(tf.TensorSpec(default_shape, tf.int8))
            elif model_input_type == np.uint8:
                call = loaded.__call__.get_concrete_function(tf.TensorSpec(default_shape, tf.uint8))
            else:
                raise ValueError("We currently do not support input type: %s" % str(model_input_type))
            tf.saved_model.save(loaded, module_with_signature_path, signatures=call)
            converter = tf.lite.TFLiteConverter.from_saved_model(module_with_signature_path)
            if quantize:
                converter.optimizations = [tf.lite.Optimize.DEFAULT]
                converter.representative_dataset = dataset_gen
                if input_type == 'int8':
                    converter.inference_input_type = tf.int8
                elif input_type == 'uint8':
                    converter.inference_input_type = tf.uint8
                if output_type == 'int8':
                    converter.inference_output_type = tf.int8
                elif output_type == 'uint8':
                    converter.inference_output_type = tf.uint8
            converter.experimental_new_converter = experimental_new_converter
            converter.allow_custom_ops = allow_custom_ops
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
            try:
                return converter.convert()
            except Exception as e:
                try:
                    converter.experimental_new_converter = not experimental_new_converter
                    return converter.convert()
                except Exception as e:
                    if quantize:
                        try:
                            converter.experimental_new_converter = experimental_new_converter
                            converter.experimental_new_quantizer = False
                            return converter.convert()
                        except Exception as e:
                            converter.experimental_new_converter = not experimental_new_converter
                            return converter.convert()
                    else:
                        raise e
    else:
        converter = tf.lite.TFLiteConverter.from_saved_model(model_dir)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = dataset_gen
        if input_type == 'int8':
            converter.inference_input_type = tf.int8
        elif input_type == 'uint8':
            converter.inference_input_type = tf.uint8
        if output_type == 'int8':
            converter.inference_output_type = tf.int8
        elif output_type == 'uint8':
            converter.inference_output_type = tf.uint8
    converter.experimental_new_converter = experimental_new_converter
    converter.allow_custom_ops = allow_custom_ops
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
    try:
        return converter.convert()
    except Exception as e:
        try:
            converter.experimental_new_converter = not experimental_new_converter
            return converter.convert()
        except Exception as e:
            if quantize:
                try:
                    converter.experimental_new_converter = experimental_new_converter
                    converter.experimental_new_quantizer = False
                    return converter.convert()
                except Exception as e:
                    converter.experimental_new_converter = not experimental_new_converter
                    return converter.convert()
            else:
                raise e


def graph_def_from_tfhub_model(default_shape, model_handle, experimental_new_converter=True, allow_custom_ops=False,
                               quantize=False, model_input_type=np.float32, input_type='float32', output_type='float32', 
                               dataset_gen=None, dequantize=False):
    """
    graph_def_from_tfhub_model(default_shape, model_handle, experimental_new_converter=True, allow_custom_ops=False,
                               quantize=False, input_type='float32', output_type='float32', dataset_gen=None,
                               dequantize=False)

    Converts a provided TFHub URL to TFLite and returns the buffer.

    Parameters
    ----------
    default_shape : list
        The default shape for the input to the provided TFHub Model.
    model_handle : string
        The TFHub URL of the desired model to be converted.
    experimental_new_converter : {True, False}, optional
        Whether to use TOCO or MLIR conversion to TFLite.
    allow_custom_ops : {True, False}, optional
        Whether to allow the use of custom operations within the TFLite Model.
    quantize : {True, False}, optional
        Whether to quantize the provided TFHub Model during conversion to TFLite.
    input_type : {'float32', 'int8', 'uint8'}, optional
        The datatype for input layers in the model during quantization to TFLite.
    output_type : {'float32', 'int8', 'uint8'}, optional
        The datatype for output layers in the model during quantization to TFLite.
    dataset_gen : function, optional
        The function that provides samples for quantization. If None is provided,
        quantization is unavailable.
    dequantize : {True, False}, optional
        This parameter is obsolete and to be removed.

    Returns
    -------
    tflite_buffer : bytes
        The converted TFLite Model buffer.
    """
    # Loads a TF Hub model by converting to a keras model and prepending an input layer
    import tensorflow_hub as hub
    import tensorflow as tf
    assert float(tf.__version__[:2]) >= 2.0, \
        "Tensorflow 2.0 or greater is required for Tensorflow Hub models"
    print("Importing TF Hub model with shape: " + str(default_shape))
    print("If you want a different input size, specify a default shape using --default_shape")

    if model_input_type == np.float32:
        inputs = tf.keras.Input(shape=default_shape[1:], dtype=tf.float32)
    elif model_input_type == np.int8:
        inputs = tf.keras.Input(shape=default_shape[1:], dtype=tf.int8)
    elif model_input_type == np.uint8:
        inputs = tf.keras.Input(shape=default_shape[1:], dtype=tf.uint8)
    else:
        raise ValueError("We currently do not support input type: %s" % str(model_input_type))
    layers = hub.KerasLayer(model_handle)(inputs)
    keras_model = tf.keras.Model(inputs=inputs, outputs=layers)

    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = dataset_gen
        if input_type == 'int8':
            converter.inference_input_type = tf.int8
        elif input_type == 'uint8':
            converter.inference_input_type = tf.uint8
        if output_type == 'int8':
            converter.inference_output_type = tf.int8
        elif output_type == 'uint8':
            converter.inference_output_type = tf.uint8
    converter.experimental_new_converter = experimental_new_converter
    converter.allow_custom_ops = allow_custom_ops
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]

    try:
        return converter.convert()
    except Exception as e:
        if quantize:
            converter.experimental_new_quantizer = False
            return converter.convert()
        else:
            raise e


def saved_model_exists(filename):
    """
    saved_model_exists(filename)

    Determines whether a filepath is a valid Saved Model file or directory.

    Parameters
    ----------
    filename : string
        The filepath to the Saved Model file/directory to be tested for validity.

    Returns
    -------
    valid : bool
        The validity of whether the file/directory is a Saved Model.
    """
    return os.path.isfile(filename + '/saved_model.pb') or \
           os.path.isfile(filename + '/saved_model.pbtxt') or \
           filename.endswith('saved_model.pb') or \
           filename.endswith('saved_model.pbtxt')


def nnef_model_exists(filename):
    from os import listdir
    from os.path import isfile, join, isdir
    if filename.endswith(".nnef"):
        return True
    if isdir(filename):
        for f in listdir(filename):
            if isfile(join(filename, f)) and f.endswith(".nnef"):
                return True
    return False


def convert_to_mmdnn(default_shape,
                     source_framework,
                     network_file,
                     weights_file):
    from subprocess import call
    from tempfile import mkdtemp
    graph_prefix = os.path.join(mkdtemp(), "mmdnn_graph")
    print("Using input shape {}. This can be changed by passing"
          " your required shape to --default_shape".format(default_shape))
    # MXNet's shapes are in NCHW, also ignore batch due to it always being 1
    mmdnn_shape = ",".join(
        map(str, [default_shape[3], default_shape[1], default_shape[2]]))
    convert_command = ["mmtoir",
                       "-f", source_framework,
                       "-in", network_file,
                       "-d", graph_prefix,
                       "--inputShape", mmdnn_shape]
    if weights_file:
        convert_command.append("-iw")
        convert_command.append(weights_file)
    else:
        print("Warning! No weights were found. Converting without weights.")
    if call(convert_command) != 0:
        raise RuntimeError("Could not convert model using MMdnn")
    return graph_prefix


def mxnet_model_exists(filename):
    from os import listdir
    from os.path import isfile, join, isdir
    if not isdir(filename):
        return False
    json_count = 0
    for f in listdir(filename):
        if isfile(join(filename, f)) and f.endswith(".json"):
            json_count += 1

    if json_count == 1:
        return True
    if json_count > 1:
        raise ValueError("More than one MXNet model is present in directory: {} ".format(filename))
    else:
        return False


def get_mxnet_model(filename):
    from os import listdir
    from os.path import isfile, join
    params_file = ""
    json_file = ""
    for f in listdir(filename):
        if isfile(join(filename, f)):
            if f.endswith(".params"):
                params_file = join(filename, f)
            elif f.endswith(".json"):
                json_file = join(filename, f)
    return params_file, json_file


def caffe_model_exists(filename):
    from os import listdir
    from os.path import isfile, join, isdir
    if not isdir(filename):
        return False
    proto_count = 0
    for f in listdir(filename):
        if isfile(join(filename, f)) and f.endswith(".prototxt"):
            proto_count += 1

    if proto_count == 1:
        return True
    if proto_count > 1:
        raise ValueError("More than one Caffe model is present in directory {}".format(filename))
    else:
        return False


def get_caffe_model(filename):
    from os import listdir
    from os.path import isfile, join
    proto_file = ""
    caffe_model_file = ""
    for f in listdir(filename):
        if isfile(join(filename, f)):
            if f.endswith(".prototxt"):
                proto_file = join(filename, f)
            elif f.endswith(".caffemodel"):
                caffe_model_file = join(filename, f)
    return proto_file, caffe_model_file


def mmdnn_model_exists(filename):
    """
    mmdnn_model_exists(filename)

    Determines whether a directory/file is a valid MMDNN Model.

    Parameters
    ----------
    filename : string
        The filepath to the MMDNN file or directory.

    Returns
    -------
    valid : bool
        The boolean response of the validity of the provided file as a MMDNN Model.
    """
    from os import listdir
    from os.path import isfile, join, isdir
    if not isdir(filename):
        return False
    proto_count = 0
    for f in listdir(filename):
        if isfile(join(filename, f)) and f.endswith(".pb"):
            proto_count += 1

    if proto_count == 1:
        return True
    if proto_count > 1:
        raise ValueError("More than one MMdnn model is present in directory {}".format(filename))
    else:
        return False


def get_mmdnn_model(filename):
    """
    get_mmdnn_model(filename)

    Generates the correct naming structure for MMDNN files for conversion.

    Parameters
    ----------
    filename : string
        The input filename to the MMDNN Model.

    Returns
    -------
    filename : string
        Returns the filename with model name prefix for the given MMDNN Model.
    """
    from os import listdir
    from os.path import isfile, join

    for f in listdir(filename):
        if isfile(join(filename, f)):
            if f.endswith(".npy"):
                return join(filename, f)[:-4]
            elif f.endswith(".pb"):
                return join(filename, f)[:-3]


def setup_logger():
    """
    setup_logger()

    Sets up the logger and returns the filepath of the logged information.

    Returns
    -------
    log_path : string
        The filepath of the logged information.
    """
    import logging
    import tempfile

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_dir = tempfile.mkdtemp()
    log_path = os.path.join(log_dir, "unknown_nodes_log.txt")

    formatter = logging.Formatter('%(levelname)s - %(message)s')

    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return log_path
