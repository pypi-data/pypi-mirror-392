def tflite_converter_from_frozen_graph(filename, input_names, output_names, input_shapes):
    import tensorflow as tf
    return tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
        filename, input_names, output_names,
        input_shapes=input_shapes)


def keras_models_load_model(filename, compile, custom_objects):
    import tensorflow as tf
    return tf.keras.models.load_model(filename, compile=compile,
                                      custom_objects=custom_objects)


def tflite_converter_from_keras_model(model):
    import tensorflow as tf
    return tf.lite.TFLiteConverter.from_keras_model(model)


def tflite_converter_from_keras_model_file(filename):
    import tensorflow as tf
    return tf.lite.TFLiteConverter.from_keras_model_file(filename)


def extract_sub_graph(replaced_inputs_graph_def, output_nodes):
    import tensorflow as tf
    return tf.compat.v1.graph_util.extract_sub_graph(replaced_inputs_graph_def, output_nodes)
