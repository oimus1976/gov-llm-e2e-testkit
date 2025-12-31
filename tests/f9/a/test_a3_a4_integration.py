# tests/f9/a/test_a3_a4_integration.py

import pytest

from dataclasses import dataclass, field

from src.f9.a.resolution.auto_resolver import (
    auto_resolve_article_paragraph,
    ResolutionRequired,
)
from src.f9.a.resolution.user_input_resolver import (
    resolve_by_user_input,
)


@dataclass
class DummyOrdinanceStructure:
    """
    テスト用の最小条例構造スタブ
    """

    articles: list[int] = field(default_factory=lambda: [3, 7])
    paragraphs: dict[int, list[int]] = field(
        default_factory=lambda: {
            3: [1, 2, 3],
            7: [1],
        }
    )


def test_a3_to_a4_integration_resolve_with_user_input():
    """
    A-3 が ResolutionRequired を投げ、
    A-4 による人間入力で最終確定できること。
    """

    ordinance = DummyOrdinanceStructure()

    # A-3：自動解決を試みる（第○条のみ指定）
    with pytest.raises(ResolutionRequired) as excinfo:
        auto_resolve_article_paragraph(
            question_text="第○条はどのような内容を定めていますか。",
            ordinance_structure=ordinance,
        )

    # A-3 が提示した候補を取得
    candidates = excinfo.value.candidates

    assert candidates["article_candidates"] == [3, 7]
    assert candidates["paragraphs_by_article"][3] == [1, 2, 3]
    assert candidates["paragraphs_by_article"][7] == [1]

    # A-4：人間入力で確定（条=3、項=2）
    article, paragraph = resolve_by_user_input(
        article_input=3,
        paragraph_input=2,
        candidates=candidates,
    )

    assert article == 3
    assert paragraph == 2
