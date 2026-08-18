from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "auto-bovina" / "src"))

from autobovina.config import LegacySettings, SettingsError
from autobovina.models import AnimalRecord
from autobovina.putty import SERVER_PROFILE
from autobovina.runtime import default_data_path
from autobovina.service import prepare_batch, simulate_legacy_connection, simulate_vif_workflow


def record(row: int, **changes: object) -> AnimalRecord:
    data: dict[str, object] = {
        "row": row,
        "criterion_number": 100 + row,
        "ear_tag": f"RO{row}",
        "age": 3,
        "sex": "F",
        "breed": "AB ANGUS",
        "owner": "Owner Test",
        "locality": "Localitate Test",
        "holding_code": "RO123",
        "passport_number": f"P{row}",
        "vehicle": "B 01 TEST",
    }
    data.update(changes)
    return AnimalRecord(**data)


class LegacySettingsTests(unittest.TestCase):
    def test_source_distribution_has_safe_default_templates(self) -> None:
        self.assertTrue(default_data_path("settings.txt").is_file())
        self.assertTrue(default_data_path("rasa.txt").is_file())

    def test_reads_the_four_line_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.txt"
            path.write_text("C:\\book.xls\nC:\\putty.exe\nFoaie1\nDate\n", encoding="utf-8")
            settings = LegacySettings.read(path)
        self.assertEqual(settings.receptions_sheet, "Foaie1")
        self.assertEqual(settings.automation_sheet, "Date")

    def test_rejects_an_incomplete_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.txt"
            path.write_text("one\ntwo\n", encoding="utf-8")
            with self.assertRaises(SettingsError):
                LegacySettings.read(path)

    def test_resolves_portable_relative_paths_from_the_settings_folder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.txt"
            path.write_text(".\\book.xls\n.\\putty.exe\nFoaie1\nDate\n", encoding="utf-8")
            settings = LegacySettings.read(path)
        self.assertEqual(settings.workbook_path, (path.parent / "book.xls").resolve())
        self.assertEqual(settings.putty_path, (path.parent / "putty.exe").resolve())


class BatchValidationTests(unittest.TestCase):
    BREEDS = ("AB ANGUS", "BRUNA")

    def test_accepts_a_valid_batch(self) -> None:
        self.assertTrue(prepare_batch([record(9)], self.BREEDS).valid)

    def test_reports_missing_and_invalid_values(self) -> None:
        result = prepare_batch([record(9, sex="X", owner=None, breed="UNKNOWN")], self.BREEDS)
        self.assertFalse(result.valid)
        self.assertEqual({issue.field for issue in result.issues}, {"sex", "owner", "breed"})

    def test_reports_duplicate_ear_tags(self) -> None:
        result = prepare_batch([record(9, ear_tag="RO1"), record(10, ear_tag="RO1")], self.BREEDS)
        self.assertEqual([issue.field for issue in result.issues], ["ear_tag", "ear_tag"])

    def test_rejects_a_batch_without_records(self) -> None:
        result = prepare_batch([], self.BREEDS)
        self.assertFalse(result.valid)
        self.assertEqual(result.issues[0].field, "batch")

    def test_rejects_a_decimal_string_that_the_legacy_int_conversion_rejects(self) -> None:
        result = prepare_batch([record(9, criterion_number="109.0")], self.BREEDS)
        self.assertFalse(result.valid)
        self.assertEqual(result.issues[0].field, "criterion_number")


class PuttyMockTests(unittest.TestCase):
    def test_records_the_recovered_connection_protocol(self) -> None:
        session = simulate_legacy_connection(Path("C:/vifout/Putty/putty.exe"), "p01")
        self.assertEqual(session.events[1], ("select_profile", (SERVER_PROFILE,)))
        self.assertEqual(session.events[-1], ("press", ("enter", 4)))


class VifWorkflowTests(unittest.TestCase):
    def test_single_record_reconstructs_both_work_posts_without_ui_io(self) -> None:
        workflow = simulate_vif_workflow([record(9, breed="RED HOOL X")], doctor_id=17)
        steps = workflow.steps

        self.assertEqual([step.values[0] for step in steps if step.action == "open_console"], ["p01", "p02"])
        self.assertIn(("typewrite", ("RED HOLL",)), [(step.action, step.values) for step in steps])
        self.assertEqual([step.values for step in steps if step.action == "set_workbook_cell"], [("G3", 2), ("G3", 2)])
        self.assertEqual(steps[-1].action, "save_workbook")
        self.assertNotIn("live_execute", [step.action for step in steps])

    def test_same_owner_path_uses_the_recovered_skip_sequence(self) -> None:
        workflow = simulate_vif_workflow([record(9), record(10)], doctor_id=17)
        presses = [step.values for step in workflow.steps if step.action == "press"]
        self.assertIn(("pyautogui", "enter", 4), presses)
        self.assertEqual([step.values[0] for step in workflow.steps if step.action == "open_console"], ["p01", "p02"])

    def test_owner_change_syncs_a_completed_group_before_reopening_p01(self) -> None:
        workflow = simulate_vif_workflow([record(9), record(10, owner="Other Owner")], doctor_id=17)
        self.assertEqual([step.values[0] for step in workflow.steps if step.action == "open_console"], ["p01", "p02", "p01", "p02"])
        self.assertEqual([step.values for step in workflow.steps if step.action == "set_workbook_cell"], [("G3", 111), ("G3", 3), ("G3", 3)])
