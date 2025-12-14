from pathlib import Path
from datetime import datetime
from typing import Dict


def write_f4_result(
    *,
    output_dir: Path,
    case_info: Dict[str, str],
    run_info: Dict[str, str],
    answer_text: str,
    evidence_result: Dict[str, object],
):
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"F4_results_{case_info['case_id']}.md"

    lines = [
        "---",
        "title: F4_RAG_Evaluation_Results",
        "phase: F4 (RAG Evaluation)",
        "version: v0.1",
        f"generated_at: {datetime.now().isoformat()}",
        "---",
        "",
        "# F4 RAG 評価結果ログ（自動生成）",
        "",
        "## Case Information",
        "",
        f"- Case ID: {case_info['case_id']}",
        f"- 対象条例: {case_info['ordinance']}",
        f"- 質問: {case_info['question']}",
        "",
        "## Execution",
        "",
        f"- 実行条件: {run_info['mode']}",
        f"- chat_id: {run_info.get('chat_id', 'N/A')}",
        f"- submit_id: {run_info.get('submit_id', 'N/A')}",
        "",
        "## Raw Answer",
        "",
        "```text",
        answer_text,
        "```",
        "",
        "## Evidence Hit",
        "",
        f"- Evidence語リスト: {evidence_result['evidence_terms']}",
        f"- 出現語: {evidence_result['hits']}",
        f"- Hit Count: {evidence_result['hit_count']}",
        f"- Total: {evidence_result['total']}",
        f"- Hit Rate: {evidence_result['hit_rate']}",
        "",
    ]

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
