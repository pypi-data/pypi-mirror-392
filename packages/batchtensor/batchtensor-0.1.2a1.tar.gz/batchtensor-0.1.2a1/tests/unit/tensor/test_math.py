from __future__ import annotations

import pytest
import torch
from coola import objects_are_equal

from batchtensor.tensor import (
    cumprod_along_batch,
    cumprod_along_seq,
    cumsum_along_batch,
    cumsum_along_seq,
)

DTYPES = [torch.float, torch.double, torch.long]


#########################################
#     Tests for cumprod_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_batch(torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
        torch.tensor([[1, 2], [3, 8], [15, 48], [105, 384], [945, 3840]], dtype=dtype),
    )


#######################################
#     Tests for cumprod_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_seq(torch.tensor([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype)),
        torch.tensor([[1, 2, 6, 24, 120], [6, 42, 336, 3024, 30240]], dtype=dtype),
    )


########################################
#     Tests for cumsum_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([[0, 1], [2, 4], [6, 9], [12, 16], [20, 25]], dtype=dtype),
    )


######################################
#     Tests for cumsum_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([[0, 1, 3, 6, 10], [5, 11, 18, 26, 35]], dtype=dtype),
    )
