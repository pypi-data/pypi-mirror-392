from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from coola import objects_are_allclose, objects_are_equal
from coola.equality import EqualityConfig
from coola.equality.testers import EqualityTester

from minrecord import MinScalarRecord, Record
from minrecord.base import RecordEqualityComparator
from tests.unit.helpers import ExamplePair

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def config() -> EqualityConfig:
    return EqualityConfig(tester=EqualityTester())


##############################################
#     Tests for RecordEqualityComparator     #
##############################################

RECORD_FUNCTIONS = [objects_are_equal, objects_are_allclose]

RECORD_EQUAL = [
    pytest.param(
        ExamplePair(actual=Record(name="loss"), expected=Record(name="loss")),
        id="record",
    ),
    pytest.param(
        ExamplePair(actual=MinScalarRecord(name="loss"), expected=MinScalarRecord(name="loss")),
        id="min scalar record",
    ),
    pytest.param(
        ExamplePair(
            actual=Record(name="loss", elements=[(0, 4), (1, 2), (None, 1)]),
            expected=Record(name="loss", elements=[(0, 4), (1, 2), (None, 1)]),
        ),
        id="record with elements",
    ),
]


RECORD_NOT_EQUAL = [
    pytest.param(
        ExamplePair(
            actual=Record(name="loss"),
            expected=MinScalarRecord(name="loss"),
            expected_message="objects have different types:",
        ),
        id="different types",
    ),
    pytest.param(
        ExamplePair(
            actual=Record(name="loss"),
            expected=Record(name="my_loss"),
            expected_message="objects are not equal:",
        ),
        id="different names",
    ),
    pytest.param(
        ExamplePair(
            actual=Record(name="loss", elements=[(0, 4), (1, 2), (None, 1)]),
            expected=Record(name="my_loss", elements=[(0, 4), (1, 2), (None, 0)]),
            expected_message="objects are not equal:",
        ),
        id="different elements",
    ),
]


def test_record_equality_comparator_repr() -> None:
    assert repr(RecordEqualityComparator()) == "RecordEqualityComparator()"


def test_record_equality_comparator_str() -> None:
    assert str(RecordEqualityComparator()) == "RecordEqualityComparator()"


def test_record_equality_comparator__eq__true() -> None:
    assert RecordEqualityComparator() == RecordEqualityComparator()


def test_record_equality_comparator__eq__false() -> None:
    assert RecordEqualityComparator() != 123


def test_record_equality_comparator_clone() -> None:
    op = RecordEqualityComparator()
    op_cloned = op.clone()
    assert op is not op_cloned
    assert op == op_cloned


def test_record_equality_comparator_equal_true_same_object(config: EqualityConfig) -> None:
    x = Record(name="loss")
    assert RecordEqualityComparator().equal(x, x, config)


@pytest.mark.parametrize("example", RECORD_EQUAL)
def test_record_equality_comparator_equal_true(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    comparator = RecordEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", RECORD_EQUAL)
def test_record_equality_comparator_equal_true_show_difference(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config.show_difference = True
    comparator = RecordEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", RECORD_NOT_EQUAL)
def test_record_equality_comparator_equal_false(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    comparator = RecordEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert not comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", RECORD_NOT_EQUAL)
def test_record_equality_comparator_equal_false_show_difference(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config.show_difference = True
    comparator = RecordEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert not comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert caplog.messages[-1].startswith(example.expected_message)


@pytest.mark.parametrize("function", RECORD_FUNCTIONS)
@pytest.mark.parametrize("example", RECORD_EQUAL)
@pytest.mark.parametrize("show_difference", [True, False])
def test_objects_are_equal_true(
    function: Callable,
    example: ExamplePair,
    show_difference: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        assert function(example.actual, example.expected, show_difference=show_difference)
        assert not caplog.messages


@pytest.mark.parametrize("function", RECORD_FUNCTIONS)
@pytest.mark.parametrize("example", RECORD_NOT_EQUAL)
def test_objects_are_equal_false(
    function: Callable, example: ExamplePair, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        assert not function(example.actual, example.expected)
        assert not caplog.messages


@pytest.mark.parametrize("function", RECORD_FUNCTIONS)
@pytest.mark.parametrize("example", RECORD_NOT_EQUAL)
def test_objects_are_equal_false_show_difference(
    function: Callable, example: ExamplePair, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        assert not function(example.actual, example.expected, show_difference=True)
        assert caplog.messages[-1].startswith(example.expected_message)
