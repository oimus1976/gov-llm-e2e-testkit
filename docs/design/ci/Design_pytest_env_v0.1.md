# Design_pytest_env_v0.1  

gov-llm-e2e-testkit — pytest Execution Layer 設計書  
バージョン: v0.1  
最終更新: 2025-12-07

参照文書:
- Responsibility_Map_v0.1
- Design_env_v0.1
- Design_playwright_v0.1
- Design_BasePage_v0.1
- Design_LoginPage_v0.1
- Design_ChatPage_v0.1
- test_plan_v0.1
- CI: .github/workflows/e2e.yml

---

## 1. 目的（Purpose）

本設計書は gov-llm-e2e-testkit における  
**pytest 実行レイヤ（Execution Layer）の正式仕様**を定義する。

Execution Layer は以下を担う：

- Playwright の browser/context/page を生成  
- env.yaml（INTERNET / LGWAN）の設定適用  
- timeout / headless / URL / 認証情報の注入  
- PageObject の初期化  
- LLM テスト（Smoke / RAG_Basic / RAG_Advanced）に必要な基盤の提供  

pytest は Application Test Layer に値を提供する **インフラ層**であり、  
PageObject の内部実装や HTML/RAG の検証ロジックには関与しない。

---

## 2. pytest Execution Layer の責務（Responsibility）

以下は Responsibility Map v0.1 に基づく公式定義である。

### 2.1 pytest 層の責務
- browser/context/page の唯一の生成ポイント  
- env_loader に基づく環境構成（INTERNET / LGWAN）適用  
- timeout 設定の注入（page.set_default_timeout）  
- PageObject（LoginPage / ChatPage など）へ page を提供  
- RAG YAML ケースをテスト関数へ受け渡す  
- CI（e2e.yml）からの実行入口  

### 2.2 pytest 層の非責務
- UI ロジック（PageObject に委譲）  
- env.yaml の定義そのもの（Environment Layer の責務）  
- ログイン操作（LoginPage の責務）  
- LLM 応答の妥当性判断（Application Test Layer）  
- ブラウザ操作の具体手順（Playwright / PageObject の責務）  

---

## 3. pytest フォルダ構造（v0.1）

```text
tests/
conftest.py              ← pytest Execution Layer の中心
test_smoke_llm.py        ← Smoke Test
rag/
test_rag_basic_v0.1.py
test_rag_advanced_v0.1.py
data/
rag/
*.yaml                 ← RAG テストケース
src/
env_loader.py            ← env.yaml 読み込みロジック
```

conftest.py はブラウザ起動・環境初期化のすべてを管理する。

---

## 4. conftest.py（正式仕様）

本章では **Execution Layer の基盤コード**を示す。  
実装はすべてこの仕様に従う。

---

### 4.1 env_config Fixture（必須）

環境設定（env.yaml → env_loader）の読み込みを行う。

```python
@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config
```

**理由：**

- INTERNET / LGWAN の差異を pytest 側で統一的に扱う
- pytest session 単位で固定されるため高速

---

## 4.2 browser Fixture（Playwright browser 生成）

```python
@pytest.fixture(scope="session")
async def browser(env_config):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=env_config["browser"]["headless"]
        )
        yield browser
        await browser.close()
```

**責務：**

- Playwright browser の唯一の生成と破棄
- env.yaml（headless）の適用

---

### 4.3 page Fixture（context/page の生成と timeout 適用）

```python
@pytest.fixture
async def page(browser, env_config):
    context = await browser.new_context()
    page = await context.new_page()

    # INTERNET/LGWAN の timeout を適用
    page.set_default_timeout(env_config["browser"]["page_timeout_ms"])

    yield page
    await context.close()
```

**責務：**

- context/page の生成
- LGWAN / INTERNET の timeout を適用
- PageObject へ渡すための唯一の page インスタンス作成

---

## 5. PageObject との接合仕様（LoginPage / ChatPage）

pytest は PageObject に page を注入し、
PO 側は UI 操作だけに専念する。

```python
@pytest.fixture
async def login_page(page):
    return LoginPage(page)

@pytest.fixture
async def chat_page(page):
    return ChatPage(page)
```

---

## 6. RAG YAML の読み込み仕様

RAG テストケースは data/rag/*.yaml に格納される。

```python
@pytest.fixture(params=load_yaml_cases())
def case(request):
    return request.param
```

この仕様により：

- test_rag_basic_v0.1.py は case を自動展開
- test_plan_v0.1 に書かれた「順序と構造」を満たす
- CI 側で exit code 5（テストゼロ）を回避できる

---

## 7. CI（e2e.yml）との責務境界

pytest は CI への **実行インターフェース**を提供する。

CI の責務：

- poetry install
- pytest 実行
- env.yaml の存在チェック
- INTERNET profile 固定（ENV_PROFILE=internet）

pytest の責務：

- browser 起動
- timeout 適用
- PageObject 初期化
- LLM 応答取得
- RAG 検証ロジックの呼出

CI は pytest の内部仕様を持たず、pytest は CI の制御を前提としない。

---

## 8. pytest 例（最小）

```python
async def test_smoke_llm(chat_page):
    response = await chat_page.ask("こんにちは")
    assert isinstance(response, str)
```

---

## 9. 想定される将来拡張（v0.2 / v1.0）

| 版    | 機能                                       |
| ---- | ---------------------------------------- |
| v0.2 | retry_policy の導入（LGWAN 遅延対策）             |
| v1.0 | multi-tenant、LLM 別の並列設定、ChatObserver の追加 |
| v1.0 | 基地局レベルの timeout 自動学習（LGWAN 最適化）          |

---

## 10. まとめ

本書により pytest Execution Layer の責務は次のように確定した：

- env.yaml を読み込むのは pytest → env_loader
- browser/context/page の生成は pytest
- timeout 適用は pytest
- PageObject は純粋な UI 抽象化
- Application Test Layer は検証ロジックのみ
- CI は pytest を呼び出すだけ

以上を Design_pytest_env_v0.1 として正式採用する。

---
