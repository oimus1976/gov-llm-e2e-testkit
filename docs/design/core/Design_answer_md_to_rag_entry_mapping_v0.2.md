---
title: Design: answer.md ↔ rag_entry Mapping
project: gov-llm-e2e-testkit
phase: F9-D
status: FIX
version: v0.2
date: 2025-12-29
owner: Sumio Nishioka
related:
  - Responsibility_Map_v0.2
  - Schema_rag_entry_v0.2
  - Spec_F9-C_DOM_Scope_Rules_v0.2
---

# 📘 Design: answer.md ↔ rag_entry Mapping v0.2

## 0. 本ドキュメントの目的（拘束）

本書は、**物理成果物である `answer.md` と、論理データ単位である `rag_entry` の対応関係**を定義する。  
本書は **変換・解釈・補完の自由を与えるものではなく**、  
下流フェーズが **機械的に同一の rag_entry を再構成できること**を目的とする。

- 本書は **F9-C（Extracted 正本化）完了を前提**とする
- 本書は **Schema_rag_entry_v0.2** を補助する設計文書である
- 本書に反する読み取り・補完・再解釈は **設計違反**とみなす

---

## 1. 基本原則（重要）

1. **answer.md は物理成果物、rag_entry は論理データ単位である**
2. **answer.md 1 ファイルは rag_entry 1 件に対応する**
3. 対応は **決定的（deterministic）**でなければならない
4. 対応過程で **意味解釈・評価・補完を行ってはならない**

---

## 2. 全体対応図

```text
answer.md（1ファイル）
├─ frontmatter
├─ ## Question（任意）
├─ ## Answer (Extracted)
├─ ## Answer (Raw)
└─ ## Metadata
↓（機械的対応）
rag_entry（1件）
```

---

## 3. frontmatter の対応

### answer.md（例）

```yaml
---
question_id: Q12
profile: INTERNET
run_id: run-001
timestamp: 2025-12-29T10:30:12+09:00
---
```

### rag_entry への対応

```yaml
rag_entry:
  question:
    question_id: Q12
  execution:
    profile: INTERNET
    run_id: run-001
    timestamp: 2025-12-29T10:30:12+09:00
```

### 対応ルール

| answer.md (frontmatter) | rag_entry            | 必須 |
| ----------------------- | -------------------- | ---- |
| question_id             | question.question_id | ✔    |
| profile                 | execution.profile    | ✔    |
| run_id                  | execution.run_id     | ✔    |
| timestamp               | execution.timestamp  | ✔    |

#### 注意（拘束）

- frontmatter に存在しない項目を **推測・生成してはならない**
- env.yaml / test_plan との整合確認は **本対応の責務外**

---

## 4. Question セクションの対応（任意）

### answer.md（存在する場合）

```markdown
## Question

〇〇条例第5条について説明してください。
```

### rag_entry への対応

```yaml
rag_entry:
  question:
    text: "〇〇条例第5条について説明してください。"
```

### ルール（重要）

- `question.text` は **実行時に UI に送信された文字列そのもの**
- 質問文の生成元は問わない
  （テストコード直書き／外部ファイル読み込み いずれも可）
- `## Question` が存在しない場合：

  - `question.text` は **null / 欠落**として扱う
- writer / dataset は：

  - 質問文を **生成・補完・正規化してはならない**

👉 **将来の外部ファイル化を妨げないための設計余地**

---

## 5. Answer (Extracted) の対応（必須）

### answer.md

```markdown
## Answer (Extracted)

<div class="markdown">
  <p>〇〇条例第5条では…</p>
</div>
```

### rag_entry への対応

```yaml
rag_entry:
  answer:
    extracted: |
      <div class="markdown">
        <p>〇〇条例第5条では…</p>
      </div>
```

### ルール（拘束）

- **HTML 非変換**
- DOM 構造・タグ・順序を保持
- Markdown / text への変換は禁止

---

## 6. Answer (Raw) の対応（条件付き）

### answer.md (INVALID ステータス時)

```markdown
## Answer (Raw)

<div id="message-item-14">
  ...
</div>
```

### rag_entry への対応

```yaml
rag_entry:
  answer:
    raw: |
      <div id="message-item-14">
        ...
      </div>
```

### ルール

| 条件                        | raw            |
| --------------------------- | -------------- |
| metadata.status = VALID     | 省略可 / null  |
| metadata.status = INVALID   | **必須**       |

- Raw は **同一 Anchor DOM 起点**
- デバッグ・再現確認専用
- 評価用途に使用してはならない

---

## 7. Metadata の対応（必須）

### answer.md (Metadata セクション例)

```markdown
## Metadata

- status: INVALID
- reason: anchor_dom_not_found
```

### rag_entry への対応

```yaml
rag_entry:
  metadata:
    status: INVALID
    reason: anchor_dom_not_found
```

### 対応ルール（拘束）

- status は **Answer Extraction Layer が確定**
- writer / dataset は **再判定・上書き禁止**
- reason は **機械的識別子のみ**（自由記述禁止）

---

## 8. 対応一覧（総表）

|answer.md セクション|rag_entry フィールド|必須|
|---|---|---|
|frontmatter.question_id|question.question_id|✔|
|frontmatter.profile|execution.profile|✔|
|frontmatter.run_id|execution.run_id|✔|
|frontmatter.timestamp|execution.timestamp|✔|
|Question（本文）|question.text|任意|
|Answer (Extracted)|answer.extracted|✔|
|Answer (Raw)|answer.raw|条件付き|
|Metadata.status|metadata.status|✔|
|Metadata.reason|metadata.reason|任意|

---

## 9. writer の責務境界（再確認）

- writer は：

  - answer.md を **書き出すだけ**
  - rag_entry を「作ろう」と意識しない
- 本対応は：

  - **読む側の契約**
  - writer を賢くしないための設計

---

## 10. 非対象（明示）

本書では以下を扱わない。

- dataset schema
- entry_id の生成規則
- 質問文の外部ファイル形式・管理方法
- 評価・比較ロジック

---

## 11. 本ドキュメントの役割（再掲）

- answer.md の解釈を **唯一に固定**
- 下流での「勝手な読み替え」を防止
- F9-C の設計成果を **確実に保持**

---
