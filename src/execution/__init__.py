"""Execution engine package (single-question I/F and F8 runner)."""

from src.execution.run_single_question import (
    ChatPageProtocol,
    SingleQuestionResult,
    run_single_question,
)
from src.execution.run_f8_set1 import (
    F8QuestionOutcome,
    F8_SET1_QUESTIONS,
    run_f8_set1,
)
from src.execution.f8_orchestrator import (
    ExecutionProfile,
    OrdinanceSpec,
    QuestionSpec,
    ResultStatus,
    RunSummary,
    run_f8_collection,
)

__all__ = [
    "ChatPageProtocol",
    "SingleQuestionResult",
    "run_single_question",
    "F8QuestionOutcome",
    "F8_SET1_QUESTIONS",
    "run_f8_set1",
    "ExecutionProfile",
    "OrdinanceSpec",
    "QuestionSpec",
    "ResultStatus",
    "RunSummary",
    "run_f8_collection",
]
