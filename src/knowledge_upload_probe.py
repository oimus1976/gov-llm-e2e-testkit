"""Synthetic-only login/control inspection probe; live upload stays disabled."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "knowledge_upload" / "synthetic.md"
SAMPLE_BYTES = b"# Synthetic Private Knowledge probe\n\nFictional test only. The sample code is SYNTHETIC-KNOWLEDGE-0001.\n"


def prepare_txt(source: Path) -> tuple[Path, str]:
    """Retain exact UTF-8 Markdown bytes and refuse divergent exports."""
    if source.suffix.lower() != ".md" or not source.is_file():
        raise ValueError("An existing .md file is required")
    raw = source.read_bytes()
    raw.decode("utf-8")
    if not raw:
        raise ValueError("Empty input is not valid")
    target = source.with_suffix(".txt")
    if target.exists():
        if target.read_bytes() != raw:
            raise FileExistsError("Different existing export; refusing overwrite")
    else:
        with target.open("xb") as stream:
            stream.write(raw)
    return target, hashlib.sha256(raw).hexdigest()


def validate_sample(source: Path) -> None:
    """A synthetic assertion alone must not enable arbitrary business data."""
    if source.resolve() != SAMPLE.resolve() or source.read_bytes() != SAMPLE_BYTES:
        raise ValueError("Only the unchanged bundled synthetic sample is permitted")


def write_receipt(source: Path, target: Path, digest: str) -> Path:
    """For future observed file selection; not used by inspection mode."""
    receipt = source.parent / (
        source.stem
        + ".selection-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        + ".json"
    )
    data = {
        "source_name": source.name,
        "upload_name": target.name,
        "sha256": digest,
        "status": "selected_unverified",
        "http_acceptance_verified": False,
        "server_registration_verified": False,
        "search_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return receipt


def load_login_config() -> dict:
    from src.env_loader import load_env

    config, _options = load_env()
    for key in ("url", "username", "password"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Required login configuration is missing: {key}")
    return config


def inspect_ui(config: dict, *, check_observed_controls: bool = False) -> None:
    from playwright.sync_api import sync_playwright
    from tests.pages.login_page import LoginPage

    settings = config.get("browser", {})
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.set_default_timeout(settings["browser_timeout_ms"])
            page.set_default_navigation_timeout(settings["page_timeout_ms"])
            login = LoginPage(page, config, timeout=settings["page_timeout_ms"])
            login.open()
            login.login()
            if check_observed_controls:
                from tests.pages.private_knowledge_page import PrivateKnowledgePage

                knowledge = PrivateKnowledgePage(
                    page, config, timeout=settings["page_timeout_ms"]
                )
                knowledge.open_my_drive()
                knowledge.inspect_controls()
                print(
                    "Read-only check PASS: My Drive, New menu, upload item and file input."
                )
                print("No file was selected; network acceptance remains unverified.")
            else:
                print(
                    "Login completed. Inspect registration navigation in Playwright Inspector."
                )
            print(
                "Do not upload, delete, replace, or send chats during this observation."
            )
            page.pause()
        finally:
            browser.close()


def upload_synthetic_one(
    config: dict,
    source: Path,
    target: Path,
    digest: str,
    *,
    operator_input=None,
) -> bool:
    """Future *separately authorized* live test; never called by inspection mode.

    A selected file can upload immediately. A manual duplicate check is required
    because file-list DOM and provider replacement semantics are unobserved.
    """
    from playwright.sync_api import sync_playwright
    from tests.pages.login_page import LoginPage
    from tests.pages.private_knowledge_page import PrivateKnowledgePage

    settings = config.get("browser", {})
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.set_default_timeout(settings["browser_timeout_ms"])
            page.set_default_navigation_timeout(settings["page_timeout_ms"])
            login = LoginPage(page, config, timeout=settings["page_timeout_ms"])
            login.open()
            login.login()
            knowledge = PrivateKnowledgePage(
                page, config, timeout=settings["page_timeout_ms"]
            )
            knowledge.open_my_drive()
            print(
                "PRE-SELECTION CHECKPOINT: inspect My Drive for an existing synthetic.txt."
            )
            print(
                "If there is any duplicate or the list is incomplete, do not proceed."
            )
            print(
                "Resume Inspector after checking; file selection may trigger immediate upload."
            )
            page.pause()
            read_input = operator_input if operator_input is not None else input
            try:
                phrase = read_input(
                    "Confirm NO existing synthetic.txt, and approve one possible "
                    "immediate upload by typing exactly UPLOAD synthetic.txt: "
                )
            except EOFError:
                phrase = ""
            if phrase != "UPLOAD synthetic.txt":
                print("Stopped before file selection; no selection receipt created.")
                return False

            # The PageObject revalidates the exact sample and export immediately
            # before clicking. Never retry automatically if this step fails.
            outcome = knowledge.select_synthetic_file(
                source, target, confirmation="UPLOAD"
            )
            receipt = write_receipt(source, target, digest)
            print(f"File chooser result: {outcome}.")
            print(f"Local receipt: {receipt.name}.")
            print(
                "HTTP acceptance, My Drive registration and search remain unverified."
            )
            print("Inspect the page without deleting, replacing or retrying.")
            page.pause()
            return True
        finally:
            browser.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synthetic Private Knowledge UI inspection"
    )
    parser.add_argument(
        "markdown", type=Path, help="Unchanged data/knowledge_upload/synthetic.md"
    )
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--confirm-upload", action="store_true")
    parser.add_argument(
        "--execute-synthetic-upload",
        action="store_true",
        help="Future human-authorized one-file synthetic selection only",
    )
    parser.add_argument(
        "--inspect-ui",
        action="store_true",
        help="Automatic login and Inspector; no file selection",
    )
    parser.add_argument(
        "--check-observed-controls",
        action="store_true",
        help="Read-only My Drive/menu/file-input check; requires --inspect-ui",
    )
    args = parser.parse_args(argv)
    if args.execute_synthetic_upload and (
        not args.confirm_upload or args.inspect_ui or args.check_observed_controls
    ):
        parser.error(
            "--execute-synthetic-upload requires --confirm-upload and cannot "
            "be combined with inspection controls"
        )
    if args.check_observed_controls and not args.inspect_ui:
        parser.error("--check-observed-controls requires --inspect-ui")
    if args.confirm_upload and args.inspect_ui:
        parser.error("Do not combine --confirm-upload with inspection mode")
    if not args.synthetic or (not args.inspect_ui and not args.confirm_upload):
        parser.error("Requires --synthetic and either --inspect-ui or --confirm-upload")
    try:
        source = args.markdown.expanduser().resolve()
        validate_sample(source)
    except (OSError, ValueError):
        print(
            "Stopped: only the unchanged bundled synthetic Markdown sample is permitted."
        )
        return 2
    if not args.inspect_ui and not args.execute_synthetic_upload:
        print(
            "Stopped: --confirm-upload alone never selects or uploads a file."
        )
        print(
            "Use --synthetic --inspect-ui --check-observed-controls for read-only checks."
        )
        return 2
    try:
        config = load_login_config()
    except Exception:
        print(
            "Stopped: existing env.yaml/.env profile or login dependencies are unavailable."
        )
        print(
            "Check existing configuration locally; no fallback or settings changes were made."
        )
        return 2
    try:
        prepared = prepare_txt(source)
        if args.execute_synthetic_upload:
            target, digest = prepared
            upload_synthetic_one(config, source, target, digest)
        elif args.check_observed_controls:
            inspect_ui(config, check_observed_controls=True)
        else:
            inspect_ui(config)
    except Exception:
        # Playwright fill errors can include credentials; never print the exception.
        print(
            "Stopped: export, browser, login, inspection or selection failed."
        )
        print(
            "If file selection was attempted, server state is unknown. Do not retry."
        )
        return 2
    print(
        "Session ended. HTTP acceptance, list registration and search remain unverified."
    )
    return 2
