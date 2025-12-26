---
doc_type: design
phase: F8
title: Design_F8_v0.3.1_runner
version: v0.3.1
status: fixed
date: 2025-12-25
based_on:
  - Design_F8_v0.3_runner
notes:
  - Clarifies canonical source of answer.md as UI DOM-based artifact
  - No change in phase, scope, API, or non-goals
---

# 📘 Design_F8_v0.3.1_runner.md（責務明確化・FIX）

## 1. Purpose（目的）

本設計は、F8（Markdown 価値判断フェーズ）において使用する  
**runner / orchestrator API** を定義する。

目的は以下に限定される。

- 条例集合 × 質問集合を **止まらずに回す**
- 各質問について **必ず 1 レコード（Markdown）を生成**する
- 成否にかかわらず **事実ログおよび回答素材を取り切る**
- 評価・判断・最適化を一切行わない

本設計において、F8 runner は  
**「回答を評価する存在」ではなく  
「後工程へ渡す材料を最大限回収する存在」**として定義される。

---

## 2. Design Principles（設計原則）

### 2.1 Orchestrator は関数である

- runner / orchestrator は **状態を表現しない**
- 実行手順を一度発火させる **制御手続き**とする
- クラス化・内部状態保持は禁止

---

### 2.2 continue-on-error を前提とする

- 原則として処理は中断しない
- 各質問は独立した実行単位とする

#### 唯一の中断条件

- browser / context / page が破壊され、
  **以降の実行が技術的に不可能**と判断された場合のみ

---

### 2.3 外部 UI 非契約前提

- Qommons.AI の UI / DOM 構造は **契約されていない**
- DOM 構造・class 名・描画順序・更新タイミングは
  将来変更される前提とする
- 単一 DOM 構造への依存を前提とした設計は禁止

---

## 3. Orchestrator API（論理 I/F）

```python
def run_f8_collection(
    *,
    chat_page,
    ordinances: list[OrdinanceSpec],
    questions: list[QuestionSpec],
    execution_profile: ExecutionProfile,
    output_root: Path,
) -> RunSummary:
    ...
````

* 本 API は **実行制御のみ**を責務とする
* 回答内容・品質・成否判断は行わない

---

## 4. Input Data Structures

### 4.1 OrdinanceSpec

```python
@dataclass(frozen=True)
class OrdinanceSpec:
    ordinance_id: str
    display_name: str
```

* 条例本文・ファイルパスは含めない
* knowledge 投入は別レイヤ責務

---

### 4.2 QuestionSpec

```python
@dataclass(frozen=True)
class QuestionSpec:
    question_id: str   # Q01–Q18
    question_text: str
```

* 質問生成・改変は禁止
* 並び順＝実行順

---

### 4.3 ExecutionProfile

```python
@dataclass(frozen=True)
class ExecutionProfile:
    profile_name: str     # "markdown" 等
    run_mode: str         # 固定: "collect-only"
```

* 判断・評価パラメータは禁止
* frontmatter へ事実として記録するのみ

---

## 5. RunSummary（aborted-only）

```python
@dataclass(frozen=True)
class RunSummary:
    aborted: bool
    fatal_error: str | None
```

* 内部確認用のみ
* 成功数・失敗数・集計情報は禁止
* 外部プロジェクトへの受け渡し不可

---

## 6. Internal Flow（概念）

```text
for ordinance in ordinances:
    for question in questions:
        run_single_question(...)
        if fatal error:
            abort execution
        else:
            continue
```

* failure taxonomy は `run_single_question` 側で記録
* taxonomy を制御分岐に使用しない

---

## 7. Answer Detection の位置づけ

Answer Detection は以下の目的に限定される。

* 回答生成が **完了したかどうか** を
  観測事実に基づき確定する
* 実行制御および状態ラベル付与のための
  **制御信号**を提供する

Answer Detection は以下を行わない。

* 回答テキストの回収可否判断
* 回答品質・正確性の評価
* 後工程での利用可否判断

---

### 7.1 answer.md（正本）の生成責務（明確化）

answer.md は、当該質問実行において
**UI 上に実際に表示された最終回答内容**を
後工程へ受け渡すための **正本成果物**である。

その生成においては、以下を原則とする。

* answer.md の本文は
  **Raw Answer Capture により選択された DOM ブロック**に基づいて生成する
* Answer Detection（probe）は
  回答生成完了の観測および実行制御のための **補助的信号**であり、
  answer.md の本文生成可否・内容決定には **直接関与しない**
* Answer Detection が例外を返した場合であっても、
  Raw Answer Capture により UI 表示内容が取得できている場合、
  answer.md はその内容を正として生成される

本原則により、

* 通信観測（probe）
* UI 観測（DOM）
* 成果物正本（answer.md）

の責務を分離し、
UI 実態に基づく **一貫した成果物生成**を保証する。

---

## 8. Raw Answer Capture（best-effort）

### 8.1 目的と位置づけ

Raw Answer Capture は、Answer Detection とは独立した
**回答素材回収経路**である。

* UI 上に実際に表示された内容を
  **評価・判定を行わず** best-effort で回収する
* UI 変更や Answer Detection の失敗が発生しても、
  **後工程へ渡す材料の欠損を最小化**する
* runner の成否判定・制御・評価には
  **一切関与しない**

---

### 8.2 Answer Detection との関係

Answer Detection と Raw Answer Capture は **競合しない**。

* Answer Detection

  * 設計上想定した UI 構造から
    回答生成完了を観測するための **センサー**
* Raw Answer Capture

  * Answer Detection の成否に関係なく、
    UI に表示された内容を **素材として回収する経路**

Answer Detection が失敗した場合でも、
Raw Answer Capture により **素材回収は継続される**。

---

### 8.3 構造選択（selection）の非評価性

Raw Answer Capture では、
DOM 上の複数候補から **1 つの保存対象を選択**するために
量的・構造的指標を用いることがある。

この処理は、

* 保存対象を 1 つに限定するための
  **技術的選択（selection）**
* 容量・取り扱い単位を安定させるための手段

であり、以下を **一切評価・判定しない**。

* 回答の正しさ
* 回答の品質
* 回答としての妥当性

---

### 8.4 raw_capture フラグの定義

`raw_capture` は、以下の事実のみを表す。

> **当該質問実行において、
> Answer Detection とは独立した raw capture 経路を
> best-effort で試行したかどうか**

* `raw_capture: true`

  * capture 処理を試行した
* `raw_capture: false`

  * capture 処理を試行していない（旧 runner 等）

以下は `raw_capture` の意味に **含まれない**。

* raw 成果物が新規保存されたかどうか
* 既存ファイルが存在したかどうか
* 保存内容の有無・量・品質

---

### 8.5 成果物

```text
<question_id>/
  answer.md
  raw_answer.html        # 選択された DOM ブロック（outerHTML）
  raw_answer.txt         # raw_answer.html の textContent
  raw_capture_meta.json  # 選択事実メタデータ
```

raw 成果物はすべて **観測素材**であり、

* 正本は `answer.md`
* raw 成果物は **後続工程向けの一次素材**

と位置づけられる。

---

## 9. Artifact Policy（成果物ポリシー）

### 9.1 ディレクトリ構成

```text
f8_runs/
└─ YYYYMMDD/
   └─ <ordinance_id>/
      └─ <question_id>/
         ├─ answer.md
         ├─ raw_answer.html
         ├─ raw_answer.txt
         └─ raw_capture_meta.json
```

* 1 問 = 1 ディレクトリ
* 上書き・差し替え禁止

---

### 9.2 frontmatter（要約）

* result_status: FAILURE TAXONOMY（単一値）
* result_reason: 事実補足（任意）
* aborted_run: 全体中断フラグ
* raw_capture: true / false
  （Raw Answer Capture 経路を **試行した事実**）

---

## 10. Non-Goals（明示）

本設計では以下を行わない。

* 回答品質・正確性の評価
* 成功率・件数の算出
* retry / 並列化 / 最適化
* CI 統合
* HTML 構造の意味解析・比較

---

## 11. Runtime Execution Constraint（実行環境上の制約）

本プロジェクトでは、Playwright を用いたランタイム試験は
VS Code 上の LLM 実行環境では実行できない。

そのため、静的テスト通過後は
**ローカル実行または CI によるランタイム確認を必須工程**とする。

---

## 12. Conclusion

本 runner / orchestrator 設計は、

* F8 を **材料生成フェーズ**に厳密に位置づけ
* 回答回収経路を **通信観測と UI 観測に分離**し
* answer.md の正本生成責務を **UI 実態に基づき明確化**する

ことで、後続プロジェクトに対し
**再解釈不要・再現可能な素材セット**を提供する。

---

### 裁定（最終）

* **Design_F8_v0.3.1_runner として FIX**
* v0.3 の設計思想・裁定を破壊しない
* 実装は本設計に追従する最小修正のみを許可する
