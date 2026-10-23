"""Client to handle connections and actions executed against a remote host."""

from typing import List

from paramiko import RejectPolicy, RSAKey, SSHClient
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException

from log import LOGGER


class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        ssh_key_filepath: str,
        remote_path: str,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        self.client = None
        self._scp = None

    @property
    def connection(self):
        """Open SSH connection to remote host."""
        if self.client is not None:
            return self.client
        client = SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(RejectPolicy())
            client.connect(
                self.host,
                username=self.user,
                password=self.password,
                key_filename=self.ssh_key_filepath,
                timeout=5000,
            )
            self.client = client
            return client
        except AuthenticationException as e:
            LOGGER.error(
                f"AuthenticationException occurred; did you remember to generate an SSH key? {e}"
            )
            client.close()
            raise
        except Exception as e:
            client.close()
            LOGGER.error(f"Unexpected error occurred while connecting to host: {e}")
            raise

    @property
    def scp(self) -> SCPClient:
        if self._scp is None:
            self._scp = SCPClient(self.connection.get_transport())
        return self._scp

    def _get_ssh_key(self):
        """Fetch locally stored SSH key."""
        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            LOGGER.info(f"Found SSH key at self {self.ssh_key_filepath}")
            return self.ssh_key
        except SSHException as e:
            LOGGER.error(f"SSHException while getting SSH key: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected error while getting SSH key: {e}")

    def disconnect(self):
        """Close existing connections without opening any new connection."""
        if self._scp is not None:
            self._scp.close()
            self._scp = None
        if self.client is not None:
            self.client.close()
            self.client = None

    def bulk_upload(self, filepaths: List[str]):
        """
        Upload multiple files to a remote directory.

        :param List[str] filepaths: List of local files to be uploaded.
        """
        try:
            self.scp.put(filepaths, remote_path=self.remote_path, recursive=True)
            LOGGER.info(
                f"Finished uploading {len(filepaths)} files to {self.remote_path} on {self.host}"
            )
        except SCPException as e:
            LOGGER.error(f"SCPException during bulk upload: {e}")
        except Exception as e:
            LOGGER.error(f"Unexpected exception during bulk upload: {e}")

    def download_file(self, filepath: str):
        """
        Download file from remote host.

        :param str filepath: Path to file hosted on remote server to fetch.
        """
        self.scp.get(filepath)

    def execute_commands(self, commands: List[str]):
        """
        Execute multiple commands in succession.

        :param List[str] commands: List of unix commands as strings.
        """
        for cmd in commands:
            stdin, stdout, stderr = self.connection.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                LOGGER.info(f"INPUT: {cmd}\n \
                    OUTPUT: {line}")
