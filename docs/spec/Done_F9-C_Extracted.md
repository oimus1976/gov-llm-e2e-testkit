---
title: "F9-C Done Definition — Extracted 正本化"
doc_type: spec
phase: F9-C
status: active
version: 1.0.0
last_updated: 2025-12-28
scope:
  - extracted_canonicalization
non_goals:
  - answer_evaluation
  - quality_scoring
  - html_markdown_comparison
related:
  - PROJECT_STATUS.md
  - Roadmap.md
---

# F9-C Done Definition — Extracted 正本化

## 目的

本書は、gov-llm-e2e-testkit における  
**F9-C（Extracted 正本化）が「完了した」と判断するための Done 定義**を定める。

本 Done 定義は、

- 実装の合否判定
- Backlog 完了判断
- フェーズ移行判断
- 後続プロジェクトへの引き渡し条件

の **参照正本**として用いられる。

---

## スコープ宣言

本 Done 定義が扱うのは、  
**Extracted が評価入力として単独で使用可能であること**のみである。

以下は対象外とする。

- 回答内容の正誤・品質・妥当性
- LLM 応答の意味理解・網羅性
- HTML / Markdown の優劣判断
- CI 合否・自動評価条件

---

## 正本性（Single Source of Truth）

- Extracted は **評価入力の唯一の正本**である
- 評価フェーズにおいて Raw を参照する必要はない
- answer.md を評価に投入する際、  
  **Extracted セクションのみで完結する**

Raw は **デバッグ用途の補助成果物**としてのみ扱う。

---

## 取得保証（Availability）

- Extracted は **原則として生成される**
- 生成できなかった場合でも、  
  **状態（INVALID）が明示される**
- Extracted が空文字・未定義のまま放置されることはない

※ 実行中断（ABORTED）は F9-C の対象外とする

---

## 構造安定性（Structural Stability）

Extracted は以下を満たす。

- `## Answer (Extracted)` セクションが必ず存在する
- Markdown としてパース可能である
- 改行・箇条書き等の基本構造が保持される
- UI 文言・サイドバー等の補助要素が混入しない  
  （混入した場合は INVALID として扱われる）

表現の正確さ・簡潔さは要求しない。

---

## 状態分類（Explicit State）

Extracted には以下のいずれかの状態が  
**Metadata として必ず付与**される。

| State   | 意味                                   |
| ------- | -------------------------------------- |
| VALID   | 仕様どおり Extracted が取得できている |
| INVALID | 抽出失敗または仕様違反が発生している |

INVALID の場合は、  
原因（例：`ui_noise`, `extraction_error`, `structure_violation` 等）を  
Metadata に記録する。

---

## 再現性（Reproducibility）

- 同一質問・同一条例・同一 profile で再実行した場合、  
  **Extracted の基本構造（見出し・本文区分）が破壊されない**
- 文言の揺れ・表現差分は許容する

---

## 失敗時の扱い

- INVALID の場合でも answer.md 自体は必ず生成される
- INVALID は例外・中断・失敗とは扱わない
- INVALID は評価フェーズで **機械的に除外可能**である

---

## 禁止事項（Guardrails）

以下は一切行わない。

- Raw を用いた補完・修正
- 抽出結果の内容改善・要約・最適化
- 評価基準・スコア・品質判定の導入

---

## Done 判定

以下がすべて満たされている場合、  
**F9-C（Extracted 正本化）は Done と判定する。**

- Extracted が評価入力の正本として明示されている
- Extracted が原則生成され、状態が明示されている
- Markdown 構造が安定している
- UI ノイズ混入が発生しない、または INVALID として分類される
- Raw がデバッグ用途に限定されている

---

## 位置づけ

- 本書は **設計文書**である
- CI 合格条件ではない
- 自動評価の導入を意味しない
