# Design_ChatPage_v0.1  

gov-llm-e2e-testkit — ChatPage（チャット画面）Page Object 設計書

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

ChatPage は **チャット画面の操作に特化した Page Object** であり、

- 質問入力  
- 送信  
- LLM からのレスポンス取得  
- ローディング（処理中）検知  
- Chat UI の変動吸収  

を担当する。

BasePage を継承し、UI 操作の共通処理は BasePage 側へ委譲する。

---

## 2. 前提条件（Prerequisites）

- Playwright（Python / async）を前提  
- BasePage の locator factory / safe actions を利用  
- locator の優先順位は Locator_Guide_v0.2 に従う  
- LGWAN / INTERNET は config/env.yaml により timeout 切替  
- ChatPage はテストケースから直接操作される高レベル API を提供  
- テストコードに locator を直書きしてはならない（GRAND_RULES）

---

## 3. ChatPage の責務（Responsibilities）

### 3.1 MUST（必須）

- 質問入力欄のロケータ定義  
- 送信ボタンのロケータ定義  
- 最新メッセージの取得ロジック  
- 質問入力（input_message）  
- 送信（click_send）  
- 応答待機（wait_for_response）  
- 高レベルAPI（ask）

### 3.2 SHOULD（推奨）

- ロケータ fallback（部分一致・aria-label）  
- LLM 応答の検証支援（テキスト抽出）  
- 例外検知（UI破壊時）

### 3.3 MUST NOT（禁止）

- BasePage の責務を侵食する  
- 外部通信を行う（LGWAN 違反）  
- テストケースで locator を再定義する

---

## 4. ロケータ設計（Locator Design）

Locator_Guide_v0.2 に基づき、以下の優先順位で定義する。

### 4.1 質問入力欄（textbox）

優先ロケータ：

```python
self.find(role="textbox", name="質問")
```

fallback：

```python
self.find(label="質問")
self.find(placeholder="質問を入力")
self.find(aria="chat-input")
```

## 4.2 送信ボタン（button）

UI文言「送信 / 送る / 投稿」に備え multi-locator を用意。

```python
SEND_LABELS = ["送信", "送る", "投稿"]
```

優先：

```python
self.find(role="button", name=re.compile("|".join(SEND_LABELS)))
```

fallback：

```python
self.find(aria="send")
self.find(testid="send-button")
```

## 4.3 LLM応答メッセージ

優先：

```python
self.page.locator("[data-testid='message']").last
```

fallback：

```python
self.page.get_by_role("article").last
```

（UI の変動に強い selector を採用）

---

## 5. メソッド設計（Method Design）

### 5.1 input_message(text)

```python
async def input_message(self, text):
    box = await self.find(role="textbox", name="質問")
    await self.safe_fill(box, text)
```

### 5.2 click_send()

```python
async def click_send(self):
    btn = await self.find(role="button", name=re.compile("|".join(SEND_LABELS)))
    await self.safe_click(btn)
```

### 5.3 wait_for_response()

チャット処理中 UI（loading）を待ち、LLM 応答が出るまで待機。

```python
async def wait_for_response(self):
    await self.wait_for_loading()
    await self.page.wait_for_timeout(500)  # 安定化のための短期待機
```

### 5.4 get_latest_response()

```python
async def get_latest_response(self):
    msg = self.page.locator("[data-testid='message']").last
    await msg.wait_for(state="visible", timeout=self.timeout)
    return await msg.inner_text()
```

### 5.5 ask(text)（高レベルAPI）

```python
async def ask(self, text):
    await self.input_message(text)
    await self.click_send()
    await self.wait_for_response()
    return await self.get_latest_response()
```

---

## 6. ローディング検知（Loading Detection）

Design_BasePage_v0.1 の wait_for_loading() を利用する。

デフォルト selector：

```python
[data-loading='true']
```

必要に応じて ChatPage 側で override 可能。

---

## 7. エラー／例外処理（Exception Handling）

- ロケータ取得失敗 → 明示的例外
- LLM応答が取得できない → timeout
- UI変更の疑い → Page Object 更新提案を出す（PENTA推奨）

---

## 8. 拡張予定（v0.2）

- Markdown / HTML の応答内容向けパーサ
- 引用・コードブロック抽出
- RAGテスト仕様との直接統合（expected_keywords チェック）
- multi-locator の強化（role + aria + fallback merge）

---

## 9. まとめ

ChatPage は、
**“質問 → 送信 → 応答取得” の流れを抽象化する中心的 Page Object** であり、
Smoke Test、RAG Test の両方において最も重要なクラス。

BasePage と Locator_Guide の仕様を正しく実装することで、
UI変動・LLM更新時にもテスト基盤が壊れない構造を実現する。

---
