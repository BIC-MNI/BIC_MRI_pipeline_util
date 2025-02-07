from enum import Enum
from typing import Any


class Comparison(Enum):
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
