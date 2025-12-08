# tests/conftest.py
import pytest
from playwright.async_api import async_playwright
from src.env_loader import load_env


@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config


@pytest.fixture(scope="session")
async def browser(env_config):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=env_config["browser"]["headless"])
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser, env_config):
    context = await browser.new_context()
    page = await context.new_page()

    # ★ LGWAN / INTERNET に応じて timeout をここで適用
    page.set_default_timeout(env_config["browser"]["page_timeout_ms"])

    yield page
    await context.close()
