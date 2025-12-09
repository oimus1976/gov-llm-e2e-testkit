# ==========================================================
# RAG Advanced Sync v0.2
# ==========================================================

import pytest
from datetime import datetime, timezone, timedelta

from tests.rag.rag_cases_advanced import load_advanced_cases
from tests.pages.chat_page import ChatPage
from src.log_writer import LogContext, create_case_log

JST = timezone(timedelta(hours=9))


@pytest.mark.parametrize("case", load_advanced_cases())
def test_rag_advanced(case, chat_page, env_config, case_dirs):
    config, _ = env_config
    now = datetime.now(JST)

    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    turns = case.get("turns", [])
    must_not = case.get("must_not_contain", [])
    last_answer = ""

    for turn in turns:
        role = turn["role"]
        content = turn["content"]

        if role == "user":
            last_answer = chat_page.ask(content, evidence_dir=case_assets_dir)

        elif role == "expected_keywords":
            for kw in content:
                assert kw in last_answer, f"[{case['id']}] expected keyword not found: {kw}"

    unexpected = [ng for ng in must_not if ng in last_answer]
    status = "PASS" if not unexpected else "FAIL"

    ctx = LogContext(
        case_id=case["id"],
        test_type="advanced",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=turns[-1]["content"] if turns else "",
        output_text=last_answer,
        must_not_contain=must_not,
        unexpected_words=unexpected,
        status=status,
        assets_dir=str(case_assets_dir),
    )

    create_case_log(case_log_dir, ctx)
    assert status == "PASS"
