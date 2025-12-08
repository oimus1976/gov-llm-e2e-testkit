# tests/pages/login_page.py
"""
LoginPage v0.2

- ログイン画面の操作を抽象化する Page Object
- BasePage v0.2 の safe_* / collect_evidence を利用し、
  UI 操作失敗時にスクリーンショット＋DOM を自動収集する
- INTERNET / LGWAN 両環境での安定動作を目指す

設計書:
- docs/Design_LoginPage_v0.2.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from playwright.async_api import Page, Locator

from .base_page import BasePage


PathLike = Union[str, Path]


class LoginError(Exception):
    """ログインが成功しなかった場合に送出される例外。"""
    pass


class LoginPage(BasePage):
    """
    ログイン画面を表現する Page Object。

    想定フロー:
      1. テスト側で login ページ URL に遷移
      2. LoginPage を初期化
      3. login() を呼び出して認証を実施
    """

    def __init__(self, page: Page, timeout: int = 20_000) -> None:
        """
        :param page: Playwright Page
        :param timeout: UI 操作のデフォルトタイムアウト（ミリ秒）
        """
        super().__init__(page, timeout=timeout)

    # ------------------------------------------------------------------
    # ロケータ取得用ヘルパー
    # ------------------------------------------------------------------
    @property
    def _username_locator(self) -> Locator:
        """
        ユーザ ID 入力欄のロケータ。
        - data-testid="login-username" を優先
        - 必要に応じてここに fallback ロジックを追加する
        """
        return self.page.get_by_test_id("login-username")

    @property
    def _password_locator(self) -> Locator:
        """
        パスワード入力欄のロケータ。
        - data-testid="login-password" を優先
        """
        return self.page.get_by_test_id("login-password")

    @property
    def _submit_locator(self) -> Locator:
        """
        ログインボタンのロケータ。
        - data-testid="login-submit" を優先
        """
        return self.page.get_by_test_id("login-submit")

    # ------------------------------------------------------------------
    # 入力・クリック操作
    # ------------------------------------------------------------------
    async def input_username(
        self,
        username: str,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        ユーザ ID を入力する。

        :param username: ユーザ ID
        :param evidence_dir: 操作失敗時の証跡保存ディレクトリ（任意）
        """
        locator = self._username_locator
        await self.safe_fill(
            locator,
            username,
            evidence_dir=evidence_dir,
            label="login_username_error",
        )

    async def input_password(
        self,
        password: str,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        パスワードを入力する。

        :param password: パスワード
        :param evidence_dir: 操作失敗時の証跡保存ディレクトリ（任意）
        """
        locator = self._password_locator
        await self.safe_fill(
            locator,
            password,
            evidence_dir=evidence_dir,
            label="login_password_error",
        )

    async def click_login(
        self,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        ログインボタンをクリックする。

        :param evidence_dir: 操作失敗時の証跡保存ディレクトリ（任意）
        """
        locator = self._submit_locator
        await self.safe_click(
            locator,
            evidence_dir=evidence_dir,
            label="login_submit_error",
        )

    # ------------------------------------------------------------------
    # ログイン成功判定
    # ------------------------------------------------------------------
    async def is_login_success(self) -> bool:
        """
        ログイン成功かどうかを判定する。

        ここでは暫定的に「チャット入力欄が表示されているか」で判定する。
        実際の UI に合わせて selector は適宜調整する。

        :return: 成功していれば True
        """
        try:
            # 例: data-testid="chat-input" を持つ入力欄が表示されれば成功
            await self.page.get_by_test_id("chat-input").wait_for(
                state="visible",
                timeout=self.timeout,
            )
            return True
        except Exception:
            return False

    async def wait_for_login_success(
        self,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        ログイン成功を待機し、失敗時には証跡を収集して LoginError を送出する。

        :param evidence_dir: 証跡保存ディレクトリ（任意）
        """
        if await self.is_login_success():
            return

        # 成功しなかった場合は証跡を収集
        if evidence_dir is not None:
            try:
                await self.collect_evidence(evidence_dir, label="login_failure")
            except Exception:
                # 証跡収集自体の失敗はここでは握りつぶし、
                # まずは LoginError を優先して伝える。
                pass

        raise LoginError("Login did not succeed.")

    # ------------------------------------------------------------------
    # 高レベル API
    # ------------------------------------------------------------------
    async def login(
        self,
        username: str,
        password: str,
        *,
        evidence_dir: Optional[PathLike] = None,
    ) -> None:
        """
        ログインフローを一括実行する高レベル API。

        呼び出し側は通常、このメソッドだけを使えばよい。

        :param username: ユーザ ID
        :param password: パスワード
        :param evidence_dir: 証跡保存ディレクトリ（任意）
        """
        await self.input_username(username, evidence_dir=evidence_dir)
        await self.input_password(password, evidence_dir=evidence_dir)
        await self.click_login(evidence_dir=evidence_dir)
        await self.wait_for_login_success(evidence_dir=evidence_dir)
