---
doc_type: design
phase: F8
title: Design_F8_AutoQuestion_Execution
version: v0.1
status: fixed
date: 2025-12-23
parent: Roadmap_v1.3
related:
  - Design_probe_graphql_answer_detection_v0.2
  - Design_answer_probe_api_v0.1
  - 成果物インターフェース定義_v0.1r+
notes:
  - This design defines execution I/F only (question submission, answer detection, raw logging).
  - Evaluation, judgment, and comparison are explicitly out of scope.
  - F8 is “material generation for value judgment”, not the judgment itself.
---

# 📘 Design_F8_AutoQuestion_Execution v0.1（FIX）

## 0. 目的（Purpose）

本設計書は、F8（**Markdown 価値判断のための材料生成フェーズ**）において使用する
**自動質問・回答収集の実行 I/F**を定義する。

本 I/F は以下を満たすことを目的とする。

- 1 問単位の処理を **純粋な実行エンジン**として切り出す
- pytest（F4）およびバッチ実行（F8）の **両方から再利用可能**とする
- 回答内容の評価・判断・比較・整形を一切行わない
- 成果物は **成果物インターフェース定義 v0.1r+** に準拠して記録する

---

## 1. 設計方針（Design Principles）

### 1.1 単一質問 I/F を最小単位とする

- **1 問 = 1 回の実行**
- 実行結果は必ず 1 つの成果物として出力される
- 成否は「取得できた／できなかった」のみで扱う（評価語は禁止）

---

### 1.2 18 問セットは制御層で扱う

- 18 問という構造は **実行エンジンの責務ではない**
- ループ・中断・セット無効判定は **上位制御（runner）**で行う

---

### 1.3 pytest を I/F の外に追い出す

- pytest fixture 依存は **実行エンジンに持ち込まない**
- pytest は「検証用ラッパー」としてのみ利用する（F4）

---

## 2. 単一質問実行 I/F 定義

### 2.1 関数シグネチャ（論理 I/F）

```python
run_single_question(
    *,
    chat_page,
    question_text: str,
    question_id: str,
    ordinance_id: str,
    output_dir: Path,
    profile: str,
    execution_context: dict | None = None,
) -> None
```

---

### 2.2 入力仕様

| 引数                | 内容                                     |
| ----------------- | -------------------------------------- |
| chat_page         | Playwright ChatPage（submit / page を提供） |
| question_text     | 質問本文（原文そのまま）                           |
| question_id       | Q01–Q18 等の識別子                          |
| ordinance_id      | 対象条例 ID                                |
| output_dir        | 出力ディレクトリ（1問専用）                         |
| profile           | html / markdown 等（実行条件の識別に使用）          |
| execution_context | 任意（取得できる範囲のみ／推測禁止）                     |

---

### 2.3 処理内容（内部手順）

1. `chat_page.submit(question_text)` を実行する
2. `submit_id` / `chat_id` を観測する（取得できない場合は定義済みの扱いに従う）
3. Answer Detection（probe）により **回答確定待ち**を行う
4. UI 表示された **回答全文（Raw）**を取得する（改変・要約禁止）
5. UI 表示された **引用・参照（Citations As Displayed）**を取得する（補完禁止）
6. 成果物インターフェース定義 v0.1r+ に従い Markdown を出力する

---

### 2.4 出力仕様

- **1 問 = 1 Markdown ファイル**
- 上書き禁止
- 整形・要約・評価は禁止
- 出力形式は **成果物インターフェース定義 v0.1r+** に準拠する

---

## 3. F8 セット実行（制御層）

### 3.1 セット実行の責務

- 条例 1 本 × 質問 18 問を **順序固定で実行**する
- 1 問でも失敗した場合、**セット全体を未完了（無効）**として扱う
- 途中生成物は削除しない（事実として残す）

---

### 3.2 論理フロー

```text
for question in questions_18:
    run_single_question(...)
    if failure:
        abort set (set is incomplete/invalid)
```

---

### 3.3 禁止事項

- 質問の生成・改変
- 質問順序の変更
- UI 手動送信
- HTML の参照・比較（Markdown 実行中）
- pytest 実行による代替（F8 実行は runner による）

---

## 4. F4 pytest との関係

- F4 pytest は `run_single_question()` を呼び出す
- Evidence 評価（evaluate_evidence 等）は **pytest 側（F4 側）のみ**で実施する
- F8 実行では Evidence 評価ロジックを使用しない（評価禁止）

---

## 5. Non-Goals（明示）

本設計は以下を **対象外**とする。

- CLI UX の最適化
- 並列実行
- 再試行制御
- 自動評価・自動判断
- CI 恒久化・自動合否判定

---

## 6. 将来拡張（非拘束・参考）

- JSON 併設出力（成果物インターフェース定義の範囲での将来拡張）
- LGWAN 実行対応（環境提供後の別フェーズで扱う）

※ 本節は拘束力を持たない。必要になった時点で別途設計する。

---

## 7. 設計確定事項（FIX）

- 単一質問 I/F（`run_single_question`）を新設する
- 18 問は制御層（runner）でループする
- pytest は実行エンジンではなく、検証用ラッパーである
- F4 / F8 は同一実行エンジンを共有する
- F8 は価値判断を行わず、価値判断のための材料（観測ログ）を生成する

---
