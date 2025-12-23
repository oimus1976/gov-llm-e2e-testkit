import pytest
from pathlib import Path

from src.execution.run_single_question import run_single_question
from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


def test_f4_case2_writer(chat_page, resolved_profile):
    """
    F4 Case2:
    - 本則と附則をまたぐ構造参照
    - HTML / Markdown 差分評価
    """
    question = (
        "この条例（k518RG00000400）について、"
        "本則と附則のそれぞれで定められている内容を整理して説明してください。"
    )

    # v0.1 観測用 Evidence（語の存在のみ）
    evidence_terms = ["附則", "施行", "経過措置"]

    output_dir = Path("sandbox/f4")

    # -----------------------------------------------------
    # 1-2. 質問送信 + Answer Detection（probe）
    # -----------------------------------------------------
    try:
        result = run_single_question(
            chat_page=chat_page,
            question_text=question,
            question_id="case2",
            ordinance_id="k518RG00000400",
            output_dir=output_dir,
            profile=resolved_profile,
            timeout_sec=30,
        )
    except (AnswerTimeoutError, AnswerNotAvailableError) as e:
        pytest.skip(str(e))

    # -----------------------------------------------------
    # 3. Evidence 評価
    # -----------------------------------------------------
    evidence = evaluate_evidence(result.answer_text, evidence_terms)

    # -----------------------------------------------------
    # 4. F4 結果ログ出力
    # -----------------------------------------------------
    write_f4_result(
        output_dir=output_dir,
        case_info={
            "case_id": "case2",
            "ordinance": result.ordinance_id,
            "question": result.question_text,
        },
        profile=result.profile,
        run_info={
            "chat_id": result.chat_id,
            "submit_id": result.submit_id,
        },
        answer_text=result.answer_text,
        evidence_result=evidence,
    )
