import pytest

from src.f9.a.resolution.auto_resolver import (
    resolve_article_reference,
    ArticleResolutionError,
)
from src.f9.a.ordinance.ordinance_structure import OrdinanceStructure


def test_resolve_article_only_ok_single_article():
    """条が1つしか存在しない場合は自動解決できる"""

    ordinance = OrdinanceStructure(
        ordinance_id="k518RG00000022",
        articles=[3],
        paragraphs={3: [1, 2]},
    )

    result = resolve_article_reference(
        question_text="第○条はどのような内容を定めていますか。",
        ordinance_structure=ordinance,
    )

    assert result.article == 3
    assert result.paragraph is None


def test_resolve_article_only_ng_multiple_articles():
    """条が複数存在する場合は解決不能"""

    ordinance = OrdinanceStructure(
        ordinance_id="k518RG00000022",
        articles=[1, 2, 3],
        paragraphs={
            1: [1],
            2: [1],
            3: [1],
        },
    )

    with pytest.raises(ArticleResolutionError):
        resolve_article_reference(
            question_text="第○条はどのような内容を定めていますか。",
            ordinance_structure=ordinance,
        )


def test_resolve_article_and_paragraph_ok_single_each():
    """条・項ともに1つなら自動解決できる"""

    ordinance = OrdinanceStructure(
        ordinance_id="k518RG00000022",
        articles=[3],
        paragraphs={3: [2]},
    )

    result = resolve_article_reference(
        question_text="第○条第○項では何を規定していますか。",
        ordinance_structure=ordinance,
    )

    assert result.article == 3
    assert result.paragraph == 2


def test_resolve_article_and_paragraph_ng_multiple_paragraphs():
    """項が複数存在する場合は解決不能"""

    ordinance = OrdinanceStructure(
        ordinance_id="k518RG00000022",
        articles=[3],
        paragraphs={3: [1, 2, 3]},
    )

    with pytest.raises(ArticleResolutionError):
        resolve_article_reference(
            question_text="第○条第○項では何を規定していますか。",
            ordinance_structure=ordinance,
        )
