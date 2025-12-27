# Design_ChatPage_v0.2

**This document supersedes Design_ChatPage_v0.1.**
参照: BasePage v0.2, Locator_Guide_v0.2, Design_playwright_v0.1, PROJECT_GRAND_RULES v3.0
（v0.1）

---

## 1. 目的（Purpose）

ChatPage v0.2 は以下を目的とする：

1. **質問入力 → 送信 → 応答取得の高レベルUI操作を PageObject として抽象化すること**
2. **UI 操作失敗時に証跡（evidence）を自動収集する機能を追加すること**
3. **BasePage v0.2（safe_* / collect_evidence）と統合すること**
4. **INTERNET / LGWAN 環境差に依存しない高い耐障害性を提供すること**

---

## 2. 責務（Responsibilities）

### MUST

* 質問の入力
* 送信ボタン押下
* UI 応答待ち
* 最新メッセージの抽出
* ask() を通じた高レベル API を提供
* BasePage v0.2 の safe_* を利用して例外時の evidence を自動生成する

### SHOULD

* Locator_Guide_v0.2 に基づく multi-locator fallback
* LGWAN 遅延に耐える robust wait
* ask() の evidence_dir 連携

### MUST NOT

* RAG 判定ロジックを含める（Application Test Layer の責務）
* env.yaml を読む（pytest の責務）
* browser/context/page を生成する（pytest の責務）

---

## 3. ロケータ設計（Locator Strategy）

### 3.1 質問入力欄

```python
self.find(role="textbox", name="質問")
```

fallback:

```python
self.find(label="質問")
self.find(placeholder="質問を入力")
self.find(aria="chat-input")
self.page.locator("[data-testid='chat-input']")
```

### 3.2 送信ボタン

```
SEND_LABELS = ["送信", "送る", "投稿"]
```

```python
self.find(role="button", name=re.compile("|".join(SEND_LABELS)))
```

fallback:

```python
self.find(aria="send")
self.find(testid="send-button")
self.page.locator("[data-testid='chat-send']")
```

### 3.3 最新メッセージ

```python
self.page.locator("[data-testid='message']").last
```

fallback:

```python
self.page.get_by_role("article").last
```

---

## 4. メソッド設計

### 4.1 input_message(text, evidence_dir=None)

```python
async def input_message(self, text, *, evidence_dir=None):
    box = await self.find(role="textbox", name="質問")
    await self.safe_fill(box, text, evidence_dir=evidence_dir, label="chat_input_error")
```

---

### 4.2 click_send(evidence_dir=None)

```python
async def click_send(self, *, evidence_dir=None):
    btn = await self.find(role="button", name=re.compile("|".join(self.SEND_LABELS)))
    await self.safe_click(btn, evidence_dir=evidence_dir, label="chat_send_error")
```

---

### 4.3 wait_for_response(evidence_dir=None)

```python
async def wait_for_response(self, *, evidence_dir=None):
    try:
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(500)  # 安定化
    except Exception:
        if evidence_dir:
            await self.collect_evidence(evidence_dir, "chat_wait_error")
        raise
```

---

### 4.4 get_latest_response(evidence_dir=None)

```python
async def get_latest_response(self, *, evidence_dir=None) -> str:
    try:
        msg = self.page.locator("[data-testid='message']").last
        await msg.wait_for(state="visible", timeout=self.timeout)
        return await msg.inner_text()
    except Exception:
        if evidence_dir:
            await self.collect_evidence(evidence_dir, "chat_extract_error")
        raise
```

---

### 4.5 ask(text, evidence_dir=None)（高レベルAPI）

```python
async def ask(self, text: str, *, evidence_dir=None) -> str:
    try:
        await self.input_message(text, evidence_dir=evidence_dir)
        await self.click_send(evidence_dir=evidence_dir)
        await self.wait_for_response(evidence_dir=evidence_dir)
        return await self.get_latest_response(evidence_dir=evidence_dir)
    except Exception:
        if evidence_dir:
            await self.collect_evidence(evidence_dir, "ask_error")
        raise
```

---

## 5. pytest + log_writer との連携

pytest が：

* `case_log_dir`, `case_assets_dir` を生成し
* ChatPage.ask(..., evidence_dir=case_assets_dir) を呼び
* 必要なら log_writer の artifacts として evidence パスを記録する

ChatPage 自身はパス構造を知らず、**渡された evidence_dir に書くだけ**の設計を厳守する。

---

## 6. 例外処理

* UI失敗 → safe_* → evidence保存 → Exception 再送出
* ask 全体の失敗 → ask_error.png + ask_error.html
* pytest が FAIL として扱い、log_writer がログに残す

---

## 7. 将来拡張（v0.3）

* streaming UI（部分応答）対応
* Markdown / HTML の応答パーサ
* DOM diff の自動抽出
* multi-turn ask シーケンスの標準化

---

