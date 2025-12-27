# gov-llm-e2e-testkit Roadmap v1.1（確定版）

最終更新: **2025-12-14**
更新理由: **Basic RAG Test 実装完了・Answer Detection API v0.1r 確定・RAG 評価基準 v0.1 固定を反映**

---

## 0. 本ロードマップの位置づけ（重要）

本ロードマップは、
**Design_playwright_v0.1 に定義された Playwright 利用設計を
「技術的前提（アーキテクチャ憲法）」として進行する。**

* Playwright の責務・抽象化方針・環境分離（INTERNET / LGWAN）は
  **Design_playwright_v0.1 を唯一の正本**とする
* 本ロードマップは、それを **どの順序で・どこまで実装・検証するか**を示す進行図である

---

## 1. プロジェクト全体像（4層統治モデル｜不変）

本プロジェクトは以下の4層構造で維持される：

1. **統治層**：PROJECT_GRAND_RULES
2. **運転層**：Startup Template
3. **行動制御層**：Startup Workflow
4. **実行層**：PROJECT_STATUS（現在地の唯一の正本）

この構造により、
設計 → 実装 → テスト → CI → 運用 が破綻しない体制を維持する。

---

## 2. フェーズ構造（Master Timeline｜更新後）

### フェーズ一覧

1. **F1：設計フェーズ（完了）**
2. **F2：Page Object 実装フェーズ（完了）**
3. **F3：Answer Detection & テスト基盤構築フェーズ（完了）**
4. **F4：RAG 評価基準・比較テスト構築フェーズ（進行予定）**
5. **F5：CI（e2e.yml）整備フェーズ**
6. **F6：LGWAN 対応フェーズ**
7. **F7：運用・保守フェーズ（継続）**

---

## 3. F1：設計フェーズ（完了）

### 完了成果

* Design_playwright_v0.1
* Locator_Guide_v0.2
* Design_BasePage / LoginPage / ChatPage
* Startup Template / Workflow
* プロジェクト統治ルール一式

### 状態

→ **設計フェーズは 100% 完了**

---

## 4. F2：Page Object 実装フェーズ（完了）

### 完了根拠

* BasePage / LoginPage / ChatPage 実装済み
* submit v0.6 による UI submit の安定化
* Smoke Test / Basic RAG Test が Page Object 経由で成立
* Locator_Guide に基づく修正容易性を確認済み

👉 **UI 操作層は安定版に到達**

---

## 5. F3：Answer Detection & テスト基盤構築フェーズ（完了）

### 背景（学習点）

* chat-id 境界問題
* pytest-facing API 境界問題
* page 隠蔽の失敗と撤回
* Inconclusive（評価不能）という第三の判定モデルの必要性

### 完了成果

* Answer Detection Layer（probe v0.2）正規統合
* pytest-facing Answer Probe API v0.1r 確定
* page を受け取る低レベル API 境界の正式採用
* Inconclusive（SKIPPED）モデル確立
* Basic RAG Test が **「基盤不具合ではなく、品質理由で落ちる」状態に到達**

👉 **テスト基盤としての完成**

---

## 6. F4：RAG 評価基準・比較テスト構築フェーズ（次フェーズ）

### 6.1 評価基準（確定）

* **RAG 評価基準 v0.1（正式決定）**

  * Evidence Hit Rate（条例由来語・条番号）
  * Hallucination Rate（無根拠表現）
  * Answer Stability（再現性）
* 絶対評価ではなく **差分評価（HTML vs Markdown）**

### 6.2 実装内容

* HTML 投入構成 / Markdown 投入構成で同一テストを実行
* 評価結果の差分サマリ生成
* 20GB 容量制約との関係整理
* Markdown 変換の「やる／やらない」判断材料を得る

👉 **本プロジェクトの目的ど真ん中**

---

## 7. F5：CI（e2e.yml）整備フェーズ

### 目的

* GitHub Actions 上で Smoke / Basic RAG Test を自動実行
* exit code 5（テスト件数0）の恒久回避

### 必須要素

* Playwright install
* artifact 出力（ログ / スクリーンショット）
* INTERNET 環境専用 CI として設計

---

## 8. F6：LGWAN 対応フェーズ

* env.yaml による secure-config 切替
* timeout / retry 調整
* 手動実行手順書の整備
* ログ持ち出し制限への対応

---

## 9. F7：運用・保守フェーズ（継続）

* UI 変動時の修正ルート確立
  （Locator_Guide → Page Object → テスト）
* モデル更新時の Smoke → Basic → Advanced 再走
* 半年〜1年単位の棚卸し

---

## 10. Roadmap × Design_playwright 対応表（参考）

| Roadmap フェーズ | Design_playwright 節            |
| ------------ | ------------------------------ |
| F2           | 3.1 / 5（Page Object / Locator） |
| F3           | 2 / 6（Test Level / Wait設計）     |
| F4           | 7 / 8（Test Data / Log）         |
| F5           | 9（CI）                          |
| F6           | 4（LGWAN）                       |

---

## 📌 総括（v1.1）

Roadmap v1.1 は、

* **テストが動く段階は完了**
* **前処理（Markdown変換）の価値を証明する段階へ正式移行**

という、現在地を正確に反映した
**進行ロードマップの確定版**である。

---

### 次の確定アクション（ロードマップ観点）

* Roadmap v1.1 を正式採用
* PROJECT_STATUS に

  * F2 / F3 完了
  * F4 開始
    を反映
* CHANGELOG に Roadmap 更新を記録

---
