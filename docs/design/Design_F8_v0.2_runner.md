---
doc_type: design
phase: F8
title: Design_F8_v0.2_runner
version: v0.2
status: fixed
date: 2025-12-24
based_on:
  - Design_F8_AutoQuestion_Execution_v0.1
  - F8 v0.2 設計合意サマリー
  - Roadmap_v1.4
notes:
  - This design defines runner / orchestrator API only.
  - Evaluation, judgment, optimization are explicitly out of scope.
---

# 📘 Design_F8_v0.2_runner.md（FIX）

## 1. Purpose（目的）

本設計は、F8（Markdown 価値判断フェーズ）において使用する  
**runner / orchestrator API** を定義する。

目的は以下に限定される。

- 条例集合 × 質問集合を **止まらずに回す**
- 各質問について **必ず 1 レコード（Markdown）を生成**する
- 成否にかかわらず **事実ログを取り切る**
- 評価・判断・最適化を一切行わない

---

## 2. Design Principles（設計原則）

### 2.1 Orchestrator は関数である

- runner / orchestrator は **状態を表現しない**
- 実行手順を一度発火させる **制御手続き**とする
- クラス化・内部状態保持は禁止

### 2.2 continue-on-error を前提とする

- 原則として処理は中断しない
- 各質問は独立した実行単位とする

#### 唯一の中断条件

- browser / context / page が破壊され、
  **以降の実行が技術的に不可能**と判断された場合のみ

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

### 4.2 QuestionSpec

```python
@dataclass(frozen=True)
class QuestionSpec:
    question_id: str   # Q01–Q18
    question_text: str
```

- 質問生成・改変は禁止
- 並び順＝実行順

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

## 7. Artifact Policy（成果物ポリシー）

### 7.1 ディレクトリ構成（FIX）

```text
f8_runs/
└─ YYYYMMDD/
   └─ <ordinance_id>/
      └─ <question_id>/
         └─ answer.md
```

- 1 問 = 1 ファイル
- 上書き・差し替え禁止

### 7.2 frontmatter（要約）

- result_status: FAILURE TAXONOMY（単一値）
- result_reason: 事実補足（任意）
- aborted_run: 全体中断フラグ

---

## 8. Non-Goals（明示）

本設計では以下を行わない。

- 回答品質・正確性の評価
- 成功率・件数の算出
- retry / 並列化 / 最適化
- CI 統合
- HTML 参照・比較

---

## 9. Conclusion

本 runner / orchestrator 設計は、

- F8 を **材料生成フェーズ**に閉じ込め
- 正本を **Markdown 成果物**に固定し
- 後続プロジェクトによる自由な判断を阻害しない

ための **最小かつ誤解耐性のある設計**である。

---

### 裁定（最終）

- **設計として FIX**
- 既存合意・Roadmap・Non-Goals との不整合なし
- 実装着手可能な状態

---
