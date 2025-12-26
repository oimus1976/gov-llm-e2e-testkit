# gov-llm-e2e-testkit
自治体向け LLM サービスの品質検証を目的とした E2E 自動テスト基盤（Python + Playwright）。 条例ナレッジ QA の自動検証や LGWAN 環境での運用を想定した非公式テストキットです。

## プロジェクト構成（クイックガイド）

本リポジトリは、自治体向け LLM サービスを対象とした
E2E テスト・実行検証用の実験的基盤です。

フェーズ（F4 / F8 等）によって、実行の入口や役割が異なります。

### F8（回答素材収集フェーズ）の主な構成

- **コア（正式・非実行）**
  - `src/execution/f8_orchestrator.py`
    - F8 フェーズの正式 orchestrator
    - 単独では実行できず、ドライバから呼び出されます

- **実行入口（手動検証用）**
  - `scripts/run_f8_set1_manual.py`
    - F8 の runtime 検証用スクリプト
    - Playwright が動作する環境で人が直接実行します

- **設計ドキュメント**
  - `docs/design/Design_F8_v0.3.1_runner.md`
    - F8 runner / orchestrator の最新・正式設計

詳細な実行フローや役割分担については、
`docs/operation/` 配下のドキュメントを参照してください。
