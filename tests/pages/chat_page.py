# chat_page.py
# gov-llm-e2e-testkit ChatPage (v0.1)
# 参照設計書:
# - Design_ChatPage_v0.1
# - Design_BasePage_v0.1
# - Locator_Guide_v0.2

import re
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class ChatPage(BasePage):
    """
    チャット画面専用 Page Object。
    質問入力 → 送信 → 応答取得 の一連操作を抽象化する。
    """

    # UI文言の変動に備えた送信ボタンの候補（fallback）
    SEND_LABELS = ["送信", "送る", "投稿", "Send", "SEND"]

    # --------------------------------------------
    # 1. 質問入力
    # --------------------------------------------
    async def input_message(self, text: str):
        box = await self.find(role="textbox", name="質問")
        await self.safe_fill(box, text)

    # --------------------------------------------
    # 2. 送信ボタン押下
    # --------------------------------------------
    async def click_send(self):
        # 優先: role='button' name=regex("送信|送る|投稿")
        pattern = "|".join(self.SEND_LABELS)
        btn = await self.find(role="button", name=re.compile(pattern))
        await self.safe_click(btn)

    # --------------------------------------------
    # 3. 応答を待機（loading → メッセージ出現）
    # --------------------------------------------
    async def wait_for_response(self):
        # loading がある場合は BasePage 側で検知してもらう
        await self.wait_for_loading()

        # メッセージが追加されるまで待つ
        latest_msg = self.page.locator("[data-testid='message']").last
        try:
            await latest_msg.wait_for(state="visible", timeout=self.timeout)
        except PlaywrightTimeoutError:
            raise Exception("LLM response did not appear within timeout.")

        # 若干の安定化待ち
        await self.page.wait_for_timeout(300)

    # --------------------------------------------
    # 4. 最新メッセージの取得
    # --------------------------------------------
    async def get_latest_response(self) -> str:
        # data-testid を最優先
        msg = self.page.locator("[data-testid='message']").last

        try:
            await msg.wait_for(state="visible", timeout=self.timeout)
            return await msg.inner_text()
        except PlaywrightTimeoutError:
            # fallback: role='article'
            fallback = self.page.get_by_role("article").last
            await fallback.wait_for(state="visible", timeout=self.timeout)
            return await fallback.inner_text()

    # --------------------------------------------
    # 5. 高レベルAPI：質問して応答を取得する
    # --------------------------------------------
    async def ask(self, text: str) -> str:
        await self.input_message(text)
        await self.click_send()
        await self.wait_for_response()
        return await self.get_latest_response()

    # --------------------------------------------
    # 6. 画面表示完了（LoginPage→ChatPage遷移後に呼ばれる想定）
    # --------------------------------------------
    async def wait_for_ready(self):
        # ChatPage の textbox が出現すれば画面準備完了と判断
        box = await self.find(role="textbox", name="質問")
        await box.wait_for(state="visible", timeout=self.timeout)
