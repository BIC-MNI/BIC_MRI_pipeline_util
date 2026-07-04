import os
import tarfile
from collections.abc import Generator
from pathlib import Path

from bic_util.print import get_progress_printer, print_error_exit


def require_directory(dir_path: Path):
    """
    Check that a directory exists, or exit the program with an error if that is not the case.
    """

    if not dir_path.exists():
        print_error_exit(f"Directory '{dir_path}' not found.")

    if not dir_path.is_dir():
        print_error_exit(f"'{dir_path}' is not a directory.")


def require_readable_directory(dir_path: Path):
    """
    Check that a directory exists and is readable, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    if not os.access(dir_path, os.R_OK):
        print_error_exit(f"Directory '{dir_path}' is not readable.")


def require_writable_directory(dir_path: Path):
    """
    Check that a directory exists and is writable, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    if not os.access(dir_path, os.W_OK):
        print_error_exit(f"Directory '{dir_path}' is not writable.")


def require_empty_directory(dir_path: Path):
    """
    Check that a directory exists and is empty, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    with os.scandir(dir_path) as iterator:
        if any(iterator):
            print_error_exit(f"Directory '{dir_path}' is not empty.")


def require_output_directory(dir_path: Path):
    """
    Check that a directory can be used as an output directory, or exit the program with an error if that is
    not the case.

    To be usable as an output directory, a directory must either:
    - Exist and be writable.
    - Not exist, but can be created with write permissions (which is done by this function).
    """

    if not dir_path.exists():
        create_directory(dir_path)
        return

    require_writable_directory(dir_path)


def require_readable_file(file_path: Path):
    """
    Check that a file exists and is readable, or exit the program with an error if that is not the
    case.
    """

    if not file_path.exists():
        print_error_exit(f"File '{file_path}' not found.")

    if not file_path.is_file():
        print_error_exit(f"File '{file_path}' is not a directory.")

    if not os.access(file_path, os.R_OK):
        print_error_exit(f"File '{file_path}' is not readable.")


def require_writable_file(file_path: Path):
    """
    Check that a file exists and is writable, or can be created with write permissions, or exit
    the program with an error if that is not the case.
    """

    if file_path.exists():
        if not file_path.is_file():
            print_error_exit(f"'{file_path}' is not a file.")

        if not os.access(file_path, os.W_OK):
            print_error_exit(f"File '{file_path}' is not writable.")
    else:
        if not os.access(file_path.parent, os.W_OK):
            print_error_exit(f"Cannot create file '{file_path}'.")


def create_directory(dir_path: Path):
    """
    Create a directory or exit the program with an error if that is not possible.
    """

    try:
        dir_path.mkdir()
    except FileExistsError:
        print_error_exit(f"Directory '{dir_path}' already exists.")
    except FileNotFoundError:
        print_error_exit(f"Cannot create directory '{dir_path}', parent directory does not exist.")


def rename_file(old_path: Path, new_name: str):
    """
    Rename a file or directory.
    """

    new_path = old_path.parent / new_name
    old_path.rename(new_path)


def count_all_dir_files(dir_path: Path) -> int:
    """
    Count the number of files in a directory recursively.
    """

    return sum([len(file_names) for _, _, file_names in os.walk(dir_path)])


def iter_all_dir_files(dir_path: Path) -> Generator[Path, None, None]:
    """
    Iterate through all the files in a directory recursively, and yield the path of each file
    relative to that directory.
    """

    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            yield file_path.relative_to(dir_path)


def tar_with_progress(file_path: Path, tar_path: Path, file_alias: str | None = None):
    """
    Archive a file or directory into a tar file, printing progress while doing so.
    """

    arc_name = file_alias if file_alias is not None else file_path.name
    progress = get_progress_printer(count_all_dir_files(file_path))
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(
            file_path,
            arcname=arc_name,
            filter=lambda x: next(progress) or x
        )


def get_size(path: Path) -> int:
    """
    Get the size of a file or directory in bytes.
    """

    if path.is_dir():
        return get_directory_size(path)
    else:
        return get_file_size(path)


def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes.
    """

    return file_path.stat().st_size


def get_directory_size(dir_path: Path) -> int:
    """
    Get the size of a directory in bytes.
    """

    total_size = 0

    for entry in os.scandir(dir_path):
        total_size += get_size(Path(entry.path))

    return total_size
