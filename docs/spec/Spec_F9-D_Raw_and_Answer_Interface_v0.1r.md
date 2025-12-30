---
doc_type: spec
project: gov-llm-e2e-testkit
phase: F9-D
title: Raw and answer.md Interface Specification
version: v0.1r
status: draft
date: 2025-12-30
related_phase:
  - F9-C
  - F9-D
  - F4
related_docs:
  - Spec_F9-C_DOM_Scope_Rules_v0.2.md
  - Schema_dataset_v0.2.md
  - PROJECT_STATUS.md
  - Roadmap.md
non_goals:
  - 回答内容の評価・品質判断
  - HTML / Markdown の優劣判断
  - writer / rag_entry の内部実装規定
---

## 1. Purpose（目的）

本仕様は、F9-D において  
**Answer (Raw)** および **answer.md** のインターフェースを最終確定し、  
F4（RAG 入力差分影響の観測・試験データ提供フェーズ）へ  
**評価可能な入力データを、意味を持たせず安定供給する**ための  
**出力条件・構造・運用境界**を定義する。

---

## 2. Scope（対象範囲）

### 2.1 対象

- Answer (Raw)
- Answer (Extracted)
- answer.md（frontmatter + body）
- UI ノイズ混入に関する扱い
- debug profile を主用途とした Raw 出力運用

### 2.2 非対象（明示的 Non-Goals）

- 回答内容の正誤・品質・有用性の判断
- Raw / Extracted の意味的解釈
- writer / rag_entry / dataset の内部処理変更

---

## 3. Definitions（用語定義）

### 3.1 Answer (Extracted)

- **評価入力の正本**
- UI 上で「回答として提示された DOM スコープ」から抽出された  
  **HTML 非変換テキスト**
- VALID / INVALID の状態を必ず持つ

### 3.2 Answer (Raw)

- **補助成果物（デバッグ・再現確認用途）**
- Answer (Extracted) と **同一の起点 DOM スコープ**から取得される
- HTML → Markdown 等の **意味的変換を一切行わない**
- DOM に存在した構造・タグ・順序を保持したまま保存する

---

## 4. DOM Scope Rules（前提）

- Raw / Extracted は **同一の起点 DOM スコープ**を共有する
- 起点 DOM スコープは  
  `Spec_F9-C_DOM_Scope_Rules_v0.2.md` を唯一の正本とする
- 起点 DOM 外の情報は **仕様違反**とみなす

---

## 5. Raw Output Rules（Backlog D）

### 5.1 出力条件

|Extracted 状態|Raw 出力|
|------------|------|
|VALID|省略可能|
|INVALID|必須|

- VALID 時に Raw を出力するか否かは **運用判断**とする
- INVALID 時に Raw が存在しない場合は **仕様違反**

### 5.2 位置づけ

- Raw は以下の用途に限定される：
  - DOM 抽出失敗時の原因分析
  - UI 変更時の再現確認
  - デバッグ証跡
- **評価・比較・スコアリング用途では使用しない**

---

## 6. UI Noise Handling（Backlog E）

### 6.1 UI ノイズの定義

以下は **回答とは無関係な UI 補助要素**と定義する：

- サイドバー
- 操作説明文
- ナビゲーション要素
- フィードバック UI（👍👎 等）
- システムメッセージ（警告・案内）

### 6.2 仕様上の扱い

- UI ノイズが Extracted に混入した場合：
  - **Extracted = INVALID**
  - Raw を必ず出力する
- UI ノイズ混入は「品質劣化」ではなく
  **DOM 抽出仕様違反**として扱う

---

## 7. answer.md Interface Specification（Backlog F）

### 7.1 構造（固定）

```markdown
---
# frontmatter（必須）
---

# Answer (Extracted)
<text or empty>

# Answer (Raw)   # optional
<html>

# Metadata
- status: VALID | INVALID
- reason: <code>
- extracted_len: <int>
- raw_len: <int | null>
- dom_anchor: <string>
```

### 7.2 必須セクション

- frontmatter
- Answer (Extracted)
- Metadata

### 7.3 任意セクション

- Answer (Raw)

  - INVALID 時：必須
  - VALID 時：省略可

---

## 8. Frontmatter Requirements

### 8.1 必須項目（抽象定義）

answer.md の frontmatter には、以下の **論理情報**を必ず含める：

- **case 識別子**
- **question 識別子**
- **生成時刻**
- **バージョン識別子**

※ 具体的なキー名は、
writer / F4 I/F 仕様で別途確定する。

### 8.2 欠落時の扱い

- 必須情報が欠落している answer.md は
  **仕様違反（評価投入不可）**とする

---

## 9. Debug Profile Limited Operation

- Raw の**常時出力**は  
  **debug profile を主用途**とする
- 通常 profile では：
  - VALID → Raw 省略可
  - INVALID → Raw 必須
- profile は  
  **実行文脈識別用メタデータ**としてのみ扱う

---

## 10. Metadata Semantics

- `Metadata.reason` は  
  **状態分類を示す短いコード**とする
- 自由記述・意味的説明は禁止する
- 具体的なコード体系は  
  **本仕様では定義しない**

---

## 11. Downstream Responsibility Boundary

- 本仕様で定義された answer.md は：
  - writer
  - rag_entry
  - dataset
    に対して **意味を持たない入力**
- 下流は以下を行ってはならない：
  - 内容の解釈
  - 補完
  - 正規化
  - 評価

---

## 12. Completion Criteria（完了条件）

本仕様が FIX した時点で：

- Backlog D / E / F は **完了**
- F9-D は **完全クローズ**
- F4 は **本仕様に準拠した入力のみを前提**として進行可能

---

## 13. Notes

- 本仕様 v0.1r は
  **v0.1 の合意逸脱を是正する改訂版**である
- 新規仕様追加・I/F 拡張を行う場合は
  **v0.2 として別途定義する**

---
