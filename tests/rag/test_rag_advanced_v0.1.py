# ---------------------------------------------------------
# test_rag_advanced_v0.2.py  -- Advanced RAG Test v0.2
# gov-llm-e2e-testkit
#
# - multi-turn user/expected_keywords の対話評価
# - must_not_contain の NOT 判定
# - evidence_dir に応じて PageObject v0.2 が証跡保存
# ---------------------------------------------------------

import pytest
import yaml
import pathlib
from datetime import datetime, timezone, timedelta

from src.log_writer import LogContext, create_case_log

JST = timezone(timedelta(hours=9))


# ---------------------------------------------------------
# helper: load advanced_cases.yaml
# ---------------------------------------------------------
def load_advanced_cases():
    path = pathlib.Path("data/rag/advanced_cases.yaml")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cases = data.get("cases", [])
            if not cases:
                pytest.skip("No advanced RAG cases found (skip to avoid CI exit 5).")
            return cases
    except Exception as e:
        pytest.skip(f"YAML load error: {e}")


# ---------------------------------------------------------
# advanced test
# ---------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_advanced_cases())
async def test_rag_advanced(case, chat_page, env_config, case_dirs):
    config, _ = env_config

    # ---------------------------------------------
    # case directories
    # ---------------------------------------------
    now = datetime.now(JST)
    case_log_dir, case_assets_dir = case_dirs(case["id"], now)

    turns = case.get("turns", [])
    must_not = case.get("must_not_contain", [])
    last_answer = ""

    # ---------------------------------------------
    # multi-turn flow
    # ---------------------------------------------
    for turn in turns:
        role = turn.get("role")
        content = turn.get("content")

        if role == "user":
            last_answer = await chat_page.ask(content, evidence_dir=case_assets_dir)

        elif role == "expected_keywords":
            for kw in content:
                assert kw in last_answer, f"[{case['id']}] expected keyword not found: {kw}"

        else:
            # unsupported roles → skip（未来拡張）
            continue

    # ---------------------------------------------
    # must_not_contain 判定
    # ---------------------------------------------
    unexpected = [ng for ng in must_not if ng in last_answer]
    status = "PASS" if not unexpected else "FAIL"

    # ---------------------------------------------
    # logging
    # ---------------------------------------------
    ctx = LogContext(
        case_id=case["id"],
        test_type="advanced",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=turns[-1].get("content") if turns else "",
        output_text=last_answer,
        must_not_contain=must_not,
        unexpected_words=unexpected,
        status=status,
        details="Advanced multi-turn evaluation",
        assets_dir=str(case_assets_dir),
    )

    create_case_log(case_log_dir, ctx)
    assert status == "PASS"
