"""
Manual runner for F8 Set-1 (v0.1r+).

Purpose:
- Execute F8-Set-1 manually with a real browser
- Verify end-to-end execution and artifact generation
- Record operational evidence without pytest

Non-Goals:
- Evaluation or comparison of answers
- Automatic retries or heuristics
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

from src.execution.run_f8_set1 import run_f8_set1


def main():
    # --------------------------------------------------
    # Load environment (same as conftest.py)
    # --------------------------------------------------
    config, _ = load_env()

    # --------------------------------------------------
    # Fixed manual execution parameters (explicit, no inference)
    # --------------------------------------------------
    run_id = "manual-check-001"
    output_root = Path("./out/f8")

    qommons_config = {
        "model": "gpt-5.2",
        "web_search": False,
        "region": "jp",
        "ui_mode": "web",
    }

    execution = {
        "mode": "manual",
        "retry": 0,
        "temperature": 0.0,
        "max_tokens": 2048,
    }

    # --------------------------------------------------
    # Playwright bootstrap
    # --------------------------------------------------
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---- Login ----
        login = LoginPage(page, config)
        login.open()
        login.login()

        # ---- Chat selection ----
        select_page = ChatSelectPage(page, config)
        ai_name = config.get("chat_name", "プライベートナレッジ")
        select_page.open_ai(ai_name)

        # ---- ChatPage ----
        chat_page = ChatPage(page, config)

        # --------------------------------------------------
        # Run F8 Set-1
        # --------------------------------------------------
        outcomes = run_f8_set1(
            chat_page=chat_page,
            ordinance_id="manual-test",
            profile="web-default",
            run_id=run_id,
            qommons_config=qommons_config,
            knowledge_scope="golden",
            knowledge_files=[],
            ordinance_set="Golden_Ordinance_Set_v1",
            output_root=output_root,
            execution=execution,
        )

        # --------------------------------------------------
        # Minimal result summary (fact only)
        # --------------------------------------------------
        print("Executed questions:", len(outcomes))
        for o in outcomes:
            print(
                o.question_id,
                "OK" if o.error is None else "ERR",
                o.error,
            )

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
