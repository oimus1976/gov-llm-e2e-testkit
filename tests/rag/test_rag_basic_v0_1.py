# tests/rag/test_rag_basic_v0_1.py

import pytest
from datetime import datetime, timezone, timedelta

from tests.rag.rag_cases_basic import load_basic_cases
from tests.pages.chat_page import ChatPage
from src.log_writer import LogContext, create_case_log
from src.answer_probe import (
    wait_for_answer_text,
    AnswerNotAvailableError,
    AnswerTimeoutError,
)


pytestmark = pytest.mark.rag
JST = timezone(timedelta(hours=9))


@pytest.mark.parametrize("case", load_basic_cases())
def test_rag_basic(case, chat_page, env_config, case_dirs):
    config, _ = env_config
    now = datetime.now(JST)

    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    # -----------------------------------------------------
    # 1. 質問送信（submit のみ）
    # -----------------------------------------------------
    submit_result = chat_page.submit(case["question"])

    # submit_id（v0.1 では probe 呼び出しに未使用）
    submit_id = None
    if isinstance(submit_result, dict):
        submit_id = submit_result.get("submit_id")

    # -----------------------------------------------------
    # 2. Answer Detection（probe v0.2 経由）
    # -----------------------------------------------------
    chat_id = chat_page.page.url.split("/")[-1]

    try:
        answer_text = wait_for_answer_text(
            page=chat_page.page,
            submit_id=submit_id or "N/A",
            chat_id=chat_id,
            timeout_sec=config["browser"]["page_timeout_ms"] // 1000,
        )
    except AnswerNotAvailableError as e:
        pytest.skip(str(e))
    except AnswerTimeoutError as e:
        pytest.skip(str(e))

    # -----------------------------------------------------
    # 3. logging
    # -----------------------------------------------------
    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config.get("profile", "internet"),
        timestamp=now,
    )

    create_case_log(case_log_dir, ctx)
