import pytest

from src.f9.a.binding.ordinance_binder import (
    bind_ordinance_id,
    OrdinanceBindingError,
)
from src.f9.a.binding.binding_model import OrdinanceBinding


def test_bind_ordinance_id_ok():
    """条例IDと質問テンプレ集合を正常に束縛できる"""
    ordinance_id = "k518RG00000022"
    templates = [
        "この条例は何を目的として制定されていますか。",
        "第○条はどのような内容を定めていますか。",
    ]

    result = bind_ordinance_id(
        ordinance_id=ordinance_id,
        question_templates=templates,
    )

    assert isinstance(result, OrdinanceBinding)
    assert result.ordinance_id == ordinance_id
    assert result.question_templates == templates


def test_bind_ordinance_id_ng_empty_ordinance_id():
    """条例IDが空の場合はエラー"""
    with pytest.raises(OrdinanceBindingError):
        bind_ordinance_id(
            ordinance_id="",
            question_templates=["この条例は何を目的として制定されていますか。"],
        )


def test_bind_ordinance_id_ng_none_ordinance_id():
    """条例IDが None の場合はエラー"""
    with pytest.raises(OrdinanceBindingError):
        bind_ordinance_id(
            ordinance_id=None,  # type: ignore
            question_templates=["この条例は何を目的として制定されていますか。"],
        )


def test_bind_ordinance_id_ng_empty_templates():
    """質問テンプレ集合が空の場合はエラー"""
    with pytest.raises(OrdinanceBindingError):
        bind_ordinance_id(
            ordinance_id="k518RG00000022",
            question_templates=[],
        )
