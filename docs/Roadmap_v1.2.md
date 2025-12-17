# gov-llm-e2e-testkit Roadmap v1.2（責務是正・最終版）

最終更新: **2025-12-17**
更新理由:

* **F4 フェーズの責務を「意思決定」から「試金石データ提供」へ是正**
* **F4 v0.2 を最初の完了マイルストーンとして明示**
* **F6（LGWAN）を外部依存による保留フェーズとして明確化**

---

## 0. 本ロードマップの位置づけ（重要・不変）

本ロードマップは、
**Design_playwright_v0.1 に定義された Playwright 利用設計を
「技術的前提（アーキテクチャ憲法）」として進行する。**

* Playwright の責務・抽象化方針・環境分離（INTERNET / LGWAN）は
  **Design_playwright_v0.1 を唯一の正本**とする
* 本ロードマップは、それを
  **どの順序で・どこまで構築・検証・提供するか**を示す進行図である

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

## 2. フェーズ構造（Master Timeline｜責務是正後）

### フェーズ一覧

1. **F1：設計フェーズ（完了）**
2. **F2：Page Object 実装フェーズ（完了）**
3. **F3：Answer Detection & テスト基盤構築フェーズ（完了）**
4. **F4：RAG 入力差分影響の観測・試験データ提供フェーズ**
5. **F5：CI（e2e.yml）整備フェーズ**
6. **F6：LGWAN 対応フェーズ（保留｜サービス提供待ち）**
7. **F7：運用・保守フェーズ（継続）**

> ※ F4 は RAG 前処理の是非を判断するフェーズではなく、
> 他プロジェクトが判断に利用可能な
> **再現可能な試験データを提供するフェーズ**と位置づける。

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
* Basic RAG Test が
  **「基盤不具合ではなく、品質理由で落ちる」状態に到達**

👉 **テスト基盤としての完成**

---

## 6. F4：RAG 入力差分影響の観測・試験データ提供フェーズ

### 6.1 フェーズの目的（責務固定）

F4 の目的は、

> **HTML / Markdown 等の入力差分が
> Qommons.AI の RAG 応答に与える影響を、
> 再現可能に観測・記録し、
> 他プロジェクト（例：例規HTML変換プロジェクト）が
> 採否判断の根拠として利用可能な
> 試験データを提供すること**

である。

本フェーズでは、
**判断・結論・採用可否の決定は行わない。**

---

### 6.2 評価基準（確定・不変）

* **RAG 評価基準 v0.1（正式決定）**

  * Evidence Hit Rate（条例由来語・条番号）
  * Hallucination Rate（無根拠表現）
  * Answer Stability（再現性）
* 絶対評価ではなく **差分評価（HTML vs Markdown）**

---

### 6.3 マイルストーン構成

#### F4 v0.1（完了）

**目的**：
入力差分評価が技術的に成立することを確認する

* 手動運用前提での評価ルール確定
* 再現可能な評価ログ取得
* 評価不能（Inconclusive / SKIPPED）を含む三値モデルの確立

👉 **試験基盤の成立確認**

---

#### F4 v0.2（次段階／最初の完了マイルストーン）

**目的**：
試験結果を構造化し、再利用可能な形で提供する

* ケース横断での評価結果集約
* 差分傾向の把握が可能な形式への整理
* 他プロジェクトが判断材料として直接利用可能な
  試金石データ一式の提供

👉 **試験データ提供フェーズの完了**

> ※ F4 v0.2 は、本フェーズのゴールを満たす
> **最初の完了マイルストーン**として位置づける。
> 追加の評価観点や提供形式が必要となった場合は、
> v0.3 以降として切り出す。

---

## 7. F5：CI（e2e.yml）整備フェーズ

### 目的

* GitHub Actions 上で Smoke / Basic RAG Test を自動実行
* exit code 5（テスト件数 0）の恒久回避

### 必須要素

* Playwright install
* artifact 出力（ログ / スクリーンショット）
* INTERNET 環境専用 CI として設計

---

## 8. F6：LGWAN 対応フェーズ（保留）

本フェーズは、
**サービス事業者による LGWAN 環境提供が開始されるまで
着手不可（Blocked）**とする。

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

## 📌 総括（v1.2）

Roadmap v1.2 は、

* **テスト基盤構築フェーズ（F1–F3）は完了**
* **F4 を「意思決定」ではなく
  「判断に使える試験データ提供フェーズ」として再定義**
* **F4 v0.2 を最初の完了マイルストーンとして明確化**
* **F6（LGWAN）を外部依存による保留フェーズとして固定**

することで、
本プロジェクトの責務・終点・保留条件を
**誤解なく共有するための最終ロードマップ**である。

---
