# sandbox/debug_chat_flow_v0_1.py
# ---------------------------------------------------------
# Qommons Chat flow debugger (menu → chat UUID)
# - ログイン → /chat 到達確認
# - /chat で #message が存在するか検証
# - ChatSelectPage で /chat/<uuid> に遷移
# - /chat/<uuid> で #message が存在するか検証
#
# 出力:
#   sandbox/debug_chat_<timestamp>/after_login.{html,png}
#   sandbox/debug_chat_<timestamp>/after_select.{html,png}
#   標準出力に URL と #message 存在可否ログ
# ---------------------------------------------------------

from pathlib import Path
from datetime import datetime, timezone, timedelta

from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage


JST = timezone(timedelta(hours=9))


def create_debug_dir() -> Path:
    """sandbox 配下にタイムスタンプ付きディレクトリを作成"""
    ts = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
    base = Path("sandbox") / f"debug_chat_{ts}"
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_snapshot(page, base_dir: Path, label: str) -> None:
    """HTML とスクリーンショットを保存"""
    html_path = base_dir / f"{label}.html"
    png_path = base_dir / f"{label}.png"

    html_path.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(png_path), full_page=True)

    print(f"[snapshot] {label}:")
    print(f"  HTML: {html_path}")
    print(f"  PNG : {png_path}")


def locator_exists(page, selector: str) -> bool:
    """シンプルに selector の存在を確認"""
    try:
        count = page.locator(selector).count()
        return count > 0
    except Exception as e:
        print(f"[locator_exists] error for selector '{selector}': {e}")
        return False


def main():
    # 1. env_config のロード（Design_env_v0.2.3 準拠）
    config, options = load_env()

    debug_dir = create_debug_dir()
    print(f"[debug] output dir = {debug_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # -------------------------------------------------
        # 2. LoginPage でログイン → /chat へ
        # -------------------------------------------------
        login_page = LoginPage(page, config)
        login_page.open()
        login_page.login()

        url_after_login = page.url
        print(f"[step] after login: url = {url_after_login}")
        save_snapshot(page, debug_dir, "after_login")

        has_message_on_menu = locator_exists(page, "#message")
        print(f"[check] /chat 画面で #message が存在するか: {has_message_on_menu}")

        # -------------------------------------------------
        # 3. ChatSelectPage で個別チャットを開く
        #    - name は環境に合わせて変更
        #    - 仮に「プライベートナレッジ」をデフォルト候補にする
        # -------------------------------------------------
        select_page = ChatSelectPage(page, config)

        # config 側に将来 "default_chat_name" を持たせる余地を残す
        chat_name = config.get("chat_name", "プライベートナレッジ")
        print(f"[step] open_ai: name = {chat_name!r}")

        select_page.open_ai(chat_name)

        url_after_select = page.url
        print(f"[step] after select: url = {url_after_select}")
        save_snapshot(page, debug_dir, "after_select")

        has_message_on_room = locator_exists(page, "#message")
        print(f"[check] /chat/<uuid> 画面で #message が存在するか: {has_message_on_room}")

        # -------------------------------------------------
        # 4. ChatPage をここで初期化（将来の確認用）
        # -------------------------------------------------
        chat_page = ChatPage(page, config)
        print("[info] ChatPage initialized (no ask() executed)")

        browser.close()


if __name__ == "__main__":
    main()
