"""Console script entry point."""

from __future__ import annotations

import sys

from . import __version__
from ._runner import run_cli


def main() -> None:
    """Invoke the CLI runner."""
    if "--pip-version" in sys.argv:
        print(__version__)
        return
    exit_code = run_cli(sys.argv[1:])
    raise SystemExit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    main()

