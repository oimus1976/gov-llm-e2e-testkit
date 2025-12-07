# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.1  
ステータス: プロジェクト名変更反映済

---

## 1. プロジェクト概要

本プロジェクトは **自治体向け LLM サービス（Qommons.AI を含む）の E2E 自動テスト基盤**を構築する。  
Playwright + Python により、条例ナレッジ QA の検証を自動化し、  
INTERNET / LGWAN の双方で安定した動作を目指す。

---

## 2. 現在地（Where we are now）

- プロジェクト名を **gov-llm-e2e-testkit** に正式変更  
- Startup Template v1.1（改名版）が確定  
- Design_playwright_v0.1.md（改名反映版）が完成  
- ディレクトリ標準構成の基準値を定義済  

---

## 3. 完了した成果

- プロジェクト名変更  
- Startup Template の再生成  
- DESIGN 文書の名称統一  
- 初期セットアップ台帳（STATUS v0.1.1）の作成  

---

## 4. 未完了タスク

- UI識別規範の単独ドキュメント作成  
- RAGテストデータスキーマ（YAML/JSON）整備  
- e2e.yml 初版の設計  
- smoke test（初版）の作成  
- Advanced RAG テスト DSL の検討  

---

## 5. リスク・注意点

- LLM UI の頻繁な変化によるテスト破壊リスク  
- LGWAN 上でのログ保存運用  
- Qommons.AI へのアクセス仕様変更リスク  
- 想定外のモデル挙動によるテスト失敗頻発  

---

## 6. Next Action（最優先）

### ▶ **UI識別規範（Role-based Locator Guide）を design/ に生成する**

※ Playwright の成功率に直結するため、最優先。

---

## 7. 必須資料（Files / Specs）

- Startup Template v1.1（改名版）  
- Design_playwright_v0.1  
- test_plan（未作成）  
- CI（e2e.yml）草案（未作成）

---

## 8. PENTA 推奨ポイント

- UI識別規範の策定  
- CI 設計時  
- RAGテストの expected_keywords の粒度検討  
- LGWAN 運用のプロセス化  

---

## 9. 更新履歴

- **v0.1.1（2025-12-07）** プロジェクト名を gov-llm-e2e-testkit に変更、全ドキュメントへ反映  
- **v0.1.0（2025-12-07）** 初期版作成
