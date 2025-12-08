# ---------------------------------------------------------
# test_smoke_llm.py  -- Smoke Test v0.2
# gov-llm-e2e-testkit
#
# - ログイン → チャット質問 → 応答取得 が成立する最小テスト
# - PageObject v0.2 の safe_* / evidence_dir を利用
# - ケース単位で case_log_dir / case_assets_dir を作成
# ---------------------------------------------------------

import pytest
from datetime import datetime, timezone, timedelta

from tests.pages.login_page import LoginPage
from tests.pages.chat_page import ChatPage

from src.log_writer import LogContext, create_case_log


JST = timezone(timedelta(hours=9))


@pytest.mark.asyncio
async def test_smoke_llm(page, env_config, case_dirs):
    config, _ = env_config

    # -----------------------------------------------------
    # 1. case directories
    # -----------------------------------------------------
    now = datetime.now(JST)
    case_id = "SMOKE_001"
    case_log_dir, case_assets_dir = case_dirs(case_id, now)

    # -----------------------------------------------------
    # 2. Login
    # -----------------------------------------------------
    login = LoginPage(page, timeout=config["browser"]["page_timeout_ms"])

    USERNAME = config["auth"]["username"]
    PASSWORD = config["auth"]["password"]

    await page.goto(config["auth"]["login_url"])
    await login.login(USERNAME, PASSWORD, evidence_dir=case_assets_dir)

    # -----------------------------------------------------
    # 3. Chat
    # -----------------------------------------------------
    chat = ChatPage(page, timeout=config["browser"]["page_timeout_ms"])
    await chat.wait_for_ready()

    question = "こんにちは"
    answer = await chat.ask(question, evidence_dir=case_assets_dir)

    status = "PASS" if answer.strip() else "FAIL"

    # -----------------------------------------------------
    # 4. logging
    # -----------------------------------------------------
    ctx = LogContext(
        case_id=case_id,
        test_type="smoke",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=question,
        output_text=answer,
        status=status,
        metadata={"browser": "chromium"},
        assets_dir=str(case_assets_dir),
    )

    create_case_log(case_log_dir, ctx)
    assert status == "PASS"
