---
title: "Decision Record: F10-A における SubmitConfirmationError 非 fatal 化"
id: decision_record_f10a_submit_non_fatal
version: v0.1
status: accepted
decided_at: 2026-01-12
scope:
  - F10-A
related_phases:
  - F8
  - F10-A
related_files:
  - src/execution/f8_orchestrator.py
  - src/execution/run_single_question.py
  - scripts/run_question_set.py
supersedes: []
---

## Decision

F10-A モードにおいては、`SubmitConfirmationError`  
（submit acknowledgment が観測されない、`ui_ack=false` を含む）を  
**fatal error として扱わない**。

該当ケースは **UNGENERATED** として記録し、  
**run は継続する**。

---

## Context / Background

F10-A は「評価用成果物生成フェーズ」であり、  
目的は **評価判断を含まない入力データ（answer.md）を最大限回収すること**にある。

このフェーズでは以下を前提としている：

- pytest は契約保証用途に限定され、意味評価は行わない
- UI / LLM 側の一時的・確率的失敗は想定内である
- 成否そのものよりも「事実として何が起きたか」を記録することが重要である

実行ログおよび submit_diagnostics.json から、  
以下の事象が確認された：

- 質問文は正常に投入されている
- submit ボタンは gray（生成中）状態のまま遷移せず、blue にならない
- submit acknowledgment（ui_ack）が観測されない
- その結果 `SubmitConfirmationError` が送出され、run 全体が中断される

この挙動は **UI / LLM 側の遅延・スタックに起因する可能性が高く**、  
F10-A の目的（素材生成）と fatal 扱いは整合しない。

---

## Decision Rationale

以下の理由により、`SubmitConfirmationError` を F10-A では fatal としない判断を行った：

1. **F10-A は評価フェーズではない**
   - 失敗を「評価」する工程ではなく、事実を「収集」する工程である

2. **ui_ack=false は観測結果であり、異常終了ではない**
   - submit_diagnostics により、失敗理由は既に記録可能となっている

3. **fatal 扱いは成果物回収率を不必要に下げる**
   - 単一質問の失敗が run 全体の中断につながるのは不合理である

4. **評価フェーズ（F10-B 以降）での扱いは分離可能**
   - F10-B 以降では、UNGENERATED を評価対象から除外すればよい

---

## Decision Details / What Will Be Done

F10-A モードでは、以下の処理を行う：

- `SubmitConfirmationError` 発生時：
  - 該当質問のステータスを `UNGENERATED` とする
  - `execution_context.json` に失敗理由を記録する
  - run は継続する

- fatal error として扱うのは以下に限定する：
  - Playwright のプロセスクラッシュ
  - ブラウザ / context の強制終了
  - スクリプト自身の例外（未捕捉例外）

---

## Out of Scope

本 Decision Record は以下を対象外とする：

- submit acknowledgment 失敗の根本原因分析
- UI 側の改善・retry ロジック追加
- 評価ロジック（F10-B 以降）での扱い

---

## Post-Change Observation Plan

本修正適用後、以下を記録する：

- 修正後 run の結果
  - [ ] 完走できた
  - [ ] 依然として途中で停止した
  - [ ] 挙動が悪化した（早期停止・質問投入不可 等）

- UNGENERATED の発生件数と分布
- 以前 fatal で止まっていた質問（例：Q15）が  
  UNGENERATED として記録され、run が継続したか

これらは **本 Decision Record への追記**、  
または後続の Decision Record で補足する。

---

## Status

- 本判断は **確定（accepted）**
- F10-A 実装および成果物生成は、本判断を前提として進行する
