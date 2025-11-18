from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping
from typing import Any
from unittest.mock import Mock, patch

import pytest
import torch
from coola import objects_are_equal

from batchtensor.utils.bfs import (
    DefaultTensorIterator,
    IterableTensorIterator,
    IteratorState,
    MappingTensorIterator,
    TensorIterator,
    bfs_tensor,
)


@pytest.fixture
def state() -> IteratorState:
    return IteratorState(iterator=TensorIterator(), queue=deque())


################################
#     Tests for bfs_tensor     #
################################


def test_bfs_tensor_tensor() -> None:
    assert objects_are_equal(list(bfs_tensor(torch.ones(2, 3))), [torch.ones(2, 3)])


@pytest.mark.parametrize(
    "data",
    [
        pytest.param("abc", id="string"),
        pytest.param(42, id="int"),
        pytest.param(4.2, id="float"),
        pytest.param([1, 2, 3], id="list"),
        pytest.param([], id="empty list"),
        pytest.param(("a", "b", "c"), id="tuple"),
        pytest.param((), id="empty tuple"),
        pytest.param({1, 2, 3}, id="set"),
        pytest.param(set(), id="empty set"),
        pytest.param({"key1": 1, "key2": 2, "key3": 3}, id="dict"),
        pytest.param({}, id="empty dict"),
    ],
)
def test_bfs_tensor_no_tensor(data: Any) -> None:
    assert objects_are_equal(list(bfs_tensor(data)), [])


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            [torch.ones(2, 3), torch.tensor([0, 1, 2, 3, 4])], id="list with only tensors"
        ),
        pytest.param(
            ["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])],
            id="list with non tensor objects",
        ),
        pytest.param(
            (torch.ones(2, 3), torch.tensor([0, 1, 2, 3, 4])), id="tuple with only tensors"
        ),
        pytest.param(
            ("abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])),
            id="tuple with non tensor objects",
        ),
        pytest.param(
            {"key1": torch.ones(2, 3), "key2": torch.tensor([0, 1, 2, 3, 4])},
            id="dict with only tensors",
        ),
        pytest.param(
            {
                "key1": "abc",
                "key2": torch.ones(2, 3),
                "key3": 42,
                "key4": torch.tensor([0, 1, 2, 3, 4]),
            },
            id="dict with non tensor objects",
        ),
    ],
)
def test_bfs_tensor_iterable_tensor(data: Any) -> None:
    assert objects_are_equal(
        list(bfs_tensor(data)), [torch.ones(2, 3), torch.tensor([0, 1, 2, 3, 4])]
    )


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({torch.ones(2, 3), torch.tensor([0, 1, 2, 3, 4])}, id="set with only tensors"),
        pytest.param(
            {"abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])},
            id="set with non tensor objects",
        ),
    ],
)
def test_bfs_tensor_set(data: Any) -> None:
    assert len(list(bfs_tensor(data))) == 2


def test_bfs_tensor_nested_data() -> None:
    data = [
        {"key1": torch.zeros(1, 1, 1), "key2": torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])},
        torch.ones(2, 3),
        [torch.ones(4), torch.tensor([0, -1, -2]), [torch.ones(5)]],
        (1, torch.tensor([42.0]), torch.zeros(2)),
        torch.tensor([0, 1, 2, 3, 4]),
    ]
    assert objects_are_equal(
        list(bfs_tensor(data)),
        [
            torch.ones(2, 3),
            torch.tensor([0, 1, 2, 3, 4]),
            torch.zeros(1, 1, 1),
            torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            torch.ones(4),
            torch.tensor([0, -1, -2]),
            torch.tensor([42.0]),
            torch.zeros(2),
            torch.ones(5),
        ],
    )


###########################################
#     Tests for DefaultTensorIterator     #
###########################################


def test_default_tensor_iterator_str() -> None:
    assert str(DefaultTensorIterator()).startswith("DefaultTensorIterator(")


def test_default_tensor_iterator_iterable(state: IteratorState) -> None:
    DefaultTensorIterator().iterate("abc", state)
    assert state.queue == deque()


############################################
#     Tests for IterableTensorIterator     #
############################################


def test_iterable_tensor_iterator_str() -> None:
    assert str(IterableTensorIterator()).startswith("IterableTensorIterator(")


@pytest.mark.parametrize(
    "data",
    [
        pytest.param([], id="empty list"),
        pytest.param((), id="empty tuple"),
        pytest.param(set(), id="empty set"),
        pytest.param(deque(), id="empty deque"),
    ],
)
def test_iterable_tensor_iterator_iterate_empty(data: Iterable, state: IteratorState) -> None:
    IterableTensorIterator().iterate(data, state)
    assert state.queue == deque()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])], id="list"),
        pytest.param(
            deque(["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])]), id="deque"
        ),
        pytest.param(("abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])), id="tuple"),
    ],
)
def test_iterable_tensor_iterator_iterate(data: Iterable, state: IteratorState) -> None:
    IterableTensorIterator().iterate(data, state)
    assert objects_are_equal(
        list(state.queue), ["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])]
    )


###########################################
#     Tests for MappingTensorIterator     #
###########################################


def test_mapping_tensor_iterator_str() -> None:
    assert str(MappingTensorIterator()).startswith("MappingTensorIterator(")


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({}, id="empty dict"),
        pytest.param(OrderedDict(), id="empty OrderedDict"),
    ],
)
def test_mapping_tensor_iterator_iterate_empty(data: Mapping, state: IteratorState) -> None:
    MappingTensorIterator().iterate(data, state)
    assert state.queue == deque()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(
            {
                "key1": "abc",
                "key2": torch.ones(2, 3),
                "key3": 42,
                "key4": torch.tensor([0, 1, 2, 3, 4]),
            },
            id="dict",
        ),
        pytest.param(
            OrderedDict(
                {
                    "key1": "abc",
                    "key2": torch.ones(2, 3),
                    "key3": 42,
                    "key4": torch.tensor([0, 1, 2, 3, 4]),
                }
            ),
            id="OrderedDict",
        ),
    ],
)
def test_mapping_tensor_iterator_iterate(data: Mapping, state: IteratorState) -> None:
    MappingTensorIterator().iterate(data, state)
    assert objects_are_equal(
        list(state.queue), ["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])]
    )


####################################
#     Tests for TensorIterator     #
####################################


def test_iterator_str() -> None:
    assert str(TensorIterator()).startswith("TensorIterator(")


@patch.dict(TensorIterator.registry, {}, clear=True)
def test_iterator_add_iterator() -> None:
    iterator = TensorIterator()
    seq_iterator = IterableTensorIterator()
    iterator.add_iterator(list, seq_iterator)
    assert iterator.registry[list] is seq_iterator


@patch.dict(TensorIterator.registry, {}, clear=True)
def test_iterator_add_iterator_duplicate_exist_ok_true() -> None:
    iterator = TensorIterator()
    seq_iterator = IterableTensorIterator()
    iterator.add_iterator(list, DefaultTensorIterator())
    iterator.add_iterator(list, seq_iterator, exist_ok=True)
    assert iterator.registry[list] is seq_iterator


@patch.dict(TensorIterator.registry, {}, clear=True)
def test_iterator_add_iterator_duplicate_exist_ok_false() -> None:
    iterator = TensorIterator()
    seq_iterator = IterableTensorIterator()
    iterator.add_iterator(list, DefaultTensorIterator())
    with pytest.raises(RuntimeError, match=r"An iterator (.*) is already registered"):
        iterator.add_iterator(list, seq_iterator)


def test_iterator_iterate(state: IteratorState) -> None:
    TensorIterator().iterate(
        ["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])], state=state
    )
    assert objects_are_equal(
        list(state.queue), ["abc", torch.ones(2, 3), 42, torch.tensor([0, 1, 2, 3, 4])]
    )


def test_iterator_has_iterator_true() -> None:
    assert TensorIterator().has_iterator(list)


def test_iterator_has_iterator_false() -> None:
    assert not TensorIterator().has_iterator(type(None))


def test_iterator_find_iterator_direct() -> None:
    assert isinstance(TensorIterator().find_iterator(list), IterableTensorIterator)


def test_iterator_find_iterator_indirect() -> None:
    assert isinstance(TensorIterator().find_iterator(str), DefaultTensorIterator)


def test_iterator_find_iterator_incorrect_type() -> None:
    with pytest.raises(TypeError, match=r"Incorrect data type:"):
        TensorIterator().find_iterator(Mock(__mro__=[]))


def test_iterator_registry_default() -> None:
    assert len(TensorIterator.registry) >= 9
    assert isinstance(TensorIterator.registry[Iterable], IterableTensorIterator)
    assert isinstance(TensorIterator.registry[Mapping], MappingTensorIterator)
    assert isinstance(TensorIterator.registry[deque], IterableTensorIterator)
    assert isinstance(TensorIterator.registry[dict], MappingTensorIterator)
    assert isinstance(TensorIterator.registry[list], IterableTensorIterator)
    assert isinstance(TensorIterator.registry[object], DefaultTensorIterator)
    assert isinstance(TensorIterator.registry[set], IterableTensorIterator)
    assert isinstance(TensorIterator.registry[str], DefaultTensorIterator)
    assert isinstance(TensorIterator.registry[tuple], IterableTensorIterator)
