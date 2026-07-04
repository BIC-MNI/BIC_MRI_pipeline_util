import re
import subprocess
from pathlib import Path

from bic_util.print import print_error_exit


def get_acls(file_path: Path):
    """
    Get the access-control lists (ACLs) of a file.
    """

    result = subprocess.run(['getfacl', str(file_path)], capture_output=True, text=True)
    if result.returncode != 0:
        print_error_exit(f'Unable to get the ACLs of file \'{file_path}\'.')

    return result.stdout


def set_acl(file_path: Path, acl: str):
    """
    Set an access-control list (ACL) on a file.
    """

    result = subprocess.run(['setfacl', '-m', acl, str(file_path)], capture_output=True)
    if result.returncode != 0:
        print_error_exit(f'Unable to set the ACL on file \'{file_path}\'.')


def copy_acls(src_path: Path, dst_path: Path):
    """
    Copy the access-control lists (ACLs) of a file on another file.
    """

    acls = get_acls(src_path)
    users = re.findall(r'user:(.+):r--', acls)
    for user in users:
        set_acl(dst_path, f'user:{user}:r--')
