def calc_binary_output(node_x, node_y):
    """
    Calculates binary op's output shape and handles shape errors
    :param node_name: Binary op's name
    :param node_x: x input node
    :param node_y: y input node
    :param x_name: x input name
    :param y_name: y input name
    :return: Binary op's output shape
    """
    return define_elementwise_binary_output_shape(node_x, node_y)


def define_elementwise_binary_output_shape(x, y):
    """
    Get output shape of binary op
    :param x: First input node
    :param y: Second input node
    :return: Shape as list
    """
    # Check that shapes are valid
    x_dims = x['output_shape'][:]
    y_dims = y['output_shape'][:]
    if len(x_dims) > len(y_dims):
        for i in range(len(x_dims) - len(y_dims)):
            y_dims.insert(0, None)
    elif len(y_dims) > len(y_dims):
        for i in range(len(y_dims) - len(x_dims)):
            x_dims.insert(0, None)

    for x_dim, y_dim in zip(x_dims, y_dims):
        assert (x_dim == y_dim) or (x_dim == 1 or y_dim == 1) or (
                x_dim is None or y_dim is None), \
            "Binary operands could not be broadcast together " \
            "with shapes " + str(x['output_shape']) + ", " + \
            str(y['output_shape'])

    y_size = x_size = 1
    for i in x['output_shape']:
        x_size *= i
    for i in y['output_shape']:
        y_size *= i
    if x_size >= y_size:
        output_shape = x['output_shape'][:]
    else:
        output_shape = y['output_shape'][:]

    return output_shape


def fully_connected_shape(node_input, node_weights):
    output_shape = []
    for i in node_input['output_shape'][0:-1]:
        output_shape.append(i)
    for i in node_weights['output_shape'][1:]:
        output_shape.append(i)
    return output_shape


def split_shape(begin, end, split_axis):
    return [end[i] - begin[i] if i == split_axis else end[i]
            for i in range(len(end))]


def concat_shape(nodes, axis):
    output_shape = nodes[0]['output_shape'][:]
    for node in nodes[1:]:
        output_shape[axis] += node['output_shape'][axis]
    return output_shape


def slice_shape(input_shape, axes, begin, end):
    output_shape = input_shape[:]
    for i in range(len(axes)):
        shape = int(end[i] - begin[i])
        if shape > 0:
            output_shape[i] = shape
    return output_shape
