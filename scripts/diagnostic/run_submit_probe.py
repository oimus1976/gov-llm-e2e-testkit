"""
Diagnostic: submit button state probe (Q3 -> Q15 -> Q1) per Implementation Brief.

- Standalone script (no changes to collection/orchestrator).
- Uses submit class transitions as the primary gate.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page, sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage


RUN_ID_PREFIX = "submit_probe"
ORDINANCE_ID = "k518RG00000022"

QUESTIONS = [
    {
        "label": "Q3",
        "question_id": "GQPA:v1.1:Q3:a1",
        "text": "第1条の内容を要約してください。",
    },
    {
        "label": "Q15",
        "question_id": "GQPA:v1.1:Q15",
        "text": "法規文書を「目的→手続き→義務→例外→附則」の順に再構成してください。",
    },
    {
        "label": "Q1",
        "question_id": "GQPA:v1.1:Q1",
        "text": "この法規文書の目的を分かりやすく説明してください。",
    },
]

SUBMIT_CANDIDATE_SELECTORS: List[str] = [
    "button:has-text(\"送信\")",
    "button[type=\"submit\"]",
    "[role=\"button\"]:has-text(\"送信\")",
    "form button[type=\"submit\"]",
    "form button",
    "button:has-text(\"Submit\")",
]

SUBMIT_BLUE_CLASS = "text-blue-500"
SUBMIT_GRAY_CLASS = "text-gray-400"
SUBMIT_DISABLED_CLASS = "cursor-not-allowed"

GENERATION_INDICATOR_SELECTORS: List[str] = [
    "[data-testid*=\"loading\"]",
    "[aria-busy=\"true\"]",
    "[role=\"status\"]",
    ".loading",
    ".spinner",
]

# Safety cap for abort only; completion never relies on this value.
MAX_WAIT_MS = 300000
MONITOR_INTERVAL_MS = 500
SUBMIT_READY_MAX_WAIT_MS = 120000
POST_TRANSITION_WATCHDOG_MS = 5000


def _now_jst_iso() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _collect_submit_candidates(page: Page) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    seen_html: set[str] = set()

    for selector in SUBMIT_CANDIDATE_SELECTORS:
        locator = page.locator(selector)
        count = locator.count()

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
    return "unknown"


def _derive_submit_state(candidates: List[Dict[str, Any]]) -> str:
    # Priority: blue (ready) > gray (busy) > unknown.
    if any(_classify_submit_state(c) == "blue" for c in candidates):
        return "blue"
    if any(_classify_submit_state(c) == "gray" for c in candidates):
        return "gray"
    return "unknown"


def _collect_generation_indicators(page: Page) -> List[Dict[str, Any]]:
    indicators: List[Dict[str, Any]] = []

    for selector in GENERATION_INDICATOR_SELECTORS:
        locator = page.locator(selector)
        count = locator.count()
        sample_html: Optional[str] = None

        if count > 0:
            try:
                sample_html = locator.first.evaluate("el => el.outerHTML")
            except Exception:
                sample_html = None

        try:
            first_visible = locator.first.is_visible()
        except Exception:
            first_visible = False

        indicators.append(
            {
                "selector": selector,
                "count": count,
                "first_visible": first_visible,
                "sample_outer_html": sample_html,
            }
        )

    return indicators


def _snapshot_dom_state(
    page: Page,
    *,
    run_id: str,
    question_label: str,
    question_id: str,
    question_text: str,
    stage: str,
    click_result: Optional[Dict[str, Any]] = None,
    submit_state: Optional[str] = None,
) -> Dict[str, Any]:
    submit_candidates = _collect_submit_candidates(page)
    return {
        "ts": _now_jst_iso(),
        "run_id": run_id,
        "ordinance_id": ORDINANCE_ID,
        "question_label": question_label,
        "question_id": question_id,
        "question_text": question_text,
        "stage": stage,
        "url": page.url,
        "submit_candidates": submit_candidates,
        "submit_state": submit_state or _derive_submit_state(submit_candidates),
        "generation_indicators": _collect_generation_indicators(page),
        "click_result": click_result,
    }


<<<<<<< HEAD
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
=======
def _save_artifacts(
    page: Page,
    *,
    target_dir: Path,
    base_name: str,
    payload: Dict[str, Any],
) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    _write_json(target_dir / f"{base_name}.json", payload)
    page.screenshot(path=str(target_dir / f"{base_name}.png"))
    (target_dir / f"{base_name}.html").write_text(page.content(), encoding="utf-8")


def _derive_submit_state(candidates: List[Dict[str, Any]]) -> str:
    for candidate in candidates:
        cls = candidate.get("class") or ""
        if "text-blue-500" in cls:
            return "blue"
    for candidate in candidates:
        cls = candidate.get("class") or ""
        if "text-gray-400" in cls and "cursor-not-allowed" in cls:
            return "gray"
    return "unknown"
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)


def _attempt_submit_click(page: Page) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ts": _now_jst_iso(),
        "attempted": False,
        "clicked": False,
        "selector": None,
        "index": None,
        "error": None,
        "reason": None,
        "candidate_class": None,
    }

    candidates = _collect_submit_candidates(page)
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


def _prepare_chat(page: Page, config: Dict[str, Any]) -> None:
    login = LoginPage(page, config)
    login.open()
    login.login()

    selector = ChatSelectPage(page, config)
    ai_name = config.get("chat_name", "プライベートナレッジ")
    selector.open_ai(ai_name)


def _fill_question_input(page: Page, chat_timeout: int, text: str) -> None:
    input_box = page.locator(ChatPage.MESSAGE_INPUT)
    input_box.wait_for(state="visible", timeout=chat_timeout)
    input_box.fill("")
    input_box.fill(text)


def _prepare_question_text(text: str) -> str:
    replaced = text.replace("条例", "法規文書")
    return f"法規文書ID：{ORDINANCE_ID} に基づき、次の法規文書について回答してください。{replaced}"


<<<<<<< HEAD
def _read_input_value(page: Page) -> str:
    try:
        return page.locator(ChatPage.MESSAGE_INPUT).input_value()
    except Exception:
        return ""


def _abort_probe(
    page: Page,
    *,
    question_dir: Path,
    question_label: str,
    reason: str,
    payload: Dict[str, Any],
) -> None:
    payload["reason"] = reason
    _write_json(question_dir / f"{question_label}_abort.json", payload)
    page.screenshot(path=str(question_dir / f"{question_label}_screenshot_abort.png"))
    (question_dir / f"{question_label}_page_abort.html").write_text(
        page.content(), encoding="utf-8"
    )
    raise RuntimeError(reason)


def _validate_transitions(transitions: List[str]) -> bool:
    allowed_sequences = [
        ["blue", "gray", "blue"],
        ["gray", "blue"],
    ]
    for allowed in allowed_sequences:
        if transitions == allowed[: len(transitions)]:
            return True
    return False


def _monitor_submit_cycle(
    page: Page,
    *,
    question_dir: Path,
    question_label: str,
    interval_ms: int,
    max_wait_ms: int,
    monitor_input: bool,
=======
def _monitor_transition_and_fire_action(
    page: Page,
    *,
    max_wait_ms: int,
    interval_ms: int,
    watchdog_ms: int,
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
) -> Dict[str, Any]:
    start = perf_counter()
    timeline: List[Dict[str, Any]] = []
    first_gray_ms: Optional[int] = None
    first_blue_ms: Optional[int] = None
<<<<<<< HEAD
    transitions: List[str] = []
    saw_gray = False
    baseline_input = _read_input_value(page) if monitor_input else ""
    allow_clear = monitor_input and bool(baseline_input)
=======
    transition_to_blue_ms: Optional[int] = None
    action_result: Optional[Dict[str, Any]] = None
    watchdog_trigger: Optional[Dict[str, Any]] = None
    action_delay_ms: Optional[int] = None
    last_state: Optional[str] = None
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)
<<<<<<< HEAD
        if not transitions or submit_state != transitions[-1]:
            transitions.append(submit_state)
            if not _validate_transitions(transitions):
                _abort_probe(
                    page,
                    question_dir=question_dir,
                    question_label=question_label,
                    reason="submit_class_not_monotonic",
                    payload={
                        "elapsed_ms": elapsed_ms,
                        "transitions": transitions,
                        "timeline": timeline,
                    },
                )
=======

        if first_gray_ms is None and submit_state == "gray":
            first_gray_ms = elapsed_ms

        if first_blue_ms is None and submit_state == "blue":
            first_blue_ms = elapsed_ms

        if (
            submit_state == "blue"
            and transition_to_blue_ms is None
            and (last_state == "gray" or last_state is None)
        ):
            transition_to_blue_ms = elapsed_ms
            action_result = _attempt_submit_click(page)
            action_result["fired_ms"] = elapsed_ms
            action_delay_ms = elapsed_ms - (transition_to_blue_ms or elapsed_ms)

        timeline.append(
            {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "submit_state": submit_state,
                "submit_candidates": candidates,
            }
        )

        if (
            transition_to_blue_ms is not None
            and action_result is None
            and elapsed_ms - transition_to_blue_ms >= watchdog_ms
        ):
            watchdog_trigger = {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "since_transition_ms": elapsed_ms - transition_to_blue_ms,
                "reason": "blue_state_without_action",
            }
            break

        if action_result is not None:
            break

        if elapsed_ms >= max_wait_ms:
            watchdog_trigger = {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "reason": "transition_timeout",
            }
            break

        last_state = submit_state
        page.wait_for_timeout(interval_ms)

    return {
        "duration_ms": int((perf_counter() - start) * 1000),
        "interval_ms": interval_ms,
        "first_gray_ms": first_gray_ms,
        "first_blue_ms": first_blue_ms,
        "transition_to_blue_ms": transition_to_blue_ms,
        "action_result": action_result,
        "action_delay_ms": action_delay_ms,
        "watchdog": watchdog_trigger,
        "timeline": timeline,
    }


def _monitor_submit_classes(
    page: Page,
    *,
    duration_ms: int,
    interval_ms: int,
) -> Dict[str, Any]:
    start = perf_counter()
    timeline: List[Dict[str, Any]] = []
    first_gray_ms: Optional[int] = None
    first_blue_ms: Optional[int] = None

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)

        if first_gray_ms is None and submit_state == "gray":
            first_gray_ms = elapsed_ms
            saw_gray = True

        if first_blue_ms is None and submit_state == "blue":
            first_blue_ms = elapsed_ms

<<<<<<< HEAD
        input_value = _read_input_value(page) if monitor_input else ""
        if monitor_input:
            if allow_clear and baseline_input and not input_value:
                baseline_input = ""
                allow_clear = False
            elif input_value != baseline_input and input_value.strip():
                _abort_probe(
                    page,
                    question_dir=question_dir,
                    question_label=question_label,
                    reason="input_overwritten",
                    payload={
                        "elapsed_ms": elapsed_ms,
                        "baseline_input": baseline_input,
                        "current_input": input_value,
                        "transitions": transitions,
                        "timeline": timeline,
                    },
                )

=======
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
        timeline.append(
            {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "submit_state": submit_state,
                "submit_candidates": candidates,
                "input_value": input_value if monitor_input else None,
            }
        )

        if saw_gray and submit_state == "blue":
            break

        if elapsed_ms >= max_wait_ms:
            _abort_probe(
                page,
                question_dir=question_dir,
                question_label=question_label,
                reason="submit_not_returned_blue",
                payload={
                    "elapsed_ms": elapsed_ms,
                    "transitions": transitions,
                    "timeline": timeline,
                },
            )

        page.wait_for_timeout(interval_ms)

    return {
        "max_wait_ms": max_wait_ms,
        "interval_ms": interval_ms,
        "first_gray_ms": first_gray_ms,
        "first_blue_ms": first_blue_ms,
<<<<<<< HEAD
        "transitions": transitions,
=======
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
        "timeline": timeline,
    }


def _wait_for_submit_ready(
    page: Page,
    *,
    max_wait_ms: int,
    interval_ms: int,
) -> Dict[str, Any]:
    start = perf_counter()
    timeline: List[Dict[str, Any]] = []
    first_gray_ms: Optional[int] = None

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)

        if first_gray_ms is None and submit_state == "gray":
            first_gray_ms = elapsed_ms

        timeline.append(
            {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "submit_state": submit_state,
                "submit_candidates": candidates,
            }
        )

        if submit_state == "blue":
            return {
                "state": "blue",
                "first_gray_ms": first_gray_ms,
                "timeline": timeline,
                "waited_ms": elapsed_ms,
            }

        if elapsed_ms >= max_wait_ms:
            return {
                "state": "timeout",
                "first_gray_ms": first_gray_ms,
                "timeline": timeline,
                "waited_ms": elapsed_ms,
            }

        page.wait_for_timeout(interval_ms)


def _run_probe_for_question(
    page: Page,
    *,
    run_id: str,
    question: Dict[str, str],
    probe_root: Path,
    chat_timeout: int,
) -> bool:
    question_dir = probe_root / question["label"]
    question_dir.mkdir(parents=True, exist_ok=True)

    prepared_text = _prepare_question_text(question["text"])
<<<<<<< HEAD
    pre_candidates = _collect_submit_candidates(page)
    pre_state = _derive_submit_state(pre_candidates)
    if pre_state != "blue":
        _abort_probe(
            page,
            question_dir=question_dir,
            question_label=question["label"],
            reason="submit_not_blue_before_input",
            payload={"submit_state": pre_state, "submit_candidates": pre_candidates},
        )
=======
    precondition_snapshot = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="precondition_check",
    )

    precondition_results = {
        "message_input_visible": False,
        "submit_candidate_count": 0,
        "submit_class_readable": False,
    }

    try:
        input_box = page.locator(ChatPage.MESSAGE_INPUT)
        input_box.wait_for(state="visible", timeout=chat_timeout)
        precondition_results["message_input_visible"] = input_box.is_visible()
    except Exception:
        precondition_results["message_input_visible"] = False

    submit_candidates = precondition_snapshot["submit_candidates"]
    precondition_results["submit_candidate_count"] = len(submit_candidates)
    precondition_results["submit_class_readable"] = any(
        candidate.get("class") is not None for candidate in submit_candidates
    )

    precondition_payload = {
        **precondition_snapshot,
        "precondition_results": precondition_results,
    }
    _save_artifacts(
        page,
        target_dir=question_dir,
        base_name=f"{question['label']}_precondition",
        payload=precondition_payload,
    )

    if not all(
        (
            precondition_results["message_input_visible"],
            precondition_results["submit_candidate_count"] > 0,
            precondition_results["submit_class_readable"],
        )
    ):
        abort_payload = {
            "reason": "precondition_failed",
            "details": precondition_results,
            "run_id": run_id,
            "question_label": question["label"],
        }
        _write_json(question_dir / f"{question['label']}_abort.json", abort_payload)
        return False

>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
    _fill_question_input(page, chat_timeout, prepared_text)

    before_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="before_submit",
    )
    _save_artifacts(
        page,
        target_dir=question_dir,
        base_name=f"{question['label']}_before_submit",
        payload=before_payload,
    )

<<<<<<< HEAD
    click_result = _attempt_submit_click(page)
    if not click_result.get("clicked"):
        _abort_probe(
            page,
            question_dir=question_dir,
            question_label=question["label"],
            reason="submit_click_failed",
            payload={"click_result": click_result},
        )
=======
    transition_monitor = _monitor_transition_and_fire_action(
        page,
        max_wait_ms=SUBMIT_READY_MAX_WAIT_MS,
        interval_ms=MONITOR_INTERVAL_MS,
        watchdog_ms=POST_TRANSITION_WATCHDOG_MS,
    )
    _write_json(
        question_dir / f"{question['label']}_transition_monitor.json",
        transition_monitor,
    )

    click_result = transition_monitor.get("action_result") or {}

>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
    after_click_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="after_click",
        click_result=click_result,
    )
    _save_artifacts(
        page,
        target_dir=question_dir,
        base_name=f"{question['label']}_after_click",
        payload=after_click_payload,
    )

    transition_watchdog_reason: Optional[str] = None
    if transition_monitor.get("watchdog"):
        transition_watchdog_reason = transition_monitor["watchdog"].get("reason", "watchdog_triggered")
    elif not click_result.get("clicked"):
        transition_watchdog_reason = "action_not_clicked"
    elif (
        transition_monitor.get("action_delay_ms") is None
        or transition_monitor.get("action_delay_ms", 0) > POST_TRANSITION_WATCHDOG_MS
    ):
        transition_watchdog_reason = "action_delay_exceeded"

    if transition_watchdog_reason:
        watchdog_payload = {
            "reason": transition_watchdog_reason,
            "monitor": transition_monitor,
            "run_id": run_id,
            "question_label": question["label"],
        }
        _save_artifacts(
            page,
            target_dir=question_dir,
            base_name=f"{question['label']}_transition_watchdog",
            payload={
                "watchdog": transition_monitor.get("watchdog"),
                "action_delay_ms": transition_monitor.get("action_delay_ms"),
                "click_result": click_result,
                "dom_state": _snapshot_dom_state(
                    page,
                    run_id=run_id,
                    question_label=question["label"],
                    question_id=question["question_id"],
                    question_text=prepared_text,
                    stage="transition_watchdog",
                ),
            },
        )
        _write_json(question_dir / f"{question['label']}_abort.json", watchdog_payload)
        return False

    monitor_payload = _monitor_submit_cycle(
        page,
        interval_ms=MONITOR_INTERVAL_MS,
<<<<<<< HEAD
        max_wait_ms=MAX_WAIT_MS,
        question_dir=question_dir,
        question_label=question["label"],
        monitor_input=question["label"] == "Q15",
=======
>>>>>>> 6faa4c0 (wip: align submit-state timeline with click/watchdog decision baseline)
    )
    _write_json(question_dir / f"{question['label']}_submit_class_timeline.json", monitor_payload)

    if monitor_payload.get("first_blue_ms") is None:
        abort_payload = {
            "reason": "submit_never_recovered_to_blue",
            "monitor": {
                "duration_ms": monitor_payload.get("duration_ms"),
                "first_gray_ms": monitor_payload.get("first_gray_ms"),
                "timeline_length": len(monitor_payload.get("timeline", [])),
            },
            "run_id": run_id,
            "question_label": question["label"],
        }
        _save_artifacts(
            page,
            target_dir=question_dir,
            base_name=f"{question['label']}_abort_after_monitor",
            payload=_snapshot_dom_state(
                page,
                run_id=run_id,
                question_label=question["label"],
                question_id=question["question_id"],
                question_text=prepared_text,
                stage="abort_after_monitor",
                click_result=click_result,
            ),
        )
        _write_json(question_dir / f"{question['label']}_abort.json", abort_payload)
        return False

    after_wait_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="after_wait",
        click_result=click_result,
    )
    _save_artifacts(
        page,
        target_dir=question_dir,
        base_name=f"{question['label']}_after_wait",
        payload=after_wait_payload,
    )

    readiness_after_generation = _wait_for_submit_ready(
        page,
        max_wait_ms=SUBMIT_READY_MAX_WAIT_MS,
        interval_ms=MONITOR_INTERVAL_MS,
    )
    _write_json(
        question_dir / f"{question['label']}_wait_for_blue_after_generation.json",
        readiness_after_generation,
    )

    if readiness_after_generation.get("state") != "blue":
        abort_payload = {
            "reason": "submit_not_ready_after_generation",
            "readiness": readiness_after_generation,
            "run_id": run_id,
            "question_label": question["label"],
        }
        _save_artifacts(
            page,
            target_dir=question_dir,
            base_name=f"{question['label']}_abort_after_generation",
            payload=_snapshot_dom_state(
                page,
                run_id=run_id,
                question_label=question["label"],
                question_id=question["question_id"],
                question_text=prepared_text,
                stage="abort_after_generation",
            ),
        )
        _write_json(question_dir / f"{question['label']}_abort.json", abort_payload)
        return False

    return True


def main() -> int:
    run_id = f"{RUN_ID_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_root = Path("out") / run_id
    probe_root = output_root / "probe"
    probe_root.mkdir(parents=True, exist_ok=True)

    config, _ = load_env()

    playwright = sync_playwright().start()
    browser = None
    context = None

    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        _prepare_chat(page, config)

        for question in QUESTIONS:
            success = _run_probe_for_question(
                page,
                run_id=run_id,
                question=question,
                probe_root=probe_root,
                chat_timeout=getattr(ChatPage(page, config), "timeout", 15000),
            )
            if not success:
                return 1

        return 0

    finally:
        try:
            if context is not None:
                context.close()
        except Exception:
            pass

        try:
            if browser is not None:
                browser.close()
        except Exception:
            pass

        try:
            playwright.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
