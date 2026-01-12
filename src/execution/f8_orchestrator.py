"""F8 orchestrator (canonical, DOM-based answer capture).

Responsibilities:
- iterate ordinances × questions (continue-on-error)
- wait for completion via probe (observation only)
- capture UI DOM as raw answer source
- generate answer.md (artifact of record)

Non-goals:
- evaluation, heuristics, retries, or optimization
- embedding set-specific logic
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from playwright.sync_api import Error as PlaywrightError

from src.answer_probe import (
    AnswerNotAvailableError,
    AnswerTimeoutError,
    ProbeExecutionError,
)
from src.execution.run_single_question import (
    ChatPageProtocol,
    RawCapture,
    SubmitConfirmationError,
    run_single_question,
)


class ResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NO_ANSWER = "NO_ANSWER"
    TIMEOUT = "TIMEOUT"
    UI_ERROR = "UI_ERROR"
    EXEC_ERROR = "EXEC_ERROR"
    UNGENERATED = "UNGENERATED"


@dataclass(frozen=True)
class OrdinanceSpec:
    ordinance_id: str
    display_name: str


@dataclass(frozen=True)
class QuestionSpec:
    question_id: str
    question_text: str


@dataclass(frozen=True)
class ExecutionProfile:
    profile_name: str
    run_mode: str = "collect-only"


@dataclass(frozen=True)
class RunSummary:
    aborted: bool
    fatal_error: Optional[str]
    executed_at: datetime


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_execution_context_file(
    *, question_dir: Path, execution_context: Mapping[str, Any], result_status: ResultStatus, result_reason: Optional[str]
) -> None:
    payload = {
        "result_status": result_status.value,
        "result_reason": result_reason or "",
        "execution_context": execution_context,
    }
    path = question_dir / "execution_context.json"
    if path.exists():
        raise FileExistsError(f"execution_context already exists: {path}")
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def _fs_safe_segment(value: str) -> str:
    sanitized = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)
    sanitized = sanitized.strip("_")
    return sanitized or "question"


def _is_fatal_state(chat_page: ChatPageProtocol) -> bool:
    try:
        return chat_page.page.is_closed()
    except Exception:
        return False


def _validate_required_keys(
    data: Mapping[str, object], keys: Sequence[str], *, label: str
) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise KeyError(f"{label} missing required keys: {', '.join(missing)}")


def _write_answer_markdown(
    *,
    question_dir: Path,
    question: QuestionSpec,
    ordinance: OrdinanceSpec,
    execution_profile: ExecutionProfile,
    run_id: str,
    executed_at: datetime,
    qommons_config: Mapping[str, Any],
    knowledge_scope: str,
    knowledge_files: Sequence[Mapping[str, str]],
    ordinance_set: str,
    question_pool: str,
    execution: Mapping[str, Any],
    extracted_answer_text: str,
    execution_context: Mapping[str, Any],
    raw_capture: Optional[RawCapture],
    raw_capture_attempted: bool,
    result_status: ResultStatus,
    result_reason: Optional[str],
    aborted_run: bool,
    citations: Sequence[str],
    observation_notes: Optional[Sequence[str]],
    submit_id: str,
    chat_id: str,
    extracted_status: str,
    submit_sent_at: datetime,
    submitted_question_text: str,
    submit_confirmation: Mapping[str, Any],
) -> Path:
    fs_question_id = _fs_safe_segment(question.question_id)
    _validate_required_keys(
        qommons_config,
        ["model", "web_search", "region", "ui_mode"],
        label="qommons_config",
    )
    _validate_required_keys(
        execution,
        ["retry", "temperature", "max_tokens"],
        label="execution",
    )

    question_dir.mkdir(parents=True, exist_ok=True)
    output_path = question_dir / f"{fs_question_id}_answer.md"
    if output_path.exists():
        raise FileExistsError(f"answer already exists: {output_path}")

    lines = [
        "---",
        "schema_version: v0.1r+",
        f"run_id: {run_id}",
        f"executed_at: {executed_at.isoformat()}",
        f"extracted_status: {extracted_status if extracted_status in {'VALID', 'INVALID'} else 'INVALID'}",
        f"result_status: {result_status.value}",
        f"result_reason: {result_reason or ''}",
        f"aborted_run: {aborted_run}",
        f"raw_capture: {raw_capture_attempted}",
        "qommons:",
        f"  model: {qommons_config['model']}",
        f"  web_search: {qommons_config['web_search']}",
        f"  region: {qommons_config['region']}",
        f"  ui_mode: {qommons_config['ui_mode']}",
        "knowledge:",
        f"  scope: {knowledge_scope}",
        "  files:",
    ]

    for item in knowledge_files:
        _validate_required_keys(item, ["type", "name"], label="knowledge_files")
        lines.append("    - type: {type}".format(type=item["type"]))
        lines.append("      name: {name}".format(name=item["name"]))

    lines.extend(
        [
            "target:",
            f"  ordinance_id: {ordinance.ordinance_id}",
            f"  ordinance_set: {ordinance_set}",
            f"  question_id: {question.question_id}",
            f"  question_fs_id: {fs_question_id}",
            f"  question_pool: {question_pool}",
            "execution:",
            f"  retry: {execution['retry']}",
            f"  temperature: {execution['temperature']}",
            f"  max_tokens: {execution['max_tokens']}",
            "execution_profile:",
            f"  profile_name: {execution_profile.profile_name}",
            f"  run_mode: {execution_profile.run_mode}",
            "---",
            "",
            "## Question",
            "",
            question.question_text,
            "",
            "## Answer (Extracted)",
            "",
            "```text",
            extracted_answer_text or "",
            "```",
            "",
            "## Answer (Raw)",
            "",
            "```text",
            raw_capture.raw_html if raw_capture is not None else "",
            "```",
            "",
            "## Citations (As Displayed)",
            "",
        ]
    )

    if citations:
        lines.extend(f"- {c}" for c in citations)
    else:
        lines.append("- (none observed)")

    lines.extend(
        [
            "",
            "## Observation Notes (Optional)",
            "",
        ]
    )

    if observation_notes:
        lines.extend(f"- {note}" for note in observation_notes)
    else:
        lines.append("- (none)")

    # --- Observed DOM extraction metadata (non-evaluative) ---
    dom = (execution_context or {}).get("dom_extraction", {})
    dom_text_len = dom.get("text_len")
    if not isinstance(dom_text_len, int):
        try:
            dom_text_len = int(dom_text_len) if dom_text_len is not None else None
        except Exception:
            dom_text_len = None
    if dom_text_len is None:
        dom_text_len = len(extracted_answer_text) if extracted_answer_text else 0
    # --- /Observed DOM extraction metadata ---

    lines.extend(
        [
            "",
            "## Metadata (Observed)",
            "",
            f"- submit_id: {submit_id or 'N/A'}",
            f"- chat_id: {chat_id or 'N/A'}",
            f"- submit_timestamp: {submit_sent_at.isoformat() if submit_sent_at else 'N/A'}",
            f"- profile: {execution_profile.profile_name}",
            f"- output_dir: {question_dir}",
            f"- dom_selected: {dom.get('selected', 'N/A')}",
            f"- dom_reason: {dom.get('reason', 'N/A')}",
            f"- anchor_dom_selector: {dom.get('anchor_dom_selector', 'N/A')}",
            f"- dom_text_len: {dom_text_len}",
            f"- dom_selected_n: {dom.get('selected_n', 'N/A')}",
            f"- dom_parity: {dom.get('parity', 'N/A')}",
            f"- dom_candidates: {dom.get('candidates', 'N/A')}",
            f"- dom_errors: {dom.get('errors', [])}",
            f"- raw_answer_html: {raw_capture.html_path if raw_capture else 'N/A'}",
            f"- raw_answer_txt: {raw_capture.text_path if raw_capture else 'N/A'}",
            f"- raw_capture_meta: {raw_capture.meta_path if raw_capture else 'N/A'}",
        ]
    )

    submission_signals = (
        ", ".join(submit_confirmation.get("signals", []))
        if isinstance(submit_confirmation, Mapping)
        else ""
    )
    lines.extend(
        [
            "",
            "## Submission Trace",
            "",
            f"- submit_signals: {submission_signals or 'N/A'}",
            f"- message_state_before: {submit_confirmation.get('before') if isinstance(submit_confirmation, Mapping) else 'N/A'}",
            f"- message_state_after: {submit_confirmation.get('after') if isinstance(submit_confirmation, Mapping) else 'N/A'}",
            f"- message_state_final: {submit_confirmation.get('final_after') if isinstance(submit_confirmation, Mapping) else 'N/A'}",
            "",
            "### Submitted Question (echo)",
            "",
            "```text",
            submitted_question_text or "",
            "```",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def run_f8_collection(
    *,
    chat_page: ChatPageProtocol,
    ordinances: Sequence[OrdinanceSpec],
    questions: Sequence[QuestionSpec],
    execution_profile: ExecutionProfile,
    run_id: str,
    qommons_config: Mapping[str, Any],
    knowledge_scope: str,
    knowledge_files: Sequence[Mapping[str, str]],
    ordinance_set: str,
    output_root: Path,
    execution: Mapping[str, Any],
    question_pool: str = "Golden_Question_Pool_A_v1.1",
    citations_fetcher: Optional[Callable[[ChatPageProtocol], Iterable[str]]] = None,
    observation_notes: Optional[Sequence[str]] = None,
    timeout_sec: int = 60,
    f10a_mode: bool = False,
    submit_blue_timeout_sec: float = 10.0,
    submit_ack_timeout_sec: float = 3.0,
    submit_timeline_poll_ms: int = 100,
) -> RunSummary:
    """
    Canonical orchestrator for F8 (DOM-based capture).

    Control is continue-on-error. Abort only when browser/page is unusable.
    """
    executed_at = datetime.now(timezone.utc)
    run_root = Path(output_root)

    aborted = False
    fatal_error: Optional[str] = None
    fatal_submit_error: Optional[Exception] = None

    for ordinance in ordinances:
        for question in questions:
            fs_question_id = _fs_safe_segment(question.question_id)
            question_dir = (
                run_root / "answer" / ordinance.ordinance_id / fs_question_id
            )

            status = ResultStatus.EXEC_ERROR
            reason: Optional[str] = None
            raw_capture: Optional[RawCapture] = None
            raw_capture_attempted = False
            skip_answer_write = False

            submit_id = "N/A"
            chat_id = "N/A"
            submit_sent_at: Optional[datetime] = None
            submit_confirmation: Mapping[str, Any] = {}
            extracted_answer_text = ""
            extracted_status = "INVALID"
            execution_context: Optional[dict] = None

            try:
                # SingleQuestion execution (submit + probe + DOM extraction)
                # No evaluation here; exceptions are mapped to ResultStatus.
                try:
                    result = run_single_question(
                        chat_page=chat_page,
                        question_text=question.question_text,
                        question_id=question.question_id,
                        ordinance_id=ordinance.ordinance_id,
                        output_dir=question_dir,
                        profile=execution_profile.profile_name,
                        execution_context=None,
                        timeout_sec=timeout_sec,
                        f10a_mode=f10a_mode,
                        submit_blue_timeout_sec=submit_blue_timeout_sec,
                        submit_ack_timeout_sec=submit_ack_timeout_sec,
                        submit_timeline_poll_ms=submit_timeline_poll_ms,
                    )
                    submit_id = result.submit_id
                    chat_id = result.chat_id
                    submit_sent_at = result.submit_sent_at
                    submit_confirmation = result.submit_confirmation
                    extracted_answer_text = result.answer_text
                    extracted_status = result.extracted_status
                    execution_context = result.execution_context or {}
                    raw_capture = result.raw_capture
                    raw_capture_attempted = result.raw_capture_attempted
                    status = ResultStatus.SUCCESS
                    if (
                        f10a_mode
                        and isinstance(execution_context, Mapping)
                        and execution_context.get("ungenerated")
                    ):
                        status = ResultStatus.UNGENERATED
                        ungenerated = execution_context.get("ungenerated", {})
                        if isinstance(ungenerated, Mapping):
                            reason = ungenerated.get("reason")
                        else:
                            reason = str(ungenerated)
                        skip_answer_write = True
                except SubmitConfirmationError as exc:
                    reason = str(exc)
                    if f10a_mode:
                        status = ResultStatus.UNGENERATED
                        skip_answer_write = True
                        submit_receipt = getattr(exc, "submit_receipt", None)
                        submit_confirmation = getattr(exc, "submit_confirmation", {})
                        if submit_receipt is not None:
                            submit_id = getattr(submit_receipt, "submit_id", submit_id)
                            submit_sent_at = getattr(
                                submit_receipt, "sent_at", submit_sent_at
                            )
                            submit_diag = getattr(
                                submit_receipt, "diagnostics", {}
                            )
                        else:
                            submit_diag = {}
                        execution_context = {
                            "ungenerated": {
                                "reason": reason,
                                "type": type(exc).__name__,
                            },
                            "submit_diagnostics": submit_diag,
                            "submit_confirmation": submit_confirmation,
                        }
                    else:
                        status = ResultStatus.EXEC_ERROR
                        aborted = True
                        fatal_error = reason
                        skip_answer_write = True
                        fatal_submit_error = exc
                except AnswerTimeoutError as exc:
                    status = ResultStatus.TIMEOUT
                    reason = str(exc)
                except AnswerNotAvailableError as exc:
                    status = ResultStatus.NO_ANSWER
                    reason = str(exc)
                except ProbeExecutionError as exc:
                    status = ResultStatus.EXEC_ERROR
                    reason = str(exc)
                except PlaywrightError as exc:
                    status = ResultStatus.UI_ERROR
                    reason = str(exc)
                    if _is_fatal_state(chat_page):
                        aborted = True
                        fatal_error = str(exc)
                except Exception as exc:
                    status = ResultStatus.EXEC_ERROR
                    reason = str(exc)

            except Exception as exc:
                # Defensive catch-all to keep continue-on-error contract.
                status = ResultStatus.EXEC_ERROR
                reason = reason or str(exc)

            citations: Sequence[str] = []
            if citations_fetcher is not None:
                try:
                    citations = list(citations_fetcher(chat_page))
                except Exception:
                    citations = []

            if raw_capture_attempted and raw_capture is None and reason is None:
                reason = "raw capture unavailable"

            try:
                if not isinstance(execution_context, Mapping):
                    execution_context = {}
                else:
                    execution_context = dict(execution_context)

                dom_extraction = execution_context.get("dom_extraction")
                if dom_extraction is None:
                    execution_context["dom_extraction"] = {
                        "selected": False,
                        "reason": "dom extraction unavailable",
                        "text_len": len(extracted_answer_text)
                        if extracted_answer_text
                        else 0,
                        "errors": ["dom extraction unavailable"],
                        "extracted_status": extracted_status,
                        "candidates": [],
                        "selected_n": None,
                        "parity": None,
                    }

                # --- TEMP DEBUG: before writing answer.md ---
                print(
                    "[DEBUG] about to write answer.md",
                    question.question_id,
                    "execution_context=",
                    execution_context,
                )
                # --- /TEMP DEBUG ---

                if not skip_answer_write:
                    _write_answer_markdown(
                        question_dir=question_dir,
                        question=question,
                        ordinance=ordinance,
                        execution_profile=execution_profile,
                        run_id=run_id,
                        executed_at=executed_at,
                        qommons_config=qommons_config,
                        knowledge_scope=knowledge_scope,
                        knowledge_files=knowledge_files,
                        ordinance_set=ordinance_set,
                        question_pool=question_pool,
                        execution=execution,
                        extracted_answer_text=extracted_answer_text,
                        execution_context=execution_context,
                        raw_capture=raw_capture,
                        raw_capture_attempted=raw_capture_attempted,
                        result_status=status,
                        result_reason=reason,
                        aborted_run=aborted,
                        citations=citations,
                        observation_notes=observation_notes,
                        submit_id=submit_id,
                        chat_id=chat_id,
                        extracted_status=extracted_status,
                        submit_sent_at=submit_sent_at or executed_at,
                        submitted_question_text=question.question_text,
                        submit_confirmation=submit_confirmation,
                    )
                elif f10a_mode and status == ResultStatus.UNGENERATED:
                    _write_execution_context_file(
                        question_dir=question_dir,
                        execution_context=execution_context,
                        result_status=status,
                        result_reason=reason,
                    )
            except Exception as exc:
                print("[DEBUG] answer.md write failed:", exc)
                status = ResultStatus.EXEC_ERROR
                reason = reason or f"answer write failed: {exc}"
                # continue-on-error (no raise)

            if aborted:
                break
        if aborted:
            break

    if fatal_submit_error is not None:
        raise fatal_submit_error

    return RunSummary(aborted=aborted, fatal_error=fatal_error, executed_at=executed_at)
