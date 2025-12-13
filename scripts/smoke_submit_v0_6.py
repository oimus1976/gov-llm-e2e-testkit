# scripts/smoke_submit_v0_6.py
#
# Smoke: ChatPage.submit v0.6
# - sync Playwright only (NO async)
# - reuse (copy) stable template steps: login -> chat selection
# - call ChatPage.submit() once and verify SubmitReceipt is returned
# - NO completion semantics, NO probe, NO REST/GraphQL access here

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage


def main() -> int:
    # ---------------------------
    # Setup output dir
    # ---------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/smoke_submit_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)

    # ---------------------------
    # Playwright start (sync)
    # ---------------------------
    playwright = sync_playwright().start()
    browser = None
    context = None

    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---------------------------
        # env load
        # ---------------------------
        config, _ = load_env()

        # ---------------------------
        # Login (PageObject only)
        # ---------------------------
        login = LoginPage(page, config)
        try:
            login.open()
            login.login(evidence_dir=outdir)
            print("[smoke] login OK")
        except Exception as e:
            raise RuntimeError(f"[smoke] LOGIN FAILED: {e}")

        # ---------------------------
        # Chat selection (PageObject only)
        # ---------------------------
        selector = ChatSelectPage(page, config)
        try:
            selector.open_ai("プライベートナレッジ", evidence_dir=outdir)
            print("[smoke] chat selection OK")
        except Exception as e:
            raise RuntimeError(f"[smoke] CHAT SELECT FAILED: {e}")

        # ---------------------------
        # Submit (v0.6) — ONLY ONE CALL
        # ---------------------------
        chat = ChatPage(page, config)
        try:
            receipt = chat.submit("SMOKE submit v0.6", evidence_dir=outdir)
        except Exception as e:
            raise RuntimeError(f"[smoke] SUBMIT FAILED: {e}")

        # ---------------------------
        # Verify: SubmitReceipt returned (minimal)
        # ---------------------------
        print("[smoke] submit returned SubmitReceipt")
        print(f"  submit_id: {receipt.submit_id}")
        print(f"  sent_at  : {receipt.sent_at}")
        print(f"  ui_ack   : {receipt.ui_ack}")
        print(f"  diag_keys: {list(receipt.diagnostics.keys())}")

        if not receipt.submit_id:
            raise RuntimeError("[smoke] submit_id is empty (unexpected)")
        if receipt.ui_ack is not True:
            raise RuntimeError("[smoke] ui_ack is not True (unexpected)")
        if receipt.sent_at is None:
            raise RuntimeError("[smoke] sent_at is None (unexpected)")

        print(f"[smoke] OK. evidence_dir={outdir}")
        return 0

    finally:
        # Best-effort cleanup (no throws)
        try:
            if context is not None:
                context.close()
        except Exception:
            pass
        try:
            if browser is not None:
                browser.close()
        except Exception:
            pass
        try:
            playwright.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
