"""Offline tests for the isolated upload probe (never access QommonsAI)."""

import io
import json
import tempfile
import unittest
from pathlib import Path


from unittest.mock import Mock, patch
from contextlib import redirect_stdout

from src import knowledge_upload_probe as probe


class ProbeTests(unittest.TestCase):
    def test_preserves_source_bytes_and_idempotent_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            data = b"# Example\r\nfictional datum\r\n"
            src.write_bytes(data)
            txt, digest = probe.prepare_txt(src)
            self.assertEqual(txt.read_bytes(), data)
            self.assertEqual(src.read_bytes(), data)
            self.assertEqual(probe.prepare_txt(src), (txt, digest))

    def test_rejects_conflicting_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            src.write_text("A", encoding="utf-8")
            src.with_suffix(".txt").write_text("B", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                probe.prepare_txt(src)

    def test_rejects_invalid_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            src.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                probe.prepare_txt(src)
            src.write_bytes(b"")
            with self.assertRaises(ValueError):
                probe.prepare_txt(src)

    def test_upload_disabled_without_dom(self):
        with (
            patch.object(probe, "load_login_config") as load,
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "inspect_ui") as inspect,
        ):
            self.assertEqual(
                probe.main([str(probe.SAMPLE), "--synthetic", "--confirm-upload"]), 2
            )
            load.assert_not_called()
            export.assert_not_called()
            inspect.assert_not_called()

    def test_receipt_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            src.write_text("# Sample", encoding="utf-8")
            target, digest = probe.prepare_txt(src)
            receipt = probe.write_receipt(src, target, digest)
            result = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "selected_unverified")
            self.assertFalse(result["server_registration_verified"])
            self.assertFalse(result["search_verified"])

    def test_cli_rejects_missing_operator_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "synthetic.md"
            src.write_text("# Example", encoding="utf-8")
            with self.assertRaises(SystemExit) as result:
                probe.main([str(src)])
            self.assertEqual(result.exception.code, 2)
            self.assertFalse(src.with_suffix(".txt").exists())


class LoginInspectionTests(unittest.TestCase):
    def test_sample_is_exact_and_arbitrary_data_rejected(self):
        self.assertEqual(probe.SAMPLE.read_bytes(), probe.SAMPLE_BYTES)
        probe.validate_sample(probe.SAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "business.md"
            source.write_bytes(probe.SAMPLE_BYTES)
            with self.assertRaises(ValueError):
                probe.validate_sample(source)
            with patch.object(probe, "load_login_config") as load:
                self.assertEqual(
                    probe.main([str(source), "--synthetic", "--inspect-ui"]), 2
                )
                load.assert_not_called()
        with patch.object(Path, "read_bytes", return_value=b"modified"):
            with self.assertRaises(ValueError):
                probe.validate_sample(probe.SAMPLE)

    def test_existing_loader_called_without_overrides(self):
        config = {
            "url": "https://synthetic.invalid",
            "username": "fake",
            "password": "fake",
        }
        with patch(
            "src.env_loader.load_env", return_value=(config, {"retry_policy": 0})
        ) as load:
            self.assertIs(probe.load_login_config(), config)
            load.assert_called_once_with()
            self.assertEqual(
                config,
                {
                    "url": "https://synthetic.invalid",
                    "username": "fake",
                    "password": "fake",
                },
            )

    def test_missing_fields_and_loader_failure_do_not_fallback(self):
        for key in ("url", "username", "password"):
            for value in (None, "", " "):
                config = dict(
                    url="https://synthetic.invalid", username="fake", password="fake"
                )
                config[key] = value
                with patch("src.env_loader.load_env", return_value=(config, {})):
                    with self.assertRaises(ValueError):
                        probe.load_login_config()
        with patch(
            "src.env_loader.load_env", side_effect=ValueError("invalid profile")
        ) as load:
            with self.assertRaises(ValueError):
                probe.load_login_config()
            load.assert_called_once_with()

    def test_configuration_failure_precedes_export_and_browser(self):
        output = io.StringIO()
        with (
            patch.object(
                probe, "load_login_config", side_effect=RuntimeError("SECRET_MARKER")
            ),
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "inspect_ui") as inspect,
            redirect_stdout(output),
        ):
            self.assertEqual(
                probe.main([str(probe.SAMPLE), "--synthetic", "--inspect-ui"]), 2
            )
            export.assert_not_called()
            inspect.assert_not_called()
        self.assertNotIn("SECRET_MARKER", output.getvalue())

    def test_inspection_never_writes_selection_receipt(self):
        config = {"synthetic": True}
        with (
            patch.object(probe, "load_login_config", return_value=config),
            patch.object(probe, "prepare_txt") as export,
            patch.object(probe, "inspect_ui") as inspect,
            patch.object(probe, "write_receipt") as receipt,
        ):
            self.assertEqual(
                probe.main([str(probe.SAMPLE), "--synthetic", "--inspect-ui"]), 2
            )
            export.assert_called_once_with(probe.SAMPLE)
            inspect.assert_called_once_with(config)
            receipt.assert_not_called()

    def test_browser_login_order_timeouts_and_cleanup(self):
        config = {"browser": {"browser_timeout_ms": 60000, "page_timeout_ms": 61000}}
        for failure in (False, True):
            with self.subTest(failure=failure):
                pw = Mock()
                context = Mock()
                context.__enter__ = Mock(return_value=pw)
                context.__exit__ = Mock(return_value=False)
                browser = pw.chromium.launch.return_value
                page = browser.new_page.return_value
                login_class = Mock()
                ordered = Mock()
                ordered.attach_mock(login_class.return_value.open, "open")
                ordered.attach_mock(login_class.return_value.login, "login")
                ordered.attach_mock(page.pause, "pause")
                if failure:
                    login_class.return_value.login.side_effect = RuntimeError(
                        "SECRET_MARKER"
                    )
                with (
                    patch("playwright.sync_api.sync_playwright", return_value=context),
                    patch("tests.pages.login_page.LoginPage", login_class),
                ):
                    if failure:
                        with self.assertRaises(RuntimeError):
                            probe.inspect_ui(config)
                    else:
                        probe.inspect_ui(config)
                self.assertEqual(
                    [call[0] for call in ordered.mock_calls],
                    ["open", "login"] if failure else ["open", "login", "pause"],
                )
                pw.chromium.launch.assert_called_once_with(headless=False)
                page.set_default_timeout.assert_called_once_with(60000)
                page.set_default_navigation_timeout.assert_called_once_with(61000)
                login_class.assert_called_once_with(page, config, timeout=61000)
                browser.close.assert_called_once_with()
                page.locator.assert_not_called()
                page.goto.assert_not_called()

    def test_browser_errors_are_redacted(self):
        output = io.StringIO()
        with (
            patch.object(probe, "load_login_config", return_value={}),
            patch.object(probe, "prepare_txt"),
            patch.object(
                probe, "inspect_ui", side_effect=RuntimeError("SECRET_MARKER")
            ),
            redirect_stdout(output),
        ):
            self.assertEqual(
                probe.main([str(probe.SAMPLE), "--synthetic", "--inspect-ui"]), 2
            )
        self.assertNotIn("SECRET_MARKER", output.getvalue())


if __name__ == "__main__":
    unittest.main()
