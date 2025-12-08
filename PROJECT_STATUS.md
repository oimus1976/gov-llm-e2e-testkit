# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.11  
ステータス: env.yaml ローダー実装完了

---

## 1. プロジェクト概要

本プロジェクトは、自治体向け LLM サービスを対象とした  
Python + Playwright ベースの E2E 自動テスト基盤を構築するものである。

以下の 4 層構造によって統制される：

- **統治層**：PROJECT_GRAND_RULES  
- **運転層**：Startup Template  
- **行動制御層**：Startup Workflow  
- **実行層**：本 PROJECT_STATUS  

本 STATUS はプロジェクトの「唯一の現在地」を定義する。

---

## 2. 現在地（Where we are now）

- test_plan_v0.1 完成  
- BasePage / ChatPage / LoginPage 実装完成  
- Smoke Test 完成  
- RAG YAML v0.1（basic/advanced）完成  
- RAG pytest 実装 v0.1 完成  
- CI（e2e.yml）v0.1 設計完了  
- env.yaml v0.1 設計完了
- **env_loader.py v0.1 実装完了（← NEW）**  
- BasePage / pytest での env 読み込み経路が統一された  
- INTERNET / LGWAN の環境抽象が動作可能段階に到達

現時点で、INTERNET / LGWAN の2環境を統合的に扱う基盤設計が完了した。

---

## 3. 完了した成果（Done）

- Locator_Guide_v0.2  
- Design_playwright_v0.1  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- BasePage.py / ChatPage.py / LoginPage.py  
- test_smoke_llm.py  
- RAG YAML v0.1  
- RAG pytest v0.1  
- Design_ci_e2e_v0.1  
- Design_env_v0.1（← NEW）
- **env_loader.py v0.1 ← NEW** 
- **BasePage 連携コード（timeout/認証情報の注入）← NEW**

---

## 4. 未完了タスク（Backlog）

### 設計関連
- ロギング仕様（logs/YYYYMMDD/case.md）  
- env.yaml v0.2（retry_policy / multi-profile 拡張）

### 実装関連
- pytest strict/lenient モード（v0.2）  
- Advanced RAG の深層比較（v0.2）

---

## 5. リスク・注意点

- env.yaml はプロジェクトの唯一の環境抽象 → 削除禁止  
- LGWAN の timeout 値は INTERNET の 4〜6 倍必要  
- Secrets の扱いミスによる CI 事故  
- Smoke / Basic / Advanced の依存順序を壊さないこと  
- timeout が短すぎると LGWAN 実行が必ず失敗する

---

## 6. Next Action（最優先・常に1つ）

### ▶ logs/YYYYMMDD/case.md のロギング仕様（v0.1）を策定する

---

## 7. 必須資料（Dependencies）

- Design_env_v0.1  
- Design_ci_e2e_v0.1  
- Design_playwright_v0.1  
- test_plan_v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- 最新の単体・RAG・Smoke テスト実装

---

## 8. 更新履歴

- **v0.1.10（2025-12-07）**  
  - env.yaml v0.1 設計完了を反映  
  - Next Action を env.yaml 実体生成へ更新  
  - Design_env_v0.1 を Done に追加  
- **v0.1.9（2025-12-07）**  
  - CI 設計書追加  
