import pytest

from src.f9.a.question.template_validator import validate_question_templates
from src.f9.a.binding.ordinance_binder import bind_ordinance_id
from src.f9.a.binding.binding_model import OrdinanceBinding


def test_a1_to_a2_integration_ok():
    """
    A-1 で検証された質問テンプレ集合が
    A-2 にそのまま渡せることを確認する
    """

    templates = [
        "この条例は何を目的として制定されていますか。",
        "第○条はどのような内容を定めていますか。",
        "第○条第○項では何を規定していますか。",
    ]

    validated = validate_question_templates(templates)

    result = bind_ordinance_id(
        ordinance_id="k518RG00000022",
        question_templates=validated,
    )

    assert isinstance(result, OrdinanceBinding)
    assert result.ordinance_id == "k518RG00000022"
    assert result.question_templates == templates
