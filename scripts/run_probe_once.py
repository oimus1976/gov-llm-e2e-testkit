# sandbox/run_probe_once.py
"""
run_probe_once.py - Probe v0.2.1 起動スクリプト

Design_run_probe_once_v0.1.1 に基づき、
- Qommons.AI へのログイン & チャット準備（template_prepare_chat_v0_1）
- GraphQL createData 監視プローブ（probe_v0_2.run_graphql_probe）
を 1 回だけ実行するユーティリティ。

実行例:
    python -m sandbox.run_probe_once
    python -m sandbox.run_probe_once --seconds 45 --headless
"""

import argparse
import inspect
import sys
from typing import Any, Optional, Tuple

from src.templates.prepare_chat.template_prepare_chat_v0_1 import (
    prepare_chat_session,
)
from sandbox.probe_v0_2 import run_graphql_probe


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Qommons GraphQL probe (probe_v0.2.1) once."
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=30,
        help="Probe capture duration in seconds (default: 30).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Playwright browser in headless mode if supported by template.",
    )
    return parser.parse_args(argv)


def _prepare_chat(headless: bool) -> Tuple[Any, Any, Any, Optional[Any]]:
    """
    template_prepare_chat_v0_1 の Stable Core に最大限合わせる。

    想定されるパターン:
        1) page, context, chat_id = prepare_chat_session(...)
        2) browser, context, page, chat_id = prepare_chat_session(...)

    どちらでも動作するようにし、テンプレ側の変更を強要しない。
    戻り値:
        (page, context, chat_id, browser_or_none)
    """
    kwargs = {}

    # テンプレ側が headless 引数をサポートしている場合のみ渡す
    sig = inspect.signature(prepare_chat_session)
    if "headless" in sig.parameters:
        kwargs["headless"] = headless

    result = prepare_chat_session(**kwargs)

    # 返り値をタプルとして扱う（list でも OK）
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
            "prepare_chat_session() must return 3 or 4 values: "
            "(page, context, chat_id) or (browser, context, page, chat_id). "
            f"Got {len(seq)} values."
        )

    return page, context, chat_id, browser


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    capture_seconds: int = args.seconds
    headless: bool = args.headless

    # QA 基準値は 30 秒。変更された場合は警告のみ出す（挙動は変えない）
    if capture_seconds != 30:
        print(
            "[run_probe_once] WARNING: capture_seconds is not the QA standard (30s).",
            file=sys.stderr,
        )

    page = None
    context = None
    browser = None
    chat_id = None

    try:
        # 1. チャット準備（ログイン・チャット画面遷移・chat_id 取得）
        page, context, chat_id, browser = _prepare_chat(headless=headless)

        print("[run_probe_once] Chat prepared.")
        print(f"[run_probe_once] chat_id = {chat_id}")
        print(f"[run_probe_once] capture_seconds = {capture_seconds}")

        # 2. GraphQL createData 監視プローブ起動
        #    戻り値は probe の出力ディレクトリ（想定）
        probe_dir = run_graphql_probe(
            page=page,
            chat_id=chat_id,
            capture_seconds=capture_seconds,
        )

        print("[run_probe_once] Probe finished successfully.")
        if probe_dir is not None:
            print(f"[run_probe_once] probe_dir = {probe_dir}")

        # 成功: exit code 0
        return 0

    except Exception as exc:
        # 失敗時: 標準エラーにメッセージ出力 + exit code 1
        print(f"[run_probe_once] ERROR: {exc}", file=sys.stderr)
        return 1

    finally:
        # 3. リソース解放（context / browser を確実に閉じる）
        #    どちらが存在していても落とさないように try/except で保護
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
