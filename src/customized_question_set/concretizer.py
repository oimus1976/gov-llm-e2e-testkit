from __future__ import annotations

"""
Concretizer utilities for customized_question_set schema v0.2.

Responsibilities:
- Keep question ordering and identifiers untouched
- Apply vocabulary neutralization so execution inputs are document-type agnostic
"""

from dataclasses import dataclass, replace
from typing import List, Mapping, MutableMapping, Sequence

_VOCAB_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("条例", "法規文書"),
)


@dataclass(frozen=True)
class ConcretizedQuestion:
    """
    Concrete question entry aligned with Execution Input Contract v0.2.
    """

    question_id: str
    text: str
    source_template_id: str


def neutralize_question_text(text: str) -> str:
    """
    Replace document-type specific vocabulary with neutral terms.
    """
    result = text
    for src, dest in _VOCAB_REPLACEMENTS:
        result = result.replace(src, dest)
    return result


def neutralize_questions(
    questions: Sequence[ConcretizedQuestion],
) -> List[ConcretizedQuestion]:
    """
    Apply vocabulary neutralization to all concretized questions.
    """
    return [replace(q, text=neutralize_question_text(q.text)) for q in questions]


def neutralize_execution_input(payload: Mapping[str, object]) -> dict:
    """
    Apply vocabulary neutralization to Execution Input payloads (schema v0.2).

    The payload structure is preserved; only `questions[].text` is rewritten.
    """
    questions = payload.get("questions")
    if isinstance(questions, (str, bytes)) or not isinstance(questions, Sequence):
        raise ValueError("payload must include questions as a sequence")

    normalized_questions: List[MutableMapping[str, object]] = []
    for idx, item in enumerate(questions):
        if not isinstance(item, Mapping):
            raise ValueError(f"questions[{idx}] must be a mapping")
        if "text" not in item:
            raise ValueError(f"questions[{idx}] is missing text")

        rewritten = dict(item)
        rewritten["text"] = neutralize_question_text(str(item["text"]))
        normalized_questions.append(rewritten)

    new_payload = dict(payload)
    new_payload["questions"] = normalized_questions
    return new_payload
