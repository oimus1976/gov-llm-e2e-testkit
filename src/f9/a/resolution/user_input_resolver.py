# src/f9/a/resolution/user_input_resolver.py

from typing import Dict, List, Optional, Tuple


class UserInputResolutionError(Exception):
    """人間入力による条・項解決に失敗した場合の例外（日本語メッセージ前提）"""

    pass


def resolve_by_user_input(
    article_input: int,
    paragraph_input: Optional[int],
    candidates: Dict,
) -> Tuple[int, Optional[int]]:
    """
    A-4: 人間入力を検証し、条・項を確定する（純関数）

    - 判断・推測は行わない
    - 構造的候補に含まれるかのみを検証する
    """

    # --- 前提検証 ---
    if not isinstance(article_input, int):
        raise UserInputResolutionError("条番号が不正です。整数で入力してください。")

    article_candidates: List[int] = candidates.get("article_candidates", [])
    paragraphs_by_article: Dict[int, List[int]] = candidates.get(
        "paragraphs_by_article", {}
    )

    # --- 条番号の検証 ---
    if article_input not in article_candidates:
        raise UserInputResolutionError(
            "条番号が候補に含まれていません。\n"
            f"- 入力値: {article_input}\n"
            f"- 候補: {article_candidates}"
        )

    # --- 項番号の検証（任意） ---
    if paragraph_input is None:
        # 条のみ指定を許可
        return article_input, None

    if not isinstance(paragraph_input, int):
        raise UserInputResolutionError("項番号が不正です。整数で入力してください。")

    paragraph_candidates = paragraphs_by_article.get(article_input, [])

    if paragraph_input not in paragraph_candidates:
        raise UserInputResolutionError(
            "項番号が候補に含まれていません。\n"
            f"- 条番号: {article_input}\n"
            f"- 入力値: {paragraph_input}\n"
            f"- 候補: {paragraph_candidates}"
        )

    return article_input, paragraph_input
