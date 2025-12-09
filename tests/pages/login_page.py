# tests/pages/login_page.py
from playwright.sync_api import Page
from .base_page import BasePage

class LoginPage(BasePage):
    """Qommons ログインページ"""

    URL = "/login"

    def goto(self):
        self.page.goto(self.full_url(self.URL))
        self.page.wait_for_load_state("networkidle")

    def login(self, username: str, password: str):
        # 入力欄
        user_field = self.page.locator("input[name='username']")
        pass_field = self.page.locator("input[name='password']")
        login_btn  = self.page.locator("#login-button")

        # 入力
        user_field.click()
        user_field.fill(username)

        pass_field.click()
        pass_field.fill(password)

        # ボタンが enabled になるまで待つ
        login_btn.wait_for(state="visible", timeout=5000)
        login_btn.click()

        # 遷移待ち
        self.page.wait_for_url("**/chat", timeout=15000)
        return True
