# ==========================================================
# ChatPage v0.5  （Qommons.AI 2025-12 DOM 完全対応）
# ==========================================================

from .base_page import BasePage


class ChatPage(BasePage):
    """
    チャット画面 PageObject（DOM完全解析版）
    - 入力欄:   #message
    - 送信ボタン: #chat-send-button
    - 最新メッセージ: div[id^='message-item-']
    - 本文:         div[id^='markdown-']
    """

    # 入力欄
    @property
    def input_box(self):
        return self.page.locator("#message")

    # 送信ボタン
    @property
    def send_button(self):
        return self.page.locator("#chat-send-button")

    # 最新のメッセージItem全体
    @property
    def last_message_item(self):
        return self.page.locator("div[id^='message-item-']").last

    # 最新メッセージの本文（markdown内テキスト）
    @property
    def last_message_content(self):
        # 最新メッセージの中の markdown-<n> を探す
        return self.last_message_item.locator("div[id^='markdown-']")

    # ------------------------------------------------------
    # API
    # ------------------------------------------------------
    def input_message(self, text: str, *, evidence_dir=None):
        self.safe_fill(
            self.input_box,
            text,
            evidence_dir=evidence_dir,
            label="chat_input_error",
        )

    def send(self, *, evidence_dir=None):
        self.safe_click(
            self.send_button,
            evidence_dir=evidence_dir,
            label="chat_send_error",
        )

    def ask(self, text: str, *, evidence_dir=None):
        # 送信前に既存メッセージ数を取得（新規応答を検出する用）
        before_count = self.page.locator("div[id^='message-item-']").count()

        # 入力 & 送信
        self.input_message(text, evidence_dir=evidence_dir)
        self.send(evidence_dir=evidence_dir)

        # 応答待ち：メッセージ数が増えるのを待つ
        self.page.wait_for_function(
            """(before) => {
                return document.querySelectorAll("div[id^='message-item-']").length > before;
            }""",
            arg=before_count,
            timeout=self.timeout
        )

        # 安定化
        self.page.wait_for_timeout(500)

        # 最新メッセージ本文を抽出
        content = self.last_message_content.inner_text()

        return content.strip()
