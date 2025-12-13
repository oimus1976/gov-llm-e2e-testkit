# Basic RAG Test v0.1

## 1. Purpose（目的）

Basic RAG Test v0.1 は、RAG（Retrieval-Augmented Generation）を用いた
QA システムに対して、**最低限の品質確認を自動テストとして実施可能にする**
ことを目的とする。

本テストは以下を保証する：

- 入力した質問に対し、LLM が何らかの応答を返すこと
- 応答本文に、事前に定義した *expected keywords* がすべて含まれていること

本テストは以下を保証しない：

- 応答内容の正確性・完全性・網羅性
- 根拠の妥当性や引用構造
- モデルや知識ベースの品質評価

---

## 2. Scope（適用範囲）

### In Scope
- 単一質問に対する単一応答の検証
- 非決定的な LLM 応答を前提とした **キーワード包含判定**
- YAML 定義に基づくデータ駆動テスト

### Out of Scope
- 複数ターン対話の文脈評価
- 厳密一致・数値比較・構造比較
- 回答の「正しさ」を意味論的に評価すること
- Advanced RAG Test で扱う高度な検証

---

## 3. Test Level Positioning（テストレベルの位置づけ）

本テストは、以下のテスト階層のうち **Basic** に位置づけられる。

- Smoke Test  
  → システムが動作可能であることを確認する最小テスト
- **Basic RAG Test（本ドキュメント）**  
  → RAG QA が最低限成立していることを確認
- Advanced RAG Test  
  → 回答品質・根拠構造・一貫性などの高度検証

Basic RAG Test は、Smoke Test が成功していることを前提条件とする。

---

## 4. Judgment Rules（合否判定ルール）

### PASS 条件
- 応答本文（プレーンテキスト）に、
  定義された `expected_keywords` が **すべて含まれている**

### FAIL 条件
- `expected_keywords` のうち、1つ以上が応答本文に含まれていない

### 判定不能（Inconclusive）
- 応答本文を取得できなかった場合
- システムエラーや通信エラーにより判定が実施できない場合

※ FAIL / Inconclusive は  
「システムまたはモデルが *悪い*」ことを意味しない。  
あくまで **観測事実として条件を満たさなかった** ことを示す。

---

## 5. Test Case Specification（テストケース定義）

### 入力項目（YAML）

最小構成は以下とする：

```yaml
case_id: BASIC_RAG_001
input: |
  ○○について簡潔に説明してください。
expected_keywords:
  - ○○
  - △△
strict: false
```

- `case_id`
  テストケース識別子
- `input`
  チャットに送信する質問文
- `expected_keywords`
  応答に含まれることを期待するキーワードの配列
- `strict`
  判定拡張用フラグ（v0.1 では false のみを想定）

---

## 6. Execution Preconditions（実行前提条件）

- Smoke Test が成功していること
- テスト環境（env.yaml）が正しく設定されていること
- PageObject / locator / submit / answer detection の設計を変更しないこと

Basic RAG Test は、既存のアプリケーション基盤の上で
**テストロジックのみを追加する層**である。

---

## 7. Evidence (Observed Facts)（観測事実）

本テストで取得・保持する証跡は以下に限定する：

- 質問文（input）
- 応答本文（raw text）
- 判定結果（PASS / FAIL / Inconclusive）
- 不足していたキーワード（FAIL 時）

テストは、これらの **観測事実のみを記録**し、
意味解釈や評価は行わない。

---

## 8. Known Limitations（既知の限界）

- 応答が言い換え表現のみの場合でも FAIL となる
- キーワードが文脈上否定されていても PASS となる可能性がある
- モデル更新や知識更新により、結果が変動しうる

これらの制約は、Advanced RAG Test で段階的に扱う。

---
