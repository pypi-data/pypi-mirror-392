from __future__ import annotations

import importlib
import logging

from coola import objects_are_equal

from minrecord import Record

logger = logging.getLogger(__name__)


def check_imports() -> None:
    logger.info("Checking imports...")
    objects_to_import = [
        "minrecord.BaseRecord",
        "minrecord.Record",
        "minrecord.MaxScalarRecord",
        "minrecord.MinScalarRecord",
        "minrecord.RecordManager",
        "minrecord.utils",
    ]
    for a in objects_to_import:
        module_path, name = a.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        assert obj is not None


def check_record() -> None:
    logger.info("Checking Record...")
    record = Record("loss", max_size=3, elements=[(1, 123), (2, 123), (3, 124), (4, 125)])
    assert record.get_last_value() == 125
    assert record.get_most_recent() == ((2, 123), (3, 124), (4, 125))

    assert objects_are_equal(Record("loss"), Record("loss"))


def main() -> None:
    check_imports()
    check_record()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
