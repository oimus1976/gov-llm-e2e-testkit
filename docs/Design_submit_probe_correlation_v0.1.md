# 📘 **Design_submit_probe_correlation_v0.1**

**submit_id ↔ Answer Detection（probe）相関設計**

**Version:** v0.1
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

本設計は、**観測事実（Appendix A）を唯一の根拠**とし、
推測・仮定・将来予測に基づく判断を行わない。

---

## 2. Design Principles（設計原則）

本設計は、以下の原則に従う。

1. **観測事実を超えた推測を行わない**
   設計判断は Appendix A に記載された一次情報のみを根拠とする。

2. **submit（送信）と completion（完了判定）を同一レイヤで扱わない**
   UI 送信責務と意味的完了検知責務は、明確に分離する。

3. **best-effort ではなく traceability（追跡可能性）を優先する**
   相関できない場合は「できない」と判定できる設計を採用する。

4. **既存 probe v0.2 ログとの後方互換性を維持する**
   既存の観測資産を破壊せず、段階的な導入を前提とする。

---

## 3. Scope & Non-Goals（適用範囲・非目標）

### 3.1 In Scope

本設計が対象とする事項は以下である。

* submit_id の**意味的役割定義**
* submit_id と probe 観測結果の**相関関係**
* テスト・ログ・CI における**追跡可能性の確立**

### 3.2 Out of Scope

以下は本設計の対象外とする。

* submit_id の生成タイミングや実装方法
* probe の内部検知ロジック変更
* UI DOM 構造の安定化
* 再送制御、並列 submit、最適化議論

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

このため、現状では以下の課題が存在する。

* 同一 chat_id 内での**送信試行単位の区別**
* 時間的に近接したイベント間の**曖昧性の排除**
* 「この回答がどの送信に対応するか」を**確実に説明すること**

submit_id は、これらの欠損を補うための**相関用一次キー**として導入される。

---

## 6. Responsibility Boundary（責務境界）

### 6.1 ChatPage.submit の責務

ChatPage.submit は、以下を責任範囲とする。

* submit_id の生成
* UI 上の送信試行を**一意な単位**として確定する
* submit_id を外部（テスト／probe）へ引き渡す

ChatPage.submit は、**回答の取得や完了判定を行わない**。

---

### 6.2 Answer Detection Layer（probe）の責務

probe は、以下を責任範囲とする。

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
* **bounded time window（概念）**
* REST GET `/messages` に含まれる message.id

本章は「使用可能な素材」の列挙に留め、
具体的な利用方法は定義しない。

---

## 8. Correlation Model（相関モデル概要・概念レベル）

本設計では、以下の概念モデルを採用する。

* submit_id を**一次相関キー**とする
* chat_id、ts、time window を**補助情報**として用いる
* v0.1 では **単一 submit を前提**とする
* 複数 submit が発生し得る将来ケースは**非目標**とする

本章は**概念定義のみ**を扱い、
アルゴリズムや実装手順は記載しない。

---

## 9. Failure & Ambiguity Handling（相関失敗・曖昧性）

以下のケースを想定する。

* submit_id は存在するが、対応する回答が取得できない
* time window 内に複数の候補回答が存在する
* GraphQL createData が発火しない

これらの場合、probe は **相関不能（correlation failure）** と判定する。

※ これは submit failure とは明確に区別される。

---

## 10. Logging & Traceability（ログと追跡性）

ログには、最低限以下を含める。

* submit_id
* chat_id
* event timestamp（ts）
* 対応する message.id（取得できた場合）

これにより、CI やテストレポートにおいて
送信と回答の対応関係を追跡可能とする。

---

## 11. Compatibility & Migration（互換性・移行）

* submit_id 導入前の probe v0.2 ログは引き続き有効とする
* submit_id は段階的に導入可能である
* 既存テスト資産への破壊的変更は行わない

---

## 12. Summary（要約）

本設計は、

* submit と completion の責務を分離し
* 観測事実に基づいた相関境界を定義し
* テスト・ログ・CI における説明可能性を確保する

ことを目的とする。

---

## Appendix A. Observed Facts

* **Observation_submit_probe_correlation_v0.1** を参照

---
