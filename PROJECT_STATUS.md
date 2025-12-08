# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-09  
バージョン: **v0.1.16**  
ステータス: **PageObject v0.2 設計開始（証跡収集基盤の導入準備）**

---

## 1. プロジェクト概要

本プロジェクトは、自治体向け LLM サービス（特に「チャット型生成 AI」）に対して、  
**信頼性の高い End-to-End 自動テスト基盤を OSS として提供する**ことを目的としている。

アーキテクチャは以下の三層構造で設計されている：

1. **Playwright Layer（UI 自動操作レイヤー）**  
2. **PageObject Layer（UI モデル化レイヤー）**  
3. **pytest Application Test Layer（要件検証・判定・ログ生成）**

すべての作業は次の規定に従って行われる：

- [PROJECT_GRAND_RULES_v2.0.md](docs/PROJECT_GRAND_RULES_v2.0.md)  
- [ChatGPT_Startup_Workflow_v3.0.md](docs/ChatGPT_Startup_Workflow_v3.0.md)  
- OSS 標準のドキュメントバージョニングポリシー（v0.1.16 で正式採用）

---

## 2. 現在地（Where we are now）

- PageObject（BasePage / LoginPage / ChatPage）v0.1 完成  
- env.yaml / env_loader 実装済  
- pytest Execution Layer v0.1 完成  
- Smoke / Basic / Advanced の E2E テスト完成  
- CI（e2e.yml）v0.1 完成  
- Logging Spec（Design_logging_v0.1）整備済  
- log_writer.py v0.1 完成  
- **Smoke / Basic / Advanced pytest に log_writer v0.1 を統合（v0.1.15）**  
- **PageObject v0.2（証跡収集機能）の設計フェーズに突入 ← NEW**

E2E テスト基盤として実行可能な状態に到達し、  
次フェーズで「UI 失敗時の証跡収集」が実装される段階である。

---

## 3. 完了した成果（Done）

### 🎯 設計書（Design Documents）

- [Locator_Guide_v0.2.md](docs/Locator_Guide_v0.2.md)
- [Design_playwright_v0.1.md](docs/Design_playwright_v0.1.md)
- [Design_BasePage_v0.1.md](docs/Design_BasePage_v0.1.md)
- [Design_BasePage_v0.2.md](docs/Design_BasePage_v0.2.md) ← NEW（v0.1 supersede）
- [Design_BasePage.md](docs/Design_BasePage.md) ← latest ラッパー
- [Design_LoginPage_v0.1.md](docs/Design_LoginPage_v0.1.md)
- [Design_ChatPage_v0.1.md](docs/Design_ChatPage_v0.1.md)
- [Design_ci_e2e_v0.1.md](docs/Design_ci_e2e_v0.1.md)
- [Design_env_v0.1.md](docs/Design_env_v0.1.md)
- [Design_pytest_env_v0.1.md](docs/Design_pytest_env_v0.1.md)
- [Design_logging_v0.1.md](docs/Design_logging_v0.1.md)
- [Design_log_writer_v0.1.md](docs/Design_log_writer_v0.1.md)

### 🎯 実装（Implementation）

- PageObject（BasePage / LoginPage / ChatPage）v0.1
- env_loader.py / env.yaml  
- conftest.py v0.1.15（log_writer 統合に対応）
- log_writer.py v0.1
- 全 E2E テスト（Smoke / Basic / Advanced）

### 🎯 運用（Project Rules / Architecture）

- [PROJECT_GRAND_RULES_v2.0.md](docs/PROJECT_GRAND_RULES_v2.0.md)
- 設計書バージョニング方式（全バージョン保持＋latest ラッパー）を正式採用 ← NEW

---

## 4. 未完了タスク（Backlog）

### 4.1 設計関連

- LoginPage v0.2（証跡連携仕様）
- ChatPage v0.2（ask-error evidence）
- Design_playwright_v0.2（DOM dump 処理の標準化）
- log_writer v0.2（JSON ログ／差分ハイライト対応）
- test_plan v0.2（strict/lenient 判定導入）
- env.yaml v0.2（retry_policy / CI 設定強化）

### 4.2 実装関連

- PageObject v0.2 実装（BasePage / LoginPage / ChatPage）
- pytest v0.2 実装（evidence_dir パス伝搬）
- CI artifacts 再構成（DOM + screenshot の bundle 化）
- Advanced deep comparison helper の導入

---

## 5. リスク・注意点

- LGWAN 環境で生成される logs/assets/* の扱いには厳格な運用が必要  
- Markdown ログ形式はフォーマット破壊に弱いため log_writer の改修時は要注意  
- PageObject v0.2 により例外フローが変わるため、pytest 連携の追加設計が必要  
- Versioning Policy（設計書の多重管理方式）の定着が重要

---

## 6. Next Action（常に1つ）

### ▶ **BasePage v0.2 の実装開始（証跡収集基盤の導入 / safe_click / safe_fill / collect_evidence）**

理由：  
- PageObject v0.2 は E2E 自動テスト基盤における「UI 障害解析」の中核である。  
- これを導入することで、UI の不具合・ネットワーク遅延・ポップアップなどの  
  **“原因が分からない FAIL” を大幅に減らせる。**
- 現行 v0.1 → v0.2 の移行はページ遷移や locator 安定化にも寄与し、  
  将来の v1.0 安定版に向けた基盤整備になる。

---

## 7. Dependencies（参照ドキュメント / リンク）

- [Design_BasePage_v0.2.md](docs/Design_BasePage_v0.2.md) ← 最新仕様  
- [Design_LoginPage_v0.1.md](docs/Design_LoginPage_v0.1.md)  
- [Design_ChatPage_v0.1.md](docs/Design_ChatPage_v0.1.md)  
- [Design_playwright_v0.1.md](docs/Design_playwright_v0.1.md)  
- [Design_logging_v0.1.md](docs/Design_logging_v0.1.md)  
- [Design_log_writer_v0.1.md](docs/Design_log_writer_v0.1.md)  
- [PROJECT_GRAND_RULES_v2.0.md](docs/PROJECT_GRAND_RULES_v2.0.md)

---

## 8. 更新履歴

### **v0.1.16（2025-12-09） ← NEW**
- 設計書バージョニング方式（全バージョン保持＋latest ラッパー）を正式採用  
- Design_BasePage_v0.2.md を正式採用し v0.1 を supersede  
- Design_BasePage.md（latest）を追加  
- PageObject v0.2 設計フェーズへ移行  

### **v0.1.15（2025-12-09）**
- Smoke / Basic / Advanced pytest に log_writer v0.1 を統合  
- conftest.py 更新（env_config tuple 化）  

（省略）

---

