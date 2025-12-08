# tests/test_smoke_llm.py
# gov-llm-e2e-testkit Smoke Test (v0.1)
# 目的：ログイン → 質問 → 応答取得 が成立することのみを確認

from datetime import datetime, timezone, timedelta
import pytest

from src.log_writer import LogContext, create_case_log


@pytest.mark.asyncio
async def test_smoke_llm(chat_page, env_config, log_base_dir):
    """
    Smoke Test の正式構造：
    - chat_page fixture：ログイン済み PageObject を提供
    - env_config：config, options から環境情報を取得
    - log_writer：ログ生成を行う
    """
    config, options = env_config

    # -------------------------
    # 1. 実行
    # -------------------------
    question = "こんにちは"
    answer = await chat_page.ask(question)

    # -------------------------
    # 2. 判定
    # -------------------------
    status = "PASS" if isinstance(answer, str) and answer.strip() else "FAIL"

    # -------------------------
    # 3. ログ生成
    # -------------------------
    ctx = LogContext(
        case_id="SMOKE_001",
        test_type="smoke",
        environment=config["profile"],
        timestamp=datetime.now(timezone(timedelta(hours=9))),
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=question,
        output_text=answer,
        status=status,
        metadata={
            "browser": "chromium",
            "test_type": "smoke",
        },
    )

    create_case_log(log_base_dir, ctx)

    # -------------------------
    # 4. pytest アサーション
    # -------------------------
    assert status == "PASS", "LLM が応答を返しませんでした。"
