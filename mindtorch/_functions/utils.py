from mindtorch._operations import raw_sum, raw_squeeze

def argsort(arr):
    return [i for i, _ in sorted(enumerate(arr), key=lambda x: x[1])]

def reshape_sum_backward(gy, x_shape, axis, keepdims):
    """Reshape gradient appropriately for dezero.functions.sum's backward.

    Args:
        gy (dezero.Variable): Gradient variable from the output by backprop.
        x_shape (tuple): Shape used at sum function's forward.
        axis (None or int or tuple of ints): Axis used at sum function's
            forward.
        keepdims (bool): Keepdims used at sum function's forward.

    Returns:
        dezero.Variable: Gradient variable which is reshaped appropriately
    """
    ndim = len(x_shape)
    tupled_axis = axis
    if axis is None:
        tupled_axis = None
    elif not isinstance(axis, tuple):
        tupled_axis = (axis,)

    if not (ndim == 0 or tupled_axis is None or keepdims):
        actual_axis = [a if a >= 0 else a + ndim for a in tupled_axis]
        shape = list(gy.shape)
        for a in sorted(actual_axis):
            shape.insert(a, 1)
    else:
        shape = gy.shape

    gy = gy.reshape(shape)  # reshape
    return gy

def sum_to(x, shape):
    """Sum elements along axes to output an array of a given shape.

    Args:
        x (ndarray): Input array.
        shape:

    Returns:
        ndarray: Output array of the shape.
    """
    ndim = len(shape)
    lead = x.dim() - ndim
    lead_axis = tuple(range(lead))

    axis = tuple([i + lead for i, sx in enumerate(shape) if sx == 1])
    y = raw_sum(x, lead_axis + axis, keepdims=True)
    if lead > 0:
        y = raw_squeeze(y, lead_axis)
    return y


def slice_helper(slice_spec):
    if not isinstance(slice_spec, (list, tuple)):
        slice_spec = [slice_spec]

    begin, end, strides = (), (), ()
    index = 0

    new_axis_mask, shrink_axis_mask = 0, 0
    begin_mask, end_mask = 0, 0
    ellipsis_mask = 0

    for s in slice_spec:
        if isinstance(s, slice):
            if s.start is not None:
                begin += (s.start,)
            else:
                begin += (0,)
                begin_mask |= (1 << index)
            
            if s.stop is not None:
                end += (s.stop,)
            else:
                end += (0,)
                end_mask |= (1 << index)

            if s.step is not None:
                strides += (s.step,)
            else:
                strides += (1,)
        elif s is Ellipsis:
            begin += (0,)
            end += (0,)
            strides += (0,)
            ellipsis_mask |= (1 << index)
        elif s is None:
            begin += (0,)
            end += (0,)
            strides += (0,)
            new_axis_mask |= (1 << index)
        else:
            begin += (s,)
            end += (s + 1,)
            strides += (1,)
            shrink_axis_mask |= (1 << index)
        index += 1
        
    return begin, end, strides, begin_mask, end_mask, ellipsis_mask, new_axis_mask, shrink_axis_mask
