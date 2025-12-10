# ---------------------------------------------------------
# test_api_response_v0_4.py
#
# Qommons が「UI 上では応答しているのに Playwright が取得できない」
# 状況を一次情報で切り分けるための検証スクリプト。
#
# 追加:
#   - DEBUG_KEEP_BROWSER=1 のとき、処理後にブラウザを閉じず保持する。
# ---------------------------------------------------------

import os
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage


# ---------------------------------------------------------
# Debug Flag: DEBUG_KEEP_BROWSER=1 ならブラウザを閉じない
# ---------------------------------------------------------
DEBUG_KEEP_BROWSER = os.getenv("DEBUG_KEEP_BROWSER") == "1"


def main():
    # ----------------------------------------------
    # 1. 証跡ディレクトリ
    # ----------------------------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/api_check_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"[debug] evidence dir = {outdir}")

    # ----------------------------------------------
    # 2. Playwright 起動
    # ----------------------------------------------
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ----------------------------------------------
        # 3. env 読み込み
        # ----------------------------------------------
        config, _ = load_env()

        # ----------------------------------------------
        # 4. ログイン
        # ----------------------------------------------
        login = LoginPage(page, config)

        login.open()
        login.login(evidence_dir=outdir)

        print(f"[step] after login: url = {page.url}")

        page.screenshot(path=outdir / "after_login.png")
        outdir.joinpath("after_login.html").write_text(page.content(), encoding="utf-8")

        # ----------------------------------------------
        # 5. チャット選択画面 (/chat)
        # ----------------------------------------------
        selector = ChatSelectPage(page, config, timeout=15000)
        selector.open_ai("プライベートナレッジ", evidence_dir=outdir)

        print(f"[step] after select: url = {page.url}")

        page.screenshot(path=outdir / "after_select.png")
        outdir.joinpath("after_select.html").write_text(page.content(), encoding="utf-8")

        # ----------------------------------------------
        # 6. ChatPage
        # ----------------------------------------------
        chat = ChatPage(page, config, timeout=15000)

        question = "かつらぎ町について教えて"
        print(f"[send] {question}")

        # ----------------------------------------------
        # 7. ask() 実行 → 回答取得
        # ----------------------------------------------
        try:
            answer = chat.ask(question, evidence_dir=outdir)
            print("========================================")
            print("[SUCCESS] AI answered:")
            print(answer)
            print("========================================")
        except Exception as e:
            print("========================================")
            print("[ERROR] AI did not answer properly.")
            print(e)
            print("========================================")

        # ----------------------------------------------
        # 8. ブラウザ終了 or 保持
        # ----------------------------------------------
        if DEBUG_KEEP_BROWSER:
            print("\n[info] DEBUG_KEEP_BROWSER=1 → ブラウザを保持します")
            print("      実画面を見ながら調査できます。")
            input("      Enter を押すと終了します...")
        else:
            browser.close()


if __name__ == "__main__":
    main()
