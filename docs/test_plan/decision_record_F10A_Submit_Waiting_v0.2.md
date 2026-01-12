---
id: DR-F10A-002
date: 2026-01-11
scope: F10-A submit handling
status: implemented
result: completed-run
confidence: medium
related:
  - src/execution/run_single_question.py
  - src/execution/f8_orchestrator.py
---

## Decision

F10-A モードでは submit が blue になるまで無制限に待機し、
submit acknowledgment が得られない場合でも例外で停止せず、
UNGENERATED として記録した上で run を継続する。

非 F10-A モードでは従来どおり timeout を例外とするが、
待機時間は従来の約 2 倍に延長する。

## Background

F10-A 実行において、Q15 以降で submit が gray のまま長時間遷移し、
SubmitConfirmationError により run 全体が中断される事象が発生していた。

この挙動は、ユーザー指示として
「submit が blue になるまで待つ」
「未生成は記録するが run は止めない」
という要件と一致していなかった。

## Action Taken

- run_single_question.py にて F10-A 時は submit 待機を無制限化
- SubmitConfirmationError を F10-A では送出せず ungenerated として扱う
- f8_orchestrator.py で UNGENERATED を明示的に処理

## Outcome

- 修正後の実行にて run は最後まで完走した
- 途中での強制終了・例外停止は発生しなかった

## Remaining Risk

- timeout 発生時に直前の回答 DOM を誤って再利用していないかは未確認
- answer.md 内容の健全性については別途 diff 確認が必要
