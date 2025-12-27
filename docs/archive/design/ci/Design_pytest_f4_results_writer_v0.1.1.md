---
title: Design_pytest_f4_results_writer_v0.1.1
project: gov-llm-e2e-testkit
phase: F4 (RAG Evaluation)
version: v0.1.1
status: Approved (Revised)
date: 2025-12-14
---

# Design_pytest_f4_results_writer v0.1.1

## 1. Purpose（目的）

本設計書は、F4 RAG 評価フェーズにおいて、
pytest 実行結果を **差分観測用の Markdown ログ**として
自動生成する writer 機構の仕様を定義する。

本 writer は以下を満たすことを目的とする。

- HTML / Markdown ナレッジ差分評価を **同一フォーマット**で記録
- 評価基準 v0.1（Evidence / Hallucination / Stability）に完全準拠
- 観測事実と判断を分離し、将来の自動集計・CI 連携を阻害しない

---

## 2. Scope（対象範囲）

### 対象

- pytest 実行層（F4 用テスト）
- F4_results_template_v0.1.md に基づく結果ログ生成
- Case 単位の実行結果記録

### 対象外（非責務）

- ナレッジのアップロード / 削除
- HTML / Markdown 変換処理
- RAG の良否判定・自動評価
- Golden 資産の管理

---

## 3. Design Principles（設計原則）

1. **writer は推測しない**
2. **一次事実のみを記録する**
3. **取得経路ではなく、確定値を扱う**
4. **F4 v0.1 の運用ルールを逸脱しない**

---

## 4. Profile の位置づけ（重要）

### 4.1 基本方針

- profile（例：`html`, `markdown`）は
  **F4 評価結果ログに必須の一次メタデータ**である
- writer は **profile を必ず明示的な値として受け取る**
- writer 自身が profile を推測・解決してはならない

---

### 4.2 Profile Resolution Order（v0.1.1）

pytest 実行時の profile は、以下の **優先順位で解決される**。

1. pytest コマンドラインオプション（`--profile`）
2. env.yaml に明示的に記載された profile
3. デフォルト profile（`html`）

いずれの場合も、最終的に writer に渡される時点では
**解決済みの profile 値でなければならない**。

writer は profile の解決過程を知らず、
確定値のみを扱う。

---

### 4.3 デフォルト profile の扱い

- profile が明示されなかった場合、
  **デフォルト値として `html` を使用する**
- この場合もログ上は省略せず、以下を必ず記録する：

```yaml
profile: html
profile_source: default
````

※ これは暗黙推測ではなく、
　本設計で定義された **正式な既定値**である。

---

## 5. 命名規約（結果ログ）

### 5.1 ファイル名規約（必須）

結果ログのファイル名は以下の要素を **すべて含む**。

```text
<case_id>_<profile>_<timestamp>.md
```

例：

```text
case1_html_20251214_195012.md
case1_markdown_20251214_200033.md
```

### 5.2 上書き禁止

- 同一 case / profile でも **必ず別ファイル**
- 上書き・追記は行わない

---

## 6. Writer API Specification

### 6.1 入力（必須）

- case_id: str
- profile: str（解決済み）
- timestamp: datetime
- raw_answer: str
- evidence_terms: list[str]
- observed_hits: list[str]
- hallucination_flags: dict
- stability_notes: dict

### 6.2 禁止事項

writer は以下を **行ってはならない**。

- profile を env / OS / config から直接取得する
- profile を推測・補完する
- HTML / Markdown の優劣判断を行う
- Case 間の比較・集計を行う

---

## 7. Error Handling

- profile が None / 空文字の場合：即例外
- 必須メタデータ欠落時：ログ生成を中断
- 例外は pytest 層へ伝播させる

---

## 8. Relationship to F4 Operation Rules

本設計は以下に完全準拠する。

- F4 RAG 評価フェーズ 運用ルール v0.1.1
- F4_results_template_v0.1.md
- RAG 評価基準 v0.1

---

## 9. Non-Goals（v0.1.1）

以下は **意図的に行わない**。

- CLI option の自動追加
- profile 切替の自動化
- ナレッジ管理の自動化
- CI 統合

---

## 10. Summary

- profile は **必須メタデータ**
- 取得経路は pytest 実行層の責務
- writer は **確定値のみを扱う**
- v0.1.1 は v0.1 の設計思想を一切変更しない

---
(End of Document)
