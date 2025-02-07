from collections.abc import Callable, Iterable
from datetime import datetime
from typing import TypeVar

T = TypeVar('T')
U = TypeVar('U')


def find(predicate: Callable[[T], bool], iterable: Iterable[T]) -> T | None:
    """
    Find the first element in an iterable that satisfies a predicate, or return `None` if no match
    is found.
    """

    for item in iterable:
        if predicate(item):
            return item

    return None


def find_map(predicate: Callable[[T], U | None], iterable: Iterable[T]) -> U | None:
    """
    Find the first element in an iterable that satisfies a predicate, or return `None` if no match
    is found.
    """

    for item in iterable:
        item = predicate(item)
        if item is not None:
            return item

    return None


def hours_to_seconds(hours: int):
    """
    Convert a number of hours to a number of seconds.
    """

    return hours * 3600


def format_datetime(datetime: datetime):
    """
    Format a date time object.
    """

    return datetime.strftime("%Y-%m-%d %H:%M:%S")
