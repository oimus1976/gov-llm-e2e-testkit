# CHANGELOG — gov-llm-e2e-testkit

全ドキュメント・設計書・仕様変更の履歴を記録する公式 CHANGELOG です。  
本プロジェクトは Keep a Changelog に準拠し、バージョンは日付ベース＋プロジェクト内バージョンで管理します。

---

## v0.2.0 (2025-12-09)

### Added

- `docs/Debugging_Principles_v0.1.md` を追加  
  - E2E / Python / SPA / CI に共通するデバッグ原則を体系化。

### Changed

- E2Eテスト基盤を Playwright Async → Sync へ移行し、安定動作を実現。
  - LoginPage（Sync版）を正式採用  
  - conftest.py を Sync Playwright に書き換え  
  - no_wait_after=True を標準化  
  - headless=False を推奨デバッグモードに設定

### Fixed

- Async Playwright が pytest-asyncio(strict) と競合して停止する問題を解消。  
- SPA ログインが navigation せずタイムアウトする問題を Sync版で安定回避。  
- Smoke Test が安定して PASS することを確認。

### Notes

- 次版では ChatPage Sync 実装と RAG Basic Sync テストを予定。  
- Debugging_Principles は v0.2 → v0.3 系でさらに強化（逆引き辞典・フローチャート）。

---

## v0.1.17 (2025-12-08)
### pytest Execution Layer v0.2
- ADD: conftest.py に `case_dirs` fixture を追加し、テストケース単位で evidence_dir を生成
- ADD: Smoke / Basic / Advanced の全テストを v0.2 構造に全面改修
- ADD: PageObject v0.2 の evidence_dir 機能と統合
- IMPROVE: test_smoke_llm を v0.2 仕様へ再設計（LoginPage / ChatPage v0.2 準拠）
- IMPROVE: basic_cases / advanced_cases のテスト構造を統一
- IMPROVE: advanced の multi-turn 処理を PageObject API に準拠する形に統一
- ADD: pytest 設計書の最新版 `Design_pytest_v0.2.md` を追加
- IMPROVE: latest エントリーポイント `Design_pytest.md` を統一フォーマットへ刷新

### Documentation
- IMPROVE: Design_BasePage.md / Design_ChatPage.md / Design_pytest.md を統一スタイルへ整理

---

## v0.1.16 (2025-12-09)

### Added
- Design_BasePage.md（最新版を参照する固定ファイル）を追加
- 設計書バージョニング方式（全バージョン保持＋latest ラッパー方式）を正式採用

### Changed
- Design_BasePage_v0.2.md を最新仕様として確定し、v0.1 を supersede
- PROJECT_STATUS.md に設計書管理ポリシーを反映

### Notes
- 今後の設計書（LoginPage / ChatPage / Playwright / CI / Logging など）も同じ方式に統一予定。

---

## v0.1.15 (2025-12-09)

### Added

* `test_smoke_llm.py`、`test_rag_basic_v0.1.py`、`test_rag_advanced_v0.1.py` に
  **log_writer v0.1 を正式統合**
* multi-turn advanced ログ仕様に基づく詳細ログ（details）生成を追加

### Changed

* `tests/conftest.py` を v0.1.15 仕様に書き換え（env_config tuple 化・timeout 正常化）
* Basic / Advanced 判定ロジックを設計書の通り統一

### Notes

* これにより E2E testkit の全レイヤが一貫し、
  CI artifacts も公式仕様どおりに整う v0.1 系の最終安定版となった。

---

## **[v0.1.14] - 2025-12-08**

### Added

- `log_writer.py v0.1` を実装

  - Design_log_writer_v0.1 の仕様に基づき

    - frontmatter 生成
    - Markdown セクション生成
    - Smoke / Basic / Advanced 切替
    - assets ディレクトリ生成
      をすべて実装。

### Changed

- PROJECT_STATUS を v0.1.14 に更新。
  - Next Action を「pytest への log_writer 統合」に変更。

### Notes

- これにより **ログ生成の最終要素が揃い、自動テスト基盤の全レイヤが接続可能となった**。

---

## [v0.1.13] - 2025-12-07

### Added

- Design_logging_v0.1.md を新規追加（標準ログフォーマットを定義）
  - frontmatter・基本構造・Basic/Advanced 差分・スクショ保存規約を含む

### Changed

- PROJECT_STATUS を v0.1.13 に更新  
  - logging v0.1 の追加を反映  
  - Next Action を「logger_v0.1 設計」に変更

---

## [v0.1.12] - 2025-12-07

### Added
- Responsibility_Map_v0.1.md を新規追加（全レイヤの責務境界を正式定義）
- Design_pytest_env_v0.1.md を追加（pytest Execution Layer の正式設計）
- conftest.py v0.1 の設計仕様を正式確立（browser/context/page生成・timeout適用・env_loader連携）

### Changed
- PROJECT_STATUS を v0.1.12 に更新  
  - Responsibility Map / pytest Execution Layer 追加を反映  
  - Next Action を「ロギング仕様 v0.1」に変更

---

## [v0.1.11] - 2025-12-07

### Added
- env_loader.py v0.1 を追加（env.yaml の正式ローダー）
- BasePage / pytest への env 連携を統一

### Changed
- PROJECT_STATUS を v0.1.11 に更新  
  - env.yaml ローダー実装完了を反映  
  - Next Action を「ロギング仕様 v0.1」策定に変更

---

## [v0.1.10] - 2025-12-07

### Added

- Design_env_v0.1.md（INTERNET/LGWAN 切替仕様の正式版）を追加

### Changed

- PROJECT_STATUS を v0.1.10 に更新  
  - env.yaml 設計の完了を反映  
  - Next Action を「env.yaml（実ファイル）生成」に変更

### Notes

- 本バージョンにより、INTERNET・LGWAN の環境統合レイヤが完成。  
  gov-llm-e2e-testkit は次に env.yaml 実体生成フェーズへ移行する。


---

## [v0.1.9] - 2025-12-07

### Added

- **Design_ci_e2e_v0.1.md** を追加（INTERNET向け CI 設計の正式版）
- .github/workflows/e2e.yml の仕様を確定

### Changed

- PROJECT_STATUS を v0.1.9 に更新  
  - Next Action を「CI（e2e.yml）v0.1 の実装」に変更  

### Notes

- 本版により、gov-llm-e2e-testkit の E2E 自動化パイプラインの設計が完成。  
  次は CI 実ファイル e2e.yml の GitHub 反映へ進む。

---

## [v0.1.8] - 2025-12-07

### Added

- **RAG Basic / Advanced pytest implementation v0.1** を追加  
  - YAML → pytest のマッピング仕様（Design_RAG_Test_v0.1）に準拠  
  - tests/rag/test_rag_basic_v0.1.py  
  - tests/rag/test_rag_advanced_v0.1.py  

### Changed

- PROJECT_STATUS.md を v0.1.8 に更新  
  - Next Action を CI（e2e.yml）v0.1 設計へ変更  
  - rag_basic / rag_advanced の物理フォルダを廃止し、data/rag/ 統合構造へ整合  

### Notes

- v0.1.8 により RAG テストの **データ → 実装 → pytest 結合** が完了。  
  CI レイヤに進むための準備が整った。

---

## [v0.1.7] - 2025-12-07

### Added

- **test_plan_v0.1** を新規追加  
  - Smoke / Basic RAG / Advanced RAG の3層テスト体系を正式策定  
  - basic/advanced YAML のスキーマを定義  
  - INTERNET/LGWAN 実行ポリシーを明文化  
  - CI（e2e.yml）の基本方針を規定  
  - UI変動／モデル更新時の再テスト手順を定義  
  → テスト基盤の“最上位仕様”が確立された

### Changed

- PROJECT_STATUS.md を v0.1.7 に更新  
  - test_plan 完成を反映  
  - Next Action を「RAG YAML スキーマ実体化」に変更  
  - Backlog を整理

### Notes

- v0.1.7 は **E2Eテスト体系の全体像が初めて統合された重要マイルストーン** であり、  
  RAG 設計・CI 設計へ進むための基盤が整った。

---

## [v0.1.6] - 2025-12-07

### Added

- **Design_LoginPage_v0.1** を新規追加  
  - username / password / login ボタンのロケータ設計  
  - login() / wait_for_login_success() など高レベルAPIを定義  
  - BasePage / Locator_Guide_v0.2 に基づく UI変動耐性を確保  
  - LGWAN timeout 対応を明示

### Changed

- PROJECT_STATUS.md を **v0.1.6** に更新  
  - ChatPage / LoginPage 設計フェーズ完了を反映  
  - Next Action を “BasePage 実装” に更新  
  - Backlog と必須資料リストを整理

### Notes

- v0.1.6 により主要 Page Object（BasePage + ChatPage + LoginPage）の  
  **設計段階がすべて完了し、実装フェーズへ移行可能**となった。

---

## [v0.1.5] - 2025-12-07

### Added

- **Design_BasePage_v0.1** を新規追加  
  - Page Object 基底クラスの責務・構造を定義  
  - locator factory / safe actions / LGWAN timeout / loading wait など  
    共通インターフェースの仕様を確立  
  - Locator_Guide_v0.2 と Design_playwright_v0.1 に正式準拠

### Changed

- PROJECT_STATUS.md を v0.1.5 に更新  
  - BasePage 設計書の完成を反映  
  - Next Action を「ChatPage 設計書 v0.1 作成」に更新  
  - 参照文書体系を最新化

### Notes

- 本バージョン v0.1.5 により、Page Object 層の“基底構造”が確立され、  
  ChatPage / LoginPage / Smoke Test へ進むための基盤が完成した。

---

## [v0.1.4] - 2025-12-07

### Added

- **ChatGPT Startup Workflow v3.0** を新規追加  
  - PROJECT_GRAND_RULES v2.0 / Startup Template v3.0 と整合  
  - /start 時のブートシーケンスを拡張（参照文書同期・Next Action 単一検証・LGWAN判定など）  
  - 作業フェーズ（設計→実装→テスト→文書更新）を体系化  
  - UI変動・モデル更新の検知フローを追加  
  - LGWAN 実行モード（オフライン動作）の特別ルールを定義  

### Changed

- PROJECT_STATUS.md を **v0.1.4** に更新  
  - Startup Workflow v3.0 の導入を反映  
  - 現在地／Backlog／Next Action を最新化  
  - 必須資料に Workflow v3.0 を追加  
- プロジェクト内部レイヤを再整理  
  - 「設計（Design）／運転（Startup Template）／行動制御（Workflow）／実行（STATUS）」の4階層構造を明確化  

### Notes

- 本バージョン v0.1.4 は、  
  Startup Template（運転層）に加えて **Startup Workflow（行動制御層）が完成した最初の版** であり、  
  プロジェクトが「設計駆動で破綻しない統制構造」を正式に獲得した重要バージョンである。

---

## [v0.1.3] - 2025-12-07

### Added

- **Startup Template v3.0（運転層統合版）** を新規作成  
  - PROJECT_GRAND_RULES v3.0 と整合した行動規範を統合  
  - Design_playwright_v0.1 / Locator_Guide_v0.2 への準拠を明文化  
  - /start 時のブートシーケンスを再定義  
- PROJECT_STATUS.md を v0.1.3 に更新  
  - Startup Template v3.0 の運用開始を反映  
  - 参照文書・Backlog・Next Action を最新化

### Changed

- 参照文書体系を最新版に整合  
  - Startup Template → v3.0 に更新  
  - STATUS / GRAND_RULES / Locator_Guide との依存関係を整理  
- STATUS の「プロジェクト目的」「現在地」「未完了タスク」を刷新  
- Next Action を **BasePage（Page Object 基底クラス）の作成**として再設定

### Notes

- 本バージョン v0.1.3 は、プロジェクトの「運転層（Startup Template）」が  
  統治層（GRAND_RULES）と完全整合した、  
  **初のフル統合バージョン**である。

---

## [v0.1.2] - 2025-12-07

### Added

- **Locator_Guide_v0.2.md（UI識別規範）** を新規作成  
  - ロケータ優先順位を明確化（Role → Label → aria-label → data-testid → CSS）  
  - LGWAN 遅延を考慮した timeout 推奨値を追加  
  - 文言変動に強くする fallback パターンを追加  
- PROJECT_STATUS.md を v0.1.2 に更新  
  - UI識別規範作成完了を反映  
  - Next Action を BasePage 作成へ変更  
- Startup Template v1.1 の「参照文書」に Locator_Guide_v0.2 を追加

### Changed

- STATUS の「未完了タスク」「完了タスク」を最新版に更新  
- プロジェクト参照文書体系を整備

---

## [v0.1.1] - 2025-12-07

### Changed

- プロジェクト名を **qommons-ai-auto-test → gov-llm-e2e-testkit** に正式変更  
- Startup Template / PROJECT_STATUS / 各設計書の名称を一括更新  
- ディレクトリ標準構成のプロジェクト名を差し替え

---

## [v0.1.0] - 2025-12-07

### Added

- プロジェクト初期セットアップ  
  - Startup Template v1.1（行動規範、設計規範、運用ルール）  
  - PROJECT_STATUS v0.1.0（最初の進行管理表）  
  - Design_playwright_v0.1.md（Playwrightの基盤設計書）
- 基本ディレクトリ構成の定義  
  - design/ tests/ data/ logs/ .github/workflows/

---

## 運用方針

- すべての更新は PENTA による検討・整理後に実施する  
- 設計書・ルール・STATUS の変更は必ず CHANGELOG に追記する  
- バージョン番号は **プロジェクト全体の進行管理番号** であり、コードとは独立
