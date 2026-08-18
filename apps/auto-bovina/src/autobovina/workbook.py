"""Excel adapter for the fixed column layout used by autoBovina."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import AnimalRecord


FIRST_DATA_ROW = 9


def read_records_with_xlwings(workbook_path: Path, sheet_name: str) -> list[AnimalRecord]:
    """Read columns C, E, and G:N without writing to the workbook.

    ``xlwings`` is imported lazily so unit tests and dry-run code do not need
    Microsoft Excel installed.
    """
    with _open_read_only_book(workbook_path) as book:
        sheet = book.sheets[sheet_name]
        last_row = sheet.range(f"E{sheet.cells.last_cell.row}").end("up").row
        if last_row < FIRST_DATA_ROW:
            return []

        records = []
        for row in range(FIRST_DATA_ROW, last_row + 1):
            records.append(
                AnimalRecord(
                    row=row,
                    criterion_number=sheet.range(f"C{row}").value,
                    ear_tag=sheet.range(f"E{row}").value,
                    age=sheet.range(f"G{row}").value,
                    sex=sheet.range(f"H{row}").value,
                    breed=sheet.range(f"I{row}").value,
                    owner=sheet.range(f"J{row}").value,
                    locality=sheet.range(f"K{row}").value,
                    holding_code=sheet.range(f"L{row}").value,
                    passport_number=sheet.range(f"M{row}").value,
                    vehicle=sheet.range(f"N{row}").value,
                )
            )
        return records


def read_doctor_id_with_xlwings(workbook_path: Path, sheet_name: str) -> object:
    """Read the recovered automation-sheet value from cell ``E2``.

    Reading is deliberately isolated from workflow construction, so tests can
    supply an anonymized value and never require Excel.
    """
    with _open_read_only_book(workbook_path) as book:
        return book.sheets[sheet_name].range("E2").value


@contextmanager
def _open_read_only_book(workbook_path: Path) -> Iterator[object]:
    """Open a workbook in an app owned by this process and always release it."""
    try:
        import xlwings as xw
    except ImportError as exc:  # pragma: no cover - depends on a Windows Excel installation
        raise RuntimeError("Install the [windows] extra to read legacy .xls workbooks.") from exc

    app = xw.App(visible=False, add_book=False)
    book = None
    try:
        book = app.books.open(str(workbook_path), update_links=False, read_only=True)
        yield book
    finally:
        if book is not None:
            book.close()
        app.quit()
