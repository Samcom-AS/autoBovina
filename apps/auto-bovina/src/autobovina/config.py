"""Read the four-line settings file used by the legacy executable."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SettingsError(ValueError):
    """Raised when the legacy settings file cannot be interpreted."""


@dataclass(frozen=True)
class LegacySettings:
    workbook_path: Path
    putty_path: Path
    receptions_sheet: str
    automation_sheet: str

    @classmethod
    def read(cls, path: Path) -> "LegacySettings":
        """Load the original four-line format without changing its contract."""
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            content = path.read_text(encoding="cp1250")

        lines = [line.rstrip("\r\n") for line in content.splitlines()]
        if len(lines) != 4 or any(not line.strip() for line in lines):
            raise SettingsError(
                f"{path} must contain exactly four non-empty lines: workbook, Putty, reception sheet, data sheet."
            )
        return cls(
            _resolve_path(lines[0], path),
            _resolve_path(lines[1], path),
            lines[2],
            lines[3],
        )


def _resolve_path(value: str, settings_path: Path) -> Path:
    """Support legacy absolute paths and portable relative distribution paths."""
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (settings_path.parent / candidate).resolve()
