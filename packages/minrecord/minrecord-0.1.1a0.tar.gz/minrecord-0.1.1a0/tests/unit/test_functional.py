from __future__ import annotations

import pytest

from minrecord import (
    BaseRecord,
    MaxScalarRecord,
    MinScalarRecord,
    Record,
    get_best_values,
    get_last_values,
)


@pytest.fixture
def records() -> dict[str, BaseRecord]:
    record1 = MinScalarRecord.from_elements("loss", elements=[(None, 1.9), (None, 1.2)])
    record2 = MaxScalarRecord.from_elements("accuracy", elements=[(None, 42), (None, 35)])
    record3 = Record("epoch", elements=[(None, 0), (None, 1)])
    record4 = MaxScalarRecord("f1")
    return {
        record1.name: record1,
        record2.name: record2,
        record3.name: record3,
        record4.name: record4,
    }


#####################################
#     Tests for get_best_values     #
#####################################


def test_get_best_values(records: dict[str, BaseRecord]) -> None:
    assert get_best_values(records) == {"loss": 1.2, "accuracy": 42}


def test_get_best_values_prefix(records: dict[str, BaseRecord]) -> None:
    assert get_best_values(records, prefix="best/") == {"best/loss": 1.2, "best/accuracy": 42}


def test_get_best_values_suffix(records: dict[str, BaseRecord]) -> None:
    assert get_best_values(records, suffix="/best") == {"loss/best": 1.2, "accuracy/best": 42}


def test_get_best_values_empty() -> None:
    assert get_best_values({}) == {}


#####################################
#     Tests for get_last_values     #
#####################################


def test_get_last_values(records: dict[str, BaseRecord]) -> None:
    assert get_last_values(records) == {"loss": 1.2, "accuracy": 35, "epoch": 1}


def test_get_last_values_prefix(records: dict[str, BaseRecord]) -> None:
    assert get_last_values(records, prefix="last/") == {
        "last/loss": 1.2,
        "last/accuracy": 35,
        "last/epoch": 1,
    }


def test_get_last_values_suffix(records: dict[str, BaseRecord]) -> None:
    assert get_last_values(records, suffix="/last") == {
        "loss/last": 1.2,
        "accuracy/last": 35,
        "epoch/last": 1,
    }


def test_get_last_values_empty() -> None:
    assert get_last_values({}) == {}
