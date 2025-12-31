from typing import List
from .binding_model import OrdinanceBinding


class OrdinanceBindingError(Exception):
    """条例IDバインディングに失敗した場合の例外"""

    pass


def bind_ordinance_id(
    ordinance_id: str,
    question_templates: List[str],
) -> OrdinanceBinding:
    """
    A-2: 条例IDを質問テンプレ集合に束縛する
    """

    # 条例ID の検証
    if not ordinance_id or not isinstance(ordinance_id, str):
        raise OrdinanceBindingError("条例IDが指定されていません。")

    # 質問テンプレ集合の検証
    if not isinstance(question_templates, list) or len(question_templates) == 0:
        raise OrdinanceBindingError("質問テンプレ集合が空です。")

    # A-2 の責務は「束縛する」だけ
    return OrdinanceBinding(
        ordinance_id=ordinance_id,
        question_templates=question_templates,
    )
