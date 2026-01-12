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

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
import time

from playwright.sync_api import Page

from src.answer_probe import wait_for_answer_text
from src.execution.answer_dom_extractor import (
    collect_dom_candidates,
    extract_answer_dom,
)

NON_F10A_TIMEOUT_MULTIPLIER = 2
F10A_BLUE_WAIT_TIMEOUT_SEC = float("inf")


class ChatPageProtocol(Protocol):
    """Minimal ChatPage interface needed for execution."""

    page: Page

    def submit(self, message: str) -> Any: ...


class SubmitConfirmationError(Exception):
    """Raised when submit success cannot be confirmed via DOM signals."""


@dataclass(frozen=True)
class MessageState:
    count: int
    last_message_id: Optional[int]
    last_markdown_id: Optional[int]
    last_timestamp: Optional[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "last_message_id": self.last_message_id,
            "last_markdown_id": self.last_markdown_id,
            "last_timestamp": self.last_timestamp,
        }


@dataclass(frozen=True)
class SingleQuestionResult:
    question_id: str
    ordinance_id: str
    question_text: str
    profile: str
    output_dir: Path
    submit_id: str
    submit_sent_at: datetime
    submit_confirmation: Dict[str, Any]
    chat_id: str
    answer_text: str
    extracted_status: str
    raw_capture: Optional["RawCapture"]
    raw_capture_attempted: bool
    anchor_dom_selector: Optional[str]
    execution_context: Optional[dict]
    message_state_before: MessageState
    message_state_after: MessageState


@dataclass(frozen=True)
class RawCapture:
    raw_html: str
    raw_text: str
    html_path: Path
    text_path: Path
    meta_path: Path
    anchor_dom_selector: Optional[str]
    selection_reason: str
    extracted_status: str


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


def _snapshot_message_state(page: Page) -> MessageState:
    try:
        data = page.evaluate(
            """() => {
                const parseMax = (selector, prefix) => {
                    const ids = Array.from(document.querySelectorAll(selector))
                        .map(el => el.id || "")
                        .filter(id => typeof id === "string" && id.startsWith(prefix))
                        .map(id => parseInt(id.slice(prefix.length), 10))
                        .filter(n => Number.isFinite(n));
                    if (!ids.length) return null;
                    return Math.max(...ids);
                };

                const items = Array.from(document.querySelectorAll("div[id^='message-item-']"));
                const lastTimestamp = items.length
                    ? items[items.length - 1].getAttribute("data-timestamp")
                    : null;

                return {
                    count: items.length,
                    last_message_id: parseMax("div[id^='message-item-']", "message-item-"),
                    last_markdown_id: parseMax("div[id^='markdown-']", "markdown-"),
                    last_timestamp: lastTimestamp,
                };
            }"""
        )
        return MessageState(
            count=int(data.get("count", 0)),
            last_message_id=data.get("last_message_id"),
            last_markdown_id=data.get("last_markdown_id"),
            last_timestamp=data.get("last_timestamp"),
        )
    except Exception:
        return MessageState(count=0, last_message_id=None, last_markdown_id=None, last_timestamp=None)


def _has_increment(current: Optional[int], baseline: Optional[int]) -> bool:
    if current is None:
        return False
    if baseline is None:
        return current >= 0
    return current > baseline


def _wait_for_submit_confirmation(
    page: Page, before_state: MessageState, *, timeout_sec: int
) -> Dict[str, Any]:
    """
    Wait for DOM-level evidence that the submit was accepted.
    Returns a confirmation payload with observed states.
    Raises SubmitConfirmationError on timeout.
    """
    deadline = time.time() + max(timeout_sec, 1)

    try:
        send_button = page.locator("#chat-send-button")
    except Exception:
        send_button = None

    while time.time() < deadline:
        state = _snapshot_message_state(page)
        primary_signals: List[str] = []
        secondary_signals: List[str] = []

        if state.count > before_state.count:
            primary_signals.append("message_count_increased")
        if _has_increment(state.last_message_id, before_state.last_message_id):
            primary_signals.append("message_id_advanced")
        if _has_increment(state.last_markdown_id, before_state.last_markdown_id):
            primary_signals.append("markdown_id_advanced")

        if send_button is not None:
            try:
                if send_button.is_disabled():
                    secondary_signals.append("send_button_disabled")
            except Exception:
                pass

        if primary_signals:
            return {
                "before": before_state.as_dict(),
                "after": state.as_dict(),
                "signals": primary_signals + secondary_signals,
            }

        page.wait_for_timeout(200)

    raise SubmitConfirmationError(
        "submit confirmation not observed via DOM signals",
    )


def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _capture_html_snapshot(
    page: Page, path: Path, label: str, errors: List[str]
) -> str:
    try:
        html = page.content()
        _safe_write_text(path, html)
        return html
    except Exception as exc:
        errors.append(f"{label} html capture failed: {exc}")
        return ""


def _capture_screenshot(page: Page, path: Path, label: str, errors: List[str]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(path), full_page=True)
    except Exception as exc:
        errors.append(f"{label} screenshot failed: {exc}")


def _persist_raw_capture(
    *,
    output_dir: Path,
    raw_html: str,
    raw_text: str,
    anchor_dom_selector: Optional[str],
    selection_reason: str,
    extracted_status: str,
    errors: List[str],
) -> Optional[RawCapture]:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = output_dir / "raw_answer.html"
        text_path = output_dir / "raw_answer.txt"
        meta_path = output_dir / "raw_capture_meta.json"

        _safe_write_text(html_path, raw_html or "")
        _safe_write_text(text_path, raw_text or "")

        meta = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source": "answer_dom_extractor",
            "anchor_dom_selector": anchor_dom_selector,
            "selection_reason": selection_reason,
            "extracted_status": extracted_status,
            "lengths": {"html": len(raw_html or ""), "text": len(raw_text or "")},
        }
        _safe_write_text(meta_path, json.dumps(meta, ensure_ascii=False, indent=2))

        return RawCapture(
            raw_html=raw_html or "",
            raw_text=raw_text or "",
            html_path=html_path,
            text_path=text_path,
            meta_path=meta_path,
            anchor_dom_selector=anchor_dom_selector,
            selection_reason=selection_reason,
            extracted_status=extracted_status,
        )
    except Exception as exc:  # pragma: no cover - forensics best-effort
        errors.append(f"raw capture persist failed: {exc}")
        return None


def _write_dom_candidates_file(
    *,
    path: Path,
    html: str,
    submit_id: str,
    chat_id: str,
    observation: Optional[dict],
    errors: List[str],
) -> None:
    try:
        candidates, candidate_errors = collect_dom_candidates(html)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "run_single_question",
            "checkpoint": "after_answer_ready",
            "submit_id": submit_id,
            "chat_id": chat_id,
            "html_available": bool(html),
            "candidates": candidates,
            "errors": errors + candidate_errors,
        }

        if observation is not None:
            payload["extraction"] = {
                "selected": observation.get("selected"),
                "selected_n": observation.get("selected_n"),
                "parity": observation.get("parity"),
                "reason": observation.get("reason"),
                "text_len": observation.get("text_len"),
                "extracted_status": observation.get("extracted_status"),
            }

        _safe_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))
    except Exception:
        # Forensics must never block execution.
        return


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
    f10a_mode: bool = False,
    submit_blue_timeout_sec: float = 10.0,
    submit_ack_timeout_sec: float = 3.0,
    submit_timeline_poll_ms: int = 100,
) -> SingleQuestionResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    effective_timeout_sec = (
        max(int(timeout_sec * NON_F10A_TIMEOUT_MULTIPLIER), 1)
        if not f10a_mode
        else timeout_sec
    )
    effective_submit_blue_timeout_sec = (
        F10A_BLUE_WAIT_TIMEOUT_SEC if f10a_mode else submit_blue_timeout_sec
    )

    snapshot_errors: List[str] = []
    after_submit_path = output_dir / "after_submit.html"
    after_ready_html_path = output_dir / "after_answer_ready.html"
    after_ready_png_path = output_dir / "after_answer_ready.png"
    dom_candidates_path = output_dir / "dom_candidates.json"
    after_submit_html = ""
    after_ready_html = ""
    dom_html = ""
    submit_confirmation: Dict[str, Any] = {}

    # TEMP: UI readiness stabilization (remove after confirmation)
    chat_page.page.wait_for_timeout(1000)
    # ------------------------------------------------------------

    before_submit_state = _snapshot_message_state(chat_page.page)

    submit_receipt = chat_page.submit(
        question_text,
        wait_for_blue=f10a_mode,
        blue_wait_timeout_sec=effective_submit_blue_timeout_sec,
        ack_timeout_sec=submit_ack_timeout_sec,
        timeline_poll_ms=submit_timeline_poll_ms,
    )
    submit_id = _extract_submit_id(submit_receipt)
    submit_sent_at = getattr(submit_receipt, "sent_at", datetime.now(timezone.utc))
    chat_id = _extract_chat_id(chat_page)
    submit_diagnostics = getattr(submit_receipt, "diagnostics", {})

    merged_context = dict(execution_context or {})
    if submit_diagnostics:
        merged_context["submit_diagnostics"] = dict(submit_diagnostics)
        _safe_write_text(
            output_dir / "submit_diagnostics.json",
            json.dumps(submit_diagnostics, ensure_ascii=True, indent=2),
        )

    if not getattr(submit_receipt, "ui_ack", False):
        reason = (
            submit_diagnostics.get("reason")
            if isinstance(submit_diagnostics, dict)
            else None
        )
        message = "submit acknowledgment not observed (ui_ack=False)"
        if reason:
            message = f"{message}: {reason}"
        error = SubmitConfirmationError(message)
        error.submit_receipt = submit_receipt
        if f10a_mode:
            merged_context.update(
                {
                    "ungenerated": {
                        "reason": message,
                        "type": type(error).__name__,
                    },
                    "submit_confirmation": {},
                }
            )
            final_message_state = _snapshot_message_state(chat_page.page)
            return SingleQuestionResult(
                question_id=question_id,
                ordinance_id=ordinance_id,
                question_text=question_text,
                profile=profile,
                output_dir=output_dir,
                submit_id=submit_id,
                submit_sent_at=submit_sent_at,
                submit_confirmation={},
                chat_id=chat_id,
                answer_text="",
                extracted_status="INVALID",
                raw_capture=None,
                raw_capture_attempted=False,
                anchor_dom_selector=None,
                execution_context=merged_context,
                message_state_before=before_submit_state,
                message_state_after=final_message_state,
            )
        raise error

    try:
        submit_confirmation = _wait_for_submit_confirmation(
            chat_page.page,
            before_submit_state,
            timeout_sec=min(effective_timeout_sec, 20),
        )
    except SubmitConfirmationError as exc:
        exc.submit_receipt = submit_receipt
        if f10a_mode:
            merged_context.update(
                {
                    "ungenerated": {
                        "reason": str(exc),
                        "type": type(exc).__name__,
                    },
                    "submit_confirmation": {},
                }
            )
            final_message_state = _snapshot_message_state(chat_page.page)
            return SingleQuestionResult(
                question_id=question_id,
                ordinance_id=ordinance_id,
                question_text=question_text,
                profile=profile,
                output_dir=output_dir,
                submit_id=submit_id,
                submit_sent_at=submit_sent_at,
                submit_confirmation={},
                chat_id=chat_id,
                answer_text="",
                extracted_status="INVALID",
                raw_capture=None,
                raw_capture_attempted=False,
                anchor_dom_selector=None,
                execution_context=merged_context,
                message_state_before=before_submit_state,
                message_state_after=final_message_state,
            )
        raise

    after_submit_html = _capture_html_snapshot(
        chat_page.page, after_submit_path, "after_submit", snapshot_errors
    )

    probe_answer_text = ""
    probe_exception: Optional[Exception] = None

    dom_result = None
    dom_result_observation: Optional[dict] = None
    raw_capture_attempted = False
    raw_capture: Optional[RawCapture] = None

    # ------------------------------------------------------------
    # Probe phase (observation only) — must not block DOM extraction
    # ------------------------------------------------------------
    try:
        probe_answer_text = wait_for_answer_text(
            page=chat_page.page,
            submit_id=submit_id,
            chat_id=chat_id,
            timeout_sec=effective_timeout_sec,
        )
    except Exception as exc:
        probe_exception = exc
        merged_context["probe_exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }

        # TEMP/VERIFY: capture root exception from probe
        _safe_write_text(
            output_dir / "verify_dom_exception.txt",
            f"{type(exc).__name__}: {exc}",
        )

    # ------------------------------------------------------------
    # DOM snapshot + extraction phase (always)
    # ------------------------------------------------------------
    try:
        after_ready_html = _capture_html_snapshot(
            chat_page.page, after_ready_html_path, "after_answer_ready", snapshot_errors
        )
        _capture_screenshot(
            chat_page.page, after_ready_png_path, "after_answer_ready", snapshot_errors
        )

        dom_html = after_ready_html or chat_page.page.content()

        # TEMP/VERIFY: capture pre-extraction state
        _safe_write_text(
            output_dir / "verify_reached_extract.txt",
            "before extract_answer_dom",
        )

        dom_result = extract_answer_dom(dom_html, question_text)

        # TEMP/VERIFY: capture post-extraction state
        _safe_write_text(
            output_dir / "verify_after_extract.txt",
            f"dom_result is None = {dom_result is None}",
        )

        if dom_result is not None:
            dom_result_observation = {
                "candidates": dom_result.observation.candidates,
                "selected": dom_result.observation.selected,
                "selected_n": dom_result.observation.selected_n,
                "parity": dom_result.observation.parity,
                "reason": dom_result.observation.reason,
                "text_len": dom_result.observation.text_len,
                "errors": dom_result.observation.errors,
                "extracted_status": dom_result.extracted_status,
                "anchor_dom_selector": dom_result.anchor_dom_selector,
            }

            raw_capture_attempted = True
            raw_capture = _persist_raw_capture(
                output_dir=output_dir,
                raw_html=dom_result.raw_html,
                raw_text=dom_result.raw_text,
                anchor_dom_selector=dom_result.anchor_dom_selector,
                selection_reason=dom_result.observation.reason,
                extracted_status=dom_result.extracted_status,
                errors=snapshot_errors,
            )
    except Exception as exc:
        # DOM extraction failure must not block overall execution.
        snapshot_errors.append(f"dom extraction failed: {type(exc).__name__}: {exc}")

        if not after_ready_html:
            after_ready_html = _capture_html_snapshot(
                chat_page.page,
                after_ready_html_path,
                "after_answer_ready-on-dom-error",
                snapshot_errors,
            )
        _capture_screenshot(
            chat_page.page,
            after_ready_png_path,
            "after_answer_ready-on-dom-error",
            snapshot_errors,
        )
        if not dom_html:
            dom_html = after_ready_html

    # ------------------------------------------------------------
    # Finalize: ensure snapshot + candidates are saved
    # ------------------------------------------------------------
    if not after_ready_html:
        after_ready_html = _capture_html_snapshot(
            chat_page.page,
            after_ready_html_path,
            "after_answer_ready-finalize",
            snapshot_errors,
        )

    _write_dom_candidates_file(
        path=dom_candidates_path,
        html=dom_html or after_ready_html or after_submit_html,
        submit_id=submit_id,
        chat_id=chat_id,
        observation=dom_result_observation,
        errors=snapshot_errors,
    )

    final_message_state = _snapshot_message_state(chat_page.page)
    submit_validation_failures: List[str] = []
    if final_message_state.count <= before_submit_state.count:
        submit_validation_failures.append(
            "no new message observed after submit (count did not increase)"
        )
    if (
        final_message_state.last_markdown_id is not None
        and before_submit_state.last_markdown_id is not None
        and final_message_state.last_markdown_id <= before_submit_state.last_markdown_id
    ):
        submit_validation_failures.append("markdown id did not advance after submit")
    if dom_result_observation is not None:
        selected_n = dom_result_observation.get("selected_n")
        if (
            isinstance(selected_n, int)
            and final_message_state.last_markdown_id is not None
            and selected_n != final_message_state.last_markdown_id
        ):
            submit_validation_failures.append(
                "extracted markdown is not the latest message after submit"
            )

    if submit_validation_failures:
        message = "; ".join(submit_validation_failures)
        error = SubmitConfirmationError(message)
        error.submit_receipt = submit_receipt
        error.submit_confirmation = submit_confirmation
        if not f10a_mode:
            raise error
        merged_context["ungenerated"] = {
            "reason": message,
            "type": type(error).__name__,
        }

    # --- Observed facts (no evaluation, no print) ---
    dom_observation = dom_result_observation or {
        "candidates": [],
        "selected": False,
        "selected_n": None,
        "parity": None,
        "anchor_dom_selector": None,
        "reason": "dom extraction unavailable",
        "text_len": 0,
        "errors": ["dom extraction unavailable"],
        "extracted_status": "INVALID",
    }

    merged_context.update(
        {
            "probe_answer_text": probe_answer_text,
            "dom_extraction": dom_observation,
            "submit_confirmation": {
                **submit_confirmation,
                "final_after": final_message_state.as_dict(),
            },
        }
    )

    extracted_status = (
        dom_result.extracted_status
        if dom_result is not None
        else dom_observation.get("extracted_status", "INVALID")
    )

    canonical_answer_text = (
        dom_result.text
        if dom_result is not None and extracted_status == "VALID" and dom_result.text
        else ""
    )

    # TEMP/VERIFY: diagnose extraction result
    _safe_write_text(
        output_dir / "verify_extraction_state.txt",
        json.dumps(
            {
                "dom_result_is_none": dom_result is None,
                "dom_result_status": getattr(dom_result, "extracted_status", None),
                "dom_result_text_len": (
                    len(dom_result.text) if dom_result and dom_result.text else None
                ),
                "final_extracted_status": extracted_status,
                "canonical_answer_len": len(canonical_answer_text),
                "probe_exception_type": (
                    type(probe_exception).__name__
                    if probe_exception is not None
                    else None
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
    )

    return SingleQuestionResult(
        question_id=question_id,
        ordinance_id=ordinance_id,
        question_text=question_text,
        profile=profile,
        output_dir=output_dir,
        submit_id=submit_id,
        submit_sent_at=submit_sent_at,
        submit_confirmation={
            **submit_confirmation,
            "final_after": final_message_state.as_dict(),
        },
        chat_id=chat_id,
        answer_text=canonical_answer_text,
        extracted_status=extracted_status,
        raw_capture=raw_capture,
        raw_capture_attempted=raw_capture_attempted,
        anchor_dom_selector=dom_observation.get("anchor_dom_selector"),
        execution_context=merged_context,
        message_state_before=before_submit_state,
        message_state_after=final_message_state,
    )
