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
) -> Dict[str, Any]:
    start = perf_counter()
    timeline: List[Dict[str, Any]] = []
    first_gray_ms: Optional[int] = None
    first_blue_ms: Optional[int] = None
    transitions: List[str] = []
    saw_gray = False
    baseline_input = _read_input_value(page) if monitor_input else ""
    allow_clear = monitor_input and bool(baseline_input)

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)
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

        if first_gray_ms is None and submit_state == "gray":
            first_gray_ms = elapsed_ms
            saw_gray = True

        if first_blue_ms is None and submit_state == "blue":
            first_blue_ms = elapsed_ms

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
        "transitions": transitions,
        "timeline": timeline,
    }


def _run_probe_for_question(
    page: Page,
    *,
    run_id: str,
    question: Dict[str, str],
    probe_root: Path,
    chat_timeout: int,
) -> None:
    question_dir = probe_root / question["label"]
    question_dir.mkdir(parents=True, exist_ok=True)

    prepared_text = _prepare_question_text(question["text"])
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
    _fill_question_input(page, chat_timeout, prepared_text)

    before_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="before_submit",
    )
    _write_json(question_dir / f"{question['label']}_before_submit.json", before_payload)
    page.screenshot(path=str(question_dir / f"{question['label']}_screenshot_before_submit.png"))
    (question_dir / f"{question['label']}_page_full.html").write_text(
        page.content(), encoding="utf-8"
    )

    click_result = _attempt_submit_click(page)
    if not click_result.get("clicked"):
        _abort_probe(
            page,
            question_dir=question_dir,
            question_label=question["label"],
            reason="submit_click_failed",
            payload={"click_result": click_result},
        )
    after_click_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="after_click",
        click_result=click_result,
    )
    _write_json(question_dir / f"{question['label']}_after_click.json", after_click_payload)
    page.screenshot(path=str(question_dir / f"{question['label']}_screenshot_after_click.png"))

    monitor_payload = _monitor_submit_cycle(
        page,
        interval_ms=MONITOR_INTERVAL_MS,
        max_wait_ms=MAX_WAIT_MS,
        question_dir=question_dir,
        question_label=question["label"],
        monitor_input=question["label"] == "Q15",
    )
    _write_json(question_dir / f"{question['label']}_submit_class_timeline.json", monitor_payload)

    after_wait_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="after_wait",
        click_result=click_result,
    )
    _write_json(question_dir / f"{question['label']}_after_wait.json", after_wait_payload)
    page.screenshot(path=str(question_dir / f"{question['label']}_screenshot_after_wait.png"))


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
            _run_probe_for_question(
                page,
                run_id=run_id,
                question=question,
                probe_root=probe_root,
                chat_timeout=getattr(ChatPage(page, config), "timeout", 15000),
            )

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
