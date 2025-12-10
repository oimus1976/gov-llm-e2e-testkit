# ---------------------------------------------------------
# LoginPage v0.3  (gov-llm-e2e-testkit)
# Sync Playwright 対応 / BasePage v0.2 準拠
# 最終更新: 2025-12-10
# ---------------------------------------------------------

from .base_page import BasePage


class LoginPage(BasePage):
    """ログインページを操作する PageObject (v0.3, sync版)"""

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
    #  - ID/PW 入力
    #  - ログインボタン押下
    #  - ログイン成功まで待機
    # ------------------------------
    def login(self, username: str, password: str, *, evidence_dir=None) -> None:
        user = self.username_input()
        pwd = self.password_input()
        btn = self.login_button()

        self.safe_fill(user, username, evidence_dir=evidence_dir, label="login_username_error")
        self.safe_fill(pwd, password, evidence_dir=evidence_dir, label="login_password_error")
        self.safe_click(btn, evidence_dir=evidence_dir, label="login_button_error")

        # 成功判定まで含めることで、後続ステップの安定性を確保
        self.wait_for_login_success(evidence_dir=evidence_dir)

    # ------------------------------
    # 成功判定（SPAなので URL は変わらず、
    # メニューのカード出現で判断する）
    # ------------------------------
    def wait_for_login_success(self, *, evidence_dir=None) -> None:
        try:
            # ログイン後はメニュー画面に data-slot="card" が出現する想定
            locator = self.page.locator("div[data-slot='card']").first
            locator.wait_for(state="visible", timeout=self.timeout)
        except Exception:
            if evidence_dir:
                self.collect_evidence(evidence_dir, "login_failed")
            raise
