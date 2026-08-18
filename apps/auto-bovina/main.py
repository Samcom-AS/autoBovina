"""Executable-compatible entry point for autoBovina.

It works both from the checked-out source tree and when bundled as
``dist\\autoBovina\\autoBovina.exe`` by ``build.ps1``.
"""

from __future__ import annotations

import sys
from pathlib import Path


if not getattr(sys, "frozen", False):
    source_root = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(source_root))

from autobovina.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
