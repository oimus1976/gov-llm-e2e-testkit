# ==========================================================
# RAG Basic Sync v0.2
# ==========================================================

import pytest
from datetime import datetime, timezone, timedelta

from tests.rag.rag_cases_basic import load_basic_cases
from tests.pages.chat_page import ChatPage
from src.log_writer import LogContext, create_case_log

pytestmark = pytest.mark.rag

JST = timezone(timedelta(hours=9))


@pytest.mark.parametrize("case", load_basic_cases())
def test_rag_basic(case, chat_page, env_config, case_dirs):
    config, _ = env_config
    now = datetime.now(JST)

    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    # 1回質問
    answer = chat_page.ask(case["question"], evidence_dir=case_assets_dir)

    # 判定
    expected_keywords = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    missing = [kw for kw in expected_keywords if kw not in answer]
    unexpected = [ng for ng in must_not if ng in answer]

    status = "PASS" if not missing and not unexpected else "FAIL"

    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=case["question"],
        output_text=answer,
        expected_keywords=expected_keywords,
        must_not_contain=must_not,
        missing_keywords=missing,
        unexpected_words=unexpected,
        status=status,
        assets_dir=str(case_assets_dir),
    )

    create_case_log(case_log_dir, ctx)
    assert status == "PASS"
