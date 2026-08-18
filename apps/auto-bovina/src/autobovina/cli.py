"""Safe command-line entry point for the recovered compatibility core."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import LegacySettings
from .runtime import default_data_path
from .service import prepare_batch, simulate_legacy_connection, simulate_vif_workflow
from .validation import load_breeds
from .workbook import read_doctor_id_with_xlwings, read_records_with_xlwings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an autoBovina legacy workbook without external automation.")
    parser.add_argument("--settings", type=Path, default=default_data_path("settings.txt"))
    parser.add_argument("--breeds", type=Path, default=default_data_path("rasa.txt"))
    parser.add_argument("--show-putty-transcript", action="store_true")
    parser.add_argument(
        "--show-vif-transcript",
        action="store_true",
        help="Print the recovered VIF action plan only; it never starts Putty or sends keys.",
    )
    args = parser.parse_args(argv)

    try:
        settings = LegacySettings.read(args.settings)
        if not settings.workbook_path.is_file():
            raise FileNotFoundError(f"Registrul Excel nu exista: {settings.workbook_path}")
        if not args.breeds.is_file():
            raise FileNotFoundError(f"Fisierul de rase nu exista: {args.breeds}")
        records = read_records_with_xlwings(settings.workbook_path, settings.receptions_sheet)
        result = prepare_batch(records, load_breeds(args.breeds))
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        print(f"Eroare configurare: {exc}")
        return 2
    if not result.valid:
        for issue in result.issues:
            print(f"row {issue.row}, {issue.field}: {issue.message}")
        return 2

    print(f"Validated {len(result.records)} reception rows. No external automation was executed.")
    if args.show_putty_transcript:
        for event in simulate_legacy_connection(settings.putty_path).events:
            print(event)
    if args.show_vif_transcript:
        try:
            doctor_id = read_doctor_id_with_xlwings(settings.workbook_path, settings.automation_sheet)
        except (KeyError, OSError, RuntimeError, ValueError) as exc:
            print(f"Eroare configurare: {exc}")
            return 2
        for step in simulate_vif_workflow(result.records, doctor_id).steps:
            print(step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
