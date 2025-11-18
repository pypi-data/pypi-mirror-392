from __future__ import annotations

import pytest
import torch
from coola import objects_are_equal

from batchtensor.nested import (
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
def test_cumprod_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_batch(torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype)),
        torch.tensor([[1, 2], [3, 8], [15, 48], [105, 384], [945, 3840]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_batch(
            {
                "a": torch.tensor([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": torch.tensor([[1, 2], [3, 8], [15, 48], [105, 384], [945, 3840]], dtype=dtype),
            "b": torch.tensor([4, 12, 24, 24, 0]),
        },
    )


#######################################
#     Tests for cumprod_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_seq(torch.tensor([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype)),
        torch.tensor([[1, 2, 6, 24, 120], [6, 42, 336, 3024, 30240]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumprod_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumprod_along_seq(
            {
                "a": torch.tensor([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": torch.tensor([[1, 2, 6, 24, 120], [6, 42, 336, 3024, 30240]], dtype=dtype),
            "b": torch.tensor([[4, 12, 24, 24, 0]]),
        },
    )


########################################
#     Tests for cumsum_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([[0, 1], [2, 4], [6, 9], [12, 16], [20, 25]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": torch.tensor([[0, 1], [2, 4], [6, 9], [12, 16], [20, 25]], dtype=dtype),
            "b": torch.tensor([4, 7, 9, 10, 10]),
        },
    )


######################################
#     Tests for cumsum_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([[0, 1, 3, 6, 10], [5, 11, 18, 26, 35]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_cumsum_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        cumsum_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": torch.tensor([[0, 1, 3, 6, 10], [5, 11, 18, 26, 35]], dtype=dtype),
            "b": torch.tensor([[4, 7, 9, 10, 10]]),
        },
    )
