# PROJECT_STATUS — gov-llm-e2e-testkit
最終更新: 2025-12-07  
バージョン: v0.1.7  
ステータス: test_plan_v0.1 完成（テスト体系が確立）

---

## 1. プロジェクト概要
本プロジェクトは自治体向け LLM サービスを対象とした  
E2E 自動テスト基盤（Python + Playwright）を構築する。

プロジェクトは以下の多層構造で統制される：
- **統治層**：PROJECT_GRAND_RULES  
- **運転層**：Startup Template v3.0  
- **行動制御層**：Startup Workflow v3.0  
- **実行層**：本ステータス（唯一の現在地）  

また、設計書（Design）、UI規範（Locator Guide）、test_plan、CI、STATUS の  
**完全整合** によって品質を維持する。

---

## 2. 現在地（Where we are now）

- Startup Template v3.0 / Workflow v3.0 / GRAND_RULES v2.0 完備  
- Page Object 設計（Base / Chat / Login）完了  
- Page Object 実装（BasePage.py / ChatPage.py / LoginPage.py）完了  
- Smoke Test v0.1 実装済  
- **test_plan_v0.1（テスト体系の最上位仕様）完成 ← 今回の更新**

これにより **RAGテスト設計／CI設計へ正式に進める状態**が整った。

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
- **test_plan_v0.1（本更新）**  
- STATUS v0.1.6 → v0.1.7（本更新）

---

## 4. 未完了タスク（Backlog）

### 設計
- RAG テストデータ（YAML スキーマの具体化：basic/advanced）  
- env.yaml（INTERNET/LGWAN 切替仕様）  
- CI（e2e.yml）v0.1 設計

### 実装
- basic/*.yaml の実装  
- advanced/*.yaml の実装  
- CI（e2e.yml）  
- RAG テストコード（test_rag_basic.py / test_rag_advanced.py）

---

## 5. リスク・注意点

- RAG expected_keywords の粒度過不足  
- UI変動 → Page Object 破壊 → RAG 全滅リスク  
- LGWAN は timeout が大きく実施が困難になる可能性  
- YAML データの質がテストの精度を決定する

---

## 6. Next Action（最優先タスク：常に1つ）

### ▶ **RAG テストデータ（basic/advanced）YAML スキーマの実体化**  
（test_plan v0.1 の仕様を実データに落とし込む）

**理由：**
- test_plan（方針）が完成したので、次は「実データ（ケース）」を作るフェーズ  
- CI のためにも最低1件の basic/advanced YAML が必須  
- Smoke Test の次に最も依存度が高い作業

---

## 7. 必須資料

- test_plan_v0.1  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- Locator_Guide_v0.2  
- PROJECT_STATUS v0.1.7（本書）  
- CHANGELOG.md

---

## 8. PENTA 推奨ポイント

- RAG キーワードの粒度調整  
- strict / lenient 搭載の判断  
- YAML の命名規則（case_id）  
- LGWAN での実行可能性  
- CI の優先度順（Smoke → Basic → Advanced）

---

## 9. 更新履歴

- **v0.1.7（2025-12-07）**  
  - test_plan_v0.1 の完成を反映  
  - Next Action を「RAG YAML スキーマ実体化」へ更新  
- **v0.1.6（2025-12-07）**  
  - LoginPage 設計完了を反映  
- （以下略）
