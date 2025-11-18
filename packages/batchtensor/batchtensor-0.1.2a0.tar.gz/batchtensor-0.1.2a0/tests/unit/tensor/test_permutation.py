from __future__ import annotations

from unittest.mock import patch

import pytest
import torch
from coola import objects_are_equal

from batchtensor.tensor import (
    permute_along_batch,
    permute_along_seq,
    shuffle_along_batch,
    shuffle_along_seq,
)
from batchtensor.utils.seed import get_torch_generator

INDEX_DTYPES = [torch.int, torch.long]

#########################################
#     Tests for permute_along_batch     #
#########################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        torch.tensor([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


def test_permute_along_batch_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with tensor shape \(.*\)",
    ):
        permute_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            torch.tensor([4, 3, 2, 1, 0, 2, 0]),
        )


#######################################
#     Tests for permute_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        torch.tensor([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


def test_permute_along_seq_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with tensor shape \(.*\)",
    ):
        permute_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), torch.tensor([4, 3, 2, 1, 0, 2, 0])
        )


#########################################
#     Tests for shuffle_along_batch     #
#########################################


@patch(
    "batchtensor.tensor.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_batch() -> None:
    assert objects_are_equal(
        shuffle_along_batch(torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])),
        torch.tensor([[6, 7, 8], [3, 4, 5], [9, 10, 11], [0, 1, 2]]),
    )


def test_shuffle_along_batch_same_random_seed() -> None:
    tensor = torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    assert objects_are_equal(
        shuffle_along_batch(tensor, get_torch_generator(1)),
        shuffle_along_batch(tensor, get_torch_generator(1)),
    )


def test_shuffle_along_batch_different_random_seeds() -> None:
    tensor = torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    assert not objects_are_equal(
        shuffle_along_batch(tensor, get_torch_generator(1)),
        shuffle_along_batch(tensor, get_torch_generator(2)),
    )


def test_shuffle_along_batch_multiple_shuffle() -> None:
    tensor = torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
    generator = get_torch_generator(1)
    assert not objects_are_equal(
        shuffle_along_batch(tensor, generator), shuffle_along_batch(tensor, generator)
    )


#######################################
#     Tests for shuffle_along_seq     #
#######################################


@patch(
    "batchtensor.tensor.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_seq() -> None:
    assert objects_are_equal(
        shuffle_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])),
        torch.tensor([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
    )


def test_shuffle_along_seq_same_random_seed() -> None:
    tensor = torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    assert objects_are_equal(
        shuffle_along_seq(tensor, get_torch_generator(1)),
        shuffle_along_seq(tensor, get_torch_generator(1)),
    )


def test_shuffle_along_seq_different_random_seeds() -> None:
    tensor = torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    assert not objects_are_equal(
        shuffle_along_seq(tensor, get_torch_generator(1)),
        shuffle_along_seq(tensor, get_torch_generator(2)),
    )


def test_shuffle_along_seq_multiple_shuffle() -> None:
    tensor = torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    generator = get_torch_generator(1)
    assert not objects_are_equal(
        shuffle_along_seq(tensor, generator), shuffle_along_seq(tensor, generator)
    )
