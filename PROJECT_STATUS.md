# 📘 PROJECT_STATUS v0.7.4  
**— Design / Ops / Protocol 実行モデル確定反映版 —**

**Last Updated:** 2025-12-26  
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

#### 設計合意（v0.2）

- **F8 v0.2 設計合意サマリーを確定**
  - continue-on-error を前提とした runner / orchestrator 方針を合意
  - failure handling を二値ではなく状態（taxonomy）として扱う方針を合意
  - 全質問について成功・失敗を問わず **1 レコード必ず生成**する成果物完全性ルールを合意
- v0.1r で確定した単一質問 I/F（run_single_question）および  
  submit / probe / Answer Detection の責務分離は  
  **非改変・再利用前提**とすることを再確認

#### 状態

- F8 v0.2 は **設計合意フェーズ完了**
- 実装・詳細設計は未着手

---

## 2. プロジェクトの到達点（要約）

本プロジェクトは現在、

> **再現可能な E2E テスト基盤（F1–F3）**  
> **判断材料として利用可能な試金石データ（F4）**  
> **基盤破壊を即時検知する最小 CI（F5）**  
> がすべて成立・完結した状態で、  
> **F7-C（拡張試行フェーズ）を完結**し、  
> F8（Markdown 価値判断フェーズ）へ移行している。

---

## 3. 完了済み成果（完結）

### ✅ F1–F3：E2E 基盤フェーズ（完全完結）

- Playwright ベースの E2E テスト基盤を確立
- Page Object / Answer Detection / pytest Execution Layer の責務境界を固定
- UI 変動・モデル更新に対して再現可能な観測が可能な状態に到達

---

## 4. Design / Ops / Protocol 実行モデル（確定）

以下の 3 文書を、  
**AI 参加前提の正式な実行モデル定義として確定**した。

- **Design_Execution_Model_QommonsAI_TestAutomation_v1.1.md**
- **Ops_Web_VSCode_Roundtrip_Guide_v1.1.md**
- **Protocol_Web_VSCode_Roundtrip_v1.1.md**

確定したポイント：

- AI（Codex）を **正式メンバーとして参加させる前提**を明文化
- pytest 実行を **必須ルール**として設計に昇格
- 実行主体（Codex / 人間）の責務分離を固定
- Web版 / VS Code / Codex の裁定構造を三層分離
- Protocol を **AI拘束用の最下位正本**として定義

---

## 5. F8（単一質問 I/F）に関する確定事項

- F8 v0.1r+ は runner 実装完了をもって **FIX**
- UI 表示どおりの回答テキストを保存する
- Citations は独立セクションとして扱わない

以下は **v0.2 以降の検討対象（Backlog）**とする：

- Citations 構造化の可否
- 成果物配置・命名規約の正式 FIX
- frontmatter メタデータ既定値ポリシー
---

## 6. 運用上の前提（評価・判断と無関係）

以下は **品質評価・フェーズ進行判断の材料とはしない**。

- LLM 応答の非決定性
- UI 変更によるロケータ破壊
- 外部サービス起因の一時的失敗
---

## 7. Next Action（単一・最優先）

- **F8 v0.2 runner / orchestrator の具体 API 設計に着手**

---

## 8. Backlog（正式登録）

- **バージョニング規則の整理**
  - r / + 表記の採否
  - 採用する場合の意味論
  - 採用しない場合の禁止明文化
  - 影響範囲（Design / Docs / PROJECT_STATUS / CHANGELOG）

---

## 9. 注記（不変）

- 本 STATUS は **「現在地の唯一の正本」**である
- 設計・裁定・フェーズ判断は、  
  本文書と **Roadmap v1.4 / CHANGELOG** の整合をもって行う
