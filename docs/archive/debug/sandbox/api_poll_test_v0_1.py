# ---------------------------------------------------------
# api_poll_test_v0_1.py
#   Qommons API が「POST → 完成回答の GET」で取得できるか
#   を検証するための最小スクリプト。
#
# Playwright なし / DOM なし / UI 無視
# ---------------------------------------------------------

import time
import requests
from src.env_loader import load_env


def post_user_message(api_url: str, chat_id: str, user_message: str, headers):
    """メッセージ送信（UI を使わず API 経由）"""
    url = f"{api_url}/chat/{chat_id}/messages"

    payload = {
        "content": user_message
    }

    print(f"[POST] → {url}")
    r = requests.post(url, json=payload, headers=headers)
    print("[POST] status:", r.status_code)
    return r


def fetch_messages(api_url: str, chat_id: str, headers):
    """assistant の最新回答を GET"""
    url = f"{api_url}/chat/{chat_id}/messages"
    r = requests.get(url, headers=headers)
    print("[GET] status:", r.status_code)
    return r.json()


def poll_until_answer(api_url, chat_id, headers, timeout=60):
    """assistant の content が空でない回答になるまで polling"""
    print("[POLL] Waiting for assistant response...")

    start = time.time()
    last_content = None

    while True:
        data = fetch_messages(api_url, chat_id, headers)

        msgs = data.get("data", {}).get("messages", [])
        assistant_msgs = [m for m in msgs if m["role"] == "assistant"]

        if assistant_msgs:
            last = assistant_msgs[-1]["content"]

            if last and last != "" and last != "回答を作成中...":
                print("\n=== ASSISTANT FINAL ANSWER ===")
                print(last)
                print("================================")
                return last  # 成功

            last_content = last

        if time.time() - start > timeout:
            raise RuntimeError(f"Timeout. last_content={last_content!r}")

        time.sleep(1)  # 1秒ごとに polling


def main():
    # --------------------------------------------
    # env.yaml の読み込み
    # --------------------------------------------
    config, _ = load_env()

    api_url = config["api_base"]  # env.yaml に要定義
    chat_id = config["chat_id"]   # 既存チャット or 適当に固定
    user_id = config["user_id"]   # Cookie ではなくヘッダで渡す

    headers = {
        "x-user-id": user_id,
        "Content-Type": "application/json"
    }

    question = "かつらぎ町について教えて"

    print("\n=== STEP 1: POST user message ===")
    post_user_message(api_url, chat_id, question, headers)

    print("\n=== STEP 2: POLL until assistant reply ===")
    answer = poll_until_answer(api_url, chat_id, headers)

    print("\n=== RESULT: Assistant reply obtained via API ONLY ===")
    print(answer)


if __name__ == "__main__":
    main()
