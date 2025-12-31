from pathlib import Path

from src.f9.a.question.template_validator import validate_question_templates
from src.f9.a.question_set.csv_loader import load_question_set_from_csv


def test_a0_csv_to_a1_integration_ok(tmp_path: Path):
    """
    A-0:
    CSV から読み込んだ質問テンプレ集合を、
    A-1 にそのまま渡せることを確認する。
    """

    csv_file = tmp_path / "questions.csv"
    csv_file.write_text(
        "question_id,text\n"
        "Q01,この条例は何を目的として制定されていますか。\n"
        "Q02,第○条はどのような内容を定めていますか。\n"
        "Q03,第○条第○項では何を規定していますか。\n",
        encoding="utf-8",
    )

    question_texts = load_question_set_from_csv(csv_file)

    assert question_texts == [
        "この条例は何を目的として制定されていますか。",
        "第○条はどのような内容を定めていますか。",
        "第○条第○項では何を規定していますか。",
    ]

    # A-1 に渡せることを保証
    validated = validate_question_templates(question_texts)
    assert len(validated) == 3
