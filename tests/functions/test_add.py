import numpy as np
from mindtorch import Tensor

def test_radd():
    x = Tensor(np.array(2.0))
    y = x + 3.0
    print(y)

def test_add():
    x = Tensor(np.array(2.0))
    y = 3.0 + x
    print(y)