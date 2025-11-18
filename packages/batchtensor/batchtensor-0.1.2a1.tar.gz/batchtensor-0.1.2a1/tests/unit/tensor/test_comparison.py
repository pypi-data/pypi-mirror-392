from __future__ import annotations

import torch
from coola import objects_are_equal

from batchtensor.tensor import (
    argsort_along_batch,
    argsort_along_seq,
    sort_along_batch,
    sort_along_seq,
)
from tests.conftest import torch_greater_equal_1_13

#########################################
#     Tests for argsort_along_batch     #
#########################################


def test_argsort_along_batch_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
    )


def test_argsort_along_batch_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]), descending=True
        ),
        torch.tensor([[3, 0], [0, 4], [4, 1], [2, 3], [1, 2]]),
    )


@torch_greater_equal_1_13
def test_argsort_along_batch_stable_true() -> None:
    assert objects_are_equal(
        argsort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]), stable=True),
        torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
    )


#######################################
#     Tests for argsort_along_seq     #
#######################################


def test_argsort_along_seq_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
    )


def test_argsort_along_seq_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]), descending=True),
        torch.tensor([[3, 0, 4, 2, 1], [0, 4, 1, 3, 2]]),
    )


@torch_greater_equal_1_13
def test_argsort_along_seq_stable_true() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]), stable=True),
        torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
    )


######################################
#     Tests for sort_along_batch     #
######################################


def test_sort_along_batch_descending_false() -> None:
    assert objects_are_equal(
        sort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        torch.return_types.sort(
            [
                torch.tensor([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
                torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
            ]
        ),
    )


def test_sort_along_batch_descending_true() -> None:
    assert objects_are_equal(
        sort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]), descending=True),
        torch.return_types.sort(
            [
                torch.tensor([[5, 9], [4, 8], [3, 7], [2, 6], [1, 5]]),
                torch.tensor([[3, 0], [0, 4], [4, 1], [2, 3], [1, 2]]),
            ]
        ),
    )


@torch_greater_equal_1_13
def test_sort_along_batch_stable_true() -> None:
    assert objects_are_equal(
        sort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [2, 9]]), stable=True),
        torch.return_types.sort(
            [
                torch.tensor([[1, 5], [2, 6], [2, 7], [4, 9], [5, 9]]),
                torch.tensor([[1, 2], [2, 3], [4, 1], [0, 0], [3, 4]]),
            ]
        ),
    )


####################################
#     Tests for sort_along_seq     #
####################################


def test_sort_along_seq_descending_false() -> None:
    assert objects_are_equal(
        sort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        torch.return_types.sort(
            [
                torch.tensor([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
                torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
            ]
        ),
    )


def test_sort_along_seq_descending_true() -> None:
    assert objects_are_equal(
        sort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]), descending=True),
        torch.return_types.sort(
            [
                torch.tensor([[5, 4, 3, 2, 1], [9, 8, 7, 6, 5]]),
                torch.tensor([[3, 0, 4, 2, 1], [0, 4, 1, 3, 2]]),
            ]
        ),
    )


@torch_greater_equal_1_13
def test_sort_along_seq_stable_true() -> None:
    assert objects_are_equal(
        sort_along_seq(torch.tensor([[4, 1, 3, 5, 3], [9, 7, 5, 6, 9]]), stable=True),
        torch.return_types.sort(
            [
                torch.tensor([[1, 3, 3, 4, 5], [5, 6, 7, 9, 9]]),
                torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 0, 4]]),
            ]
        ),
    )
