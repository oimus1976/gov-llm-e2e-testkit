# PROJECT_STATUS — gov-llm-e2e-testkit
最終更新: 2025-12-07  
バージョン: v0.1.8  
ステータス: RAG Basic / Advanced pytest v0.1 実装完了

---

## 1. プロジェクト概要
本プロジェクトは自治体向け LLM サービスを対象とした  
E2E 自動テスト基盤（Python + Playwright）を構築する。

プロジェクトは次の多層構造で統制される：
- **統治層**：PROJECT_GRAND_RULES  
- **運転層**：Startup Template v3.0  
- **行動制御層**：Startup Workflow v3.0  
- **実行層**：本ステータス（唯一の現在地）

設計書（Design）、UI規範（Locator Guide）、test_plan、CI、STATUS の  
**完全整合**によって品質を維持する。

---

## 2. 現在地（Where we are now）

- test_plan_v0.1（最上位テスト仕様）完成  
- RAG Basic / Advanced の **YAML 実体化 v0.1 完了**  
- RAG テストの pytest 実装 v0.1（basic/advanced）完成  
- Page Object（Base / Chat / Login）実装済  
- Smoke Test v0.1 完成  

これにより **CI（e2e.yml）設計フェーズへ正式に移行可能な状態**になった。

---

## 3. 完了した成果（Done）

- Design_playwright_v0.1  
- Locator_Guide_v0.2  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- BasePage.py  
- ChatPage.py  
- LoginPage.py  
- Smoke Test（test_smoke_llm.py）  
- Roadmap_v1.0  
- test_plan_v0.1  
- RAG YAML v0.1（basic / advanced）  
- **RAG Basic / Advanced pytest 実装 v0.1 ← NEW（v0.1.8）**  
- STATUS v0.1.7 → v0.1.8（本更新）

---

## 4. 未完了タスク（Backlog）

### 設計
- CI（e2e.yml）v0.1 の設計  
- env.yaml（INTERNET/LGWAN 切替仕様）  
- ロギング（logs/YYYYMMDD/case.md）仕様

### 実装
- CI（e2e.yml）v0.1  
- pytest の strict / lenient オプション（v0.2）  
- Advanced（階層構造 / evidence）の強化（v0.2）

---

## 5. リスク・注意点

- YAML expected_keywords の粒度がテスト品質を左右  
- UI変動 → Page Object 破壊 → RAG 全滅リスク  
- LGWAN 実行時の timeout の大きさ  
- CI のテスト件数 0 → exit 5（禁止）

---

## 6. Next Action（最優先タスク：常に1つ）

### ▶ **CI（e2e.yml）v0.1 の正式設計**

**理由：**
- Smoke → Basic → Advanced の実行順は test_plan により強制  
- CI exit 5 回避（YAML ゼロ件禁止）  
- Pytest 実装が揃ったため、CI レイヤを構築できる唯一の状態になった  
- 自動化が進むことで LGWAN 手動実行の負荷を最小化できる

---

## 7. 必須資料（Dependencies）

- test_plan_v0.1  
- RAG pytest 実装 v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- Locator_Guide_v0.2  
- CHANGELOG.md  
- 本 PROJECT_STATUS v0.1.8

---

## 8. PENTA 推奨ポイント（CI 設計向け）

- Smoke → Basic → Advanced の依存シーケンス  
- YAML ケース 0 件 → exit 5 → CI 落ちの防止  
- Playwright ブラウザの install step 必須  
- LGWAN 用 artifact 制御（ログ外部持ち出し禁止）  
- strict モード導入の可否  

---

## 9. 更新履歴

- **v0.1.8（2025-12-07）**  
  - RAG Basic / Advanced pytest v0.1 実装完了を反映  
  - Next Action を「CI（e2e.yml）v0.1 設計」へ更新  
  - rag_basic / rag_advanced の物理フォルダ廃止 → rag/ へ統一の方針確立  
- **v0.1.7（2025-12-07）** test_plan_v0.1 完成（略）
