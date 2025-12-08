# Design_LoginPage_v0.2

**This document supersedes Design_LoginPage_v0.1.**
（参照：BasePage v0.2, Locator_Guide_v0.2, Design_playwright_v0.1）


---

## 1. 目的（Purpose）

LoginPage v0.2 は gov-llm-e2e-testkit における
**ログイン操作の標準化と、UI 失敗時の証跡収集（evidence）対応を備えた Page Object**である。

本バージョンでは以下を提供する：

* BasePage v0.2 の safe_* API を完全利用
* UI 変動への強い耐性（Locator_Guide_v0.2 に準拠）
* INTERNET / LGWAN 両対応（timeout は pytest Execution Layer に委譲）
* 失敗時の screenshot + DOM dump を含む証跡収集フロー
* 将来の MFA / リダイレクト対応を見据えた拡張性の確保

---

## 2. 責務（Responsibilities）

### 2.1 MUST（必須）

* username/password の入力
* login ボタン押下
* ログイン成功判定
* BasePage v0.2 の safe_* / find を利用
* 証跡収集（異常系で自動生成）

### 2.2 SHOULD（推奨）

* 複数 UI バージョンに対する fallback
* LGWAN 環境の遅延を考慮した堅牢な find
* 認証後の画面変化を複数パターンで検出可能にする

### 2.3 MUST NOT（禁止）

* env.yaml の読み込み（pytest の責務）
* timeout の内部保持（pytest → page.default_timeout に依存）
* テストロジックの記述（判定は Application Test Layer）

---

## 3. ロケータ設計（Locator Strategy）

### 3.1 username field

```python
self.find(role="textbox", name="ユーザーID")
```

fallback:

```python
self.find(label="ユーザーID")
self.find(placeholder="ユーザーIDを入力")
self.find(aria="username")
```

### 3.2 password field

同様のルール：

```python
self.find(role="textbox", name="パスワード")
```

fallback:

```python
self.find(label="パスワード")
self.find(placeholder="パスワードを入力")
self.find(aria="password")
```

### 3.3 login button

```python
self.find(role="button", name="ログイン")
```

fallback:

```python
self.find(role="button", name=re.compile("ログイン|LOGIN|Sign In"))
self.find(aria="login")
self.find(testid="login-button")
```

---

## 4. メソッド設計（Method Design）

### 4.1 input_username(username)

safe_fill を採用し、証跡取得付きとなる：

```python
async def input_username(self, username: str):
    field = await self.find(role="textbox", name="ユーザーID")
    await self.safe_fill(field, username, action_name="input_username")
```

### 4.2 input_password(password)

```python
async def input_password(self, password: str):
    field = await self.find(role="textbox", name="パスワード")
    await self.safe_fill(field, password, action_name="input_password")
```

### 4.3 click_login()

```python
async def click_login(self):
    btn = await self.find(role="button", name="ログイン")
    await self.safe_click(btn, action_name="click_login")
```

### 4.4 is_login_success()

v0.2 で追加された判定メソッド：

```python
async def is_login_success(self) -> bool:
    try:
        await self.page.get_by_role("textbox", name="質問").wait_for(state="visible")
        return True
    except Exception:
        return False
```

### 4.5 wait_for_login_success()

成功判定のラッパー：

```python
async def wait_for_login_success(self):
    if not await self.is_login_success():
        await self.collect_evidence("login_failure")
        raise LoginError("Login did not succeed.")
```

### 4.6 login(username, password)

高レベル API：

```python
async def login(self, username: str, password: str):
    await self.input_username(username)
    await self.input_password(password)
    await self.click_login()
    await self.wait_for_login_success()
```

---

## 5. 証跡収集（Evidence Collection）

BasePage v0.2 の `collect_evidence(event_name)` を利用し、
ログイン失敗時に以下を自動保存：

* screenshot（PNG）
* DOM snapshot（HTML）
* timestamp
* event_name="login_failure"

保存先は pytest 側で生成する log_base_dir 配下となる。

---

## 6. 例外処理（Exception Handling）

### 6.1 LoginError（v0.2 新設）

ログイン成功判定の失敗時に raise する。

### 6.2 locator 取得失敗

BasePage の safe_* が自動で証跡を残しつつ例外化する。

---

## 7. 将来拡張（v0.3 / v1.0）

* MFA / SSO 対応
* ログイン成功判定の強化（URL 変化・Cookie 判定）
* retry_policy（LGWAN 環境用）との統合

---
