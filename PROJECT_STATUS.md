# 📘 PROJECT_STATUS v0.7.5  
**— F8（Markdown 価値判断フェーズ）実装・観測成立反映版 —**

**Last Updated:** 2025-12-27  
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 0. フェーズ定義の統一（不変）

本プロジェクトのフェーズ定義は、  
**Roadmap v1.4 を唯一の正本**として以下に統一する。

| フェーズ | 内容 |
|---|---|
| F1 | 設計フェーズ |
| F2 | Page Object 実装フェーズ |
| F3 | Answer Detection & テスト基盤構築フェーズ |
| F4 | RAG 入力差分影響の観測・試験データ提供フェーズ |
| F5 | CI（e2e.yml）整備フェーズ |
| F6 | LGWAN 対応フェーズ（保留） |
| F7-A | 運用準備フェーズ |
| F7-B | 制御付き実運用試行フェーズ |
| F7-C | 拡張試行フェーズ |
| **F8** | **Markdown 価値判断フェーズ** |

※ F7 は単一フェーズではなく、A / B / C の段階構造を持つ。

---

## 1. Current Phase（現在地）

### **F8：Markdown 価値判断フェーズ**

#### 設計・実装の確定状況

- **F8 v0.2 設計合意を前提に、実装・観測が成立**
- runner / orchestrator / single-question I/F を含む  
  **F8 実行パスが end-to-end で動作確認済み**
- Q01–Q18 を通じて、以下を満たすことを確認：
  - continue-on-error による全件記録
  - SUCCESS / NO_ANSWER / TIMEOUT 等の状態保持
  - answer.md が常に生成される成果物完全性

#### DOM 抽出に関する確定事項（重要）

- **Answer (Extracted)**  
  - UI DOM 上の `div.markdown`（markdown-n）を対象に  
    **最新・偶数 index を優先選択する非評価ロジックを確定**
  - 書式情報は保持しない（text 抽出）
- **Answer (Raw)**  
  - UI DOM（main/body）をそのまま保存する観測用スナップショット
  - UI 文言・サイドバー混入は **設計どおり許容**

- 抽出成否・理由・文字数は  
  **Metadata（Observed）として明示的に記録**

#### 状態

- **F8 は「設計 → 実装 → 観測成立」まで完了**
- 品質評価・価値判断（F9 以降）は未着手

---

## 2. プロジェクトの到達点（要約）

本プロジェクトは現在、

> **再現可能な E2E テスト基盤（F1–F3）**  
> **差分影響を測定可能な試行データ（F4）**  
> **基盤破壊を検知する最小 CI（F5）**  
> **制御付き実運用試行（F7-C）**  
> **Markdown 価値判断の技術的成立（F8）**  

がすべて **同一 main ブランチ上で整合した状態**に到達している。

---

## 3. 完了済み成果（完結）

### ✅ F1–F3：E2E 基盤フェーズ

- Playwright ベースの E2E テスト基盤を確立
- Page Object / Answer Detection / Execution Layer の責務境界を固定

### ✅ F7-C：拡張試行フェーズ

- 実運用相当条件下での制御付き試行を完結
- Golden Question / Ordinance を保持したまま次フェーズへ移行

### ✅ F8：Markdown 価値判断フェーズ（技術成立）

- DOM-based Answer 抽出の成立
- answer.md 正本生成ルールの確定
- 非評価・観測モデルの実装固定

---

## 4. Design / Ops / Protocol 実行モデル（確定）

以下の文書を、  
**AI 参加前提の正式な実行モデル定義として確定**した。

- **Design_Execution_Model_QommonsAI_TestAutomation_v1.1.md**
- **Ops_Web_VSCode_Roundtrip_Guide_v1.1.md**
- **Protocol_Web_VSCode_Roundtrip_v1.1.md**

---

## 5. F8 単一質問 I/F に関する確定事項

- run_single_question は **非評価・観測専用 I/F として FIX**
- probe（完了検知）と DOM 抽出は責務分離を維持
- status 判定は runner 側の観測事実にのみ依存

---

## 6. 運用上の前提（評価・判断と無関係）

以下は **品質評価・フェーズ進行判断の材料とはしない**。

- LLM 応答の非決定性
- UI 構造変更・文言変化
- 外部サービス起因の一時的失敗

---

## 7. Next Action（単一・最優先）

- **F9（Markdown 価値評価・比較指標定義フェーズ）構想整理**

---

## 8. Backlog（正式登録）

- DOM 構造変化検知ルールの将来検討
- Answer (Extracted) の書式保持可否
- バージョニング規則（r / + 表記）の整理

---

## 9. 注記（不変）

- 本 STATUS は **「現在地の唯一の正本」**である
- 設計・裁定・フェーズ判断は、  
  本文書と **Roadmap v1.4 / CHANGELOG** の整合をもって行う
