# PROJECT_STATUS — gov-llm-e2e-testkit
最終更新: 2025-12-07  
バージョン: v0.1.13  
ステータス: テストログ仕様（Design_logging_v0.1）正式追加

---

## 1. プロジェクト概要

本プロジェクトは、自治体向け LLM サービスを対象とした  
Python + Playwright + pytest ベースの E2E 自動テスト基盤を構築するものである。

設計は PROJECT_GRAND_RULES / Startup Template / Startup Workflow に従い、  
必ず「設計 → 実装 → CI → STATUS更新 → 次の設計」の順に進む。

---

## 2. 現在地（Where we are now）

- PageObject（BasePage / LoginPage / ChatPage）実装完了  
- test_plan v0.1 完成  
- Smoke Test 完成  
- RAG YAML（basic / advanced）完成  
- RAG pytest（basic / advanced）完成  
- CI（e2e.yml）v0.1 完成  
- env.yaml / env_loader 完成  
- pytest Execution Layer（Design_pytest_env_v0.1）完成  
- Responsibility Map v0.1 完成  
- **Design_logging_v0.1（ログ仕様）完成 ← NEW**

ネットワーク環境抽象・PO 層・CI 層・テスト層に加え、  
今回のログ出力仕様により **E2E テスト基盤の中核が一通り揃った段階**である。

---

## 3. 完了した成果（Done）

- Locator_Guide_v0.2  
- Design_playwright_v0.1  
- Design_BasePage_v0.1  
- Design_LoginPage_v0.1  
- Design_ChatPage_v0.1  
- test_smoke_llm.py  
- Design_ci_e2e_v0.1  
- Design_env_v0.1  
- env_loader.py  
- conftest.py（Execution Layer）  
- RAG YAML v0.1  
- RAG pytest v0.1  
- Responsibility_Map_v0.1  
- Design_pytest_env_v0.1  
- **Design_logging_v0.1 ← NEW**

---

## 4. 未完了タスク（Backlog）

### 設計関連
- **ログ生成ユーティリティ（logger_v0.1）の設計 ← 次フェーズ**  
- env.yaml v0.2（retry_policy / multi-profile）  
- Advanced RAG deep comparison（v0.2）  
- strict/lenient mode 仕様

### 実装関連
- logger_v0.1 実装  
- スクリーンショット／DOM dump 自動保存処理  
- RAG Advanced 深層比較ユーティリティ

---

## 5. リスク・注意点

- ログファイルに個人情報や庁内固有データを書かない  
- LGWAN 環境のログは持ち出し禁止・利用者教育が必須  
- 失敗時の artifacts 保存により情報漏洩リスクが発生しうる  
- 仕様 v0.1 は最小構成であり、v0.2 の拡張前提で運用すること  
- ログフォーマットを独自に変更すると解析不能になる

---

## 6. Next Action（最優先・常に1つ）

### ▶ **logger_v0.1（ログ生成ユーティリティ）の正式設計を行う**

理由：  
Design_logging_v0.1 に基づき、  
Smoke / Basic / Advanced / LGWAN / CI すべてで統一したログ生成を  
programmatically 行う基盤が必要となったため。

---

## 7. 必須資料（Dependencies）

- Design_logging_v0.1  
- Responsibility_Map_v0.1  
- Design_pytest_env_v0.1  
- Design_env_v0.1  
- test_plan_v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  

---

## 8. 更新履歴

- **v0.1.13（2025-12-07） ← NEW**
  - Design_logging_v0.1 を追加  
  - Next Action を「logger_v0.1 の設計」に更新
- v0.1.12（2025-12-07）
  - pytest Execution Layer/Responsibility Map 追加
