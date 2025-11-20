from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from coola import objects_are_allclose, objects_are_equal
from coola.equality import EqualityConfig
from coola.equality.testers import EqualityTester

from minrecord import MaxScalarComparator, MinScalarComparator
from minrecord.comparator import ComparatorEqualityComparator
from tests.unit.helpers import ExamplePair

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture
def config() -> EqualityConfig:
    return EqualityConfig(tester=EqualityTester())


#########################################
#     Tests for MaxScalarComparator     #
#########################################


def test_max_scalar_equal_true() -> None:
    assert MaxScalarComparator().equal(MaxScalarComparator())


def test_max_scalar_equal_false() -> None:
    assert not MaxScalarComparator().equal(MinScalarComparator())


def test_max_scalar_get_initial_best_value() -> None:
    assert MaxScalarComparator().get_initial_best_value() == -float("inf")


def test_max_scalar_is_better_int() -> None:
    comparator = MaxScalarComparator()
    assert comparator.is_better(5, 12)
    assert comparator.is_better(12, 12)
    assert not comparator.is_better(12, 5)


def test_max_scalar_is_better_float() -> None:
    comparator = MaxScalarComparator()
    assert comparator.is_better(5.2, 12.1)
    assert comparator.is_better(5.2, 5.2)
    assert not comparator.is_better(12.2, 5.1)


#########################################
#     Tests for MinScalarComparator     #
#########################################


def test_min_scalar_equal_true() -> None:
    assert MinScalarComparator().equal(MinScalarComparator())


def test_min_scalar_equal_false() -> None:
    assert not MinScalarComparator().equal(MaxScalarComparator())


def test_min_scalar_get_initial_best_value() -> None:
    assert MinScalarComparator().get_initial_best_value() == float("inf")


def test_min_scalar_is_better_int() -> None:
    comparator = MinScalarComparator()
    assert not comparator.is_better(5, 12)
    assert comparator.is_better(12, 12)
    assert comparator.is_better(12, 5)


def test_min_scalar_is_better_float() -> None:
    comparator = MinScalarComparator()
    assert not comparator.is_better(5.2, 12.1)
    assert comparator.is_better(5.2, 5.2)
    assert comparator.is_better(12.2, 5.1)


##################################################
#     Tests for ComparatorEqualityComparator     #
##################################################

COMPARATOR_FUNCTIONS = [objects_are_equal, objects_are_allclose]

COMPARATOR_EQUAL = [
    pytest.param(
        ExamplePair(actual=MaxScalarComparator(), expected=MaxScalarComparator()),
        id="different values",
    ),
    pytest.param(
        ExamplePair(actual=MinScalarComparator(), expected=MinScalarComparator()),
        id="different types",
    ),
]


COMPARATOR_NOT_EQUAL = [
    pytest.param(
        ExamplePair(
            actual=MaxScalarComparator(),
            expected=MinScalarComparator(),
            expected_message="objects have different types:",
        ),
        id="different types",
    ),
]


def test_comparator_equality_comparator_repr() -> None:
    assert repr(ComparatorEqualityComparator()) == "ComparatorEqualityComparator()"


def test_comparator_equality_comparator_str() -> None:
    assert str(ComparatorEqualityComparator()) == "ComparatorEqualityComparator()"


def test_comparator_equality_comparator__eq__true() -> None:
    assert ComparatorEqualityComparator() == ComparatorEqualityComparator()


def test_comparator_equality_comparator__eq__false() -> None:
    assert ComparatorEqualityComparator() != 123


def test_comparator_equality_comparator_clone() -> None:
    op = ComparatorEqualityComparator()
    op_cloned = op.clone()
    assert op is not op_cloned
    assert op == op_cloned


def test_comparator_equality_comparator_equal_true_same_object(config: EqualityConfig) -> None:
    x = MaxScalarComparator()
    assert ComparatorEqualityComparator().equal(x, x, config)


@pytest.mark.parametrize("example", COMPARATOR_EQUAL)
def test_comparator_equality_comparator_equal_true(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    comparator = ComparatorEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", COMPARATOR_EQUAL)
def test_comparator_equality_comparator_equal_true_show_difference(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config.show_difference = True
    comparator = ComparatorEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", COMPARATOR_NOT_EQUAL)
def test_comparator_equality_comparator_equal_false(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    comparator = ComparatorEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert not comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert not caplog.messages


@pytest.mark.parametrize("example", COMPARATOR_NOT_EQUAL)
def test_comparator_equality_comparator_equal_false_show_difference(
    example: ExamplePair,
    config: EqualityConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config.show_difference = True
    comparator = ComparatorEqualityComparator()
    with caplog.at_level(logging.INFO):
        assert not comparator.equal(actual=example.actual, expected=example.expected, config=config)
        assert caplog.messages[-1].startswith(example.expected_message)


@pytest.mark.parametrize("function", COMPARATOR_FUNCTIONS)
@pytest.mark.parametrize("example", COMPARATOR_EQUAL)
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


@pytest.mark.parametrize("function", COMPARATOR_FUNCTIONS)
@pytest.mark.parametrize("example", COMPARATOR_NOT_EQUAL)
def test_objects_are_equal_false(
    function: Callable, example: ExamplePair, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        assert not function(example.actual, example.expected)
        assert not caplog.messages


@pytest.mark.parametrize("function", COMPARATOR_FUNCTIONS)
@pytest.mark.parametrize("example", COMPARATOR_NOT_EQUAL)
def test_objects_are_equal_false_show_difference(
    function: Callable, example: ExamplePair, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        assert not function(example.actual, example.expected, show_difference=True)
        assert caplog.messages[-1].startswith(example.expected_message)
