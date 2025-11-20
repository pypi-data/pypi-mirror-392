r"""Contain functionalities to configure the records."""

from __future__ import annotations

__all__ = ["get_max_size", "set_max_size"]


from minrecord.utils.value import MutableValue

_max_size = MutableValue(10)


def get_max_size() -> int:
    r"""Get the current default maximum size of values to track in each
    record.

    Returns:
        The current default maximum size of values to track in each
            record.

    This value can be changed by using ``set_max_size``.

    Example usage:

    ```pycon

    >>> from minrecord import get_max_size
    >>> get_max_size()
    10

    ```
    """
    return _max_size.get_value()


def set_max_size(max_size: int) -> None:
    r"""Set the default maximum size of values to track in each record.

    This function does not change the maximum size of records that are
    already created. It only changes the maximum size of records that
    will be created after the call of this function.

    Args:
        max_size: The new default maximum size of values to track in
            each record.

    Example usage:

    ```pycon

    >>> from minrecord import get_max_size, set_max_size
    >>> get_max_size()
    10
    >>> set_max_size(5)
    >>> get_max_size()
    5

    ```
    """
    _max_size.set_value(max_size)
