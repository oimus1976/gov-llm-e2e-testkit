# CHANGELOG — gov-llm-e2e-testkit

全ドキュメント・設計書・仕様変更の履歴を記録する公式 CHANGELOG です。  
本プロジェクトは Keep a Changelog に準拠し、バージョンは日付ベース＋プロジェクト内バージョンで管理します。

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
