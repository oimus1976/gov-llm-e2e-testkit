---
title: Design_pytest_f4_results_writer_v0.1.2
project: gov-llm-e2e-testkit
phase: F4 (RAG Evaluation)
version: v0.1.2
status: Approved
date: 2025-12-16
---

# Design_pytest_f4_results_writer v0.1.2

## 1. Purpose（目的）

本設計書は、F4 RAG 評価フェーズにおいて、
pytest 実行結果を **差分観測用の Markdown ログ**として
自動生成する writer 機構の仕様を定義する。

本 writer は以下を満たすことを目的とする。

* HTML / Markdown ナレッジ差分評価を **同一フォーマット**で記録する
* 評価基準 v0.1（Evidence / Hallucination / Stability）に完全準拠する
* 観測事実と判断を分離し、将来の自動集計・CI 連携を阻害しない

---

## 2. Scope（対象範囲）

### 対象

* pytest 実行層（F4 用テスト）
* `F4_results_template_v0.1.md` に基づく結果ログ生成
* Case 単位の実行結果記録

### 対象外（非責務）

* ナレッジのアップロード / 削除
* HTML / Markdown 変換処理
* RAG の良否判定・自動評価
* Golden 資産の管理
* アカウント切替・認証制御

---

## 3. Design Principles（設計原則）

1. **writer は推測しない**
2. **一次事実のみを記録する**
3. **取得経路ではなく、確定値を扱う**
4. **F4 v0.1 の運用ルールを逸脱しない**
5. **観測不能な事実は「未確認（unverified）」として明示的に記録する**

---

## 4. Profile の位置づけ（重要）

### 4.1 基本方針

* profile（例：`html`, `markdown`）は
  **F4 評価結果ログに必須の一次メタデータ**である
* writer は **profile を必ず明示的な値として受け取る**
* writer 自身が profile を推測・解決してはならない

---

### 4.2 Profile Resolution Order（v0.1.2）

pytest 実行時の profile は、以下の **優先順位で解決される**。

1. pytest コマンドラインオプション（`--profile`）
2. env.yaml に明示的に記載された profile
3. デフォルト profile（`html`）

いずれの場合も、最終的に writer に渡される時点では
**解決済みの profile 値でなければならない**。

writer は profile の解決過程を知らず、
**確定値のみを扱う**。

---

### 4.3 デフォルト profile の扱い

* profile が明示されなかった場合、
  **デフォルト値として `html` を使用する**
* この場合もログ上は省略せず、以下を必ず記録する：

```yaml
profile: html
profile_source: default
```

※ これは暗黙推測ではなく、
　本設計で定義された **正式な既定値**である。

---

## 5. Execution Context（v0.1.2 追加）

### 5.1 目的

F4 フェーズでは profile 切替およびアカウント切替が
**完全手動**で行われる。

そのため pytest 実行結果ログには、
**当該実行がどのアカウント文脈で行われたかを説明可能な補助情報**
を残すことが望ましい。

Execution Context は評価判断や自動切替を目的とせず、
**評価ログの説明責任を補強するための補助メタデータ**としてのみ使用される。

---

### 5.2 基本方針

* Execution Context は **任意メタデータ**である
* writer は **与えられた値を加工せず記録する**
* 取得・構築・検証は **pytest 実行層の責務**である
* 未確認の場合は **未確認であることを明示的に記録する**

Execution Context は pytest 実行層が提供する場合にのみ記録される。
記録されない場合、writer は補完・生成を行わず、
**未指定のままログを生成する**。

---

### 5.3 login_identity

#### 概念定義

`login_identity` は、
**本 pytest 実行がどのログイン主体で行われたかを説明するための補助情報**
である。

これはテスト結果の合否判定や自動処理には使用されず、
**後から人間が評価ログを検証するための説明材料**としてのみ用いられる。

---

#### 構造（推奨）

```yaml
execution_context:
  login_identity:
    configured:
      source: env.yaml
      value: <string>
    observed:
      status: verified | unverified
      value: <string | null>
      note: <string>
```

---

#### 各項目の意味

* **configured**

  * pytest 実行時に設定として与えられたログイン識別子
  * 例：env.yaml に定義された USERNAME / EMAIL
  * **v0.1.2 では必須**

* **observed**

  * 実行中に機械的に観測されたログイン識別子
  * v0.1.2 では **観測不能な状態が正当ケース**
  * 観測不能な場合は以下を必須とする：

```yaml
observed:
  status: unverified
  value: null
  note: "Headless 実行における取得可否が未検証のため"
```

---

### 5.4 禁止事項（重要）

writer は以下を **行ってはならない**。

* login_identity を自動取得・解決・検証する
* env.yaml / OS / UI / API から直接 login_identity を取得する
* login_identity の構築ロジックを内部に持つ
* configured / observed の一致・不一致を判定する
* login_identity を用いた profile / case 判定を行う

---

### 5.5 Responsibility Boundary

login_identity の取得および構築は
**pytest 実行層の責務**である。

pytest 実行層は、

* env.yaml 由来の configured identity
* （取得可能な場合）実行中に観測された observed identity

を用いて login_identity を構築し、
**確定値または未確認状態として writer に渡す**。

writer は、
渡された login_identity を **推測・補完・検証することなく記録する**。

---

## 6. Writer API Specification

### 6.1 入力

#### 必須（v0.1.1 から変更なし）

* case_id: str
* profile: str（解決済み）
* timestamp: datetime
* raw_answer: str
* evidence_terms: list[str]
* observed_hits: list[str]
* hallucination_flags: dict
* stability_notes: dict

#### 任意（v0.1.2 追加）

* execution_context: dict

  * 未指定の場合はログに含めなくてよい

---

## 7. Error Handling

* profile が None / 空文字の場合：即例外
* 必須メタデータ欠落時：ログ生成を中断
* 例外は pytest 実行層へ伝播させる

---

## 8. Relationship to F4 Operation Rules

本設計は以下に完全準拠する。

* F4 RAG 評価フェーズ 運用ルール v0.1.5
* RAG 評価基準 v0.1

本設計は、
アカウント切替・認証・自動化を **一切導入しない**。

---

## 9. Non-Goals（v0.1.2）

以下は **意図的に行わない**。

* login_identity の自動取得・自動検証
* UI / API によるアカウント識別の必須化
* observed 未確認状態の解消を v0.1.x で保証すること
* CI への統合

---

## 10. Summary

* v0.1.2 は **評価ログの説明責任を補強するための設計拡張**である
* writer の責務は **記録専用に固定**される
* login_identity の取得・構築は **pytest 実行層の責務**である
* 観測不能な状態は **設計上の正当ケース**として扱う
* 将来 observed が取得可能になっても **再設計は不要**

---

*(End of Document)*
