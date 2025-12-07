# CHANGELOG — gov-llm-e2e-testkit

全ドキュメント・設計書・仕様変更の履歴を記録する公式 CHANGELOG です。  
本プロジェクトは Keep a Changelog に準拠し、バージョンは日付ベース＋プロジェクト内バージョンで管理します。

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
