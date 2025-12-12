# Observation_submit_probe_correlation_v0.1（確定版）

**Source:** `summary.json`, `graphql_probe.jsonl`（probe v0.2 実行結果）
**Date:** 2025-12-13
**Status:** Observation only（設計判断なし）

---

## 1. Scope

* 対象：probe v0.2 実行により生成された **`summary.json`** および **`graphql_probe.jsonl`**
* 目的：**submit_id ↔ probe 相関設計**の前提となる**観測事実**の確定
* 非目的：相関方式の決定、submit_id の設計、実装案の提示

---

## 2. Observed Log Sources

### 2.1 Summary（`summary.json`）

* **chat_id**: `cfbe75c3-6fb7-4bd1-aac1-fbc5d0cc2b1b`
* **status**: `no_graphql`
* **first_graphql_ts**: `null`
* **graphql_answer**: `null`
* **rest_answer**: 取得あり（本文テキスト）
* **has_post**: `true`
* **has_get**: `true`
* **has_graphql**: `false`
* **event_count**: `23`
* **output_dir**: `...\scripts\xhr_probe_20251213_045959`
* **jsonl_path**: `...\scripts\xhr_probe_20251213_045959\graphql_probe.jsonl`

---

### 2.2 Event Log（`graphql_probe.jsonl`）

* 記録形式：JSON Lines（時系列）
* 主な event kind：

  * `rest_post`（POST /messages）
  * `rest_get`（GET /messages）
  * `other`（Google Analytics、認証、静的リソース等）
* **GraphQL createData に相当する event kind は観測されていない**

---

## 3. Timeline（要点・JST）

1. **04:59:59.xxx**

   * Google Analytics（`kind: other`、POST 204）
   * **chat_id なし**

2. **04:59:59.614**

   * `PUT /api/v1/chat/{chat_id}/messages`（200）
   * **chat_id あり**

3. **05:00:00.247**

   * `POST /api/v1/chat/{chat_id}/messages`（200、`kind: rest_post`）
   * **chat_id あり**

4. **05:00:00.305–00.382**

   * Cognito Identity（POST 200）
   * **chat_id なし**

5. **05:00:52.294**

   * Lambda URL への POST（200、`kind: other`）
   * **chat_id なし**
   * ※ **GraphQL createData イベントとしては観測されていない**

6. **05:00:53.270**

   * `GET /api/v1/chat/{chat_id}/messages`（200、`kind: rest_get`）
   * **assistant 最終回答を含む messages 配列を取得**
   * **chat_id あり**

---

## 4. Confirmed Facts（確定事実）

* **REST GET `/messages` 経路で最終回答が取得できている**

  * `kind: rest_get`、200
  * `messages[]` に `role: assistant` の本文が存在
  * `summary.json.rest_answer` と内容が一致
* **REST POST `/messages` が観測されている**

  * `kind: rest_post`、200
* **GraphQL createData は“イベントとして”観測されていない**

  * `has_graphql = false`
  * `first_graphql_ts = null`
  * `graphql_probe.jsonl` に `kind: graphql` 相当が存在しない
* **chat_id は REST 系イベントに付与されている**

  * PUT / POST / GET で一致
  * GA / 認証 / 静的リソースでは `chat_id = null`
* **複数の非本質イベント（ノイズ）が混在**

  * GA、フォント取得、認証等

---

## 5. Observed Correlatable Information（観測可能な相関素材）

| 項目                   | 観測可否       | 備考                    |
| -------------------- | ---------- | --------------------- |
| chat_id              | ✅          | REST PUT/POST/GET に付与 |
| HTTP method / URL    | ✅          | PUT / POST / GET      |
| イベント時刻（ts）           | ✅          | 全 event に付与           |
| message.id           | ✅（GET 応答内） | assistant メッセージに存在    |
| submit_id            | ❌          | **未観測**               |
| GraphQL operation id | ❌          | **未観測**               |

※ 本表は「観測された情報」の列挙に留める。

---

## 6. Non-binding Notes（示唆・非拘束）

* **GraphQL 非発火は summary と event の二層で一致**して観測された。
* **最終回答取得は REST GET に依存**していることが確認された。
* **相関に利用可能な一次情報として**、`chat_id` とイベント時刻（`ts`）が観測されている。

※ 本章は示唆に留め、**設計判断は行わない**。

---

## 7. Conclusion

* **submit_id は現状ログに存在しない**。
* **GraphQL createData はイベントとして観測されていないケースが実在**。
* **最終回答は REST GET `/messages` で取得できる**。
* 相関設計に先立つ**観測事実は確定**した。

---
