# tests/f9/a/resolution/test_user_input_resolver.py

import pytest

from src.f9.a.resolution.user_input_resolver import (
    resolve_by_user_input,
    UserInputResolutionError,
)


def test_a4_ok_article_only():
    """
    条のみ指定。
    条候補に存在し、項候補がない場合は paragraph=None で確定。
    """
    candidates = {
        "article_candidates": [3, 7],
        "paragraphs_by_article": {
            3: [],
            7: [],
        },
    }

    article, paragraph = resolve_by_user_input(
        article_input=3,
        paragraph_input=None,
        candidates=candidates,
    )

    assert article == 3
    assert paragraph is None


def test_a4_ok_article_and_paragraph():
    """
    条・項ともに指定。
    両方が候補に含まれていれば確定できる。
    """
    candidates = {
        "article_candidates": [3],
        "paragraphs_by_article": {
            3: [1, 2, 3],
        },
    }

    article, paragraph = resolve_by_user_input(
        article_input=3,
        paragraph_input=2,
        candidates=candidates,
    )

    assert article == 3
    assert paragraph == 2


def test_a4_ng_invalid_article():
    """
    条番号が候補に含まれない場合はエラー。
    """
    candidates = {
        "article_candidates": [3],
        "paragraphs_by_article": {
            3: [1],
        },
    }

    with pytest.raises(UserInputResolutionError) as excinfo:
        resolve_by_user_input(
            article_input=5,
            paragraph_input=None,
            candidates=candidates,
        )

    msg = str(excinfo.value)
    assert "条番号" in msg
    assert "候補" in msg


def test_a4_ng_invalid_paragraph():
    """
    項番号が候補に含まれない場合はエラー。
    """
    candidates = {
        "article_candidates": [3],
        "paragraphs_by_article": {
            3: [1, 2],
        },
    }

    with pytest.raises(UserInputResolutionError) as excinfo:
        resolve_by_user_input(
            article_input=3,
            paragraph_input=5,
            candidates=candidates,
        )

    msg = str(excinfo.value)
    assert "項番号" in msg
    assert "候補" in msg


def test_a4_ok_skip_paragraph_when_none():
    """
    項候補が存在しても、paragraph_input=None は許可される。
    （条のみ指定の質問を想定）
    """
    candidates = {
        "article_candidates": [3],
        "paragraphs_by_article": {
            3: [1, 2, 3],
        },
    }

    article, paragraph = resolve_by_user_input(
        article_input=3,
        paragraph_input=None,
        candidates=candidates,
    )

    assert article == 3
    assert paragraph is None
