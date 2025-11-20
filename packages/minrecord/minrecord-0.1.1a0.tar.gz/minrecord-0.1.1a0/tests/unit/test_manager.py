from __future__ import annotations

import pytest

from minrecord import MaxScalarRecord, MinScalarRecord, Record, RecordManager
from minrecord.testing import objectory_available
from minrecord.utils.imports import is_objectory_available

if is_objectory_available():
    from objectory import OBJECT_TARGET

NAMES = ("NAME", "my_record")


###################################
#     Tests for RecordManager     #
###################################


def test_record_manager_repr() -> None:
    assert repr(RecordManager()) == "RecordManager()"


def test_record_manager_repr_with_record() -> None:
    assert repr(RecordManager({"something": Record("something")})).startswith("RecordManager(")


def test_record_manager_str() -> None:
    assert str(RecordManager()) == "RecordManager()"


def test_record_manager_str_with_record() -> None:
    manager = RecordManager()
    manager.get_record("something")
    assert str(manager).startswith("RecordManager(")


def test_record_manager_len_empty() -> None:
    assert len(RecordManager()) == 0


def test_record_manager_len_1_record() -> None:
    manager = RecordManager()
    manager.get_record("my_record1")
    assert len(manager) == 1


def test_record_manager_len_2_records() -> None:
    manager = RecordManager()
    manager.get_record("my_record1")
    manager.get_record("my_record2")
    assert len(manager) == 2


@pytest.mark.parametrize("key", NAMES)
def test_record_manager_add_record_with_key(key: str) -> None:
    manager = RecordManager()
    manager.add_record(MinScalarRecord("loss"), key)
    assert key in manager._records


@pytest.mark.parametrize("key", NAMES)
def test_record_manager_add_record_without_key(key: str) -> None:
    manager = RecordManager()
    manager.add_record(MinScalarRecord(key))
    assert key in manager._records


def test_record_manager_add_record_duplicate_key() -> None:
    manager = RecordManager()
    manager.add_record(MinScalarRecord("loss"))
    with pytest.raises(RuntimeError, match=r"A record .* is already registered for the key loss"):
        manager.add_record(MinScalarRecord("loss"))


def test_record_manager_get_best_values_empty() -> None:
    assert RecordManager().get_best_values() == {}


def test_record_manager_get_best_values_empty_record() -> None:
    state = RecordManager()
    record = MinScalarRecord("loss")
    state.add_record(record)
    assert state.get_best_values() == {}


def test_record_manager_get_best_values_not_comparable_record() -> None:
    state = RecordManager()
    record = Record("loss")
    record.add_value(1.2, step=0)
    record.add_value(0.8, step=1)
    state.add_record(record)
    assert state.get_best_values() == {}


def test_record_manager_get_best_values_1_record() -> None:
    state = RecordManager()
    record = MinScalarRecord("loss")
    state.add_record(record)
    record.add_value(1.2, step=0)
    record.add_value(0.8, step=1)
    assert state.get_best_values() == {"loss": 0.8}


def test_record_manager_get_best_values_2_record() -> None:
    state = RecordManager()
    record1 = MinScalarRecord("loss")
    record1.add_value(1.2, step=0)
    record1.add_value(0.8, step=1)
    state.add_record(record1)
    record2 = MaxScalarRecord("accuracy")
    record2.add_value(42, step=0)
    record2.add_value(41, step=1)
    state.add_record(record2)
    assert state.get_best_values() == {"loss": 0.8, "accuracy": 42}


def test_record_manager_get_record_exists() -> None:
    manager = RecordManager()
    record = MinScalarRecord("loss")
    manager.add_record(record)
    assert manager.get_record("loss") is record


def test_record_manager_get_record_does_not_exist() -> None:
    manager = RecordManager()
    record = manager.get_record("loss")
    assert isinstance(record, Record)
    assert len(record.get_most_recent()) == 0


def test_record_manager_get_records() -> None:
    manager = RecordManager()
    record1 = MinScalarRecord("loss")
    record2 = MinScalarRecord("accuracy")
    manager.add_record(record1)
    manager.add_record(record2)
    assert manager.get_records() == {"loss": record1, "accuracy": record2}


def test_record_manager_get_records_empty() -> None:
    assert RecordManager().get_records() == {}


def test_record_manager_has_record_true() -> None:
    manager = RecordManager()
    manager.add_record(MinScalarRecord("loss"))
    assert manager.has_record("loss")


def test_record_manager_has_record_false() -> None:
    assert not RecordManager().has_record("loss")


def test_record_manager_load_state_dict_empty() -> None:
    manager = RecordManager()
    manager.load_state_dict({})
    assert len(manager) == 0


def test_record_manager_load_state_dict_with_existing_record() -> None:
    manager = RecordManager()
    manager.add_record(MinScalarRecord("loss"))
    manager.get_record("loss").add_value(2, step=0)
    manager.load_state_dict(
        {
            "loss": {
                "state": {
                    "record": ((0, 10), (1, 9), (2, 8), (3, 7), (4, 6)),
                    "improved": True,
                    "best_value": 6,
                },
            }
        }
    )
    record = manager.get_record("loss")
    assert isinstance(record, MinScalarRecord)
    assert record.get_last_value() == 6
    assert record.get_best_value() == 6


@objectory_available
def test_record_manager_load_state_dict_without_record() -> None:
    manager = RecordManager()
    manager.load_state_dict(
        {
            "loss": {
                "config": {
                    OBJECT_TARGET: "minrecord.comparable.MinScalarRecord",
                    "name": "loss",
                    "max_size": 10,
                },
                "state": {
                    "record": ((0, 10), (1, 9), (2, 8), (3, 7), (4, 6)),
                    "improved": True,
                    "best_value": 6,
                },
            }
        },
    )
    record = manager.get_record("loss")
    assert isinstance(record, MinScalarRecord)
    assert record.get_last_value() == 6
    assert record.get_best_value() == 6


def test_record_manager_state_dict_empty() -> None:
    assert RecordManager().state_dict() == {}


def test_record_manager_state_dict_1_record() -> None:
    manager = RecordManager()
    record = MinScalarRecord("loss")
    manager.add_record(record)
    assert manager.state_dict() == {"loss": record.to_dict()}


def test_record_manager_state_dict_2_record() -> None:
    manager = RecordManager()
    record1 = MinScalarRecord("loss")
    manager.add_record(record1)
    record2 = MaxScalarRecord("accuracy")
    manager.add_record(record2)
    assert manager.state_dict() == {"loss": record1.to_dict(), "accuracy": record2.to_dict()}
