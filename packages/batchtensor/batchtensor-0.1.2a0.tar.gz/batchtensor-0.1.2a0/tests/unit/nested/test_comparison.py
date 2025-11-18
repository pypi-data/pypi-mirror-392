from __future__ import annotations

import torch
from coola import objects_are_equal

from batchtensor.nested import (
    argsort_along_batch,
    argsort_along_seq,
    sort_along_batch,
    sort_along_seq,
)
from tests.conftest import torch_greater_equal_1_13

#########################################
#     Tests for argsort_along_batch     #
#########################################


def test_argsort_along_batch_tensor_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
    )


def test_argsort_along_batch_tensor_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]), descending=True
        ),
        torch.tensor([[3, 0], [0, 4], [4, 1], [2, 3], [1, 2]]),
    )


@torch_greater_equal_1_13
def test_argsort_along_batch_tensor_stable_true() -> None:
    assert objects_are_equal(
        argsort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]), stable=True),
        torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
    )


def test_argsort_along_batch_dict_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": torch.tensor([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            }
        ),
        {
            "a": torch.tensor([[1, 3], [0, 1], [2, 0], [4, 4], [3, 2]]),
            "b": torch.tensor([4, 3, 2, 1, 0]),
        },
    )


def test_argsort_along_batch_dict_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": torch.tensor([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            },
            descending=True,
        ),
        {
            "a": torch.tensor([[3, 2], [4, 4], [2, 0], [0, 1], [1, 3]]),
            "b": torch.tensor([0, 1, 2, 3, 4]),
        },
    )


def test_argsort_along_batch_nested() -> None:
    assert objects_are_equal(
        argsort_along_batch(
            {
                "a": torch.tensor([[2, 6], [0, 3], [4, 9], [8, 1], [5, 7]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "list": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.tensor([[1, 3], [0, 1], [2, 0], [4, 4], [3, 2]]),
            "b": torch.tensor([4, 3, 2, 1, 0]),
            "list": [torch.tensor([0, 1, 2, 3, 4])],
        },
    )


#######################################
#     Tests for argsort_along_seq     #
#######################################


def test_argsort_along_seq_tensor_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
    )


def test_argsort_along_seq_tensor_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]), descending=True),
        torch.tensor([[3, 0, 4, 2, 1], [0, 4, 1, 3, 2]]),
    )


@torch_greater_equal_1_13
def test_argsort_along_seq_tensor_stable_true() -> None:
    assert objects_are_equal(
        argsort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]), stable=True),
        torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
    )


def test_argsort_along_seq_dict_descending_false() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": torch.tensor([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            }
        ),
        {
            "a": torch.tensor([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": torch.tensor([[4, 3, 2, 1, 0]]),
        },
    )


def test_argsort_along_seq_dict_descending_true() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": torch.tensor([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            },
            descending=True,
        ),
        {
            "a": torch.tensor([[3, 0, 4, 1, 2], [1, 2, 3, 4, 0]]),
            "b": torch.tensor([[0, 1, 2, 3, 4]]),
        },
    )


def test_argsort_along_seq_nested() -> None:
    assert objects_are_equal(
        argsort_along_seq(
            {
                "a": torch.tensor([[7, 3, 0, 8, 5], [1, 9, 6, 4, 2]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                "list": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.tensor([[2, 1, 4, 0, 3], [0, 4, 3, 2, 1]]),
            "b": torch.tensor([[4, 3, 2, 1, 0]]),
            "list": [torch.tensor([[0, 1, 2, 3, 4]])],
        },
    )


######################################
#     Tests for sort_along_batch     #
######################################


def test_sort_along_batch_tensor_descending_false() -> None:
    assert objects_are_equal(
        sort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]])),
        torch.return_types.sort(
            [
                torch.tensor([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
                torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
            ]
        ),
    )


def test_sort_along_batch_tensor_descending_true() -> None:
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
def test_sort_along_batch_tensor_stable_true() -> None:
    assert objects_are_equal(
        sort_along_batch(torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [2, 9]]), stable=True),
        torch.return_types.sort(
            [
                torch.tensor([[1, 5], [2, 6], [2, 7], [4, 9], [5, 9]]),
                torch.tensor([[1, 2], [2, 3], [4, 1], [0, 0], [3, 4]]),
            ]
        ),
    )


def test_sort_along_batch_dict_descending_false() -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            }
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
                    torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([0, 1, 2, 3, 4], dtype=torch.float),
                    torch.tensor([4, 3, 2, 1, 0]),
                ]
            ),
        },
    )


def test_sort_along_batch_dict_descending_true() -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            },
            descending=True,
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[5, 9], [4, 8], [3, 7], [2, 6], [1, 5]]),
                    torch.tensor([[3, 0], [0, 4], [4, 1], [2, 3], [1, 2]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                    torch.tensor([0, 1, 2, 3, 4]),
                ]
            ),
        },
    )


def test_sort_along_batch_nested() -> None:
    assert objects_are_equal(
        sort_along_batch(
            {
                "a": torch.tensor([[4, 9], [1, 7], [2, 5], [5, 6], [3, 8]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "list": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[1, 5], [2, 6], [3, 7], [4, 8], [5, 9]]),
                    torch.tensor([[1, 2], [2, 3], [4, 1], [0, 4], [3, 0]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([0, 1, 2, 3, 4], dtype=torch.float),
                    torch.tensor([4, 3, 2, 1, 0]),
                ]
            ),
            "list": [
                torch.return_types.sort(
                    [
                        torch.tensor([5, 6, 7, 8, 9]),
                        torch.tensor([0, 1, 2, 3, 4]),
                    ]
                )
            ],
        },
    )


####################################
#     Tests for sort_along_seq     #
####################################


def test_sort_along_seq_tensor_descending_false() -> None:
    assert objects_are_equal(
        sort_along_seq(torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]])),
        torch.return_types.sort(
            [
                torch.tensor([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
                torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
            ]
        ),
    )


def test_sort_along_seq_tensor_descending_true() -> None:
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
def test_sort_along_seq_tensor_stable_true() -> None:
    assert objects_are_equal(
        sort_along_seq(torch.tensor([[4, 1, 3, 5, 3], [9, 7, 5, 6, 9]]), stable=True),
        torch.return_types.sort(
            [
                torch.tensor([[1, 3, 3, 4, 5], [5, 6, 7, 9, 9]]),
                torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 0, 4]]),
            ]
        ),
    )


def test_sort_along_seq_dict_descending_false() -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            }
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
                    torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([[0, 1, 2, 3, 4]], dtype=torch.float),
                    torch.tensor([[4, 3, 2, 1, 0]]),
                ]
            ),
        },
    )


def test_sort_along_seq_dict_descending_true() -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            },
            descending=True,
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[5, 4, 3, 2, 1], [9, 8, 7, 6, 5]]),
                    torch.tensor([[3, 0, 4, 2, 1], [0, 4, 1, 3, 2]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                    torch.tensor([[0, 1, 2, 3, 4]]),
                ]
            ),
        },
    )


def test_sort_along_seq_nested() -> None:
    assert objects_are_equal(
        sort_along_seq(
            {
                "a": torch.tensor([[4, 1, 2, 5, 3], [9, 7, 5, 6, 8]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                "list": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.return_types.sort(
                [
                    torch.tensor([[1, 2, 3, 4, 5], [5, 6, 7, 8, 9]]),
                    torch.tensor([[1, 2, 4, 0, 3], [2, 3, 1, 4, 0]]),
                ]
            ),
            "b": torch.return_types.sort(
                [
                    torch.tensor([[0, 1, 2, 3, 4]], dtype=torch.float),
                    torch.tensor([[4, 3, 2, 1, 0]]),
                ]
            ),
            "list": [
                torch.return_types.sort(
                    [
                        torch.tensor([[5, 6, 7, 8, 9]]),
                        torch.tensor([[0, 1, 2, 3, 4]]),
                    ]
                )
            ],
        },
    )
