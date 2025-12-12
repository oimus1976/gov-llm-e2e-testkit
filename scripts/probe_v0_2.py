# scripts/probe_v0_2.py
"""
probe v0.2.1 — GraphQL createData 監視 + assistant 抽出
(Design_probe_graphql_answer_detection_v0.1 / Design_chat_answer_detection_v0.1 準拠)

改訂履歴（v0.2 → v0.2.1）:
- operationName == "createData" の厳密判定を追加
- JSON パース不能レスポンスもイベントとして記録（一次情報保持）
- createData 到着時刻（first_graphql_ts）を summary に追加
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page, Response  # type: ignore[import]


# プロジェクト標準
JST = timezone(timedelta(hours=9))


@dataclass
class ProbeEvent:
    ts: str
    kind: str  # "graphql" | "rest_post" | "rest_get" | "other"
    chat_id: Optional[str]
    url: str
    method: str
    status: int
    raw: Optional[Dict[str, Any]]
    parse_error: bool = False  # JSON parse 不能かどうか


def _now_ts() -> str:
    return datetime.now(JST).isoformat()


def _default_output_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    base = repo_root / "logs"
    ts = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
    return base / f"xhr_probe_{ts}"



def _extract_chat_id_from_sk(sk: str) -> Optional[str]:
    if not isinstance(sk, str):
        return None
    if "#" not in sk:
        return None
    return sk.split("#", 1)[0]


def _extract_graphql_answer(raw: Dict[str, Any]) -> Optional[str]:
    """
    GraphQL createData.value の "assistant#..." を抽出（設計書準拠）。
    """
    try:
        value = raw["data"]["createData"]["value"]
    except Exception:
        return None

    if not isinstance(value, str):
        return None

    # もっとも期待される形式
    if value.startswith("assistant#"):
        return value.split("assistant#", 1)[1]

    # プレフィックス揺らぎ対策
    if "#" in value:
        return value.split("#", 1)[1]

    return value  # 最終 fallback


def _extract_rest_answer(raw: Dict[str, Any]) -> Optional[str]:
    """
    REST GET /messages → assistant.content を抽出（設計書・実測ログ準拠）。
    """
    if not isinstance(raw, dict):
        return None

    # data ラップを吸収
    data = raw.get("data") if isinstance(raw.get("data"), dict) else raw

    msgs = data.get("messages")
    if isinstance(msgs, list):
        for msg in reversed(msgs):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content")
                if isinstance(content, str):
                    return content

    return None



def run_graphql_probe(
    page: Page,
    chat_id: str,
    *,
    capture_seconds: int = 30,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    probe v0.2.1 の中核:
    - POST /messages
    - GraphQL createData (回答確定)
    - GET /messages
    の3系統を監視し、一次情報を jsonl と summary.json に保存。
    """

    if output_dir is None:
        output_dir = _default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    events: List[ProbeEvent] = []
    first_graphql_ts: Optional[str] = None

    def _handle_response(response: Response) -> None:
        url = response.url
        method = response.request.method  # type: ignore[attr-defined]
        status = response.status

        parsed_json: Optional[Dict[str, Any]] = None
        parse_error = False

        # JSON 解析（失敗してもイベント記録するため raw=None で保持）
        try:
            parsed_json = response.json()
        except Exception:
            parse_error = True

        # ---- GraphQL createData 判定 ----
        if "/graphql" in url and method.upper() == "POST":

            # createData 以外の GraphQL は記録しない（設計書の厳密化）
            if parsed_json and isinstance(parsed_json, dict):
                # GraphQL の operationName を優先してチェック
                op = parsed_json.get("operationName")
                if op != "createData":
                    return

                # data.createData.sk の chat_id 抽出
                try:
                    create_data = parsed_json["data"]["createData"]
                    sk = create_data.get("sk")
                    event_chat_id = _extract_chat_id_from_sk(sk)
                except Exception:
                    return

                if event_chat_id != chat_id:
                    return

                ts = _now_ts()
                nonlocal first_graphql_ts
                if first_graphql_ts is None:
                    first_graphql_ts = ts

                events.append(
                    ProbeEvent(
                        ts=ts,
                        kind="graphql",
                        chat_id=chat_id,
                        url=url,
                        method=method,
                        status=status,
                        raw=parsed_json,
                        parse_error=parse_error,
                    )
                )
                return

            # GraphQL だが JSON パース失敗 → 設計に従い raw=None で記録
            events.append(
                ProbeEvent(
                    ts=_now_ts(),
                    kind="graphql",
                    chat_id=None,
                    url=url,
                    method=method,
                    status=status,
                    raw=None,
                    parse_error=True,
                )
            )
            return

        # ---- REST /chat/<chat_id>/messages ----
        if "/chat/" in url and "/messages" in url:
            if chat_id not in url:
                return

            if method.upper() == "POST":
                kind = "rest_post"
            elif method.upper() == "GET":
                kind = "rest_get"
            else:
                kind = "other"

            events.append(
                ProbeEvent(
                    ts=_now_ts(),
                    kind=kind,
                    chat_id=chat_id,
                    url=url,
                    method=method,
                    status=status,
                    raw=parsed_json,
                    parse_error=parse_error,
                )
            )
            return

        # ---- それ以外の XHR も記録（設計書の "一次情報保持" に従う）----
        # ただし chat_id に関係しない一般通信は kind="other"
        events.append(
            ProbeEvent(
                ts=_now_ts(),
                kind="other",
                chat_id=None,
                url=url,
                method=method,
                status=status,
                raw=parsed_json,
                parse_error=parse_error,
            )
        )

    # Playwright の response イベント登録
    page.on("response", _handle_response)

    # capture_seconds 監視
    page.wait_for_timeout(capture_seconds * 1000)

    # ---- JSONL 出力 ----
    jsonl_path = output_dir / "graphql_probe.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(
                json.dumps(
                    {
                        "ts": ev.ts,
                        "kind": ev.kind,
                        "chat_id": ev.chat_id,
                        "url": ev.url,
                        "method": ev.method,
                        "status": ev.status,
                        "parse_error": ev.parse_error,
                        "raw": ev.raw,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    # ---- summary.json を生成 ----
    has_post = any(e.kind == "rest_post" for e in events)
    has_get = any(e.kind == "rest_get" for e in events)
    has_graphql = any(e.kind == "graphql" for e in events)

    graphql_answer: Optional[str] = None
    rest_answer: Optional[str] = None

    # 最初の createData から回答抽出
    for ev in events:
        if ev.kind == "graphql" and ev.raw:
            graphql_answer = _extract_graphql_answer(ev.raw)
            if graphql_answer:
                break

    # 最後の GET /messages から回答抽出
    for ev in reversed(events):
        if ev.kind == "rest_get" and ev.raw:
            rest_answer = _extract_rest_answer(ev.raw)
            if rest_answer:
                break

    # ステータス判定
    if not has_graphql:
        status = "no_graphql"
    elif graphql_answer and rest_answer and graphql_answer == rest_answer:
        status = "ok"
    elif graphql_answer and rest_answer and graphql_answer != rest_answer:
        status = "mismatch_with_rest"
    else:
        status = "incomplete"

    summary = {
        "chat_id": chat_id,
        "status": status,
        "first_graphql_ts": first_graphql_ts,
        "graphql_answer": graphql_answer,
        "rest_answer": rest_answer,
        "has_post": has_post,
        "has_get": has_get,
        "has_graphql": has_graphql,
        "event_count": len(events),
        "output_dir": str(output_dir),
        "jsonl_path": str(jsonl_path),
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


if __name__ == "__main__":
    print(
        "probe_v0_2.1 はライブラリモジュールとして利用します。\n"
        "template_prepare_chat_v0_1 などから page / chat_id を取得し、\n"
        "run_graphql_probe(page, chat_id) を呼び出してください。"
    )
