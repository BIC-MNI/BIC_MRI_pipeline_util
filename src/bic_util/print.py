import contextlib
import io
import sys
from collections.abc import Callable, Generator
from typing import Never, TextIO, TypeVar

verbose_flag: bool = False

COLOR_WARNING = '\033[93m'
COLOR_ERROR   = '\033[91m'
COLOR_DIM     = '\033[2m'
COLOR_END     = '\033[0m'


def set_verbose(verbose: bool):
    """
    Set the console verbose flag.
    """

    global verbose_flag
    verbose_flag = verbose


def print_verbose(message: str):
    """
    Print a message in the console if the script is running in verbose mode.
    """

    if verbose_flag:
        print(message)


def print_warning(message: str):
    """
    Print a warning message in the console.
    """

    print_with_color(sys.stderr, f"WARNING: {message}", COLOR_WARNING)


def print_error(message: str):
    """
    Print an error message in the console.
    """

    print_with_color(sys.stderr, f"ERROR: {message}", COLOR_ERROR)


def print_error_exit(message: str, exit_code: int = -1) -> Never:
    """
    Print an error message in the console and exit the program.
    """

    print_error(message)
    sys.exit(exit_code)


T = TypeVar('T')


def with_print_subscript(f: Callable[[], T]) -> T:
    """
    Run a function while printing its output as a subscript output.
    """

    is_terminal = sys.stdout.isatty()
    if not is_terminal:
        return f()

    print(COLOR_DIM, end='')

    try:
        return f()
    finally:
        print(COLOR_END, end='')


def with_print_capture(f: Callable[[], T]) -> tuple[str, str, T]:
    """
    Run a function while capturing its standad output and error.
    """

    # Create string buffers to capture the output.
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    # Redirect both stdout and stderr.
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        return_value = f()

    # Get the captured content.
    stdout_content = stdout_buffer.getvalue()
    stderr_content = stderr_buffer.getvalue()

    return stdout_content, stderr_content, return_value


def get_progress_printer(total: int) -> Generator[None, None, None]:
    """
    Get a function whose each call increments and prints a progress counter up to the defined
    maximum.
    """

    is_terminal = sys.stdout.isatty()

    progress = 0
    while progress <= total:
        progress += 1

        # Do not print every step in a non-terminal output stream to not flood that stream.
        if is_terminal:
            print(f"{progress} / {total}", end='\r')
        elif progress % 100 == 0:
            print(f"{progress} / {total}")

        yield None


def print_with_color(output_stream: TextIO, message: str, color_code: str):
    """
    Print a message in an output stream using the given color code if that output stream is a
    terminal, or print the message normally otherwise.
    """

    if output_stream.isatty():
        print(f'{color_code}{message}{COLOR_END}', file=output_stream)
    else:
        print(message, file=output_stream)
