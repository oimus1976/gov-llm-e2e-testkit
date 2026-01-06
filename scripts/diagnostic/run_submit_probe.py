"""
Diagnostic: submit button state probe (Q3 -> Q15 -> Q1) per Implementation Brief.

- Standalone script (no changes to collection/orchestrator).
- Captures DOM state before/after submit attempts plus class transition timeline.
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

GENERATION_INDICATOR_SELECTORS: List[str] = [
    "[data-testid*=\"loading\"]",
    "[aria-busy=\"true\"]",
    "[role=\"status\"]",
    ".loading",
    ".spinner",
]

WAIT_AFTER_SUBMIT_MS = 30000
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
) -> Dict[str, Any]:
    return {
        "ts": _now_jst_iso(),
        "run_id": run_id,
        "ordinance_id": ORDINANCE_ID,
        "question_label": question_label,
        "question_id": question_id,
        "question_text": question_text,
        "stage": stage,
        "url": page.url,
        "submit_candidates": _collect_submit_candidates(page),
        "generation_indicators": _collect_generation_indicators(page),
        "click_result": click_result,
    }


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

    for selector in SUBMIT_CANDIDATE_SELECTORS:
        locator = page.locator(selector)
        count = locator.count()

        for idx in range(count):
            candidate = locator.nth(idx)

            try:
                candidate_class = candidate.get_attribute("class") or ""
            except Exception:
                candidate_class = ""

            if "text-blue-500" not in candidate_class:
                continue

            result.update(
                {
                    "attempted": True,
                    "selector": selector,
                    "index": idx,
                    "candidate_class": candidate_class,
                }
            )

            try:
                if not candidate.is_visible():
                    result["reason"] = "candidate_not_visible"
                    return result
                candidate.click()
                result["clicked"] = True
            except Exception as exc:
                result["error"] = str(exc)

            return result

    result["reason"] = "no_blue_candidate"
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


def _monitor_submit_classes(
    page: Page,
    *,
    duration_ms: int,
    interval_ms: int,
    enable_transition_click: bool,
    already_clicked: bool,
) -> Dict[str, Any]:
    start = perf_counter()
    timeline: List[Dict[str, Any]] = []
    first_gray_ms: Optional[int] = None
    first_blue_ms: Optional[int] = None
    transition_click: Optional[Dict[str, Any]] = None

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)

        if first_gray_ms is None and any(
            (c.get("class") or "").find("text-gray-400") != -1
            and (c.get("class") or "").find("cursor-not-allowed") != -1
            for c in candidates
        ):
            first_gray_ms = elapsed_ms

        if first_blue_ms is None and any(
            "text-blue-500" in (c.get("class") or "") for c in candidates
        ):
            first_blue_ms = elapsed_ms

            if enable_transition_click and transition_click is None and not already_clicked:
                transition_click = _attempt_submit_click(page)

        timeline.append(
            {
                "ts": _now_jst_iso(),
                "elapsed_ms": elapsed_ms,
                "submit_candidates": candidates,
            }
        )

        if elapsed_ms >= duration_ms:
            break

        page.wait_for_timeout(interval_ms)

    return {
        "duration_ms": duration_ms,
        "interval_ms": interval_ms,
        "first_gray_ms": first_gray_ms,
        "first_blue_ms": first_blue_ms,
        "transition_click": transition_click,
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

    monitor_payload = _monitor_submit_classes(
        page,
        duration_ms=WAIT_AFTER_SUBMIT_MS,
        interval_ms=MONITOR_INTERVAL_MS,
        enable_transition_click=question["label"] == "Q15",
        already_clicked=click_result.get("clicked", False),
    )
    _write_json(question_dir / f"{question['label']}_submit_class_timeline.json", monitor_payload)

    after_wait_payload = _snapshot_dom_state(
        page,
        run_id=run_id,
        question_label=question["label"],
        question_id=question["question_id"],
        question_text=prepared_text,
        stage="after_wait",
        click_result=monitor_payload.get("transition_click") or click_result,
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
