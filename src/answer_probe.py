# src/answer_probe.py
"""
answer_probe v0.1
pytest から Answer Detection Layer（probe v0.2）を正規利用するための最小入口。

- probe の完了意味論には介入しない
- DOM/UI 操作は一切行わない
- v0.1 では証跡保存は扱わない（probe 内部出力は制御対象外）
"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Page

from scripts.probe_v0_2 import run_graphql_probe


# =========================
# Exceptions（v0.1）
# =========================


class AnswerProbeError(Exception):
    """answer_probe 系の基底例外"""


class AnswerTimeoutError(AnswerProbeError):
    """timeout_sec 経過までに answer を取得できなかった（原因は推測しない）"""


class AnswerNotAvailableError(AnswerProbeError):
    """観測は行われたが、answer_text を取得できなかった（観測事実）"""


class ProbeExecutionError(AnswerProbeError):
    """probe 呼び出し自体が失敗した"""


# =========================
# Internal Adapter
# =========================


class _ProbeClient:
    """
    probe v0.2 呼び出し専用の薄いアダプタ。

    - v0.1 では submit_id は使用しない
    - capture_seconds は timeout_sec をそのままマッピング
    """

    def wait_for_summary(
        self,
        *,
        page: Page,
        chat_id: str,
        timeout_sec: int,
    ) -> dict:
        try:
            summary = run_graphql_probe(
                page=page,
                chat_id=chat_id,
                capture_seconds=timeout_sec,
            )
            return summary
        except Exception as e:
            # probe 内部の詳細には踏み込まない
            raise ProbeExecutionError("probe execution failed") from e


# =========================
# Public API（v0.1）
# =========================


def wait_for_answer_text(
    *,
    page: Page,
    submit_id: str,
    chat_id: str,
    timeout_sec: int = 60,
    poll_interval_sec: float = 1.0,  # v0.1 では未使用（将来拡張用）
) -> str:
    """
    probe v0.2 を用いて回答テキスト（raw str）を取得する。

    Notes:
    - page は response hook 観測のために必須
    - submit_id は v0.1 では probe 呼び出しに使用しない（API互換用）
    - DOM/UI 操作は行わない
    """

    client = _ProbeClient()
    summary = client.wait_for_summary(
        page=page,
        chat_id=chat_id,
        timeout_sec=timeout_sec,
    )

    # --- answer_text 抽出ルール（v0.1 確定） ---
    # 1. REST answer を最優先
    rest_answer: Optional[str] = summary.get("rest_answer")
    if isinstance(rest_answer, str) and rest_answer.strip():
        return rest_answer

    # 2. GraphQL answer をフォールバック
    graphql_answer: Optional[str] = summary.get("graphql_answer")
    if isinstance(graphql_answer, str) and graphql_answer.strip():
        return graphql_answer

    # 3. どちらも無い → 観測事実として例外
    # timeout / mismatch 等の理由は推測しない
    raise AnswerNotAvailableError("answer_text not available after probe observation")
