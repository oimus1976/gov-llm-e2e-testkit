# Chat Answer Detection — GraphQL messages query 観測メモ v0.1
**Type:** design_memo  
**Status:** Observation / Non-normative  
**Last Updated:** 2025-12-12

---

## 0. この文書の位置づけ（重要）

本メモは **設計書（Design_XXX）ではない**。  
以下の目的で作成された **設計メモ（design_memo）**である。

- 実測により得られた一次情報を整理する
- 将来の設計更新（Design_chat_answer_detection_v0.2）の判断材料を残す
- 現行設計（v0.1）を**変更・上書きしない**

本メモは **仕様を定義しない**。  
拘束力・規範力は持たない。

---

## 1. 背景

Answer Detection Layer の検証過程において、以下が実測された。

- GraphQL createData（生成ストリーム）が **発火しないケース**が存在
- その一方で、GraphQL API 経由で **messages 一式を取得できるレスポンス**が確認された

この挙動は、既存設計書：

- Design_chat_answer_detection_v0.1
- Design_probe_graphql_answer_detection_v0.1

の想定と **矛盾はしないが、明示されてもいなかった経路**である。

---

## 2. 観測された一次情報（事実）

以下は、実行ログおよび `graphql_probe.json` に基づく **確定事実**である。

### 2.1 GraphQL messages query の存在

- GraphQL レスポンス内に `messages` 配列が存在
- 配列には以下の role が含まれる：
  - system
  - user
  - assistant
- assistant.content には **最終的な AI 応答全文**が含まれている

### 2.2 createData との非同期性

- 上記 messages 取得時点で：
  - GraphQL createData は観測されていない
  - REST `/messages` の POST / GET は観測されている

つまり：

> **GraphQL は使用されているが、  
> 回答生成の streaming（createData）は必ずしも使用されない**

---

## 3. 解釈（推測を含まない範囲）

以下は **事実から論理的に導かれる範囲の解釈**である。

### 3.1 GraphQL messages query の役割

- GraphQL messages query は
  - 回答生成そのものを制御していない
  - **完成済みのチャット状態を取得する API**として機能している

### 3.2 REST /messages との関係

- REST /messages と GraphQL messages query は
  - 同一内容（user / assistant メッセージ）を返す
  - 正本性は **REST /messages 側にある**と解釈するのが安全

---

## 4. 設計への含意（暫定）

※ 本節は **設計変更ではなく、含意の整理**である。

### 4.1 Answer Detection への影響

- GraphQL createData  
  → 「出現すれば有力な生成シグナル」  
  → **必須条件にはできない**
- REST /messages  
  → **必須の安定経路**
- GraphQL messages query  
  → **検証用セカンダリ経路として利用可能**

### 4.2 Dual Validation Path の補強

現行設計で想定されている Dual Validation Path は、

- REST（必須）
- GraphQL（補助）

という構造を持つが、  
GraphQL 内部にも **役割の違う 2 系統**が存在する可能性が示唆された。

---

## 5. 非対象事項（明示）

本メモでは、以下を行わない。

- GraphQL messages query を正式仕様として採用しない
- probe の観測対象を変更しない
- ChatPage.ask の実装を変更しない
- Design_chat_answer_detection_v0.2 を定義しない

---

## 6. 次アクションへの接続

本メモは、以下のいずれかが満たされた時点で参照される。

- GraphQL messages query の再現性が複数回確認された場合
- createData 発火条件が整理された場合
- Answer Detection 設計を v0.2 に更新する判断を行う場合

---

## 7. 結論（メモとしてのまとめ）

- GraphQL messages query は **実在し、安定して応答を返す**
- これは createData とは独立した経路である
- 現時点では **検証用セカンダリ経路として扱うのが妥当**
- 設計更新は **保留**とする

本メモは、その判断根拠を残すためのものである。
