# ==========================================================
# ChatPage v0.7  （2025-12 DOM 実証版）
# ----------------------------------------------------------
# DOM 実態：
#   - AIメッセージ:  div.message-received
#   - 本文:          div.markdown
# ==========================================================

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class ChatPage(BasePage):
    """Qommons.AI 個別チャット画面"""

    RESPONSE_POLL_INTERVAL_MS = 200
    RESPONSE_POLL_MAX_STEPS = 70  # 70 * 200ms = 最大14秒

    # -----------------------------------------------------
    # DOM Locators
    # -----------------------------------------------------
    def input_box(self):
        return self.page.locator("#message")

    def send_button(self):
        return self.page.locator("#chat-send-button")

    def ai_bubbles(self):
        """実 DOM：AI 側メッセージは常に .message-received"""
        return self.page.locator("div.message-received")

    # -----------------------------------------------------
    # 基本操作
    # -----------------------------------------------------
    def input_message(self, text, *, evidence_dir=None):
        self.safe_fill(
            self.input_box(),
            text,
            evidence_dir=evidence_dir,
            label="input_message_error",
        )

    def click_send(self, *, evidence_dir=None):
        self.safe_click(
            self.send_button(),
            evidence_dir=evidence_dir,
            label="send_button_error",
        )

    # -----------------------------------------------------
    # AI 応答待ち
    # -----------------------------------------------------
    def _wait_for_new_ai_bubble(self, before, *, evidence_dir=None):
        """
        DOM 実態：AI バブルは div.message-received の件数で増える
        """
        try:
            self.page.wait_for_function(
                """(before) => {
                    return document.querySelectorAll("div.message-received").length > before;
                }""",
                arg=before,           # ← 修正ポイント（位置引数 → arg=）
                timeout=60000,
            )
        except PlaywrightTimeoutError as e:
            if evidence_dir:
                self.collect_evidence(evidence_dir, "wait_ai_bubble_timeout")
            raise AssertionError(
                f"[ChatPage] New AI bubble did not appear: {e}"
            )


    def _get_latest_ai_text(self, *, evidence_dir=None):
        bubbles = self.ai_bubbles()
        count = bubbles.count()

        if count == 0:
            raise AssertionError("[ChatPage] No AI bubbles found.")

        last = bubbles.nth(count - 1)
        md = last.locator(".markdown")

        # 内部テキストが確定するまでポーリング
        last_text = ""
        for _ in range(self.RESPONSE_POLL_MAX_STEPS):
            text = md.inner_text().strip()
            last_text = text

            if text and text != "回答を作成中...":
                return text

            self.page.wait_for_timeout(self.RESPONSE_POLL_INTERVAL_MS)

        if evidence_dir:
            self.collect_evidence(evidence_dir, "ai_content_not_ready")

        raise AssertionError(
            f"[ChatPage] AI response text not ready. last_text={last_text!r}"
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------
    def ask(self, message: str, *, evidence_dir=None, timeout=60000):
        """
        Qommons の実装に対応した ask()
        - DOM 上の message-item は増えないため count 比較は使わない
        - 最新バブルの markdown が空 / プレースホルダ から本文に変わる瞬間を監視する
        """

        # 1. 送信
        self.input_message(message, evidence_dir=evidence_dir)
        self.click_send(evidence_dir=evidence_dir)

        # 2. 最新の message-item を取得（常に最後が AI バブル）
        bubble = self.page.locator("div[id^='message-item-']").last
        md = bubble.locator(".markdown")

        # 3. ストリーミング開始を待つ（markdown が空→非空）
        try:
            self.page.wait_for_function(
                """
                (selector) => {
                    const el = document.querySelector(selector);
                    if (!el) return false;
                    const text = el.innerText.trim();
                    return text.length > 0;
                }
                """,
                arg=".markdown",
                timeout=timeout
            )
        except Exception:
            if evidence_dir:
                self.collect_evidence(evidence_dir, "ai_stream_not_started")
            raise RuntimeError("AI stream did not start")

        # 4. 本文確定までポーリング
        for _ in range(120):  # 最大 60 秒
            text = md.inner_text().strip()

            if text and text != "回答を作成中...":
                if evidence_dir:
                    self.collect_evidence(evidence_dir, "ai_answer_ready")
                return text

            self.page.wait_for_timeout(500)

        # 5. タイムアウト
        if evidence_dir:
            self.collect_evidence(evidence_dir, "ai_answer_not_ready")

        raise RuntimeError(f"AI answer did not complete. last_text={text!r}")
