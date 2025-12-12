# scripts/run_probe_once.py
"""
run_probe_once.py - Probe v0.2 runner

Design_run_probe_once_v0.1.1
Design_probe_graphql_answer_detection_v0.2

- Qommons.AI へのログイン & チャット準備（template_prepare_chat_v0_1）
- Answer Detection Probe（probe_v0_2.run_graphql_probe）を
  「意味的完了イベント待ち + 時間上限」で 1 回実行する。

NOTE:
- capture_seconds は完了条件ではなくフォールバック上限。
- 完了判定の意味論は probe_v0_2 側に委譲する。
"""

import argparse
import inspect
import sys
from typing import Any, Optional, Tuple

from src.templates.prepare_chat.template_prepare_chat_v0_1 import (
    prepare_chat_session,
)
from scripts.probe_v0_2 import run_graphql_probe


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Qommons Answer Detection probe (v0.2) once."
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=30,
        help=(
            "Maximum waiting time in seconds. "
            "Used only as a fallback upper bound (default: 30)."
        ),
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Playwright browser in headless mode if supported by template.",
    )
    return parser.parse_args(argv)


def _prepare_chat(headless: bool) -> Tuple[Any, Any, Any, Optional[Any]]:
    """
    template_prepare_chat_v0_1 の Stable Core に合わせる。

    Supported return patterns:
        1) (page, context, chat_id)
        2) (browser, context, page, chat_id)

    Returns:
        (page, context, chat_id, browser_or_none)
    """
    kwargs = {}

    sig = inspect.signature(prepare_chat_session)
    if "headless" in sig.parameters:
        kwargs["headless"] = headless

    result = prepare_chat_session(**kwargs)

    try:
        seq = tuple(result)  # type: ignore[arg-type]
    except TypeError:
        raise RuntimeError(
            "prepare_chat_session() must return an iterable "
            "like (page, context, chat_id) or (browser, context, page, chat_id)."
        )

    if len(seq) == 3:
        page, context, chat_id = seq
        browser = None
    elif len(seq) == 4:
        browser, context, page, chat_id = seq
    else:
        raise RuntimeError(
            "prepare_chat_session() must return 3 or 4 values. "
            f"Got {len(seq)} values."
        )

    return page, context, chat_id, browser


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    max_wait_seconds: int = args.seconds
    headless: bool = args.headless

    # QA 基準は 30 秒（意味論は変えない）
    if max_wait_seconds != 30:
        print(
            "[run_probe_once] WARNING: max_wait_seconds is not the QA standard (30s).",
            file=sys.stderr,
        )

    page = None
    context = None
    browser = None
    chat_id = None

    try:
        # 1. チャット準備
        page, context, chat_id, browser = _prepare_chat(headless=headless)

        print("[run_probe_once] Chat prepared.")
        print(f"[run_probe_once] chat_id = {chat_id}")
        print(
            "[run_probe_once] waiting for semantic completion "
            f"(fallback timeout = {max_wait_seconds}s)"
        )

        # 2. Answer Detection Probe 起動
        #    - 完了条件は probe 側で判断
        #    - seconds は上限としてのみ使用
        probe_result = run_graphql_probe(
            page=page,
            chat_id=chat_id,
            capture_seconds=max_wait_seconds,
        )

        print("[run_probe_once] Probe finished.")
        if probe_result is not None:
            print(f"[run_probe_once] probe_result = {probe_result}")

        return 0

    except Exception as exc:
        print(f"[run_probe_once] ERROR: {exc}", file=sys.stderr)
        return 1

    finally:
        # 3. リソース解放
        if page is not None:
            try:
                page.close()
            except Exception:
                pass

        if context is not None:
            try:
                context.close()
            except Exception:
                pass

        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
