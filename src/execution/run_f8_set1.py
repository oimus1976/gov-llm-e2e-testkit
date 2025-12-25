# src/execution/run_f8_set1.py
"""
Runner for F8-Set-1 (single-question set, 18 fixed questions).

Responsibilities:
- sequentially execute F8-Set-1 using run_single_question()
- assemble v0.1r+ Markdown outputs (raw observations only)
- avoid evaluation, inference, or default completion
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Optional, Sequence

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.answer_probe import (
    AnswerNotAvailableError,
    AnswerTimeoutError,
    ProbeExecutionError,
)

from src.execution.run_single_question import (
    ChatPageProtocol,
    SingleQuestionResult,
    run_single_question,
)


# ---------------------------------------------------------------------------
# F8-Set-1: source of truth = docs/Golden_Question_Pool_A_v1.1.md
# Question IDs follow Q01?Q18 (operation procedure example).
# ---------------------------------------------------------------------------
F8_SET1_QUESTIONS: List[tuple[str, str]] = [
    ("Q01", "Q1. この条例の目的を分かりやすく説明してください。"),
    (
        "Q02",
        "Q2. この条例が何条で構成されているかを示し、それぞれの条の概要を説明してください。",
    ),
    ("Q03", "Q3. 第○条の内容を要約してください。"),
    ("Q04", "Q4. 第○条第○項の内容を説明してください。"),
    (
        "Q05",
        "Q5. この条例で定められている義務・禁止事項をすべて抽出し、箇条書きで説明してください。",
    ),
    (
        "Q06",
        "Q6. この条例に基づく手続きの全体的な流れを、関連条文を引用しながら説明してください。",
    ),
    (
        "Q07",
        "Q7. 他の条文の解釈に影響を与える条があれば、引用して説明してください。",
    ),
    ("Q08", "Q8. 附則がある場合、その内容を要約し、本則との関係を説明してください。"),
    ("Q09", "Q9. 住民（関係者）が特に注意すべき点を説明してください。"),
    (
        "Q10",
        "Q10. 例外規定がある場合、その内容を説明してください。なければ「ない」と答えてください。",
    ),
    ("Q11", "Q11. 定義されている用語があれば、定義条を引用して説明してください。"),
    ("Q12", "Q12. 第○条と第○条の関係性を説明してください。"),
    ("Q13", "Q13. 回答の根拠となる条文を引用して示してください。"),
    (
        "Q14",
        "Q14. 判断基準を本文の記載箇所を引用しながらまとめてください。",
    ),
    (
        "Q15",
        "Q15. 条例を「目的→手続き→義務→例外→附則」の順に再構成してください。",
    ),
    ("Q16", "Q16. 第三者に説明する場合の最適な説明順を、条文に基づいて示してください。"),
    ("Q17", "Q17. 条例全体を統合して説明してください。"),
    ("Q18", "Q18. 条例全体を100字以内で要約してください。"),
]


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
    run_mode: str  # fixed: "collect-only"


@dataclass(frozen=True)
class RunSummary:
    aborted: bool
    fatal_error: Optional[str]


@dataclass(frozen=True)
class F8QuestionOutcome:
    """Outcome per question (facts only)."""

    question_id: str
    output_path: Optional[Path]
    result: Optional[SingleQuestionResult]
    result_status: str
    error: Optional[str]


def _validate_required_keys(data: Mapping[str, Any], keys: Sequence[str], *, label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise KeyError(f"{label} missing required keys: {', '.join(missing)}")


def _render_yaml_block(data: Mapping[str, Any], indent: int = 0) -> List[str]:
    import yaml

    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip().splitlines()
    prefix = " " * indent
    return [f"{prefix}{line}" for line in dumped]


def _is_execution_context_broken(chat_page: ChatPageProtocol) -> bool:
    """Detect fatal browser/context/page breakage."""
    try:
        page = chat_page.page
    except Exception:
        return False

    try:
        if page.is_closed():
            return True

        context = page.context
        if hasattr(context, "is_closed") and context.is_closed():
            return True

        browser = getattr(context, "browser", None)
        if browser is not None and hasattr(browser, "is_connected") and not browser.is_connected():
            return True
    except Exception:
        return False

    return False


def _classify_failure(exc: Exception) -> str:
    """Map observable exceptions to fixed failure taxonomy labels."""
    if isinstance(exc, AnswerTimeoutError):
        return "TIMEOUT"
    if isinstance(exc, AnswerNotAvailableError):
        return "NO_ANSWER"
    if isinstance(exc, PlaywrightTimeoutError):
        return "UI_ERROR"
    if isinstance(exc, PlaywrightError):
        return "UI_ERROR"
    if isinstance(exc, ProbeExecutionError):
        return "EXEC_ERROR"
    return "EXEC_ERROR"


def _capture_observation_logs(*, chat_page: ChatPageProtocol, output_dir: Path, label: str) -> None:
    """
    Best-effort capture of DOM and page content for investigation.

    Only used on TIMEOUT/NO_ANSWER to avoid altering normal execution.
    """

    try:
        page = chat_page.page
    except Exception:
        return

    debug_dir = Path(output_dir) / "debug"
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return

    try:
        dom_snapshot = page.evaluate("document.documentElement.outerHTML")
        (debug_dir / f"{label}_dom_snapshot.html").write_text(str(dom_snapshot), encoding="utf-8")
    except Exception:
        pass

    try:
        page_content = page.content()
        (debug_dir / f"{label}_page_content.html").write_text(str(page_content), encoding="utf-8")
    except Exception:
        pass


def _capture_raw_answer_block(
    *, chat_page: ChatPageProtocol, output_dir: Path, selection_rule_version: str = "v2"
) -> bool:
    """
    Best-effort capture of a likely answer block from the rendered DOM.

    Returns True when new raw artifacts are written.
    """

    try:
        page = chat_page.page
    except Exception:
        return False

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return False

    html_path = Path(output_dir) / "raw_answer.html"
    text_path = Path(output_dir) / "raw_answer.txt"
    meta_path = Path(output_dir) / "raw_capture_meta.json"

    # Avoid overwriting any existing artifacts.
    if html_path.exists() or text_path.exists() or meta_path.exists():
        return False

    try:
        capture = page.evaluate(
            """
            () => {
              const blocks = Array.from(document.querySelectorAll('div.markdown'));
              if (!blocks.length) return null;

              const selectedIndex = blocks.length - 1;
              const el = blocks[selectedIndex];
              const text = (el.innerText || '').trim();
              if (!text) return null;

              return {
                block_count: blocks.length,
                selected_index: selectedIndex,
                html: el.outerHTML || '',
                text,
              };
            }
            """
        )
    except Exception:
        return False

    if not capture:
        return False

    html = capture.get("html")
    text = capture.get("text")
    if not html or text is None:
        return False

    meta = {
        "selection_rule": "div.markdown:last",
        "block_count": capture.get("block_count"),
        "selected_index": capture.get("selected_index"),
        "selection_rule_version": selection_rule_version,
    }

    try:
        html_path.write_text(str(html), encoding="utf-8")
        text_path.write_text(str(text), encoding="utf-8")
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        return False

    return True


def _write_single_markdown(
    *,
    question_id: str,
    question_text: str,
    ordinance_id: str,
    profile: str,
    output_dir: Path,
    submit_id: Optional[str],
    chat_id: Optional[str],
    answer_text: str,
    execution_context: Optional[dict],
    run_id: str,
    executed_at: datetime,
    qommons_config: Mapping[str, Any],
    knowledge_scope: str,
    knowledge_files: Sequence[Mapping[str, str]],
    ordinance_set: str,
    question_pool: str,
    execution: Mapping[str, Any],
    citations: Sequence[str],
    observation_notes: Optional[Sequence[str]],
    result_status: str,
    result_reason: Optional[str],
    aborted_run: bool,
    raw_capture: bool,
) -> Path:
    """Create one v0.1r+ Markdown log (no evaluation)."""

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

    question_dir = Path(output_dir)
    question_dir.mkdir(parents=True, exist_ok=True)

    output_path = question_dir / "answer.md"

    if output_path.exists():
        raise FileExistsError(f"output already exists: {output_path}")

    lines: List[str] = [
        "---",
        "schema_version: v0.1r+",
        f"run_id: {run_id}",
        f"executed_at: {executed_at.isoformat()}",
        f"result_status: {result_status}",
        f"aborted_run: {aborted_run}",
        f"raw_capture: {str(raw_capture).lower()}",
    ]

    if result_reason:
        lines.append(f"result_reason: {result_reason}")

    lines.extend(
        [
            "qommons:",
            f"  model: {qommons_config['model']}",
            f"  web_search: {qommons_config['web_search']}",
            f"  region: {qommons_config['region']}",
            f"  ui_mode: {qommons_config['ui_mode']}",
            "knowledge:",
            f"  scope: {knowledge_scope}",
            "  files:",
        ]
    )

    for item in knowledge_files:
        _validate_required_keys(item, ["type", "name"], label="knowledge_files")
        lines.append("    - type: {type}".format(type=item["type"]))
        lines.append("      name: {name}".format(name=item["name"]))

    lines.extend(
        [
            "target:",
            f"  ordinance_id: {ordinance_id}",
            f"  ordinance_set: {ordinance_set}",
            f"  question_id: {question_id}",
            f"  question_pool: {question_pool}",
            "execution:",
            f"  retry: {execution['retry']}",
            f"  temperature: {execution['temperature']}",
            f"  max_tokens: {execution['max_tokens']}",
            "---",
            "",
            "## Question",
            "",
            question_text,
            "",
            "## Answer (Raw)",
            "",
            "```text",
            answer_text,
            "```",
            "",
            "## Citations (As Displayed)",
            "",
        ]
    )

    if citations:
        lines.extend([f"- {c}" for c in citations])
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
        lines.extend([f"- {note}" for note in observation_notes])
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            "## Metadata (Observed)",
            "",
            f"- submit_id: {submit_id or 'N/A'}",
            f"- chat_id: {chat_id or 'N/A'}",
            f"- profile: {profile}",
            f"- output_dir: {output_dir}",
        ]
    )

    if execution_context is not None:
        lines.extend(
            [
                "- execution_context:",
                "```yaml",
                *_render_yaml_block(execution_context),
                "```",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def run_f8_set1(
    *,
    chat_page: ChatPageProtocol,
    ordinance_id: str,
    profile: str,
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
    execution_context: Optional[dict] = None,
    timeout_sec: int = 60,
) -> List[F8QuestionOutcome]:
    """
    Run the fixed 18-question set (F8-Set-1) sequentially.

    The runner does not perform evaluation or inference.
    Missing metadata stays as observed (e.g., N/A).
    """

    executed_at = datetime.now(timezone.utc)
    run_date = executed_at.strftime("%Y%m%d")
    outcomes: List[F8QuestionOutcome] = []
    aborted = False
    fatal_error: Optional[str] = None

    for question_id, question_text in F8_SET1_QUESTIONS:
        question_dir = Path(output_root) / run_date / ordinance_id / question_id
        result: Optional[SingleQuestionResult] = None
        result_status = "SUCCESS"
        result_reason: Optional[str] = None
        output_path: Optional[Path] = None
        citations: Sequence[str] = []
        answer_text = ""
        submit_id: Optional[str] = None
        chat_id: Optional[str] = None
        profile_used = profile
        raw_capture_saved = False

        try:
            result = run_single_question(
                chat_page=chat_page,
                question_text=question_text,
                question_id=question_id,
                ordinance_id=ordinance_id,
                output_dir=question_dir,
                profile=profile,
                execution_context=execution_context,
                timeout_sec=timeout_sec,
            )

            answer_text = result.answer_text
            submit_id = result.submit_id
            chat_id = result.chat_id
            profile_used = result.profile

            if citations_fetcher is not None:
                try:
                    citations = list(citations_fetcher(chat_page))
                except Exception:
                    citations = []

        except Exception as exc:  # noqa: BLE001 - propagate fact of failure
            result_status = _classify_failure(exc)
            result_reason = str(exc)
            if result_status in ("TIMEOUT", "NO_ANSWER"):
                _capture_observation_logs(
                    chat_page=chat_page,
                    output_dir=question_dir,
                    label=result_status.lower(),
                )
            if _is_execution_context_broken(chat_page):
                aborted = True
                fatal_error = result_reason

        try:
            raw_capture_saved = _capture_raw_answer_block(
                chat_page=chat_page,
                output_dir=question_dir,
            )
        except Exception:
            raw_capture_saved = False
        finally:
            try:
                output_path = _write_single_markdown(
                    question_id=question_id,
                    question_text=question_text,
                    ordinance_id=ordinance_id,
                    profile=profile_used,
                    output_dir=question_dir,
                    submit_id=submit_id,
                    chat_id=chat_id,
                    answer_text=answer_text,
                    execution_context=execution_context,
                    run_id=run_id,
                    executed_at=executed_at,
                    qommons_config=qommons_config,
                    knowledge_scope=knowledge_scope,
                    knowledge_files=knowledge_files,
                    ordinance_set=ordinance_set,
                    question_pool=question_pool,
                    execution=execution,
                    citations=citations,
                    observation_notes=observation_notes,
                    result_status=result_status,
                    result_reason=result_reason,
                    aborted_run=aborted,
                    raw_capture=raw_capture_saved,
                )
            except Exception as write_exc:  # noqa: BLE001
                result_status = "EXEC_ERROR"
                result_reason = result_reason or str(write_exc)
                output_path = None
                if _is_execution_context_broken(chat_page):
                    aborted = True
                    fatal_error = result_reason

        outcomes.append(
            F8QuestionOutcome(
                question_id=question_id,
                output_path=output_path,
                result=result,
                result_status=result_status,
                error=result_reason,
            )
        )

        if aborted:
            break

    return outcomes
