# base_page.py
# gov-llm-e2e-testkit BasePage (v0.1)
# 参照設計書:
# - Design_playwright_v0.1 :contentReference[oaicite:0]{index=0}
# - Locator_Guide_v0.2 :contentReference[oaicite:1]{index=1}
# - PROJECT_GRAND_RULES v2.0 :contentReference[oaicite:2]{index=2}

import re
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

class BasePage:
    """
    Page Object の基底クラス。
    共通処理のみを実装し、画面固有の処理は Page Object 側に委譲する。
    """

    def __init__(self, page: Page, timeout: int = 15000):
        self.page = page
        self.timeout = timeout  # INTERNET/LGWAN で切替予定（v0.2でenv読み込み）

    # ---------------------------------------------------------
    # 1. locator factory（優先順：role → label → placeholder → aria → testid → css）
    # ---------------------------------------------------------
    async def find(self, role=None, name=None, label=None, placeholder=None,
                   aria=None, testid=None, css=None):
        """
        UI 変動に備えた locator factory（Locator_Guide_v0.2 準拠）
        """
        # role + name
        if role:
            if name:
                return self.page.get_by_role(role, name=name)
            return self.page.get_by_role(role)

        # label
        if label:
            return self.page.get_by_label(label)

        # placeholder
        if placeholder:
            return self.page.get_by_placeholder(placeholder)

        # aria
        if aria:
            return self.page.locator(f"[aria-label='{aria}']")

        # testid
        if testid:
            return self.page.locator(f"[data-testid='{testid}']")

        # css（最終手段）
        if css:
            return self.page.locator(css)

        raise ValueError("No valid locator strategy provided.")

    # ---------------------------------------------------------
    # 2. safe actions（共通のクリック／入力メソッド）
    # ---------------------------------------------------------
    async def safe_click(self, locator):
        try:
            await locator.wait_for(state="visible", timeout=self.timeout)
            await locator.click()
        except PlaywrightTimeoutError:
            raise Exception(f"[safe_click] Locator not clickable within timeout: {locator}")

    async def safe_fill(self, locator, text: str):
        try:
            await locator.wait_for(state="visible", timeout=self.timeout)
            await locator.fill(text)
        except PlaywrightTimeoutError:
            raise Exception(f"[safe_fill] Locator not fillable within timeout: {locator}")

    # ---------------------------------------------------------
    # 3. ページ遷移
    # ---------------------------------------------------------
    async def goto(self, url: str):
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")

    async def wait_for_ready(self):
        """
        各 Page Object 側で override できる“画面表示完了待ち”。
        BasePage では networkidle のみ。
        """
        await self.page.wait_for_load_state("networkidle")

    # ---------------------------------------------------------
    # 4. ローディング検知（Design_BasePage_v0.1 準拠）
    # ---------------------------------------------------------
    async def wait_for_loading(self):
        """
        loading=true が出ている場合 → 消えるまで待つ。
        無ければ即 return。
        """
        loading_selector = "[data-loading='true']"
        loading = self.page.locator(loading_selector)

        try:
            # loading が表示されるまで少し待つ（あれば拾う）
            await loading.wait_for(state="visible", timeout=500)
            # 表示された場合 → 消えるまで待つ
            await loading.wait_for(state="hidden", timeout=self.timeout)
        except PlaywrightTimeoutError:
            # loading が無い場合、または検知できなかった場合はスキップ
            pass

    # ---------------------------------------------------------
    # 5. スクリーンショット（失敗時など）
    # ---------------------------------------------------------
    async def screenshot(self, path: str):
        await self.page.screenshot(path=path)
