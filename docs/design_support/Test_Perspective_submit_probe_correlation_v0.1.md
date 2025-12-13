# 📋 Test Perspective Checklist v0.1

## submit_id ↔ Answer Detection（probe）Correlation

**Project:** gov-llm-e2e-testkit
**Status:** Final (Design Review Aid)
**Version:** v0.1
**Last Updated:** 2025-12-13

---

## 1. Purpose（目的）

本チェックリストは、
**ChatPage.submit v0.6** と **Answer Detection Layer（probe v0.2）** の
相関設計が、

* 責務境界を侵害していないか
* 実装時に誤った結合・誤判定を招かないか
* 一次情報（設計書・観測事実）に基づいて成立しているか

を **実装前に検証するための観点整理**である。

本書は **テストコード仕様書ではない**。
assert / pytest / CI 条件を定義することを目的としない。

---

## 2. Scope（適用範囲）

### In Scope

* submit_id を一次相関キーとする設計妥当性
* submit / probe の MUST / MUST NOT 境界
* REST-only / GraphQL 非発火ケースを含む成立条件整理
* 相関不能ケースの扱いの明文化

### Out of Scope（重要）

* submit / probe の実装方法
* retry / 再送制御
* CI timeout 調整
* DOM / UI 状態の検知方式
* submit_id の外部公開・永続化

---

## 3. ChatPage.submit 側 テスト観点

### 3.1 MUST（満たすべき条件）

* [ ] `submit_id` は **ChatPage.submit 内で必ず生成**される
* [ ] `submit_id` は **1 submit 呼び出しにつき一意**である
* [ ] submit は **UI 送信操作のみ**を責務とする
* [ ] UI が送信を受理したことを
  **最小限の観測（例：入力欄クリア）で確認**している
* [ ] UI 操作失敗時は
  **例外または evidence（diagnostics）を伴って終了**する

---

### 3.2 MUST NOT（やってはいけないこと）

* [ ] 回答完了を判定しない
* [ ] 回答本文を取得・返却しない
* [ ] REST / GraphQL の状態を観測・解釈しない
* [ ] semantic completion を定義しない
* [ ] probe の成功・失敗を推測しない

---

## 4. Answer Detection Layer（probe）側 テスト観点

### 4.1 MUST（満たすべき条件）

* [ ] 回答完了の一次判定は **REST GET /messages** を用いる
* [ ] GraphQL createData は **副次的観測（verification）**として扱う
* [ ] `submit_id` を **submit と probe の一次相関キー**として使用する
* [ ] submit_id と chat_id / message_id の対応関係を
  **観測事実として記録可能**である
* [ ] 待機は **意味的完了優先、時間は fallback**である

---

### 4.2 MUST NOT（重要）

* [ ] UI / DOM 状態に依存しない
* [ ] ChatPage.submit を再呼び出ししない
* [ ] submit 側の `ui_ack` / `diagnostics` を
  **成功・失敗判定に再解釈しない**
* [ ] submit の UI 成功・失敗を
  probe の成立条件に組み込まない

> 注記：
> submit 側の情報は **相関補助メタデータ**であり、
> probe の成立・不成立を左右する根拠にはならない。

---

## 5. ケース分類（成立性テスト観点）

### 5.1 正式なケース分類

| Case | REST | GraphQL | 判定                              |
| ---- | ---- | ------- | ------------------------------- |
| A    | ○    | ○       | **成立（completed_with_graphql）**  |
| B    | ○    | ×       | **成立（completed_rest_only）**     |
| C    | ×    | ×       | **不成立（timeout / inconclusive）** |
| D    | ×    | ○       | 非推奨・観測用（成立条件外）                  |

---

### 5.2 判定原則

* [ ] **REST が返っていれば成立**とみなす
* [ ] GraphQL 非発火は **失敗条件ではない**
* [ ] REST / GraphQL ともに未観測の場合のみ
  **不成立（timeout / inconclusive）**とする

---

## 6. 相関不能ケースの扱い

### 原則（重要）

* [ ] submit_id と回答イベントが相関できない場合、
  **「失敗」と断定してはならない**
* [ ] 相関不能は以下のいずれかとして扱う：

  * 不成立（timeout）
  * 未確定（inconclusive）

### 禁止事項

* [ ] 相関不能を
  submit の失敗と断定する
* [ ] 相関不能を
  probe 実装不良と断定する
* [ ] CI failure と即座に結びつける

---

## 7. 設計レビュー用 最終チェック

* [ ] submit と probe の責務が **一方向依存**になっている
* [ ] submit → probe への情報流れは **相関キーのみ**である
* [ ] probe → submit への逆依存が存在しない
* [ ] REST-only ケースが
  **第一級の成立ケースとして扱われている**
* [ ] 「失敗」という語が
  相関不能・非発火ケースに使われていない

---

## 8. Positioning（位置づけ）

本チェックリストは：

* 実装前レビュー
* 設計妥当性確認
* 実装者・レビュアー間の認識同期

を目的とした **設計補助ドキュメント**である。

本書を満たした後にのみ、
submit / probe 相関の **実装フェーズへ進むことが許可される**。

---
