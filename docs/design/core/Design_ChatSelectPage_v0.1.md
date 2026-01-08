---
title: Design_ChatSelectPage
version: v0.1
status: frozen
created: 2026-01-08
component: ChatSelectPage
layer: PageObject
related:
  - Design_BasePage_v0.2
  - Design_ChatPage_v0.5
  - Design_playwright_v0.1
  - Design_Submit_Blue_Semantics_v0.1
---

# Design: ChatSelectPage

## 1. 目的と位置づけ

ChatSelectPage は、QommonsAI における **チャット選択 UI** を操作するための  
PageObject である。

本 PageObject の責務は以下に限定される。

- `/chat` 画面上で AI / チャットを選択する
- 選択操作により **個別チャット (`/chat/<chat_id>`) へ遷移**させる
- 遷移完了をもって、制御を ChatPage に引き渡す

ChatSelectPage は、チャット内容の生成・送信・完了判定には関与しない。

---

## 2. 前提条件（事実）

- ログイン後、ユーザーは `/chat` に遷移する
- チャット選択操作により、URL は **必ず `/chat/<chat_id>` に遷移する**
- QommonsAI v2.2 以降においても、この URL 遷移仕様は維持されている

※ 本設計では、UI 表示構成や DOM 構造の詳細は前提としない。

---

## 3. 成功条件（凍結）

ChatSelectPage の成功条件は、以下と定義する。

> **URL が `/chat/<chat_id>` に遷移した状態**

- `/chat` への遷移では不十分
- chat_id を含む個別チャット URL への遷移を必須とする

この成功条件は、UI 表示状態や DOM 構造には依存しない。

---

## 4. 既存実装と発生した問題

### 4.1 既存実装（v0.3 以前）

従来の ChatSelectPage 実装では、以下の順序で遷移待機を行っていた。

1. チャット選択要素を click
2. `wait_for_url(/chat/[^/]+$)` を呼び出す

### 4.2 発生した問題（pytest FAIL）

以下の事象が確認された。

- URL は実際には `/chat/<chat_id>` に遷移している
- しかし `wait_for_url` がタイムアウトするケースが発生

この問題は以下の条件で顕在化した。

- SPA 環境において、URL 遷移が **click 処理中または直後**に発生
- `wait_for_url` が **遷移発生後に呼び出される**
- Playwright の仕様上、**過去に発生した遷移イベントは捕捉できない**

結果として、

> **遷移は起きているが、待機が捕捉できていない**

という状態が発生した。

---

## 5. 設計判断（今回凍結）

### 5.1 問題の本質

本問題は以下に起因する。

- UI の変更
- サービス側仕様変更
- chat_id が URL に反映されない

これらではない。

**原因は 100% テストコード側の待機モデルにある。**

---

### 5.2 採用する待機モデル（凍結）

ChatSelectPage における URL 遷移待機は、  
**click 操作と同時に遷移イベントを購読する方式**を採用する。

#### 正式採用パターン

```python
with page.expect_navigation(
    url=re.compile(r"/chat/[^/]+$")
):
    safe_click(...)
```

この方式により：

* URL 遷移が click 前後いずれで発生しても捕捉可能
* SPA / 非SPA を問わず安定
* Playwright のイベントモデルと整合

---

### 5.3 非採用とする方式

以下の方式は **ChatSelectPage では採用しない**。

* click 後に `wait_for_url` を呼び出す方式
* 遷移イベントを伴わない状態監視を主成功条件とする方式

理由：

* 遷移イベントの取り逃しが発生しうる
* 成功条件の意味が曖昧になる

---

## 6. ChatPage との責務分離

* ChatSelectPage

  * チャット選択
  * URL `/chat/<chat_id>` への遷移完了まで

* ChatPage

  * メッセージ入力
  * submit 操作
  * submit blue semantics に基づく完了判定

この責務分離は `Design_Responsibility_Separation.md` に準拠する。

---

## 7. 本設計の適用範囲

* pytest / Playwright による E2E テスト
* Internet / LGWAN 環境の差異に依存しない
* QommonsAI v2.2 以降を含む現行 UI に適用可能

---

## 8. 変更履歴

* v0.1 (2026-01-08)

  * 初版作成
  * ChatSelectPage の成功条件を URL `/chat/<chat_id>` に凍結
  * `wait_for_url` 誤用事例を整理
  * `expect_navigation` 採用を設計判断として記録

---
