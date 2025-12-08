# PROJECT_STATUS — gov-llm-e2e-testkit
最終更新: 2025-12-07  
バージョン: v0.1.12  
ステータス: pytest Execution Layer（conftest.py）設計完了・責務マップ追加

---

## 1. プロジェクト概要

本プロジェクトは自治体向け LLM サービスを対象とした  
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
- PageObject（BasePage / ChatPage / LoginPage）実装済み  
- Smoke Test 完成  
- RAG YAML（basic/advanced）v0.1 完成  
- RAG pytest 実装 v0.1 完成  
- CI（e2e.yml）v0.1 完成  
- env.yaml v0.1 完成  
- env_loader.py v0.1 完成  
- **Responsibility_Map_v0.1.md 新規追加（← NEW）**  
- **Design_pytest_env_v0.1（pytest Execution Layer の正式設計書）追加（← NEW）**  
- **conftest.py v0.1 の設計仕様が正式確立（← NEW）**

INTERNET / LGWAN の環境抽象、  
PageObject 層、RAG テスト、pytest 実行基盤、CI すべてが  
「設計書ドリブンで一貫した構造」を獲得した段階。

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
- Design_env_v0.1  
- env_loader.py v0.1  
- BasePage ← env連携コード  
- **Responsibility_Map_v0.1.md ← NEW**  
- **Design_pytest_env_v0.1.md ← NEW**  
- **conftest.py v0.1（Execution Layer の正式仕様）← NEW**

---

## 4. 未完了タスク（Backlog）

### 設計関連
- ロギング仕様（logs/YYYYMMDD/case.md）の正式設計書 v0.1  
- env.yaml v0.2（retry_policy / multi-profile 拡張）  
- pytest strict/lenient モード設計 v0.2  
- Advanced RAG Test の深層比較 v0.2

### 実装関連
- ログ生成ユーティリティ  
- strict/lenient mode の pytest 実装  
- LGWAN 専用 run-script（手動運用）

---

## 5. リスク・注意点

- env.yaml の削除禁止（環境抽象の唯一のファイル）  
- Smoke / Basic / Advanced の依存順序を維持すること  
- LGWAN の timeout は INTERNET の 4〜6 倍必要  
- CI は INTERNET 専用。LGWAN 試験は手動運用  
- conftest.py の責務境界を崩さないこと（Design_pytest_env_v0.1 準拠）

---

## 6. Next Action（最優先・常に1つ）

### ▶ logs/YYYYMMDD/case.md のロギング仕様（v0.1）を作成する  

（Responsibility Map および pytest Execution Layer の整備が完了したため、  
次はテスト基盤に必須となるログ出力仕様へ進む）

---

## 7. 必須資料（Dependencies）

- Responsibility_Map_v0.1.md  
- Design_pytest_env_v0.1.md  
- Design_env_v0.1  
- Design_ci_e2e_v0.1  
- Design_playwright_v0.1  
- test_plan_v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  

---

## 8. 更新履歴

- **v0.1.12（2025-12-07） ← NEW**  
  - Responsibility_Map_v0.1.md を正式追加  
  - Design_pytest_env_v0.1 を正式追加  
  - pytest Execution Layer（conftest.py v0.1）の設計仕様を確定  
  - Next Action を「ロギング仕様 v0.1」へ更新  
