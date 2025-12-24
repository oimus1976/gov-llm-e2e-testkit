---
doc_type: design
phase: F8
title: Design_F8_v0.3_runner
version: v0.3
status: fixed
date: 2025-12-25
based_on:
  - Design_F8_v0.2_runner
  - Design_F8_AutoQuestion_Execution_v0.1
  - F8 v0.2 設計合意サマリー
  - Roadmap_v1.4
notes:
  - This design defines runner / orchestrator API only.
  - Evaluation, judgment, optimization are explicitly out of scope.
  - Introduces best-effort raw answer capture independent of Answer Detection.
---

# 📘 Design_F8_v0.3_runner.md（FIX）

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
```

- 本 API は **実行制御のみ**を責務とする
- 回答内容・品質・成否判断は行わない

---

## 4. Input Data Structures

### 4.1 OrdinanceSpec

```python
@dataclass(frozen=True)
class OrdinanceSpec:
    ordinance_id: str
    display_name: str
```

- 条例本文・ファイルパスは含めない
- knowledge 投入は別レイヤ責務

---

### 4.2 QuestionSpec

```python
@dataclass(frozen=True)
class QuestionSpec:
    question_id: str   # Q01–Q18
    question_text: str
```

- 質問生成・改変は禁止
- 並び順＝実行順

---

### 4.3 ExecutionProfile

```python
@dataclass(frozen=True)
class ExecutionProfile:
    profile_name: str     # "markdown" 等
    run_mode: str         # 固定: "collect-only"
```

- 判断・評価パラメータは禁止
- frontmatter へ事実として記録するのみ

---

## 5. RunSummary（aborted-only）

```python
@dataclass(frozen=True)
class RunSummary:
    aborted: bool
    fatal_error: str | None
```

- 内部確認用のみ
- 成功数・失敗数・集計情報は禁止
- 外部プロジェクトへの受け渡し不可

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

- failure taxonomy は `run_single_question` 側で記録
- taxonomy を制御分岐に使用しない

---

## 7. Answer Detection の位置づけ

Answer Detection は以下の目的に限定される。

- 回答生成が **完了したかどうか** を
  観測事実に基づき確定する
- 実行制御および状態ラベル付与のための
  **制御信号**を提供する

Answer Detection は以下を行わない。

- 回答テキストの回収可否判断
- 回答品質・正確性の評価
- 後工程での利用可否判断

---

## 8. Raw Answer Capture（best-effort）

### 8.1 目的

Raw Answer Capture は、Answer Detection とは独立した
**回答素材回収経路**である。

- UI 上に実際に表示された回答テキストを
  **評価・判定を行わず** best-effort で保存する
- UI 変更や検出失敗が発生しても、
  **後工程へ渡す材料の欠損を最小化**する

---

### 8.2 基本方針

- DOM 上の複数候補から
  **量的・構造的指標に基づき 1 つを選択**する
- この処理は **判定ではなく選択（selection）**とする
- 選択結果は result_status・制御分岐に影響しない
- 失敗は例外とせず、黙って握りつぶす

---

### 8.3 成果物

```text
<question_id>/
  answer.md
  raw_answer.html        # 選択された DOM ブロック（outerHTML）
  raw_answer.txt         # raw_answer.html の textContent
  raw_capture_meta.json  # 選択事実メタデータ
```

#### raw_capture_meta.json（例）

```json
{
  "candidates_count": 12,
  "selected_index": 4,
  "metrics": {
    "text_length": 3241,
    "p_count": 18,
    "h_count": 3,
    "li_count": 9
  },
  "selection_rule_version": "v1"
}
```

※ 上記は **評価ではなく観測事実**である。

---

## 9. Artifact Policy（成果物ポリシー）

### 9.1 ディレクトリ構成（FIX）

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

- 1 問 = 1 ディレクトリ
- 上書き・差し替え禁止

---

### 9.2 frontmatter（要約）

- result_status: FAILURE TAXONOMY（単一値）
- result_reason: 事実補足（任意）
- aborted_run: 全体中断フラグ
- raw_capture: true / false（取得事実）

---

## 10. Non-Goals（明示）

本設計では以下を行わない。

- 回答品質・正確性の評価
- 成功率・件数の算出
- retry / 並列化 / 最適化
- CI 統合
- HTML 構造の意味解析・比較

---

## 11. Runtime Execution Constraint（実行環境上の制約）

本プロジェクトでは、Playwright を用いたランタイム試験は
VS Code 上の LLM 実行環境では実行できない。

そのため、静的テスト通過後は
**ローカル実行または CI によるランタイム確認を必須工程**とする。

---

## 12. Conclusion

本 runner / orchestrator 設計は、

- F8 を **材料生成フェーズ**に厳密に位置づけ
- 回答回収経路を **単線から二系統へ分離**し
- 外部 UI 変更に対する **耐性を設計として内包**する

ことで、後続プロジェクト（例規HTML変換等）に対し
**最大限の自由度と再現可能な素材**を提供する。

---

### 裁定（最終）

- **Design_F8_v0.3_runner として FIX**
- v0.2 系からの設計世代更新
- 実装着手可能な状態
