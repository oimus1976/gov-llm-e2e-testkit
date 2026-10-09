"""Observed QommonsAI Private Knowledge My Drive controls (Issue #2).

DOM-derived locators only. Live file selection is not connected to the CLI.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from src.knowledge_upload_probe import SAMPLE_BYTES, validate_sample

from .base_page import BasePage


class PrivateKnowledgePage(BasePage):
    MY_DRIVE_PATH = "/private-knowledge/my-drive"
    FILE_ACCEPT = ".txt,.pdf,.docx,.html,.csv,.pptx,.xlsx,.md,.mp3,.wav,.png,.jpg,.jpeg"

    @staticmethod
    def _unique(locator, what: str):
        if locator.count() != 1:
            raise RuntimeError(f"Expected one observed {what}; stopping")
        return locator

    def open_my_drive(self) -> None:
        """Visit the operator-observed My Drive path after LoginPage succeeded."""
        base = urlsplit(self.config["url"])
        if base.scheme != "https" or not base.netloc:
            raise ValueError("Expected configured HTTPS origin; stopping")
        url = urlunsplit((base.scheme, base.netloc, self.MY_DRIVE_PATH, "", ""))
        self.page.goto(url)
        self.page.wait_for_url(url, timeout=self.timeout)

    def _new_button(self):
        return self._unique(
            self.page.get_by_role("button", name="新規", exact=True), "New button"
        )

    def _upload_item(self):
        return self._unique(
            self.page.get_by_role(
                "menuitem", name="ファイルをアップロード", exact=True
            ),
            "upload menu item",
        )

    def _open_upload_menu(self):
        self._new_button().click()
        return self._upload_item()

    @classmethod
    def _is_observed_file_input(cls, element) -> bool:
        return (
            element.get_attribute("type") == "file"
            and element.get_attribute("accept") == cls.FILE_ACCEPT
            and element.get_attribute("multiple") is not None
            and element.get_attribute("webkitdirectory") is None
            and element.get_attribute("directory") is None
        )

    def _observed_file_input(self):
        """Differentiate file upload from the observed folder-selection input."""
        inputs = self.page.locator('input[type="file"]')
        matches = [
            item
            for index in range(inputs.count())
            if self._is_observed_file_input(item := inputs.nth(index))
        ]
        if len(matches) != 1:
            raise RuntimeError("Observed file input is missing or ambiguous; stopping")
        return matches[0]

    def inspect_controls(self) -> dict:
        """Read-only check; neither upload menu click nor file selection occurs."""
        self._open_upload_menu()
        self._observed_file_input()
        return {
            "my_drive_path": self.MY_DRIVE_PATH,
            "upload_menuitem_observed": True,
            "file_accept": self.FILE_ACCEPT,
            "multiple": True,
            "file_selected": False,
        }

    def select_synthetic_file(
        self, markdown: Path, exported_txt: Path, *, confirmation: str
    ) -> str:
        """Future opt-in only; NOT wired to CLI. Selection may cause instant upload."""
        if confirmation != "UPLOAD":
            raise PermissionError("Explicit UPLOAD confirmation required")

        markdown = Path(markdown).resolve()
        exported_txt = Path(exported_txt).resolve()
        validate_sample(markdown)
        if (
            exported_txt != markdown.with_suffix(".txt")
            or not exported_txt.is_file()
            or exported_txt.read_bytes() != SAMPLE_BYTES
        ):
            raise ValueError("Only the byte-identical synthetic .txt export is allowed")

        item = self._open_upload_menu()
        self._observed_file_input()
        with self.page.expect_file_chooser(timeout=self.timeout) as pending:
            item.click()
        chooser = pending.value
        if not self._is_observed_file_input(chooser.element):
            raise RuntimeError("File chooser points to an unexpected input; stopping")
        chooser.set_files(str(exported_txt))
        return "selected_unverified"
