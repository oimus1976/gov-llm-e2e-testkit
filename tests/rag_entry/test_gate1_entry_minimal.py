import pytest
from time import perf_counter
from typing import Any, Dict, List, Optional


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


def _collect_submit_candidates(page) -> List[Dict[str, Any]]:
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
                    "class": candidate.get_attribute("class"),
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


def _attempt_submit_click(page, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
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


def _monitor_gray_to_blue_and_click(
    page,
    *,
    max_wait_ms: int,
    interval_ms: int,
) -> Dict[str, Any]:
    start = perf_counter()
    saw_gray = False
    last_state: Optional[str] = None
    transition_to_blue_ms: Optional[int] = None
    action_result: Dict[str, Any] = {
        "attempted": False,
        "clicked": False,
        "selector": None,
        "index": None,
        "error": None,
        "reason": None,
        "candidate_class": None,
        "fired_ms": None,
    }

    while True:
        elapsed_ms = int((perf_counter() - start) * 1000)
        candidates = _collect_submit_candidates(page)
        submit_state = _derive_submit_state(candidates)

        if submit_state == "gray":
            saw_gray = True

        if (
            saw_gray
            and submit_state == "blue"
            and transition_to_blue_ms is None
            and last_state != "blue"
        ):
            transition_to_blue_ms = elapsed_ms
            action_result = _attempt_submit_click(page, candidates)
            action_result["fired_ms"] = elapsed_ms
            break

        if elapsed_ms >= max_wait_ms:
            action_result["reason"] = "transition_timeout"
            break

        last_state = submit_state
        page.wait_for_timeout(interval_ms)

    return {
        "saw_gray": saw_gray,
        "transition_to_blue_ms": transition_to_blue_ms,
        "action_result": action_result,
    }


def test_gate1_entry_minimal(chat_page, env_config):
    """
    Gate1 minimal entry check: rely on submit gray→blue transition semantics only.
    """
    _config, _ = env_config
    question = "Gate1 entry minimal path check"

    chat_page.submit(question)

    transition_result = _monitor_gray_to_blue_and_click(
        chat_page.page,
        max_wait_ms=120000,
        interval_ms=500,
    )

    action = transition_result["action_result"]

    assert transition_result["saw_gray"], "submit did not enter gray state"
    assert transition_result["transition_to_blue_ms"] is not None, "submit did not return to blue"
    assert action["attempted"], "submit click was not attempted on blue transition"
    assert action["clicked"], f"submit click failed: {action.get('error') or action.get('reason')}"
