"""Command runner that proxies invocation to the Node.js CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from ._config import get_cli_entry_path
from ._installer import InstallError, _detect_command, ensure_cli_installed


def run_cli(argv: Sequence[str]) -> int:
    """Ensure the CLI is installed and execute it with the provided args."""
    try:
        install_dir = ensure_cli_installed()
    except InstallError as exc:
        message = f"[dev-tool] {exc}"
        print(message, file=sys.stderr)
        return 1

    entry_path = get_cli_entry_path()
    if not entry_path.is_file():
        print(
            f"[dev-tool] CLI entry '{entry_path}' is missing. "
            "Re-run with AILINONE_CLI_FORCE_INSTALL=1 to reinstall.",
            file=sys.stderr,
        )
        return 1

    node_cmd = _detect_command("node")
    env = os.environ.copy()
    env.setdefault("AILINONE_CLI_HOME", str(install_dir))

    process = subprocess.run(
        [node_cmd, str(entry_path), *argv],
        env=env,
    )
    return process.returncode

