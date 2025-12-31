import pytest

from src.f9.a.question.template_validator import (
    validate_question_templates,
    TemplateValidationError,
)


def test_validate_question_templates_ok():
    """抽象表現のみの質問テンプレは通過する"""
    templates = [
        "この条例は何を目的として制定されていますか。",
        "第○条はどのような内容を定めていますか。",
        "第○条第○項では何を規定していますか。",
    ]

    result = validate_question_templates(templates)

    # A-1 は変換しない
    assert result == templates


def test_validate_question_templates_ng_concrete_article():
    """具体的な条番号が含まれる場合はエラー"""
    templates = [
        "第3条は何を定めていますか。",
    ]

    with pytest.raises(TemplateValidationError) as excinfo:
        validate_question_templates(templates)

    message = str(excinfo.value)
    assert "質問テンプレが仕様に違反しています" in message
    assert "具体的な条番号" in message


def test_validate_question_templates_ng_concrete_paragraph():
    """具体的な条・項番号が含まれる場合はエラー"""
    templates = [
        "第2条第1項では何を定めていますか。",
    ]

    with pytest.raises(TemplateValidationError):
        validate_question_templates(templates)


def test_validate_question_templates_ng_ordinance_id():
    """条例IDが直接書かれている場合はエラー"""
    templates = [
        "この条例（k518RG00000022）は何を目的としていますか。",
    ]

    with pytest.raises(TemplateValidationError):
        validate_question_templates(templates)
