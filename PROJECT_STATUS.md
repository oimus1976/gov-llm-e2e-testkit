# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.6  
ステータス: ChatPage / LoginPage 設計フェーズ完了

---

## 1. プロジェクト概要

本プロジェクトは自治体向け LLM サービスを対象とした  
E2E 自動テスト基盤（Playwright + Python）を構築する。

プロジェクトは以下の 4 層構造により維持される：

- **統治層**：PROJECT_GRAND_RULES  
- **運転層**：Startup Template v3.0  
- **行動制御層**：Startup Workflow v3.0  
- **実行層**：本ステータス（唯一の現在地）

そして **Design / Locator Guide / CHANGELOG** に基づいて  
INTERNET / LGWAN 両環境で壊れないテスト基盤を提供する。

---

## 2. 現在地（Where we are now）

- Startup Workflow v3.0 導入済  
- Startup Template v3.0 採用済  
- Locator_Guide_v0.2 / Design_playwright_v0.1 / BasePage 設計完了  
- **ChatPage 設計書 v0.1 完成**  
- **LoginPage 設計書 v0.1 完成 ← 今ここ**  

これにより **Page Object（基底＋主要画面）の設計フェーズが完了**し、  
次は実装フェーズへ進む準備が整った状態となった。

---

## 3. 完了した成果（Done）

- GRAND_RULES v2.0 制定  
- Startup Template v3.0 更新  
- Startup Workflow v3.0 作成  
- Design_playwright_v0.1 作成  
- Locator_Guide_v0.2 作成  
- Design_BasePage_v0.1 作成  
- Design_ChatPage_v0.1 作成  
- **Design_LoginPage_v0.1 作成 ← 今回**  
- CHANGELOG v0.1.5 まで更新済  
- STATUS v0.1.5 → v0.1.6（本更新）

---

## 4. 未完了タスク（Backlog）

### 🔹 設計

- test_plan（RAG テスト方針 v0.1）
- CI 設計書（e2e.yml）v0.1
- env.yaml（INTERNET / LGWAN 切替仕様）

### 🔹 実装

- **BasePage（Pythonコード）実装** ← 最優先  
- ChatPage 実装  
- LoginPage 実装  
- Smoke Test（test_smoke_llm.py）初版作成

### 🔹 データ

- basic / advanced RAG テストデータ（YAML/JSON）設計

---

## 5. リスク・注意点

- Page Object 実装と設計書の乖離  
- ロケータ破壊時の早期検知が必要  
- LGWAN での timeout 影響  
- RAG expected_keywords の粒度調整  
- CI（Actions）でのブラウザ依存／安定性

---

## 6. Next Action（最優先タスク：常に 1 つ）

### ▶ **BasePage（Python 実装）を作成する**

**理由：**

- ChatPage / LoginPage の実装は BasePage 実装が基盤  
- Smoke Test のコア機能（質問入力→送信→応答取得）を動かす最初の工程  
- UI変動の影響を最小化する中心クラス

---

## 7. 必須資料

- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_playwright_v0.1  
- Locator_Guide_v0.2  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- CHANGELOG.md  
- PROJECT_STATUS.md（本書）

---

## 8. PENTA 推奨ポイント

- BasePage のロケータ生成の厳密実装  
- LGWAN timeout 実装方針  
- ChatPage / LoginPage のメソッド粒度  
- CI との紐付け（e2e.yml の設計）

---

## 9. 更新履歴

- **v0.1.6（2025-12-07）**  
  - LoginPage 設計書 v0.1 完成を反映  
  - Next Action を BasePage 実装へ更新  
- **v0.1.5（2025-12-07）**  
  - BasePage 設計書 v0.1 完成を反映  
- **v0.1.4〜v0.1.0**  
  - 既存履歴の通り
