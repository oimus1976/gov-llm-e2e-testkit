import pytest
import os

from src.answer_probe import wait_for_answer_text


def _resolve_probe_timeout(config: dict) -> int:
    """
    Determine probe timeout with precedence:
    1) config["probe_timeout_sec"]
    2) config["probe_capture_seconds"]
    3) env PROBE_TIMEOUT_SEC
    4) default: 90
    """
    candidates = [
        config.get("probe_timeout_sec"),
        config.get("probe_capture_seconds"),
        os.getenv("PROBE_TIMEOUT_SEC"),
    ]

    for value in candidates:
        if value is None:
            continue
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed

    return 90


def test_gate1_entry_minimal(chat_page, env_config):
    """
    Gate1 minimal entry check: verify submit→probe pipeline returns raw answer and context.
    Quality evaluation is intentionally out of scope.
    """
    config, _ = env_config
    question = "Gate1 entry minimal path check"

    receipt = chat_page.submit(question)

    submit_id = None
    if hasattr(receipt, "submit_id"):
        submit_id = receipt.submit_id
    elif isinstance(receipt, dict):
        submit_id = receipt.get("submit_id")

    chat_id = chat_page.page.url.split("/")[-1]
    timeout_sec = _resolve_probe_timeout(config)

    raw_answer = wait_for_answer_text(
        page=chat_page.page,
        submit_id=submit_id or "N/A",
        chat_id=chat_id,
        probe_timeout_sec=timeout_sec,
    )

    execution_context = {
        "chat_id": chat_id,
        "submit_id": submit_id or "N/A",
        "profile": config.get("profile"),
    }

    assert raw_answer is not None, "raw answer not obtained"
    assert execution_context is not None, "execution context not obtained"
    assert execution_context["chat_id"] is not None, "chat_id missing in execution context"
    assert execution_context["submit_id"] is not None, "submit_id missing in execution context"
