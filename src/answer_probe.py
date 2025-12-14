# src/answer_probe.py
"""
pytest-facing Answer Detection API (v0.1r).

Operational binding for Spec_answer_probe_api_v0.1,
reflecting current probe implementation constraints.

Key points:
- Requires Playwright sync Page as execution context.
- Delegates all completion semantics to probe.
- Surfaces observable facts only (raw answer or exceptions).
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
    submit_id: str,
    chat_id: str,
    timeout_sec: int = 60,
) -> str:
    """
    Wait for an answer text via Answer Detection Layer (probe).

    Parameters
    ----------
    page : Page
        Playwright sync Page used as probe execution context.
    submit_id : str
        Client-generated submit identifier.
        (Kept for pytest-side correlation; not passed to probe in v0.1r.)
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

    # NOTE:
    # submit_id is intentionally unused in v0.1r.
    # It is kept to preserve API contract and future extensibility.

    try:
        summary: Dict[str, Any] = run_graphql_probe(
            page=page,
            chat_id=chat_id,
            capture_seconds=timeout_sec,
        )
    except Exception as exc:
        raise ProbeExecutionError("probe execution failed") from exc

    # ------------------------------------------------------------------
    # Answer selection (summary -> pytest API mapping)
    # ------------------------------------------------------------------

    rest_answer = summary.get("rest_answer")
    if rest_answer:
        return rest_answer

    graphql_answer = summary.get("graphql_answer")
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
