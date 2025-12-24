# ---------------------------------------------------------
# Smoke Test v0.4 (Sync Playwright)
# gov-llm-e2e-testkit
# ---------------------------------------------------------

import pytest
from datetime import datetime, timezone, timedelta

from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

from scripts.probe_v0_2 import run_graphql_probe
from src.log_writer import LogContext, create_case_log


# JST タイムスタンプ（ログ用）
JST = timezone(timedelta(hours=9))


@pytest.mark.smoke
def test_smoke_llm(page, env_config, case_dirs):
    """
    Smoke Test v0.4

    Guarantees:
    - Login succeeds
    - Chat page can be opened
    - UI submit succeeds (submit v0.6)
    - Probe observes correlation_state (submit–probe v0.2)

    Non-goals:
    - Semantic answer correctness
    - ask() API
    """

    config, _options = env_config

    # -----------------------------------------------------
    # 1. Test Case Directories
    # -----------------------------------------------------
    now = datetime.now(JST)
    case_id = "SMOKE_001"
    case_log_dir, case_assets_dir = case_dirs(case_id, now)

    # -----------------------------------------------------
    # 2. LogContext
    # -----------------------------------------------------
    log = LogContext(
        case_id=case_id,
        timestamp=now,
        test_type="smoke",
        environment=config.get("profile", "internet"),
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
    )
    create_case_log(case_log_dir, log)

    # -----------------------------------------------------
    # 3. Instantiate Page Objects
    # -----------------------------------------------------
    login = LoginPage(page, config, timeout=30000)
    select = ChatSelectPage(page, config, timeout=30000)
    chat = ChatPage(page, config, timeout=30000)

    # -----------------------------------------------------
    # 4. Login
    # -----------------------------------------------------
    page.goto(config["url"], wait_until="load")

    from pathlib import Path

    # --- CI evidence (temporary) ---
    assets_dir = Path(case_assets_dir)
    page.screenshot(path=str(assets_dir / "before_login.png"))
    html = page.content()
    (assets_dir / "before_login.html").write_text(html, encoding="utf-8")
    # --- /CI evidence ---

    login.login(
        evidence_dir=case_assets_dir,
    )
    log.add_section("login", {"result": "success"})

    # -----------------------------------------------------
    # 5. Select Chat
    # -----------------------------------------------------
    AI_NAME = "プライベートナレッジ"

    select.open_ai(
        name=AI_NAME,
        evidence_dir=case_assets_dir,
    )
    log.add_section("chat_select", {"ai_name": AI_NAME})

    # -----------------------------------------------------
    # 6. Submit (UI only)
    # -----------------------------------------------------
    QUESTION = "こんにちは"

    receipt = chat.submit(
        QUESTION,
        evidence_dir=case_assets_dir,
    )
    log.add_section(
        "chat_submit",
        {
            "submit_id": receipt.submit_id,
            "ui_ack": receipt.ui_ack,
        },
    )

    assert receipt.ui_ack is True, "UI submit did not complete"

    # -----------------------------------------------------
    # 7. Probe (Answer Detection)
    # -----------------------------------------------------
    capture_seconds = config.get("probe_capture_seconds", 30)

    summary = run_graphql_probe(
        page,
        chat_id=page.url.split("/")[-1],
        capture_seconds=capture_seconds,
    )

    log.add_section(
        "probe_summary",
        {
            "status": summary["status"],
            "correlation_state": summary["correlation_state"],
        },
    )

    # Smoke-level assertion:
    # At least some evidence must exist.
    assert (
        summary["correlation_state"] != "No Evidence"
    ), "No observable correlation evidence was detected"
