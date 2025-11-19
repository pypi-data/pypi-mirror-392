import networkx as nx
import numpy as np
from enum import Enum

class LayerFormat(Enum):
    UNKNOWN=0,
    NHWC=1,
    NCHW=2,
    NDC=3,
    NCD=4

class Op(Enum):
    EXTERNAL=0,
    CONSTANT=1

class AGLayer:
    def __init__(self, name, op='UNKNOWN', inputs=[], params={}, 
                 datatype=np.float32, layer_format=LayerFormat.UNKNOWN, tensor=None,
                 shape=[], scale=None, zero_point=None, quant_axis=0):
        self.name = name
        self.inputs = inputs
        self.op = op
        self.params = params
        self.tensor = tensor
        self.datatype = datatype
        self.format = layer_format
        self.shape = shape
        self.quant_scale = scale
        self.zero_point = zero_point
        self.quant_axis = quant_axis
        self.out_nodes = []

    def __str__(self):
        print_str = "Name: %s\n" % self.name
        print_str += "Inputs: [%s]\n" % ', '.join(self.inputs)
        print_str += "Op: %s\n" % self.op
        params_str = "Params: {"
        for key, val in self.params.items():
            params_str += "%s: %s, " % (key, str(val))
        params_str += "}\n"
        print_str += params_str
        print_str += "Datatype: %s\n" % str(self.datatype)
        print_str += "Format: %s\n" % str(self.format)
        print_str += "Shape: [%s]" % ', '.join(map(str, self.shape))
        return print_str


class AbstractGraph:
    def __init__(self):
        self.node_map = {}

    def add_node(self, layer: AGLayer):
        self.node_map[layer.name] = layer
        for input_name in layer.inputs:
            if input_name not in self.node_map.keys():
                raise AssertionError("Input %s does not exist in graph, while adding node %s" % (input_name, layer.name))
            self.node_map[input_name].out_nodes.append(layer.name)
