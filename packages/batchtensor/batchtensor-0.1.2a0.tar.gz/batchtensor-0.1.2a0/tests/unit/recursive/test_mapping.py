from __future__ import annotations

from collections import OrderedDict

import pytest
import torch
from coola import objects_are_equal

from batchtensor.recursive import ApplyState, AutoApplier, MappingApplier


@pytest.fixture
def state() -> ApplyState:
    return ApplyState(applier=AutoApplier())


####################################
#     Tests for MappingApplier     #
####################################


def test_mapping_applier_str() -> None:
    assert str(MappingApplier()) == "MappingApplier()"


def test_mapping_applier_apply_str(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply({"a": 1, "b": "abc"}, str, state), {"a": "1", "b": "abc"}
    )


def test_mapping_applier_apply_tensor(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply(
            {"a": torch.ones(2, 3), "b": torch.ones(2), "c": {"d": torch.ones(2, 1)}},
            lambda tensor: tensor.shape,
            state,
        ),
        {"a": torch.Size([2, 3]), "b": torch.Size([2]), "c": {"d": torch.Size([2, 1])}},
    )


def test_mapping_applier_apply_ordered_dict(state: ApplyState) -> None:
    assert objects_are_equal(
        MappingApplier().apply(OrderedDict({"a": 1, "b": "abc"}), str, state),
        OrderedDict({"a": "1", "b": "abc"}),
    )
