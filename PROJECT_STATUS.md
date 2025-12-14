# 📘 PROJECT_STATUS v0.6.0 — E2E基盤完了 / RAG評価フェーズ（v0.1）正式開始

**Last Updated:** 2025-12-14
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 0. フェーズ定義の統一について（重要）

本プロジェクトのフェーズ定義は、
**Roadmap v1.1 を唯一の正本**として以下に統一する。

| 区分 | 内容                             |
| -- | ------------------------------ |
| F1 | 設計フェーズ                         |
| F2 | Page Object 実装フェーズ             |
| F3 | Answer Detection & テスト基盤構築フェーズ |
| F4 | RAG 評価基準・比較テストフェーズ             |
| F5 | CI（e2e.yml）整備フェーズ              |
| F6 | LGWAN 対応フェーズ                   |
| F7 | 運用・保守フェーズ                      |

以降、本 STATUS では
**Phase A / B / C といった別系統の呼称は使用しない。**

---

## 1. Current Focus（現在の主眼）

本プロジェクトの最終目的は変わらない。

> **HTML 形式の例規・文書を RAG に投入する際、
> Markdown 変換が「容量制約（20GB）下で精度向上に寄与するか」を
> 自動テストで客観評価できる状態を作ること。**

そのために、

* 人手評価に依存しない
* 再現可能で
* 差分比較ができる

**RAG QA 自動評価基盤**を構築・運用する。

---

## 2. Completed（完了事項）

### ✅ F1–F3：E2E 基盤フェーズ（完全完了・凍結）

以下は **基盤として完成・変更禁止（freeze）** 状態である。

#### 設計・構造

* Design_playwright_v0.1（Playwright 利用設計・憲法）
* Locator_Guide_v0.2
* Debugging_Principles v0.2
* PROJECT_GRAND_RULES v4.2

#### 実装

* Environment Layer（env_loader v0.2.3）QA 完了・凍結
* Page Object（Base / Login / Chat）安定版
* ChatPage.submit v0.6

  * UI送信責務のみに限定
  * submit_id / SubmitReceipt 意味論確定

#### Answer Detection

* probe v0.2.1（GraphQL / REST 両対応）
* submit–probe 相関設計 v0.2

  * 相関を **アルゴリズムではなく state** として定義
* pytest-facing Answer Probe API v0.1r 確定

  * page を受け取る低レベル API 境界を正式採用

#### CI / 可視化

* CI Correlation Summary Presentation Semantics v0.1
* GitHub Actions summary による **日本語相関サマリー**
* WARN / INFO を FAIL と誤認しない意味論を保証

👉 **E2E 基盤としての完成条件をすべて満たした**

---

## 3. F3 補足：今回の学習事項（Lessons Learned）

* page を隠蔽した高レベル API は
  **一次情報欠落・境界不明瞭化のリスクが高い**
* chat-id は「便利に推測する対象」ではなく
  **API 境界で明示的に受け取る事実**
* RAG QA では
  **FAIL / PASS / SKIPPED（Inconclusive）** の三値判定が必須
* 「意味的に正しい」と「文字列的に一致」は別問題

これらは **設計判断として固定済み**。

---

## 4. Current Phase（現在のフェーズ）

### ▶ F4：RAG 評価基準・比較テストフェーズ（進行中）

本フェーズは **E2E 基盤を変更せず**、
その上で RAG の品質を測ることに専念する。

#### 確定事項

* **RAG 評価基準 v0.1（正式決定）**

  * Evidence Hit Rate（条例由来語）
  * Hallucination Rate（無根拠表現）
  * Answer Stability（再現性）
* 絶対評価ではなく **差分評価**

  * HTML 投入 vs Markdown 投入

#### 状態

* Basic RAG Test 実装完了
* テストは「基盤不具合」ではなく
  **評価基準により FAIL / SKIP する段階に到達**

👉 **目的に直結するフェーズへ正式移行**

---

## 5. Next Actions（次の一手）

### 🎯 F4 内で行うこと（順序固定）

1. HTML / Markdown 両構成での Basic RAG Test 実行
2. 評価結果の差分整理（Evidence / Hallucination / Stability）
3. Markdown 変換の費用対効果を定量化
4. v0.2 以降の評価指標（意味的同義語など）検討材料を得る

---

## 6. Out of Scope（本フェーズでは扱わない）

* 高度な意味理解・同義語判定
* 自動要約の品質評価
* モデル間比較

※ いずれも **F4 完了後に再検討**

---

## 7. Risks / Notes（引き続き意識する点）

* LLM 応答の非決定性
* RAG ナレッジ更新による期待値変動
* LGWAN 環境での実行制約

→ **いずれも基盤ではなく評価レイヤの課題**

---

## 8. Version History

### v0.6.0 — フェーズ定義統一 / RAG評価フェーズ正式開始

* Roadmap v1.1 にフェーズ定義を完全統一
* F1–F3 を「基盤フェーズ」として明確に凍結
* RAG 評価基準 v0.1 を STATUS に反映

### v0.5.1 — 基盤確認 CI 意味論確定

（省略：内容は前版を踏襲）

---

## 📌 総括

本プロジェクトは現在、

> **「テストが動く」段階を完全に通過し、
> 「テストで価値判断をする」段階に入った**

という、非常に健全な状態にある。

---

### 次の作業提案

1. この PROJECT_STATUS v0.6.0 を採用
2. CHANGELOG 更新（Roadmap v1.1 / STATUS v0.6.0 反映）
3. F4 作業ログの整理開始

👉 この STATUS 更新案、
**そのまま確定して CHANGELOG に進みますか？**
