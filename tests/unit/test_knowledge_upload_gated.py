"""Mock-only tests for the future one-file live gate. Never contact QommonsAI."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from src import knowledge_upload_probe as probe


class SyntheticUploadCliContractTests(unittest.TestCase):
    def test_incomplete_flags_stop_before_any_settings_or_browser(self):
        invalid = [
            ["--synthetic", "--execute-synthetic-upload"],
            ["--execute-synthetic-upload", "--confirm-upload"],
            [
                "--synthetic",
                "--execute-synthetic-upload",
                "--confirm-upload",
                "--inspect-ui",
            ],
            [
                "--synthetic",
                "--execute-synthetic-upload",
                "--confirm-upload",
                "--check-observed-controls",
            ],
        ]
        with (
            patch.object(probe, "load_login_config") as login,
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "upload_synthetic_one") as upload,
        ):
            for flags in invalid:
                with self.subTest(flags=flags), self.assertRaises(SystemExit) as error:
                    probe.main([str(probe.SAMPLE), *flags])
                self.assertEqual(error.exception.code, 2)
            login.assert_not_called()
            export.assert_not_called()
            upload.assert_not_called()

    def test_confirm_upload_alone_still_stops_before_browser(self):
        with (
            patch.object(probe, "load_login_config") as login,
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "upload_synthetic_one") as upload,
        ):
            self.assertEqual(
                probe.main([str(probe.SAMPLE), "--synthetic", "--confirm-upload"]),
                2,
            )
            login.assert_not_called()
            export.assert_not_called()
            upload.assert_not_called()

    def test_new_explicit_flags_route_to_future_handler_only(self):
        config = {"url": "https://synthetic.invalid"}
        target = probe.SAMPLE.with_suffix(".txt")
        arguments = [
            str(probe.SAMPLE),
            "--synthetic",
            "--confirm-upload",
            "--execute-synthetic-upload",
        ]
        with (
            patch.object(probe, "load_login_config", return_value=config),
            patch.object(probe, "prepare_txt", return_value=(target, "abc")) as export,
            patch.object(probe, "upload_synthetic_one", return_value=True) as upload,
            patch.object(probe, "inspect_ui") as inspect,
        ):
            self.assertEqual(probe.main(arguments), 2)
            export.assert_called_once_with(probe.SAMPLE)
            upload.assert_called_once_with(config, probe.SAMPLE, target, "abc")
            inspect.assert_not_called()

    def test_bad_sample_stops_even_with_all_execution_flags(self):
        with (
            patch.object(probe, "load_login_config") as login,
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "upload_synthetic_one") as upload,
            patch.object(probe, "validate_sample", side_effect=ValueError("not sample")),
        ):
            self.assertEqual(
                probe.main([
                    str(probe.SAMPLE), "--synthetic", "--confirm-upload",
                    "--execute-synthetic-upload",
                ]),
                2,
            )
            login.assert_not_called()
            export.assert_not_called()
            upload.assert_not_called()

    def test_secrets_in_browser_errors_are_redacted(self):
        output = io.StringIO()
        with (
            patch.object(probe, "load_login_config", return_value={}),
            patch.object(
                probe, "prepare_txt", return_value=(Path("synthetic.txt"), "digest")
            ),
            patch.object(
                probe, "upload_synthetic_one",
                side_effect=RuntimeError("SECRET_MARKER"),
            ),
            redirect_stdout(output),
        ):
            self.assertEqual(
                probe.main([
                    str(probe.SAMPLE), "--synthetic", "--confirm-upload",
                    "--execute-synthetic-upload",
                ]),
                2,
            )
        self.assertNotIn("SECRET_MARKER", output.getvalue())


class LivePathWithFakePlaywrightTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "browser": {
                "browser_timeout_ms": 15000,
                "page_timeout_ms": 20000,
            }
        }
        self.source = probe.SAMPLE
        self.target = probe.SAMPLE.with_suffix(".txt")
        self.digest = "local-test-digest"

        self.playwright = Mock()
        self.session = Mock()
        self.session.__enter__ = Mock(return_value=self.playwright)
        self.session.__exit__ = Mock(return_value=False)
        self.browser = self.playwright.chromium.launch.return_value
        self.page = self.browser.new_page.return_value
        self.login_class = Mock()
        self.knowledge_class = Mock()

        self.receipt_mock = Mock(return_value=Path("receipt.json"))
        self.patchers = [
            patch("playwright.sync_api.sync_playwright", return_value=self.session),
            patch("tests.pages.login_page.LoginPage", self.login_class),
            patch(
                "tests.pages.private_knowledge_page.PrivateKnowledgePage",
                self.knowledge_class,
            ),
            patch.object(probe, "write_receipt", self.receipt_mock),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_fake_live(self, answer):
        return probe.upload_synthetic_one(
            self.config, self.source, self.target, self.digest,
            operator_input=answer,
        )

    def test_cancel_never_calls_file_selection_or_receipt(self):
        for answer in ("", "UPLOAD", "upload synthetic.txt", "NO_DUPLICATE"):
            with self.subTest(answer=answer):
                self.assertFalse(self.run_fake_live(lambda prompt: answer))
                self.knowledge_class.return_value.select_synthetic_file.assert_not_called()
                self.receipt_mock.assert_not_called()
                self.page.expect_file_chooser.assert_not_called()
                self.browser.close.assert_called()
                self.knowledge_class.return_value.select_synthetic_file.reset_mock()

    def test_eof_cancels_before_menu_and_receipt(self):
        prompt = Mock(side_effect=EOFError)
        self.assertFalse(self.run_fake_live(prompt))
        self.knowledge_class.return_value.select_synthetic_file.assert_not_called()
        self.receipt_mock.assert_not_called()
        self.browser.close.assert_called_once()

    def test_exact_phrase_calls_pageobject_once_and_records_unverified(self):
        self.knowledge_class.return_value.select_synthetic_file.return_value = (
            "selected_unverified"
        )
        with patch.object(probe, "write_receipt", return_value=Path("receipt.json")) as receipt:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertTrue(
                    self.run_fake_live(lambda prompt: "UPLOAD synthetic.txt")
                )
            receipt.assert_called_once_with(
                self.source, self.target, self.digest
            )
        self.knowledge_class.return_value.select_synthetic_file.assert_called_once_with(
            self.source, self.target, confirmation="UPLOAD"
        )
        self.assertEqual(self.page.pause.call_count, 2)
        self.login_class.return_value.open.assert_called_once()
        self.login_class.return_value.login.assert_called_once()
        self.knowledge_class.return_value.open_my_drive.assert_called_once()
        self.browser.close.assert_called_once()
        self.assertIn("selected_unverified", output.getvalue())
        self.assertIn("remain unverified", output.getvalue())

    def test_ui_failure_is_never_automatically_retried(self):
        self.knowledge_class.return_value.select_synthetic_file.side_effect = (
            RuntimeError("ambiguous FileChooser")
        )
        with patch.object(probe, "write_receipt") as receipt:
            with self.assertRaises(RuntimeError):
                self.run_fake_live(lambda prompt: "UPLOAD synthetic.txt")
            receipt.assert_not_called()
        self.knowledge_class.return_value.select_synthetic_file.assert_called_once()
        self.browser.close.assert_called_once()

    def test_browser_failure_never_prompts_or_selects(self):
        self.login_class.return_value.login.side_effect = RuntimeError("login failed")
        user_prompt = Mock()
        with self.assertRaises(RuntimeError):
            self.run_fake_live(user_prompt)
        user_prompt.assert_not_called()
        self.knowledge_class.return_value.select_synthetic_file.assert_not_called()
        self.browser.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
