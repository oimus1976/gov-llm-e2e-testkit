# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.5  
ステータス: BasePage 設計書 v0.1 完成

---

## 1. プロジェクト概要

本プロジェクトは、自治体向け LLM サービスを対象とした  
E2E 自動テスト基盤（Python + Playwright）を構築する。

PROJECT_GRAND_RULES（統治層）  
Startup Template v3.0（運転層）  
Startup Workflow v3.0（行動制御層）  
Design / Locator Guide / STATUS / CHANGELOG の連携により、  
INTERNET / LGWAN の両環境で壊れない QA 基盤を長期運用する。

---

## 2. 現在地（Where we are now）

- Startup Workflow v3.0 を正式採用  
- Startup Template v3.0、GR v2.0 と完全整合  
- Locator_Guide_v0.2, Design_playwright_v0.1 を保持  
- **BasePage 設計書（Design_BasePage_v0.1）が完成**  
→ これにより ChatPage / LoginPage 設計フェーズへ進む準備が整った。

---

## 3. 完了した成果（Done）

- PROJECT_GRAND_RULES v2.0 制定・採択  
- Startup Template v3.0（統合版）作成  
- Startup Workflow v3.0（行動制御層）作成  
- Design_playwright_v0.1 作成  
- Locator_Guide_v0.2 作成  
- BasePage 設計書 v0.1 作成 ← ★今回  
- CHANGELOG v0.1.4 まで反映  
- STATUS v0.1.4 → v0.1.5（本更新）

---

## 4. 未完了タスク（Backlog）

### 🔹 設計フェーズ

- **ChatPage 設計書（Design_ChatPage_v0.1）**  
- LoginPage 設計書  
- RAG test_plan（v0.1）  
- CI（e2e.yml）設計書 v0.1

### 🔹 実装フェーズ

- BasePage（Pythonコード）実装  
- ChatPage / LoginPage の実装  
- Smoke Test（test_smoke_llm.py）作成

### 🔹 データ設計

- basic / advanced RAG テストデータ（YAML/JSON）のスキーマ化

### 🔹 環境関連

- env.yaml（INTERNET / LGWAN の timeout / retry 設計）  
- LGWAN モード向けの manual-run ガイド

---

## 5. リスク・注意点

- BasePage と Locator_Guide の乖離  
- ChatPage / LoginPage 間で UI 操作の重複が発生  
- LLM UIの変動によるロケータ破壊  
- LGWAN でのレスポンス遅延  
- テストデータの粒度過不足  

---

## 6. Next Action（最優先タスク：常に 1 つ）

### ▶ **ChatPage 設計書（Design_ChatPage_v0.1）を作成する**

**理由：**

- BasePage の上に乗る最初のページクラス  
- Smoke Test／RAG Test の主要動作（質問入力→送信→レスポンス検証）を担う  
- UI変動時の修正点を BasePage＋ChatPage の2点に限定できるため

---

## 7. 必須資料

- DESIGN: Design_BasePage_v0.1 / Design_playwright_v0.1  
- GUIDES: Locator_Guide_v0.2  
- GOVERN: PROJECT_GRAND_RULES v2.0  
- OPERATE: Startup Template v3.0  
- CONTROL: Startup Workflow v3.0  
- STATUS: PROJECT_STATUS v0.1.5（本書）  
- HISTORY: CHANGELOG.md

---

## 8. PENTA 推奨ポイント

- ChatPage の責務境界の決定  
- BasePage locator factory の継承方法  
- UI変動をどこまで ChatPage または BasePage で吸収するか  
- RAG テストデータとの整合性  
- CI（e2e.yml）のテスト順序設計

---

## 9. 更新履歴

- **v0.1.5（2025-12-07）**  
  - BasePage 設計書 v0.1 の完成を反映  
  - Next Action を ChatPage 設計書作成へ更新  
- **v0.1.4（2025-12-07）**  
  - Startup Workflow v3.0 の導入を反映  
- **v0.1.3〜v0.1.0**  
  - 既存履歴のとおり
