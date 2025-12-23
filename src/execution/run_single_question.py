# src/execution/run_single_question.py
"""
Single-question execution engine (UI submit + answer detection).

Responsibilities:
- isolate pytest-independent execution steps used by F4 / F8
- perform submit → wait_for_answer_text without evaluation
- return observed facts only
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Protocol

from playwright.sync_api import Page

from src.answer_probe import wait_for_answer_text


class ChatPageProtocol(Protocol):
    """Minimal ChatPage interface needed for execution."""

    page: Page

    def submit(self, message: str) -> Any:
        ...


@dataclass(frozen=True)
class SingleQuestionResult:
    question_id: str
    ordinance_id: str
    question_text: str
    profile: str
    output_dir: Path
    submit_id: str
    chat_id: str
    answer_text: str
    execution_context: Optional[dict]


def _extract_submit_id(submit_result: Any) -> str:
    """
    Derive submit_id from SubmitReceipt or dict.
    Falls back to 'N/A' when unavailable (no guessing).
    """
    if hasattr(submit_result, "submit_id"):
        value = getattr(submit_result, "submit_id")
        if isinstance(value, str):
            return value

    if isinstance(submit_result, dict):
        value = submit_result.get("submit_id")
        if isinstance(value, str):
            return value

    return "N/A"


def _extract_chat_id(chat_page: ChatPageProtocol) -> str:
    """Extract chat_id from page URL; fall back to N/A on failure."""
    try:
        url = chat_page.page.url
    except Exception:
        return "N/A"

    parts = str(url).split("/")
    if not parts:
        return "N/A"
    return parts[-1] or "N/A"


def run_single_question(
    *,
    chat_page: ChatPageProtocol,
    question_text: str,
    question_id: str,
    ordinance_id: str,
    output_dir: Path,
    profile: str,
    execution_context: Optional[dict] = None,
    timeout_sec: int = 60,
) -> SingleQuestionResult:
    """
    Execute one question via UI and probe for an answer.

    Notes:
    - pytest dependencies are intentionally excluded.
    - No evaluation or formatting is performed here.
    """
    submit_receipt = chat_page.submit(question_text)
    submit_id = _extract_submit_id(submit_receipt)
    chat_id = _extract_chat_id(chat_page)

    answer_text = wait_for_answer_text(
        page=chat_page.page,
        submit_id=submit_id,
        chat_id=chat_id,
        timeout_sec=timeout_sec,
    )

    return SingleQuestionResult(
        question_id=question_id,
        ordinance_id=ordinance_id,
        question_text=question_text,
        profile=profile,
        output_dir=output_dir,
        submit_id=submit_id,
        chat_id=chat_id,
        answer_text=answer_text,
        execution_context=execution_context,
    )
