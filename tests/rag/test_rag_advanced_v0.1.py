# tests/rag/test_rag_advanced_v0.1.py
# Advanced RAG Test v0.1
# 目的：
# - multi-turn RAG の高度検証
# - expected_keywords（各ターン）の確認
# - must_not_contain の確認
# - 詳細ログ（details）を含む Markdown ログ生成

import pytest
import yaml
import pathlib

from datetime import datetime, timezone, timedelta
from src.log_writer import LogContext, create_case_log


# ---------------------------------------------------------
# YAML 読み込みユーティリティ
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
# Advanced RAG Test（正式版）
# ---------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_advanced_cases())
async def test_rag_advanced(case, chat_page, env_config, log_base_dir):
    config, options = env_config

    turns = case.get("turns", [])
    must_not = case.get("must_not_contain", [])

    last_answer = ""
    detail_lines = []

    # -----------------------------------------------------
    # 1. multi-turn 実行と詳細ログ構築
    # -----------------------------------------------------
    for i, turn in enumerate(turns, start=1):
        role = turn.get("role")
        content = turn.get("content")

        if role == "user":
            # user → LLM 質問
            last_answer = await chat_page.ask(content)
            detail_lines.append(f"[Turn {i}] user: {content}")
            detail_lines.append(f"[Turn {i}] llm_answer: {last_answer}")

        elif role == "expected_keywords":
            # expected_keywords → 検証
            for kw in content:
                if kw in last_answer:
                    detail_lines.append(f"[Turn {i}] OK: keyword found → {kw}")
                else:
                    detail_lines.append(f"[Turn {i}] NG: keyword missing → {kw}")
        else:
            # 未知ロール → スキップ（後方互換）
            detail_lines.append(f"[Turn {i}] UNKNOWN ROLE skipped: {role}")
            continue

    # -----------------------------------------------------
    # 2. missing / unexpected 判定
    # -----------------------------------------------------
    # 全ターン expected_keywords を flatten
    expected_keywords_total = [
        kw for turn in turns if turn.get("role") == "expected_keywords"
        for kw in turn.get("content", [])
    ]

    missing = [kw for kw in expected_keywords_total if kw not in last_answer]
    unexpected = [ng for ng in must_not if ng in last_answer]

    status = "PASS" if not missing and not unexpected else "FAIL"

    # detail の最終整形
    detail_lines.append("")
    detail_lines.append("=== SUMMARY ===")
    detail_lines.append(f"missing_keywords: {missing}")
    detail_lines.append(f"unexpected_words: {unexpected}")
    details_text = "\n".join(detail_lines)

    # -----------------------------------------------------
    # 3. LogContext 構築
    # -----------------------------------------------------
    ctx = LogContext(
        case_id=case["id"],
        test_type="advanced",
        environment=config["profile"],
        timestamp=datetime.now(timezone(timedelta(hours=9))),
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],

        # Advanced は「最後の回答を代表回答とする」
        question="multi-turn advanced test",
        output_text=last_answer,

        expected_keywords=expected_keywords_total,
        must_not_contain=must_not,
        missing_keywords=missing,
        unexpected_words=unexpected,

        # Advanced 独自の詳細情報
        details=details_text,

        status=status,
        metadata={
            "browser": "chromium",
            "test_type": "advanced",
        },
    )

    create_case_log(log_base_dir, ctx)

    # -----------------------------------------------------
    # 4. pytest アサーション
    # -----------------------------------------------------
    assert status == "PASS", (
        f"[{case['id']}] Advanced RAG Test failed: "
        f"missing={missing}, unexpected={unexpected}"
    )
