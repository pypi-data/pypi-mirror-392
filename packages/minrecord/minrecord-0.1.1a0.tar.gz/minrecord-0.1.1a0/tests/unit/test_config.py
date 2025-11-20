from __future__ import annotations

import pytest

from minrecord import get_max_size, set_max_size


@pytest.fixture(autouse=True)
def _reset_max_size() -> None:
    max_size = get_max_size()
    yield
    set_max_size(max_size)


##################################
#     Tests for get_max_size     #
##################################


def test_get_max_size() -> None:
    assert get_max_size() == 10


##################################
#     Tests for set_max_size     #
##################################


def test_set_max_size() -> None:
    set_max_size(5)
    assert get_max_size() == 5
