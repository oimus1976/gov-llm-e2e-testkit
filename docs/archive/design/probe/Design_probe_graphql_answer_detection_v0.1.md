# 📘 **Design_probe_graphql_answer_detection_v0.1.md**

**Qommons.AI — GraphQL createData に基づく回答収束検知プローブ設計**

---

## 1. Purpose（目的）

本設計書は、Qommons.AI の回答収束方式（案1〜案3）において
**最も確実な方式である案2「GraphQL createData 監視」** を検証するための
**Probe v0.2（検証専用ツール）** の仕様を定義する。

目的は以下：

1. **createData.value を “確定回答” として抽出できるかを実測で確認する**
2. `POST → createData → GET` の時系列関係をログ化し、再現性を担保する
3. ChatPage.ask() vNext の設計根拠とする

---

## 2. Background（背景）

### 2.1 probe v0.1 の成果（一次情報）

jsonl より以下が実測で確認された：

* **POST /messages**（質問送信）
* **GraphQL createData（assistant#<本文> を含む）**
* **GET /messages**（保存結果反映）

よって、回答の最初の確定ソースは **GraphQL createData.value** である。
→ DOM のストリームテキストは途中断片であり、回答判定には不適。

---

## 3. Probe v0.2 のスコープ定義

### 3.1 本プローブが担うこと

* 1回目メッセージ送信直後から **全XHR/GraphQLを監視**
* GraphQL `/graphql` の中で
  **mutation createData** のレスポンスのみ抽出
* value に含まれる
  **assistant# 以降全テキストを抽出**
* timestamp / raw payload を保存

### 3.2 本プローブが担わないこと

* DOM 監視
* 完了判定ロジックの実装（これは ChatPage vNext の領域）
* POST `/messages` の API 再現
* CI 組み込み

本プローブは **純粋に一次データを収集する観測ツール**である。

---

## 4. Architecture（アーキテクチャ）

### 4.1 前段テンプレート（Stable Core）

Probe v0.2 は
`template_prepare_chat_v0_1.py`
で返される以下をそのまま利用する：

```
page, context, chat_id = prepare_chat_session()
```

このテンプレートは以下を保証する：

* ログイン成功
* プライベートナレッジチャットへの遷移成功
* 1回目メッセージ送信成功
* chat_id の取得成功

テンプレート本体は **probe の都合で変更しない**。

### 4.2 レスポンスと chat_id の紐付け

Probe v0.2 は、テンプレートから返却された `chat_id` のみを対象として
GraphQL createData / GET /messages を関連付ける。

- GraphQL 側:
  - `json.data.createData.sk` に含まれる `<chat_id>#messages#...` をパースし、
    テンプレートから渡された `chat_id` と一致するもののみを「対象チャット」として扱う。
- GET /messages 側:
  - リクエスト URL に `/api/v1/chat/<chat_id>/messages` を含むレスポンスのみ記録する。


---

## 5. Detailed Flow（詳細フロー）

1. `page.on("response", ...)` を登録する。
2. テンプレート `prepare_chat_session()` を呼び出し、`page, context, chat_id` を取得する。
   - テンプレート内部では「1回目メッセージ送信」が行われる。
3. 以降 30 秒間、全 response を監視し、対象となる
   - POST /messages
   - GraphQL /graphql（createData）
   - GET /messages（指定 chat_id のみ）
   をログに記録する。


---

## 6. Output（出力）

`/sandbox/xhr_probe_TIMESTAMP/graphql_probe.jsonl`

行ごとに：

```json
{
  "ts": "...",
  "kind": "graphql" | "rest_post" | "rest_get",
  "chat_id": "<uuid>",
  "raw": {...}
}
```
観測全体のサマリとして、別途 `summary.json` を出力する:
```json
{
  "chat_id": "<uuid>",
  "status": "ok" | "no_graphql" | "mismatch_with_rest",
  "graphql_answer": "<assistant text or null>",
  "rest_answer": "<assistant text or null>",
  "has_post": true | false,
  "has_get": true | false,
  "has_graphql": true | false
}
```
---

## 7. Validation Criteria（検証成功条件）

Probe v0.2 の 1 回の実行結果は、最低限以下を満たすこと:

- summary.json が出力されていること。
- `has_post` が true であること。
- 少なくとも 1 回の GET /messages が観測されていること。

そのうえで、以下のパターンを分類する:

- status = "ok"
  - has_graphql = true
  - graphql_answer と rest_answer が非nullかつ完全一致
- status = "no_graphql"
  - has_graphql = false（createData が観測されなかった）
- status = "mismatch_with_rest"
  - has_graphql = true
  - 両者が非nullだが一致しない

---

## 8. Future Work（次段階）

Probe v0.3（ChatPage.ask vNext の前段）では：

* createData arrival を「完了イベント」と扱う
* ChatPage.ask() vNext に統合
* 18問連続テストで安定性検証
* CI 版の最適化（軽量監視）を設計

---

# 📘 **Design_probe_graphql_answer_detection_v0.2.md — 完成**

---

以上が **probe v0.2 の公式設計書（PENTA 出力）**です。
GRAND_RULES v4.2 と Debugging_Principles v0.2 に完全準拠しており、
v0.1 → v0.2 の知見もすべて反映しています。

---

