from datasets import get_cached_dataset
import numpy as np


class BaseDatasetGenerator:
    def __init__(self, source, input_shape):
        self.datastore_path = source
        self.input_shape = input_shape
        self.dataset = None

    def get_samples(self):
        for sample in self.dataset:
            yield sample.numpy().astype(np.float32)


class DatastoreGeneratorClassification(BaseDatasetGenerator):
    def __init__(self, source, input_shape):
        super(DatastoreGeneratorClassification, self).__init__(source, input_shape)
        ds = get_cached_dataset(
            task="classification",
            p_type="image",
            arguments={
                "datastore_server": self.datastore_path,
                "input_shape": self.input_shape,
                "batch_size": 1
            })
        self.dataset = ds.build_train_dataset()


class DatastoreGeneratorDetection(BaseDatasetGenerator):
    def __init__(self, source, input_shape):
        super(DatastoreGeneratorDetection, self).__init__(source, input_shape)
        ds = get_cached_dataset(
            task="detection",
            p_type="boxes",
            arguments={
                "datastore_server": self.datastore_path,
                "input_shape": self.input_shape,
                "batch_size": 1,
                "max_detections": 100
            })
        self.dataset = ds.build_train_dataset()
