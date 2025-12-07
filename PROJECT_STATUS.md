# PROJECT_STATUS — gov-llm-e2e-testkit

最終更新: 2025-12-07  
バージョン: v0.1.2  
ステータス: UI識別規範（Locator_Guide_v0.2）完了

---

## 1. プロジェクト概要

本プロジェクトは **自治体向け LLM サービス（Qommons.AI を含む）の E2E 自動テスト基盤**を構築する。  
Playwright + Python により条例ナレッジ QA を自動検証し、  
INTERNET / LGWAN 両環境で安定した長期運用を可能とする。

---

## 2. 現在地（Where we are now）

- Startup Template v1.1（改名版 + 参照文書更新）を反映済  
- Design_playwright_v0.1.md を格納済  
- **Locator_Guide_v0.2（UI識別規範）が完成し、design/ に追加済**  
- プロジェクトの基盤文書が揃い、Page Object 実装に進める状態

---

## 3. 完了した成果（Done）

- プロジェクト名変更 → gov-llm-e2e-testkit  
- Startup Template v1.1（参照文書へ Locator_Guide を追記）  
- Design_playwright_v0.1.md（Playwright基盤設計）  
- **Locator_Guide_v0.2（UI識別規範 v0.2）作成・格納**  
- 初期ステータス v0.1.1 → v0.1.2 への更新

---

## 4. 未完了タスク（ToDo / Backlog）

- **Page Object 標準インターフェース（BasePage）作成** ← 次の最優先  
- RAGテスト用 YAML/JSON スキーマ設計（basic_cases / advanced_cases）  
- CI（e2e.yml）初版の設計（pytest + Playwright）  
- 初回 Smoke Test（test_smoke_llm.py）の作成  
- Advanced RAG Test 用 DSL/シナリオ定義の検討  
- LGWAN 実行手順書（manual-run 手順）  
- 参照文書のバージョニング戦略確立（v0.2→v0.3）

---

## 5. リスク・注意点

- LLM UI の頻繁な変更によるテスト破壊リスク  
- LGWAN でのネットワーク遅延に伴うタイムアウト増加  
- Qommons.AI 側での DOM変更・Reactコンポーネント変動リスク  
- ログサイズ肥大によるディスク圧迫（LGWAN側の方が顕著）  
- RAGテストの expected_keywords が過剰 or 不足するリスク  
- Page Object の分散・重複による保守性低下

---

## 6. Next Action（最優先タスク：常に1つ）

### ▶ **Page Object 標準インターフェース（BasePage）を design/ に作成する**

理由：

- Locator_Guide_v0.2 の内容をコードに落とし込む最初の工程  
- Smoke Test / Basic RAG / Advanced RAG のすべての土台となる  
- UI変更時の影響を最小化するための「中心クラス」になる

---

## 7. 必須資料（Files / Specs）

- Startup Template v1.1（参照文書更新版）  
- Design_playwright_v0.1.md :contentReference[oaicite:0]{index=0}  
- **Locator_Guide_v0.2.md（UI識別規範）** :contentReference[oaicite:1]{index=1}  
- PROJECT_STATUS v0.1.2（本書）  
- test_plan（未作成）  
- CI（e2e.yml）草案（未作成）

---

## 8. PENTA 推奨ポイント

- Page Object 設計（BasePage / ChatPage / LoginPage）  
- RAGテストデータ設計（YAML/JSON スキーマ）  
- CI での timeout・リトライ戦略  
- Expected Keywords / Must-not Contain の粒度調整  
- LGWAN 運用プロセス（持ち出し手順・ログ管理）

---

## 9. 更新履歴

- **v0.1.2（2025-12-07）** Locator_Guide_v0.2 の作成完了に伴い STATUS を更新  
- **v0.1.1（2025-12-07）** プロジェクト名変更反映  
- **v0.1.0（2025-12-07）** 初期版作成
