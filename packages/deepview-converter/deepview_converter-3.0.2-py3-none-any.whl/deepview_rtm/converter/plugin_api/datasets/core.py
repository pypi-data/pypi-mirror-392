import tensorflow as tf
from typing import List
import math


class VirtualMethodError(NotImplementedError):
    def __init__(self, method='undefined'):
        super(VirtualMethodError, self).__init__(
            'Unable to call virtual method: %s' % method)


class RequestFieldError(LookupError):
    def __init__(self, field='unknown'):
        super(RequestFieldError, self).__init__(
            'Request missing required field: %s' % field)


class RemoteResponseError(RuntimeError):
    def __init__(self, message='', code=None):
        code = ' [%d]' % code if code is not None else ''
        super(RemoteResponseError, self).__init__(
            'Remote responded with error %s: %s' % (code, message))


class BaseDataset(object):
    def __init__(self, datastore, input_shape, batch_size=10, sparse=False):
        self.datastore = datastore
        self.input_shape = input_shape
        self.batch_size = batch_size
        self.sparse = sparse
        self.num_train_samples = 0
        self.num_test_samples = 0
        self.preprocess_input = None
        self.number_of_threads = 4
        self.labels = None

    def is_batched(self) -> bool:
        """
        This function can be override by sub-classes to return True to signal
        that reading from the dataset is done in batches.  The batch size does
        not need to be defined as it will be handled through tf.data.unbatch().

        Returns
        -------
        False: Each sample is returned as a single instance
        True: Samples are returned in batches.
        """
        return False

    def init_labels(self):
        """
        Initializes labels and applies needed processing.
        """
        self.labels = sorted(self.get_labels())

    def init_dataset(self):
        self.init_labels()

    def get_per_epoch_steps(self):
        return math.ceil(self.num_train_samples / self.batch_size), \
               math.ceil(self.num_test_samples / self.batch_size)

    def get_train_num_annotations(self):
        return self.num_train_samples

    def get_test_num_annotations(self):
        return self.num_test_samples

    def get_num_classes(self):
        return len(self.labels)

    def get_labels(self):
        return self.labels

    def set_preprocess_input(self, func):
        self.preprocess_input = func

    def cache_on_memory(self, num_samples):
        """
            # classification sample
            num_bytes = 2 * num_samples * self.input_shape[0] * self.input_size[1] * 3
            if psutil.virtual_memory().free >= num_bytes:
                return True
            return False

        Parameters
        ----------
        num_samples: Num of instances in dataset (train/test). This function will be called for train and test samples

        Returns: if dataset fully fits in memory
        -------

        """
        return False

    def get_labels(self) -> List[str]:
        """

        Returns: list of sorted labels
        -------

        """
        return []

    def read_annotations(self, grouping):
        """
        Parameters
        ----------
            grouping: "train" or "test"

        Returns: All the annotations from the datastore
        -------
        """
        return []

    def load_instance(self, instance_id):
        """
        Loads the instance for presentation to the model which could be a
        cropped image in the case of image classification or a full image in
        the case of object detection.

        This function should return different values depending on the current
        task.

            * classification: [image, label]
            * detection: [image, boxes, labels]

        Parameters:
            instance_id: this can represent an annotation, and image, or others
                depending on the current task.

        Returns:
            A tuple of sample, label, and others.
        """
        return tuple()

    @tf.function
    def tf_fetch_sample(self, instance_id):
        """
        Parameters
        ----------
        image_id: annotation_id in case of classification, otherwise, the image_id

        Returns: this function should return different values in case of the problem
        - classification: [image, label]
        - detection: [image, boxes, labels]
        -------
        """
        return None

    def build_tf_iterator(self, grouping):
        samples = self.read_annotations(grouping)
        n_samples = len(samples)

        if grouping == "train":
            self.num_train_samples = n_samples
        else:
            self.num_test_samples = n_samples

        dataset = tf.data.Dataset.from_tensor_slices(samples)
        if grouping == 'train' and not self.cache_on_memory(n_samples):
            dataset = dataset.shuffle(n_samples)

        dataset = dataset.map(self.tf_fetch_sample,
                              num_parallel_calls=tf.data.AUTOTUNE)

        if self.is_batched():
            dataset = dataset.unbatch()

        if self.cache_on_memory(n_samples):
            print('Caching %s dataset in memory' % grouping)
            dataset = dataset.cache()
            # readme: Shuffle should be performed after the cache, otherwise we'll see a jumping loss
            if grouping == 'train':
                dataset = dataset.shuffle(n_samples)
        return dataset

    def build_train_dataset(self):
        """
                Parameters
                ----------
                    grouping: "train" or "test"

                Returns: All the annotations from the datastore
                -------
                """
        raise VirtualMethodError(self.__class__.build_train_dataset.__name__)

    def build_test_dataset(self):
        """
                Parameters
                ----------
                    grouping: "train" or "test"

                Returns: All the annotations from the datastore
                -------
                """
        raise VirtualMethodError(self.__class__.build_test_dataset.__name__)
