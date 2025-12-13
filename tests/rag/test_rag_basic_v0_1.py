# tests/rag/test_rag_basic_v0_1.py

import pytest
from datetime import datetime, timezone, timedelta

from tests.rag.rag_cases_basic import load_basic_cases
from tests.pages.chat_page import ChatPage
from src.log_writer import LogContext, create_case_log
from src.answer_probe import wait_for_answer_text  # ← 既存 or 最小ラッパー

pytestmark = pytest.mark.rag
JST = timezone(timedelta(hours=9))


@pytest.mark.parametrize("case", load_basic_cases())
def test_rag_basic_v0_1(case, chat_page, env_config, case_dirs):
    config, _ = env_config
    now = datetime.now(JST)

    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    # 1. submit（UI送信のみ）
    receipt = chat_page.submit(
        case["question"],
        evidence_dir=case_assets_dir,
    )
    assert receipt.ui_ack is True

    # 2. answer detection（probe）
    answer_text = wait_for_answer_text(
        submit_id=receipt.submit_id,
        chat_id=chat_page.chat_id,
        timeout_sec=60,
    )

    assert answer_text, "answer_text not retrieved"

    # 3. keyword judgment
    expected = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    missing = [kw for kw in expected if kw not in answer_text]
    unexpected = [ng for ng in must_not if ng in answer_text]

    status = "PASS" if not missing and not unexpected else "FAIL"

    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config["profile"],
        timestamp=now,
        question=case["question"],
        output_text=answer_text,
        expected_keywords=expected,
        must_not_contain=must_not,
        missing_keywords=missing,
        unexpected_words=unexpected,
        status=status,
        assets_dir=str(case_assets_dir),
    )

    create_case_log(case_log_dir, ctx)
    assert status == "PASS"
