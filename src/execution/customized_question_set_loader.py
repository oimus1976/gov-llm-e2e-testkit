from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from src.execution.f8_orchestrator import QuestionSpec


class QuestionSetLoadError(Exception):
    """Raised when customized_question_set.json cannot be loaded or validated."""


@dataclass(frozen=True)
class CustomizedQuestionSet:
    ordinance_id: str
    question_set_id: str
    question_pool: str
    questions: List[QuestionSpec]


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QuestionSetLoadError(f"invalid JSON: {exc}") from exc


def load_customized_question_set(json_path: Path) -> CustomizedQuestionSet:
    """
    Load a customized_question_set.json without modifying its contents.

    Returns a CustomizedQuestionSet with QuestionSpec entries whose
    question_text already includes the ordinance ID prefix.
    """
    if not json_path.is_file():
        raise QuestionSetLoadError(f"question set file not found: {json_path}")

    payload = _load_json(json_path)
    required_keys = ["question_set_id", "source_golden_question_pool", "target_ordinance_id", "questions"]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise QuestionSetLoadError(f"missing required keys: {', '.join(missing)}")

    ordinance_id = str(payload["target_ordinance_id"]).strip()
    question_set_id = str(payload["question_set_id"]).strip()
    question_pool = str(payload["source_golden_question_pool"]).strip()

    if not ordinance_id:
        raise QuestionSetLoadError("target_ordinance_id is empty")
    if not question_set_id:
        raise QuestionSetLoadError("question_set_id is empty")
    if not question_pool:
        raise QuestionSetLoadError("source_golden_question_pool is empty")

    questions_raw = payload.get("questions")
    if not isinstance(questions_raw, list) or not questions_raw:
        raise QuestionSetLoadError("questions must be a non-empty list")

    prefix = f"（条例ID：{ordinance_id}）"
    questions: List[QuestionSpec] = []
    for idx, entry in enumerate(questions_raw):
        if not isinstance(entry, dict):
            raise QuestionSetLoadError(f"questions[{idx}] must be an object")

        question_id = str(entry.get("question_id", "")).strip()
        question_text = str(entry.get("text", "")).strip()
        if not question_id:
            raise QuestionSetLoadError(f"questions[{idx}] is missing question_id")
        if not question_text:
            raise QuestionSetLoadError(f"questions[{idx}] is missing text")

        questions.append(
            QuestionSpec(
                question_id=question_id,
                question_text=f"{prefix}{question_text}",
            )
        )

    return CustomizedQuestionSet(
        ordinance_id=ordinance_id,
        question_set_id=question_set_id,
        question_pool=question_pool,
        questions=questions,
    )
