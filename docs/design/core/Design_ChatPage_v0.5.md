# Design_ChatPage_v0.5  

gov-llm-e2e-testkit – ChatPage DOM 対応設計書（2025-12）


## 1. 目的（Purpose）

本ドキュメントは、Qommons.AI（2025年12月時点）の最新 DOM 構造に
完全準拠した **ChatPage PageObject v0.5** の仕様を定義する。

特に以下の課題に対応するために設計を刷新した：

- data-testid が非採用となり、既存ロケータが全滅した
- 入力欄・送信ボタン・メッセージ要素の DOM が刷新された
- visible 判定が不安定で、SPA 遷移やアニメーションが多い
- 最新メッセージの取得方法が変更され、既存ロケータでは抽出不可

本設計書は、Smoke Test v0.3 を安定動作させるための正式仕様である。

**Note (Important):**

 The `ask()` API defined in this document is a **DOM-based legacy interface**
 that includes UI-level answer observation and extraction.

 Formal submission semantics and responsibility boundaries are defined separately in  
 **Design_ChatPage_submit_v0.6.md**.

 This document remains valid for DOM observation, debugging, and experimental usage,
 but it does **not** define the canonical submission API.

---

## 2. 対象 DOM の概要（Analyzed DOM Summary）

### ● 入力欄（textarea）
```html
<textarea id="message" ...></textarea>
````

* 唯一の入力欄
* data-testid が存在しない
* id="message" を使用するのが最も安定

### ● 送信ボタン（submit）

```html
<button id="chat-send-button" type="submit"> ... </button>
```

* id が明確に固定されている
* Playwright ロケータとして最強の安定性

### ● AI 応答メッセージ（message-item）

```html
<div id="message-item-2" class="message-received ..."> ... </div>
```

* 「message-item-N」の形式でメッセージが連番管理される
* 最新メッセージ：`div[id^='message-item-']` の `.last`

### ● 本文（markdown-番号）

```html
<div id="markdown-2" class="markdown"> ... </div>
```

* 各メッセージ本文は `markdown-N` の内部に含まれる
* Markdown がそのまま inner_text で取得可能

---

## 3. ロケータ仕様（Locator Specification）

| 要素          | ロケータ                                                | 備考           |
| ----------- | --------------------------------------------------- | ------------ |
| 入力欄         | `#message`                                          | テキスト入力欄      |
| 送信ボタン       | `#chat-send-button`                                 | SVG ボタン      |
| 最新メッセージ（全体） | `"div[id^='message-item-']".last`                   | AI/ユーザー共通    |
| 最新メッセージ本文   | `last_message_item.locator("div[id^='markdown-']")` | Markdown 展開済 |

---

## 4. イベント待機仕様（Wait Strategy）

### ● メッセージ送信 → 応答検出

旧方式（visible / inner_text 変化）は不安定なため廃止する。

v0.5 では以下の **メッセージ件数増加方式** を採用する：

```python
before_count = page.locator("div[id^='message-item-']").count()

# …送信処理…

page.wait_for_function(
    "(before) => document.querySelectorAll(\"div[id^='message-item-']\").length > before",
    arg=before_count,
    timeout=timeout
)
```

理由：

* SPA / Tailwind のアニメーションに影響されない
* visible / opacity / bounding-box 等のゆらぎがない
* DOM における新規 message-item が増えた事実のみを見るため堅牢

---

## 5. PageObject 実装（ChatPage v0.5）

```python
# ==========================================================
# ChatPage v0.5  （Qommons.AI 最新 DOM 完全対応）
# ==========================================================

from .base_page import BasePage


class ChatPage(BasePage):
    """
    チャット画面 PageObject（DOM完全解析版）
    - 入力欄:         #message
    - 送信ボタン:     #chat-send-button
    - 最新メッセージ: div[id^='message-item-']
    - 本文抽出:       div[id^='markdown-']
    """

    # 入力欄
    @property
    def input_box(self):
        return self.page.locator("#message")

    # 送信ボタン
    @property
    def send_button(self):
        return self.page.locator("#chat-send-button")

    # 最新メッセージの要素
    @property
    def last_message_item(self):
        return self.page.locator("div[id^='message-item-']").last

    # 最新メッセージ本文
    @property
    def last_message_content(self):
        return self.last_message_item.locator("div[id^='markdown-']")

    # ------------------------------------------------------
    # Workflow API
    # ------------------------------------------------------
    def input_message(self, text: str, *, evidence_dir=None):
        self.safe_fill(
            self.input_box,
            text,
            evidence_dir=evidence_dir,
            label="chat_input_error",
        )

    def send(self, *, evidence_dir=None):
        self.safe_click(
            self.send_button,
            evidence_dir=evidence_dir,
            label="chat_send_error",
        )

    def ask(self, text: str, *, evidence_dir=None):
        # 送信前のメッセージ数
        before_count = self.page.locator("div[id^='message-item-']").count()

        # 入力 + 送信
        self.input_message(text, evidence_dir=evidence_dir)
        self.send(evidence_dir=evidence_dir)

        # 新規メッセージ到着待ち
        self.page.wait_for_function(
            """(before) => {
                return document.querySelectorAll("div[id^='message-item-']").length > before;
            }""",
            arg=before_count,
            timeout=self.timeout,
        )

        # 安定化
        self.page.wait_for_timeout(500)

        # 本文抽出
        return self.last_message_content.inner_text().strip()
```

---

## 6. テスト観点（Testability Points）

* メッセージ件数による応答検出は UI 変更に非常に強い
* “最新メッセージ = last(message-item)” は DOM が並び変わらない前提で安定
* input と送信ボタンが id 固定のため破損リスクが低い
* ChatSelectPage と独立して正常動作できるため Smoke Test 向き

---

## 7. 保守上の注意（Maintenance Notes）

1. message-item / markdown の命名規則が変更されると本実装は要更新
   → DOM チェックの手順を定期 CI に組み込む余地あり

2. ChatPage は “AI 応答の可観測性” に依存するため
   ローディングスピナーやエラーメッセージの DOM も別途観測予定

3. 応答がストリーミング（逐次表示）への変更が入った場合は
   count 方式 → streaming chunk 検知方式へアップデートする必要あり

---

## 8. バージョン履歴（History）

### v0.5（2025-12-10）

* DOM 完全再解析に基づくロケータ全面刷新
* message-item / markdown により AI 応答取得を安定化
* 送信前後のメッセージ件数差分による応答待ち方式を採用
* Smoke Test v0.3 が初めて完全成功

---

**以上。ChatPage v0.5 の正式設計書。**

