# ==========================================================
# RAG Advanced Sync v0.2
# ==========================================================

import pytest
from datetime import datetime, timezone, timedelta

from tests.rag.rag_cases_advanced import load_advanced_cases
from tests.pages.chat_page import ChatPage
from src.log_writer import LogContext, create_case_log

pytestmark = pytest.mark.rag

JST = timezone(timedelta(hours=9))

@pytest.mark.parametrize("case", load_advanced_cases())
def test_rag_advanced(case, chat_page, env_config, case_dirs):
    config, _ = env_config
    now = datetime.now(JST)

    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    turns = case.get("turns", [])
    last_answer = ""

    for turn in turns:
        role = turn["role"]
        content = turn["content"]

        if role == "user":
            last_answer = chat_page.ask(content, evidence_dir=case_assets_dir)

        elif role == "expected_keywords":
            pass

    ctx = LogContext(
        case_id=case["id"],
        test_type="advanced",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
    )

    create_case_log(case_log_dir, ctx)
