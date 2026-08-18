"""Pure, mock-first reconstruction of the legacy VIF keyboard workflow.

The original ``main.py`` interleaves Excel, Putty, and desktop calls at module
scope.  This module keeps the recovered ordering, but expresses it as data so
it can be reviewed and regression-tested without opening Putty or sending
keystrokes to VIF.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import AnimalRecord


VIF_UNIT_CODE = "10301"
VIF_DOCUMENT_ISSUER = "UE"
VIF_COUNTRY_CODE = "RO"


@dataclass(frozen=True)
class VifStep:
    """One recovered UI action, recorded without performing any I/O."""

    action: str
    values: tuple[object, ...] = ()


@dataclass(frozen=True)
class VifWorkflow:
    """The complete action transcript that would have been sent to VIF."""

    steps: tuple[VifStep, ...]


class WorkflowInputError(ValueError):
    """Raised when a record cannot satisfy the source program's conversions."""


class _WorkflowBuilder:
    def __init__(self, doctor_id: int) -> None:
        self.doctor_id = doctor_id
        self.steps: list[VifStep] = []

    def add(self, action: str, *values: object) -> None:
        self.steps.append(VifStep(action, values))

    def press(self, key: str, presses: int = 1, *, driver: str = "pyautogui") -> None:
        self.add("press", driver, key, presses)

    def typewrite(self, value: object) -> None:
        self.add("typewrite", str(value))

    def sleep(self, seconds: float) -> None:
        self.add("sleep", seconds)

    def set_pydirectinput_pause(self, seconds: float) -> None:
        self.add("set_pydirectinput_pause", seconds)

    def preflight(self) -> None:
        """Record source lines 73-74 and 292-299 without inspecting the OS."""
        self.add("set_failsafe", "pyautogui", False)
        self.add("set_failsafe", "pydirectinput", False)
        self.add("select_workbook_cell", "E1")
        self.add("turn_capslock_off_if_on")

    def open_console(self, work_post: str) -> None:
        # This represents the complete deschidereConsola(work_post) call.  Its
        # own Putty launch sequence remains independently covered in putty.py.
        self.add("open_console", work_post)

    def start_reception(self) -> None:
        self.open_console("p01")
        self.press("r")
        self.press("e")
        self.press("enter", 2)

    def close_reception_task(self, *, settle_seconds: float | None) -> None:
        self.press("f4")
        self.press("d")
        if settle_seconds is not None:
            self.sleep(settle_seconds)

    def click_vif_close_and_confirm(self) -> None:
        # The legacy window title is locale dependent: Close / Închidere.
        self.add("click_vif_close")
        self.press("enter")

    def set_automation_counter(self, value: int) -> None:
        self.add("set_workbook_cell", "G3", value)

    def save_workbook(self) -> None:
        self.add("save_workbook")

    def write_full_reception(self, record: AnimalRecord, *, settle_seconds: float) -> None:
        """Recover source lines 322-364 / 371-427 / 479-535 exactly."""
        self.press("f3")
        self.press("enter")
        self.typewrite("0")
        self.press("enter")
        self.typewrite(record.vehicle)
        self.press("enter")
        self.typewrite(self.doctor_id)
        self.press("enter")
        self.press("f2")
        self.typewrite(VIF_UNIT_CODE)
        self.press("enter")
        self.typewrite(record.ear_tag)
        self.press("enter")
        self.press("enter")
        self.typewrite(VIF_DOCUMENT_ISSUER)
        self.press("enter")
        self.typewrite(_legacy_breed(record.breed))
        self.press("enter")
        self.typewrite(record.sex)
        self.press("enter")
        self.typewrite(_legacy_int(record.age, "age"))
        self.press("enter")
        self.press("enter")
        self.typewrite(record.owner)
        self.press("enter")
        self.typewrite(record.owner)
        self.press("enter")
        self.typewrite(record.holding_code)
        self.press("enter")
        self.typewrite(record.locality)
        self.press("enter")
        self.typewrite(_legacy_int(record.criterion_number, "criterion_number"))
        self.press("enter")
        self.typewrite(VIF_COUNTRY_CODE)
        self.press("enter")
        self.press("f2")
        self.press("f2")
        self.sleep(settle_seconds)

    def write_same_owner_reception(self, record: AnimalRecord) -> None:
        """Recover source lines 541-580 (the no-owner-change branch)."""
        self.press("enter")
        self.typewrite(record.ear_tag)
        self.sleep(1)
        self.press("enter")
        self.press("enter")
        self.typewrite(VIF_DOCUMENT_ISSUER)
        self.press("enter")
        self.typewrite(record.passport_number)
        self.press("enter")
        self.typewrite(_legacy_breed(record.breed))
        self.press("enter")
        self.typewrite(record.sex)
        self.press("enter")
        self.typewrite(_legacy_int(record.age, "age"))
        self.press("enter")
        # The original skips the owner-related entries with four Enters.
        self.press("enter", 4)
        self.typewrite(_legacy_int(record.criterion_number, "criterion_number"))
        self.press("enter")
        self.typewrite(VIF_COUNTRY_CODE)
        self.press("enter")
        self.press("f2")
        self.press("f2")
        self.sleep(3)

    def sync_ear_tags(self, ear_tags: Iterable[object], *, directinput_pause: float) -> None:
        """Recover the p02 import sequence from source lines 448-466."""
        self.set_pydirectinput_pause(directinput_pause)
        # The source computes ``sorted(...)`` immediately before each import,
        # but proceeds with the original list. Preserve that observable quirk.
        self.add("sort_ear_tags_unused")
        self.open_console("p02")
        self.press("b")
        self.press("e")
        self.sleep(1)
        for ear_tag in ear_tags:
            self.add("key_down", "ctrl")
            self.press("o")
            self.add("key_up", "ctrl")
            self.typewrite(VIF_UNIT_CODE)
            self.press("enter")
            self.press("f2")
            self.sleep(2)
            self.press("enter")
            self.typewrite(ear_tag)
            self.press("enter", driver="pydirectinput")
            self.press("f2", driver="pydirectinput")
            self.sleep(2.5)


def build_vif_workflow(records: Iterable[AnimalRecord], doctor_id: object) -> VifWorkflow:
    """Return the recovered VIF workflow without opening Putty or Excel.

    ``records`` must already have passed validation.  Like the executable, the
    workflow groups consecutive rows by owner.  It synchronizes each completed
    owner group on post ``p02`` before starting the next owner group on ``p01``.
    """
    materialized = tuple(records)
    if not materialized:
        return VifWorkflow(())

    builder = _WorkflowBuilder(_legacy_int(doctor_id, "doctor_id"))
    counter_after_all_records = len(materialized) + 1  # legacy: lastCell - 7

    builder.preflight()
    builder.start_reception()
    if len(materialized) == 1:
        only_record = materialized[0]
        builder.write_full_reception(only_record, settle_seconds=1)
        builder.close_reception_task(settle_seconds=None)
        builder.set_automation_counter(counter_after_all_records)
        builder.click_vif_close_and_confirm()
        builder.sync_ear_tags((only_record.ear_tag,), directinput_pause=0.02)
        builder.click_vif_close_and_confirm()
        builder.set_automation_counter(counter_after_all_records)
        builder.save_workbook()
        return VifWorkflow(tuple(builder.steps))

    pending_ear_tags: list[object] = []
    first_record = materialized[0]
    builder.write_full_reception(first_record, settle_seconds=3)
    pending_ear_tags.append(first_record.ear_tag)
    previous_owner = first_record.owner

    for record in materialized[1:]:
        if record.owner != previous_owner:
            builder.close_reception_task(settle_seconds=2)
            builder.click_vif_close_and_confirm()
            # Source line 440 writes the new group's first criterion + 1.
            builder.set_automation_counter(_legacy_int(record.criterion_number, "criterion_number") + 1)
            builder.sync_ear_tags(pending_ear_tags, directinput_pause=0.03)
            pending_ear_tags.clear()
            builder.click_vif_close_and_confirm()
            builder.start_reception()
            builder.write_full_reception(record, settle_seconds=3)
        else:
            builder.write_same_owner_reception(record)
        previous_owner = record.owner
        pending_ear_tags.append(record.ear_tag)

    builder.close_reception_task(settle_seconds=3)
    builder.set_automation_counter(counter_after_all_records)
    builder.click_vif_close_and_confirm()
    builder.sync_ear_tags(pending_ear_tags, directinput_pause=0.02)
    builder.click_vif_close_and_confirm()
    builder.set_automation_counter(counter_after_all_records)
    builder.save_workbook()
    return VifWorkflow(tuple(builder.steps))


def _legacy_breed(value: object) -> str:
    """Replicate the source's one special spelling correction, including case."""
    breed = str(value).strip(" ")
    if "RED HOOL" in breed:
        return "RED HOLL"
    return breed


def _legacy_int(value: object, field: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise WorkflowInputError(f"{field} must support the legacy int() conversion.") from exc
