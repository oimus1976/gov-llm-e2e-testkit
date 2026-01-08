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
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
import time
import uuid

from playwright.sync_api import Page

from src.answer_probe import wait_for_answer_text
from src.execution.answer_dom_extractor import (
    collect_dom_candidates,
    extract_answer_dom,
)


class ChatPageProtocol(Protocol):
    """Minimal ChatPage interface needed for execution."""

    page: Page

    def submit(self, message: str) -> Any: ...


class SubmitConfirmationError(Exception):
    """Raised when submit cannot be confirmed via submit-state transitions."""


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


SUBMIT_CANDIDATE_SELECTORS: List[str] = [
    'button:has-text("送信")',
    'button[type="submit"]',
    '[role="button"]:has-text("送信")',
    'form button[type="submit"]',
    "form button",
    'button:has-text("Submit")',
]

SUBMIT_BLUE_CLASS = "text-blue-500"
SUBMIT_GRAY_CLASS = "text-gray-400"
SUBMIT_DISABLED_CLASS = "cursor-not-allowed"

SUBMIT_MONITOR_INTERVAL_MS = 500
MESSAGE_INPUT_SELECTOR = "#message"


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
        return MessageState(
            count=0, last_message_id=None, last_markdown_id=None, last_timestamp=None
        )


def _collect_submit_candidates(page: Page) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    seen_html: set[str] = set()

    for selector in SUBMIT_CANDIDATE_SELECTORS:
        locator = page.locator(selector)
        try:
            count = locator.count()
        except Exception:
            count = 0

        for idx in range(count):
            candidate = locator.nth(idx)
            try:
                outer_html = candidate.evaluate("el => el.outerHTML")
            except Exception:
                outer_html = None

            dedup_key = f"{selector}:{outer_html}"
            if dedup_key in seen_html:
                continue
            seen_html.add(dedup_key)

            try:
                is_visible = candidate.is_visible()
            except Exception:
                is_visible = False

            try:
                is_enabled = candidate.is_enabled()
            except Exception:
                is_enabled = False

            results.append(
                {
                    "selector": selector,
                    "index": idx,
                    "is_visible": is_visible,
                    "is_enabled": is_enabled,
                    "disabled_attr": candidate.get_attribute("disabled"),
                    "aria_disabled": candidate.get_attribute("aria-disabled"),
                    "class": candidate.get_attribute("class"),
                    "outer_html": outer_html,
                }
            )

    return results


def _classify_submit_state(candidate: Dict[str, Any]) -> str:
    class_value = candidate.get("class") or ""
    if SUBMIT_BLUE_CLASS in class_value:
        return "blue"
    if SUBMIT_GRAY_CLASS in class_value and SUBMIT_DISABLED_CLASS in class_value:
        return "gray"
    if SUBMIT_GRAY_CLASS in class_value:
        return "gray"
    return "unknown"


def _derive_submit_state(candidates: List[Dict[str, Any]]) -> str:
    if any(_classify_submit_state(c) == "blue" for c in candidates):
        return "blue"
    if any(_classify_submit_state(c) == "gray" for c in candidates):
        return "gray"
    return "unknown"


def _pick_submit_candidate(
    candidates: List[Dict[str, Any]], *, target_state: str
) -> Optional[Dict[str, Any]]:
    for candidate in candidates:
        if _classify_submit_state(candidate) != target_state:
            continue
        if not candidate.get("is_visible"):
            continue
        if target_state == "blue" and not candidate.get("is_enabled"):
            continue
        return candidate
    return None


def _attempt_submit_click(
    page: Page, candidates: List[Dict[str, Any]]
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "attempted": False,
        "clicked": False,
        "selector": None,
        "index": None,
        "error": None,
        "reason": None,
        "candidate_class": None,
    }

    preferred = _pick_submit_candidate(candidates, target_state="blue")
    if not preferred:
        result["reason"] = "no_blue_candidate"
        return result

    result.update(
        {
            "attempted": True,
            "selector": preferred.get("selector"),
            "index": preferred.get("index"),
            "candidate_class": preferred.get("class"),
        }
    )

    try:
        locator = page.locator(preferred["selector"]).nth(int(preferred["index"]))
        if not locator.is_visible():
            result["reason"] = "candidate_not_visible"
            return result
        locator.click()
        result["clicked"] = True
    except Exception as exc:
        result["error"] = str(exc)

    return result


def _read_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _save_submit_abort_artifacts(
    *,
    page: Page,
    output_dir: Path,
    submit_id: str,
    reason: str,
    elapsed_ms: int,
    submit_state: str,
    submit_candidates: List[Dict[str, Any]],
) -> None:
    payload = {
        "submit_id": submit_id,
        "reason": reason,
        "elapsed_ms": elapsed_ms,
        "submit_state": submit_state,
        "submit_candidates": submit_candidates,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "submit_abort.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _capture_html_snapshot(page, output_dir / "submit_abort.html", "submit_abort", [])
    _capture_screenshot(page, output_dir / "submit_abort.png", "submit_abort", [])


def _wait_for_blue_and_click(
    *,
    page: Page,
    output_dir: Path,
    submit_id: str,
    max_wait_ms: int,
    interval_ms: int,
    watchdog_ms: int,
) -> Dict[str, Any]:
    start = time.monotonic()
    last_state: Optional[str] = None
    transition_to_blue_ms: Optional[int] = None
    click_result: Optional[Dict[str, Any]] = None

    while True:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)

        if submit_state == "blue" and last_state != "blue":
            transition_to_blue_ms = elapsed_ms
            click_result = _attempt_submit_click(page, candidates)
            if click_result.get("clicked"):
                return {
                    "submit_state": submit_state,
                    "submit_candidates": candidates,
                    "click_result": click_result,
                    "transition_to_blue_ms": transition_to_blue_ms,
                }

        if submit_state == "blue" and click_result and not click_result.get("clicked"):
            click_result = _attempt_submit_click(page, candidates)
            if click_result.get("clicked"):
                return {
                    "submit_state": submit_state,
                    "submit_candidates": candidates,
                    "click_result": click_result,
                    "transition_to_blue_ms": transition_to_blue_ms,
                }

        if (
            transition_to_blue_ms is not None
            and (click_result is None or not click_result.get("clicked"))
            and elapsed_ms - transition_to_blue_ms >= watchdog_ms
        ):
            _save_submit_abort_artifacts(
                page=page,
                output_dir=output_dir,
                submit_id=submit_id,
                reason="watchdog_no_click_after_blue",
                elapsed_ms=elapsed_ms,
                submit_state=submit_state,
                submit_candidates=candidates,
            )
            raise SubmitConfirmationError("submit click watchdog expired after blue")

        if elapsed_ms >= max_wait_ms:
            _save_submit_abort_artifacts(
                page=page,
                output_dir=output_dir,
                submit_id=submit_id,
                reason="submit_never_reached_blue",
                elapsed_ms=elapsed_ms,
                submit_state=submit_state,
                submit_candidates=candidates,
            )
            raise SubmitConfirmationError("submit never reached blue state")

        last_state = submit_state
        page.wait_for_timeout(interval_ms)


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
    probe_timeout_sec: Optional[int] = None,
) -> SingleQuestionResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_errors: List[str] = []
    after_submit_path = output_dir / "after_submit.html"
    after_ready_html_path = output_dir / "after_answer_ready.html"
    after_ready_png_path = output_dir / "after_answer_ready.png"
    dom_candidates_path = output_dir / "dom_candidates.json"
    after_submit_html = ""
    after_ready_html = ""
    dom_html = ""
    submit_confirmation: Dict[str, Any] = {}

    before_submit_state = _snapshot_message_state(chat_page.page)

    submit_id = str(uuid.uuid4())
    chat_id = _extract_chat_id(chat_page)

    input_box = chat_page.page.locator(MESSAGE_INPUT_SELECTOR)
    input_box.wait_for(state="visible", timeout=max(timeout_sec, 10) * 1000)
    input_box.fill("")
    input_box.fill(question_text)

    submit_ready_max_ms = _read_env_int(
        "SUBMIT_READY_MAX_WAIT_MS", max(timeout_sec, 1) * 1000
    )
    submit_watchdog_ms = _read_env_int("POST_TRANSITION_WATCHDOG_MS", 5000)
    submit_interval_ms = _read_env_int(
        "SUBMIT_MONITOR_INTERVAL_MS", SUBMIT_MONITOR_INTERVAL_MS
    )
    submit_confirmation = _wait_for_blue_and_click(
        page=chat_page.page,
        output_dir=output_dir,
        submit_id=submit_id,
        max_wait_ms=submit_ready_max_ms,
        interval_ms=submit_interval_ms,
        watchdog_ms=submit_watchdog_ms,
    )
    submit_confirmation["signals"] = [
        f"submit_state={submit_confirmation.get('submit_state')}"
    ]
    submit_sent_at = datetime.now(timezone.utc)

    after_submit_html = _capture_html_snapshot(
        chat_page.page, after_submit_path, "after_submit", snapshot_errors
    )

    probe_answer_text = ""
    probe_exception: Optional[Exception] = None

    dom_result = None
    dom_result_observation: Optional[dict] = None
    raw_capture_attempted = False
    raw_capture: Optional[RawCapture] = None

    merged_context = dict(execution_context or {})

    # ------------------------------------------------------------
    # Probe phase (observation only) — must not block DOM extraction
    # ------------------------------------------------------------
    probe_timeout_override = None
    if probe_timeout_sec is not None:
        probe_timeout_override = probe_timeout_sec
    else:
        env_probe_timeout = os.getenv("PROBE_TIMEOUT_SEC")
        if env_probe_timeout:
            try:
                parsed = int(env_probe_timeout)
                if parsed > 0:
                    probe_timeout_override = parsed
            except ValueError:
                probe_timeout_override = None

    try:
        probe_answer_text = wait_for_answer_text(
            page=chat_page.page,
            submit_id=submit_id,
            chat_id=chat_id,
            probe_timeout_sec=probe_timeout_override,
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
            "submit_confirmation": submit_confirmation,
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

    # TEMP/VERIFY: output_dir & answer materialization check
    _safe_write_text(
        output_dir / "verify_answer_materialization.txt",
        json.dumps(
            {
                "output_dir": str(output_dir),
                "output_dir_exists": output_dir.exists(),
                "files_in_output_dir": (
                    sorted(p.name for p in output_dir.iterdir())
                    if output_dir.exists()
                    else []
                ),
                "canonical_answer_len": len(canonical_answer_text),
                "will_write_answer_md": bool(canonical_answer_text),
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
        submit_confirmation=submit_confirmation,
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
