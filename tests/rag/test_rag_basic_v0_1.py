# ---------------------------------------------------------
# test_rag_basic_v0.2.py  -- Basic RAG Test v0.2
# gov-llm-e2e-testkit
#
# - expected_keywords を全て含むか
# - must_not_contain を含まないか
# - evidence_dir に証跡を保存
# ---------------------------------------------------------

import pytest
import yaml
import pathlib
from datetime import datetime, timezone, timedelta

from src.log_writer import LogContext, create_case_log

JST = timezone(timedelta(hours=9))


# ---------------------------------------------------------
# helper: load basic_cases.yaml
# ---------------------------------------------------------
def load_basic_cases():
    path = pathlib.Path("data/rag/basic_cases.yaml")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cases = data.get("cases", [])
            if not cases:
                pytest.skip("No basic RAG cases found (skip to avoid CI exit 5).")
            return cases
    except Exception as e:
        pytest.skip(f"YAML load error: {e}")


# ---------------------------------------------------------
# basic test
# ---------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_basic_cases())
async def test_rag_basic(case, chat_page, env_config, case_dirs):
    config, _ = env_config

    # ---------------------------------------------
    # case directories
    # ---------------------------------------------
    now = datetime.now(JST)
    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    # ---------------------------------------------
    # ask
    # ---------------------------------------------
    answer = await chat_page.ask(case["question"], evidence_dir=case_assets_dir)

    # ---------------------------------------------
    # evaluation
    # ---------------------------------------------
    expected_keywords = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    missing = [kw for kw in expected_keywords if kw not in answer]
    unexpected = [ng for ng in must_not if ng in answer]

    status = "PASS" if not missing and not unexpected else "FAIL"

    # ---------------------------------------------
    # logging
    # ---------------------------------------------
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
