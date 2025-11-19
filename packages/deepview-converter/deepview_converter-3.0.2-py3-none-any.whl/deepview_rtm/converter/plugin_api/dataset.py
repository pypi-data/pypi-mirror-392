import os
from PIL import Image
import numpy as np
import tensorflow as tf


class Dataset:
    def __init__(self, samples, input_shape, quant_norm, num_samples=10, input_type=np.float32):
        self.samples = samples
        self.input_shape = input_shape
        self.quant_norm = quant_norm
        self.annotations_list = []
        self.num_samples = num_samples
        self.input_type = input_type

    def generator(self):
        samples_source, crop = self.samples
        if samples_source.startswith('http://') or \
                samples_source.endswith('.deepview') or \
                samples_source.endswith('.eiqp'):
            def representative_dataset_gen():
                if crop or crop == ' ':
                    from dataset_interface import \
                        DatastoreGeneratorClassification as DatasetInterface
                else:
                    from dataset_interface import \
                        DatastoreGeneratorDetection as DatasetInterface
                ds_iterator = DatasetInterface(
                    source=samples_source,
                    input_shape=self.input_shape[1:]
                )

                count = 0
                for instance in ds_iterator.get_samples():
                    # Need to add options for different input types
                    if self.quant_norm == 'unsigned':
                        data = tf.cast(instance, tf.float32)
                        data /= 255.
                    elif self.quant_norm == 'signed':
                        data = tf.cast(instance, tf.float32)
                        data /= 127.5
                        data -= 1.
                    elif self.quant_norm == 'imagenet':
                        mean = [123.68, 116.779, 103.939]  # RGB means
                        mean_tensor = tf.keras.backend.constant(-np.array(mean), dtype=tf.float32)
                        data = tf.keras.backend.bias_add(
                            tf.cast(instance, tf.float32),
                            mean_tensor,
                            'channels_last')
                    elif self.quant_norm in ['raw' or None]:
                        data = instance
                    else:
                        raise ValueError("\t - [{}] is not supported as a "
                                         "normalization option.".format(self.quant_norm))
                    data = tf.cast(data, tf.float32)
                    yield [data]
                    count += 1
                    if count >= self.num_samples:
                        return

        elif os.path.isdir(samples_source):
            def representative_dataset_gen():
                image_paths = []
                for root, _, files in os.walk(samples_source):
                    for filename in files:
                        if not filename.lower().endswith('.png') and \
                                not filename.lower().endswith('.jpg') and \
                                not filename.lower().endswith('.jpeg'):
                            continue
                        image_paths.append(filename)

                if len(image_paths) == 0:
                    raise ValueError("Cannot find any usable images for quantization in %s" % samples_source)

                for i in range(self.num_samples):
                    if len(image_paths) == 0:
                        return
                    file_index = np.random.randint(0, len(image_paths))
                    filename = image_paths.pop(file_index)
                    try:
                        img = Image.open(
                            os.path.join(root, filename)
                        )
                        img.load()
                        if self.input_shape[1] == 3:
                            img = img.resize(self.input_shape[2:4])
                        else:
                            img = img.resize(self.input_shape[1:3])
                        data = np.asarray(img)
                        if self.input_shape[1] == 3:
                            data = np.transpose(data, [2,0,1])
                        if self.input_type == np.uint8:
                            instance = np.reshape(data, self.input_shape).astype(self.input_type)
                            yield [instance]
                        elif self.input_type == np.int8:
                            instance = (data.astype(np.int32) - 128).astype(np.int8)
                            instance = np.reshape(data, self.input_shape).astype(self.input_type)
                            yield [instance]
                        elif self.input_type == np.float32:
                            instance = np.reshape(data, self.input_shape).astype(np.float32)
                            if self.quant_norm == 'unsigned':
                                data = tf.cast(instance, tf.float32)
                                data /= 255.
                            elif self.quant_norm == 'signed':
                                data = tf.cast(instance, tf.float32)
                                data /= 127.5
                                data -= 1.
                            elif self.quant_norm == 'imagenet':
                                if self.input_shape[1] == 3:
                                    data = np.transpose(data, [0,2,3,1])
                                mean = [123.68, 116.779, 103.939]  # RGB means
                                mean_tensor = tf.keras.backend.constant(-np.array(mean), dtype=tf.float32)
                                data = tf.keras.backend.bias_add(
                                    tf.cast(instance, tf.float32),
                                    mean_tensor,
                                    'channels_last')
                                if self.input_shape[1] == 3:
                                    data = np.transpose(data, [0,3,1,2])
                            elif self.quant_norm in ['raw' or None]:
                                data = instance
                            else:
                                raise ValueError("\t - [{}] is not supported as a "
                                                "normalization option.".format(self.quant_norm))
                            
                            data = tf.cast(data, tf.float32)
                            yield [data]
                        else:
                            raise ValueError("Input type: %s not supported" % str(self.input_type))
                    except Exception:
                        continue
        else:
            print("We do not support datastore datasets currently")
            print("Using white noise dataset generation")
            def representative_dataset_gen():
                for _ in range(self.num_samples):
                    if self.input_type == np.float32:
                        yield [np.random.random(self.input_shape).astype(self.input_type)]
                    elif self.input_type == np.uint8:
                        yield [np.random.randint(0, 256, self.input_shape).astype(self.input_type)]
                    elif self.input_type == np.int8:
                        yield [np.random.randint(-128, 128, self.input_shape).astype(self.input_type)]

        return representative_dataset_gen
