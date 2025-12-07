# gov-llm-e2e-testkit Roadmap v1.0  

最終更新: 2025-12-07  
参照：PROJECT_GRAND_RULES / Startup Template v3.0 / Startup Workflow v3.0 / STATUS v0.1.6

---

## 1. プロジェクト全体像（4層統治モデル）

本プロジェクトは以下の4層構造で維持される：

1. **統治層**：PROJECT_GRAND_RULES  
2. **運転層**：Startup Template v3.0  
3. **行動制御層**：Startup Workflow v3.0  
4. **実行層**：STATUS（現在地の唯一の正本）

この構造により、  
設計書 → 実装 → CI → 運用 のすべてが破綻しない体制を作る。

---

## 2. フェーズ構造（Master Timeline）

プロジェクトは大きく以下のフェーズに分かれる：

1. **F1：設計フェーズ（完了済）**  
2. **F2：Page Object 実装フェーズ（次）**  
3. **F3：Smoke / Basic / Advanced テスト設計フェーズ**  
4. **F4：RAG テストデータ（YAML/JSON）構築フェーズ**  
5. **F5：CI（e2e.yml）整備フェーズ**  
6. **F6：LGWAN 対応フェーズ**  
7. **F7：運用フェーズ（UI変動・モデル更新対応）**

各フェーズ完了時に **STATUS / CHANGELOG を更新**する。

---

## 3. F1：設計フェーズ（完了）

### 完了成果
- Design_playwright_v0.1  
- Locator_Guide_v0.2  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- Startup Template v3.0  
- Startup Workflow v3.0  

### 状態
→ 設計フェーズは **100% 完了**  
→ 次フェーズは F2：Page Object 実装フェーズ

---

## 4. F2：Page Object 実装フェーズ（着手予定）

### 4.1 実装順序（MUST）

1. BasePage.py  
2. ChatPage.py  
3. LoginPage.py  

### 4.2 主目的

- 設計書の構造を正確にコードへ落とす  
- Locator_Guide との一貫性確保  
- UI変動時に最小の変更で済む構造を作る  

### 4.3 完了条件

- 3 ファイルのコード実装完了  
- STATUS / CHANGELOG 更新  
- Smoke テストでページ操作が動作確認できること

---

## 5. F3：テスト設計フェーズ

### 5.1 Smoke Test（最重要）

- test_smoke_llm.py  
- 質問 → 送信 → 応答取得の一連動作

### 5.2 Basic RAG Test

- expected_keywords の一致  
- YAML / JSON でテストケース化

### 5.3 Advanced RAG Test

- 説明、根拠、理由の整合  
- 差分チェック（diff-based validation）

---

## 6. F4：RAG テストデータ構築フェーズ

### 6.1 スキーマ設計

- case_id  
- input_text  
- expected_keywords  
- strict / lenient 判定

### 6.2 データ管理

- tests/rag/basic/*.yaml  
- tests/rag/advanced/*.yaml

---

## 7. F5：CI（e2e.yml）整備フェーズ

### 7.1 目的

- GitHub Actions 上で Playwright を自動実行  
- LGWAN は対象外（INTERNET版 CI のみ）

### 7.2 必須要素

- Smoke Test の存在確認（exit 5 回避）  
- Playwright browser install  
- artifact 出力（ログ、スクショ）  
- synthetic_html の CI 通過チェック  

---

## 8. F6：LGWAN 対応フェーズ

### 8.1 実行制約

- 外部通信禁止  
- timeout 増大  
- env.yaml により secure-config をロード

### 8.2 最適化

- manual-run 手順書  
- timeout・retry 調整  
- ログ持ち出し制限対応

---

## 9. F7：運用・保守フェーズ（継続）

### 9.1 UI änderungen（UI変動）

- Locator_Guide → BasePage → Page Object の順で修正  
- PENTA を使用して破壊範囲を特定する

### 9.2 モデル更新

- 基本的に Smoke → Basic → Advanced の順で再走  
- 変更箇所を差分として CHANGELOG に記録

### 9.3 半年〜1年単位の保守

- テストケースの棚卸し  
- env.yaml の timeout 再調整  
- CI の Playwright バージョンを更新

---

## 10. プロジェクト進行ルール

- フェーズ完了時に **STATUS / CHANGELOG を必ず更新**  
- 重大な設計変更は必ず **PENTA を経由**  
- Next Action は常に 1 つ  
- 作業開始時は /start（状態同期）  
- すべてのコード/設計書は GitHub 管理  
- CI でテスト件数 0 → exit 5 の回避は最重要

---

## 📌 総括

本ロードマップは  
**gov-llm-e2e-testkit 全体の“唯一の公式進行図”** である。

これにより：

- 何を  
- どの順番で  
- どこまで実施すれば  
- 長期的に壊れない QA 基盤が完成するか

が明確になる。

以上を **Roadmap_v1.0** として採用する。
