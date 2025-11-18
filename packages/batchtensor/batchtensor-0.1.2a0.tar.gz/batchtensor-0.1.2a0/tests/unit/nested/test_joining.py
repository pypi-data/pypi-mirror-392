from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch
from coola import objects_are_equal

from batchtensor.nested import cat_along_batch, cat_along_seq, repeat_along_seq

if TYPE_CHECKING:
    from collections.abc import Hashable, Sequence

#####################################
#     Tests for cat_along_batch     #
#####################################


@pytest.mark.parametrize(
    "data",
    [
        [
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {"a": torch.tensor([[10, 11, 12], [14, 15, 16]]), "b": torch.tensor([[17], [18]])},
        ],
        (
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {"a": torch.tensor([[10, 11, 12], [14, 15, 16]]), "b": torch.tensor([[17], [18]])},
        ),
        [
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {"a": torch.tensor([[10, 11, 12]]), "b": torch.tensor([[17]])},
            {"a": torch.tensor([[14, 15, 16]]), "b": torch.tensor([[18]])},
        ],
    ],
)
def test_cat_along_batch(data: Sequence[dict[Hashable, torch.Tensor]]) -> None:
    assert objects_are_equal(
        cat_along_batch(data),
        {
            "a": torch.tensor([[0, 1, 2], [4, 5, 6], [10, 11, 12], [14, 15, 16]]),
            "b": torch.tensor([[7], [8], [17], [18]]),
        },
    )


def test_cat_along_batch_empty() -> None:
    assert objects_are_equal(cat_along_batch([]), {})


###################################
#     Tests for cat_along_seq     #
###################################


@pytest.mark.parametrize(
    "data",
    [
        [
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {
                "a": torch.tensor([[10, 11, 12], [13, 14, 15]]),
                "b": torch.tensor([[17, 18], [18, 19]]),
            },
        ],
        (
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {
                "a": torch.tensor([[10, 11, 12], [13, 14, 15]]),
                "b": torch.tensor([[17, 18], [18, 19]]),
            },
        ),
        [
            {"a": torch.tensor([[0, 1, 2], [4, 5, 6]]), "b": torch.tensor([[7], [8]])},
            {"a": torch.tensor([[10, 11], [13, 14]]), "b": torch.tensor([[17], [18]])},
            {"a": torch.tensor([[12], [15]]), "b": torch.tensor([[18], [19]])},
        ],
    ],
)
def test_cat_along_seq(data: Sequence[dict[Hashable, torch.Tensor]]) -> None:
    assert objects_are_equal(
        cat_along_seq(data),
        {
            "a": torch.tensor([[0, 1, 2, 10, 11, 12], [4, 5, 6, 13, 14, 15]]),
            "b": torch.tensor([[7, 17, 18], [8, 18, 19]]),
        },
    )


def test_cat_along_seq_empty() -> None:
    assert objects_are_equal(cat_along_seq([]), {})


######################################
#     Tests for repeat_along_seq     #
######################################


def test_repeat_along_seq_tensor_repeats_0() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]), repeats=0
        ),
        torch.zeros(2, 0),
    )


def test_repeat_along_seq_tensor_repeats_1() -> None:
    assert objects_are_equal(
        repeat_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), repeats=1),
        torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
    )


def test_repeat_along_seq_tensor_repeats_2() -> None:
    assert objects_are_equal(
        repeat_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), repeats=2),
        torch.tensor([[0, 1, 2, 3, 4, 0, 1, 2, 3, 4], [5, 6, 7, 8, 9, 5, 6, 7, 8, 9]]),
    )


def test_repeat_along_seq_tensor_repeats_3d() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            torch.tensor(
                [
                    [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
                    [[10, 11], [12, 13], [14, 15], [16, 17], [18, 19]],
                ]
            ),
            repeats=2,
        ),
        torch.tensor(
            [
                [
                    [0, 1],
                    [2, 3],
                    [4, 5],
                    [6, 7],
                    [8, 9],
                    [0, 1],
                    [2, 3],
                    [4, 5],
                    [6, 7],
                    [8, 9],
                ],
                [
                    [10, 11],
                    [12, 13],
                    [14, 15],
                    [16, 17],
                    [18, 19],
                    [10, 11],
                    [12, 13],
                    [14, 15],
                    [16, 17],
                    [18, 19],
                ],
            ]
        ),
    )


def test_repeat_along_seq_dict_repeats_0() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            repeats=0,
        ),
        {"a": torch.zeros(2, 0, dtype=torch.long), "b": torch.zeros(1, 0, dtype=torch.long)},
    )


def test_repeat_along_seq_dict_repeats_1() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            repeats=1,
        ),
        {
            "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
            "b": torch.tensor([[4, 3, 2, 1, 0]]),
        },
    )


def test_repeat_along_seq_dict_repeats_2() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            repeats=2,
        ),
        {
            "a": torch.tensor([[0, 1, 2, 3, 4, 0, 1, 2, 3, 4], [5, 6, 7, 8, 9, 5, 6, 7, 8, 9]]),
            "b": torch.tensor([[4, 3, 2, 1, 0, 4, 3, 2, 1, 0]]),
        },
    )


def test_repeat_along_seq_dict_repeats_3d() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            {
                "a": torch.tensor(
                    [
                        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
                        [[10, 11], [12, 13], [14, 15], [16, 17], [18, 19]],
                    ]
                ),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            repeats=2,
        ),
        {
            "a": torch.tensor(
                [
                    [
                        [0, 1],
                        [2, 3],
                        [4, 5],
                        [6, 7],
                        [8, 9],
                        [0, 1],
                        [2, 3],
                        [4, 5],
                        [6, 7],
                        [8, 9],
                    ],
                    [
                        [10, 11],
                        [12, 13],
                        [14, 15],
                        [16, 17],
                        [18, 19],
                        [10, 11],
                        [12, 13],
                        [14, 15],
                        [16, 17],
                        [18, 19],
                    ],
                ]
            ),
            "b": torch.tensor([[4, 3, 2, 1, 0, 4, 3, 2, 1, 0]]),
        },
    )


def test_repeat_along_seq_dict_nested() -> None:
    assert objects_are_equal(
        repeat_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "list": [torch.tensor([[5, 6, 7, 8, 9]])],
            },
            repeats=2,
        ),
        {
            "a": torch.tensor([[0, 1, 2, 3, 4, 0, 1, 2, 3, 4], [5, 6, 7, 8, 9, 5, 6, 7, 8, 9]]),
            "b": torch.tensor([[4, 3, 2, 1, 0, 4, 3, 2, 1, 0]]),
            "list": [torch.tensor([[5, 6, 7, 8, 9, 5, 6, 7, 8, 9]])],
        },
    )
