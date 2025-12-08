from tests.pages.login_page import LoginPage

def test_smoke_llm(page, env_config):
    config, _ = env_config

    print("\n=== SMOKE TEST START ===")

    # ログイン画面へ
    page.goto(config["url"])
    print("INITIAL URL:", page.url)

    login = LoginPage(page)
    login.login(config["username"], config["password"])

    # デバッグ：ログイン後の状態を確認
    print("FINAL URL:", page.url)
    print("TITLE:", page.title())

    # HTML の先頭1000文字を保存してデバッグ
    html = page.content()
    with open("after_login.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Smoke としては「ログイン後画面に行っていること」を確認
    assert page.url.startswith("https://qommons.ai/"), "URLが遷移していません"
