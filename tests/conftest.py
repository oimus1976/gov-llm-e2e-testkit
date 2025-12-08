# tests/conftest.py
import pytest
from playwright.async_api import async_playwright
from pathlib import Path
from src.env_loader import load_env


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
    config, options = env_config

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
    config, options = env_config

    context = await browser.new_context()
    page = await context.new_page()

    # ★ LGWAN / INTERNET の timeout を適用（仕様準拠）
    page.set_default_timeout(config["browser"]["page_timeout_ms"])

    yield page
    await context.close()
