# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.9  
ステータス: CI（e2e.yml）v0.1 設計完了

---

## 1. プロジェクト概要

E2E 自動テスト基盤（Python + Playwright）を自治体向け LLM サービスに適用するプロジェクト。  
統治層（GRAND_RULES）・運転層（Startup Template）・行動制御層（Workflow）・実行層（STATUS）の4層で統制する。

---

## 2. 現在地（Where we are now）

- test_plan_v0.1 完成  
- All Page Object（Base/Chat/Login）実装済  
- Smoke Test v0.1 完成  
- RAG YAML v0.1 完成  
- RAG Basic / Advanced pytest v0.1 完成  
- **CI（e2e.yml）v0.1 設計書 完成（← NEW）**

---

## 3. 完了した成果（Done）

- Design_playwright_v0.1  
- Locator_Guide_v0.2  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- BasePage.py / ChatPage.py / LoginPage.py  
- Smoke Test  
- RAG YAML v0.1  
- RAG pytest v0.1  
- **Design_ci_e2e_v0.1.md（← NEW）**

---

## 4. 未完了タスク（Backlog）

### 設計  

- env.yaml（INTERNET/LGWAN 切替仕様）  
- ロギング仕様（logs/YYYYMMDD/case.md）  

### 実装  

- **CI（e2e.yml）v0.1 の実装（← Next Action）**  
- pytest strict/lenient モード（v0.2）  
- Advanced 深層比較（v0.2）

---

## 5. リスク・注意点

- Smoke / Basic / Advanced の順序依存を CI で壊さない  
- テスト件数 0 → exit code 5（禁止）  
- secrets の安全運用  

---

## 6. Next Action（最優先・単一）

### ▶ **CI（e2e.yml）v0.1 の実装（ファイル配置）**

---

## 7. 必須資料（Dependencies）

- Design_ci_e2e_v0.1  
- test_plan_v0.1  
- pytest 実装 v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  

---

## 8. 更新履歴

- **v0.1.9（2025-12-07）**  
  - CI（e2e.yml）v0.1 設計書を新規追加  
  - Next Action を「CI 実装」に更新  
- **v0.1.8（2025-12-07）** RAG pytest 実装（略）
