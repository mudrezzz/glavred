#!/usr/bin/env python3
"""Operate the isolated Glavred Docker test runtime through the flowise SSH host."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Iterator, Sequence


EXPECTED_HOSTNAME = "213.148.13.45"
EXPECTED_SSH_USER = "root"
EXPECTED_SSH_PORT = "22"
MIN_REMOTE_CPUS = 4
MIN_REMOTE_MEMORY_BYTES = 12 * 1024**3
MIN_REMOTE_FREE_KIB = 10 * 1024**2
POWER_WEB_PORTS = {5173, 8001, 6380}
SECRET_FILES = {
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "GLAVRED_DEV_AUTH_PASSWORD": "glavred_dev_auth_password",
}
SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
LOCAL_ONLY_RUNTIME_SETTINGS = {"DATABASE_URL"}
TEST_SUITES: dict[str, list[list[str]]] = {
    "remote-runtime": [
        [
            "python",
            "-m",
            "pytest",
            "backend/tests/test_remote_docker_runtime.py",
            "backend/tests/test_settings_secret_files.py",
        ]
    ],
    "backend": [["python", "-m", "pytest", "backend/tests"]],
    "frontend": [["npm", "test", "--", "--run"]],
    "architecture": [["npm", "run", "test:architecture"]],
    "design": [["npm", "run", "test:design"]],
    "visual": [["npm", "run", "test:visual"]],
    "smoke": [["npm", "run", "smoke"]],
    "auth": [["npm", "run", "test:auth-session"]],
    "workspace-integrity": [
        [
            "python",
            "scripts/check_workspace_integrity.py",
            "--db",
            "/runtime-var/glavred-portfolio.sqlite3",
            "--fail-on-error",
        ]
    ],
    "live-radar": [
        [
            "sh",
            "-lc",
            "GLAVRED_LIVE_PROOF_SKIP_REPLAY=1 node scripts/live_radar_signal_utility_proof.mjs",
        ]
    ],
}
TEST_SUITES["full"] = [
    *TEST_SUITES["backend"],
    *TEST_SUITES["frontend"],
    *TEST_SUITES["architecture"],
    *TEST_SUITES["design"],
    *TEST_SUITES["visual"],
    *TEST_SUITES["smoke"],
    *TEST_SUITES["workspace-integrity"],
    [
        "python",
        "scripts/backend-architecture-audit.py",
        "--format",
        "json",
        "--ledger",
        "docs/architecture/backend-architecture-debt-ledger.json",
        "--fail-on-unledgered",
        "high",
    ],
]


class RemoteRuntimeError(RuntimeError):
    """Controlled operator error without secret-bearing payloads."""


@dataclass(frozen=True)
class RemoteRuntimeConfig:
    docker_host: str
    ssh_alias: str
    project: str
    frontend_port: int
    api_port: int
    secret_dir: str
    runtime_env_file: Path
    compose_files: tuple[Path, Path]
    lock_dir: str = "/var/lock/glavred-remote-runtime.lock"

    @classmethod
    def from_environment(cls, root: Path) -> "RemoteRuntimeConfig":
        docker_host = os.getenv("GLAVRED_REMOTE_DOCKER_HOST", "ssh://flowise")
        if not docker_host.startswith("ssh://"):
            raise RemoteRuntimeError("GLAVRED_REMOTE_DOCKER_HOST must use ssh://")
        ssh_alias = docker_host.removeprefix("ssh://")
        if not re.fullmatch(r"[A-Za-z0-9_.@-]+", ssh_alias):
            raise RemoteRuntimeError("Remote SSH alias contains unsupported characters")
        project = os.getenv("GLAVRED_REMOTE_PROJECT", "glavred")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", project):
            raise RemoteRuntimeError("GLAVRED_REMOTE_PROJECT is invalid")
        secret_dir = os.getenv("GLAVRED_REMOTE_SECRET_DIR", "/opt/glavred-secrets")
        if not re.fullmatch(r"/[A-Za-z0-9_./-]+", secret_dir):
            raise RemoteRuntimeError("GLAVRED_REMOTE_SECRET_DIR must be a safe absolute path")
        return cls(
            docker_host=docker_host,
            ssh_alias=ssh_alias,
            project=project,
            frontend_port=_port_from_env("GLAVRED_REMOTE_FRONTEND_PORT", 5176),
            api_port=_port_from_env("GLAVRED_REMOTE_API_PORT", 8000),
            secret_dir=secret_dir.rstrip("/"),
            runtime_env_file=root / "var" / "remote" / "glavred.runtime.env",
            compose_files=(root / "compose.yaml", root / "compose.remote.yaml"),
        )


class CommandRunner:
    def run(
        self,
        args: Sequence[str],
        *,
        input_bytes: bytes | None = None,
        capture: bool = False,
        check: bool = True,
        announce: bool = True,
    ) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
        if announce:
            print(f"$ {_display_command(args)}", flush=True)
        if input_bytes is not None:
            return subprocess.run(args, input=input_bytes, capture_output=capture, check=check)
        return subprocess.run(args, text=True, capture_output=capture, check=check)


class RuntimeEnvSanitizer:
    def prepare(self, source: Path, target: Path) -> dict[str, str]:
        if not source.is_file():
            raise RemoteRuntimeError(f"Runtime source env does not exist: {source}")
        secrets: dict[str, str] = {}
        safe_lines: list[str] = []
        for raw_line in source.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = stripped.removeprefix("export ").split("=", 1)
            key = key.strip()
            value = _decode_env_value(raw_value)
            if key in SECRET_FILES:
                if not value:
                    raise RemoteRuntimeError(f"Required secret {key} is empty")
                secrets[key] = value
                continue
            if key in LOCAL_ONLY_RUNTIME_SETTINGS:
                continue
            if value and any(marker in key.upper() for marker in SECRET_MARKERS):
                raise RemoteRuntimeError(f"Unknown secret-like setting is not allowlisted: {key}")
            if value and re.search(r"://[^/@:\s]+:[^/@\s]+@", value):
                raise RemoteRuntimeError(
                    f"Credential-bearing setting cannot enter the remote runtime env: {key}"
                )
            safe_lines.append(f"{key}={raw_value}")
        missing = sorted(set(SECRET_FILES) - set(secrets))
        if missing:
            raise RemoteRuntimeError(f"Required secrets are missing: {', '.join(missing)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(safe_lines) + "\n", encoding="utf-8", newline="\n")
        return secrets


class RemoteDockerRuntime:
    def __init__(
        self,
        root: Path,
        config: RemoteRuntimeConfig,
        runner: CommandRunner | None = None,
    ) -> None:
        self.root = root
        self.config = config
        self.runner = runner or CommandRunner()

    def doctor(self) -> None:
        ssh_config = self._capture(["ssh", "-G", self.config.ssh_alias])
        resolved = _parse_ssh_config(ssh_config)
        self._assert_ssh_target(resolved)
        self.runner.run(["ssh", "-o", "BatchMode=yes", self.config.ssh_alias, "true"])
        info = self._capture(
            [
                "docker",
                "--host",
                self.config.docker_host,
                "info",
                "--format",
                "host={{.Name}} cpus={{.NCPU}} memory={{.MemTotal}} root={{.DockerRootDir}}",
            ]
        )
        resources = _parse_docker_info(info)
        if resources["cpus"] < MIN_REMOTE_CPUS or resources["memory"] < MIN_REMOTE_MEMORY_BYTES:
            raise RemoteRuntimeError("Remote Docker host does not satisfy the Glavred resource floor")
        free_kib = int(
            self._capture(
                [
                    "ssh",
                    self.config.ssh_alias,
                    "df -Pk /var/lib/docker | awk 'NR==2 {print $4}'",
                ]
            ).strip()
        )
        if free_kib < MIN_REMOTE_FREE_KIB:
            raise RemoteRuntimeError("Remote Docker host has less than 10 GiB free")
        self._assert_ports_available()
        self._assert_compose_ownership()
        secret_status = self._capture(
            [
                "ssh",
                self.config.ssh_alias,
                (
                    f"if test -d {shlex.quote(self.config.secret_dir)}; then "
                    f"stat -c 'dir:%a' {shlex.quote(self.config.secret_dir)}; "
                    "else echo 'dir:missing'; fi; "
                    f"for name in {' '.join(SECRET_FILES.values())}; do "
                    f"path={shlex.quote(self.config.secret_dir)}/$name; "
                    "if test -f \"$path\"; then stat -c '%n:%a' \"$path\"; else echo \"$path:missing\"; fi; done"
                ),
            ]
        )
        for line in secret_status.splitlines():
            if line.startswith("dir:") and line not in {"dir:missing", "dir:700"}:
                raise RemoteRuntimeError("Remote secret directory permissions must be 0700")
            if not line.startswith("dir:") and not line.endswith(":missing") and not line.endswith(":600"):
                raise RemoteRuntimeError("Remote secret file permissions must be 0600")
        print(info.strip())
        print(f"docker-free-kib={free_kib}")
        print(secret_status.strip())
        print(
            f"Power Web reserved ports: {', '.join(str(port) for port in sorted(POWER_WEB_PORTS))}"
        )
        print("Remote Docker doctor passed.")

    def sync_secrets(self, env_file: Path) -> None:
        sanitizer = RuntimeEnvSanitizer()
        secrets = sanitizer.prepare(env_file, self.config.runtime_env_file)
        with self.locked():
            for setting_name, remote_name in SECRET_FILES.items():
                self._write_secret(remote_name, secrets[setting_name])
        print(
            f"Prepared sanitized runtime env with {len(secrets)} file-backed secrets; values were not printed."
        )

    def build(self) -> None:
        self._require_runtime_inputs()
        with self.locked():
            self.runner.run([*self._compose(), "--profile", "qa", "build"])

    def up(self) -> None:
        self._require_runtime_inputs()
        self._assert_ports_available()
        with self.locked():
            self.runner.run([*self._compose(), "up", "-d", "--build"])

    def ps(self) -> None:
        self.runner.run([*self._compose(), "ps"])

    def exec(self, service: str, command: list[str]) -> None:
        if command[:1] == ["--"]:
            command = command[1:]
        if not command:
            raise RemoteRuntimeError("exec requires a command")
        self.runner.run([*self._compose(), "exec", "-T", service, *command])

    def test(self, suite: str, *, reuse_live_run: bool = False) -> None:
        self._require_runtime_inputs()
        if reuse_live_run and suite != "live-radar":
            raise RemoteRuntimeError("--reuse-live-run is only valid for the live-radar suite")
        if suite in {"auth", "live-radar", "workspace-integrity", "full"}:
            self._assert_stack_running()
        commands = TEST_SUITES[suite]
        if reuse_live_run:
            commands = [
                [
                    "sh",
                    "-lc",
                    (
                        "GLAVRED_LIVE_PROOF_SKIP_REPLAY=1 "
                        "GLAVRED_LIVE_PROOF_REUSE=1 "
                        "node scripts/live_radar_signal_utility_proof.mjs"
                    ),
                ]
            ]
        with self.locked():
            for command in commands:
                qa_service = self._qa_service_for(suite, command)
                self.runner.run(
                    [
                        *self._compose(),
                        "--profile",
                        "qa",
                        "run",
                        "--rm",
                        "--no-deps",
                        qa_service,
                        *command,
                    ]
                )

    @staticmethod
    def _qa_service_for(suite: str, command: list[str]) -> str:
        if suite in {"auth", "live-radar", "workspace-integrity"}:
            return "qa-live"
        if command in TEST_SUITES["workspace-integrity"]:
            return "qa-live"
        return "qa"

    def collect_artifacts(self, target: Path) -> None:
        self._require_runtime_inputs()
        name = f"{self.config.project}-artifact-export"
        target.mkdir(parents=True, exist_ok=True)
        with self.locked():
            self.runner.run(
                ["docker", "--host", self.config.docker_host, "rm", "-f", name],
                check=False,
            )
            self.runner.run(
                [
                    *self._compose(),
                    "--profile",
                    "qa",
                    "run",
                    "-d",
                    "--name",
                    name,
                    "--no-deps",
                    "qa",
                    "sleep",
                    "300",
                ]
            )
            try:
                self.runner.run(
                    ["docker", "--host", self.config.docker_host, "cp", f"{name}:/app/var/.", str(target)]
                )
            finally:
                self.runner.run(
                    ["docker", "--host", self.config.docker_host, "rm", "-f", name],
                    check=False,
                )

    def logs(self, service: str) -> None:
        output = self._capture([*self._compose(), "logs", "--tail", "250", service])
        print(_redact_text(output, self._known_secret_values()), end="")

    def down(self) -> None:
        with self.locked():
            self.runner.run([*self._compose(), "down", "--remove-orphans"])

    def tunnel_command(self) -> None:
        print(
            "ssh -N "
            f"-L {self.config.frontend_port}:127.0.0.1:{self.config.frontend_port} "
            f"-L {self.config.api_port}:127.0.0.1:{self.config.api_port} "
            f"{self.config.ssh_alias}"
        )

    @contextmanager
    def locked(self) -> Iterator[None]:
        acquire = self.runner.run(
            [
                "ssh",
                self.config.ssh_alias,
                (
                    f"mkdir {shlex.quote(self.config.lock_dir)} 2>/dev/null && "
                    f"printf '%s\\n' {shlex.quote(self.config.project)} > "
                    f"{shlex.quote(self.config.lock_dir)}/owner"
                ),
            ],
            check=False,
        )
        if acquire.returncode != 0:
            raise RemoteRuntimeError("Remote Glavred runtime is locked by another operation")
        try:
            yield
        finally:
            self.runner.run(
                ["ssh", self.config.ssh_alias, f"rm -rf {shlex.quote(self.config.lock_dir)}"],
                check=False,
            )

    def _write_secret(self, remote_name: str, value: str) -> None:
        remote_dir = shlex.quote(self.config.secret_dir)
        remote_path = shlex.quote(f"{self.config.secret_dir}/{remote_name}")
        command = (
            "set -eu; umask 077; "
            f"install -d -m 700 {remote_dir}; "
            f"tmp=$(mktemp {remote_dir}/.{remote_name}.XXXXXX); "
            "cat > \"$tmp\"; chmod 600 \"$tmp\"; "
            f"mv \"$tmp\" {remote_path}"
        )
        result = self.runner.run(
            ["ssh", self.config.ssh_alias, command],
            input_bytes=value.encode("utf-8"),
            capture=True,
        )
        if result.returncode != 0:
            raise RemoteRuntimeError(f"Failed to install remote secret {remote_name}")

    def _assert_ports_available(self) -> None:
        container_rows = self._capture(
            [
                "docker",
                "--host",
                self.config.docker_host,
                "ps",
                "--format",
                '{{.Names}}|{{.Ports}}|{{.Label "com.docker.compose.project"}}',
            ]
        )
        allowed_occupied: set[int] = set()
        for row in container_rows.splitlines():
            name, ports, project = (row.split("|", 2) + ["", ""])[:3]
            for port in (self.config.frontend_port, self.config.api_port):
                if re.search(rf"(?:127\.0\.0\.1|0\.0\.0\.0|\[::\]):{port}->", ports):
                    if project != self.config.project:
                        raise RemoteRuntimeError(f"Port {port} is owned by another container: {name}")
                    allowed_occupied.add(port)
        listeners = self._capture(["ssh", self.config.ssh_alias, "ss -ltnH"])
        for port in (self.config.frontend_port, self.config.api_port):
            if re.search(rf":{port}\s", listeners) and port not in allowed_occupied:
                raise RemoteRuntimeError(f"Port {port} is occupied outside the Glavred compose project")

    def _assert_ssh_target(self, resolved: dict[str, str]) -> None:
        expected = {
            "hostname": EXPECTED_HOSTNAME,
            "user": EXPECTED_SSH_USER,
            "port": EXPECTED_SSH_PORT,
        }
        if any(resolved.get(key) != value for key, value in expected.items()):
            raise RemoteRuntimeError(
                f"SSH alias {self.config.ssh_alias} does not resolve to the approved root endpoint"
            )

    def _assert_compose_ownership(self) -> None:
        rows = self._capture(
            [
                "docker",
                "--host",
                self.config.docker_host,
                "ps",
                "-a",
                "--filter",
                "name=glavred",
                "--format",
                '{{.Names}}|{{.Label "com.docker.compose.project"}}',
            ]
        )
        for row in rows.splitlines():
            name, _, project = row.partition("|")
            if name.startswith(f"{self.config.project}-") and project != self.config.project:
                raise RemoteRuntimeError(f"Glavred-named container has foreign ownership: {name}")

    def _assert_stack_running(self) -> None:
        running = set(
            self._capture([*self._compose(), "ps", "--services", "--status", "running"])
            .strip()
            .splitlines()
        )
        required = {"backend", "frontend", "worker", "redis"}
        missing = sorted(required - running)
        if missing:
            raise RemoteRuntimeError(
                f"Remote stack must be running for this suite: {', '.join(missing)}"
            )

    def _require_runtime_inputs(self) -> None:
        if not self.config.runtime_env_file.is_file():
            raise RemoteRuntimeError("Run sync-secrets before remote build or execution")
        for compose_file in self.config.compose_files:
            if not compose_file.is_file():
                raise RemoteRuntimeError(f"Missing compose file: {compose_file}")

    def _capture(self, args: Sequence[str]) -> str:
        result = self.runner.run(args, capture=True)
        stdout = result.stdout
        return stdout.decode("utf-8", errors="replace") if isinstance(stdout, bytes) else stdout

    def _known_secret_values(self) -> list[str]:
        source = self.root / ".env"
        if not source.is_file():
            return []
        values: list[str] = []
        for raw_line in source.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = stripped.removeprefix("export ").split("=", 1)
            if key.strip() in SECRET_FILES:
                value = _decode_env_value(raw_value)
                if value:
                    values.append(value)
        return values

    def _compose(self) -> list[str]:
        command = ["docker", "--host", self.config.docker_host, "compose", "-p", self.config.project]
        for compose_file in self.config.compose_files:
            command.extend(["-f", str(compose_file)])
        return command


def _port_from_env(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if not 1024 <= value <= 65535:
        raise RemoteRuntimeError(f"{name} must be between 1024 and 65535")
    return value


def _parse_ssh_config(source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in source.splitlines():
        key, _, value = line.partition(" ")
        if key in {"hostname", "user", "port"}:
            result[key] = value.strip()
    return result


def _parse_docker_info(source: str) -> dict[str, int]:
    match = re.search(r"\bcpus=(\d+)\s+memory=(\d+)\b", source)
    if not match:
        raise RemoteRuntimeError("Remote Docker resource report is malformed")
    return {"cpus": int(match.group(1)), "memory": int(match.group(2))}


def _decode_env_value(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {'"', "'"}:
        return stripped[1:-1]
    return stripped


def _display_command(args: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in args)


def _redact_text(source: str, values: Sequence[str]) -> str:
    result = source
    for value in values:
        result = result.replace(value, "[REDACTED]")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor")
    sync_parser = subparsers.add_parser("sync-secrets")
    sync_parser.add_argument("--env-file", type=Path, default=Path(".env"))
    subparsers.add_parser("build")
    subparsers.add_parser("up")
    subparsers.add_parser("ps")
    exec_parser = subparsers.add_parser("exec")
    exec_parser.add_argument("--service", required=True)
    exec_parser.add_argument("args", nargs=argparse.REMAINDER)
    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--suite", choices=sorted(TEST_SUITES), required=True)
    test_parser.add_argument("--reuse-live-run", action="store_true")
    collect_parser = subparsers.add_parser("collect-artifacts")
    collect_parser.add_argument("--target", type=Path, default=Path("var/remote-proof"))
    logs_parser = subparsers.add_parser("logs")
    logs_parser.add_argument("--service", required=True)
    subparsers.add_parser("down")
    subparsers.add_parser("tunnel-command")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    args = build_parser().parse_args(argv)
    runtime = RemoteDockerRuntime(root, RemoteRuntimeConfig.from_environment(root))
    try:
        if args.command == "doctor":
            runtime.doctor()
        elif args.command == "sync-secrets":
            runtime.sync_secrets(args.env_file)
        elif args.command == "build":
            runtime.build()
        elif args.command == "up":
            runtime.up()
        elif args.command == "ps":
            runtime.ps()
        elif args.command == "exec":
            runtime.exec(args.service, list(args.args))
        elif args.command == "test":
            runtime.test(args.suite, reuse_live_run=args.reuse_live_run)
        elif args.command == "collect-artifacts":
            runtime.collect_artifacts(args.target)
        elif args.command == "logs":
            runtime.logs(args.service)
        elif args.command == "down":
            runtime.down()
        elif args.command == "tunnel-command":
            runtime.tunnel_command()
    except (RemoteRuntimeError, subprocess.CalledProcessError, ValueError) as error:
        print(f"remote-runtime-error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
