# 📘 **Design_submit_probe_correlation_v0.2**

**submit_id ↔ Answer Detection（probe）相関設計（完全統合版）**

**Version:** v0.2
**Status:** Design
**Last Updated:** 2025-12-13

---

## 1. Purpose（目的）

本設計書は、**ChatPage.submit が発行する submit_id** と
**Answer Detection Layer（probe）が観測する REST / GraphQL の結果**を
**説明可能（traceable）かつ再現可能**に関連付けるための設計を定義する。

本設計の目的は以下に限定される。

* UI 送信起点（submit）と回答検知結果（probe）を**同一の試行単位**として結び付ける
* GraphQL createData が発火しないケースを含め、**観測事実に基づいた相関境界**を確定する
* テスト・ログ・CI において、**「なぜこの回答がこの送信に対応するのか」**を説明可能にする
* 相関結果を **状態として表現**し、テスト結果表示と分離する

本設計は、**観測事実を唯一の根拠**とし、
推測・仮定・将来予測に基づく判断を行わない。

---

## 2. Design Principles（設計原則）

本設計は、以下の原則に従う。

1. **観測事実を超えた推測を行わない**
   設計判断は一次情報のみを根拠とする。

2. **submit（送信）と completion（完了判定）を同一レイヤで扱わない**
   UI 送信責務と意味的完了検知責務は明確に分離する。

3. **best-effort より traceability（追跡可能性）を優先する**
   相関できない場合は「できない」と判定できる設計を採用する。

4. **ユーザー側テスト基盤の責務境界を厳密に守る**
   AI 内部状態やサービス内部挙動を推測しない。

5. **既存 probe v0.2 ログとの後方互換性を維持する**

---

## 3. Scope & Non-Goals（適用範囲・非目標）

### 3.1 In Scope

* submit_id の**意味的役割定義**
* submit_id と probe 観測結果の**相関関係**
* 相関を **状態として表現**する語彙
* 相関状態とテスト結果（PASS / WARN / INFO）の**写像**
* テスト・ログ・CI における**追跡可能性の確立**

### 3.2 Out of Scope

* submit_id の生成タイミングや UI 実装
* probe の内部検知ロジック変更
* UI DOM 構造の安定化
* 再送制御、並列 submit、最適化議論
* AI の生成意図・生成失敗理由の推定
* FAIL 判定の導入

---

## 4. Observed Facts Reference（観測事実の参照）

本設計は、以下の観測事実文書を前提とする。

* **Observation_submit_probe_correlation_v0.1**

本文では観測事実を再掲せず、
**Appendix A として参照のみ**を行う。

---

## 5. Correlation Problem Definition（相関課題の定義）

現状の probe ログから、以下の情報が**観測できている**。

* chat_id
* REST GET `/messages` に含まれる message.id
* event timestamp（ts）

一方で、以下の情報は**観測できていない**。

* UI 送信起点を一意に表す submit_id

このため、以下の課題が存在する。

* 同一 chat_id 内での**送信試行単位の区別**
* 時間的に近接したイベント間の**曖昧性**
* 「この回答がどの送信に対応するか」を**説明可能にすること**

submit_id は、これらの欠損を補うための
**相関用一次キー**として導入される。

---

## 6. Responsibility Boundary（責務境界）

### 6.1 ChatPage.submit の責務

* submit_id の生成
* UI 上の送信試行を**一意な単位**として確定
* submit_id を外部（テスト／probe）へ引き渡す

ChatPage.submit は、**回答の取得や完了判定を行わない**。

---

### 6.2 Answer Detection Layer（probe）の責務

* REST / GraphQL イベントの観測
* 回答完了判定
* submit_id と観測結果の関連付け
* 相関不能時の**明示的な判定**

---

## 7. Correlation Inputs（相関に用いる情報）

相関に使用可能な情報は以下に限定される。

* submit_id（UI 起点の一次キー）
* chat_id（サーバ側識別子）
* event timestamp（ts）
* bounded time window（概念）
* REST GET `/messages` に含まれる message.id

本章は「使用可能な素材」の列挙に留め、
具体的な利用方法は定義しない。

---

## 8. Correlation Model（相関モデル概要・概念）

* submit_id を**一次相関キー**とする
* chat_id、ts、time window を**補助情報**として用いる
* v0.2 では **単一 submit を前提**とする
* 複数 submit が発生し得る将来ケースは**非目標**

---

## 9. Failure & Ambiguity Handling（相関失敗・曖昧性）

以下のケースを想定する。

* submit_id は存在するが、対応する回答が取得できない
* time window 内に複数の候補回答が存在する
* GraphQL createData が発火しない

これらの場合、probe は
**相関未成立（Not Established）** または
**相関不可（No Evidence）** と判定する。

※ submit failure とは明確に区別される。

---

## 10. Logging & Traceability（ログと追跡性）

ログには、最低限以下を含める。

* submit_id
* chat_id
* event timestamp（ts）
* 対応する message.id（取得できた場合）

---

## 11. Compatibility & Migration（互換性・移行）

* submit_id 導入前の probe v0.2 ログは引き続き有効
* submit_id は段階的に導入可能
* 既存テスト資産への破壊的変更は行わない

---

## 12. Correlation as a State（相関という“状態”）

相関は、以下の **排他的な状態**のいずれかとして表現される。

### S0. Unassessed（未評価）

* 観測データは存在
* 相関評価をまだ行っていない

### S1. Candidate Exists（相関候補あり）

* submit 後、同一 chat_id を共有する観測イベントが存在

### S2. Established（相関成立）

* submit 起点として **説明可能な因果関係**が成立
* 他の submit でも説明できない

### S3. Not Established（相関未成立）

* 候補は存在するが、特定・説明ができない

### S4. No Evidence（相関不可）

* submit 後、該当しうる観測イベントが存在しない

---

## 13. Observable Signals（観測定義）

ユーザー側テスト基盤が観測可能なのは以下に限られる。

* submit 後、同一 chat_id に対して
  **assistant role を含む messages が取得できたか**

以下は観測不能であり、本設計では扱わない。

* AI が「答えようとした」意図
* ネットワーク断やサービス内部エラーの原因
* セーフティブロックの理由

---

## 14. Mapping to Test Results（状態 → テスト結果の写像）

| 相関状態            | テスト結果 | 意味            |
| --------------- | ----- | ------------- |
| Established     | PASS  | 観測可能な応答が返却された |
| Not Established | WARN  | 応答は観測されなかった   |
| No Evidence     | INFO  | 判断材料が存在しない    |
| Unassessed      | INFO  | 評価対象外         |

### 設計上の注意

* FAIL は使用しない
* WARN は失敗を意味しない
* INFO は CI 失敗を引き起こさない

---

## 15. Non-Guarantees（保証しないこと）

* AI が答えようとしたこと
* 応答が返らなかった理由
* submit と応答の 1:1 対応
* サービス内部挙動の推定

---

## 16. Summary（要約）

* submit ↔ probe 相関を **状態として定義**
* 観測可能な事実のみを扱う
* 状態とテスト結果を **写像で分離**
* v0.2 単体で設計が完結する

---

## Appendix A. Observed Facts

* **Observation_submit_probe_correlation_v0.1** を参照

---
