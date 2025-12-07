# Design_ci_e2e_v0.1  

gov-llm-e2e-testkit — CI（GitHub Actions）設計書  
最終更新: 2025-12-07  
バージョン: v0.1  
参照: PROJECT_GRAND_RULES v2.0 / Startup Template v3.0 / test_plan v0.1 / PROJECT_STATUS v0.1.8

---

## 1. 目的（Purpose）

本書は gov-llm-e2e-testkit における  
**CI（GitHub Actions / INTERNET 専用）で実行する E2E テストの正式設計**を定義する。

目的：

- Smoke → Basic → Advanced の強制順で pytest を実行  
- Playwright（Python/async）ブラウザを CI 上でセットアップ  
- YAML → pytest 実装（v0.1）の自動実行  
- exit code 5（テスト件数ゼロ）を回避  
- LGWAN 環境を CI 対象に含めない（INTERNET 専用）  

---

## 2. スコープ（Scope）

INTERNET 環境の GitHub Actions のみを対象とする。  
LGWAN 環境は CI に含めない（Startup Template v3.0 の規則）。

---

## 3. 実行順序（test_plan v0.1 準拠）

1. **Smoke Test**  
2. **Basic RAG Test**（成功時のみ実行）  
3. **Advanced RAG Test**（成功時のみ実行）

下位テストは上位テストの成功を前提とする。

---

## 4. ディレクトリ構造

```text
tests/
test_smoke_llm.py
rag/
test_rag_basic_v0.1.py
test_rag_advanced_v0.1.py

data/
rag/
basic_cases.yaml
advanced_cases.yaml
```

---

## 5. secrets（機密情報）管理方針

GitHub Secrets を用いて pytest に渡す：

- `QOMMONS_URL`
- `QOMMONS_USERNAME`
- `QOMMONS_PASSWORD`

env.yaml の上書きは行わない。  
pytest 内で環境変数経由で参照する。

---

## 6. CI 実行ステップ（概要）

1. リポジトリ checkout  
2. Python セットアップ  
3. 必要パッケージ install  
4. Playwright browser install  
5. pytest 実行（Smoke → Basic → Advanced）  
6. 失敗時のみ logs/ を artifacts として収集  

---

## 7. 完全版 e2e.yml（v0.1）

```yaml
name: E2E Tests

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install

      - name: Run Smoke Test
        run: |
          pytest tests/test_smoke_llm.py -q --disable-warnings

      - name: Run Basic RAG Test
        if: ${{ success() }}
        run: |
          pytest tests/rag/test_rag_basic_v0.1.py -q --disable-warnings

      - name: Run Advanced RAG Test
        if: ${{ success() }}
        run: |
          pytest tests/rag/test_rag_advanced_v0.1.py -q --disable-warnings

      - name: Upload artifacts (failure only)
        if: ${{ failure() }}
        uses: actions/upload-artifact@v4
        with:
          name: test-failure-screenshots
          path: logs/
```

---

## 8. 今後の拡張（v0.2 予定）

- strict / lenient モード対応
- pytest-xdist による並列最適化（LGWAN 非対象）
- HTML レポート生成（要セキュリティ検討）
- YAML の階層型比較（Advanced 強化）

---

## 9. まとめ

本設計書 v0.1 は、
**設計書 → pytest 実装 → CI 実行のフルパイプラインの最小実働版**である。

これにより gov-llm-e2e-testkit は
E2E 全自動テスト基盤へ移行できる基本フレームを獲得した。

---
