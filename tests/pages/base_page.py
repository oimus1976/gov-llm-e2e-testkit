# ==========================================================
# BasePage v0.21  （safe_fill の visible 依存を解消）
# ==========================================================

from __future__ import annotations
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import time


class BasePage:
    """
    共通 PageObject 基盤（v0.21）
    - safe_click / safe_fill をより安定化
    """

    def __init__(self, page: Page, config: dict = None, timeout: int = 15000):
        self.page = page
        self.config = config or {}
        self.timeout = timeout

    # --------------------------
    # locate & wait
    # --------------------------
    def wait_for_attached(self, locator):
        try:
            locator.wait_for(state="attached", timeout=self.timeout)
        except PlaywrightTimeoutError:
            raise AssertionError(f"[BasePage] element not attached: {locator}")

    # --------------------------
    # safe_fill（最重要修正）
    # --------------------------
    def safe_fill(self, locator, text: str, *, evidence_dir=None, label="fill_error"):
        """
        旧仕様：visible を待ってから .fill()
        新仕様：attached を待ってから .fill() → visible 依存を排除
        """
        try:
            self.wait_for_attached(locator)
            locator.fill(text)
        except Exception as e:
            if evidence_dir:
                self.collect_evidence(evidence_dir, label)
            raise AssertionError(f"[BasePage] fill failed: {e}")

    # --------------------------
    # safe_click（既存）
    # --------------------------
    def safe_click(self, locator, *, evidence_dir=None, label="click_error"):
        try:
            locator.wait_for(state="attached", timeout=self.timeout)
            locator.click()
        except Exception as e:
            if evidence_dir:
                self.collect_evidence(evidence_dir, label)
            raise AssertionError(f"[BasePage] click failed: {e}")

    # --------------------------
    # evidence
    # --------------------------
    def collect_evidence(self, evidence_dir, name: str):
        ts = int(time.time() * 1000)
        self.page.screenshot(path=f"{evidence_dir}/{name}_{ts}.png")
        with open(f"{evidence_dir}/{name}_{ts}.html", "w", encoding="utf-8") as f:
            f.write(self.page.content())
