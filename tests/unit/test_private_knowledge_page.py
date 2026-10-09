"""Offline mock-only contract tests for observed Private Knowledge UI (no network)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from src import knowledge_upload_probe as probe
from tests.pages.private_knowledge_page import PrivateKnowledgePage


def element(attributes):
    node = Mock()
    node.get_attribute.side_effect = lambda name: attributes.get(name)
    return node


class PrivateKnowledgePageTests(unittest.TestCase):
    def setUp(self):
        self.page = Mock()
        self.new = Mock()
        self.new.count.return_value = 1
        self.upload = Mock()
        self.upload.count.return_value = 1

        def roles(role, **kwargs):
            if (role, kwargs.get("name"), kwargs.get("exact")) == (
                "button", "新規", True
            ):
                return self.new
            if (role, kwargs.get("name"), kwargs.get("exact")) == (
                "menuitem", "ファイルをアップロード", True
            ):
                return self.upload
            raise AssertionError("Unexpected locator request")

        self.page.get_by_role.side_effect = roles
        self.valid = element(
            {
                "type": "file",
                "accept": PrivateKnowledgePage.FILE_ACCEPT,
                "multiple": "",
                "class": "hidden",
            }
        )
        self.folder = element(
            {
                "type": "file",
                "multiple": "",
                "webkitdirectory": "true",
                "directory": "",
            }
        )
        self.inputs = Mock()
        self.inputs.count.return_value = 2
        self.inputs.nth.side_effect = lambda index: [self.valid, self.folder][index]
        self.page.locator.return_value = self.inputs
        self.knowledge = PrivateKnowledgePage(
            self.page, {"url": "https://qommons.ai/chat?temporary=ignored"}, 19000
        )

    def test_observed_my_drive_url_same_origin_and_timeout(self):
        self.knowledge.open_my_drive()
        target = "https://qommons.ai/private-knowledge/my-drive"
        self.page.goto.assert_called_once_with(target)
        self.page.wait_for_url.assert_called_once_with(target, timeout=19000)

    def test_invalid_origin_fails_before_navigation(self):
        for value in ("", "not a URL", "http://qommons.ai"):
            with self.subTest(value=value):
                self.page.reset_mock()
                bad = PrivateKnowledgePage(self.page, {"url": value})
                with self.assertRaises(ValueError):
                    bad.open_my_drive()
                self.page.goto.assert_not_called()

    def test_read_only_control_inspection_does_not_select(self):
        result = self.knowledge.inspect_controls()
        self.new.click.assert_called_once()
        self.upload.click.assert_not_called()
        self.page.expect_file_chooser.assert_not_called()
        self.page.locator.assert_called_once_with('input[type="file"]')
        self.assertFalse(result["file_selected"])
        self.assertTrue(result["upload_menuitem_observed"])
        self.assertEqual(result["file_accept"], PrivateKnowledgePage.FILE_ACCEPT)

    def test_menu_missing_or_ambiguous_stops(self):
        self.new.count.return_value = 0
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()
        self.new.click.assert_not_called()
        self.new.count.return_value = 1
        self.upload.count.return_value = 2
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()
        self.upload.click.assert_not_called()

    def test_changed_or_ambiguous_input_stops(self):
        self.valid = element({"type": "file", "accept": ".pdf", "multiple": ""})
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()

        self.valid = element(
            {"type": "file", "accept": PrivateKnowledgePage.FILE_ACCEPT}
        )  # missing multiple
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()

        self.valid = element(
            {
                "type": "file",
                "accept": PrivateKnowledgePage.FILE_ACCEPT,
                "multiple": "",
                "webkitdirectory": "",
            }
        )
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()

        self.valid = element(
            {
                "type": "file",
                "accept": PrivateKnowledgePage.FILE_ACCEPT,
                "multiple": "",
            }
        )
        self.inputs.count.return_value = 2
        self.inputs.nth.side_effect = lambda index: self.valid
        with self.assertRaises(RuntimeError):
            self.knowledge.inspect_controls()
        self.upload.click.assert_not_called()

    def test_missing_confirmation_stops_before_any_ui(self):
        with self.assertRaises(PermissionError):
            self.knowledge.select_synthetic_file(
                Path("any.md"), Path("any.txt"), confirmation=""
            )
        self.new.click.assert_not_called()
        self.page.expect_file_chooser.assert_not_called()

    def test_mismatching_synthetic_target_stops_before_ui(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            txt = src.with_suffix(".txt")
            txt.write_bytes(b"different file")
            with patch(
                "tests.pages.private_knowledge_page.validate_sample"
            ) as validate:
                with self.assertRaises(ValueError):
                    self.knowledge.select_synthetic_file(
                        src, txt, confirmation="UPLOAD"
                    )
                validate.assert_called_once()
        self.new.click.assert_not_called()

    def _fake_file_chooser(self, chooser_element):
        chooser = Mock()
        chooser.element = chooser_element
        pending = Mock()
        pending.value = chooser
        context = MagicMock()
        context.__enter__.return_value = pending
        self.page.expect_file_chooser.return_value = context
        return chooser

    def test_unexpected_folder_chooser_never_selects_file(self):
        chooser = self._fake_file_chooser(self.folder)
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            txt = src.with_suffix(".txt")
            txt.write_bytes(probe.SAMPLE_BYTES)
            with patch("tests.pages.private_knowledge_page.validate_sample"):
                with self.assertRaises(RuntimeError):
                    self.knowledge.select_synthetic_file(
                        src, txt, confirmation="UPLOAD"
                    )
        self.upload.click.assert_called_once()
        chooser.set_files.assert_not_called()

    def test_mock_only_explicit_selection_is_one_file_not_server_success(self):
        chooser = self._fake_file_chooser(self.valid)
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            txt = src.with_suffix(".txt")
            txt.write_bytes(probe.SAMPLE_BYTES)
            with patch("tests.pages.private_knowledge_page.validate_sample"):
                outcome = self.knowledge.select_synthetic_file(
                    src, txt, confirmation="UPLOAD"
                )
            chooser.set_files.assert_called_once_with(str(txt.resolve()))
        self.assertEqual(outcome, "selected_unverified")
        self.upload.click.assert_called_once()
        self.page.expect_file_chooser.assert_called_once_with(timeout=19000)


class ReadOnlyCliTests(unittest.TestCase):
    def test_new_flag_requires_inspect_mode(self):
        with self.assertRaises(SystemExit) as raised:
            probe.main(
                [
                    str(probe.SAMPLE),
                    "--synthetic",
                    "--check-observed-controls",
                ]
            )
        self.assertEqual(raised.exception.code, 2)

    def test_check_mode_does_not_call_selector_or_upload_code(self):
        with (
            patch.object(probe, "load_login_config", return_value={"synthetic": True}),
            patch.object(probe, "prepare_txt") as convert,
            patch.object(probe, "inspect_ui") as inspect,
            patch.object(probe, "write_receipt") as receipt,
        ):
            exit_code = probe.main(
                [
                    str(probe.SAMPLE),
                    "--synthetic",
                    "--inspect-ui",
                    "--check-observed-controls",
                ]
            )
            self.assertEqual(exit_code, 2)
            convert.assert_called_once_with(probe.SAMPLE)
            inspect.assert_called_once_with(
                {"synthetic": True}, check_observed_controls=True
            )
            receipt.assert_not_called()

    def test_confirm_upload_still_disabled(self):
        with (
            patch.object(probe, "load_login_config") as login,
            patch.object(probe, "prepare_txt") as convert,
            patch.object(probe, "inspect_ui") as inspect,
        ):
            self.assertEqual(
                probe.main(
                    [str(probe.SAMPLE), "--synthetic", "--confirm-upload"]
                ),
                2,
            )
            login.assert_not_called()
            convert.assert_not_called()
            inspect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
