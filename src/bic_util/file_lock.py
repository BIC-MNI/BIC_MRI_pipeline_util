import fcntl
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from bic_util.print import print_error_exit, print_verbose


@dataclass
class FileLock:
    """
    Information about a lock file, that is a file being used as a lock by a script to make sure
    this script cannot be run more than once at any given time.
    """

    path: Path
    """
    Path of the lock file.
    """

    text_io: TextIO
    """
    Open IO to the lock file.
    """


def acquire_lock(lock_file_path: Path) -> FileLock:
    """
    Acquire a lock file using its path. Exit the program with an error if the lock is already
    taken.
    """

    print_verbose(f'acquiring lock \'{lock_file_path}\'')
    text_io = lock_file_path.open('w')
    try:
        fcntl.lockf(text_io, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return FileLock(lock_file_path, text_io)
    except OSError:
        print('script already running, aborting...')
        exit(0)


def release_lock(file_lock: FileLock) -> None:
    """
    Release a file lock. Exit the program with an error if the operation fails.
    """

    print_verbose(f'releasing lock \'{file_lock.path}\'')
    try:
        file_lock.text_io.close()
        file_lock.path.unlink()
    except Exception:
        print_error_exit(f'error while releasing lock \'{file_lock.path}\'')
