from __future__ import annotations

from minrecord.utils.value import MutableValue

##################################
#     Tests for MutableValue     #
##################################


def test_mutable_value_get_value() -> None:
    assert MutableValue(10).get_value() == 10


def test_mutable_value_set_value() -> None:
    value = MutableValue(10)
    value.set_value(42)
    assert value.get_value() == 42
