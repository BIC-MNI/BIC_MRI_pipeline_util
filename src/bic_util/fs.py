import os
import tarfile

from bic_util.print import get_progress_printer, print_error_exit


def require_directory(dir_path: str):
    """
    Check that a directory exists, or exit the program with an error if that is not the case.
    """

    if not os.path.exists(dir_path):
        print_error_exit(f'directory \'{dir_path}\' not found')

    if not os.path.isdir(dir_path):
        print_error_exit(f'\'{dir_path}\' is not a directory')


def require_readable_directory(dir_path: str):
    """
    Check that a directory exists and is readable, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    if not os.access(dir_path, os.R_OK):
        print_error_exit(f'directory \'{dir_path}\' is not readable')


def require_writable_directory(dir_path: str):
    """
    Check that a directory exists and is writable, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    if not os.access(dir_path, os.W_OK):
        print_error_exit(f'directory \'{dir_path}\' is not writable')


def require_empty_directory(dir_path: str):
    """
    Check that a directory exists and is empty, or exit the program with an error if that is
    not the case.
    """

    require_directory(dir_path)

    with os.scandir(dir_path) as iterator:
        if any(iterator):
            print_error_exit(f'directory \'{dir_path}\' is not empty')


def require_output_directory(dir_path: str):
    """
    Check that a directory can be used as an output directory, or exit the program with an error if that is
    not the case.

    To be usable as an output directory, a directory must either:
    - Exist and be writable.
    - Not exist, but can be created with write permissions (which is done by this function).
    """

    if not os.path.exists(dir_path):
        create_directory(dir_path)
        return

    require_writable_directory(dir_path)


def require_readable_file(file_path: str):
    """
    Check that a file exists and is readable, or exit the program with an error if that is not the
    case.
    """

    if not os.path.exists(file_path):
        print_error_exit(f'file \'{file_path}\' not found')

    if not os.path.isfile(file_path):
        print_error_exit(f'\'{file_path}\' is not a directory')

    if not os.access(file_path, os.R_OK):
        print_error_exit(f'file \'{file_path}\' is not readable')


def require_writable_file(file_path: str):
    """
    Check that a file exists and is writable, or can be created with write permissions, or exit
    the program with an error if that is not the case.
    """

    if os.path.exists(file_path):
        if not os.path.isfile(file_path):
            print_error_exit(f'\'{file_path}\' is not a file')

        if not os.access(file_path, os.W_OK):
            print_error_exit(f'file \'{file_path}\' is not writable')
    else:
        dir_path = os.path.dirname(file_path)
        if not os.access(dir_path, os.W_OK):
            print_error_exit(f'cannot to create file \'{file_path}\'')


def create_directory(dir_path: str):
    """
    Create a directory or exit the program with an error if that is not possible.
    """

    try:
        os.mkdir(dir_path)
    except FileExistsError:
        print_error_exit(f'directory \'{dir_path}\' already exists')
    except FileNotFoundError:
        print_error_exit(f'cannot create directory \'{dir_path}\', parent directory does not exist')


def rename_file(old_path: str, new_name: str):
    """
    Rename a file or directory.
    """

    dir_name = os.path.dirname(old_path)
    new_path = os.path.join(dir_name, new_name)

    os.rename(old_path, new_path)


def count_dir_files(dir_path: str) -> int:
    """
    Count the total (recursive) number of files in a directory.
    """

    return sum([len(file_names) for _, _, file_names in os.walk(dir_path)])


def tar_with_progress(file_path: str, tar_path: str, file_alias: str | None = None):
    """
    Archive file or directory into a tar file, printing progress while doing so.
    """

    file_name = os.path.basename(file_path)
    arc_name = file_alias if file_alias is not None else file_name
    with tarfile.open(tar_path, 'w') as tar:
        tar.add(
            file_path,
            arcname=arc_name,
            filter=get_progress_printer(count_dir_files(file_path), lambda x: x)
        )
