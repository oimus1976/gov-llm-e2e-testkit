---
title: Ops Web ↔ VS Code Roundtrip Guide
version: v1.1
status: active
category: operations
scope: Qommons.AI Test Automation
owners:
  - human
  - ai-codex
related:
  - Design_Execution_Model_QommonsAI_TestAutomation_v1.1.md
  - PROJECT_GRAND_RULES.md
  - AI_Development_Standard.md
  - PROJECT_STATUS.md
changelog:
  - v1.1: Align with Execution Model v1.1 (pytest mandatory, agent usage clarified)
---

## 1. 本ガイドの位置づけ

本ドキュメントは、  
**Qommons.AI テスト自動化プロジェクトにおける日常作業の往復運用  
（Web版 ChatGPT ↔ VS Code / Codex）を定義する運用ガイド**である。

- 本ガイドは **設計思想や責務境界を再定義しない**
- 上位文書である  
  `Design_Execution_Model_QommonsAI_TestAutomation_v1.1.md`  
  を前提に、「どう回すか」だけを規定する
- 判断の正否は **Web版で裁定される**

---

## 2. 上位・下位ドキュメントとの関係

本ガイドは、  
`Design_Execution_Model_QommonsAI_TestAutomation_v1.1.md`  
で定義された実行モデルを前提とした  
**人間向け運用手順書**である。

AI（ChatGPT / Codex）との実際のやり取りで使用する  
厳密な入出力形式・順序・完了条件については、  
`Protocol_Web_VSCode_Roundtrip_v1.1.md` を正とする。

---

## 3. 基本原則（運用レベル）

1. 推測で判断しない  
2. 一次情報（コード・ログ・実行結果）を優先する  
3. チャットログは資産ではない  
4. 残すのは「事実・判断・保留」だけ  
5. **pytest の実行は必須**（実行主体は状況で分かれる）

---

## 4. 役割分担（運用視点）

### 4.1 Web版 ChatGPT

**役割**

- 司会
- 設計整理
- 裁定（/critic）

**主な作業**

- 実装ブリーフの作成
- VS Code 作業要約の裁定
- PROJECT_STATUS / CHANGELOG 反映判断

**やらないこと**

- 実装
- pytest 実行

---

### 4.2 VS Code（Codex）

#### チャットモード（原則使用）

- 権限：read-only
- 用途：
  - コード読解
  - 最小 diff 案提示
  - 設計逸脱レビュー
  - pytest 実行可否の判定

#### エージェントモード（必要時）

- 権限：write-enabled
- 用途：
  - typo
  - 機械的修正
  - 自明な変更
- ルール：
  - 原則常用しない
  - 使用後は必ずレビューする
  - 「途中で切れる」前提で使う

---

## 5. Web版 ↔ VS Code 往復フロー

```
Web版（実装ブリーフ）
↓
VS Code（作業・レビュー）
↓
VS Code 作業要約
↓
Web版（/critic・裁定）
↓
PROJECT_STATUS / CHANGELOG（公式宣言）
````

---

## 6. Web → VS Code：実装ブリーフ

Web版では、VS Code に渡す **実装ブリーフ**を必ず作成する。

```text
【VS CODE 実装ブリーフ】
1. 目的
2. 確定事項
3. 禁止事項
4. 未確定・判断保留点
5. VS Code への具体指示
   - 対象ファイル
   - チェック観点
   - 判断可／不可の境界
````

※ このブリーフなしで VS Code 作業を開始しない。

---

## 7. VS Code 作業と pytest 実行（重要）

### 7.1 pytest 実行は必須

* 設計レビューや机上確認だけでは不十分
* **実際にコードが完走するかは実行しないと分からない**
* pytest 実行は品質保証として必須

---

### 7.2 実行主体の判断

- Codex が pytest を実行可能な場合  
  → Codex が実行し、結果を報告する
- Codex が pytest を実行不可な場合  
  （Playwright / sandbox 制約など）  
  → **Codex はその事実を明示し、人間に実行を依頼する**

> Codex の責務は  
> 「pytest を実行しない」ことではなく、  
> **「pytest を実行させずに終わらせない」こと**である。

---

## 8. VS Code → Web：作業要約

VS Code 作業後、必ず以下の形式で要約を作成する。

```text
【VS CODE 作業要約】
1. 実施したこと（事実）
2. pytest 実行結果（Codex / 人間）
3. 観測された問題／なかった問題
4. 判断した点（理由）
5. 判断を保留した点
6. Web版で裁定してほしい論点
```

---

## 9. 作業要約の資産化

- チャット全文は保存しない
- 保存対象：VS CODE 作業要約のみ
- 保存先：
  ```text
  docs/vscode_logs/YYYY-MM-DD_<context>.md
  ```

保存後は必ず：

- git add
- git commit
- git push
- PROJECT_STATUS / CHANGELOG 反映要否確認

---

## 10. Markdown 保存の実務ルール

- Codex UI から Markdown を直接エクスポートできない
- UI ログを資産にしようとしない
- 必要な場合は：
  - BEGIN / END マーカー方式
  - AI に Markdown を再生成させる

---

## 11. /critic の使いどころ

- 使用場所：Web版のみ
- 対象：
  - 事実誤認
  - 推測混入
  - 過剰修正
  - 設計逸脱
  - 判断根拠不備
- 対象外：
  - 人格
  - 文体

---

## 12. unit / basic / e2e との関係

- 本ガイドの往復運用は **unit / basic を主対象**
- e2e（Playwright）は：
  - 人間実行フェーズで実施
  - 結果を Web版裁定に合流させる

---

## 13. 本ガイドの更新ルール

- 本ガイドの現行版は **v1.1**
- 上位 Design 文書が更新された場合、追従更新する
- 実務で破綻が確認された場合のみ改訂する


---
