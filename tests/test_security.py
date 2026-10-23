"""Offline SSH regressions: no hosts or credentials are contacted."""

import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

import paramiko
import pytest

SPEC = importlib.util.spec_from_file_location(
    "tutorial_server", Path(__file__).parents[1] / "paramiko_tutorial/server.py"
)
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


def make_client():
    return server.RemoteClient(
        "example.invalid", "user", "test-only", "/unused/key", "/tmp"
    )


def test_constructor_and_disconnect_have_no_external_side_effects():
    with patch.object(server, "SSHClient") as ssh, patch("os.system") as shell:
        client = make_client()
        client.disconnect()
    ssh.assert_not_called()
    shell.assert_not_called()
    assert not hasattr(client, "_upload_ssh_key")


def test_connection_requires_known_host_and_is_reused():
    with patch.object(server, "SSHClient") as ssh:
        client = make_client()
        connection = client.connection
        assert client.connection is connection
        connection.load_system_host_keys.assert_called_once_with()
        policy = connection.set_missing_host_key_policy.call_args.args[0]
        assert isinstance(policy, paramiko.RejectPolicy)
        connection.connect.assert_called_once()
        client.disconnect()
        connection.close.assert_called_once()
        assert client.client is None


def test_unknown_host_policy_rejects_without_learning_key():
    client = paramiko.SSHClient()
    client._transport = Mock()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    key = Mock()
    key.get_fingerprint.return_value = b"\x00" * 16
    with pytest.raises(paramiko.SSHException):
        client._policy.missing_host_key(client, "example.invalid", key)
    assert not client.get_host_keys()


@pytest.mark.parametrize(
    "failure",
    [
        paramiko.SSHException("unknown host"),
        paramiko.AuthenticationException("bad credentials"),
    ],
)
def test_failed_connection_is_closed_and_not_suppressed(failure):
    with patch.object(server, "SSHClient") as ssh:
        ssh.return_value.connect.side_effect = failure
        client = make_client()
        with pytest.raises(type(failure)):
            _ = client.connection
        ssh.return_value.close.assert_called_once()
        assert client.client is None


def test_scp_is_reused_and_disconnect_never_reconnects():
    with patch.object(server, "SSHClient") as ssh, patch.object(
        server, "SCPClient"
    ) as scp:
        client = make_client()
        assert client.scp is client.scp
        scp.assert_called_once()
        client.disconnect()
        client.disconnect()
        ssh.return_value.connect.assert_called_once()
        scp.return_value.close.assert_called_once()


def test_make_run_uses_script_entrypoint_without_executing_it(tmp_path):
    """Inspect the launch recipe without importing the application or opening SSH."""
    import subprocess

    activation = tmp_path / ".venv/bin/activate"
    activation.parent.mkdir(parents=True)
    activation.touch()
    makefile = Path(__file__).parents[1] / "Makefile"
    result = subprocess.run(
        [
            "make",
            "--dry-run",
            "-f",
            str(makefile),
            "run",
            "LOCAL_PYTHON=offline-python",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == "offline-python main.py"
