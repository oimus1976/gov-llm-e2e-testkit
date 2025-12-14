import pytest
from pathlib import Path

from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    wait_for_answer_text,
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


# pytestmark = pytest.mark.rag


def test_f4_case1_writer(chat_page, env_config):
    config, _ = env_config

    question = "この条例の目的を分かりやすく説明してください。"
    evidence_terms = ["規則", "施行", "必要な事項", "行政手続条例"]

    submit = chat_page.submit(question)
    submit_id = submit.get("submit_id") if isinstance(submit, dict) else "N/A"
    chat_id = chat_page.page.url.split("/")[-1]

    try:
        answer = wait_for_answer_text(
            page=chat_page.page,
            submit_id=submit_id,
            chat_id=chat_id,
            timeout_sec=30,
        )
    except (AnswerTimeoutError, AnswerNotAvailableError) as e:
        pytest.skip(str(e))

    evidence = evaluate_evidence(answer, evidence_terms)

    write_f4_result(
        output_dir=Path("sandbox/f4"),
        case_info={
            "case_id": "case1",
            "ordinance": "k518RG00000064",
            "question": question,
        },
        run_info={
            "mode": "HTML",
            "chat_id": chat_id,
            "submit_id": submit_id,
        },
        answer_text=answer,
        evidence_result=evidence,
    )
