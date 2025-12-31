# src/f9/a/question/template_validator.py

from typing import List
import re


class TemplateValidationError(Exception):
    """質問テンプレが F9-A 仕様に違反している場合に送出される例外"""

    pass


# 許可される抽象表現パターン
_ALLOWED_PATTERNS = [
    r"この条例",
    r"第○条",
    r"第○条第○項",
]

# 明示的に禁止するパターン（具体値）
_FORBIDDEN_PATTERNS = [
    r"第[0-9]+条",  # 第3条
    r"第[0-9]+条第[0-9]+項",  # 第2条第1項
    r"k[0-9A-Za-z]+",  # 条例ID 形式（例：k518RG00000022）
]


def validate_question_templates(
    question_template_set: List[str],
) -> List[str]:
    """
    質問テンプレ集合が F9-A 仕様に適合しているかを検証する。

    - 抽象表現（この条例／第○条／第○条第○項）でなければならない
    - 具体的な条番号・項番号・条例IDを含んではならない

    Args:
        question_template_set:
            抽象表現のみを含む質問テンプレ文のリスト

    Returns:
        入力と同一の質問テンプレリスト（検証済み）

    Raises:
        TemplateValidationError:
            仕様違反が検出された場合
    """
    if not isinstance(question_template_set, list):
        raise TemplateValidationError("question_template_set must be a list of strings")

    for idx, text in enumerate(question_template_set):
        if not isinstance(text, str):
            raise TemplateValidationError(
                f"Question template at index {idx} is not a string"
            )

        # 禁止パターンの検査
        for pattern in _FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                raise TemplateValidationError(
                    "質問テンプレが仕様に違反しています。\n"
                    f"- 質問番号: {idx}\n"
                    f"- 内容: {text}\n"
                    "- 理由: 具体的な条番号・項番号、または条例IDが含まれています。\n"
                    "- 許可される表現: 「この条例」「第○条」「第○条第○項」\n"
                    "- 対応: 具体的な番号を使わず、抽象表現に修正してください。"
                )

        # 許可パターンの存在確認
        if not any(re.search(pattern, text) for pattern in _ALLOWED_PATTERNS):
            raise TemplateValidationError(
                f"No allowed abstract expression found in question template [{idx}]: {text}"
            )

    # A-1 は変換を行わない
    return question_template_set
