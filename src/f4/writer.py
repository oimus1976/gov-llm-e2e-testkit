from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import yaml


JST = timezone(timedelta(hours=9))


def _dump_yaml_lines(data: Dict[str, Any], indent: int = 0) -> List[str]:
    """Render a dict as YAML lines with optional indentation."""
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    prefix = " " * indent
    return [f"{prefix}{line}" if line else prefix for line in dumped.strip().splitlines()]


def write_f4_result(
    *,
    output_dir: Path,
    case_info: Dict[str, str],
    profile: str,
    run_info: Dict[str, str],
    answer_text: str,
    evidence_result: Dict[str, object],
    execution_context: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Write F4 RAG evaluation result as a Markdown file.

    Design principles:
    - profile is mandatory metadata (HTML / Markdown / etc.)
    - filename must be collision-safe
    - writer is dumb: no judgment, no environment resolution
    - all inputs must be concrete, serializable facts
    """

    # --------------------------------------------------
    # 0. Precondition checks (fail fast, explicit)
    # --------------------------------------------------
    if not profile:
        raise ValueError("profile must be a non-empty string")

    if "case_id" not in case_info:
        raise KeyError("case_info must include 'case_id'")

    # --------------------------------------------------
    # 1. Prepare output directory
    # --------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(JST)
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    case_id = case_info["case_id"]

    # filename rule (fixed in F4 operation rule v0.1.1):
    # case_id + profile + timestamp
    filename = f"F4_results_{case_id}_{profile}_{timestamp}.md"
    path = output_dir / filename

    # --------------------------------------------------
    # 2. Markdown content (no inference, facts only)
    # --------------------------------------------------
    lines: List[str] = [
        "---",
        "title: F4_RAG_Evaluation_Results",
        "project: gov-llm-e2e-testkit",
        "phase: F4 (RAG Evaluation)",
        "version: v0.1",
        f"profile: {profile}",
        f"generated_at: {now.isoformat()}",
    ]

    if execution_context is not None:
        lines.extend(_dump_yaml_lines({"execution_context": execution_context}))

    lines.extend(
        [
            "---",
            "",
            "# F4 RAG 評価結果ログ（自動生成）",
            "",
            "## Case Information",
            "",
            f"- Case ID: {case_info.get('case_id', '')}",
            f"- 対象条例: {case_info.get('ordinance', '')}",
            f"- 質問: {case_info.get('question', '')}",
            "",
            "## Execution",
            "",
            f"- profile: {profile}",
            f"- chat_id: {run_info.get('chat_id', 'N/A')}",
            f"- submit_id: {run_info.get('submit_id', 'N/A')}",
        ]
    )

    lines.extend(
        [
            "",
            "## Raw Answer",
            "",
            "```text",
            answer_text,
            "```",
            "",
            "## Evidence Hit",
            "",
            f"- Evidence語リスト: {evidence_result.get('evidence_terms', [])}",
            f"- 出現語: {evidence_result.get('hits', [])}",
            f"- Hit Count: {evidence_result.get('hit_count', 0)}",
            f"- Total: {evidence_result.get('total', 0)}",
            f"- Hit Rate: {evidence_result.get('hit_rate', 'N/A')}",
            "",
            "## Notes",
            "",
            "- 本ファイルは pytest 実行結果から自動生成された。",
            "- 良否判定・比較判断は含まない（差分観測専用）。",
            "",
        ]
    )

    # --------------------------------------------------
    # 3. Write file
    # --------------------------------------------------
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path
