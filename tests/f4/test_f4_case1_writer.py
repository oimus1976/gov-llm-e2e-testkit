import pytest
from pathlib import Path

from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    wait_for_answer_text,
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


def test_f4_case1_writer(chat_page, env_config, resolved_profile):
    """
    F4 Case1:
    - 目的条文の基本検索
    - HTML / Markdown 差分評価のベースケース
    """
    config, _ = env_config

    question = "この条例（k518RG00000064）の目的を分かりやすく説明してください。"
    evidence_terms = ["規則", "施行", "必要な事項", "行政手続条例"]

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
            "case_id": "case1",
            "ordinance": "k518RG00000064",
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
