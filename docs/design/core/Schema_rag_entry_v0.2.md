---
title: rag_entry schema v0.2
project: gov-llm-e2e-testkit
phase: F9-D
status: FIX
version: v0.2
previous_version: none (implicit)
date: 2025-12-29
owner: Sumio Nishioka
breaking_change: YES (F9-C 前提)
---

## 0. 本ドキュメントの位置づけ（拘束）

- 本書は **F9-C（Extracted 正本化）完了を前提**とする
- 本書は **rag_entry という論理データ単位の構造・必須性・禁止事項**を定義する
- dataset schema / 運用設計は **本書に従属**する
- 本書に反する下流実装・schema は **設計違反**とみなす

---

## 1. rag_entry の定義（拘束・設計用）

> **rag_entry とは、
> ある質問を、特定の実行条件で 1 回送信した結果として、
> UI 上で実際に観測された回答 DOM とその取得成否を、
> 後続フェーズで比較・検証できる形に構造化した
> 1 件分の論理データ単位である。**

### 拘束点

- rag_entry は **1 回の質問実行につき 1 件**生成される
- 含まれるのは **観測された事実のみ**である
- 回答の正誤・品質・有用性の判断は **一切含まれない**
- 後続フェーズ（F4 以降）は rag_entry を
  **最小の比較・検証単位**として扱う

---

## 2. 補足説明（理解用・非拘束）

### 2.1 「1 回の質問実行」とは

- `ChatPage.send()` を **1 回**呼び出した単位
- 以下を含めて「1 回」と数える
  - 実際に UI に送信した質問文
  - 実行プロファイル（INTERNET / LGWAN 等）
  - 実行時刻

---

### 2.2 「観測された事実」とは

rag_entry に含まれるのは、
**Playwright を通じて UI 上で実際に確認できた事実のみ**。

含まれる例：

- 回答として表示された DOM の存在
- Extracted の取得可否
- 取得結果の状態（VALID / INVALID）

含まれない例：

- 回答内容の正しさ
- 分かりやすさ
- Markdown 変換結果
- 条例解釈の妥当性

---

### 2.3 「評価可能」の意味

本プロジェクトにおける「評価可能」とは、

- 人が良し悪しを判断できる
  ではなく、
- **同一質問を異なる条件で実行した結果を
  機械的に比較・検証できる**

という意味である。

---

## 3. rag_entry の論理構造（v0.2）

```yaml
rag_entry:
  entry_id: string
  question:
    question_id: string
    text: string | null
  execution:
    profile: string
    run_id: string
    timestamp: string
  answer:
    extracted: string
    raw: string | null
  metadata:
    status: VALID | INVALID
    reason: string | null
```

---

## 4. 各フィールド定義（具体）

### 4.1 entry_id

- 型：string
- 内容：
  - rag_entry を dataset 内で一意に識別する ID
- 備考：
  - 生成方法は **dataset / 運用側に委ねる**
  - 本 schema では生成規則を定義しない

---

### 4.2 question

#### question.question_id（必須）

- 型：string
- 内容：
  - 質問定義側で付与された安定 ID
- 特性：
  - 質問文が変わっても **不変**

---

#### question.text（任意）

- 型：string | null
- 内容：
  - **実行時に UI に実際に送信された質問文**
- 重要な設計方針：
  - 質問文の生成元は問わない
    - テストコード内の直書き
    - 外部ファイル（YAML / JSON 等）からの読み込み
  - **rag_entry schema は生成元を規定しない**
- 制約：
  - writer / dataset は
    - question.text を生成・補完・変換してはならない
  - answer.md に存在しない場合は
    - 欠落（null）として扱う

👉 **将来の外部ファイル化を妨げないための準備点**

---

### 4.3 execution

#### execution.profile（必須）

- 型：string
- 内容：
  - env.yaml に定義された実行プロファイル名

#### execution.run_id（必須）

- 型：string
- 内容：
  - 同一質問を複数回実行した場合の区別子

#### execution.timestamp（必須）

- 型：string（ISO 8601）
- 内容：
  - 実行開始時刻

---

### 4.4 answer

#### answer.extracted（必須）

- 型：string
- 内容：
  - Answer Extraction Layer が生成した **Extracted**
- 制約（拘束）：
  - **HTML 非変換**
  - DOM 構造・タグ・順序を保持
- 位置づけ：
  - **評価入力の唯一の正本**

---

#### answer.raw（条件付き必須）

- 型：string | null
- 内容：
  - 同一 Anchor DOM から取得した Raw HTML
- 必須条件：
  - metadata.status == INVALID の場合 **必須**
- 任意条件：
  - metadata.status == VALID の場合 **省略可**
- 位置づけ：
  - デバッグ・再現確認専用

---

### 4.5 metadata

#### metadata.status（必須）

- 型：enum
- 値：
  - VALID
  - INVALID
- 決定権：
  - **Answer Extraction Layer のみ**

---

#### metadata.reason（任意）

- 型：string | null
- 内容：
  - INVALID の理由を **機械的に説明する識別子**
- 例：
  - `anchor_dom_not_found`
  - `extracted_empty`
- 備考：
  - 自由記述は禁止（将来コード化前提）

---

## 5. 必須／任意ルール（一覧）

| 項目 | 必須 | 備考 |
| ---- | ---- | ---- |
| entry_id | 必須 | dataset 内一意 |
| question.question_id | 必須 | 安定 ID |
| question.text | 任意 | 欠落可・補完禁止 |
| execution.profile | 必須 | env.yaml と一致 |
| execution.run_id | 必須 | 再実行識別 |
| execution.timestamp | 必須 | ISO 8601 |
| answer.extracted | 必須 | HTML 非変換 |
| answer.raw | 条件付き | INVALID 時必須 |
| metadata.status | 必須 | VALID / INVALID |
| metadata.reason | 任意 | INVALID 時推奨 |

---

## 6. 明確な禁止事項（拘束）

- Extracted を optional にしてはならない
- Extracted を Markdown / text に変換してはならない
- Raw と Extracted を統合してはならない
- writer / dataset が status を再判定してはならない
- question.text を自動生成・補完してはならない
- 回答内容の評価・要約・正規化を行ってはならない

---

## 7. answer.md との関係（整理）

- answer.md は **rag_entry の物理的表現の一つ**
- writer は
  - answer.md を生成するだけ
  - rag_entry を「意識して」生成しない
- rag_entry schema は
  - **下流が answer.md を読む際の契約**

---

## 8. v0.2 の確定範囲と非対象

### 本 v0.2 で FIX するもの

- rag_entry の論理構造
- Extracted / Raw / status の必須性
- 下流による再解釈の禁止

### 本 v0.2 で扱わないもの

- dataset schema の詳細
- entry_id の生成規則
- 質問文の外部ファイル形式・管理方法

---

## 9. 本 schema の目的（再掲）

- F9-C（Extracted 正本化）の成果を下流で破壊させない
- F4 / dataset / 比較フェーズの暗黙前提を排除する
- 実装より先に **意味契約を固定**する

---
