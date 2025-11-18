from __future__ import annotations

from unittest.mock import patch

import pytest
import torch
from coola import objects_are_equal

from batchtensor.nested import (
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
def test_permute_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        torch.tensor([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        {
            "a": torch.tensor([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
            "b": torch.tensor([0, 1, 2, 3, 4]),
        },
    )


def test_permute_along_batch_nested() -> None:
    assert objects_are_equal(
        permute_along_batch(
            {
                "a": torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "list": [torch.tensor([5, 6, 7, 8, 9])],
            },
            permutation=torch.tensor([2, 4, 1, 3, 0]),
        ),
        {
            "a": torch.tensor([[2, 5], [3, 8], [1, 7], [5, 6], [4, 9]]),
            "b": torch.tensor([2, 0, 3, 1, 4], dtype=torch.float),
            "list": [torch.tensor([7, 9, 6, 8, 5])],
        },
    )


def test_permute_along_batch_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with tensor shape \(.*\)",
    ):
        permute_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            torch.tensor([4, 3, 2, 1, 0, 2]),
        )


#######################################
#     Tests for permute_along_seq     #
#######################################


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        torch.tensor([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
    )


@pytest.mark.parametrize("dtype", INDEX_DTYPES)
def test_permute_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        permute_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            torch.tensor([4, 3, 2, 1, 0], dtype=dtype),
        ),
        {
            "a": torch.tensor([[4, 3, 2, 1, 0], [9, 8, 7, 6, 5]]),
            "b": torch.tensor([[0, 1, 2, 3, 4]]),
        },
    )


def test_permute_along_seq_nested() -> None:
    assert objects_are_equal(
        permute_along_seq(
            {
                "a": torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                "list": [torch.tensor([[5, 6, 7, 8, 9]])],
            },
            permutation=torch.tensor([2, 4, 1, 3, 0]),
        ),
        {
            "a": torch.tensor([[2, 3, 1, 5, 4], [5, 8, 7, 6, 9]]),
            "b": torch.tensor([[2, 0, 3, 1, 4]], dtype=torch.float),
            "list": [torch.tensor([[7, 9, 6, 8, 5]])],
        },
    )


def test_permute_along_seq_incorrect_shape() -> None:
    with pytest.raises(
        RuntimeError,
        match=r"permutation shape \(.*\) is not compatible with tensor shape \(.*\)",
    ):
        permute_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            torch.tensor([4, 3, 2, 1, 0, 2]),
        )


#########################################
#     Tests for shuffle_along_batch     #
#########################################


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_batch_tensor() -> None:
    assert objects_are_equal(
        shuffle_along_batch(torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])),
        torch.tensor([[6, 7, 8], [3, 4, 5], [9, 10, 11], [0, 1, 2]]),
    )


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_batch_dict() -> None:
    assert objects_are_equal(
        shuffle_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": torch.tensor([[4, 5], [8, 9], [2, 3], [6, 7], [0, 1]]),
            "b": torch.tensor([2, 0, 3, 1, 4]),
        },
    )


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_batch_nested() -> None:
    assert objects_are_equal(
        shuffle_along_batch(
            {
                "a": torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "list": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.tensor([[2, 5], [3, 8], [1, 7], [5, 6], [4, 9]]),
            "b": torch.tensor([2, 0, 3, 1, 4], dtype=torch.float),
            "list": [torch.tensor([7, 9, 6, 8, 5])],
        },
    )


def test_shuffle_along_batch_same_random_seed() -> None:
    data = {
        "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
        "b": torch.tensor([4, 3, 2, 1, 0]),
    }
    assert objects_are_equal(
        shuffle_along_batch(data, get_torch_generator(1)),
        shuffle_along_batch(data, get_torch_generator(1)),
    )


def test_shuffle_along_batch_different_random_seeds() -> None:
    data = {
        "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
        "b": torch.tensor([4, 3, 2, 1, 0]),
    }
    assert not objects_are_equal(
        shuffle_along_batch(data, get_torch_generator(1)),
        shuffle_along_batch(data, get_torch_generator(2)),
    )


def test_shuffle_along_batch_multiple_shuffle() -> None:
    data = {
        "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
        "b": torch.tensor([4, 3, 2, 1, 0]),
    }
    generator = get_torch_generator(1)
    assert not objects_are_equal(
        shuffle_along_batch(data, generator), shuffle_along_batch(data, generator)
    )


#######################################
#     Tests for shuffle_along_seq     #
#######################################


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_seq_tensor() -> None:
    assert objects_are_equal(
        shuffle_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])),
        torch.tensor([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
    )


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_seq_dict() -> None:
    assert objects_are_equal(
        shuffle_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": torch.tensor([[2, 4, 1, 3, 0], [7, 9, 6, 8, 5]]),
            "b": torch.tensor([[2, 0, 3, 1, 4]]),
        },
    )


@patch(
    "batchtensor.nested.permutation.torch.randperm",
    lambda *args, **kwargs: torch.tensor([2, 4, 1, 3, 0]),  # noqa: ARG005
)
def test_shuffle_along_seq_nested() -> None:
    assert objects_are_equal(
        shuffle_along_seq(
            {
                "a": torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                "list": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.tensor([[2, 3, 1, 5, 4], [5, 8, 7, 6, 9]]),
            "b": torch.tensor([[2, 0, 3, 1, 4]], dtype=torch.float),
            "list": [torch.tensor([[7, 9, 6, 8, 5]])],
        },
    )


def test_shuffle_along_seq_same_random_seed() -> None:
    data = {
        "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
        "b": torch.tensor([[4, 3, 2, 1, 0]]),
    }
    assert objects_are_equal(
        shuffle_along_seq(data, get_torch_generator(1)),
        shuffle_along_seq(data, get_torch_generator(1)),
    )


def test_shuffle_along_seq_different_random_seeds() -> None:
    data = {
        "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
        "b": torch.tensor([[4, 3, 2, 1, 0]]),
    }
    assert not objects_are_equal(
        shuffle_along_seq(data, get_torch_generator(1)),
        shuffle_along_seq(data, get_torch_generator(2)),
    )


def test_shuffle_along_seq_multiple_shuffle() -> None:
    data = {
        "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
        "b": torch.tensor([[4, 3, 2, 1, 0]]),
    }
    generator = get_torch_generator(1)
    assert not objects_are_equal(
        shuffle_along_seq(data, generator), shuffle_along_seq(data, generator)
    )
