---
doc_type: spec
project: gov-llm-e2e-testkit
phase: F9-C
title: Extracted Canonical Specification
status: active
version: v0.1
date: 2025-12-28
related_docs:
  - docs/spec/Done_F9-C_Extracted.md
  - PROJECT_STATUS.md
notes:
  - This spec defines canonical rules only.
  - Evaluation, scoring, and quality judgment are explicitly out of scope.
---

# Spec_F9-C_Extracted_Canonical

## 1. Purpose

本仕様書は、F9-C（Extracted 正本化）において  
**Extracted を評価入力の唯一の正本として成立させるための規約**を定義する。

本仕様は以下を目的とする。

- 評価フェーズが **Extracted 単体で機械的に可否判断**できる状態を作る
- DOM 実装・Raw データへの依存を遮断する
- F8 成果物を **後続フェーズへ安定的に引き渡せる入力仕様**として固定する

---

## 2. Scope / Non-Goals

### 2.1 In Scope

- Extracted の状態モデル定義
- Extracted を評価入力の正本とする規約
- 評価フェーズとの責務境界
- 必須 Metadata の定義
- DOM 抽出ルールの仕様化

### 2.2 Out of Scope（本仕様では扱わない）

- 回答内容の評価・採点・品質判断
- DOM 抽出アルゴリズムの最適化
- 書式品質の優劣判断
- CI・自動合否判定
- Raw データの評価利用

---

## 3. Extracted Status Model（C-3）

### 3.1 Status Definition

Extracted は、以下いずれかの状態を取る。

| Status | Definition |
| ------ | ---------- |
| VALID | DOM 抽出ルールに基づき、評価入力として使用可能な Extracted テキストが **1件確定**している状態 |
| INVALID | DOM 抽出ルールに基づく Extracted テキストが **確定できない状態** |

- 状態は **必ず二値（VALID / INVALID）**
- 中間状態・推定状態は持たない

---

### 3.2 VALID Conditions

以下すべてを満たす場合、Extracted は VALID とする。

1. 抽出ルールに合致する候補が 1 件以上存在すること
2. 抽出ルールに基づき 1 件が選択確定していること
3. 選択された Extracted テキストが空でないこと

※ 書式保持の成否は VALID / INVALID 判定条件に含めない

---

### 3.3 INVALID Representative Cases（非網羅）

- 抽出対象が存在しない
- 抽出対象は存在するが選択ルールを満たさない
- 選択された Extracted が空文字
- DOM 抽出処理が実行不能

これらは分類例であり、是正・再試行・評価を指示するものではない。

---

## 4. Canonical Rule（C-1）

### 4.1 Canonical Definition

> **評価フェーズにおける入力の正本は、  
> `extracted_status: VALID` と判定された Extracted のみである。**

VALID 以外の Extracted は、  
いかなる場合も評価入力の正本とはみなさない。

---

### 4.2 Excluded from Canonical Input

以下は評価入力の正本から明示的に除外される。

- `extracted_status: INVALID` の Extracted
- `extracted_status` が欠落している answer.md
- Raw（UI DOM 抽出全文）
- DOM 抽出観測情報（dom_*）

Raw および DOM 観測情報は、  
**デバッグ・検証用途の補助成果物**に限定される。

---

### 4.3 Evaluation Phase Constraints

評価フェーズは以下を厳守しなければならない。

- Extracted の VALID / INVALID を再判定してはならない
- Raw を参照してはならない
- DOM 抽出ロジックを前提にしてはならない
- `extracted_status` 以外の情報で評価可否を判断してはならない

---

## 5. Metadata Requirements（C-4）

### 5.1 Mandatory Metadata

answer.md の Metadata には、以下を必須とする。

```text
- extracted_status: VALID | INVALID
```

この項目は評価フェーズにおける **唯一の判定根拠**である。

---

### 5.2 Observed Metadata

以下は観測情報として記録されるが、
評価フェーズでは使用してはならない。

- dom_selected
- dom_reason
- dom_text_len

これらは将来変更・削除されうる。

---

### 5.3 Backward Compatibility Rule

- `extracted_status` が存在しない answer.md は  
  **INVALID と同等に扱う**
- 自動補完・推定は禁止

---

## 6. DOM Extraction Rule Specification（C-2）

本節は、Extracted を **原則として取得可能**にするため、  
**回答ブロックの同定 → 抽出対象の限定 → 候補選択 → 確定判定**までを  
文章仕様として定義する。

本仕様は **DOM 構造に基づく機械的処理のみ**を対象とし、
推定・履歴解釈・再評価・意味理解を一切含まない。

---

### 6.0 Parsing Preconditions（前提条件）

本仕様は、HTML 文字列から DOM を構築する際に、
**同一の HTML 入力に対して同一の DOM 構造が得られるパーサ設定**が
実行環境間（runtime / offline 検証）で **固定されていること**を前提とする。

- パーサの具体的実装やライブラリは拘束しない
- ただし、パーサ差異により DOM 構造が変化する場合、  
  当該差異は **仕様外要因**として扱う
- runtime と offline 検証は **同一パーサ条件**で行われなければならない

本前提を満たさない場合、Extracted の成否は保証されない。

---

### 6.1 Answer Block Identification（回答ブロック同定）

DOM 抽出は、**AI の回答本文が表示されている DOM ブロック**のみを対象とする。

以下を満たす要素を **回答ブロック（answer block）** と定義する。

- 要素種別：`div`
- クラス：`message-received`

質問（`message-sent`）および UI ノイズを含む他の要素は、
**回答ブロックに含めてはならない**。

#### 複数回答ブロックが存在する場合

- DOM 上で **最後に出現した `message-received` 要素**を  
  当該質問に対する回答ブロックとして扱う
- この選択に **推定・履歴解釈・再評価**を含めてはならない

`message-received` 要素が 1 件も存在しない場合、
Extracted は確定不能（INVALID）とする。

---

### 6.2 Extraction Target（抽出対象）

抽出対象 DOM は、**6.1 で同定された回答ブロックの内部**に存在し、
以下をすべて満たす要素とする。

- 要素種別：`div`
- クラス：`markdown`
- id 属性：`markdown-N` 形式（N は自然数）

回答ブロック外の `markdown` 要素、
または条件を満たさない要素は **抽出対象外**とする。

---

### 6.3 Candidate Enumeration（候補列挙）

1. 回答ブロック内の抽出対象 DOM をすべて列挙する
2. 各要素について以下を取得する

   - N（`markdown-N` の数値）
   - 要素内テキスト（空文字を含む）

列挙結果が 0 件の場合、  
Extracted は確定不能（INVALID）とする。

---

### 6.4 Candidate Selection Rule（even-max）

複数候補が存在する場合、以下の手順で 1 件を選択する。

1. N の値で降順に並べ替える
2. N が偶数である候補を上位から探索する
3. 最初に見つかった候補を選択候補とする

- 最大 N が偶数の場合：**even-max**
- 最大 N が奇数の場合：**fallback-to-even**

偶数 N が存在しない場合、
選択不能とする。

---

### 6.5 Extracted Finalization（確定条件）

以下を **すべて満たす場合**に Extracted を確定する。

- 回答ブロックが同定されていること
- 選択ルールにより **1 件が一意に選択**されていること
- 選択された候補のテキストが **空でないこと**

いずれかを満たさない場合、
Extracted は確定不能（INVALID）とする。

---

### 6.6 Handling of Extraction Failure（失敗時の扱い）

Extracted を確定できなかった場合：

- `extracted_status` は **INVALID** とする
- 抽出不能の理由は **観測情報として記録してよい**
- 再試行・代替抽出・推定・補完は **禁止**する

INVALID は「失敗」や「品質不良」を意味せず、
**本仕様に基づき確定できなかったという事実表明**のみを表す。

---

## 7. Formatting Preservation Policy（C-5）

### 7.1 Purpose

本節は、Extracted を **評価入力としての正本性を損なわずに取得する**ため、  
DOM 抽出時の **書式保持方針および改変禁止原則**を定義する。

- 表示品質の最適化は目的としない
- 評価内容の良否判断は行わない
- DOM 実装詳細（API・ライブラリ）を拘束しない

本方針の主目的は、  
**UI 上で AI が確定的に表示したテキスト表現を、非改変で取得すること**にある。

---

### 7.2 Preservation Scope（保持対象）

Extracted において、**保持しなければならない書式要素**は以下に限定する。

- 改行構造（段落境界）
- 箇条書き構造（順序・非順序の区別および階層）
- インライン強調（太字・斜体相当）

これらは **AI が出力した論理構造の忠実な保持**を目的とする。  
取得時の都合による省略・簡略化・再解釈は許容しない。

---

### 7.3 Non-Preserved Elements（非保持対象）

以下は保持対象外とする。

- 色・フォントサイズ・装飾スタイル
- レイアウト（段組・余白・位置）
- UI 固有の装飾（アイコン・ボタン等）
- JavaScript 依存の動的要素

これらが保持されないことは  
**仕様違反ではなく仕様どおりの挙動**とする。

---

### 7.4 Extraction-Time Formatting Rule（Normative）

DOM 抽出時、Extracted テキストは以下の原則に **必ず従って生成**されなければならない。

1. DOM 上で AI の回答として確定表示された論理ブロック境界を  
   **改行構造として忠実に反映**すること
2. 箇条書き要素は、  
   **順序・非順序および階層構造を保持したまま取得**すること
3. インライン強調は、  
   **UI 上で表示された意味構造を損なわない形で保持**すること

> 取得過程において  
> 空白正規化・改行削除・統合・再構成等の  
> **表現上または構造上の改変を行ってはならない**。

---

### 7.5 Re-Execution Stability Requirement（重要）

同一 DOM 構造に対して DOM 抽出を再実行した場合：

- Extracted の **論理構造（段落数・箇条書き階層数）は一致**しなければならない
- 文字列の完全一致は要求しない
- 構造差分が発生する場合、その原因は **DOM 構造差分に限定**される

---

### 7.6 Relation to VALID / INVALID

書式保持と状態判定の関係は、以下のとおりとする。

- **AI が出力したテキスト表現を非改変で取得できない場合**、  
  当該 Extracted を **VALID としてはならない**
- 書式保持が不完全であっても、  
  それが **AI 出力の改変に該当しない**ことが明確な場合に限り VALID としてよい

VALID / INVALID 判定は
**C-3 の状態モデルを唯一の基準**とする。

---

### 7.7 Responsibility Boundary（C-2 との責務分離）

- 本節（C-5）は  
  **確定した DOM 要素をどのように非改変でテキスト化するか**を定義する
- 抽出対象 DOM の選択および候補決定は  
  **C-2（DOM Extraction Rule）の責務**とする

両者の責務は相互に侵食してはならない。

---

### 7.8 Implementation Freedom（非拘束事項）

本方針は以下を拘束しない。

- DOM パーサの選定
- HTML → テキスト変換手法
- Markdown 記法の具体形式
- 内部表現および処理アルゴリズム

ただし、**非改変取得という要件を満たす限りにおいて**  
これらは実装裁量とする。

---

### 7.9 Explicit Non-Goals

本節では以下を扱わない。

- 書式の美しさ・読みやすさ評価
- 表・コードブロックの完全再現
- HTML / Markdown の優劣比較
- UI 表示との完全一致保証

---

## 8. Done Alignment

本仕様書により、以下は仕様レベルで完了とみなす。

- C-1：Extracted 正本宣言
- C-2：DOM 抽出ルール仕様化
- C-3：状態モデル定義
- C-4：Metadata 正式化
- **C-5：書式保持方針**

👉 F9-C Backlog C（5項目）はすべて「仕様レベルで完了」

---
