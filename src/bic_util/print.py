import sys
from typing import Callable, Never, ParamSpec, TypeVar

verbose_flag: bool = False

COLOR_WARNING = '\033[93m'
COLOR_ERROR   = '\033[91m'
COLOR_END     = '\033[0m'


def set_verbose(verbose: bool):
    """
    Set the console verbose flag.
    """

    global verbose_flag
    verbose_flag = verbose


def print_verbose(message: str) -> None:
    """
    Print a message in the console if the script is running in verbose mode.
    """

    if verbose_flag:
        print(message)


def print_warning(message: str) -> None:
    """
    Print a warning message in the console.
    """

    print(f'{COLOR_WARNING}WARNING: {message}{COLOR_END}', file=sys.stderr)


def print_error_exit(message: str, exit_code: int = -1) -> Never:
    """
    Print an error message in the console and exit the program.
    """

    print(f'{COLOR_ERROR}ERROR: {message}{COLOR_END}', file=sys.stderr)
    exit(exit_code)


P = ParamSpec("P")
R = TypeVar("R")


def get_progress_printer(total: int, func: Callable[P, R] = lambda: None) -> Callable[P, R]:
    """
    Get a function whose each call increments and prints a progress counter up to the defined
    maximum.
    """

    progress = 0
    print(f'{progress} / {total}', end='\r')

    def printer(*args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal progress
        result = func(*args, **kwargs)
        progress += 1
        print(f'{progress} / {total}', end='\r')
        return result

    return printer
