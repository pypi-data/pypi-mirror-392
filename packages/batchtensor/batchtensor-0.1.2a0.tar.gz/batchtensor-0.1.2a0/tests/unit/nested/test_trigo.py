from collections.abc import Callable

import pytest
import torch
from coola import objects_are_allclose

from batchtensor import nested

DTYPES = [torch.float, torch.double, torch.long]
POINTWISE_FUNCTIONS = [
    (torch.acos, nested.acos),
    (torch.acosh, nested.acosh),
    (torch.asin, nested.asin),
    (torch.asinh, nested.asinh),
    (torch.atan, nested.atan),
    (torch.atanh, nested.atanh),
    (torch.cos, nested.cos),
    (torch.cosh, nested.cosh),
    (torch.sin, nested.sin),
    (torch.sinh, nested.sinh),
    (torch.tan, nested.tan),
    (torch.tanh, nested.tanh),
]


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_pointwise_function_tensor(
    dtype: torch.dtype, functions: tuple[Callable, Callable]
) -> None:
    torch_fn, nested_fn = functions
    tensor = torch.randn(5, 2).to(dtype=dtype)
    assert objects_are_allclose(nested_fn(tensor), torch_fn(tensor), equal_nan=True)
