"""
Run customized_question_set.json files via F8 orchestrator (F10-A path).

Features:
- Select all ordinance directories or a single ordinance interactively after startup
- Load questions from JSON without modifying the source file
- Prefix each question with the ordinance ID before submission
- Reuse existing F8/F10 execution flow (run_f8_collection)
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import List, Sequence

from playwright.sync_api import sync_playwright
import yaml

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

from src.execution.f8_orchestrator import (
    ExecutionProfile,
    OrdinanceSpec,
    run_f8_collection,
)
from src.execution.customized_question_set_loader import (
    CustomizedQuestionSet,
    QuestionSetLoadError,
    load_customized_question_set,
)
from scripts.archive_run import create_run_archive


INPUT_ROOT = Path("data") / "customized_question_sets"
QUESTION_SET_FILENAME = "customized_question_set.json"


def _resolve_output_root(args: argparse.Namespace, parser: argparse.ArgumentParser) -> Path:
    if args.output_root:
        value = args.output_root
    else:
        value = os.getenv("OUTPUT_ROOT")
    if value:
        output_root = Path(value).expanduser().resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        return output_root

    auto_env = os.getenv("AUTO_RUN_ID")
    auto_enabled = args.auto_run_id or auto_env == "1"
    if not auto_enabled:
        parser.print_usage()
        raise SystemExit(2)

    run_id = f"auto_{datetime.now():%Y%m%d_%H%M%S}"
    output_root = (Path("out") / run_id).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root


def _write_yaml_once(path: Path, payload: dict) -> None:
    if path.exists():
        raise FileExistsError(f"file already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def _write_readme_once(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"file already exists: {path}")
    content = """# F10-A Observation Dataset

- 本成果物は Qommons.AI UI を観測した一次データです（評価なし）。
- 評価・判定・Gate は reiki-rag-converter 側の責務です。
- manifest.yaml と answer/ 配下のファイル群をそのまま引き渡してください。
"""
    path.write_text(content, encoding="utf-8")


def _collect_manifest_entries(answer_root: Path) -> list[dict]:
    if not answer_root.exists():
        return []

    entries = []
    for ordinance_dir in sorted(
        [p for p in answer_root.iterdir() if p.is_dir()], key=lambda p: p.name
    ):
        for question_dir in sorted(
            [p for p in ordinance_dir.iterdir() if p.is_dir()], key=lambda p: p.name
        ):
            answer_file = question_dir / f"{question_dir.name}_answer.md"
            if not answer_file.is_file():
                continue
            entries.append(
                {
                    "ordinance_id": ordinance_dir.name,
                    "question_id": question_dir.name,
                    "file": (
                        Path("answer")
                        / ordinance_dir.name
                        / question_dir.name
                        / answer_file.name
                    ).as_posix(),
                }
            )
    return entries


def _discover_available_sets() -> dict[str, Path]:
    available: dict[str, Path] = {}
    if not INPUT_ROOT.exists():
        return available

    for child in INPUT_ROOT.iterdir():
        if not child.is_dir():
            continue
        candidate = child / QUESTION_SET_FILENAME
        if candidate.is_file():
            available[child.name] = candidate
    return available


def _prompt_selection(available: dict[str, Path]) -> List[Path]:
    if not available:
        raise SystemExit(
            "[ERROR] No customized_question_set.json files found under data/customized_question_sets/"
        )

    print("[INFO] Available ordinance directories:")
    for oid in sorted(available):
        print(f"- {oid}")

    while True:
        mode = input("Select execution mode (1: all / 2: single): ").strip()
        if mode == "1":
            return [available[k] for k in sorted(available)]
        if mode == "2":
            target = input("対象の条例IDを入力してください: ").strip()
            if target in available:
                return [available[target]]
            print(f"[ERROR] ordinance_id not found: {target}")
            continue
        print("[ERROR] Invalid selection. Enter 1 or 2.")


def _load_sets(paths: Sequence[Path]) -> List[CustomizedQuestionSet]:
    loaded: List[CustomizedQuestionSet] = []
    for path in paths:
        try:
            question_set = load_customized_question_set(path)
        except QuestionSetLoadError as exc:
            raise SystemExit(f"[ERROR] Failed to load {path}: {exc}") from exc

        parent_dir = path.parent.name
        if parent_dir and parent_dir != question_set.ordinance_id:
            raise SystemExit(
                f"[ERROR] ordinance_id mismatch: dir={parent_dir} payload={question_set.ordinance_id}"
            )

        loaded.append(question_set)
    return loaded


def _aggregate_value(values: Sequence[str]) -> str:
    unique = sorted({v for v in values if v})
    if not unique:
        return "unknown"
    if len(unique) == 1:
        return unique[0]
    return "mixed"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run customized_question_set.json files via F10-A orchestrator."
    )
    parser.add_argument(
        "--output-root",
        help="Output directory (includes run_id). Overrides OUTPUT_ROOT.",
    )
    parser.add_argument(
        "--auto-run-id",
        action="store_true",
        help="Auto-generate run_id and use out/auto_YYYYMMDD_HHMMSS as output root.",
    )
    parser.add_argument(
        "--f10a-mode",
        action="store_true",
        help="Enable F10-A submit handling (wait for blue + non-fatal submit timeouts).",
    )
    parser.add_argument(
        "--submit-blue-timeout-sec",
        type=float,
        help="Max seconds to wait for submit to turn blue (F10-A mode).",
    )
    parser.add_argument(
        "--submit-ack-timeout-sec",
        type=float,
        help="Max seconds to wait for submit ack after click (F10-A mode).",
    )
    parser.add_argument(
        "--submit-timeline-poll-ms",
        type=int,
        help="Polling interval in ms for submit button state (F10-A mode).",
    )
    args = parser.parse_args()

    config, _ = load_env()
    output_root = _resolve_output_root(args, parser)
    run_id = output_root.name

    available_sets = _discover_available_sets()
    selected_paths = _prompt_selection(available_sets)
    question_sets = _load_sets(selected_paths)

    execution_profile = ExecutionProfile(
        profile_name="web-default",
        run_mode="collect-only",
    )
    execution = {
        "mode": "manual",
        "retry": 0,
        "temperature": 0.0,
        "max_tokens": 2048,
    }
    f10a_mode = args.f10a_mode or os.getenv("F10A_MODE") == "1"
    submit_blue_timeout_sec = float(
        args.submit_blue_timeout_sec
        if args.submit_blue_timeout_sec is not None
        else os.getenv("F10A_SUBMIT_BLUE_TIMEOUT_SEC", "10")
    )
    submit_ack_timeout_sec = float(
        args.submit_ack_timeout_sec
        if args.submit_ack_timeout_sec is not None
        else os.getenv("F10A_SUBMIT_ACK_TIMEOUT_SEC", "3")
    )
    submit_timeline_poll_ms = int(
        args.submit_timeline_poll_ms
        if args.submit_timeline_poll_ms is not None
        else os.getenv("F10A_SUBMIT_POLL_MS", "100")
    )

    latest_summary = None
    question_pool_values = []
    ordinance_set_values = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login = LoginPage(page, config)
        login.open()
        login.login()

        select_page = ChatSelectPage(page, config)
        ai_name = config.get("chat_name", "プライベートナレッジ")
        select_page.open_ai(ai_name)

        chat_page = ChatPage(page, config)

        for question_set in question_sets:
            print(f"[INFO] Running ordinance_id={question_set.ordinance_id}")
            summary = run_f8_collection(
                chat_page=chat_page,
                ordinances=[
                    OrdinanceSpec(
                        ordinance_id=question_set.ordinance_id,
                        display_name=question_set.ordinance_id,
                    )
                ],
                questions=question_set.questions,
                execution_profile=execution_profile,
                run_id=run_id,
                qommons_config={
                    "model": "gpt-5.2",
                    "web_search": False,
                    "region": "jp",
                    "ui_mode": "web",
                },
                knowledge_scope="golden",
                knowledge_files=[],
                ordinance_set=question_set.question_set_id,
                output_root=output_root,
                execution=execution,
                question_pool=question_set.question_pool,
                f10a_mode=f10a_mode,
                submit_blue_timeout_sec=submit_blue_timeout_sec,
                submit_ack_timeout_sec=submit_ack_timeout_sec,
                submit_timeline_poll_ms=submit_timeline_poll_ms,
            )
            latest_summary = summary
            question_pool_values.append(question_set.question_pool)
            ordinance_set_values.append(question_set.question_set_id)
            print("aborted:", summary.aborted)
            print("fatal_error:", summary.fatal_error)

        debug_dir = output_root / "debug_dom"
        debug_dir.mkdir(parents=True, exist_ok=True)
        html = page.content()
        (debug_dir / "page_full.html").write_text(html, encoding="utf-8")
        div_texts = page.locator("div").all_inner_texts()
        with (debug_dir / "div_texts.txt").open("w", encoding="utf-8") as f:
            for i, t in enumerate(div_texts):
                f.write(f"\n===== DIV[{i}] =====\n")
                f.write(t.strip())
                f.write("\n")

        context.close()
        browser.close()

    executed_at = (
        latest_summary.executed_at.isoformat() if latest_summary else "unknown"
    )
    manifest = {
        "schema_version": "manifest_v0.1",
        "based_on_interface": "v0.2",
        "kind": "manifest",
        "run_id": run_id,
        "executed_at": executed_at,
        "sets": {
            "ordinance_set": _aggregate_value(ordinance_set_values),
            "question_pool": _aggregate_value(question_pool_values),
            "question_set_ids": ordinance_set_values,
        },
        "entries": _collect_manifest_entries(output_root / "answer"),
    }

    execution_meta = {
        "run_id": run_id,
        "executed_at": executed_at,
        "question_csv": None,
        "question_pool": _aggregate_value(question_pool_values),
        "ordinance_set": _aggregate_value(ordinance_set_values),
        "question_set_ids": ordinance_set_values,
        "execution_account": config.get("username", "N/A"),
        "evaluation_performed": False,
        "notes": ["UI 観測のみ。評価・Gate 判定は含まない。"],
    }

    _write_yaml_once(output_root / "manifest.yaml", manifest)
    _write_yaml_once(output_root / "execution_meta.yaml", execution_meta)
    _write_readme_once(output_root / "README.md")

    run_completed = (
        latest_summary is not None
        and not latest_summary.aborted
        and not latest_summary.fatal_error
    )
    if run_completed:
        archive_path = create_run_archive(output_root)
        print(f"[INFO] Created run archive: {archive_path}")
    else:
        print("[INFO] Run not completed; archive skipped.")


if __name__ == "__main__":
    main()
