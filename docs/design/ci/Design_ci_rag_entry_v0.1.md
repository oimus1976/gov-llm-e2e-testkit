---
title: Design_ci_rag_entry_v0.1
project: gov-llm-e2e-testkit
phase: F7 (運用・保守フェーズ)
status: Design (Proposed)
version: v0.1
date: 2025-12-18
---

## 1. Purpose（目的）

本設計は、
**RAG QA（評価・考察）に進む前段として必要な「入口検証」を CI として定義する**ことを目的とする。

本 CI の役割は以下に**厳密に限定**される。

* RAG QA 実行に必要な **前提条件が満たされているか** を検証する
* 基盤破壊・入力不備・資産誤消費といった
  **「入ってはいけない状態」を機械的に遮断する**
* RAG QA の **品質・優劣・妥当性を判断しない**

本 CI は **評価 CI ではない**。

---

## 2. Non-Goals（非目的・やらないこと）

本設計では、以下を**意図的に行わない**。

* RAG 回答の品質評価
* 指標算出（Evidence Hit Rate / Hallucination Rate / Answer Stability）
* PASS / WARN / INFO 等の評価ラベル付与
* HTML / Markdown 等の優劣判断
* LGWAN 環境での CI 実行

これらは **F7 の責務外**であり、
将来フェーズ（未定義）または CI 外の人手運用に委ねる。

---

## 3. Authority（設計根拠）

本設計は、以下の確定文書を正本とする。

* Roadmap v1.2
* PROJECT_STATUS v0.6.6
* Design_ci_e2e_v0.1.2（F5 基盤 CI）
* Design_rag_f4_eval_v0.1
* Design_f4_trial_dataset_v0.1

特に以下を**不変条件**とする。

* **F5 基盤 CI（e2e.yml）は凍結され、変更しない**
* F4 成果物は「判断材料」であり、CI が結論を出さない

---

## 4. CI 全体構造（Two-Gate Model）

本 CI は、以下の **二段ゲート構造**を取る。

```
Gate 0: Foundation Check（必須・自動）
   ↓
Gate 1: RAG Entry Check（条件検証）
```

いずれかのゲートで失敗した場合、
**RAG QA 入口は不成立（FAIL）** と判定し、以降を実行しない。

---

## 5. Gate 0：Foundation Check（基盤確認）

### 5.1 目的

RAG QA 以前に、
**E2E テスト基盤が成立していること**を確認する。

### 5.2 実装方針

* 既存の **F5 基盤 CI（e2e.yml）をそのまま実行**
* Smoke Test のみを対象とする
* 新たな条件分岐・matrix・拡張は行わない

### 5.3 失敗条件（FAIL）

* UI 送信が成立しない
* Answer Detection Layer が観測不能
* submit–probe 相関が確定不能

※ これらは **RAG QA 以前の基盤破壊**である。

---

## 6. Gate 1：RAG Entry Check（入口検証）

### 6.1 目的

RAG QA に進むための **前提条件・入力条件・資産保護条件**を検証する。

### 6.2 入力（必須）

CI 起動時に、以下の入力を明示的に受け取る。

| 項目          | 説明                             |
| ----------- | ------------------------------ |
| RAG_PROFILE | html / markdown / plain_text 等 |
| CASE_SET    | case01–03 / custom 等           |
| RUN_MODE    | collect-only 固定（v0.1）          |

### 6.3 検証内容

#### 6.3.1 構造検証

* F4 試金石データの三層構造
  （Raw Evidence / Execution Context / Derived Summary）
* JSON Schema Draft 2020-12 準拠

#### 6.3.2 実行条件検証

* profile / knowledge_source_id の明示
* 実行条件が Raw / Context に記録可能であること

#### 6.3.3 資産保護検証

* Golden Question Pool
* Golden Ordinance Set

上記が **誤って消費・改変されないこと**を確認する。

### 6.4 失敗条件（FAIL）

* 入力パラメータ欠落
* スキーマ不整合
* Golden 資産の誤使用が検知された場合

これらは **入口不成立**とみなす。

---

## 7. Failure Semantics（失敗の意味論）

本 CI における **FAIL は一種類のみ**である。

> **RAG QA 入口が成立していない**

FAIL は以下を意味しない。

* RAG 回答の品質が低い
* モデルが劣っている
* HTML / Markdown が不適切である

---

## 8. Artifacts（成果物）

本 CI が生成・保存する成果物は以下に限定する。

* Raw Evidence（回答生ログ）
* Execution Context（実行条件）
* Entry Check 結果（OK / NG）

評価値・スコア・優劣判断は **含めない**。

---

## 9. Future（将来拡張・拘束なし）

以下は **本設計では行わないが、将来検討可能**とする。

* 指標算出 CI
* 自動評価
* CI による合否判定
* LGWAN 対応

これらを行う場合は、
**新フェーズ・新設計として明示的に定義する**。

---

## 10. Conclusion（結論）

Design_ci_rag_entry_v0.1 は、

* F5 基盤 CI を尊重し
* F4 成果物の位置づけを侵害せず
* F7 フェーズにおける **安全な入口**を提供する

ための **最小かつ誤解耐性のある CI 設計**である。

本設計は、
**RAG QA を CI に入れるための設計ではなく、
CI に入れてよい状態かを判定する設計**である。

---

## 付録（Appendix A）

---

## Gate1（RAG Entry Check）pytest 実装境界

**— MUST / MUST NOT 定義（FIX）**

## 0. 位置づけ（前提）

Gate1 は、
**RAG QA に「入ってよい状態か」を検証する入口ゲート**であり、
**評価・品質判定・考察を行う層ではない**。

pytest 実装は、
**入口不成立を機械的に検知するための最小ロジック**に限定される。

---

## 1. pytest が **MUST（必ず行うこと）**

### MUST-1：入力条件の存在検証

pytest は、以下が **明示的に与えられていること**を検証しなければならない。

* RAG_PROFILE
* CASE_SET
* RUN_MODE（v0.1 では `collect-only` 固定）

👉 欠落時は **FAIL（入口不成立）**。

---

### MUST-2：実行条件が記録可能であることの検証

pytest は、以下が **Execution Context として記録可能であること**を検証する。

* profile
* knowledge_source_id（または同等の識別子）
* test_run_id

👉 「取得できないが推測できそう」は **不可**。

---

### MUST-3：F4 試金石データ構造の検証

pytest は、以下の **構造的成立性のみ**を検証する。

* Raw Evidence / Execution Context / Derived Summary の三層が存在する
* JSON Schema Draft 2020-12 に適合する

👉 **中身の妥当性・意味解釈は行わない**。

---

### MUST-4：Golden 資産の保護検証

pytest は、以下を **禁止状態として検知**しなければならない。

* Golden Question Pool の消費
* Golden Ordinance Set の改変・上書き

👉 検知時は **FAIL（入口不成立）**。

---

### MUST-5：FAIL 意味論の固定

pytest における FAIL は、
**「RAG QA 入口が成立していない」ことのみを意味する**。

FAIL は以下を意味してはならない。

* RAG 回答の品質不良
* 指標値の悪化
* HTML / Markdown の優劣

---

## 2. pytest が **MUST NOT（やってはいけないこと）**

### MUST NOT-1：評価・スコア算出

pytest は以下を **一切行ってはならない**。

* Evidence Hit Rate の算出
* Hallucination 判定
* Answer Stability の比較
* 数値・スコアの生成

---

### MUST NOT-2：RAG 回答内容への意味介入

pytest は、RAG 回答について以下を行ってはならない。

* 正しい／誤りの判定
* 網羅性・不足の判断
* 表現揺れの吸収
* 人間的妥当性の評価

---

### MUST NOT-3：PASS / WARN / INFO の付与

Gate1 pytest は、

* PASS
* WARN
* INFO

といった **評価ラベルを生成してはならない**。

出口は常に以下の二値のみである。

* **OK（入口成立）**
* **FAIL（入口不成立）**

---

### MUST NOT-4：FAIL 条件の増殖

pytest は、
**設計書に明示されていない条件で FAIL してはならない**。

特に以下は禁止する。

* 回答揺れによる FAIL
* 実行時間超過による FAIL（基盤が生きている場合）
* 外部サービス一時不調による FAIL

---

### MUST NOT-5：F5 基盤 CI への越境

Gate1 pytest は、

* F5 CI のテスト構成
* submit–probe 相関
* Smoke Test の成否

に **一切介入してはならない**。

---

## 3. pytest 実装の責務境界（要約）

pytest が責任を持つのは：

> **「入口条件が満たされているか」の事実確認のみ**

pytest が責任を持たないのは：

> **「RAG QA の結果が良いか悪いか」**

---

## 4. 将来拡張に関する拘束

本 MUST / MUST NOT 定義は、
**Gate1 pytest 実装に対する拘束条件**であり、
将来これを変更する場合は以下を必須とする。

* 新フェーズの定義
* 新設計書の作成
* CHANGELOG / PROJECT_STATUS への明示的記録

**暗黙の拡張は禁止する。**

---

## 5. 結論（FIX）

Gate1 pytest は、

* 実装を「入口検証」に閉じ込め
* 評価・判断・考察を完全に排除し
* FAIL の意味論を単一に保つ

ための **防波堤**である。

本定義に反する pytest 実装は、
**バグではなく設計違反**として扱う。

---

# 🧪 F4 スキーマ検証：具体的チェック項目表（Gate1 用・FIX）

## 0. 前提（再確認）

* 対象：**F4 試金石データ**
* 目的：**入口成立性の検証のみ**
* 実装主体：Gate1 pytest
* 出力：OK / FAIL（二値のみ）

---

## 1️⃣ 構造レベル（Top-level）

| ID   | チェック内容                            | MUST / MUST NOT | FAIL 条件               |
| ---- | --------------------------------- | --------------- | --------------------- |
| S-01 | データが単一 run を表す JSON オブジェクトである     | MUST            | 配列 / 空 / 非JSON        |
| S-02 | `raw_evidence` が存在する              | MUST            | 欠落                    |
| S-03 | `execution_context` が存在する         | MUST            | 欠落                    |
| S-04 | `derived_summary` が存在する           | MUST            | 欠落                    |
| S-05 | 3 要素以外の top-level key を **拒否しない** | MUST NOT        | 未定義 key の存在で FAIL しない |

📌 **補足**

* key の“意味”は見ない
* 「余分な情報がある」ことは FAIL 理由にならない

---

## 2️⃣ Raw Evidence 層

### 2.1 存在・型

| ID   | チェック内容                                | MUST / MUST NOT | FAIL 条件       |
| ---- | ------------------------------------- | --------------- | ------------- |
| R-01 | `raw_evidence` が object または array である | MUST            | string / null |
| R-02 | 空配列・空 object を **許容する**               | MUST            | 空で FAIL しない   |

### 2.2 禁止事項（重要）

| ID      | 内容             | MUST NOT | FAIL 条件      |
| ------- | -------------- | -------- | ------------ |
| R-NG-01 | 回答テキストの中身を評価   | MUST NOT | 評価処理が存在      |
| R-NG-02 | 回答長・語彙数・一致率を見る | MUST NOT | それらを条件に FAIL |

📌 **意味的妥当性・品質は完全に非対象**

---

## 3️⃣ Execution Context 層

### 3.1 必須情報（存在のみ）

| ID   | チェック内容                       | MUST | FAIL 条件 |
| ---- | ---------------------------- | ---- | ------- |
| C-01 | `rag_profile` が存在する          | MUST | 欠落      |
| C-02 | `case_set` が存在する             | MUST | 欠落      |
| C-03 | `run_mode` が存在する             | MUST | 欠落      |
| C-04 | `run_mode == "collect-only"` | MUST | 他の値     |

📌 **値の“意味”や“妥当性”はここでは見ない**

---

### 3.2 記録可能性（推測禁止）

| ID   | チェック内容                                  | MUST | FAIL 条件 |
| ---- | --------------------------------------- | ---- | ------- |
| C-05 | 値が execution_context 内に **明示的に記録**されている | MUST | 推測が必要   |

---

## 4️⃣ Derived Summary 層

### 4.1 存在・型

| ID   | チェック内容                         | MUST | FAIL 条件     |
| ---- | ------------------------------ | ---- | ----------- |
| D-01 | `derived_summary` が object である | MUST | 非 object    |
| D-02 | 中身が空 object でも許容               | MUST | 空で FAIL しない |

### 4.2 禁止事項（評価混入防止）

| ID      | 内容                           | MUST NOT | FAIL 条件       |
| ------- | ---------------------------- | -------- | ------------- |
| D-NG-01 | 数値スコアの有無を評価                  | MUST NOT | 数値があるだけで FAIL |
| D-NG-02 | EHR / HR / Stability の存在チェック | MUST NOT | それらを期待する      |

📌 **Derived Summary は「あってよいが、使わない」**

---

## 5️⃣ Golden 資産保護（入口として最重要）

| ID   | チェック内容                           | MUST | FAIL 条件   |
| ---- | -------------------------------- | ---- | --------- |
| G-01 | Golden Question Pool を参照専用で扱っている | MUST | 書換痕跡      |
| G-02 | Golden Ordinance Set を改変していない    | MUST | 差分検出      |
| G-03 | CI 実行により Golden 資産が消費されていない      | MUST | 使用回数カウント等 |

📌 **検知方法は問わないが、検知時は即 FAIL**

---

## 6️⃣ 明示的に「チェックしない」項目（FAIL にしない）

以下は **存在しても・欠落しても FAIL にしてはならない**。

* 回答内容の正しさ
* 回答の長さ・語彙
* 回答間の揺れ
* HTML / Markdown の差
* 実行時間
* LLM モデル名
* ネットワーク一時失敗（基盤が生きている場合）

---

## 7️⃣ FAIL 意味論（再固定）

このチェック項目表に基づく FAIL は、
**常に以下のみを意味する**。

> **RAG QA 入口が成立していない**

それ以上でも以下でもない。

---

## 8️⃣ この表の使い方（実装指針）

* Gate1 pytest は
  **この表の各 ID を assert に写すだけ**
* 新しい assert を足したくなったら
  👉 **設計違反の疑い**として立ち止まる
* 変更が必要な場合は
  👉 新フェーズ / 新設計が必須

---
