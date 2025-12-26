---
doc_type: design
phase: F8
title: Design_F8_v0.3.2_answer_dom_extraction
version: v0.3.2
status: fixed
date: 2025-12-26
parent:
  - Design_F8_v0.3.1_runner
scope:
  - answer_dom_extraction
notes:
  - This design defines DOM-based answer extraction only.
  - Evaluation, correctness judgment, and quality scoring are out of scope.
---

# 📘 Design_F8_v0.3.2_answer_dom_extraction

## 1. Purpose（目的）

本設計は、F8（Markdown 価値判断フェーズ）において  
**answer.md 正本本文を生成するために、UI DOM から回答本文に該当する
DOM ブロックを best-effort で選択する手順**を定義する。

本設計は **Q01–Q18 のすべてを対象**とし、  
特に Q1 / Q18 における **端点問題（first / last）**を
特例コードなしで吸収することを目的とする。

---

### 非目的（明示）

本設計は以下を **一切行わない**。

- 回答内容の正しさ・品質・妥当性の評価
- 回答生成の成否判断
- UI DOM 構造の契約化
- runner / orchestrator の制御ロジック変更
- retry / 最適化 / 修復処理

---

## 2. Positioning（設計上の位置づけ）

本設計は **runner の外部ロジック**として位置づけられる。

```text
UI DOM
  ↓
[ Answer DOM Extraction ]   ← 本設計の責務
  ↓
answer.md（正本）
```

- Answer Detection（probe）とは独立
- Raw Answer Capture の一部責務
- runner は本設計の成否によって制御分岐を行わない

---

## 3. Design Principles（設計原則）

### 3.1 非評価性（Non-evaluative）

- 本設計における extraction / selection は  
  **評価ではなく技術的選択（selection）**である
- 「最も正しい」ではなく「1つに決める」ことのみを目的とする

### 3.2 UI 非契約前提

- class 名・DOM 構造・描画順序は将来変更される前提とする
- 単一セレクタへの依存は禁止する

### 3.3 端点問題の一般化

- Q1 / Q18 を特例として扱わない
- ルール設計により吸収する

---

## 4. Inputs / Outputs

### 4.1 Inputs

- DOM snapshot（HTML）
- 対象質問 ID（Q01–Q18）
- 質問文原文

### 4.2 Outputs

- 選択された DOM block（0 または 1 件）
- または「選択不能」という結果

※ selection が常に成功することは保証しない

---

## 5. Candidate Enumeration（候補生成）

### 5.1 Primary Path（優先セレクタ）

以下のセレクタに一致する `div` を  
**候補として列挙する**。

```css
div[class~="message"],
div[class~="markdown"]
```

- 本ルールは **最優先**で適用される
- UI 実装依存であり、**長期的成立性は保証されない**
- 候補が 0 件の場合、Fallback Path に進む

---

### 5.2 Fallback Path（汎用 div 走査）

Primary Path で候補が得られなかった場合、  
`main` 配下のすべての `div` を対象に、以下を満たすものを候補とする。

- `textContent` の長さが一定以上（例：200文字以上）
- 当該質問文（またはその一部）を含まない
- 空白・改行・記号のみで構成されていない

---

### 5.3 UI 定型語による粗除外

候補 `div` に以下の **UI 定型語**が過剰に含まれる場合、  
当該 `div` を候補から除外してよい。

例：

- Toggle Sidebar
- コピー / 音声
- AIモデル / Web検索 / ナレッジ
- チャットAI選択 / 国内リージョン

※ 少量の混在は許容し、selection に委ねる

---

### 5.4 禁止事項

- `main` 要素そのものを候補として採用すること
- UI / 履歴 / 回答が混在した巨大ブロックを  
  単一候補として扱うこと

---

## 6. Selection Rules（選択ルール）

候補が存在する場合、以下の優先順位で **1件を選択**する。

### S1. 質問文を含まないものを優先

- 質問文が混在する候補は劣後させる

### S2. UI 定型語の混入が少ないものを優先

- UI 定型語の出現数が少ない候補を優先

### S3. 文字数が多いものを優先

- `textContent` の文字数が最大の候補を優先

### S4. DOM 後方優先（端点補正）

- 上記が同点の場合、  
  DOM index が最大（末尾側）の候補を選択する

#### Selection Safety Check（非評価の安全弁）

selection フェーズでは、技術的選択の安全弁として、
選択された候補の文字数が極端に小さい場合に
「選択不能」と判定してよい。

この判定は、回答内容の正しさ・品質・妥当性を評価するものではなく、
UI 断片や誤検出ブロックを answer.md 正本として
採用しないための最小限の構造チェックである。

---

## 7. Selection 不成立時の扱い（重要）

### 7.1 候補生成結果が 0 件の場合

- selection は実行しない
- answer.md は生成する
- **result_status の値は runner 側の観測事実に従う**
- 本設計では status 値を決定しない

### 7.2 候補は存在するが selection により選択不能の場合

- answer.md は生成する
- 本文は空、または最小 placeholder
- frontmatter に以下を記録する：

```yaml
result_status: NO_ANSWER
result_reason: no suitable dom candidate found
raw_capture: true
```

---

## 8. Q1 / Q18 に対する成立性説明（設計根拠）

本章は、本設計が Q1 / Q18 を含む全質問に対して  
**成立しうる理由を説明するものであり、常に成功することを保証しない**。

- Q1：
  - 初期 UI ノイズが多い
  - S1（質問文除外）および S4（後方優先）により吸収される
- Q18：
  - DOM 肥大によるノイズ増加
  - S2（UI語混入抑制）および S4 により末尾回答を選択可能

---

## 9. Non-Goals（再掲）

- 回答品質・正確性の評価
- retry / 成功率改善
- DOM 修復・再構成
- UI 実装変更提案

---

## 10. Future Extensions（非拘束）

- 抽出メタデータの詳細化
- JSON 併設出力
- UI 変更検知のための観測ログ拡張

---
