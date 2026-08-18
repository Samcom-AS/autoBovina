"""Compatibility-oriented recovery of the legacy autoBovina workflow."""

from .config import LegacySettings
from .models import AnimalRecord, ValidationIssue
from .validation import validate_records
from .workflow import VifStep, VifWorkflow, build_vif_workflow

__all__ = [
    "AnimalRecord",
    "LegacySettings",
    "ValidationIssue",
    "VifStep",
    "VifWorkflow",
    "build_vif_workflow",
    "validate_records",
]
