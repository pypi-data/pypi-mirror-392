from collections.abc import Callable
from functools import partial

import pytest
import torch
from coola import objects_are_equal

from batchtensor import nested

DTYPES = [torch.float, torch.double, torch.long]
POINTWISE_FUNCTIONS = [
    (torch.abs, nested.abs),
    (partial(torch.clamp, min=2), partial(nested.clamp, min=2)),
    (partial(torch.clamp, max=6), partial(nested.clamp, max=6)),
    (partial(torch.clamp, min=2, max=6), partial(nested.clamp, min=2, max=6)),
    (torch.exp, nested.exp),
    (torch.exp2, nested.exp2),
    (torch.expm1, nested.expm1),
    (torch.log, nested.log),
    (torch.log2, nested.log2),
    (torch.log10, nested.log10),
    (torch.log1p, nested.log1p),
]


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_pointwise_function_tensor(
    dtype: torch.dtype, functions: tuple[Callable, Callable]
) -> None:
    torch_fn, nested_fn = functions
    tensor = torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)
    assert objects_are_equal(nested_fn(tensor), torch_fn(tensor))


@pytest.mark.parametrize("dtype", DTYPES)
@pytest.mark.parametrize("functions", POINTWISE_FUNCTIONS)
def test_cumprod_along_batch_dict(dtype: torch.dtype, functions: tuple[Callable, Callable]) -> None:
    torch_fn, nested_fn = functions
    assert objects_are_equal(
        nested_fn(
            {
                "a": torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "c": [torch.tensor([5, 6, 7, 8, 9], dtype=torch.float)],
            },
        ),
        {
            "a": torch_fn(torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
            "b": torch_fn(torch.tensor([4, 3, 2, 1, 0], dtype=torch.float)),
            "c": [torch_fn(torch.tensor([5, 6, 7, 8, 9], dtype=torch.float))],
        },
    )
