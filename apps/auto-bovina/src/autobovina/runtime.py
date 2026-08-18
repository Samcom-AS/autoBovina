"""Locations that work from source and from the Windows distribution."""

from __future__ import annotations

import sys
from pathlib import Path


def application_directory() -> Path:
    """Return the directory containing the mutable local ``data`` folder."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def default_data_path(filename: str) -> Path:
    external_path = application_directory() / "data" / filename
    if external_path.is_file():
        return external_path
    # Wheel installations carry the same safe templates as package data.
    return Path(__file__).resolve().parent / "data" / filename
