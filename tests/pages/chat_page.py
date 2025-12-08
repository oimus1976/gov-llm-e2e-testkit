# tests/pages/chat_page.py
"""
ChatPage v0.2

- チャット画面の操作を抽象化する Page Object
- BasePage v0.2 の safe_* / collect_evidence を利用し、
  UI 操作失敗時にスクリーンショット＋DOM を自動収集する
- INTERNET / LGWAN 両環境での安定動作を目指す

設計書:
- docs/Design_ChatPage_v0.2.md
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import Page, Locator

from .base_page import BasePage


PathLike = Union[str, Path]


class ChatPage(BasePage):
    """
    チャット画面を表現する Page Object。

    想定フロー:
      1. LoginPage でログイン完了
      2. ChatPage を初期化
      3. wait_for_ready() で画面準備完了を待つ
      4. ask() で質問→応答取得
    """

    # 送信ボタンのラベル候補（必要に応じて拡張）
    SEND_LABELS: List[str] = ["送信", "送る", "投稿"]

    def __init__(self, page: Page, timeout: int = 20_000) -> None:
        """
        :param page: Playwright Page
        :param timeout: UI 操作のデフォルトタイムアウト（ミリ秒）
        """
        super().__init__(page, timeout=timeout)

    # ------------------------------------------------------------------
    # ロケータ取得用ヘルパー
    # ------------------------------------------------------------------
    @property
    def _input_locator(self) -> Locator:
        """
        チャット入力欄のロケータ。
        - data-testid="chat-input" を優先
        """
        return self.page.get_by_test_id("chat-input")

    @property
    def _send_locator(self) -> Locator:
        """
        送信ボタンのロケータ。
        - data-testid="chat-send" を優先
        """
        return self.page.get_by_test_id("chat-send")

    @property
    def _message_list_locator(self) -> Locator:
        """
        LLM からのメッセージ一覧のロケータ。
        - data-testid="message" が付与された要素のリストを想定
        """
        return self.page.locator("[data-testid='message']")

    # ------------------------------------------------------------------
    # 画面準備完了待ち
    # ------------------------------------------------------------------
    async def wait_for_ready(self) -> None:
        """
        チャット画面が操作可能になるまで待機する。

        ここでは「入力欄が表示されていること」で準備完了とみなす。
        """
        await self._input_locator.wait_for(
            state="visible",
            timeout=self.timeout,
        )

    # ------------------------------------------------------------------
    # 入力・送信操作
    # ------------------------------------------------------------------
    async def input_message(
        self,
        text: str,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        質問文を入力する。

        :param text: ユーザが送信する質問文
        :param evidence_dir: 操作失敗時の証跡保存ディレクトリ（任意）
        """
        locator = self._input_locator
        await self.safe_fill(
            locator,
            text,
            evidence_dir=evidence_dir,
            label="chat_input_error",
        )

    async def click_send(
        self,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        送信ボタンをクリックする。

        :param evidence_dir: 操作失敗時の証跡保存ディレクトリ（任意）
        """
        locator = self._send_locator
        await self.safe_click(
            locator,
            evidence_dir=evidence_dir,
            label="chat_send_error",
        )

    # ------------------------------------------------------------------
    # 応答待ち・最新メッセージ取得
    # ------------------------------------------------------------------
    async def wait_for_response(
        self,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        LLM の応答が安定するまで待機する。

        - networkidle まで待機
        - その後、短い追加待機を入れて DOM 安定を期待する
        """
        try:
            await self.page.wait_for_load_state("networkidle")
            # ネットワークが静かになってから少し待つ（描画の揺れ対策）
            await self.page.wait_for_timeout(500)
        except Exception:
            if evidence_dir is not None:
                try:
                    await self.collect_evidence(evidence_dir, "chat_wait_error")
                except Exception:
                    pass
            raise

    async def get_latest_response(
        self,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> str:
        """
        最新の LLM 応答テキストを取得する。

        :param evidence_dir: 取得失敗時の証跡保存ディレクトリ（任意）
        :return: 最新メッセージのテキスト
        """
        try:
            messages = self._message_list_locator
            last = messages.last
            await last.wait_for(state="visible", timeout=self.timeout)
            return await last.inner_text()
        except Exception:
            if evidence_dir is not None:
                try:
                    await self.collect_evidence(evidence_dir, "chat_extract_error")
                except Exception:
                    pass
            raise

    # ------------------------------------------------------------------
    # 高レベル API
    # ------------------------------------------------------------------
    async def ask(
        self,
        text: str,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> str:
        """
        質問を送り、LLM の応答テキストを返す高レベル API。

        典型的なテストコードからは、このメソッドだけ使えばよい。

        :param text: ユーザ質問
        :param evidence_dir: 各ステップの証跡保存ディレクトリ（任意）
        :return: LLM 応答テキスト
        """
        try:
            # 念のため画面準備完了を待つ
            await self.wait_for_ready()
            await self.input_message(text, evidence_dir=evidence_dir)
            await self.click_send(evidence_dir=evidence_dir)
            await self.wait_for_response(evidence_dir=evidence_dir)
            return await self.get_latest_response(evidence_dir=evidence_dir)
        except Exception:
            if evidence_dir is not None:
                try:
                    await self.collect_evidence(evidence_dir, "ask_error")
                except Exception:
                    pass
            raise
