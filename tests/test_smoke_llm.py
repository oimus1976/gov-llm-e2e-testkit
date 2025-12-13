# ---------------------------------------------------------
# Smoke Test v0.3 (Sync Playwright)
# gov-llm-e2e-testkit
# 最終更新: 2025-12-10
# ---------------------------------------------------------

import pytest
from datetime import datetime, timezone, timedelta

from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

from src.log_writer import LogContext, create_case_log


# JST タイムスタンプ（ログ用）
JST = timezone(timedelta(hours=9))


@pytest.mark.smoke
def test_smoke_llm(page, env_config, case_dirs):
    """
    gov-llm-e2e-testkit の最小動作保証テスト（Smoke v0.3）
    - ログイン成功
    - プライベートナレッジのチャット画面へ遷移
    - メッセージ送信 → 応答取得
    """

    config, _options = env_config

    # -----------------------------------------------------
    # 1. Test Case Directories
    # -----------------------------------------------------
    now = datetime.now(JST)
    case_id = "SMOKE_001"
    case_log_dir, case_assets_dir = case_dirs(case_id, now)

    # -----------------------------------------------------
    # 2. LogContext（v0.11）
    # -----------------------------------------------------
    log = LogContext(
        case_id=case_id,
        timestamp=now,
        test_type="smoke",
        environment=config.get("profile", "internet"),     # fallback 安全
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
    )

    create_case_log(case_log_dir, log)

    # -----------------------------------------------------
    # 3. Instantiate Page Objects
    # -----------------------------------------------------
    login = LoginPage(page, timeout=30000)
    select = ChatSelectPage(page, timeout=30000)
    chat = ChatPage(page, timeout=30000)

    # -----------------------------------------------------
    # 4. Login
    # -----------------------------------------------------
    url = config["url"]
    username = config["username"]
    password = config["password"]

    page.goto(url, wait_until="load")

    login.login(
        evidence_dir=case_assets_dir,
    )


    log.add_section("login", {"result": "success", "url": url})

    # -----------------------------------------------------
    # 5. Select Chat ("プライベートナレッジ")
    # -----------------------------------------------------
    AI_NAME = "プライベートナレッジ"

    select.open_ai(
        name=AI_NAME,
        evidence_dir=case_assets_dir,
    )

    log.add_section("chat_select", {"ai_name": AI_NAME, "result": "opened"})

    # -----------------------------------------------------
    # 6. Chat → Send → Response
    # -----------------------------------------------------
    QUESTION = "こんにちは"

    answer = chat.ask(
        QUESTION,
        evidence_dir=case_assets_dir,
    )

    log.add_section("chat_ask", {"question": QUESTION, "answer": answer})

    # -----------------------------------------------------
    # 7. Assertions
    # -----------------------------------------------------
    assert isinstance(answer, str) and len(answer) > 0, "LLM 応答が取得できませんでした。"
