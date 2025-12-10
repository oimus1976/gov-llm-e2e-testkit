# ---------------------------------------------------------
# LoginPage v0.3.1  (gov-llm-e2e-testkit)
# Sync Playwright 対応 / BasePage v0.2 準拠
# 最終更新: 2025-12-10
# ---------------------------------------------------------

from .base_page import BasePage


class LoginPage(BasePage):
    """ログインページを操作する PageObject (v0.3.1, sync版)"""

    # ------------------------------
    # ページ遷移: open()
    # ------------------------------
    def open(self) -> None:
        """ログインページURLへ遷移する"""
        self.page.goto(self.config["url"])

    # ------------------------------
    # Locator
    # ------------------------------
    def username_input(self):
        return self.page.locator("input[name='username']")

    def password_input(self):
        return self.page.locator("input[name='password']")

    def login_button(self):
        return self.page.locator("#login-button")

    # ------------------------------
    # 高レベルAPI: login()
    #  - config["username"], config["password"] を使用
    #  - SPA の成功判定まで行う
    # ------------------------------
    def login(self, *, evidence_dir=None) -> None:
        user = self.username_input()
        pwd = self.password_input()
        btn = self.login_button()

        username = self.config["username"]
        password = self.config["password"]

        self.safe_fill(user, username, evidence_dir=evidence_dir, label="login_username_error")
        self.safe_fill(pwd, password, evidence_dir=evidence_dir, label="login_password_error")
        self.safe_click(btn, evidence_dir=evidence_dir, label="login_button_error")

        self.wait_for_login_success(evidence_dir=evidence_dir)

    # ------------------------------
    # 成功判定（SPA のため URL ではなく UI 要素で判断）
    # ------------------------------
    def wait_for_login_success(self, *, evidence_dir=None) -> None:
        try:
            locator = self.page.locator("div[data-slot='card']").first
            locator.wait_for(state="visible", timeout=self.timeout)
        except Exception:
            if evidence_dir:
                self.collect_evidence(evidence_dir, "login_failed")
            raise
