from __future__ import annotations

import pytest
import torch
from coola import objects_are_equal

from batchtensor.recursive import ApplyState, AutoApplier, SequenceApplier


@pytest.fixture
def state() -> ApplyState:
    return ApplyState(applier=AutoApplier())


#####################################
#     Tests for SequenceApplier     #
#####################################


def test_sequence_applier_str() -> None:
    assert str(SequenceApplier()) == "SequenceApplier()"


def test_sequence_applier_apply_str_list(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply([1, "abc"], str, state), ["1", "abc"])


def test_sequence_applier_apply_str_tuple(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply((1, "abc"), str, state), ("1", "abc"))


def test_sequence_applier_apply_str_set(state: ApplyState) -> None:
    assert objects_are_equal(SequenceApplier().apply({1, "abc"}, str, state), {"1", "abc"})


def test_sequence_applier_apply_tensor(state: ApplyState) -> None:
    assert objects_are_equal(
        SequenceApplier().apply(
            [torch.ones(2, 3), torch.ones(2), [torch.ones(2, 1)]],
            lambda tensor: tensor.shape,
            state,
        ),
        [torch.Size([2, 3]), torch.Size([2]), [torch.Size([2, 1])]],
    )
