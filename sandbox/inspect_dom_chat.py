from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://qommons.ai/login")

        # ここで手動ログイン or 仮の自動ログイン
        # username/password locator は今の LoginPage のつもりで一旦直書き

        # ログイン後、チャット画面の HTML を保存
        page.wait_for_timeout(2000)
        html = page.content()
        with open("tmp_chat_dom.html", "w", encoding="utf-8") as f:
            f.write(html)

        # 任意でスクショも
        page.screenshot(path="tmp_chat.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    main()
