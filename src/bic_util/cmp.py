from enum import IntEnum
from typing import Any


class Comparison(IntEnum):
    """
    Enumeration that represents the result of a three-way comparison.
    """

    LT = -1
    """
    Left value is lesser than the right value.
    """

    EQ = 0
    """
    Left value is equal to the right value.
    """

    GT = 1
    """
    Left value is greater than the right value.
    """


def compare(a: Any, b: Any) -> Comparison:
    """
    Compare two values and return the three-way result of the comparison. The values should follow
    a total order.
    """

    return Comparison((a > b) - (a < b))


def optional_string_key(value: str | None) -> tuple[int, str | None]:
    """
    Key function for comparing optional strings, with `None` values ordered last.
    """

    if value is not None:
        return 0, value  # String values come first.
    else:
        return 1, ""  # None values come last.
