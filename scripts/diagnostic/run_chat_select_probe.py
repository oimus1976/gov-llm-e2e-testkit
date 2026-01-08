# scripts/diagnostic/run_chat_select_probe.py
"""
目的:
- ChatSelectPage.open_ai() 実行後、
  Playwright が観測する URL / DOM 状態を記録する
- 成功判定・assert は一切行わない
"""

from playwright.sync_api import sync_playwright
from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage


def main():
    # env.yaml / .env から設定を読む（pytestと同条件）
    config, _ = load_env()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ---- Login ----
        login = LoginPage(page, config)
        login.open()
        login.login()
        print("[probe] URL after login:", page.url)

        # ---- AI Select ----
        select = ChatSelectPage(page, config)
        ai_name = config.get("chat_name", "プライベートナレッジ")
        select.open_ai(ai_name)

        print("[probe] URL after open_ai:", page.url)

        # DOM 全体を保存（あとで diff / grep 用）
        html = page.content()
        with open("chat_select_after.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("[probe] HTML snapshot saved: chat_select_after.html")

        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    main()
