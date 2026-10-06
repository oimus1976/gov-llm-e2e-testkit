"""Offline tests for the isolated upload probe (never access QommonsAI)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "knowledge_upload_probe.py"
spec = importlib.util.spec_from_file_location("knowledge_upload_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class FakeInput:
    def __init__(self, count):
        self._count = count
        self.selected = None

    def count(self):
        return self._count

    def set_input_files(self, name):
        self.selected = name


class FakePage:
    def __init__(self, count):
        self.input = FakeInput(count)

    def locator(self, selector):
        assert selector == "input[type='file']"
        return self.input


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

    def test_requires_unique_file_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "synthetic.txt"
            for count in (0, 2):
                with self.assertRaises(RuntimeError):
                    probe.select_upload_input(FakePage(count), target)
            page = FakePage(1)
            probe.select_upload_input(page, target)
            self.assertEqual(page.input.selected, str(target))

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


if __name__ == "__main__":
    unittest.main()
