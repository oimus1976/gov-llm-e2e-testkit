# ---------------------------------------------------------
# api_poll_test_auto_v0_1.py
#   CHAT_ID / USER_ID を自動取得する案Cの実証スクリプト
# ---------------------------------------------------------

import re
import time
import requests
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright


def main():

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/api_poll_auto_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # -------------------------------------------------
        # USER_ID を自動取得する仕掛け
        # -------------------------------------------------
        user_id = None

        def on_request(req):
            nonlocal user_id

            # Chat API の最初の GET リクエストを監視
            if "api/v1/chat" in req.url and req.method == "GET":
                hdr = req.headers
                if "x-user-id" in hdr:
                    user_id = hdr["x-user-id"]

        page.on("request", on_request)

        # -------------------------------------------------
        # 1. ログイン
        # -------------------------------------------------
        page.goto("https://qommons.ai/login")
        page.fill("input[name='username']", "test_e2e@和歌山県_かつらぎ町")
        page.fill("input[name='password']", "1234Test!")
        page.click("#login-button")

        page.wait_for_selector("div[data-slot='card']")

        # -------------------------------------------------
        # 2. チャット選択 → CHAT_ID 自動抽出
        # -------------------------------------------------
        page.locator("div[data-slot='card']", has_text="プライベートナレッジ").click()

        page.wait_for_url(re.compile(r"/chat/[^/]+$"))
        print("[debug] URL after select:", page.url)

        m = re.search(r"/chat/([0-9a-fA-F-]+)$", page.url)
        chat_id = m.group(1)

        print("[OK] CHAT_ID =", chat_id)

        # USER_ID が取れるまで最大5秒待つ
        for _ in range(50):
            if user_id:
                break
            time.sleep(0.1)

        if not user_id:
            raise RuntimeError("USER_ID could not be captured")

        print("[OK] USER_ID =", user_id)

        # -------------------------------------------------
        # 3. UIを使わず API で質問送信（POST）
        # -------------------------------------------------
        API_BASE = "https://qommons.ai/api/v1"

        question = "かつらぎ町について教えて"
        print(f"[POST] {question}")

        res = requests.post(
            f"{API_BASE}/chat/{chat_id}/messages",
            json={"content": question},
            headers={"x-user-id": user_id},
        )
        print("[POST] status =", res.status_code)

        # -------------------------------------------------
        # 4. Polling GET で回答を取得
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
                raise RuntimeError(f"Timeout waiting for answer, last={last_text!r}")

            time.sleep(1)

        browser.close()


if __name__ == "__main__":
    main()
