# Design_LoginPage_v0.1  

gov-llm-e2e-testkit — LoginPage Page Object 設計書

最終更新：2025-12-07  
参照文書：  

- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_BasePage_v0.1  
- Locator_Guide_v0.2  
- Design_playwright_v0.1  

---

## 1. 目的（Purpose）

LoginPage は gov-llm-e2e-testkit における  
**ログイン処理専用の Page Object** であり、

- username の入力  
- password の入力  
- login ボタン押下  
- ログイン成功の検証  
- UI変動の吸収  
- LGWAN対応の timeout  

を行う。

---

## 2. 前提条件（Prerequisites）

- BasePage の locator factory / safe actions を継承  
- Locator_Guide_v0.2 のロケータ優先順位を使用  
- username/password はテストデータではなく **env.yaml から取得**  
- ログイン後は ChatPage または Dashboard 要素で遷移を確認  
- テストコードにロケータ直書きは禁止（GRAND_RULES）

---

## 3. LoginPage の責務（Responsibilities）

### 3.1 MUST（必須）

- username フィールド locator の定義  
- password フィールド locator の定義  
- login ボタン locator の定義  
- 入力操作（input_username / input_password）  
- login 実行（click_login）  
- ログイン成功判定  
- 高レベルAPI（login）  

### 3.2 SHOULD（推奨）

- role-based locator の fallback（placeholder, aria-label）  
- 複数 UI バージョンへの耐性  
- username/password のセキュアロード（外部通信なし）

### 3.3 MUST NOT（禁止）

- 外部通信が必要なコード（LGWAN違反）  
- テストケースにロケータを再定義する  
- ページ固有でない共通操作を LoginPage に記述する（責務逸脱）

---

## 4. ロケータ設計（Locator Design）

### 4.1 username（input field）

優先順位：

```python
self.find(role="textbox", name="ユーザーID")
```

fallback：

```python
self.find(label="ユーザーID")
self.find(placeholder="ユーザーIDを入力")
self.find(aria="username")
```

### 4.2 password（input field）

```python
self.find(role="textbox", name="パスワード")
```

fallback：

```python
self.find(label="パスワード")
self.find(placeholder="パスワードを入力")
self.find(aria="password")
```

### 4.3 login ボタン（button）

優先：

```python
self.find(role="button", name="ログイン")
```

fallback：

```python
self.find(role="button", name=re.compile("ログイン|LOGIN|Sign In"))
self.find(aria="login")
self.find(testid="login-button")
```

---

## 5. メソッド設計（Method Design）

### 5.1 input_username(username)

```python
async def input_username(self, username):
    field = await self.find(role="textbox", name="ユーザーID")
    await self.safe_fill(field, username)
```

### 5.2 input_password(password)

```python
async def input_password(self, password):
    field = await self.find(role="textbox", name="パスワード")
    await self.safe_fill(field, password)
```

### 5.3 click_login()

```python
async def click_login(self):
    btn = await self.find(role="button", name="ログイン")
    await self.safe_click(btn)
```

### 5.4 wait_for_login_success()

ログイン成功後の画面要素が表示されるまで待つ。

例：ChatPage の入力欄（textbox: 質問）

```python
async def wait_for_login_success(self):
    await self.page.get_by_role("textbox", name="質問").wait_for(
        state="visible", timeout=self.timeout
    )
```

### 5.5 login(username, password)（高レベルAPI）

```python
async def login(self, username, password):
    await self.input_username(username)
    await self.input_password(password)
    await self.click_login()
    await self.wait_for_login_success()
```

---

## 6. LGWAN対応（LGWAN Mode）

- timeout は INTERNET の 2〜3 倍
- 外部通信要素（API, fetch）は禁止
- env.yaml で secure-config を参照する：

```yaml
credentials:
  username: "${USERNAME}"
  password: "${PASSWORD}"
timeout:
  internet: 10000
  lgwan: 30000
```

---

## 7. エラー・例外処理（Error Handling）

- ロケータ取得失敗 → 明示的な例外を発生
- ログイン失敗（timeout）→ LoginError として raise
- UI変動で login ボタンが消えた場合 → Locator_Guide 更新を提案（PENTA推薦）

---

## 8. 今後の拡張（v0.2）

- MFA（多要素認証）のUI対応（オプション）
- ログイン失敗の理由表示（UI解析）
- 権限別ログイン（admin / user）対応
- ChatPage 遷移確認の強化（divergence-check）

---

## 9. まとめ

LoginPage は
**E2Eテスト開始時に必ず通過する“最初の砦”であり、
UI変動や LGWAN環境下でも破綻しないログイン処理を抽象化するクラス** である。

本設計書 v0.1 は
ChatPage / BasePage の仕様と完全整合し、
今後のテストコード安定化の基礎となる。

---
