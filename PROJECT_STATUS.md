# 📘 PROJECT_STATUS v0.7.6（追記反映案）

**— F8（Markdown 価値判断フェーズ）実装・観測成立 + Docs 構造確定版 —**

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

#### 設計・実装・運用状態

- **F8 は「設計 → 実装 → 観測成立」まで完了**
- runner / orchestrator / single-question I/F を含む
  **F8 実行パスは end-to-end で成立**
- Q01–Q18 を通じて、以下を確認：
  - continue-on-error による全件記録
  - SUCCESS / NO_ANSWER / TIMEOUT 等の状態保持
  - answer.md が必ず生成される成果物完全性

#### 回答素材（answer.md）に関する確定事項

- Answer (Extracted)
  - UI DOM 上の `div.markdown` を対象とした **非評価・best-effort 抽出**
  - 書式は保持しない（text 抽出）
- Answer (Raw)
  - UI DOM 全体を保存する **観測用スナップショット**
- 抽出結果・成否・理由・文字数は  
  **Metadata（Observed）として明示的に記録**

---

## 2. ドキュメント構造整理（v0.7.6 反映事項）

### 概要

- docs 配下のディレクトリ構造を整理し、  
  **入口文書／設計／運用／規約／アーカイブの責務を明確化**
- **内容・設計意味論の変更は一切行っていない**
- 移動のみ（move-only）による整理を実施

### 正本配置ルール（確定）

- **リポジトリ直下**
  - README.md
  - CHANGELOG.md
  - PROJECT_STATUS.md
- **docs 直下（不変・横断ルール）**
  - PROJECT_GRAND_RULES.md
  - Debugging_Principles.md
  - Roadmap.md
- **docs 配下**
  - design / operation / protocol / runbook / guidelines / spec / test_plan
- **docs/archive**
  - 旧版設計
  - 思考過程・検討メモ
  - 観測ログ・完了済みフェーズ成果物

この構造は **README.md に正式反映済み**。

---

## 3. プロジェクトの到達点（更新）

本プロジェクトは現在、以下が **同一 main ブランチ上で整合した状態**に到達している。

- 再現可能な E2E テスト基盤（F1–F3）
- RAG 入力差分影響の試行データ生成（F4）
- 基盤破壊を検知する最小 CI（F5）
- 制御付き実運用試行（F7-C）
- **回答素材収集基盤としての F8 技術成立**
- **ドキュメント構造の確定（v0.7.6）**

---

## 4. 完了済み成果（完結）

### ✅ F8：Markdown 価値判断フェーズ（技術成立）

- DOM-based Answer 抽出ロジックの確定
- answer.md 正本生成ルールの固定
- 非評価・観測モデルの実装完了

### ✅ Docs 構造整理（v0.7.6）

- OSS として第三者可読な構造に整理
- 正本／旧版／参照資料の区別を明確化
- README によるプロジェクト定義の明文化

---

## 5. 評価・判断に関する前提（不変）

以下は **本プロジェクトでは扱わない**。

- 回答の正誤・品質・有用性の評価
- Markdown / HTML の価値判断そのもの
- UI 構造の安定化保証

これらは **後続プロジェクトで扱う前提**とする。

---

## 6. Next Action（更新）

- **F9（Markdown 価値評価・比較指標定義フェーズ）の構想整理**
  - 本リポジトリでは実装しない可能性を含めて検討

---

## 7. Backlog（正式登録）

- DOM 構造変化検知ルールの将来検討
- Answer (Extracted) の書式保持可否
- バージョニング規則（r / + 表記）の整理

---

## 8. 注記（不変）

- 本 STATUS は **現在地の唯一の正本**
- CHANGELOG / Roadmap との整合をもって更新とみなす

---

## 付記：v0.7.6 の位置づけ

- 機能追加なし
- 設計意味論変更なし
- **F8 成果を引き渡すための「整理完了スナップショット」**

---
