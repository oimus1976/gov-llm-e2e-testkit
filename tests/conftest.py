import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.env_loader import load_env
from playwright.sync_api import sync_playwright

# -------------------------------
# env.yaml ロード
# -------------------------------
@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config, options


# -------------------------------
# Playwright browser（Sync版）
# -------------------------------
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


# -------------------------------
# context fixture（Sync版）
# -------------------------------
@pytest.fixture(scope="function")
def context(browser, env_config):
    config, _ = env_config
    timeout_ms = config["browser"]["page_timeout_ms"]

    context = browser.new_context()
    context.set_default_timeout(timeout_ms)
    yield context
    context.close()


# -------------------------------
# page fixture（Sync版）
# -------------------------------
@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


# -------------------------------
# ログディレクトリ生成
# -------------------------------
@pytest.fixture(scope="function")
def case_dirs():
    now = datetime.now(timezone(timedelta(hours=9)))
    ymd = now.strftime("%Y%m%d")

    base = Path("logs")
    d1 = base / ymd
    d2 = base / "assets" / ymd

    d1.mkdir(parents=True, exist_ok=True)
    d2.mkdir(parents=True, exist_ok=True)

    return d1, d2
