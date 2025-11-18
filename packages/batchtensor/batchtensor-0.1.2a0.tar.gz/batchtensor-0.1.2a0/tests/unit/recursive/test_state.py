from __future__ import annotations

from batchtensor.recursive import ApplyState, AutoApplier

################################
#     Tests for ApplyState     #
################################


def test_state_increment_depth_1() -> None:
    applier = AutoApplier()
    assert ApplyState(applier=applier).increment_depth() == ApplyState(applier=applier, depth=1)


def test_state_increment_depth_2() -> None:
    applier = AutoApplier()
    assert ApplyState(applier=applier).increment_depth(2) == ApplyState(applier=applier, depth=2)
