from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Sequence

import pytest


def _load_module() -> ModuleType:
    path = Path(__file__).parents[2] / "scripts" / "remote_docker_runtime.py"
    spec = importlib.util.spec_from_file_location("remote_docker_runtime", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


remote = _load_module()


class FakeRunner:
    def __init__(self, outputs: list[str] | None = None, returncodes: list[int] | None = None) -> None:
        self.outputs = list(outputs or [])
        self.returncodes = list(returncodes or [])
        self.calls: list[tuple[list[str], bytes | None]] = []

    def run(
        self,
        args: Sequence[str],
        *,
        input_bytes: bytes | None = None,
        capture: bool = False,
        check: bool = True,
        announce: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [str(arg) for arg in args]
        self.calls.append((command, input_bytes))
        returncode = self.returncodes.pop(0) if self.returncodes else 0
        stdout = self.outputs.pop(0) if self.outputs else ""
        if check and returncode:
            raise subprocess.CalledProcessError(returncode, command)
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")


def _config(tmp_path: Path) -> object:
    return remote.RemoteRuntimeConfig(
        docker_host="ssh://flowise",
        ssh_alias="flowise",
        project="glavred",
        frontend_port=5176,
        api_port=8000,
        secret_dir="/opt/glavred-secrets",
        runtime_env_file=tmp_path / "runtime.env",
        compose_files=(tmp_path / "compose.yaml", tmp_path / "compose.remote.yaml"),
    )


def _prepare_runtime_inputs(tmp_path: Path) -> None:
    (tmp_path / "runtime.env").write_text("GLAVRED_ENV=test\n", encoding="utf-8")
    (tmp_path / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (tmp_path / "compose.remote.yaml").write_text("services: {}\n", encoding="utf-8")


def test_runtime_env_sanitizer_separates_allowlisted_secrets(tmp_path: Path) -> None:
    source = tmp_path / ".env"
    target = tmp_path / "runtime.env"
    source.write_text(
        "OPENROUTER_API_KEY=secret-token\n"
        "GLAVRED_DEV_AUTH_PASSWORD='secret-password'\n"
        "OPENROUTER_DEFAULT_MODEL=test/model\n",
        encoding="utf-8",
    )

    secrets = remote.RuntimeEnvSanitizer().prepare(source, target)

    assert secrets == {
        "OPENROUTER_API_KEY": "secret-token",
        "GLAVRED_DEV_AUTH_PASSWORD": "secret-password",
    }
    assert target.read_text(encoding="utf-8") == "OPENROUTER_DEFAULT_MODEL=test/model\n"


def test_runtime_env_sanitizer_rejects_unknown_secret(tmp_path: Path) -> None:
    source = tmp_path / ".env"
    source.write_text(
        "OPENROUTER_API_KEY=secret-token\n"
        "GLAVRED_DEV_AUTH_PASSWORD=password\n"
        "UNEXPECTED_TOKEN=must-not-pass\n",
        encoding="utf-8",
    )

    with pytest.raises(remote.RemoteRuntimeError, match="UNEXPECTED_TOKEN"):
        remote.RuntimeEnvSanitizer().prepare(source, tmp_path / "runtime.env")


def test_runtime_env_sanitizer_omits_local_database_url(tmp_path: Path) -> None:
    source = tmp_path / ".env"
    source.write_text(
        "OPENROUTER_API_KEY=secret-token\n"
        "GLAVRED_DEV_AUTH_PASSWORD=password\n"
        "DATABASE_URL=postgresql://user:password@database/app\n",
        encoding="utf-8",
    )

    remote.RuntimeEnvSanitizer().prepare(source, tmp_path / "runtime.env")

    assert "DATABASE_URL" not in (tmp_path / "runtime.env").read_text(encoding="utf-8")


def test_runtime_env_sanitizer_rejects_unknown_embedded_credentials(tmp_path: Path) -> None:
    source = tmp_path / ".env"
    source.write_text(
        "OPENROUTER_API_KEY=secret-token\n"
        "GLAVRED_DEV_AUTH_PASSWORD=password\n"
        "EXTERNAL_SERVICE_URL=https://user:password@example.test/api\n",
        encoding="utf-8",
    )

    with pytest.raises(remote.RemoteRuntimeError, match="EXTERNAL_SERVICE_URL"):
        remote.RuntimeEnvSanitizer().prepare(source, tmp_path / "runtime.env")


def test_lock_is_released_after_failure(tmp_path: Path) -> None:
    runner = FakeRunner()
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(RuntimeError, match="boom"):
        with runtime.locked():
            raise RuntimeError("boom")

    assert "mkdir" in runner.calls[0][0][-1]
    assert runner.calls[-1][0][-1].startswith("rm -rf /var/lock/glavred-remote-runtime.lock")


def test_lock_contention_is_controlled(tmp_path: Path) -> None:
    runner = FakeRunner(returncodes=[1])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(remote.RemoteRuntimeError, match="locked"):
        with runtime.locked():
            raise AssertionError("must not enter")


def test_foreign_container_port_owner_is_rejected(tmp_path: Path) -> None:
    runner = FakeRunner(outputs=["foreign-api|127.0.0.1:8000->8000/tcp|power-web-os\n"])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(remote.RemoteRuntimeError, match="another container"):
        runtime._assert_ports_available()


def test_unapproved_ssh_target_is_rejected(tmp_path: Path) -> None:
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), FakeRunner())

    with pytest.raises(remote.RemoteRuntimeError, match="approved root endpoint"):
        runtime._assert_ssh_target(
            {"hostname": "213.148.13.45", "user": "operator", "port": "22"}
        )


def test_foreign_glavred_named_container_is_rejected(tmp_path: Path) -> None:
    runner = FakeRunner(outputs=["glavred-backend-1|foreign-project\n"])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(remote.RemoteRuntimeError, match="foreign ownership"):
        runtime._assert_compose_ownership()


def test_authenticated_suite_requires_running_stack(tmp_path: Path) -> None:
    runner = FakeRunner(outputs=["backend\nredis\n"])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(remote.RemoteRuntimeError, match="frontend, worker"):
        runtime._assert_stack_running()


def test_secret_value_is_only_sent_over_stdin(tmp_path: Path) -> None:
    runner = FakeRunner()
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    runtime._write_secret("openrouter_api_key", "do-not-print")

    command, input_bytes = runner.calls[0]
    assert "do-not-print" not in " ".join(command)
    assert input_bytes == b"do-not-print"


def test_tunnel_command_uses_loopback_ports(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), FakeRunner())

    runtime.tunnel_command()

    assert capsys.readouterr().out.strip() == (
        "ssh -N -L 5176:127.0.0.1:5176 -L 8000:127.0.0.1:8000 flowise"
    )


def test_exec_consumes_documented_argument_separator(tmp_path: Path) -> None:
    runner = FakeRunner()
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    runtime.exec("worker", ["--", "celery", "inspect", "ping"])

    command, _ = runner.calls[0]
    assert command[-3:] == ["celery", "inspect", "ping"]


@pytest.mark.parametrize(
    ("suite", "expected_service"),
    [
        ("backend", "qa"),
        ("auth", "qa-live"),
        ("live-radar", "qa-live"),
        ("workspace-integrity", "qa-live"),
    ],
)
def test_suite_uses_clean_or_live_qa_boundary(
    tmp_path: Path, suite: str, expected_service: str
) -> None:
    _prepare_runtime_inputs(tmp_path)
    outputs = (
        ["backend\nfrontend\nworker\nredis\n"]
        if suite in {"auth", "live-radar", "workspace-integrity"}
        else []
    )
    runner = FakeRunner(outputs=outputs)
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    runtime.test(suite)

    run_commands = [command for command, _ in runner.calls if "run" in command]
    assert run_commands
    assert expected_service in run_commands[0]


def test_live_radar_can_reuse_latest_saved_run_for_acceptance_retry(tmp_path: Path) -> None:
    _prepare_runtime_inputs(tmp_path)
    runner = FakeRunner(outputs=["backend\nfrontend\nworker\nredis\n"])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    runtime.test("live-radar", reuse_live_run=True)

    run_command = next(command for command, _ in runner.calls if "run" in command)
    assert "qa-live" in run_command
    assert "GLAVRED_LIVE_PROOF_REUSE=1" in run_command[-1]


def test_live_run_reuse_is_rejected_for_other_suites(tmp_path: Path) -> None:
    _prepare_runtime_inputs(tmp_path)
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), FakeRunner())

    with pytest.raises(remote.RemoteRuntimeError, match="only valid for the live-radar suite"):
        runtime.test("backend", reuse_live_run=True)


def test_logs_redact_allowlisted_secret_values(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".env").write_text(
        "OPENROUTER_API_KEY=private-provider-key\n"
        "GLAVRED_DEV_AUTH_PASSWORD=private-login-password\n",
        encoding="utf-8",
    )
    runner = FakeRunner(outputs=["provider private-provider-key login private-login-password\n"])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    runtime.logs("backend")

    output = capsys.readouterr().out
    assert "private-provider-key" not in output
    assert "private-login-password" not in output
    assert output.count("[REDACTED]") == 2


def test_artifact_export_container_is_removed_after_copy_failure(tmp_path: Path) -> None:
    _prepare_runtime_inputs(tmp_path)
    runner = FakeRunner(returncodes=[0, 0, 0, 1])
    runtime = remote.RemoteDockerRuntime(tmp_path, _config(tmp_path), runner)

    with pytest.raises(subprocess.CalledProcessError):
        runtime.collect_artifacts(tmp_path / "proof")

    commands = [" ".join(command) for command, _ in runner.calls]
    assert any("rm -f glavred-artifact-export" in command for command in commands)
    assert commands[-1].endswith("rm -rf /var/lock/glavred-remote-runtime.lock")
