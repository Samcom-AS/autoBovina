"""Compatibility service that validates a reception batch before automation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import AnimalRecord, ValidationIssue
from .putty import RecordingPuttySession
from .validation import validate_records
from .workflow import VifWorkflow, build_vif_workflow


@dataclass(frozen=True)
class BatchResult:
    records: tuple[AnimalRecord, ...]
    issues: tuple[ValidationIssue, ...]

    @property
    def valid(self) -> bool:
        return not self.issues


def prepare_batch(records: Iterable[AnimalRecord], breeds: Iterable[str]) -> BatchResult:
    materialized = tuple(records)
    issues = list(validate_records(materialized, breeds))
    if not materialized:
        issues.append(ValidationIssue(0, "batch", "Nu exista animale de prelucrat."))
    return BatchResult(materialized, tuple(issues))


def simulate_legacy_connection(putty_path, work_post: str = "p01") -> RecordingPuttySession:
    """Return the exact recovered connection transcript without starting Putty."""
    session = RecordingPuttySession()
    session.connect(putty_path, work_post)
    return session


def simulate_vif_workflow(records: Iterable[AnimalRecord], doctor_id: object) -> VifWorkflow:
    """Build the complete VIF mock transcript; it performs no desktop I/O."""
    return build_vif_workflow(records, doctor_id)
