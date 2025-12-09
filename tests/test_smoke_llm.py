import pytest
from datetime import datetime, timezone, timedelta

from tests.pages.login_page import LoginPage
from tests.pages.chat_page import ChatPage

JST = timezone(timedelta(hours=9))


def test_smoke_llm(page, env_config):
    config, _ = env_config

    print("\n=== SMOKE TEST START ===")

    # ログイン画面へ
    page.goto(config["url"])
    print("INITIAL URL:", page.url)

    login = LoginPage(page, config)
    login.login(config["username"], config["password"])

    print("AFTER LOGIN URL:", page.url)
    assert "/chat" in page.url

    chat = ChatPage(page, config)
    answer = chat.ask("テスト質問です")
    print("ANSWER:", answer)
