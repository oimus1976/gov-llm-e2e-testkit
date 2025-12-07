# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.3  
ステータス: Startup Template v3.0 反映済（運転層刷新）

---

## 1. プロジェクト概要

本プロジェクトは **自治体向け LLLM サービス（Qommons.AI を含む）を対象とした  
E2E 自動テスト基盤（Python + Playwright）** を構築する。

設計書（Design）、UI識別規範（Locator Guide）、STATUS、CHANGELOG を軸に  
INTERNET / LGWAN 両環境で再現性の高い QA テストを長期運用できる仕組みを作ることが目的。

本ステータスは **プロジェクト階層の第3層＝実行レイヤ** として、  
現時点の進捗・次のタスク・未決課題を記録する唯一の正本である。

---

## 2. 現在地（Where we are now）

- **Startup Template v3.0（統合運転層）を正式採用**  
- PROJECT_GRAND_RULES v3.0（統治層）と整合  
- Design_playwright_v0.1（Playwright設計）を保有  
- Locator_Guide_v0.2（UI識別規範）を設計・格納済  
- gov-llm-e2e-testkit の基盤文書体系がほぼ出揃い、  
  Page Object 実装フェーズに進める状態となった

---

## 3. 完了した成果（Done）

- プロジェクト名変更（qommons-ai-auto-test → gov-llm-e2e-testkit）
- Startup Template v1.1 → v3.0（運転層の総合刷新）
- PROJECT_GRAND_RULES v3.0 を制定・採択
- Design_playwright_v0.1 の生成・格納
- Locator_Guide_v0.2（UI識別規範）を生成・格納
- CHANGELOG 初版（v0.1.0〜v0.1.2）作成完了
- STATUS v0.1.2 → v0.1.3（本更新）

---

## 4. 未完了タスク（Backlog）

- **Page Object 標準インターフェース（BasePage）作成** ← 最優先
- ChatPage / LoginPage の実装  
- RAG テストデータ（YAML/JSON スキーマ）設計  
- 初回 Smoke Test（test_smoke_llm.py）作成  
- CI（e2e.yml）初版の設計（pytest + Playwright）  
- INTERNET / LGWAN 実行切替ロジックの整理（config/env.yaml）  
- Advanced RAG Test 用 DSL/シナリオ定義  
- test_plan（RAGテスト方針 v0.1）作成

---

## 5. リスク・注意点（Risks）

- LLM UI の変更に伴う Page Object 崩壊リスク  
- LGWAN の低速回線によるタイムアウト増大  
- Qommons.AI 側 DOM 構造の変動  
- YAML データ（expected_keywords）の粒度過不足  
- テストログ（Markdown/スクショ）容量増大  
- CI（GitHub Actions）でのブラウザインストール不備  
- Startup Template / GR と STATUS の不整合が進むリスク

---

## 6. Next Action（最優先タスク：常に1つ）

### ▶ **Page Object 標準インターフェース（BasePage）を design/ に作成する**

**理由：**

- Locator_Guide と Design_playwright の仕様をコードに落とし込む最初の要  
- ChatPage / LoginPage / Smoke Test すべての土台  
- UI変動時の影響範囲を最小にする構造を整えるため

---

## 7. 必須資料（Files / Specs）

- PROJECT_GRAND_RULES v3.0  
- Startup Template v3.0（運転層）  
- Design_playwright_v0.1.md  
- Locator_Guide_v0.2.md  
- CHANGELOG.md  
- （未作成）test_plan  
- （未作成）e2e.yml（CI初版）

---

## 8. PENTA 推奨ポイント

- BasePage 設計・メソッド構成  
- RAG テストデータ設計（YAML/JSON）  
- CI の timeout / retry 戦略  
- LGWAN 実行手順の明文化  
- Breaking Change（互換性破壊）の扱い判断

---

## 9. 更新履歴（STATUS version history）

- **v0.1.3（2025-12-07）**  
  - Startup Template v3.0 採用に伴い、STATUS を全面更新  
  - 参照文書・Backlog・Next Action を最新化  
- **v0.1.2（2025-12-07）**  
  - Locator_Guide_v0.2 完成を反映  
- **v0.1.1（2025-12-07）**  
  - プロジェクト名変更  
- **v0.1.0（2025-12-07）**  
  - 初期版生成
