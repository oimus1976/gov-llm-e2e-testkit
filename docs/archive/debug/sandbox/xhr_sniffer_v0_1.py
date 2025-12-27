# ---------------------------------------------------------
# xhr_sniffer_v0_1.py
# Qommons の回答完了シグナルを XHR から解析するためのスニファー
# ---------------------------------------------------------

import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/xhr_capture_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)

    log_path = outdir / "xhr_log.jsonl"
    print(f"[debug] XHR capture → {log_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # -------------------------------------------------
        # 1. XHR / fetch をすべてフックする
        # -------------------------------------------------
        def on_request(req):
            if req.resource_type == "xhr" or req.resource_type == "fetch":
                entry = {
                    "type": "request",
                    "url": req.url,
                    "method": req.method,
                    "postData": req.post_data,
                    "headers": req.headers,
                }
                log_path.write_text("", encoding="utf-8", errors="ignore")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        def on_response(res):
            if res.request.resource_type in ("xhr", "fetch"):
                try:
                    body = res.text()
                except Exception:
                    body = "<non-text or binary>"

                entry = {
                    "type": "response",
                    "url": res.url,
                    "status": res.status,
                    "body": body,
                    "headers": res.headers,
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        page.on("request", on_request)
        page.on("response", on_response)

        # -------------------------------------------------
        # 2. Qommons へログイン（環境変数ベース）
        # -------------------------------------------------
        from src.env_loader import load_env
        from tests.pages.login_page import LoginPage
        from tests.pages.chat_select_page import ChatSelectPage
        from tests.pages.chat_page import ChatPage

        config, _ = load_env()

        login = LoginPage(page, config)
        login.open()
        login.login()

        selector = ChatSelectPage(page, timeout=15000)
        selector.open_ai("プライベートナレッジ")

        chat = ChatPage(page, config, timeout=15000)

        # -------------------------------------------------
        # 3. 質問を1つ投げてログ収集
        # -------------------------------------------------
        question = "かつらぎ町について教えて"
        print(f"[send] {question}")

        chat.input_message(question)
        chat.click_send()

        print("[info] Collecting XHR for 60 seconds...")
        page.wait_for_timeout(60000)

        print("[done] Check:", log_path)
        browser.close()


if __name__ == "__main__":
    main()
