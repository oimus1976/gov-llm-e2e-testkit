# tests/test_smoke_llm.py
# gov-llm-e2e-testkit Smoke Test (v0.1)
# 目的：ログイン → 質問 → 応答取得 が成立することのみを確認
# UI変動に影響されにくい最小アクションのみを実施する

import pytest
import asyncio
from playwright.async_api import async_playwright

from tests.pages.login_page import LoginPage
from tests.pages.chat_page import ChatPage


@pytest.mark.asyncio
async def test_smoke_llm():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # Timeout 設定（将来 env.yaml で管理）
        TIMEOUT = 20000

        # -------------------------
        # 1. LoginPage 初期化
        # -------------------------
        login = LoginPage(page, timeout=TIMEOUT)

        # テスト用アカウント（暫定）
        # 将来は config/env.yaml から secure に読み込む
        USERNAME = "test-user"
        PASSWORD = "test-pass"

        await page.goto("https://example.com/login")  # 実環境 URL を後で設定
        await login.login(USERNAME, PASSWORD)

        # -------------------------
        # 2. ChatPage 初期化
        # -------------------------
        chat = ChatPage(page, timeout=TIMEOUT)
        await chat.wait_for_ready()

        # -------------------------
        # 3. ask → 応答チェック
        # -------------------------
        response = await chat.ask("これは動作テストです。")

        assert isinstance(response, str)
        assert len(response.strip()) > 0, "LLM が応答を返しませんでした。"

        await browser.close()
