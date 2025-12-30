---
title: Schema_dataset_v0.2
project: gov-llm-e2e-testkit
phase: F9-D
status: FIX
version: v0.2
previous_version: Schema_dataset_v0.1
date: 2025-12-30
owner: Sumio Nishioka
Breaking Change: NO
---

# 📦 Schema_dataset v0.2

**— rag_entry を再解釈せずに束ねる dataset 論理構造定義 —**

---

## 0. 本ドキュメントの位置づけ

本書は、**Schema_dataset_v0.1** にて定義された  
dataset の基本概念・論理単位を前提とし、  
**F9-D（下流整合）フェーズにおける利用・記述上の補足を行う**ものである。

- v0.1 の定義を置き換えない
- 上下関係や成熟度の序列は定義しない
- dataset の意味・責務を変更しない

本書は **同一スキーマの改訂版（v0.2）**であり、  
設計上の連続性を保ったまま記述を補強する。

---

## 1. dataset の定義（再掲）

dataset とは、以下を満たす **論理的集合単位**である。

- 複数の **確定済み rag_entry** を束ねた集合
- 各 rag_entry の意味・内容を **再解釈しない**
- 評価・比較・学習等の下流用途に投入可能な **安定した入力単位**

dataset 自体は、

- 回答の正誤
- 回答品質
- モデル性能

といった判断を一切行わない。

---

## 2. dataset の責務（v0.2 での明確化）

dataset の責務は、以下に **厳密に限定**される。

### 2.1 やること（責務）

- 確定済み rag_entry を **構造的に束ねる**
- 各 rag_entry の参照パスを保持する
- dataset 単位のメタ情報を付与する

### 2.2 やらないこと（非責務）

- rag_entry の内容解釈
- Raw / Extracted の再生成・補完
- 評価結果の付与
- 差分検証・一致検証の強制

---

## 3. 利用モデル（重要）

dataset は、以下の用途で **使用されることを想定する**。

- 評価フェーズ（人手・自動）の入力単位
- モデル比較・条件差分試験の素材集合
- 再実行不要な観測結果の再利用

一方で、dataset は次の用途には **使用されてはならない**。

- rag_entry の妥当性判断
- schema 適合性の検証結果の保存
- 生成ロジックの切替条件

---

## 4. dataset.yaml 構造定義

### 4.1 トップレベル構造

```yaml
dataset_id: <string>
source:
  type: f8_run
  run_id: <string>
  path: <string>
generated_at: <ISO-8601 datetime>
entries:
  - id: <question_id>
    path: entries/<question_id>/answer.md
```

---

## 4.2 フィールド定義（必須 / 任意 / 禁止）

本節では、dataset.yaml に含めるフィールドを
**必須（MUST） / 任意（MAY） / 禁止（MUST NOT）**
の 3 区分で定義する。

---

### 4.2.1 必須フィールド（MUST）

以下のフィールドは **すべて必須**であり、
いずれかが欠落した場合、そのファイルは dataset として扱われない。

---

#### schema_version（MUST）【確定】

- dataset.yaml が  
  **どの構造前提で記述されているかを明示する識別子**
- 現行は `dataset.v0.2` 固定

schema_version は、

- 内容の意味解釈
- 処理分岐
- 評価条件の切替
- 有効／無効の判断

の根拠として **使用してはならない**。

これはあくまで、  
**構造が何を前提として書かれているかを示すための情報**である。

---

#### dataset_id（MUST）

- dataset を一意に識別する論理 ID
- 人間およびツール双方で参照される識別子
- 意味的解釈や評価結果を含んではならない

#### source

dataset の生成元情報を示す。

- **人間が生成経緯を追跡するための補助情報**
- 下流処理の分岐条件として使用してはならない

|フィールド|説明|
|---|---|
|type|現時点では `f8_run` 固定|
|run_id|元となった F8 実行の識別子|
|path|元 F8 run ディレクトリのパス|

#### generated_at（MUST）

- dataset が生成された日時
- **ISO-8601 形式、タイムゾーン付き（JST, +09:00）**
- 再生成順序や履歴把握のための事実記録のみを目的とする

---

#### entries（MUST）【表現調整】

- rag_entry の集合を表すフィールド
- 各要素は **1 質問 = 1 rag_entry** に対応する
 **順序に意味は持たない**

entries が空となる状況については、

- 本 schema では **想定しない**
- 妥当性判断・エラー扱いの是非は
  **生成側（build スクリプト・運用・テスト）の責務**とする

各 entry は以下を必ず持つ。

|フィールド|要件|
|----|---|
|id|質問 ID（例：Q01）。質問セットとの 1:1 対応を保証する|
|path|dataset ルートからの相対パスで answer.md を指す|

---

### 4.2.2 任意フィールド（MAY）

#### source（MAY）

dataset の生成元に関する補助情報。

- **人間が生成経緯を追跡するためのメタ情報**
- 下流処理・評価・条件分岐の判断材料として使用してはならない
- 有無によって dataset の意味・有効性が変化してはならない

|フィールド|説明|
|---|---|
|type|現行では `f8_run`|
|run_id|元となった F8 実行の識別子|
|path|元 F8 run ディレクトリのパス|

---

### 4.2.3 禁止フィールド（MUST NOT）【責務明確化】

以下の情報は、
**本 schema の契約範囲外であり、dataset.yaml に含めてはならない。**

#### 評価・判断に関する情報（禁止）

- 回答の正誤・品質・優劣
- スコア・ランク・判定結果
- VALID / INVALID 等の集計状態
- HTML / Markdown 差分の評価結果

#### 実行条件・環境情報（禁止）

- profile / account / env
- browser / model / temperature 等の実行条件
- CI / 手動実行の別を示す情報

#### entries 内での再掲情報（禁止）

- answer.md の内容要約
- Raw / Extracted の再掲・コピー
- text_len / 判定理由などの派生情報

これらの検出・是正・拒否は、

- schema ではなく
- **生成・検証・運用側の責務**

とする。

---

## 5. rag_entry との関係（明文化）

- dataset は **rag_entry の集合**
- rag_entry は **1 質問 = 1 単位**
- dataset は **再解釈層を持たない**

```text
answer.md  →  rag_entry  →  dataset
（確定）       （確定）      （束ね）
```

---

## 6. 検証・整合性確認との関係

dataset が **rag_entry を再解釈していないことの確認**は、

- build_dataset_from_f8
- verify-diff 等の生成・検証スクリプト

によって **別途行われることがある**。

本 schema は、

- 検証方法
- 検証結果
- diff 一致条件

を **規定しない**。

---

## 7. v0.1 からの変更点（要約）

- dataset の利用モデルを明文化
- source フィールドの位置づけを明確化
- 検証責務を schema から分離
- 責務／非責務の境界を明確化

※ dataset の論理定義自体は v0.1 から変更していない。

---

## 8. 設計原則（拘束・最終確定）

1. dataset は意味を持たない
2. dataset は判断しない
3. dataset は再解釈しない
4. dataset は「束ねる」ことにのみ責任を持つ
5. dataset は評価・実行条件・派生結果を保持してはならない

---

## FIX 宣言（v0.2）

本書により、

- dataset.yaml に含める情報の **上限と下限**
- schema が責務を持つ範囲と **持たない範囲**
- F9-D における dataset の **最終的な位置づけ**

が確定した。

**Schema_dataset_v0.2 は FIX とし、
以降の拡張は v0.3 以降でのみ行う。**

---
