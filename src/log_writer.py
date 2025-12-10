# ==========================================================
# log_writer v0.11  （v0.1 の上位互換 / Smoke Test 対応版）
# gov-llm-e2e-testkit
# 最終更新: 2025-12-10
# ==========================================================

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


# ----------------------------------------------------------
# LogContext v0.11
# ----------------------------------------------------------
@dataclass
class LogContext:
    case_id: str
    timestamp: datetime
    test_type: str = "smoke"               # 追加：デフォルト値
    environment: str = "internet"          # 追加：デフォルト値
    browser_timeout_ms: int = 0            # 追加：Smoke 用の緩いデフォルト
    page_timeout_ms: int = 0               # 追加
    sections: list = field(default_factory=list)

    def add_section(self, title: str, data: dict):
        """テスト中のログセクションを追加"""
        self.sections.append({
            "title": title,
            "data": data,
        })


# ----------------------------------------------------------
# Markdown 出力（Smoke の最小要件を満たす）
# ----------------------------------------------------------
def create_case_log(case_log_dir: str | Path, context: LogContext):
    case_log_dir = Path(case_log_dir)
    case_log_dir.mkdir(parents=True, exist_ok=True)

    md_path = case_log_dir / f"{context.case_id}.md"

    lines = []
    lines.append(f"# Test Log — {context.case_id}")
    lines.append("")
    lines.append(f"- Timestamp: {context.timestamp.isoformat()}")
    lines.append(f"- Test Type: {context.test_type}")
    lines.append(f"- Environment: {context.environment}")
    lines.append(f"- Browser Timeout: {context.browser_timeout_ms} ms")
    lines.append(f"- Page Timeout: {context.page_timeout_ms} ms")
    lines.append("")

    lines.append("## Sections")
    for sec in context.sections:
        lines.append(f"### {sec['title']}")
        lines.append("```json")
        lines.append(json.dumps(sec["data"], ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    return md_path
