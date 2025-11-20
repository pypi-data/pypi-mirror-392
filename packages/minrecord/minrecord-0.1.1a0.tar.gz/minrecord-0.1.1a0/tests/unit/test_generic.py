from __future__ import annotations

import pytest
from coola import objects_are_equal

from minrecord import (
    BaseRecord,
    EmptyRecordError,
    MinScalarRecord,
    NotAComparableRecordError,
    Record,
)
from minrecord.testing import objectory_available
from minrecord.utils.imports import is_objectory_available

if is_objectory_available():
    from objectory import OBJECT_TARGET

############################
#     Tests for Record     #
############################


def test_record_repr() -> None:
    assert repr(Record("loss")) == "Record(name=loss, max_size=10, size=0)"


def test_record_str() -> None:
    assert str(Record("loss")).startswith("Record(")


@pytest.mark.parametrize("name", ["name", "accuracy", ""])
def test_record_init_name(name: str) -> None:
    assert Record(name).name == name


@pytest.mark.parametrize("max_size", [1, 5])
def test_record_init_max_size(max_size: int) -> None:
    assert Record("loss", max_size=max_size).max_size == max_size


def test_record_init_max_size_incorrect() -> None:
    with pytest.raises(ValueError, match=r"Record size must be greater than 0"):
        Record("loss", max_size=0)


def test_record_add_value() -> None:
    assert Record("loss", elements=((None, "abc"), (1, 123))).get_most_recent() == (
        (None, "abc"),
        (1, 123),
    )


def test_record_add_value_list() -> None:
    record = Record[list]("loss")
    record.add_value([1, 2, 3])
    assert record.get_last_value() == [1, 2, 3]


def test_record_clone() -> None:
    record = Record(name="loss", elements=((None, 35), (1, 42)), max_size=20)
    record_cloned = record.clone()
    assert record is not record_cloned
    assert record.equal(record_cloned)


def test_record_clone_empty() -> None:
    record = Record("loss")
    record_cloned = record.clone()
    assert record is not record_cloned
    assert record.equal(record_cloned)


def test_record_equal_true() -> None:
    assert Record("loss", elements=((None, 35), (1, 42))).equal(
        Record("loss", elements=((None, 35), (1, 42)))
    )


def test_record_equal_true_empty() -> None:
    assert Record("loss").equal(Record("loss"))


def test_record_equal_false_different_values() -> None:
    assert not Record("loss", elements=((None, 35), (1, 42))).equal(
        Record("loss", elements=((None, 35), (1, 50)))
    )


def test_record_equal_false_different_names() -> None:
    assert not Record("loss", elements=((None, 35), (1, 42))).equal(
        Record("accuracy", elements=((None, 35), (1, 42)))
    )


def test_record_equal_false_different_max_sizes() -> None:
    assert not Record("loss").equal(Record("loss", max_size=2))


def test_record_equal_false_different_types() -> None:
    assert not Record("loss").equal(1)


def test_record_equal_false_different_types_record() -> None:
    assert not Record("loss").equal(MinScalarRecord("loss"))


def test_record_get_best_value() -> None:
    record = Record("loss")
    with pytest.raises(
        NotAComparableRecordError, match=r"It is not possible to get the best value"
    ):
        record.get_best_value()


def test_record__get_best_value() -> None:
    record = Record("loss")
    with pytest.raises(NotImplementedError, match=r"_get_best_value method is not implemented"):
        record._get_best_value()


def test_record_get_most_recent() -> None:
    assert Record("loss", elements=[(1, 123)]).get_most_recent() == ((1, 123),)


def test_record_get_most_recent_empty() -> None:
    assert Record("loss").get_most_recent() == ()


def test_record_get_most_recent_max_size() -> None:
    assert Record(
        "loss", max_size=3, elements=[(1, 123), (2, 123), (3, 124), (4, 125)]
    ).get_most_recent() == ((2, 123), (3, 124), (4, 125))


def test_record_get_most_recent_add_max_size() -> None:
    record = Record("loss", max_size=3)
    for i in range(10):
        record.add_value(i)
    assert record.equal(Record("loss", max_size=3, elements=((None, 7), (None, 8), (None, 9))))
    assert record.get_last_value() == 9


def test_record_get_last_value() -> None:
    assert Record("loss", elements=((None, 35), (1, 42))).get_last_value() == 42


def test_record_get_last_value_empty() -> None:
    record = Record("loss")
    with pytest.raises(EmptyRecordError, match=r"'loss' record is empty."):
        record.get_last_value()


def test_record_has_improved() -> None:
    record = Record("loss")
    with pytest.raises(
        NotAComparableRecordError,
        match=r"It is not possible to indicate if the last value is the best value",
    ):
        record.has_improved()


def test_record__has_improved() -> None:
    record = Record("loss")
    with pytest.raises(NotImplementedError, match=r"_has_improved method is not implemented"):
        record._has_improved()


def test_record_is_comparable() -> None:
    assert not Record("loss").is_comparable()


def test_record_is_empty_true() -> None:
    assert Record("loss").is_empty()


def test_record_is_empty_false() -> None:
    assert not Record("loss", elements=((None, 35), (1, 42))).is_empty()


def test_record_update() -> None:
    record = Record("loss")
    record.update(elements=((None, 35), (1, 42)))
    assert record.equal(Record("loss", elements=((None, 35), (1, 42))))


def test_record_update_empty() -> None:
    record = Record("loss")
    record.update(elements=())
    assert record.equal(Record("loss"))


@objectory_available
def test_record_config_dict() -> None:
    assert Record("loss").config_dict() == {
        OBJECT_TARGET: "minrecord.generic.Record",
        "name": "loss",
        "max_size": 10,
    }


@objectory_available
def test_record_config_dict_create_new_record() -> None:
    assert BaseRecord.factory(**Record("loss", max_size=5, elements=[(0, 1)]).config_dict()).equal(
        Record("loss", max_size=5)
    )


def test_record_load_state_dict_empty() -> None:
    record = Record("loss")
    record.load_state_dict({"record": ()})
    assert record.get_most_recent() == ()
    assert record.equal(Record("loss"))


def test_record_load_state_dict_max_size_2() -> None:
    record = Record("loss", max_size=2)
    record.load_state_dict({"record": ((0, 1), (1, "abc"))})
    record.add_value(7, step=2)
    assert record.equal(Record("loss", max_size=2, elements=((1, "abc"), (2, 7))))


def test_record_load_state_dict_reset() -> None:
    record = Record("loss", elements=[(0, 7)])
    record.load_state_dict({"record": ((0, 4), (1, 5))})
    assert record.equal(Record("loss", elements=((0, 4), (1, 5))))


def test_record_state_dict() -> None:
    assert objects_are_equal(
        Record("loss", elements=((0, 1), (1, 5))).state_dict(), {"record": ((0, 1), (1, 5))}
    )


def test_record_state_dict_empty() -> None:
    assert objects_are_equal(Record("loss").state_dict(), {"record": ()})


@objectory_available
def test_record_to_dict() -> None:
    assert objects_are_equal(
        Record("loss", elements=[(0, 5)]).to_dict(),
        {
            "config": {OBJECT_TARGET: "minrecord.generic.Record", "name": "loss", "max_size": 10},
            "state": {"record": ((0, 5),)},
        },
    )


@objectory_available
def test_record_to_dict_empty() -> None:
    assert objects_are_equal(
        Record("loss").to_dict(),
        {
            "config": {OBJECT_TARGET: "minrecord.generic.Record", "name": "loss", "max_size": 10},
            "state": {"record": ()},
        },
    )


@objectory_available
def test_record_from_dict() -> None:
    assert BaseRecord.from_dict(
        {
            "config": {OBJECT_TARGET: "minrecord.Record", "name": "loss", "max_size": 7},
            "state": {"record": ((0, 1), (1, 5))},
        }
    ).equal(Record("loss", max_size=7, elements=((0, 1), (1, 5))))


@objectory_available
def test_record_from_dict_empty() -> None:
    assert BaseRecord.from_dict(
        {
            "config": {OBJECT_TARGET: "minrecord.Record", "name": "loss"},
            "state": {"record": ()},
        }
    ).equal(Record("loss"))
