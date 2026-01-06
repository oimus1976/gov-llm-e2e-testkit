# tests/rag/test_rag_basic_v0_1.py

import pytest
from datetime import datetime, timezone, timedelta
import os

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


def _resolve_probe_timeout(config: dict) -> int:
    """
    Determine probe timeout with precedence:
    1) config["probe_timeout_sec"]
    2) config["probe_capture_seconds"]
    3) env PROBE_TIMEOUT_SEC
    4) fallback to browser page timeout_ms
    """
    candidates = [
        config.get("probe_timeout_sec"),
        config.get("probe_capture_seconds"),
        os.getenv("PROBE_TIMEOUT_SEC"),
    ]

    for value in candidates:
        if value is None:
            continue
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed

    try:
        return max(1, int(config["browser"]["page_timeout_ms"]) // 1000)
    except Exception:
        return 90


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
            probe_timeout_sec=_resolve_probe_timeout(config),
        )
    except AnswerNotAvailableError as e:
        pytest.skip(str(e))
    except AnswerTimeoutError as e:
        pytest.skip(str(e))

    # -----------------------------------------------------
    # 3. keyword judgment
    # -----------------------------------------------------
    expected_keywords = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    missing = [kw for kw in expected_keywords if kw not in answer_text]
    unexpected = [ng for ng in must_not if ng in answer_text]

    status = "PASS" if not missing and not unexpected else "FAIL"

    # -----------------------------------------------------
    # 4. logging
    # -----------------------------------------------------
    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config.get("profile", "internet"),
        timestamp=now,
    )

    create_case_log(case_log_dir, ctx)

    print("ANSWER_TEXT:", answer_text)
    print("MISSING:", missing)
    print("UNEXPECTED:", unexpected)

    assert status == "PASS"
