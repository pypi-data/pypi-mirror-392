"""Bootstraps the npm distribution used by the CLI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from ._config import (
    CLI_PACKAGE_NAME,
    CLI_VERSION,
    ENV_FORCE_INSTALL,
    get_cli_entry_path,
    get_install_dir,
    get_manifest_path,
    get_package_json_path,
)


class InstallError(RuntimeError):
    """Raised when the npm installation cannot be completed."""


def _detect_command(name: str) -> str:
    """Return the absolute path for a command or raise InstallError."""
    resolved = shutil.which(name)
    if resolved:
        return resolved
    raise InstallError(
        f"Required command '{name}' was not found on PATH. "
        "Install Node.js (includes npm) and try again."
    )


def _write_package_json(path: Path) -> None:
    """Write a minimal package.json to assist npm install."""
    package_json = {
        "name": "dev-tool-runtime",
        "private": True,
        "version": CLI_VERSION,
        "description": "Runtime workspace for the dev-tool PyPI launcher.",
    }
    path.write_text(json.dumps(package_json, indent=2), encoding="utf-8")


def _load_manifest(path: Path) -> Dict[str, Any] | None:
    """Read the manifest file if available."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _needs_install(manifest: Dict[str, Any] | None) -> bool:
    """Determine whether a fresh npm install is required."""
    if manifest is None:
        return True
    return manifest.get("version") != CLI_VERSION


def ensure_cli_installed(force: bool = False) -> Path:
    """Ensure the npm CLI distribution exists locally and return its directory."""
    install_dir = get_install_dir()
    manifest_path = get_manifest_path()
    manifest = _load_manifest(manifest_path)
    cli_entry = get_cli_entry_path()

    should_force = force or os.environ.get(ENV_FORCE_INSTALL) == "1"
    if not should_force and cli_entry.is_file() and not _needs_install(manifest):
        return install_dir

    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)

    _write_package_json(get_package_json_path())

    npm_cmd = _detect_command("npm")
    node_cmd = _detect_command("node")

    env = os.environ.copy()
    env.setdefault("npm_config_loglevel", "warn")

    install_args = [
        npm_cmd,
        "install",
        "--omit=dev",
        "--no-audit",
        "--no-fund",
        f"{CLI_PACKAGE_NAME}@{CLI_VERSION}",
    ]

    try:
        subprocess.run(install_args, cwd=str(install_dir), check=True, env=env)
    except subprocess.CalledProcessError as exc:
        raise InstallError(
            "Failed to install the npm CLI package. "
            "Inspect the npm output above for details."
        ) from exc

    if not cli_entry.is_file():
        raise InstallError(
            f"CLI entry '{cli_entry}' was not created by npm install. "
            "Please retry with AILINONE_CLI_FORCE_INSTALL=1."
        )

    try:
        node_version = subprocess.run(
            [node_cmd, "--version"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        npm_version = subprocess.run(
            [npm_cmd, "--version"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise InstallError("Failed to capture Node/npm versions.") from exc

    manifest_data = {
        "version": CLI_VERSION,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "node": node_version,
        "npm": npm_version,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    return install_dir

