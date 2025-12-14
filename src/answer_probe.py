# src/answer_probe.py
"""
pytest-facing Answer Detection API.

This module provides a minimal adapter between pytest-based tests
and the existing Answer Detection Layer (probe v0.2).

- Completion semantics are fully delegated to probe.
- This module does NOT inspect UI / DOM.
- This module does NOT redefine probe semantics.
- This module surfaces observable facts only.
"""

from typing import Any, Dict

from playwright.sync_api import Page

from scripts.probe_v0_2 import run_graphql_probe


# ----------------------------------------------------------------------
# Exceptions (pytest-facing, fact-based)
# ----------------------------------------------------------------------


class AnswerTimeoutError(Exception):
    """
    Raised when no relevant probe evidence is observed
    within the bounded waiting period.
    """


class AnswerNotAvailableError(Exception):
    """
    Raised when probe evidence exists, but no answer text
    (REST nor GraphQL) could be obtained.
    """


class ProbeExecutionError(Exception):
    """
    Raised when probe execution itself fails.
    The original exception is chained as the cause.
    """


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def wait_for_answer_text(
    *,
    page: Page,
    chat_id: str,
    timeout_sec: int = 60,
) -> str:
    """
    Wait for an answer text via Answer Detection Layer (probe).

    Parameters
    ----------
    page : Page
        Playwright Page object (used by probe only).
    chat_id : str
        Chat boundary identifier.
    timeout_sec : int, optional
        Upper bound for waiting (seconds).
        Completion semantics are defined by probe, not here.

    Returns
    -------
    str
        Raw answer text.

    Raises
    ------
    AnswerTimeoutError
        When no relevant probe evidence is observed.
    AnswerNotAvailableError
        When probe evidence exists but answer text is unavailable.
    ProbeExecutionError
        When probe execution itself fails.
    """

    try:
        summary: Dict[str, Any] = run_graphql_probe(
            page=page,
            chat_id=chat_id,
            capture_seconds=timeout_sec,
        )
    except Exception as exc:
        raise ProbeExecutionError("probe execution failed") from exc

    # ------------------------------------------------------------------
    # Answer selection (mapping is strictly defined by specification)
    # ------------------------------------------------------------------

    rest_answer = summary.get("rest_answer")
    graphql_answer = summary.get("graphql_answer")

    if rest_answer:
        return rest_answer

    if graphql_answer:
        return graphql_answer

    # ------------------------------------------------------------------
    # Exception mapping (observable facts only)
    # ------------------------------------------------------------------

    has_post = summary.get("has_post", False)
    has_get = summary.get("has_get", False)
    has_graphql = summary.get("has_graphql", False)

    if has_post or has_get or has_graphql:
        raise AnswerNotAvailableError(
            "probe observed related events, but answer text is not available"
        )

    raise AnswerTimeoutError("no probe evidence observed within bounded waiting period")
