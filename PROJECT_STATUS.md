# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.4  
ステータス: Startup Workflow v3.0 を採用し、行動制御レイヤを正式装備

---

## 1. プロジェクト概要

本プロジェクトは **自治体向け LLM サービスを対象とした  
E2E 自動テスト基盤（Python + Playwright）** を構築する。

参照文書（GRAND_RULES / Startup Template / Workflow / Design / Locator Guide / CHANGELOG）を軸に、  
**INTERNET / LGWAN 両環境**で壊れない長期 QA 基盤を整備する。

本ステータスはプロジェクト階層の **第3層＝実行レイヤ** として、  
現時点の進捗と次の最小タスク（Next Action）を記録する唯一の正本である。

---

## 2. 現在地（Where we are now）

- PROJECT_GRAND_RULES v2.0（統治層）を完全採用 :contentReference[oaicite:3]{index=3}
- Startup Template v3.0（運転層）を正式採用 :contentReference[oaicite:3]{index=3}
- Startup Workflow v3.0（行動制御レイヤ）を導入 :contentReference[oaicite:4]{index=4}
- Design_playwright_v0.1（Playwright設計書）を保持 :contentReference[oaicite:0]{index=0}
- Locator_Guide_v0.2 を保持（UI識別の唯一の規範） :contentReference[oaicite:1]{index=1}
- CHANGELOG v0.1.3 まで更新済 :contentReference[oaicite:6]{index=6}

設計・運転・統治・行動制御の 4 レイヤが揃い、  
**BasePage（Page Object 基底）の設計に進む前提条件がすべて整った状態**。

---

## 3. 完了した成果（Done）

- プロジェクト名変更（qommons-ai-auto-test → gov-llm-e2e-testkit）
- Startup Template v1.1 → v3.0（運転層の総合刷新）
- PROJECT_GRAND_RULES v2.0 を制定・採用
- Design_playwright_v0.1 を作成
- Locator_Guide_v0.2 を作成
- ChatGPT Startup Workflow v3.0 を作成（行動制御の定着）
- CHANGELOG v0.1.0〜v0.1.3 完成
- STATUS v0.1.3 → v0.1.4（本更新）

---

## 4. 未完了タスク（Backlog）

### 🔹 設計フェーズ

- **BasePage 標準インターフェース設計（design/BasePage_spec_v0.1）** ← これが次
- ChatPage / LoginPage の設計
- test_plan（RAGテスト方針）作成
- e2e.yml（CI設計書 v0.1）作成

### 🔹 実装フェーズ

- BasePage（Pythonコード）作成
- ChatPage / LoginPage 実装
- Smoke Test 初版（test_smoke_llm.py）

### 🔹 データ設計

- RAG テストデータ構造（YAML/JSON）策定
- basic / advanced ケースのスキーマ化

### 🔹 環境関連

- INTERNET / LGWAN 切替ロジック（config/env.yaml）設計
- LGWAN 遅延向け timeout / retry 戦略の明文化

---

## 5. リスク・注意点（Risks）

- BasePage 設計が曖昧だと Page Object 全体が破綻
- UI変動 → ロケータ破壊 → テスト全停止のリスク
- LGWAN 低速での timeout 増大
- RAG データの品質による誤検知
- CI（GitHub Actions）でのブラウザ依存
- 設計書とコードの乖離

Workflow v3.0 と GRAND RULES により  
“設計駆動で進む限り破綻しない構造” は整備済。  
次は BasePage 仕様でこの構造をコードに落とす段階。

---

## 6. Next Action（最優先タスク：常に1つ）

### ▶ **BasePage（Page Object 基底クラス）の設計書を design/ に作成する**

**目的：**  

- UI操作の共通インターフェースを確立  
- Locator_Guide_v0.2 のロケータ優先順位を実装に適用  
- ChatPage / LoginPage / Smoke Test の共通基盤を構築  
- UI変動時に修正箇所を 1 箇所に集約できる構造を作る

**必要な参照文書：**  

- Design_playwright_v0.1 :contentReference[oaicite:0]{index=0}  
- Locator_Guide_v0.2 :contentReference[oaicite:1]{index=1}  
- Startup Template v3.0 :contentReference[oaicite:3]{index=3}  
- Startup Workflow v3.0 :contentReference[oaicite:4]{index=4}

---

## 7. 必須資料（Files / Specs）

- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_playwright_v0.1.md  
- Locator_Guide_v0.2.md  
- CHANGELOG.md  
- （未）BasePage_spec_v0.1  
- （未）test_plan  
- （未）e2e.yml

---

## 8. PENTA 推奨ポイント

- BasePage の責務・必須メソッド一覧  
- ロケータの抽象化粒度  
- LGWAN 遅延を考慮した timeout パラメータ  
- Basic / Advanced RAG の構造統一  
- CI での安定性確保（timeout / retries / artifacts）

---

## 9. 更新履歴（STATUS version history）

- **v0.1.4（2025-12-07）**  
  - Startup Workflow v3.0 の導入を反映  
  - Next Action と Backlog を Workflow 仕様に合わせ整理  
  - 必須資料に Workflow v3.0 を追加  
- **v0.1.3（2025-12-07）**  
  - Startup Template v3.0 採用に伴い、STATUS を全面更新  
  - 参照文書・Backlog・Next Action を最新化  
- **v0.1.2（2025-12-07）**  
  - Locator_Guide_v0.2 完成を反映  
- **v0.1.1（2025-12-07）**  
  - プロジェクト名変更  
- **v0.1.0（2025-12-07）**  
  - 初期版生成
