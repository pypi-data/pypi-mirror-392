"""Configuration helpers for the PyPI launcher."""

from __future__ import annotations

import os
import sys
from pathlib import Path

CLI_PACKAGE_NAME = "@ailin/dev-tool"
CLI_VERSION = "0.0.2"
ENV_FORCE_INSTALL = "AILINONE_CLI_FORCE_INSTALL"
ENV_HOME_OVERRIDE = "AILINONE_CLI_HOME"
MANIFEST_FILENAME = "manifest.json"


def get_base_dir() -> Path:
    """Return the base directory used to persist npm assets."""
    override = os.environ.get(ENV_HOME_OVERRIDE)
    if override:
        return Path(override).expanduser()

    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))

    return base / "ailin" / "cli"


def get_install_dir() -> Path:
    """Return the directory holding the npm installation for this version."""
    return get_base_dir() / "runtime" / CLI_VERSION


def get_manifest_path() -> Path:
    """Return the path to the manifest that tracks the installed version."""
    return get_install_dir() / MANIFEST_FILENAME


def get_cli_entry_path() -> Path:
    """Return the absolute path to the CLI entry file inside the npm install."""
    return get_install_dir() / "node_modules" / "@ailin" / "dev-tool" / "dist" / "cli.bundle.cjs"


def get_package_json_path() -> Path:
    """Return the path to the package.json used for npm install."""
    return get_install_dir() / "package.json"

