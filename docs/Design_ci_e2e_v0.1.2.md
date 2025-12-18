# Design_ci_e2e_v0.1.2

gov-llm-e2e-testkit — **CI（GitHub Actions）設計書［基盤確認 CI］**

* 最終更新: **2025-12-18**
* バージョン: **v0.1.2**
* 種別: Design（意味論確定・実装非変更）
* 参照:

  * PROJECT_GRAND_RULES v4.2
  * Startup Template v3.1
  * test_plan v0.1.1
  * PROJECT_STATUS v0.6.5

---

## 1. 目的（Purpose）

本書は gov-llm-e2e-testkit における
**E2E テスト基盤（Foundation）の成立性を CI 上で確認するための設計**を定義する。

本 CI（v0.1.2）の主目的は、以下に**厳密に限定**される。

* UI 送信（`ChatPage.submit`）が CI 環境で成立すること
* Answer Detection Layer（probe）が
  **観測事実として応答完了を検知できる**こと
* submit–probe 相関結果を
  **誤解のない意味論（PASS / WARN / INFO）**で可視化できること
* CI が
  **「次のフェーズに進める前提条件が壊れていないか」**
  を判断可能な状態を提供すること

**本 CI は、RAG QA の正確性・意味的妥当性・品質評価を一切行わない。**

---

## 2. スコープ（Scope）

* 対象環境：**INTERNET 環境の GitHub Actions のみ**
* LGWAN 環境は CI 対象に含めない
  （Startup Template v3.1 / env 設計の規定による）

本 CI は **E2E 基盤確認専用**であり、
RAG QA（Basic / Advanced）は本スコープ外とする。

---

## 3. テスト体系上の位置づけと CI 実行範囲

（test_plan v0.1.1 準拠）

本プロジェクトのテスト体系上の**論理的順序**は以下である。

1. Smoke Test
2. Basic RAG Test
3. Advanced RAG Test

ただし **本 CI（v0.1.2）で実行されるのは以下のみ**である。

* **Smoke Test（必須）**

Basic / Advanced RAG Test は：

* test_plan 上では正式に定義されているが
* **CI 実行は意図的に Deferred（保留）**されている

理由：

* submit–probe 相関を含む E2E 基盤が
  **十分に安定していることを最優先で確認するため**
* RAG QA は
  **基盤が信用できることを前提条件とする上位フェーズ**であるため

---

## 4. ディレクトリ構造（CI 観点）

```text
tests/
  test_smoke_llm.py        # 基盤確認用 Smoke Test

data/
  rag/                    # RAG QA 用データ（CI v0.1.2 では未使用）
```

Basic / Advanced RAG 用 pytest / YAML は
**存在していても CI v0.1.2 では実行しない。**

これらは **将来フェーズ（Phase B / F7 以降を含む）で
再利用される可能性を前提として保持される。**

---

## 5. Secrets（機密情報）管理方針

GitHub Actions では GitHub Secrets を用いる。

* `QOMMONS_URL`
* `QOMMONS_USERNAME`
* `QOMMONS_PASSWORD`

CI 実行時：

* `.env` を CI 内で生成
* `PROFILE=internet` を明示
* Secrets 未設定時は
  **MissingSecretError により明示的に FAIL**

env.yaml の上書きは行わない。

---

## 6. CI 実行ステップ（概要）

CI の実行ステップは以下で構成される。

1. リポジトリ checkout
2. Python セットアップ
3. 依存関係のインストール（pytest / playwright）
4. CI 用 `.env` 準備
5. Smoke Test 実行
6. submit–probe 相関サマリー生成
7. GitHub Actions Summary への結果出力
8. 失敗時のみ artifacts（logs/）を収集

---

## 7. e2e.yml（基盤確認 CI 定義）

本章に記載する `e2e.yml` は、
**E2E 基盤（submit / probe / correlation）の成立性を確認するための CI 定義**である。

この YAML は以下を保証する。

* UI 送信が CI 環境で成立すること
* probe が REST / GraphQL 観測を通じて応答を検知できること
* submit–probe 相関状態が `summary.json` として生成されること
* 相関状態が PASS / WARN / INFO として誤解なく可視化されること

以下は **基盤確認用 e2e.yml（v0.1）**であり、

* RAG QA（ask / semantic evaluation）
* Basic / Advanced RAG Test の pytest 実行

は **意図的に含めていない。**

（※ YAML 本体は実行定義であり、本設計書では変更しない）

```yaml
# e2e.yml 本体はリポジトリ上の実体と完全一致するものを使用する
```

---

## 8. 補足定義（Normative Definitions）

### 8.1 「最小 CI（Minimal CI）」の定義

本設計における「最小 CI」とは、以下を意味する。

* E2E テスト基盤の成立性を確認するために
  **必要十分な構成のみ**を含む CI であること
* 以下は **意図的に含めない**：

  * RAG 回答の品質評価
  * 意味的正確性・同義語判定
  * HTML / Markdown 差分評価（F4）
  * multi-turn / Advanced RAG Test
* CI の役割は「品質保証」ではなく、
  **基盤が壊れていないことの継続的検証**に限定される

---

### 8.2 「基盤の破壊（Foundation Breakage）」の定義

本 CI において検知対象とする
**「基盤の破壊」**とは、以下のいずれかが成立しない状態を指す。

* `ChatPage.submit` による UI 送信が成立しない
* Answer Detection Layer（probe）が
  完了意味論に基づく応答観測に失敗する
* submit_id と probe 観測結果の相関状態を確定できない
* CI 実行結果が
  **「基盤不成立」と「品質問題」を区別できない状態**に陥る

これらは RAG QA 以前の問題であり、
**本 CI はそれらを即時検知するために存在する。**

---

### 8.3 非対象の明示（再掲）

以下は「基盤の破壊」には含めない。

* LLM 応答内容の妥当性
* 回答の網羅性・正確性
* HTML / Markdown による差分
* 非決定性に起因する回答揺れ

これらは **F4 または F7 以降の責務**である。

---

## 9. Phase B（RAG QA CI）への接続方針（予告）

将来フェーズでは：

* 本 CI（v0.1.2）を **前提条件として固定**
* 新たに RAG QA 実行用 CI 設計を追加する

想定される対応：

* `Design_ci_e2e_rag_v0.1`（仮称）の新設
  または
* `Design_ci_e2e_v0.2` として段階拡張

いずれの場合も：

* **基盤確認 CI（本書 v0.1.2）は変更しない**
* RAG QA CI は **別設計として分離**する

---

## 10. まとめ

Design_ci_e2e_v0.1.2 は、

* **E2E 基盤が信用できる状態かどうかを CI で判断するための設計書**である
* RAG QA の品質評価を行うものではない
* F5 以降のフェーズに進むための
  **「基盤が壊れていないこと」の唯一の判断材料**を提供する

本 CI により、gov-llm-e2e-testkit は
**基盤確定フェーズから QA フェーズへ安全に遷移できる。**

---

