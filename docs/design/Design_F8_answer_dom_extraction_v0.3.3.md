---
doc_type: design
phase: F8
title: Design_F8_v0.3.3_answer_dom_extraction
version: v0.3.3
status: draft
date: 2025-12-27
parent:
  - Design_F8_v0.3.1_runner
replaces:
  - Design_F8_v0.3.2_answer_dom_extraction
scope:
  - answer_dom_extraction
notes:
  - This design is grounded in observed Qommons.AI DOM facts (div.markdown + id="markdown-n").
  - Canonical answer text MUST be extracted from answer-only markdown blocks, not from <main>.
  - Raw capture (<main>/<body>) remains as evidence; it is not the canonical answer source.
---

# 📘 Design_F8_v0.3.3_answer_dom_extraction

## 1. Purpose（目的）

本設計は、F8 において **answer.md の正本本文（canonical answer_text）**を生成するために、  
Qommons.AI の UI DOM スナップショット（HTML）から **回答本文のみを含む DOM ブロック**を
**非評価的に 1 件選択**する手順を定義する。

本設計は **Q01–Q18 全問**を対象とし、Q1/Q18 を含む端点問題を **特例コードなし**で吸収する。

---

## 2. Positioning（位置づけ）

```text
UI DOM snapshot (HTML)
  ├─ Raw Capture (evidence): <main> / <body>  …保存のみ（ノイズ混入許容）
  └─ Answer DOM Extraction (canonical): div.markdown[id="markdown-n"] …本設計
        ↓
answer.md 正本本文（Answer (Extracted)）
```

- Answer Detection（probe）とは独立（probe は「完了観測」であり、本文の正本ではない）
- runner/orchestrator は本設計の成否で **制御分岐しない**
- 本設計は **抽出モジュール**（例：`src/execution/answer_dom_extractor.py`）に実装される

---

## 3. Observed DOM Facts（観測事実）

### 3.1 Answer block exists as markdown div

Qommons.AI の UI DOM では、回答本文が **`div.markdown`** として存在することが観測されている。

例（観測例）：

```html
<div id="markdown-2" class="markdown">
  ...回答本文...
</div>
```

### 3.2 markdown id is monotonic and indexable

`div.markdown` の `id` は `markdown-n` 形式であり、`n` は **整数**として解釈可能である。  
同一チャット内で `n` は **単調増加**することが観測されている。

### 3.3 Alternation assumption (question/answer)

同一チャット内で `div.markdown` が増加する際、質問・回答が **交互に並ぶ**挙動が観測されている。  
この交互性を利用し、**回答は偶数 n** として取り扱うルールを採用する（Rule S2）。

> 注：交互性は UI 実装に依存するが、現時点の一次観測では成立している。
> 本設計は v0.3.x の FIX として「観測事実に基づく安定化」を優先する。

---

## 4. Inputs / Outputs

### 4.1 Inputs

- DOM snapshot（HTML, 文字列）
- 質問文（文字列）
- （任意）実行メタ（submit_id/chat_id 等）※抽出判断に使用しない

### 4.2 Outputs

- `selected=True` の場合：
  - 抽出本文（回答本文のみ）…文字列
  - 選択根拠（観測ベースの reason）…文字列
- `selected=False` の場合：
  - 本文なし
  - reason（失敗理由）

---

## 5. Non-goals（非目的：明確化）

本設計は以下を行わない。

- 回答内容の正しさ・品質・妥当性の評価
- retry / 成功率改善 / 復旧処理（送信失敗対応等）
- UI DOM 構造の一般契約化（長期保証）
- `<main>` 全体からの本文抽出（canonical としては禁止）

---

## 6. Candidate Enumeration（候補生成：FIX）

### Rule E1（FIX）: Candidate scope is markdown div only

候補は **`div.markdown`** のみとする。

- `div.message` は対象外（質問/履歴/混在の可能性があるため）
- `<main>` / `<body>` は候補として扱わない（Raw capture 専用）

### Rule E2（FIX）: Candidate must have id="markdown-n"

候補 `div.markdown` は `id` が `markdown-n`（n は整数）に一致するもののみとする。

- 一致しない `div.markdown` がある場合は候補から除外してよい
- 一致する候補が 0 件の場合は `selected=False` とする（reason を記録）

---

## 7. Selection Rules（選択ルール：FIX）

### Rule S1（FIX）: Latest index wins

候補のうち `n` が最大のものを選択する。

- `n` の最大値は「最新に追加された markdown ブロック」と見なす

### Rule S2（FIX）: Answer parity filter (even n)

`n` が最大の候補が **偶数**でない場合、`n` を 1 ずつ減らし、  
最初に見つかる **偶数 n** の候補を選択する。

- 例：最大が `markdown-7` なら `markdown-6` を選択
- 例：最大が `markdown-2` なら `markdown-2` を選択
- 例：偶数が存在しない（0件）なら `selected=False`

> 目的：質問/回答の交互性（観測事実）に基づき「回答ブロック」を定義する。

### Rule S3（FIX）: Text extraction is the div's own text content

選択された `div.markdown` の **テキスト内容のみ**を canonical answer とする。

- UI サイドバー等は別 DOM に存在する（観測）ため、marker 切断等の後処理は原則不要
- ただし **空文字**の場合は `selected=False` としてよい（reason に記録）

---

## 8. Failure Handling（失敗時の扱い）

- `div.markdown[id="markdown-n"]` が 0 件  
  → `selected=False`, reason=`no markdown-n candidates`
- 偶数 n の候補が見つからない  
  → `selected=False`, reason=`no even markdown-n candidates`
- 選択候補のテキストが空  
  → `selected=False`, reason=`selected markdown is empty`

本設計は `result_status` を決めない。  
runner/orchestrator は probe 等の観測事実に基づいて status を記録する。

---

## 9. Q1 / Q18 成立性（観測に基づく説明）

本設計は、Q1/Q18 を特例扱いしない。

- Q1：
  - 初回でも回答は `div.markdown[id="markdown-2"]` のように生成される観測がある
  - Rule S1/S2 により最新回答が取得される
- Q18：
  - DOM が肥大化しても `markdown-n` の単調増加は維持される観測がある
  - Rule S1/S2 により末尾側の最新回答が取得される

---

## 10. Implementation Notes（実装メモ：拘束）

- `BeautifulSoup` 等で `div.markdown` を列挙し、`id` から `n` をパースする
- 正規表現例：`^markdown-(\d+)$`
- 選択結果には `n` を含む reason を残してよい（例：`selected markdown-6 (even-max)`）
- デバッグ用ログは TEMP として明示し、検証完了後に除去する

---

## 11. Compatibility Notes（互換・移行）

- v0.3.2 の “Primary/Fallback + heuristics” は廃止（replaced）
- Raw capture（`raw_answer.html/txt/meta`）は継続し、証拠として保持する
- answer.md には canonical と raw を併記してよい（runner設計に従う）

---
