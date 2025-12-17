# Design_f4_trial_dataset_v0.1

## F4 v0.2 試金石データ構成設計（正式）

- Project: gov-llm-e2e-testkit
- Phase: F4（RAG 入力差分影響の観測・試験データ提供フェーズ）
- Status: Design（Approved when adopted）
- Version: v0.1
- Date: 2025-12-XX

---

## 0. Authority（設計根拠）

本設計は、以下を正本として策定される。

- Roadmap v1.2
- PROJECT_STATUS v0.6.4
- RAG 評価基準 v0.1
- Design_pytest_f4_results_writer v0.1.2

本設計は **F4 v0.2 の成果物定義**であり、
pytest 実装・自動化・CI 統合を直接の対象とはしない。

---

## 1. Purpose（目的）

本設計の目的は、

> **HTML / Markdown 等の RAG 入力差分が
> Qommons.AI の応答に与える影響を、
> 他プロジェクトが判断材料として利用可能な
>「試金石データ一式」として提供すること**

である。

本プロジェクトは、
**採用／不採用の判断を行わない**。
判断主体は外部プロジェクトに委ねられる。

---

## 2. Scope（適用範囲）

### 対象

- F4 v0.2 における試験結果の保存・提供形式
- 人手実行前提で取得された評価結果
- HTML / Markdown 差分評価（RAG 評価基準 v0.1）

### 非対象（Out of Scope）

- 評価結果の自動生成・自動更新
- CI 連携
- 意味理解・同義語評価
- スコアによる最終判断ロジック

---

## 3. 基本方針（Data Administration 原則）

本設計は、以下の原則に基づく。

1. **一次証拠（Raw）を最優先する**
2. **再評価・再集計が可能な構造を維持する**
3. **人間・機械の双方が消費可能である**
4. **将来の形式変換（JSONL / Parquet 等）を阻害しない**

---

## 4. データレイヤ構成（必須）

F4 v0.2 の試金石データは、
以下の **三層構造**を必須とする。

```

Layer A: Raw Evidence（一次証拠）
Layer B: Execution Context（実行条件）
Layer C: Derived Summary（派生サマリ）

```

いずれか一層でも欠けた場合、
本データは **試金石として不完全**とみなす。

---

## 5. ディレクトリ構成（v0.2）

```

docs/f4/trial_dataset/v0.2/
├── README.md
├── manifest.json
├── schema/
│   ├── raw_evidence.schema.json
│   ├── execution_context.schema.json
│   └── derived_summary.schema.json
├── raw/
│   ├── caseXX_html.json
│   └── caseXX_markdown.json
├── context/
│   └── execution_context.json
└── summary/
└── f4_diff_summary.json

```

---

## 6. Layer A: Raw Evidence（一次証拠）

### 6.1 目的

Raw Evidence は、
**後続のすべての評価・判断の根拠となる原本**である。

### 6.2 必須項目

| 項目 | 説明 |
|---|---|
| schema_version | スキーマ識別子 |
| case_id | Case 識別子 |
| knowledge_type | html / markdown |
| question_text | 実際に投入した質問文 |
| answer_text_raw | モデルの生回答 |
| answer_timestamp | 回答取得時刻 |
| model_identifier | 使用モデル識別子 |
| test_run_id | 実行単位識別子 |

評価スコア・判定結果は **含めない**。

---

## 7. Layer B: Execution Context（実行条件）

### 7.1 目的

Execution Context は、
**「同一条件での比較である」と証明するための情報層**である。

### 7.2 必須項目

| 項目 | 説明 |
|---|---|
| project_version | PROJECT_STATUS 対応 |
| rag_eval_version | 評価基準固定 |
| test_run_id | Raw との対応 |
| profile | 手動運用識別子 |
| login_identity.configured | 意図した条件 |
| login_identity.observed | 観測された条件 |
| knowledge_source_id | ナレッジ識別 |
| notes | 任意注記 |

---

## 8. Layer C: Derived Summary（派生サマリ）

### 8.1 位置づけ

Derived Summary は、
**人間が比較判断を行うための補助層**である。

本層のデータは **再生成可能**であり、
Raw Evidence が正本となる。

### 8.2 最小項目

| 項目 | 説明 |
|---|---|
| evidence_hit_rate | v0.1 指標 |
| hallucination_flag | 有無 |
| answer_stability_note | 定性記述 |
| inconclusive_reason | SKIP 時理由 |
| delta_comment | 差分所見 |

---

## 9. manifest.json（データセット目録）

manifest.json は、
データセット全体の **索引・説明責任ハブ**とする。

- ケース一覧
- 使用スキーマ
- 生成日
- 対象ナレッジ種別

---

## 10. 完了条件（F4 v0.2）

以下をすべて満たした時、
F4 v0.2 は **完了**とみなす。

- 三層構造のデータが揃っている
- Raw Evidence が欠落していない
- 第三者が README のみで利用目的を理解できる

---

## 11. 将来拡張（非拘束）

- JSONL / Parquet 変換
- 自動集計
- CI 連携

これらは **v0.3 以降の検討事項**とする。

---

End of Design_f4_trial_dataset_v0.1
