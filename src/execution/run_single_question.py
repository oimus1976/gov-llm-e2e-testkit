# src/execution/run_single_question.py
"""
Single-question execution engine (UI submit + answer detection + DOM-based answer extraction).

Responsibilities:
- isolate pytest-independent execution steps used by F4 / F8
- perform submit → wait_for_answer_text (probe: completion signal)
- extract answer text from UI DOM (non-evaluative selection) as canonical answer_text
- return observed facts only (no evaluation)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Protocol

from playwright.sync_api import Page

from src.answer_probe import wait_for_answer_text
from src.execution.answer_dom_extractor import extract_answer_dom


class ChatPageProtocol(Protocol):
    """Minimal ChatPage interface needed for execution."""

    page: Page

    def submit(self, message: str) -> Any: ...


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
    try:
        url = chat_page.page.url
    except Exception:
        return "N/A"
    parts = str(url).split("/")
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
    # TEMP: UI readiness stabilization (remove after confirmation)
    chat_page.page.wait_for_timeout(1000)

    submit_receipt = chat_page.submit(question_text)
    submit_id = _extract_submit_id(submit_receipt)
    chat_id = _extract_chat_id(chat_page)

    # Probe (observation only)
    probe_answer_text = wait_for_answer_text(
        page=chat_page.page,
        submit_id=submit_id,
        chat_id=chat_id,
        timeout_sec=timeout_sec,
    )

    # DOM-based canonical extraction
    dom_html = chat_page.page.content()
    dom_result = extract_answer_dom(dom_html, question_text)

    # --- Observed facts (no evaluation, no print) ---
    dom_text_len = len(dom_result.text or "")

    merged_context = dict(execution_context or {})
    merged_context.update(
        {
            "probe_answer_text": probe_answer_text,
            "dom_extraction": {
                "selected": dom_result.selected,
                "reason": dom_result.reason,
                "text_len": dom_text_len,
            },
        }
    )

    canonical_answer_text = (
        dom_result.text if dom_result.selected and dom_result.text else ""
    )

    return SingleQuestionResult(
        question_id=question_id,
        ordinance_id=ordinance_id,
        question_text=question_text,
        profile=profile,
        output_dir=output_dir,
        submit_id=submit_id,
        chat_id=chat_id,
        answer_text=canonical_answer_text,
        execution_context=merged_context,
    )
