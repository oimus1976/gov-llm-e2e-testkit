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

### 4.2 フィールド定義

#### dataset_id

- dataset を一意に識別する ID
- 評価・比較・再利用のための論理名

#### source

dataset の生成元情報を示す。

- **人間が生成経緯を追跡するための補助情報**
- 下流処理の分岐条件として使用してはならない

|フィールド|説明|
|---|---|
|type|現時点では `f8_run` 固定|
|run_id|元となった F8 実行の識別子|
|path|元 F8 run ディレクトリのパス|

#### generated_at

- dataset 生成日時
- 再生成順序や履歴把握のための情報

#### entries

- rag_entry の集合
- **順序に意味は持たない**

各 entry は以下を持つ。

|フィールド|説明|
|-----|-----------|
|id|質問 ID（Q01 等）|
|path|dataset 内での answer.md 参照パス|

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

## 8. 設計原則（拘束）

1. dataset は意味を持たない
2. dataset は判断しない
3. dataset は再解釈しない
4. dataset は「束ねる」ことにのみ責任を持つ

---

## 付記

本 schema は、F9-D フェーズにおける  
**下流処理の安定性と再利用性を確保するための契約文書**である。

実装都合・評価都合による拡張は、  
**別 schema / 別設計文書で行うこと**。

---
