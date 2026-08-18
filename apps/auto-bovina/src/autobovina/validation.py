"""Validation rules recovered from the original workbook-processing bytecode."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import AnimalRecord, ValidationIssue, display_value


REQUIRED_FIELDS = {
    "criterion_number": "Nr criteriu lipsa!",
    "age": "Varsta lipsa!",
    "sex": "Sex lipsa!",
    "breed": "Rasa lipsa!",
    "owner": "Propietar lipsa!",
    "locality": "Localitate lipsa!",
    "holding_code": "Cod exp lipsa!",
    "passport_number": "Nr pasaport lipsa!",
    "vehicle": "Masina lipsa!",
}


def load_breeds(path) -> tuple[str, ...]:
    """Return the stripped breed values from legacy ``data/rasa.txt``."""
    try:
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = path.read_text(encoding="cp1250")
    return tuple(line.strip() for line in content.splitlines() if line.strip())


def validate_records(records: Iterable[AnimalRecord], breeds: Iterable[str]) -> list[ValidationIssue]:
    """Validate the known legacy constraints without mutating an Excel workbook.

    The original program exits on its first error and colours the source cell.
    Returning all issues makes the recovered core testable; callers that need
    legacy behaviour can display only the first issue and colour its cell.
    """
    materialized = list(records)
    allowed_breeds = tuple(breed.strip() for breed in breeds if breed.strip())
    issues: list[ValidationIssue] = []

    for record in materialized:
        for field, title in REQUIRED_FIELDS.items():
            if not display_value(getattr(record, field)):
                issues.append(ValidationIssue(record.row, field, title))

        for field in ("criterion_number", "age"):
            value = display_value(getattr(record, field))
            if value:
                try:
                    int(getattr(record, field))
                except (TypeError, ValueError):
                    issues.append(ValidationIssue(record.row, field, f"{field} must be an integer."))

        sex = display_value(record.sex).upper()
        if sex and sex not in {"F", "M"}:
            issues.append(ValidationIssue(record.row, "sex", "Sex incorect"))

        breed = display_value(record.breed).upper()
        # Legacy bytecode accepts a configured breed when it occurs in the cell.
        if breed and not any(allowed.upper() in breed for allowed in allowed_breeds):
            issues.append(ValidationIssue(record.row, "breed", "Rasa incorecta"))

    by_ear_tag: dict[str, list[AnimalRecord]] = defaultdict(list)
    for record in materialized:
        ear_tag = display_value(record.ear_tag)
        if ear_tag:
            by_ear_tag[ear_tag].append(record)
    for ear_tag, duplicates in by_ear_tag.items():
        if len(duplicates) > 1:
            positions = ", ".join(str(record.criterion_number) for record in duplicates)
            for record in duplicates:
                issues.append(
                    ValidationIssue(record.row, "ear_tag", f"Crotalul {ear_tag} este duplicat la pozitia {positions}."),
                )
    return issues
