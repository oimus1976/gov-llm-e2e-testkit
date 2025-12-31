---
spec_id: Spec_F9-A_Implementation_v0.1
title: F9-A Implementation Specification
phase: F9-A
status: draft
created_at: 2025-12-31
updated_at: 2025-12-31
authors:
  - Sumio Nishioka
  - ChatGPT (Architect Role)
related_specs:
  - Spec_F9-A_Question_Set_and_Binding_v0.1.md
  - Spec_F9-B_Execution_Conditions_Freeze_v0.1r.md
  - Spec_F9-C_DOM_Scope_Rules_v0.2.md
scope:
  - implementation_flow
  - structural_resolution
  - ordinance_binding_generation
out_of_scope:
  - answer_generation
  - answer_evaluation
  - semantic_interpretation
  - ui_design
---

# Spec_F9-A_Implementation_v0.1

## 1. 目的

本仕様は、F9-A における  
**質問テンプレと条例参照情報を、必ず解決済みの実行用入力へ変換する処理フロー**  
を、実装者が誤解なく実装できる粒度で定義する。

本仕様は、

- 実装言語
- CLI / GUI / バッチ等の UI 形態

には依存しないが、  
**処理順序・責務境界・入力完全性**については厳密に拘束する。

---

## 2. F9-A の責務（再確認）

F9-A は以下を責務とする。

- 抽象的に記述された質問テンプレを受け取る
- 条例ID・条例データを前提として
- 条・項を **必ず確定**させる
- 曖昧さのない実行用質問と条例バインディングを生成する

F9-A は以下を行わない。

- 条文内容の意味解釈
- 回答の生成・評価
- 条・項の推測（意味的判断）

---

## 3. 全体処理フロー

```md

Input:

- question_template_set
- ordinance_id
- ordinance_source
- (optional) user_inputs

Process:

1. ValidateTemplate
2. BindOrdinanceID
3. LoadOrdinanceSource
4. ResolveArticleAndParagraph
   4-1. AutoResolve
   4-2. PromptUserIfNeeded
5. BuildOrdinanceBinding
6. GenerateResolvedQuestions
7. FinalGate

Output:

- ordinance_binding (resolved only)
- resolved_questions

```

---

## 4. 各処理の詳細

### 4.1 ValidateTemplate

#### 目的

質問テンプレが **仕様上許可された抽象表現のみ**を含むことを保証する。

#### 入力

- `question_template_set`

#### 処理内容

- 以下を検証する：
  - 条例ID・具体的な条番号・項番号が直接埋め込まれていない
  - 抽象表現は以下に限定される
    - この条例
    - 第○条
    - 第○項

#### 出力

- `validated_template_set`

#### 失敗時

- **即時エラー**
- ユーザー入力による回復は行わない（設計不備）

### 4.1.1 A-1 手動テスト手順（質問テンプレ検証）

本手順は、質問テンプレが F9-A 仕様に適合しているかを、
**コードを実行せずに人間（職員）が目視で確認するための手順**である。

#### 対象

- 質問セットファイル（例：YAML）
- 各 `questions[].text` に記載された質問テンプレ文

#### 手順

1. 質問セットファイルをテキストエディタで開く
2. 各質問テンプレ文（`questions[].text`）について、
   以下の OK / NG 条件を確認する

#### OK 条件（すべて満たす必要がある）

- 質問文は以下の抽象表現のみを用いている
  - 「この条例」
  - 「第○条」
  - 「第○条第○項」
- 条例ID、具体的な条番号・項番号が一切含まれていない

#### NG 条件（1つでも該当すれば不合格）

- 具体的な条番号・項番号が含まれている  
  例：
  - 「第3条は〜」
  - 「第2条第1項では〜」
- 条例IDが直接記述されている  
  例：
  - 「この条例（k518RG00000022）は〜」

#### 判定

- すべての質問テンプレが OK 条件を満たす場合、
  当該質問セットは **F9-A に投入可能**と判定する
- 1つでも NG 条件に該当する場合、
  当該質問セットは **F9-A に投入不可**と判定する

#### 補足

- 本手順は A-1（ValidateTemplate）の仕様確認手段であり、
  条・項の具体化は A-3 / A-4（条例バインディング）で行う
- 本手順により不合格となった質問セットは、
  実装上の例外ではなく **設計違反**として扱う

---

### 4.2 BindOrdinanceID

#### 目的

実行単位において **単一の条例IDを論理的に束縛**する。

#### 入力

- `ordinance_id`
- `validated_template_set`

#### 処理内容

- 「この条例」という指示語が、
  当該 `ordinance_id` を指すことを内部的に確定する
- この段階では文字列展開は行わない

#### 出力

- `template_with_ordinance_context`

---

### 4.3 LoadOrdinanceSource

#### 目的

条例データ（一次資料）を **構造情報としてロード**する。

#### 入力

- `ordinance_id`
- `ordinance_source`

#### 処理内容

- 条番号の列挙
- 各条に属する項番号の列挙

#### 出力

- `ordinance_structure`

```yaml
articles:
  1: [1]
  2: [1, 2, 3]
  3: [1]
  4: [1, 2, 3, 4, 5]
```

#### 失敗時

- 条例データ不整合エラー（入力データ不備）

---

### 4.4 ResolveArticleAndParagraph

#### 目的

各質問について、条・項を **必ず確定**させる。

---

#### 4.4.1 AutoResolve

##### 入力

- `template_with_ordinance_context`
- `ordinance_structure`

##### 処理内容

- 質問ごとに必要な参照単位を判定する

  - 条のみ必要
  - 条＋項が必要
- 以下の制約下で自動解決を試みる：

  - 事前に定義された機械的ルール
  - 明示的に与えられた索引情報
- **条文内容の意味解釈や推測は行わない**

##### 出力

- `partial_resolution`

```yaml
Q02:
  article: 3
Q03:
  article: 4
  paragraph: null
```

---

#### 4.4.2 PromptUserIfNeeded（解決保証）

##### 発火条件

- `article` または `paragraph` が未確定の場合

##### 処理内容

- 職員に対し、条・項の直接入力を要求する
- 入力時には以下を提示してよい：

  - 対象質問ID
  - 条・項の候補一覧（構造情報）

##### 入力

- `user_inputs`

##### 出力

- `fully_resolved_mapping`

##### 重要制約

- 入力された値は **即時に条例バインディング候補として反映**される
- 未解決状態のまま処理を終了してはならない

---

### 4.5 BuildOrdinanceBinding

#### 目的

解決済み情報のみを **条例バインディングとして確定**する。

#### 入力

- `fully_resolved_mapping`

#### 処理内容

- null / 未定義の検出（存在してはならない）
- 最終存在確認

#### 出力

- `ordinance_binding`

```yaml
ordinance_id: k518RG00000022
bindings:
  Q01:
    ordinance_id: k518RG00000022
  Q02:
    article: 14
  Q03:
    article: 4
    paragraph: 5
```

---

### 4.6 GenerateResolvedQuestions

#### 目的

抽象表現をすべて排除した **実行用質問文**を生成する。

#### 入力

- `validated_template_set`
- `ordinance_binding`

#### 処理内容

- 機械的な文字列展開のみを行う

#### 出力

```text
Q01: この条例（k518RG00000022）は何を目的として制定されていますか。
Q02: 第14条はどのような内容を定めていますか。
Q03: 第4条第5項では何を規定していますか。
```

---

### 4.7 FinalGate（入力完全性ゲート）

#### 目的

F9-B / F9-D に渡すための **入力完全性を保証**する。

#### チェック項目

- 抽象表現が一切残っていない
- 条例バインディングが完全に解決済み
- 実行用質問が一意に確定している

#### 出力

- F9-A Result: OK

---

## 5. 後続フェーズとの関係

- F9-B / F9-D は、
  - 条例バインディング
  - 実行用質問
    を **再解釈せず、そのまま使用する**
- F9-A は後続フェーズのための
  **入力完全性保証フェーズ**である

---

## 6. 非目標（Out of Scope）

- 回答生成
- 回答評価
- 条文内容の意味解釈
- UI 設計・UX 判断

---

## 7. まとめ

F9-A は、

- 抽象的な質問を許容しつつ
- 構造的事実のみを用いて
- 必ず評価可能な入力へ変換する

ための **決定フェーズ**である。

本仕様により、
F9-A 実装は **止まらず・迷わず・曖昧さを残さない**ことが保証される。

---
