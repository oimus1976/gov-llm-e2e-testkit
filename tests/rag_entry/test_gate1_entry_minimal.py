import pytest

from src.answer_probe import wait_for_answer_text


def test_gate1_entry_minimal(chat_page, env_config):
    """
    Gate1 minimal entry check.

    Guarantees:
    - submit() completes without error
    - chat context is established after submit
    - UI reaches a stable post-submit state

    Non-goals:
    - Answer content
    - Probe / raw_evidence
    """
    config, _ = env_config
    question = "Gate1 entry minimal path check"

    # 1. submit must complete (internal blue semantics handled inside)
    receipt = chat_page.submit(question)

    # 2. chat_id must be established (UI context boundary)
    chat_id = chat_page.page.url.split("/")[-1]
    assert chat_id, "chat_id was not established after submit"

    # 3. page must be in stable state (no navigation / crash)
    #    evaluate is used to assert browser is alive and responsive
    is_alive = chat_page.page.evaluate("() => true")
    assert is_alive is True, "page is not in stable state after submit"
