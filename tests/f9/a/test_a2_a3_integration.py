import pytest

from src.f9.a.binding.ordinance_binder import bind_ordinance_id
from src.f9.a.resolution.auto_resolver import resolve_article_reference
from src.f9.a.ordinance.ordinance_structure import OrdinanceStructure


def test_a2_to_a3_integration_ok():
    """
    A-2 で条例IDが束縛された質問テンプレが、
    条例構造を与えれば A-3 で自動解決できることを確認する。
    """

    # A-2 入力
    templates = [
        "第○条はどのような内容を定めていますか。",
        "第○条第○項では何を規定していますか。",
    ]

    binding = bind_ordinance_id(
        ordinance_id="k518RG00000022",
        question_templates=templates,
    )

    # 条例構造（A-3 前提条件を満たす最小構成）
    ordinance_structure = OrdinanceStructure(
        ordinance_id="k518RG00000022",
        articles=[3],
        paragraphs={3: [2]},
    )

    # 1問目：条のみ
    ref1 = resolve_article_reference(
        question_text=binding.question_templates[0],
        ordinance_structure=ordinance_structure,
    )

    assert ref1.article == 3
    assert ref1.paragraph is None

    # 2問目：条＋項
    ref2 = resolve_article_reference(
        question_text=binding.question_templates[1],
        ordinance_structure=ordinance_structure,
    )

    assert ref2.article == 3
    assert ref2.paragraph == 2
