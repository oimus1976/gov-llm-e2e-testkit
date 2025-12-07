# tests/pages/login_page.py
# gov-llm-e2e-testkit LoginPage (v0.1)
# 参照設計書:
# - Design_LoginPage_v0.1
# - Design_BasePage_v0.1
# - Locator_Guide_v0.2

import re
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class LoginPage(BasePage):
    """
    ログイン画面専用 Page Object。
    - ユーザーID入力
    - パスワード入力
    - ログインボタン押下
    - ログイン成功判定
    を担当する。
    """

    LOGIN_LABELS = ["ログイン", "LOGIN", "Sign In", "SignIn"]

    # ---------------------------------------------------------
    # 1. username 入力
    # ---------------------------------------------------------
    async def input_username(self, username: str):
        field = await self.find(role="textbox", name="ユーザーID")
        await self.safe_fill(field, username)

    # ---------------------------------------------------------
    # 2. password 入力
    # ---------------------------------------------------------
    async def input_password(self, password: str):
        field = await self.find(role="textbox", name="パスワード")
        await self.safe_fill(field, password)

    # ---------------------------------------------------------
    # 3. login ボタンクリック
    # ---------------------------------------------------------
    async def click_login(self):
        pattern = "|".join(self.LOGIN_LABELS)
        btn = await self.find(role="button", name=re.compile(pattern))
        await self.safe_click(btn)

    # ---------------------------------------------------------
    # 4. ログイン成功（ChatPage表示）を待機
    # ---------------------------------------------------------
    async def wait_for_login_success(self):
        """
        ChatPage の質問入力欄（role='textbox', name='質問'）が
        出現することでログイン成功と判断する。
        """
        chat_input = await self.find(role="textbox", name="質問")

        try:
            await chat_input.wait_for(state="visible", timeout=self.timeout)
        except PlaywrightTimeoutError:
            raise Exception("Login success could not be confirmed within timeout.")

    # ---------------------------------------------------------
    # 5. 高レベル API：ログイン処理全体
    # ---------------------------------------------------------
    async def login(self, username: str, password: str):
        await self.input_username(username)
        await self.input_password(password)
        await self.click_login()
        await self.wait_for_login_success()
