# -------------------------------------------------------------
# template_prepare_chat_v0_1.py
#
# 【目的】
#  login → チャット選択 → メッセージ1回送信
# を “絶対に壊れない安定区間（Stable Core）” としてテンプレ化。
#
# 【責務】
#  - UI 操作をすべて PageObject に委譲
#  - セレクタ/Playwright 生操作を一切持たない
#  - テスト側がネットワーク監視に集中できる
#
# 【戻り値】
#   page, context, chat_id
#
# -------------------------------------------------------------

from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage


def prepare_chat_session(question: str = "テストメッセージ"):
    """
    ログイン → AI 選択 → メッセージ送信 までを実施する安定テンプレート。

    Parameters
    ----------
    question : str
        最初に送信するテキスト

    Returns
    -------
    (page, context, chat_id)
    """
    # ---------------------------
    # Setup 出力ディレクトリ
    # ---------------------------
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path(f"sandbox/run_{ts}")
    outdir.mkdir(parents=True, exist_ok=True)

    # ---------------------------
    # Playwright 起動
    # ---------------------------
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # ---------------------------
    # env 読み込み
    # ---------------------------
    config, _ = load_env()

    # ---------------------------
    # Login（PageObject のみ使用）
    # ---------------------------
    login = LoginPage(page, config)
    try:
        login.open()
        login.login(evidence_dir=outdir)
        print("[template] login OK")
    except Exception as e:
        raise RuntimeError(f"[template] LOGIN FAILED: {e}")

    # ---------------------------
    # Chat 選択
    # ---------------------------
    selector = ChatSelectPage(page, config)
    try:
        selector.open_ai("プライベートナレッジ", evidence_dir=outdir)
        print("[template] chat selection OK")
    except Exception as e:
        raise RuntimeError(f"[template] CHAT SELECT FAILED: {e}")

    # ---------------------------
    # メッセージ送信（1回）
    # ---------------------------
    chat = ChatPage(page, config)
    try:
        chat.input_message(question, evidence_dir=outdir)
        chat.click_send(evidence_dir=outdir)
        print(f"[template] message sent: {question}")
    except Exception as e:
        raise RuntimeError(f"[template] MESSAGE SEND FAILED: {e}")

    # ---------------------------
    # chat_id を抽出
    # ---------------------------
    try:
        chat_id = page.url.split("/")[-1]
        print(f"[template] chat_id = {chat_id}")
    except Exception:
        raise RuntimeError("[template] FAILED TO EXTRACT chat_id")

    return page, context, chat_id
