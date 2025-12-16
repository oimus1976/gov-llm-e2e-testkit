import pytest
from pathlib import Path

from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    wait_for_answer_text,
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


def test_f4_case2_writer(chat_page, env_config, resolved_profile):
    """
    F4 Case2:
    - 本則と附則をまたぐ構造参照
    - HTML / Markdown 差分評価
    """
    config, _ = env_config

    question = (
        "この条例（k518RG00000400）について、"
        "本則と附則のそれぞれで定められている内容を整理して説明してください。"
    )

    # v0.1 観測用 Evidence（語の存在のみ）
    evidence_terms = ["附則", "施行", "経過措置"]

    # -----------------------------------------------------
    # 1. 質問送信（submit のみ）
    # -----------------------------------------------------
    submit = chat_page.submit(question)
    raw_submit_id = submit.get("submit_id") if isinstance(submit, dict) else None
    submit_id = raw_submit_id if raw_submit_id is not None else "N/A"
    chat_id = chat_page.page.url.split("/")[-1]

    # -----------------------------------------------------
    # 2. Answer Detection（probe）
    # -----------------------------------------------------
    try:
        answer = wait_for_answer_text(
            page=chat_page.page,
            submit_id=submit_id,
            chat_id=chat_id,
            timeout_sec=30,
        )
    except (AnswerTimeoutError, AnswerNotAvailableError) as e:
        pytest.skip(str(e))

    # -----------------------------------------------------
    # 3. Evidence 評価
    # -----------------------------------------------------
    evidence = evaluate_evidence(answer, evidence_terms)

    # -----------------------------------------------------
    # 4. F4 結果ログ出力
    # -----------------------------------------------------
    write_f4_result(
        output_dir=Path("sandbox/f4"),
        case_info={
            "case_id": "case2",
            "ordinance": "k518RG00000400",
            "question": question,
        },
        profile=resolved_profile,
        run_info={
            "chat_id": chat_id,
            "submit_id": submit_id,
        },
        answer_text=answer,
        evidence_result=evidence,
    )
