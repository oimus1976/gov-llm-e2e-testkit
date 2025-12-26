---
doc_type: operation
phase: F8
title: F8_Execution_Entry_Points
version: v1.0
status: current
date: 2025-12-26
based_on:
  - Design_F8_v0.3.1_runner.md
notes:
  - 本文書は「削除・改名・再設計」を目的としない
  - 現時点の実行系を人間が迷わず把握するためのマップである
---

# F8 実行系マップ（Execution Entry Points）

本ドキュメントは、F8（回答素材収集フェーズ）における  
**実行系ファイルの役割と入口を整理するための運用向けマップ**である。

コード整理・削除・再設計は目的とせず、  
**「どれが何で、今どれを使うのか」**を明確にすることに主眼を置く。

---

## 1. 全体像

F8 フェーズの実行系は、以下の 3 層で構成されている。

```text
[人間 / CI]
     ↓
[Driver（実行主体）]
     ↓
[Core Orchestrator（制御）]
     ↓
[UI / Probe / Artifact 出力]
````

- **Core**：実行制御ロジック（単独では実行不可）
- **Driver**：人や CI が直接実行する入口
- **Document**：設計・運用上の前提を定義する資料

---

## 2. Core（正式・非実行）

### src/execution/f8_orchestrator.py

**位置づけ**

- F8 フェーズの正式 orchestrator（制御核）
- 単独では実行できない

**責務**

- 条例 × 質問の実行制御
- continue-on-error の保証
- answer.md（正本）の生成制御
- Raw Answer Capture の試行管理
- fatal error 時のみ実行全体を中断

**非責務**

- Browser / Page の生成
- CLI / 引数処理
- pytest / CI 実行

> 本ファイルは「エンジン」に相当し、
> 実行開始の「スイッチ」は別に存在する。

---

## 3. Driver（実行主体）

### scripts/run_f8_set1_manual.py

**位置づけ**

- 手動検証用ドライバ
- 現時点での **推奨実行入口**

**用途**

- Playwright が動作する環境での runtime 検証
- orchestrator の動作確認
- raw / answer.md 成果物の生成確認

**特徴**

- 人が直接実行する前提
- Set1 固定
- 実験・検証用途

---

### src/execution/run_f8_set1.py

**位置づけ**

- 実験的ドライバ（過渡期資産）

**用途**

- 過去の検証・開発用
- 設計 v0.3.1 以前の名残

**注意**

- 正式な実行入口ではない
- 廃止候補だが、現時点では削除しない

---

## 4. 下位 API（実行補助）

### src/execution/run_single_question.py

**位置づけ**

- F8 / F4 共通の下位実行 API

**責務**

- UI submit
- Answer Detection（probe）の呼び出し
- 観測事実の返却

**注意**

- 実行主体ではない
- orchestrator / driver から呼び出される側

---

## 5. 設計・運用ドキュメント

### docs/design/Design_F8_v0.3.1_runner.md

- F8 runner / orchestrator の最新・正式設計
- 実装・運用は本設計に従う

---

### docs/operation/F8-Set-1_Procedure_v1.0.md

- 人間向けの実行手順書
- scripts/run_f8_set1_manual.py と対応

---

## 6. pytest / CI について（現状）

- F8 専用 pytest entry は未整備
- 現時点で F8 は CI 対象外
- 将来フェーズ（F8-B / F8-C）で統合予定

---

## 7. 現時点での整理結果（要点）

- **正式 Core**
  - src/execution/f8_orchestrator.py
- **正式実行入口（暫定）**
  - scripts/run_f8_set1_manual.py
- **過渡期・実験資産**
  - src/execution/run_f8_set1.py

実行系が複数存在するのは過渡期として正常であり、
本ドキュメントは「迷わないための地図」として位置づける。

---

## 8. 今後の整理タイミング

- runtime 検証が完了した後
- F8-B / F8-C の入口が明確になった時点
- 年明け以降を推奨

本ドキュメントは、それまでの暫定マップとして維持する。
