---
title: "Design Note: Submit Readiness Fast Path"
version: v0.1
status: deferred
created_at: 2026-01-11
origin_template: DesignNote_TestToMain_Promotion_v0.1
related_phases:
  - F10-A
  - F10-B (candidate)
---

# Design Note (Pre-Design): Submit Readiness Fast Path

## 0. Positioning

本ノートは、  
**過去のテストスクリプトで観測された submit 即時実行の挙動を、  
設計知見として保存するための Pre-Design ノート**である。

本ノートは：

- 実装を変更しない
- 評価・最適化を行わない
- F10-A の成果物仕様に影響しない

---

## 1. Purpose

- submit_probe 系テストで成立していた挙動を事実として記録する
- なぜ即時実行が可能だったのかを構造的に整理する
- main 実装に昇格させる場合の論点を明らかにする

---

## 2. Observation（観測された事実）

- 観測元：
  - テスト種別：submit_probe（Gate1 entry minimal 系）
  - 実行環境：人手実行（ブラウザ UI）
- 観測された挙動：
  - 質問入力欄が有効化された直後に入力が行われていた
  - submit ボタンが gray → blue に遷移した瞬間に submit が実行されていた
  - 固定 sleep による待機はほとんど発生していなかった

---

## 3. Why It Worked（構造的説明）

- submit 可能判定を **UI state（DOM class 遷移）**のみで行っていた
- 完了検知を「時間経過」ではなく「状態遷移」として扱っていた
- テスト前提として：
  - 対象 UI が限定されていた
  - ナレッジ状態が固定されていた
  - 失敗時のリトライ戦略を持たなかった

---

## 4. Gap to Main Execution

- main 実装では：
  - 汎用性確保のため待機条件が多段化している
  - 状態遷移確認に加えて時間ベースの待機が存在する
- 差分の影響：
  - 1 試行あたりの所要時間が増加している

※ 原因の特定・是正は本ノートの対象外

---

## 5. Responsibility Mapping

| 知見 | 想定レイヤ | 理由 |
| ---- | ---- | ---- |
| submit 可能判定 | PageObject | UI state 抽象化の責務 |
| 即時 submit 実行 | orchestrator | 実行フロー制御 |
| retry / timeout | runbook | 運用判断に近い |

---

## 6. Speed Regression Review（観点）

- 既に成立している状態を二重に確認していないか
- 状態遷移を sleep / timeout で代替していないか
- 将来フェーズ向けの安全弁が F10-A に混入していないか

---

## 7. Non-Goals

- 現行コードの修正
- 性能改善の数値評価
- pytest の再設計

---

## 8. Current Decision

- Decision: **Deferred**
- 理由：
  - 現フェーズは F10-A（評価用成果物生成）
  - UX 最適化はフェーズ外

---

## 9. One-Line Summary

> submit_probe テストで成立していた即時 submit の挙動は、  
> 将来フェーズで main 実装に昇格させ得る設計知見として保存する。
