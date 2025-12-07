# Design_BasePage_v0.1  

gov-llm-e2e-testkit — Page Object 基底クラス設計書

最終更新：2025-12-07  
参照文書：  

- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_playwright_v0.1  
- Locator_Guide_v0.2  

---

## 1. 目的（Purpose）

BasePage は gov-llm-e2e-testkit における  
**すべての Page Object の基底クラス**であり、

- UI操作の安全性  
- ロケータ規範（Locator_Guide）の自動適用  
- LGWAN/INTERNET の timeout 切替  
- ロケータ破壊検知の容易化  
- Page Object 全体の保守コスト最小化  

を目的とする。

---

## 2. 前提（Prerequisites）

- Playwright（Python / async）を使用する  
- locator の優先順位は Locator_Guide_v0.2 に従う  
- timeout 等は `config/env.yaml` に設定  
- BasePage → 各Page（ChatPage, LoginPage）→ テスト の三層構造  
- テストコードに locator を直書きすることは禁止（GRAND_RULES）

---

## 3. BasePage の責務（Responsibilities）

### 3.1 MUST（必須）

- Playwright page オブジェクトを保持
- ロケータ生成メソッド（locator factory）
- timeout 設定のロード（INTERNET / LGWAN）
- 安全な UI 操作メソッド（safe_click, safe_fill）
- ページ準備完了判定（wait_for_page_ready）
- ローディング表示のブロック検知（wait_for_loading）
- スクリーンショット生成
- 共通ログ出力

### 3.2 SHOULD（推奨）

- UI変動時の fallback（部分一致・aria-label）
- ロケータ破壊検知（要素未取得時の例外化）
- retry（再実行）ラッパー

### 3.3 MUST NOT（禁止）

- テストケース内で locator を直接定義すること  
- 外部通信が必要なコード（LGWAN 違反）  
- ページ固有の操作を BasePage に書くこと（境界侵犯）

---

## 4. クラス構造（Class Structure）

```python
class BasePage:
    def __init__(self, page, config):
        self.page = page
        self.config = config
        self.timeout = config.timeout  # INTERNET/LGWAN切替済
```

---

## 5. ロケータ生成メソッド（Locator Factory）

BasePage は locators の最優先度規範を実装する。

```python
async def find(self, role=None, name=None, label=None, placeholder=None,
               aria=None, testid=None, css=None):
    # 1. role + name
    if role and name:
        return self.page.get_by_role(role, name=name)

    # 2. label
    if label:
        return self.page.get_by_label(label)

    # 3. placeholder
    if placeholder:
        return self.page.get_by_placeholder(placeholder)

    # 4. aria-label
    if aria:
        return self.page.locator(f"[aria-label='{aria}']")

    # 5. data-testid
    if testid:
        return self.page.locator(f"[data-testid='{testid}']")

    # 6. CSS
    if css:
        return self.page.locator(css)

    raise ValueError("No valid locator arguments provided")
```

Locator_Guide の優先順位を忠実に反映した構成。

---

## 6. ページ準備完了（Page Ready）

```python
async def wait_for_page_ready(self):
    await self.page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
```

---

## 7. ローディング監視（Loading Detection）

LLM UI（Qommonsなど）では “処理中” の UI が出る可能性がある。

```python
async def wait_for_loading(self, selector="[data-loading='true']"):
    await self.page.locator(selector).wait_for(state="hidden", timeout=self.timeout)
```

---

## 8. 安全操作（Safe Actions）

```python
async def safe_click(self, locator):
    await locator.wait_for(state="visible", timeout=self.timeout)
    await locator.click()

async def safe_fill(self, locator, text):
    await locator.wait_for(state="visible", timeout=self.timeout)
    await locator.fill(text)
```

---

## 9. retry ラッパー（Optional）

```python
async def retry(self, func, retries=2):
    for _ in range(retries):
        try:
            return await func()
        except Exception:
            await self.page.wait_for_timeout(500)
    raise
```

---

## 10. スクリーンショット・ログ

```python
async def screenshot(self, name):
    await self.page.screenshot(path=f"logs/{name}.png")
```

---

## 11. Page Object 境界（Boundary Rules）

BasePage は抽象操作のみを提供し、

- ChatPage
- LoginPage

などページ固有操作は派生クラスに記述する。

---

## 12. 今後の拡張（v0.2 予定）

- aria-label / 部分一致の高度 fallback
- multi-locator（複合ロケータ）対応
- ChatPage 標準アクション
- LoginPage 標準アクション
- LGWAN timeout 自動調整の強化
- ロケータ破壊レポート（原因表示）

---

## 13. まとめ

BasePage は
**「UI 破壊に強く、LGWAN と INTERNET を両対応し、
Page Object 全体を支える最重要アーキテクチャ要素」**
として設計される。

本 v0.1 はその基礎であり、
次は ChatPage / LoginPage をこの構造の上に構築する。

---
