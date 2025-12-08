"""
gov-llm-e2e-testkit — log_writer.py v0.1
Design_log_writer_v0.1（2025-12-08）準拠

役割：
- Design_logging_v0.1 に沿った frontmatter + Markdown ログ生成
- logs/YYYYMMDD/case_id.md の作成
- assets/YYYYMMDD/{case_id}/ ディレクトリの生成
- Smoke / Basic / Advanced を統一フォーマットで扱う
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from typing import Any, Literal, Optional


# 型定義
TestType = Literal["smoke", "basic", "advanced"]
TestStatus = Literal["PASS", "FAIL"]


# -------------------------------------------------------------
# LogContext
# -------------------------------------------------------------
@dataclass
class LogContext:
    case_id: str
    test_type: TestType
    environment: str                # "internet" / "lgwan"
    timestamp: datetime
    browser_timeout_ms: int
    page_timeout_ms: int

    # Smoke / Basic / Advanced 共通
    question: Optional[str] = None
    output_text: Optional[str] = None
    status: Optional[TestStatus] = None

    # Basic / Advanced で利用
    expected_keywords: Optional[list[str]] = None
    must_not_contain: Optional[list[str]] = None
    missing_keywords: Optional[list[str]] = None
    unexpected_words: Optional[list[str]] = None

    # Advanced のみ
    details: Optional[str] = None

    # "screenshot" → path, "dom" → path のようなマッピング
    artifacts: Optional[dict[str, str]] = None

    metadata: Optional[dict[str, Any]] = None


# -------------------------------------------------------------
# ディレクトリ生成（logs/YYYYMMDD/ と logs/assets/YYYYMMDD/{case_id}/）
# -------------------------------------------------------------
def ensure_log_dirs(base_log_dir: Path, case_id: str, timestamp: datetime) -> tuple[Path, Path]:
    date_str = timestamp.strftime("%Y%m%d")

    # 例: logs/20251208/
    case_log_dir = base_log_dir / date_str
    case_log_dir.mkdir(parents=True, exist_ok=True)

    # 例: logs/assets/20251208/RAG_BASIC_001/
    assets_base = base_log_dir / "assets" / date_str / case_id
    assets_base.mkdir(parents=True, exist_ok=True)

    return case_log_dir, assets_base


# -------------------------------------------------------------
# Frontmatter 生成
# -------------------------------------------------------------
def _build_frontmatter(ctx: LogContext) -> str:
    ts = ctx.timestamp.isoformat()

    front = [
        "---",
        f"case_id: {ctx.case_id}",
        f"test_type: {ctx.test_type}",
        f"environment: {ctx.environment}",
        f"timestamp: {ts}",
        f"browser_timeout_ms: {ctx.browser_timeout_ms}",
        f"page_timeout_ms: {ctx.page_timeout_ms}",
        "---",
        "",
    ]
    return "\n".join(front)


# -------------------------------------------------------------
# Markdown 本文生成
# -------------------------------------------------------------
def _build_markdown_body(ctx: LogContext) -> str:
    lines: list[str] = []

    # 1. Summary
    lines.append("## 1. Test Summary")
    lines.append(f"- status: {ctx.status}")
    lines.append("")

    # 2. Input
    lines.append("## 2. Input")
    lines.append(f"* question: \"{ctx.question}\"" if ctx.question else "* question: null")
    lines.append("")

    # 3. Output
    lines.append("## 3. Output")
    lines.append("```text")
    lines.append(ctx.output_text or "")
    lines.append("```")
    lines.append("")

    # 4. Expected（Basic / Advanced のみ）
    if ctx.test_type in ("basic", "advanced"):
        lines.append("## 4. Expected")
        lines.append("- keywords:")
        if ctx.expected_keywords:
            for kw in ctx.expected_keywords:
                lines.append(f"    - \"{kw}\"")
        else:
            lines.append("    - (none)")
        lines.append("")
        lines.append("- must_not_contain:")
        if ctx.must_not_contain:
            for bad in ctx.must_not_contain:
                lines.append(f"    - \"{bad}\"")
        else:
            lines.append("    - (none)")
        lines.append("")

    # 5. Result
    lines.append("## 5. Result")
    lines.append(f"- status: {ctx.status}")
    lines.append("- missing_keywords:")
    if ctx.missing_keywords:
        for kw in ctx.missing_keywords:
            lines.append(f"    - \"{kw}\"")
    else:
        lines.append("    - (none)")
    lines.append("- unexpected_words:")
    if ctx.unexpected_words:
        for w in ctx.unexpected_words:
            lines.append(f"    - \"{w}\"")
    else:
        lines.append("    - (none)")
    lines.append("")

    # 6. Details（Advanced のみ）
    if ctx.test_type == "advanced":
        lines.append("## 6. Details")
        lines.append(ctx.details or "(no details)")
        lines.append("")

    # 7. Artifacts
    lines.append("## 7. Artifacts")
    if ctx.artifacts:
        for k, v in ctx.artifacts.items():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")
    lines.append("")

    # 8. Metadata
    lines.append("## 8. Metadata")
    if ctx.metadata:
        for k, v in ctx.metadata.items():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")
    lines.append("")

    return "\n".join(lines)


# -------------------------------------------------------------
# Markdown ログ書き込み
# -------------------------------------------------------------
def write_markdown_log(log_dir: Path, context: LogContext) -> Path:
    """指定ディレクトリ（例: logs/YYYYMMDD/）に case_id.md を作成する"""
    log_path = log_dir / f"{context.case_id}.md"

    front = _build_frontmatter(context)
    body = _build_markdown_body(context)

    content = front + body

    with open(log_path, "w", encoding="utf-8") as f:
        f.write(content)

    return log_path


# -------------------------------------------------------------
# 高レベル API：ディレクトリ生成 → Markdown 生成
# -------------------------------------------------------------
def create_case_log(base_log_dir: Path, context: LogContext) -> Path:
    """
    Application Test Layer が通常使う API。
    - logs/YYYYMMDD/ と assets/YYYYMMDD/{case_id}/ を生成し
    - Markdown ログを作成する
    """
    case_log_dir, case_assets_dir = ensure_log_dirs(
        base_log_dir, context.case_id, context.timestamp
    )

    # もし artifacts にファイルを保存したい場合、テスト層で先に path を作る。
    # v0.1時点では log_writer 側では何も保存処理は行わない（PO側に委譲）。

    log_path = write_markdown_log(case_log_dir, context)
    return log_path
