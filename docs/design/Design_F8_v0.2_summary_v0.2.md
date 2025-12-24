---
doc_type: design_summary
phase: F8
title: F8 v0.2 設計合意サマリー
version: v0.2
status: discussion_fixed
date: 2025-12-24
based_on:
  - F8 v0.1r 引継ぎ資料
  - Design_F8_AutoQuestion_Execution_v0.1
  - Roadmap v1.4
scope:
  - runner / orchestrator design
  - failure handling policy
  - artifact completeness policy
notes:
  - This document fixes design agreements only.
  - No implementation details are included.
  - Evaluation and value judgment are explicitly out of scope.
---

# 📘 F8 v0.2 設計合意サマリー

## 0. 本ドキュメントの目的

本ドキュメントは、  
**F8 v0.1r クローズ後、v0.2 に進むために合意された設計事項**をまとめたものである。

- 既に確定している事項を再議論しない
- v0.2 における設計スコープと非スコープを明確にする
- 次フェーズ（実装・詳細設計）への引継ぎ資料とする

---

## 1. 前提（再確認・再議論不可）

以下は **v0.1r において正式に FIX された前提**であり、  
v0.2 でも維持される。

### 1.1 v0.1r の完了定義

> 単一質問 I/F（run_single_question）と F8 runner が成立し、  
> UI 操作・通信観測・回答検出・ログ記録が実行でき、  
> 失敗を失敗として検出・記録できる状態に到達したこと。

- 18 問完走は v0.1r の Done 条件ではない
- 途中中断を「正しく検出できた」こと自体が目的

### 1.2 不変の設計資産

以下は **非改変・再利用前提**とする。

- `run_single_question`（単一質問実行 I/F）
- submit / probe / Answer Detection の責務分離
- submit–probe 相関設計
- pytest-facing API 境界
- 成果物インターフェース定義 v0.1r+

---

## 2. F8 v0.2 の目的（再定義）

v0.2 の目的は以下に集約される。

> **すべての条例 × すべての質問を自動で投入し、  
> 成否にかかわらず、  
> 回答または失敗理由を事実ログとして完全に記録すること。**

- 「止まらない」こと自体が目的
- 成功率・品質評価・価値判断は行わない

---

## 3. v0.2 で新たに導入する設計変更点

### 3.1 runner / orchestrator の責務再定義

#### v0.1r
- 例外発生時に break（中断）

#### v0.2（合意）
- **continue-on-error を前提とする**
- 原則として処理は止めない
- 各質問は独立した実行単位として扱う

#### 唯一の停止条件（設計合意）
- browser / context / page が破壊され、  
  **以降の実行が技術的に不可能**と判断された場合のみ停止可

---

### 3.2 Failure Handling の状態化（taxonomy）

v0.1r の「成功／例外（二値）」モデルを廃止し、  
**失敗を状態として分類する。**

#### 最小 failure taxonomy（合意済みのたたき）

- `SUCCESS`
- `NO_ANSWER`
  - probe 事実はあるが UI 最終回答が取得できない
- `TIMEOUT`
- `UI_ERROR`
- `EXEC_ERROR`

補足：
- taxonomy は **記録用ラベル**
- 制御分岐・評価・優劣判断には使用しない
- 新規分類の追加は v0.2 では行わない

---

### 3.3 成果物（ログ）完全性ルール

#### v0.1r
- 成功時のみ Markdown 生成

#### v0.2（合意）
- **全質問について必ず 1 レコードを生成**
- 成功・失敗・未確定を frontmatter で明示
- Raw answer / citations は「取得できた事実のみ」を記録

#### フォーマット方針
- v0.1r+ では Markdown 出力を採用している
- json / jsonl 併設は将来拡張候補（本フェーズでは未決）

---

## 4. v0.2 設計合意の成立条件

以下を満たした時点で  
**F8 v0.2 の設計合意が成立**したとみなす。

- continue-on-error 前提の runner / orchestrator 方針が合意されている
- failure taxonomy の最小集合が合意されている
- 全質問で 1 レコード保証のログ方針が合意されている
- v0.1r 実装を破壊せず再利用することが確認されている

※ 実行完走率・成功率は問わない  
※ Markdown の価値判断は F8 の出口で別途行う

---

## 5. 明示的 Non-Goals（再掲）

v0.2 では以下を **行わない**。

- 回答品質・正確性・優劣の評価
- retry / 並列化 / 最適化
- heuristic / fallback による成功率改善
- CI 統合
- 価値判断の結論提示

---

## 6. 次フェーズへの引継ぎ事項

### 次に扱うべきテーマ（別スレッド）

1. runner / orchestrator の具体 API 設計
2. failure taxonomy を frontmatter にどう表現するか
3. v0.2 runner の最小実装順序

本ドキュメント以降、  
**ここに書かれた事項は再議論しない。**

---

## 7. 1行まとめ

> **F8 v0.2 は  
> 「止まらずに、全件を事実として取り切るための設計合意」を  
> 固定するフェーズである。**
