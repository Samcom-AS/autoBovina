"""Putty integration recovered from ``deschidereConsola`` in the legacy code."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


SERVER_PROFILE = "srvvif57"


@dataclass
class RecordingPuttySession:
    """Safe test double: records the legacy launch protocol and does no I/O."""

    events: list[tuple[str, tuple[object, ...]]] = field(default_factory=list)

    def connect(self, putty_path: Path, work_post: str) -> None:
        self.events.extend(
            [
                ("start", (putty_path, "uia")),
                ("select_profile", (SERVER_PROFILE,)),
                ("click", ("Open", "1009", "Button")),
                ("typewrite", (work_post,)),
                ("press", ("enter", 1)),
                ("press", ("enter", 4)),
            ]
        )


class LivePuttySession:
    """Windows UI adapter matching the recovered console-opening function.

    It is deliberately not selected by the CLI. Calling it requires a
    separately approved test environment because it starts and controls Putty.
    """

    def connect(self, putty_path: Path, work_post: str) -> None:  # pragma: no cover - live UI integration
        try:
            from pywinauto import application
            from pywinauto.application import Application
            import pyautogui
        except ImportError as exc:
            raise RuntimeError("Install the [windows] extra for live Putty automation.") from exc

        app = Application(backend="uia").start(str(putty_path))
        process_id = application.process_from_module(module=str(putty_path))
        configuration = app.PuTTYConfiguration
        configuration.child_window(title="srvvif57", control_type="ListItem").select()
        configuration.child_window(title="Open", auto_id="1009", control_type="Button").click()
        app = Application(backend="uia").connect(process=process_id)
        pyautogui.typewrite(work_post)
        pyautogui.press("enter")
        pyautogui.press("enter", presses=4)
