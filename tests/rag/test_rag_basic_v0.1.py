# tests/rag/test_rag_basic_v0.1.py
# Basic RAG Test v0.1
# 目的：
# - expected_keywords がすべて回答に含まれる（AND 判定）
# - must_not_contain が回答に含まれない（NOT 判定）
# - 結果を log_writer により Markdown ログとして残す

import pytest
import yaml
import pathlib

from datetime import datetime, timezone, timedelta
from src.log_writer import LogContext, create_case_log


# ---------------------------------------------------------
# YAML 読み込みユーティリティ
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
# Basic RAG Test（正式版）
# ---------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_basic_cases())
async def test_rag_basic(case, chat_page, env_config, log_base_dir):
    config, options = env_config

    # -------------------------
    # 1. 実行
    # -------------------------
    question = case["question"]
    answer = await chat_page.ask(question)

    # -------------------------
    # 2. 判定
    # -------------------------
    expected_keywords = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    missing = [kw for kw in expected_keywords if kw not in answer]
    unexpected = [ng for ng in must_not if ng in answer]

    status = "PASS" if not missing and not unexpected else "FAIL"

    # -------------------------
    # 3. ログ生成
    # -------------------------
    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config["profile"],
        timestamp=datetime.now(timezone(timedelta(hours=9))),
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=question,
        output_text=answer,
        expected_keywords=expected_keywords,
        must_not_contain=must_not,
        missing_keywords=missing,
        unexpected_words=unexpected,
        status=status,
        metadata={
            "browser": "chromium",
            "test_type": "basic",
        },
    )

    create_case_log(log_base_dir, ctx)

    # -------------------------
    # 4. pytest アサーション
    # -------------------------
    assert status == "PASS", (
        f"[{case['id']}] Basic RAG Test failed: "
        f"missing={missing}, unexpected={unexpected}"
    )
