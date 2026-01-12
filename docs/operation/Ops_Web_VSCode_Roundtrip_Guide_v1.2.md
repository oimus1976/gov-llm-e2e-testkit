---
title: Ops Web ↔ VS Code Roundtrip Guide
version: v1.2
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
  - v1.2: Refine Web↔VS Code roundtrip with conditional review decision flow (formal review introduced as optional judgment-fixation step)
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

## 5. Web版 ↔ VS Code 往復フロー（変更あり）

### はじめに

本プロジェクトでは、  
`Protocol_Web_VSCode_Roundtrip_v1.1.md` を用いた  
**Web版 ↔ VS Code 間の厳密な往復運用**を行う。

以下は、**Protocol を確実に発火させるための最小実務手順**である。

### 5.1 基本フロー（変更なし）

```text
Web版（実装ブリーフ）
↓
VS Code（作業・レビュー）
↓
VS Code 作業要約
↓
Web版（/critic・裁定）
↓
PROJECT_STATUS / CHANGELOG（公式宣言）
```

#### 5.1.1 VS Code 側：初期拘束宣言

VS Code（Codex）で作業を開始する際、  
**最初の入力として必ず以下のみを貼り付ける**。

```text
You must follow Protocol_Web_VSCode_Roundtrip_v1.1.md strictly.
Do not summarize, do not explain, do not propose alternatives.
Wait for an IMPLEMENTATION_BRIEF.
```

- この宣言は **Protocol を正本として拘束するための前提操作**である
- これを省略した場合、Protocol が正しく適用されないことがある

---

#### 5.1.2 Web版：IMPLEMENTATION_BRIEF の生成

Web版では、Protocol で定義された
`[IMPLEMENTATION_BRIEF]` セクション **のみ**を生成する。

- 前置き・説明・相談文は一切付与しない
- フォーマットは Protocol 定義を厳密に守る
- 生成した内容は **そのまま VS Code に貼り付ける**

---

#### 5.1.3 VS Code 側：Phase2 / Phase3 の実行

VS Code（Codex）は、貼り付けられた
`[IMPLEMENTATION_BRIEF]` を検知次第、以下を行う。

- Phase2（作業・pytest 実行可否判断）を実施
- pytest 実行可能な場合は実行
- 実行不可な場合はその理由を明示し、人間に実行を依頼
- **必ず Phase3（`[VSCODE_WORK_SUMMARY]`）形式で出力する**

説明文や提案文を付与してはならない。

---

#### 5.1.4 Web版：裁定フェーズ

Web版では、VS Code から返却された
`[VSCODE_WORK_SUMMARY]` を受け取り、

- `/critic` による事実・判断の精査
- `[WEB_DECISION]` の発行
- PROJECT_STATUS / CHANGELOG 反映要否の判断

を行う。

---

#### 5.1.5 Protocol 逸脱時の即時是正

以下のような挙動が見られた場合、**即時是正を行う**。

- Phase3 が出力されない
- pytest 実行が無視される
- 説明・提案が混入する

是正時は、Protocol を再提示し、
`IMPLEMENTATION_BRIEF` からやり直す。

---

#### 5.1.6 補足

- 本手順は **人間向け運用ノウハウ**であり、
  Protocol 本文を置き換えるものではない
- 厳密な入出力形式・完了条件は
  `Protocol_Web_VSCode_Roundtrip_v1.1.md` を正とする

---

### 5.2 作業要約の位置づけ（変更なし）

* VS Code 作業要約は：

  * 実装結果の**事実記録**
  * pytest 実行状況の**一次情報**
* 作業要約自体は：

  * 判断結果ではない
  * 設計固定を意味しない

---

### 5.3 Review 要否判断フェーズ（新設）

本プロジェクトでは、
**すべての変更について Formal Review を起こすわけではない**。

VS Code 作業要約を受け取った Web版（裁定者）は、
次の判断を行う。

```text
この変更について、
判断を文書として固定する必要があるか？
```

#### 5.3.1 判断のトリガ条件（例）

以下のいずれかに該当する場合、
**Review 要否判断フェーズに入る**。

* 設計・Protocol・運用ルールの解釈が関わる
* Codex の判断を Web が採用／却下する必要がある
* pytest が通った理由を言語化しないと不安が残る
* UI 状態遷移・timeout・retry 等を含む
* 「今後もこの挙動を正とするか」を問われうる

※ 判断に迷う場合は、**Review を起こす側に倒す**

---

#### 5.3.2 判断材料の生成（条件付き）

Web版が必要と判断した場合、
VS Code（Codex）に対して **判断材料の生成**を指示する。

* 生成物：

  * `REVIEW_CANDIDATE_MATERIAL`
* 性質：

  * 事実のみ
  * 判断・推奨を含まない
  * Git には保存しない

この判断材料をもとに、
Web版は次の裁定を行う。

* Review を起こす
* Review を起こさず、通常フローに戻る

---

### 5.4 Formal Review フロー（条件付き・新設）

Review を起こすと裁定された場合、
以下のフローを実行する。

```text
Review 起こす（Web 裁定）
↓
Review テンプレートから文書生成（Codex）
↓
判断・裁定の記入（Web）
↓
Git 管理（docs/reviews）
```

#### 5.4.1 Review 文書の位置づけ

* Review 文書は：

  * 実装結果の正誤を保証しない
  * **判断と根拠を固定するための成果物**
* チャットログは Review 文書の代替にはならない

---

#### 5.4.2 Review を起こさない場合

Review を起こさないと判断した場合でも、
Web版は以下を意識する。

* なぜ起こさなかったかを説明できる状態であること
* 暗黙の設計固定が発生していないこと

※ Review を起こさなかった判断自体は
　Git 成果物として残さなくてよい

---

### 5.5 pytest 実行・裁定との関係（既存章への接続）

* Review 要否判断や Formal Review の有無に関わらず：

  * pytest 実行は必須
* pytest 実行結果は：

  * 事実として記録する
  * Web 裁定の判断材料の一部として扱う

Review は pytest の代替ではない。
**Review と pytest は独立した役割を持つ。**

---

## 第5章の全体像（v1.2）

```text
実装ブリーフ
↓
VS Code 実装
↓
作業要約
↓
【Review 要否判断】
├─ No → pytest → Web 裁定 → 公式化
└─ Yes
    ├─ 判断材料生成
    ├─ Review 起こす？
    │   ├─ No → pytest → 裁定 → 公式化
    │   └─ Yes → Formal Review → pytest → 裁定 → 公式化
```

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
