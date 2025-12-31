from dataclasses import dataclass
from typing import Optional

from src.f9.a.ordinance.ordinance_structure import OrdinanceStructure

from src.f9.a.ordinance.ordinance_protocol import OrdinanceStructureProtocol

# src/f9/a/resolution/auto_resolver.py に追加

from src.f9.a.resolution.resolution_required import ResolutionRequired


def auto_resolve_article_paragraph(
    question_text: str,
    ordinance_structure: OrdinanceStructureProtocol,
):
    """
    A-3 公開I/F（A-4 接続点）

    - 一意なら ResolvedArticleRef を返す
    - 一意でなければ ResolutionRequired を送出する
    """
    try:
        return resolve_article_reference(
            question_text=question_text,
            ordinance_structure=ordinance_structure,
        )
    except ArticleResolutionError as e:
        # 候補を構造的に列挙（意味解釈なし）
        candidates = {
            "article_candidates": ordinance_structure.articles,
            "paragraphs_by_article": ordinance_structure.paragraphs,
        }
        raise ResolutionRequired(str(e), candidates)


@dataclass(frozen=True)
class ResolvedArticleRef:
    article: int
    paragraph: Optional[int]  # 条のみ指定の場合は None


class ArticleResolutionError(Exception):
    """条・項の自動解決に失敗した場合の例外"""

    pass


def resolve_article_reference(
    question_text: str,
    ordinance_structure: OrdinanceStructureProtocol,
) -> ResolvedArticleRef:
    """
    A-3: 抽象参照（第○条 / 第○条第○項）を
    条例構造に基づいて一意に解決する。

    - 意味解釈は行わない
    - 一意でなければ例外を送出（A-4 に委譲）
    """

    wants_paragraph = "第○条第○項" in question_text
    wants_article = "第○条" in question_text

    # 対象が条かどうか最低限確認
    if not wants_article:
        raise ArticleResolutionError("条指定が含まれていません。")

    articles = ordinance_structure.articles

    # 条の一意性チェック
    if len(articles) != 1:
        raise ArticleResolutionError("条番号を一意に特定できません。")

    article = articles[0]

    # 項指定がない場合
    if not wants_paragraph:
        return ResolvedArticleRef(article=article, paragraph=None)

    # 項指定がある場合
    paragraphs = ordinance_structure.paragraphs.get(article, [])

    if len(paragraphs) != 1:
        raise ArticleResolutionError("項番号を一意に特定できません。")

    return ResolvedArticleRef(article=article, paragraph=paragraphs[0])
