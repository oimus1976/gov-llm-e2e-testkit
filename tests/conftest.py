# ---------------------------------------------------------
# conftest.py  -- pytest Execution Layer v0.2
# gov-llm-e2e-testkit
#
# v0.2 のポイント
#  - case_dirs fixture によりテストケース単位で evidence_dir を生成
#  - PageObject v0.2 (safe_click / safe_fill / collect_evidence) と統合
#  - INTERNET / LGWAN の timeout を page.default_timeout に反映
# ---------------------------------------------------------

import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

from playwright.async_api import async_playwright

from src.env_loader import load_env
from src.log_writer import ensure_log_dirs   # ★ pytest v0.2 の中心機能


# ---------------------------------------------------------
# 1. env_config
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def env_config():
    """
    config, options の tuple を返す（仕様通り）
    config には profile / browser などの環境設定
    options には retry_policy / log_dir などの実行オプション
    """
    config, options = load_env()
    return config, options


# ---------------------------------------------------------
# 2. browser fixture
# ---------------------------------------------------------
@pytest.fixture(scope="session")
async def browser(env_config):
    config, _ = env_config

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=config["browser"]["headless"]
        )
        yield browser
        await browser.close()


# ---------------------------------------------------------
# 3. log_base_dir
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def log_base_dir(env_config):
    """
    log_writer が使用する logs/ ディレクトリの基準パス
    env.options.log_dir に従う
    """
    config, options = env_config
    log_dir = options.get("log_dir", "logs")
    return Path(log_dir)


# ---------------------------------------------------------
# 4. page fixture
# ---------------------------------------------------------
@pytest.fixture
async def page(browser, env_config):
    """
    PageObject が参照する Playwright Page を生成する。
    LGWAN / INTERNET の timeout は page.default_timeout に統一して反映。
    """
    config, _ = env_config

    context = await browser.new_context()
    page = await context.new_page()

    page.set_default_timeout(config["browser"]["page_timeout_ms"])

    yield page
    await context.close()


# ---------------------------------------------------------
# 5. case_dirs fixture（pytest v0.2 の最重要追加）
# ---------------------------------------------------------
@pytest.fixture
def case_dirs(log_base_dir):
    """
    case_id と timestamp から以下を生成する:
      - case_log_dir     : Markdown ログの保存先
      - case_assets_dir  : スクリーンショット / DOM evidence の保存先

    使用例:
        now = datetime.now(JST)
        case_log_dir, case_assets_dir = case_dirs("SMOKE_001", now)

        answer = await chat_page.ask(
            "こんにちは",
            evidence_dir=case_assets_dir
        )
    """

    def _make(case_id: str, now: datetime):
        return ensure_log_dirs(log_base_dir, case_id, now)

    return _make
