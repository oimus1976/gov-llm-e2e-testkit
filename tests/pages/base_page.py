# ==========================================================
# BasePage v0.2  （Sync Playwright）
# ==========================================================

from __future__ import annotations
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time


class BasePage:
    """
    共通 PageObject 基盤（v0.2）
    - safe_click / safe_type / safe_wait_for / safe_get_text
    - page, config の2責務
    """

    def __init__(self, page: Page, config: dict):
        self.page = page
        self.config = config
        self.timeout_ms = config.get("browser", {}).get("page_timeout_ms", 15000)

    # --------------------------
    # 基本操作
    # --------------------------

    def safe_wait_for(self, locator: str):
        try:
            return self.page.wait_for_selector(locator, timeout=self.timeout_ms)
        except PlaywrightTimeoutError:
            raise AssertionError(f"[BasePage] selector not found: {locator}")

    def safe_click(self, locator: str):
        el = self.safe_wait_for(locator)
        try:
            el.click()
        except Exception as e:
            raise AssertionError(f"[BasePage] click failed: {locator}: {e}")

    def safe_type(self, locator: str, text: str, delay: int = 20):
        el = self.safe_wait_for(locator)
        try:
            el.fill("")
            el.type(text, delay=delay)
        except Exception as e:
            raise AssertionError(f"[BasePage] type failed: {locator}: {e}")

    def safe_get_text(self, locator: str) -> str:
        el = self.safe_wait_for(locator)
        try:
            return el.inner_text().strip()
        except Exception:
            return ""

    # --------------------------
    # URL 変化待ち
    # --------------------------
    def wait_for_url_change(self, old_url: str, timeout_sec: int = 10):
        start = time.time()
        while time.time() - start < timeout_sec:
            if self.page.url != old_url:
                return
            time.sleep(0.1)
        raise AssertionError(f"[BasePage] URL did not change from {old_url}")
