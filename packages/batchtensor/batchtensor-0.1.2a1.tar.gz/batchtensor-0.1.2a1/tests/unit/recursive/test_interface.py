from __future__ import annotations

from coola import objects_are_equal

from batchtensor.recursive import recursive_apply

#####################################
#     Tests for recursive_apply     #
#####################################


def test_recursive_apply_int() -> None:
    assert objects_are_equal(recursive_apply(1, str), "1")


def test_recursive_apply_str() -> None:
    assert objects_are_equal(recursive_apply("abc", str), "abc")


def test_recursive_apply_list() -> None:
    assert objects_are_equal(recursive_apply([1, "abc"], str), ["1", "abc"])


def test_recursive_apply_dict() -> None:
    assert objects_are_equal(recursive_apply({"a": 1, "b": "abc"}, str), {"a": "1", "b": "abc"})
