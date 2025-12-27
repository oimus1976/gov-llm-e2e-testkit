# Design_ci_e2e_v0.1.1  

gov-llm-e2e-testkit — **CI（GitHub Actions）設計書［基盤確認 CI］**  
最終更新: 2025-12-14  
バージョン: v0.1.1  
参照: PROJECT_GRAND_RULES v4.2 / Startup Template v3.1 / test_plan v0.1.1 / PROJECT_STATUS  

---

## 1. 目的（Purpose）

本書は gov-llm-e2e-testkit における  
**E2E テスト基盤（Foundation）の成立性を CI 上で確認するための設計**を定義する。

本 CI（v0.1.1）の主目的は以下に限定される：

- UI 送信（ChatPage.submit）が CI 環境で成立すること
- Answer Detection Layer（probe）が  
  **観測事実として応答を検知できる**こと
- submit–probe 相関結果を  
  **誤解のない意味論（PASS / WARN / INFO）**で可視化できること
- CI が「次のフェーズ（Phase B）に進めるか」を判断可能な状態を提供すること

**本 CI は、RAG QA の正確性・意味的妥当性・精度評価を検証しない。**

---

## 2. スコープ（Scope）

- 対象環境：**INTERNET 環境の GitHub Actions のみ**
- LGWAN 環境は CI 対象に含めない  
  （Startup Template v3.1 / env 設計の規定による）

本 CI は **E2E 基盤確認専用**であり、  
RAG QA（Basic / Advanced）は本スコープ外とする。

---

## 3. テスト体系上の位置づけと CI 実行範囲  

（test_plan v0.1.1 準拠）

本プロジェクトのテスト体系上の**論理的順序**は以下である：

1. Smoke Test  
2. Basic RAG Test  
3. Advanced RAG Test  

ただし **本 CI（v0.1.1）で実行されるのは以下のみ**である：

- **Smoke Test（必須）**

Basic / Advanced RAG Test は：

- test_plan 上では正式に定義されているが
- **CI 実行は意図的に Deferred（保留）**されている

理由：

- submit–probe 相関を含む E2E 基盤が  
  **十分に安定していることを最優先で確認するため**
- RAG QA は  
  **基盤が信用できることを前提条件とする上位フェーズ**であるため

---

## 4. ディレクトリ構造（CI 観点）

```text
tests/
  test_smoke_llm.py        # 基盤確認用 Smoke Test

data/
  rag/                    # RAG QA 用データ（CI v0.1.1 では未使用）
````

Basic / Advanced RAG 用 pytest / YAML は
**存在していても CI v0.1.1 では実行しない。**

これらは **Phase B（RAG QA CI）で再利用される前提**で保持される。

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

CI の実行ステップは以下で構成される：

1. リポジトリ checkout
2. Python セットアップ
3. 依存関係のインストール（pytest / playwright）
4. CI 用 `.env` 準備
5. Smoke Test 実行
6. submit–probe 相関サマリー生成
7. GitHub Actions Summary への結果出力
8. 失敗時のみ artifacts（logs/）を収集

---

## 7. e2e.yml

（E2E 基盤確認用 CI 定義・v0.1）

本章に記載する `e2e.yml` は、
**E2E 基盤（submit / probe / correlation）の成立性を確認するための CI 定義**である。

この YAML は以下を保証する：

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
# 現行 e2e.yml をそのまま掲載（実体と完全一致）
name: E2E Tests

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest


    steps:
      # -----------------------------------------------------
      # 1. Checkout
      # -----------------------------------------------------
      - name: Checkout repository
        uses: actions/checkout@v4

      # -----------------------------------------------------
      # 2. Python Setup
      # -----------------------------------------------------
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      # -----------------------------------------------------
      # 3. Install Dependencies
      #   - pytest, pytest-asyncio, pytest-playwright
      #   - playwright browsers (with-deps)
      # -----------------------------------------------------
      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install --with-deps

      # -----------------------------------------------------
      # 4. Prepare CI Environment
      #   - env_loader v0.2.3 は .env を読み込む
      #   - PROFILE=internet を指定し、env.yaml の internet プロファイルを使用する
      #   - QOMMONS_* は GitHub Secrets から注入（Secrets 未設定時は MissingSecretError で明示的に FAIL）
      # -----------------------------------------------------
      - name: Prepare CI .env
        run: |
          echo "PROFILE=internet" >> .env
          echo "QOMMONS_URL=https://qommons.ai" >> .env
          echo "QOMMONS_USERNAME=${{ secrets.QOMMONS_USERNAME }}" >> .env
          echo "QOMMONS_PASSWORD=${{ secrets.QOMMONS_PASSWORD }}" >> .env

      # -----------------------------------------------------
      # 5. Add src to PYTHONPATH
      # -----------------------------------------------------
      - name: Add src to PYTHONPATH
        run: echo "PYTHONPATH=$PYTHONPATH:$(pwd)/src" >> $GITHUB_ENV

      # -----------------------------------------------------
      # 6. Smoke Test（必ず1件実行 → exit code 5 対策）
      # -----------------------------------------------------
      - name: Run Smoke Test
        run: |
          mkdir -p logs
          export PROBE_CAPTURE_SECONDS=${{ matrix.capture_seconds }}
          pytest tests/test_smoke_llm.py -vv --disable-warnings
      
      - name: Write correlation summary (from summary.json)
        shell: bash
        run: |
          set -euo pipefail

          SUMMARY_JSON="$(ls -td logs/xhr_probe_* | head -n 1)/summary.json"
          echo "Using summary: $SUMMARY_JSON"

          CORR_STATE=$(python -c "import json;print(json.load(open('$SUMMARY_JSON')).get('correlation_state','Unassessed'))")
          CHAT_ID=$(python -c "import json;print(json.load(open('$SUMMARY_JSON')).get('chat_id','(n/a)'))")
          SUBMIT_ID=$(python -c "import json;print(json.load(open('$SUMMARY_JSON')).get('submit_id','(n/a)'))")

          if [ \"$CORR_STATE\" = \"Established\" ]; then
            CI_RESULT=\"PASS\"
          elif [ \"$CORR_STATE\" = \"Not Established\" ]; then
            CI_RESULT=\"WARN\"
          else
            CI_RESULT=\"INFO\"
          fi

          sed \
            -e 's|${SUBMIT_ID}|'"$SUBMIT_ID"'|g' \
            -e 's|${CHAT_ID}|'"$CHAT_ID"'|g' \
            -e 's|${CORRELATION_STATE}|'"$CORR_STATE"'|g' \
            -e 's|${CI_RESULT}|'"$CI_RESULT"'|g' \
            docs/ci/summary_template_submit_probe_v0.1.ja.md \
            >> "$GITHUB_STEP_SUMMARY"


      # Smoke Test:
      # - guarantees UI submit works
      # - guarantees probe observes correlation_state
      # - does NOT validate semantic correctness

      # NOTE:
      # RAG tests (ask / semantic evaluation) are intentionally deferred.
      # They will be re-enabled after submit–probe correlation stabilizes.


      # -----------------------------------------------------
      # 9. Artifact Upload（失敗時のみ）
      # -----------------------------------------------------
      - name: Upload artifacts (failure only)
        if: ${{ failure() }}
        uses: actions/upload-artifact@v4
        with:
          name: test-failure-evidence
          path: logs/

```

---

## 8. Phase B（RAG QA CI）への接続方針（予告）

Phase B では：

* 本 CI（v0.1.1）を **前提条件として固定**
* 新たに RAG QA 実行用 CI 設計を追加する

想定される対応：

* `Design_ci_e2e_rag_v0.1`（仮称）の新設
  または
* `Design_ci_e2e_v0.2` として段階拡張

いずれの場合も：

* **基盤確認 CI（本書 v0.1.1）は変更しない**
* RAG QA CI は **別設計として分離**する

---

## 9. まとめ

Design_ci_e2e_v0.1.1 は、

* **E2E 基盤が信用できる状態かどうかを CI で判断するための設計書**である
* RAG QA の品質評価を行うものではない
* Phase B に進むための「通行証」を提供する役割を担う

本 CI により、
gov-llm-e2e-testkit は
**基盤確定フェーズから QA フェーズへ安全に遷移できる。**

---
