# PROJECT_STATUS — gov-llm-e2e-testkit
Version: v0.1.17  
Updated: 2025-12-08

---

## 1. プロジェクト概要

gov-llm-e2e-testkit は、  
自治体向け LLM チャット UI の **E2E 自動テスト基盤**を構築する OSS である。

- INTERNET / LGWAN の両環境で安定動作
- Playwright PageObject による UI 操作抽象化
- smoke / basic / advanced の 3 レベル検証
- Markdown ログ生成＋証跡（スクリーンショット / DOM）の自動保存
- CI（GitHub Actions）統合

本ドキュメントは「現在の進捗ステータス」を明示する。

---

## 2. 進行バージョン（現在地）

| Layer | Version |
|-------|---------|
| PROJECT_STATUS | **v0.1.17** |
| PageObject BasePage | v0.2 |
| PageObject LoginPage | v0.2 |
| PageObject ChatPage | v0.2 |
| pytest Execution Layer | **v0.2** |
| log_writer | v0.1 |
| env_loader | v0.1 |
| Design Spec | v0.2（pytest） |
| CI（e2e.yml） | v0.1 |

---

## 3. 完了した主な成果（2025/12/08 時点）

### ✅ PageObject v0.2 系（Base / Login / Chat）
- evidence_dir を受け取り、操作失敗時に screenshots + DOM を保存  
- safe_click / safe_fill / collect_evidence の統合  
- LGWAN / INTERNET 両方の timeout 管理を統一  
- 設計書（v0.2）＋ latest エントリーポイントを整理

### ✅ pytest Execution Layer v0.2（今回のメイン成果）
- conftest.py に **case_dirs fixture** を導入  
  → テストケース単位で case_log_dir / case_assets_dir を生成  
- Smoke / Basic / Advanced すべてを v0.2 対応へ全面改修  
- evidence_dir を PageObject v0.2 へ確実に伝搬  
- log_writer v0.1 と完全連携  
- INTERNET / LGWAN の構成差異を pytest 側で統一管理  
- advanced の multi-turn 検証を安定動作へ調整

### ✅ 設計書体系の統一
- Design_pytest_v0.2.md の新規作成  
- Design_ChatPage.md / Design_BasePage.md / Design_pytest.md の latest alias 統合  
- バージョン付き設計書は docs/ に全保持する方針を確立

---

## 4. 未解決の課題

### 🟡 pytest v0.3 以降で対応すべき項目
- strict/lenient モード  
- retry_policy（LGWAN 固有遅延の吸収）  
- assets の体系化（case_assets_dir 配下の整理）  
- parallel execution（shard）  
- HTML / JSON ログ出力（v0.2 は Markdown のみ）

### 🟡 CI 側の拡張
- CI artifacts として evidence を保存（必要に応じて）  
- synthetic_html の追加テスト（本番データ非依存）

### 🟡 テストケース管理
- basic_cases / advanced_cases の検証観点を拡大  
- LGWAN 特有の「応答遅延」への耐性評価

---

## 5. リスク・注意点

- PageObject / pytest / log_writer の **3レイヤーの契約（arguments / return）** が密結合  
  → バージョン変更時は設計書を必ず更新し、破壊的変更を避ける  
- assets_dir が急増するため、容量管理が必要（将来バージョンで整理予定）  
- LGWAN環境は想定以上にネットワーク遅延がある可能性  
  → timeout 値（env.yaml）を随時調整すべき

---

## 6. 次の最重要アクション（Next Action）

### 🔥 **v0.2 → v0.3 の移行準備フェーズ開始**
1. **evidence_dir の標準構造化（assets/types/screenshots, dom, raw 等）**  
2. retry_policy（UI応答遅延時の再試行）  
3. strict/lenient モード設計  
4. log_writer v0.2（JSON + 人間可読 diff）  
5. CI の artifacts 出力強化  

---

## 7. 必須資料（最新リンク）

- `docs/Design_BasePage_v0.2.md`
- `docs/Design_LoginPage_v0.2.md`
- `docs/Design_ChatPage_v0.2.md`
- `docs/Design_pytest_v0.2.md`
- `docs/Design_log_writer_v0.1.md`
- `docs/PROJECT_GRAND_RULES.md`
- `docs/Responsibility_Map_v0.1.md`

---

## 8. PENTA 推奨ポイント（継続適用）

- 設計 → 実装 → STATUS → CHANGELOG の順序を守る  
- 3レイヤーの責務分離（PageObject / pytest / CI）  
- 「環境依存」部分は pytest と env_loader に寄せる  
- 破壊的変更が発生する場合はバージョン番号を必ず increment  

---

End of Document.
