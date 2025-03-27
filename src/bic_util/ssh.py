import os
import shlex
import stat
from collections.abc import Callable
from dataclasses import dataclass

from paramiko import SFTPClient, SSHClient

from bic_util.print import print_error_exit


@dataclass
class SSHCommandResult:
    """
    The exit code, standard output, and standard error returned by a command ran through SSH.
    """

    exit_code: int
    stdout: str
    stderr: str


def exec_ssh_shell_command(ssh_client: SSHClient, command: str) -> SSHCommandResult:
    """
    Execute a shell command on a remote server through SSH.
    """

    try:
        _, stdout, stderr = ssh_client.exec_command(f'bash -ic {shlex.quote(command)}', get_pty=True)

        # Wait until the command is completed and get the exit code.
        exit_code = stdout.channel.recv_exit_status()

        stdout_text = stdout.read().decode('utf-8')
        stderr_text = stderr.read().decode('utf-8')

        stdout.close()
        stderr.close()
    except Exception as e:
        print_error_exit(f"Error executing command '{command}'. Full error:\n{e}")

    return SSHCommandResult(
        exit_code = exit_code,
        stdout    = stdout_text,
        stderr    = stderr_text,
    )


def check_ssh_path_exists(ssh_client: SSHClient, remote_path: str) -> bool:
    """
    Check whether a file or directory exists on a remote server using SFTP.
    """

    sftp_client = ssh_client.open_sftp()

    try:
        sftp_client.stat(remote_path)
        return True
    except FileNotFoundError:
        return False
    finally:
        sftp_client.close()


def delete_ssh_file(ssh_client: SSHClient, remote_file_path: str):
    """
    Delete a file or directory on a remote server using SFTP.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        sftp_client.remove(remote_file_path)
    finally:
        sftp_client.close()


def delete_ssh_file_rec(ssh_client: SSHClient, remote_dir_path: str):
    """
    Delete a directory on a remote server using SFTP.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        _delete_ssh_file_rec_impl(sftp_client, remote_dir_path, '')
    finally:
        sftp_client.close()


def upload_ssh_file(ssh_client: SSHClient, local_file_path: str, remote_file_path: str):
    """
    Upload a local file to a remote server using SFTP.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        sftp_client.put(local_file_path, remote_file_path)
    finally:
        sftp_client.close()


def upload_ssh_directory(
    ssh_client: SSHClient,
    local_dir_path: str,
    remote_dir_path: str,
    progress_callback: Callable[[str], None] | None = None,
):
    """
    Upload a local directory to a remote server using SFTP. Printing the name of each file being
    uploaded.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        for root_dir_path, _, file_names in os.walk(local_dir_path):
            sub_dir_rel_path = os.path.normpath(os.path.relpath(root_dir_path, local_dir_path))
            remote_sub_dir_path = os.path.normpath(os.path.join(remote_dir_path, sub_dir_rel_path))

            sftp_client.mkdir(remote_sub_dir_path)

            for file_name in file_names:
                file_rel_path = os.path.join(sub_dir_rel_path, file_name)
                local_file_path = os.path.join(local_dir_path, file_rel_path)
                remote_file_path = os.path.join(remote_dir_path, file_rel_path)
                if progress_callback is not None:
                    progress_callback(file_rel_path)
                sftp_client.put(local_file_path, remote_file_path)
    finally:
        sftp_client.close()


def download_ssh_file(ssh_client: SSHClient, remote_file_path: str, local_file_path: str):
    """
    Download a remote file using SFTP.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        sftp_client.get(remote_file_path, local_file_path)
    finally:
        sftp_client.close()


def download_ssh_file_rec(ssh_client: SSHClient, remote_root_path: str, local_root_path: str, rel_path: str):
    """
    Download a remote file or directory using SFTP, recursively traversing directories and printing
    the name of each file being downloaded.
    """

    sftp_client = ssh_client.open_sftp()
    try:
        _download_ssh_file_rec_impl(sftp_client, remote_root_path, local_root_path, rel_path)
    finally:
        sftp_client.close()


def _delete_ssh_file_rec_impl(sftp_client: SFTPClient, remote_root_path: str, rel_path: str):
    """
    Utiliy function for `delete_ssh_file_rec`.
    """

    full_remote_path = os.path.join(remote_root_path, rel_path)

    item_attr = sftp_client.stat(full_remote_path)
    if item_attr.st_mode is None:
        raise Exception(f'ST mode not available for item \'{rel_path}\'.')

    if stat.S_ISDIR(item_attr.st_mode):
        for file_name in sftp_client.listdir(full_remote_path):
            sub_rel_path = os.path.join(rel_path, file_name)
            _delete_ssh_file_rec_impl(sftp_client, remote_root_path, sub_rel_path)

        sftp_client.rmdir(full_remote_path)
    else:
        print(f'Deleting file \'{rel_path}\'...')
        sftp_client.remove(full_remote_path)


def _download_ssh_file_rec_impl(sftp_client: SFTPClient, remote_root_path: str, local_root_path: str, rel_path: str):
    """
    Utiliy function for `download_ssh_file_rec`.
    """

    full_remote_path = os.path.join(remote_root_path, rel_path)
    full_local_path = os.path.join(local_root_path, rel_path)

    item_attr = sftp_client.stat(full_remote_path)
    if item_attr.st_mode is None:
        raise Exception(f'ST mode not available for item \'{rel_path}\'.')

    if stat.S_ISDIR(item_attr.st_mode):
        if not os.path.exists(full_local_path):
            os.makedirs(full_local_path)

        for file_name in sftp_client.listdir(full_remote_path):
            sub_rel_path = os.path.join(rel_path, file_name)
            _download_ssh_file_rec_impl(sftp_client, remote_root_path, local_root_path, sub_rel_path)
    else:
        print(f'Downloading file \'{rel_path}\'...')
        sftp_client.get(full_remote_path, full_local_path)
