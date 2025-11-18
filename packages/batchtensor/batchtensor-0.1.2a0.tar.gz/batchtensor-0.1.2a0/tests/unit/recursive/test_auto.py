from __future__ import annotations

from collections.abc import Mapping, Sequence
from unittest.mock import Mock, patch

import pytest
from coola import objects_are_equal

from batchtensor.recursive import (
    ApplyState,
    AutoApplier,
    DefaultApplier,
    MappingApplier,
    SequenceApplier,
)


@pytest.fixture
def state() -> ApplyState:
    return ApplyState(applier=AutoApplier())


#################################
#     Tests for AutoApplier     #
#################################


def test_auto_applier_str() -> None:
    assert str(AutoApplier()).startswith("AutoApplier(")


@patch.dict(AutoApplier.registry, {}, clear=True)
def test_auto_applier_add_applier() -> None:
    applier = AutoApplier()
    seq_applier = SequenceApplier()
    applier.add_applier(list, seq_applier)
    assert applier.registry[list] is seq_applier


@patch.dict(AutoApplier.registry, {}, clear=True)
def test_auto_applier_add_applier_duplicate_exist_ok_true() -> None:
    applier = AutoApplier()
    seq_applier = SequenceApplier()
    applier.add_applier(list, MappingApplier())
    applier.add_applier(list, seq_applier, exist_ok=True)
    assert applier.registry[list] == seq_applier


@patch.dict(AutoApplier.registry, {}, clear=True)
def test_auto_applier_add_applier_duplicate_exist_ok_false() -> None:
    applier = AutoApplier()
    seq_applier = SequenceApplier()
    applier.add_applier(list, MappingApplier())
    with pytest.raises(RuntimeError, match=r"An applier (.*) is already registered"):
        applier.add_applier(list, seq_applier)


def test_auto_applier_apply(state: ApplyState) -> None:
    assert objects_are_equal(AutoApplier().apply([1, "abc"], str, state=state), ["1", "abc"])


def test_auto_applier_apply_nested(state: ApplyState) -> None:
    assert objects_are_equal(
        AutoApplier().apply(
            {"list": [1, "abc"], "set": {1, 2, 3}, "dict": {"a": 1, "b": "abc"}}, str, state=state
        ),
        {"list": ["1", "abc"], "set": {"1", "2", "3"}, "dict": {"a": "1", "b": "abc"}},
    )


def test_auto_applier_has_applier_true() -> None:
    assert AutoApplier().has_applier(dict)


def test_auto_applier_has_applier_false() -> None:
    assert not AutoApplier().has_applier(type(None))


def test_auto_applier_find_applier_direct() -> None:
    assert isinstance(AutoApplier().find_applier(dict), MappingApplier)


def test_auto_applier_find_applier_indirect() -> None:
    assert isinstance(AutoApplier().find_applier(str), DefaultApplier)


def test_auto_applier_find_applier_incorrect_type() -> None:
    with pytest.raises(TypeError, match=r"Incorrect data type:"):
        AutoApplier().find_applier(Mock(__mro__=[]))


def test_auto_applier_registry_default() -> None:
    assert len(AutoApplier.registry) >= 7
    assert isinstance(AutoApplier.registry[Mapping], MappingApplier)
    assert isinstance(AutoApplier.registry[Sequence], SequenceApplier)
    assert isinstance(AutoApplier.registry[dict], MappingApplier)
    assert isinstance(AutoApplier.registry[list], SequenceApplier)
    assert isinstance(AutoApplier.registry[object], DefaultApplier)
    assert isinstance(AutoApplier.registry[set], SequenceApplier)
    assert isinstance(AutoApplier.registry[tuple], SequenceApplier)
