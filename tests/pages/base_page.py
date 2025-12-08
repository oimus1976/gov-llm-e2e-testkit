# tests/pages/base_page.py
"""
BasePage v0.2

- Playwright Page のラッパとして共通の UI 操作を提供する
- safe_* 系メソッドで UI 操作失敗時に証跡（スクリーンショット + DOM）を収集する
- LoginPage / ChatPage など他の PageObject の基底クラスとなる

設計書:
- docs/Design_BasePage_v0.2.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Union

from playwright.async_api import Page, Locator


PathLike = Union[str, Path]


class BasePage:
    """Playwright Page に対する共通ユーティリティを提供する基底クラス。"""

    def __init__(self, page: Page, timeout: int = 20_000) -> None:
        """
        :param page: Playwright の Page インスタンス
        :param timeout: 各種操作時のデフォルトタイムアウト（ミリ秒）
        """
        self.page = page
        self.timeout = timeout

    # ------------------------------------------------------------------
    # 基本ユーティリティ
    # ------------------------------------------------------------------
    def find(self, selector: str) -> Locator:
        """
        CSS / text / data-testid など任意の selector から Locator を返す。

        子クラスからの利用を想定。
        """
        return self.page.locator(selector)

    async def screenshot(self, path: PathLike) -> None:
        """
        単純なスクリーンショット取得。

        :param path: 保存先パス
        """
        await self.page.screenshot(path=str(path))

    # ------------------------------------------------------------------
    # 証跡収集（screenshot + DOM）
    # ------------------------------------------------------------------
    async def collect_evidence(self, evidence_dir: PathLike, label: str) -> Dict[str, str]:
        """
        UI 操作失敗時などに、スクリーンショットと DOM を取得して保存する。

        :param evidence_dir: 証跡保存用ディレクトリ
        :param label: ファイル名のプレフィックス（例: "click_error"）
        :return: {"screenshot": <pngパス>, "dom": <htmlパス>}
        """
        evidence_dir = Path(evidence_dir)
        evidence_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = evidence_dir / f"{label}.png"
        dom_path = evidence_dir / f"{label}.html"

        # スクリーンショット取得
        await self.page.screenshot(path=str(screenshot_path))

        # DOM 取得
        html = await self.page.content()
        dom_path.write_text(html, encoding="utf-8")

        return {
            "screenshot": str(screenshot_path),
            "dom": str(dom_path),
        }

    # ------------------------------------------------------------------
    # 安全な UI 操作（safe_* 系）
    # ------------------------------------------------------------------
    async def safe_click(
        self,
        locator: Locator,
        *,
        evidence_dir: Optional[PathLike] = None,
        label: str = "click_error",
    ) -> None:
        """
        クリック操作を安全に行うラッパ。

        - 要素が visible になるまで待機
        - 失敗時に証跡（スクリーンショット + DOM）を収集
        - その後、例外を再送出して pytest 側に伝える

        :param locator: 操作対象の Locator
        :param evidence_dir: 証跡保存先ディレクトリ（None の場合は証跡を取らない）
        :param label: 証跡ファイル名のプレフィックス
        """
        try:
            await locator.wait_for(state="visible", timeout=self.timeout)
            await locator.click()
        except Exception:
            if evidence_dir is not None:
                try:
                    await self.collect_evidence(evidence_dir, label)
                except Exception:
                    # 証跡収集の失敗自体は握りつぶさずにログ等へ回す余地を残す。
                    # ここでは再度 raise して pytest に任せる。
                    pass
            raise

    async def safe_fill(
        self,
        locator: Locator,
        text: str,
        *,
        evidence_dir: Optional[PathLike] = None,
        label: str = "fill_error",
    ) -> None:
        """
        テキスト入力を安全に行うラッパ。

        - 要素が visible になるまで待機
        - 失敗時に証跡収集
        - その後、例外を再送出

        :param locator: 操作対象の Locator
        :param text: 入力するテキスト
        :param evidence_dir: 証跡保存先ディレクトリ（None の場合は証跡を取らない）
        :param label: 証跡ファイル名のプレフィックス
        """
        try:
            await locator.wait_for(state="visible", timeout=self.timeout)
            await locator.fill(text)
        except Exception:
            if evidence_dir is not None:
                try:
                    await self.collect_evidence(evidence_dir, label)
                except Exception:
                    pass
            raise
