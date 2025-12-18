import pytest

from src.answer_probe import wait_for_answer_text


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
    timeout_sec = config["browser"]["page_timeout_ms"] // 1000

    raw_answer = wait_for_answer_text(
        page=chat_page.page,
        submit_id=submit_id or "N/A",
        chat_id=chat_id,
        timeout_sec=timeout_sec,
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
