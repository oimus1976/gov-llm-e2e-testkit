import pytest
from pathlib import Path

from src.execution.run_single_question import run_single_question
from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


def test_f4_case1_writer(chat_page, resolved_profile):
    """
    F4 Case1:
    - 目的条文の基本検索
    - HTML / Markdown 差分評価のベースケース
    """
    question = "この条例（k518RG00000064）の目的を分かりやすく説明してください。"
    evidence_terms = ["規則", "施行", "必要な事項", "行政手続条例"]

    output_dir = Path("sandbox/f4")

    # -----------------------------------------------------
    # 1-2. 質問送信 + Answer Detection（probe）
    # -----------------------------------------------------
    try:
        result = run_single_question(
            chat_page=chat_page,
            question_text=question,
            question_id="case1",
            ordinance_id="k518RG00000064",
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
            "case_id": "case1",
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


def test_write_f4_result_execution_context_records(tmp_path):
    execution_context = {
        "login_identity": {
            "configured": {
                "source": "env.yaml",
                "value": "user@example.com",
            },
            "observed": {
                "status": "unverified",
                "value": None,
                "note": "Headless 実行における取得可否が未検証のため",
            },
        }
    }

    evidence_result = {
        "evidence_terms": ["規則"],
        "hits": ["規則"],
        "hit_count": 1,
        "total": 1,
        "hit_rate": "1 / 1",
    }

    output_path = write_f4_result(
        output_dir=tmp_path,
        case_info={
            "case_id": "case1",
            "ordinance": "k518RG00000064",
            "question": "条例の目的を説明してください。",
        },
        profile="html",
        run_info={
            "chat_id": "chat-1",
            "submit_id": "submit-1",
        },
        answer_text="sample answer",
        evidence_result=evidence_result,
        execution_context=execution_context,
    )

    content = output_path.read_text(encoding="utf-8")
    assert "execution_context:" in content
    assert "login_identity:" in content
    assert "configured:" in content
    assert "observed:" in content
    assert "status: unverified" in content
    assert "value: null" in content
