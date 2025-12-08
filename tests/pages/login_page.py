from .base_page import BasePage

class LoginPage(BasePage):

    def login(self, username: str, password: str):
        page = self.page

        # ------- 1) SPA 初期描画の安定化 -------
        # networkidle は SPA に強い
        page.wait_for_load_state("networkidle")

        # ------- 2) ログインフォーム出現を待つ -------
        page.wait_for_selector("input[name='username']", state="visible")
        page.wait_for_selector("input[name='password']", state="visible")

        # ------- 3) デバッグ：実際に存在するHTMLを確認 -------
        print("\n=== LOGIN PAGE DEBUG ===")
        print("URL BEFORE LOGIN:", page.url)
        print("USERNAME FIELD (before fill):", page.get_attribute("input[name='username']", "value"))
        print("PASSWORD FIELD (before fill):", page.get_attribute("input[name='password']", "value"))

        # ------- 4) 入力 -------
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)

        # デバッグ（入力後に再確認）
        print("USERNAME FIELD (after fill):", page.get_attribute("input[name='username']", "value"))
        print("PASSWORD FIELD (after fill):", page.get_attribute("input[name='password']", "value"))

        # ------- 5) ログインボタンを押す（遷移を待たない） -------
        # SPA のログインは navigation しないため no_wait_after=True が必須
        page.click("button[type='submit']", no_wait_after=True)

        # ------- 6) SPA が内部遷移し始めるまで少し待つ -------
        page.wait_for_timeout(1500)

        # ------- 7) デバッグ出力 -------
        print("URL AFTER LOGIN CLICK:", page.url)

        # スクショを取る（デバッグ用）
        page.screenshot(path="after_login.png", full_page=True)
