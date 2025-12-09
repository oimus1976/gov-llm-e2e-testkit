from playwright.sync_api import sync_playwright

EMAIL = "test_e2e@和歌山県_かつらぎ町"
PASSWORD = "1234Test!"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(storage_state=None)
        page = context.new_page()

        # ---------------------------------------------------------
        # 1. ログインページへ
        # ---------------------------------------------------------
        page.goto("https://qommons.ai/login")

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        page.wait_for_selector("input[name='username']", timeout=20000)

        # ---------------------------------------------------------
        # 2. ログイン
        # ---------------------------------------------------------
        page.fill("input[name='username']", EMAIL)
        page.fill("input[name='password']", PASSWORD)
        page.click("#login-button")

        # ---------------------------------------------------------
        # 3. メニュー画面 DOM 保存
        # ---------------------------------------------------------
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        menu_dom = page.content()
        with open("tmp_menu_dom.html", "w", encoding="utf-8") as f:
            f.write(menu_dom)

        page.screenshot(path="tmp_menu.png", full_page=True)
        print("✔ メニュー画面 DOM を保存しました（tmp_menu_dom.html）")

        # ---------------------------------------------------------
        # 4. 右ブロックの「プライベートナレッジ」カードをクリック
        # ---------------------------------------------------------

        # 右ブロックのカードは h3 にタイトルが入っているので、それを直接クリックする
        card = page.locator("div[data-slot='card']:has(h3:text('プライベートナレッジ'))")
        card.click(force=True)
        print(card.count())  # 1 か？
        card.hover()  # hover が効くか？


        # ---------------------------------------------------------
        # 5. チャット画面読み込み待ち
        # ---------------------------------------------------------
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # ---------------------------------------------------------
        # 6. チャット DOM 保存（本命）
        # ---------------------------------------------------------
        chat_dom = page.content()
        with open("tmp_chat_dom.html", "w", encoding="utf-8") as f:
            f.write(chat_dom)

        page.screenshot(path="tmp_chat_dom.png", full_page=True)
        print("✔ チャット画面 DOM を保存しました（tmp_chat_dom.html）")

        browser.close()


if __name__ == "__main__":
    main()
