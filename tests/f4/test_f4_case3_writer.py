import pytest
from pathlib import Path

from src.execution.run_single_question import run_single_question
from src.f4.evaluator import evaluate_evidence
from src.f4.writer import write_f4_result
from src.answer_probe import (
    AnswerTimeoutError,
    AnswerNotAvailableError,
)


def test_f4_case3_writer(chat_page, resolved_profile):
    """
    F4 Case3:
    - 条文に明示された義務・禁止の抽出
    - 構造依存差分（HTML / Markdown）
    """
    question = (
        "この条例（かつらぎ町介護保険住宅改修費等受領委任払制度の登録等に関する要綱）において、"
        "条文に明示的に記載されている義務および禁止事項について、"
        "該当する条文番号を挙げながら箇条書きで整理してください。"
    )

    # v0.1 観測用 Evidence（意味解釈しない）
    evidence_terms = [
        "しなければならない",
        "できない",
        "取り消すことができる",
        "返還",
    ]

    output_dir = Path("sandbox/f4")

    # -----------------------------------------------------
    # 1-2. 質問送信 + Answer Detection（probe）
    # -----------------------------------------------------
    try:
        result = run_single_question(
            chat_page=chat_page,
            question_text=question,
            question_id="case3",
            ordinance_id="k518RG00001144",
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
            "case_id": "case3",
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
