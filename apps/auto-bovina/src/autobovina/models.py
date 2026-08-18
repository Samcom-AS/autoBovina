"""Domain values represented by rows 9 onward in the legacy workbook."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimalRecord:
    row: int
    criterion_number: object
    ear_tag: object
    age: object
    sex: object
    breed: object
    owner: object
    locality: object
    holding_code: object
    passport_number: object
    vehicle: object


@dataclass(frozen=True)
class ValidationIssue:
    row: int
    field: str
    message: str


def display_value(value: object) -> str:
    """Match Excel-oriented comparison semantics while treating empty cells as missing."""
    if value is None:
        return ""
    return str(value).strip()
