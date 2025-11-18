from __future__ import annotations

import torch
from coola import objects_are_equal

from batchtensor.tensor import (
    chunk_along_batch,
    chunk_along_seq,
    select_along_batch,
    select_along_seq,
    slice_along_batch,
    slice_along_seq,
    split_along_batch,
    split_along_seq,
)

INDEX_DTYPES = [torch.int, torch.long]

#######################################
#     Tests for chunk_along_batch     #
#######################################


def test_chunk_along_batch_chunks_3() -> None:
    assert objects_are_equal(
        chunk_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), chunks=3),
        (
            torch.tensor([[0, 1], [2, 3]]),
            torch.tensor([[4, 5], [6, 7]]),
            torch.tensor([[8, 9]]),
        ),
    )


def test_chunk_along_batch_chunks_5() -> None:
    assert objects_are_equal(
        chunk_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), chunks=5),
        (
            torch.tensor([[0, 1]]),
            torch.tensor([[2, 3]]),
            torch.tensor([[4, 5]]),
            torch.tensor([[6, 7]]),
            torch.tensor([[8, 9]]),
        ),
    )


#####################################
#     Tests for chunk_along_seq     #
#####################################


def test_chunk_along_seq_chunks_3() -> None:
    assert objects_are_equal(
        chunk_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), chunks=3),
        (
            torch.tensor([[0, 1], [5, 6]]),
            torch.tensor([[2, 3], [7, 8]]),
            torch.tensor([[4], [9]]),
        ),
    )


def test_chunk_along_seq_chunks_5() -> None:
    assert objects_are_equal(
        chunk_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), chunks=5),
        (
            torch.tensor([[0], [5]]),
            torch.tensor([[1], [6]]),
            torch.tensor([[2], [7]]),
            torch.tensor([[3], [8]]),
            torch.tensor([[4], [9]]),
        ),
    )


########################################
#     Tests for select_along_batch     #
########################################


def test_select_along_batch() -> None:
    assert objects_are_equal(
        select_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), index=2),
        torch.tensor([4, 5]),
    )


######################################
#     Tests for select_along_seq     #
######################################


def test_select_along_seq() -> None:
    assert objects_are_equal(
        select_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), index=2),
        torch.tensor([2, 7]),
    )


#######################################
#     Tests for slice_along_batch     #
#######################################


def test_slice_along_batch() -> None:
    assert objects_are_equal(
        slice_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]])),
        torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_start_2() -> None:
    assert objects_are_equal(
        slice_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), start=2),
        torch.tensor([[4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_stop_3() -> None:
    assert objects_are_equal(
        slice_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), stop=3),
        torch.tensor([[0, 1], [2, 3], [4, 5]]),
    )


def test_slice_along_batch_stop_100() -> None:
    assert objects_are_equal(
        slice_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), stop=100),
        torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
    )


def test_slice_along_batch_step_2() -> None:
    assert objects_are_equal(
        slice_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), step=2),
        torch.tensor([[0, 1], [4, 5], [8, 9]]),
    )


def test_slice_along_batch_start_1_stop_4_step_2() -> None:
    assert objects_are_equal(
        slice_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), start=1, stop=4, step=2
        ),
        torch.tensor([[2, 3], [6, 7]]),
    )


#####################################
#     Tests for slice_along_seq     #
#####################################


def test_slice_along_seq() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]])),
        torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]),
    )


def test_slice_along_seq_start_2() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), start=2),
        torch.tensor([[2, 3, 4], [7, 6, 5]]),
    )


def test_slice_along_seq_stop_3() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), stop=3),
        torch.tensor([[0, 1, 2], [9, 8, 7]]),
    )


def test_slice_along_seq_stop_100() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), stop=100),
        torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]),
    )


def test_slice_along_seq_step_2() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [9, 8, 7, 6, 5]]), step=2),
        torch.tensor([[0, 2, 4], [9, 7, 5]]),
    )


def test_slice_along_seq_start_1_stop_4_step_2() -> None:
    assert objects_are_equal(
        slice_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), start=1, stop=4, step=2),
        torch.tensor([[1, 3], [6, 8]]),
    )


#######################################
#     Tests for split_along_batch     #
#######################################


def test_split_along_batch_split_size_1() -> None:
    assert objects_are_equal(
        split_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=1
        ),
        (
            torch.tensor([[0, 1]]),
            torch.tensor([[2, 3]]),
            torch.tensor([[4, 5]]),
            torch.tensor([[6, 7]]),
            torch.tensor([[8, 9]]),
        ),
    )


def test_split_along_batch_split_size_2() -> None:
    assert objects_are_equal(
        split_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=2
        ),
        (
            torch.tensor([[0, 1], [2, 3]]),
            torch.tensor([[4, 5], [6, 7]]),
            torch.tensor([[8, 9]]),
        ),
    )


def test_split_along_batch_split_size_list() -> None:
    assert objects_are_equal(
        split_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), split_size_or_sections=[2, 2, 1]
        ),
        (
            torch.tensor([[0, 1], [2, 3]]),
            torch.tensor([[4, 5], [6, 7]]),
            torch.tensor([[8, 9]]),
        ),
    )


#####################################
#     Tests for split_along_seq     #
#####################################


def test_split_along_seq_split_size_1() -> None:
    assert objects_are_equal(
        split_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=1),
        (
            torch.tensor([[0], [5]]),
            torch.tensor([[1], [6]]),
            torch.tensor([[2], [7]]),
            torch.tensor([[3], [8]]),
            torch.tensor([[4], [9]]),
        ),
    )


def test_split_along_seq_split_size_2() -> None:
    assert objects_are_equal(
        split_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=2),
        (
            torch.tensor([[0, 1], [5, 6]]),
            torch.tensor([[2, 3], [7, 8]]),
            torch.tensor([[4], [9]]),
        ),
    )


def test_split_along_seq_split_size_list() -> None:
    assert objects_are_equal(
        split_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]), split_size_or_sections=[2, 2, 1]
        ),
        (
            torch.tensor([[0, 1], [5, 6]]),
            torch.tensor([[2, 3], [7, 8]]),
            torch.tensor([[4], [9]]),
        ),
    )
