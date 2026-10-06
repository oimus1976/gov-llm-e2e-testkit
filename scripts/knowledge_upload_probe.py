"""Synthetic-only Private Knowledge upload UI probe.

No server-side registration or indexing success is inferred from file selection.
This does not modify existing E2E profiles or F8/F9 behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def prepare_txt(source: Path) -> tuple[Path, str]:
    """Keep Markdown as the source; never overwrite divergent .txt bytes."""
    if source.suffix.lower() != ".md" or not source.is_file():
        raise ValueError("An existing .md file is required")
    raw = source.read_bytes()
    raw.decode("utf-8")  # reject invalid UTF-8, retain exact bytes and line endings
    if not raw:
        raise ValueError("Empty input is not valid")
    target = source.with_suffix(".txt")
    if target.exists():
        if target.read_bytes() != raw:
            raise FileExistsError(f"Different existing export; refusing overwrite: {target}")
    else:
        # Exclusive creation prevents silent replacement.
        with target.open("xb") as stream:
            stream.write(raw)
    return target, hashlib.sha256(raw).hexdigest()


def select_upload_input(page, target: Path) -> None:
    """Only operate on an unambiguous native input in the operator-opened form."""
    inputs = page.locator("input[type='file']")
    count = inputs.count()
    if count != 1:
        raise RuntimeError(f"Expected one file input, observed {count}; inspect live DOM")
    inputs.set_input_files(str(target))


def write_receipt(source: Path, target: Path, digest: str) -> Path:
    receipt = source.parent / (
        source.stem + ".selection-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json"
    )
    data = {
        "source_name": source.name,
        "upload_name": target.name,
        "sha256": digest,
        "status": "selected_unverified",
        "server_registration_verified": False,
        "search_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One synthetic Private Knowledge upload selection")
    parser.add_argument("markdown", type=Path, help="Approved synthetic test file (.md)")
    parser.add_argument("--synthetic", action="store_true", help="Assert input is synthetic")
    parser.add_argument("--confirm-upload", action="store_true", help="Explicitly enable UI file selection")
    args = parser.parse_args(argv)
    if not (args.synthetic and args.confirm_upload):
        parser.error("MVP requires --synthetic and --confirm-upload; real data is prohibited")

    source = args.markdown.expanduser().resolve()
    target, digest = prepare_txt(source)
    print(f"Markdown retained: {source}")
    print(f"Prepared text copy: {target} SHA256={digest}")
    print("Visible browser will open. Log in manually and navigate to the intended")
    print("Private Knowledge upload form. Do NOT use non-synthetic documents.")

    # Delayed import allows offline unit tests without a browser installation.
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto("https://qommons.ai", wait_until="domcontentloaded")
            input("When the intended upload form is visible, press Enter to inspect it: ")
            count = page.locator("input[type='file']").count()
            if count != 1:
                raise RuntimeError(f"Found {count} file inputs; no upload was attempted")
            answer = input(f"Select {target.name} in this form? Type UPLOAD to confirm: ")
            if answer != "UPLOAD":
                print("Cancelled. No file selected.")
                return 1
            select_upload_input(page, target)
            receipt = write_receipt(source, target, digest)
            print(f"File selected; server/index/search state UNVERIFIED. Receipt: {receipt}")
            input("Inspect the upload UI manually, then press Enter to close browser: ")
        finally:
            browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
