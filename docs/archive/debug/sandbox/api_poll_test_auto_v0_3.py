# ---------------------------------------------------------
# api_poll_test_auto_v0_3.py
#   CHAT_ID / USER_ID を自動取得し、
#   env.yaml の username/password を利用してログインする正式版
# ---------------------------------------------------------

import re
import time
import requests
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage


def main():

    # ----------------------------------------------
    # 0. 証跡ディレクトリ
    # ----------------------------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/api_poll_auto_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------
    # 1. env.yaml 読み込み
    # ----------------------------------------------
    config, _ = load_env()

    BASE_URL = config["url"]              # https://qommons.ai/login
    USERNAME = config["username"]
    PASSWORD = config["password"]
    API_BASE = BASE_URL.replace("/login", "") + "/api/v1"

    print("[info] env loaded:")
    print(" URL      =", BASE_URL)
    print(" username =", USERNAME)

    # ----------------------------------------------
    # 2. Playwright 起動
    # ----------------------------------------------
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # -------------------------------------------------
        # ★ context レベル request フック（USER_ID 捕獲）
        # -------------------------------------------------
        user_id = None

        def on_request(req):
            nonlocal user_id
            # GET /api/v1/chat/<uuid>/messages に USER_ID が載る
            if "/api/v1/chat/" in req.url and req.method == "GET":
                hdr = req.headers
                if "x-user-id" in hdr:
                    user_id = hdr["x-user-id"]

        context.on("request", on_request)

        # -------------------------------------------------
        # 3. page を作る（フック後）
        # -------------------------------------------------
        page = context.new_page()

        # -------------------------------------------------
        # 4. LoginPage でログイン
        # -------------------------------------------------
        login = LoginPage(page, config)
        login.open()
        login.login()

        print(f"[debug] after login URL = {page.url}")

        # -------------------------------------------------
        # 5. ChatSelectPage → CHAT_ID 抽出
        # -------------------------------------------------
        selector = ChatSelectPage(page)
        selector.open_ai("プライベートナレッジ")

        page.wait_for_url(re.compile(r"/chat/[^/]+$"))
        print("[debug] URL after select:", page.url)

        m = re.search(r"/chat/([0-9a-fA-F-]+)$", page.url)
        chat_id = m.group(1)
        print("[OK] CHAT_ID =", chat_id)

        # -------------------------------------------------
        # 6. USER_ID を待機（最大 5 秒）
        # -------------------------------------------------
        for _ in range(50):
            if user_id:
                break
            time.sleep(0.1)

        if not user_id:
            raise RuntimeError("USER_ID could not be captured")

        print("[OK] USER_ID =", user_id)

        # -------------------------------------------------
        # 7. POST → 質問送信
        # -------------------------------------------------
        question = "かつらぎ町について教えて"
        print(f"[POST] {question}")

        res = requests.post(
            f"{API_BASE}/chat/{chat_id}/messages",
            json={"content": question},
            headers={"x-user-id": user_id},
        )
        print("[POST status] =", res.status_code)

        # -------------------------------------------------
        # 8. GET polling → 回答確定まで待機
        # -------------------------------------------------
        print("[POLL] waiting for assistant response...")

        start = time.time()
        last_text = ""

        while True:
            res = requests.get(
                f"{API_BASE}/chat/{chat_id}/messages",
                headers={"x-user-id": user_id},
            )
            data = res.json()

            msgs = data.get("data", {}).get("messages", [])
            assistant_msgs = [m for m in msgs if m["role"] == "assistant"]

            if assistant_msgs:
                last = assistant_msgs[-1]["content"]
                if last and last != "回答を作成中...":
                    print("\n=== FINAL ANSWER ===")
                    print(last)
                    print("====================")
                    break
                last_text = last

            if time.time() - start > 60:
                raise RuntimeError(f"Timeout waiting for answer. last_text={last_text!r}")

            time.sleep(1)

        browser.close()


if __name__ == "__main__":
    main()
