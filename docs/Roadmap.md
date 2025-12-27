---
doc_type: roadmap
project: gov-llm-e2e-testkit
version: v1.4
status: active
date: 2025-12-22
previous_version: v1.3
update_reason:
  - add F8 phase for Markdown value judgment
  - clarify that HTML→Markdown automation is a prerequisite, not a goal
  - resolve responsibility boundary between F7-C and value judgment work
parent_design:
  - Design_playwright_v0.1
related_docs:
  - PROJECT_STATUS
  - CHANGELOG
notes:
  - This roadmap defines phase responsibility and decision points only.
  - Evaluation, CI expansion, and optimization are explicitly out of scope unless stated.
---

# gov-llm-e2e-testkit Roadmap v1.4（F8：Markdown 価値判断フェーズ追加・全文差し替え版）

最終更新: **2025-12-22**
更新理由:

- **HTML→Markdown 変換を前提とした Private Knowledge 活用の「価値判断」を、正式なフェーズとして定義**
- **Markdown 化そのものを目的化せず、「変換コストに見合う価値があるか」を判断対象として明確化**
- **F7-C（拡張試行）と本命タスクとの責務衝突を解消**
- 上記は Roadmap の意味論を拡張するため、**v1.3 → v1.4** として更新

---

## 0. 本ロードマップの位置づけ（重要・不変）

本ロードマップは、
**Design_playwright_v0.1 に定義された Playwright 利用設計を
「技術的前提（アーキテクチャ憲法）」として進行する。**

- Playwright の責務・抽象化方針・環境分離（INTERNET / LGWAN）は
  **Design_playwright_v0.1 を唯一の正本**とする
- 本ロードマップは、それを
  **どの順序で・どこまで構築・検証・提供・判断するか**を示す進行図である

---

## 1. プロジェクト全体像（4層統治モデル｜不変）

本プロジェクトは以下の4層構造で維持される：

1. **統治層**：PROJECT_GRAND_RULES
2. **運転層**：Startup Template
3. **行動制御層**：Startup Workflow
4. **実行層**：PROJECT_STATUS（現在地の唯一の正本）

この構造により、
設計 → 実装 → テスト → CI → 運用 → 判断 が破綻しない体制を維持する。

---

## 2. フェーズ構造（Master Timeline｜責務是正後）

### フェーズ一覧

1. **F1：設計フェーズ（完了）**
2. **F2：Page Object 実装フェーズ（完了）**
3. **F3：Answer Detection & テスト基盤構築フェーズ（完了）**
4. **F4：RAG 入力差分影響の観測・試験データ提供フェーズ**
5. **F5：CI（e2e.yml）整備フェーズ**
6. **F6：LGWAN 対応フェーズ（保留｜サービス提供待ち）**
7. **F7：運用・保守フェーズ（A/B/C 分割・完了）**
8. **F8：Markdown 価値判断フェーズ（新設）**

- F4 は RAG 前処理の是非を判断するフェーズではなく、
  他プロジェクトが判断に利用可能な
  **再現可能な試験データを提供するフェーズ**と位置づける。
- F8 は **評価・自動化・CI フェーズではない**。

---

## 3. F1：設計フェーズ（完了）

### 完了成果

- Design_playwright_v0.1
- Locator_Guide_v0.2
- Design_BasePage / LoginPage / ChatPage
- Startup Template / Workflow
- プロジェクト統治ルール一式

### 状態

- **設計フェーズは 100% 完了**

---

## 4. F2：Page Object 実装フェーズ（完了）

### 完了根拠

- BasePage / LoginPage / ChatPage 実装済み
- submit v0.6 による UI submit の安定化
- Smoke Test / Basic RAG Test が Page Object 経由で成立
- Locator_Guide に基づく修正容易性を確認済み
- **UI 操作層は安定版に到達**

---

## 5. F3：Answer Detection & テスト基盤構築フェーズ（完了）

### 背景（学習点）

- chat-id 境界問題
- pytest-facing API 境界問題
- page 隠蔽の失敗と撤回
- Inconclusive（評価不能）という第三の判定モデルの必要性

### 完了成果

- Answer Detection Layer（probe v0.2）正規統合
- pytest-facing Answer Probe API v0.1r 確定
- page を受け取る低レベル API 境界の正式採用
- Inconclusive（SKIPPED）モデル確立
- Basic RAG Test が
  **「基盤不具合ではなく、品質理由で落ちる」状態に到達**
- **テスト基盤としての完成**

---

## 6. F4：RAG 入力差分影響の観測・試験データ提供フェーズ

### 6.1 フェーズの目的（責務固定）

F4 の目的は、

> **HTML / Markdown 等の入力差分が
> Qommons.AI の RAG 応答に与える影響を、
> 再現可能に観測・記録し、
> 他プロジェクトが採否判断の根拠として利用可能な
> 試験データを提供すること**

である。

本フェーズでは、
**判断・結論・採用可否の決定は行わない。**

---

### 6.2 評価基準（確定・不変）

- **RAG 評価基準 v0.1（正式決定）**
  - Evidence Hit Rate（条例由来語・条番号）
  - Hallucination Rate（無根拠表現）
  - Answer Stability（再現性）
- 絶対評価ではなく **差分評価（HTML vs Markdown）**

---

### 6.3 マイルストーン構成

#### F4 v0.1（完了）

**目的**
入力差分評価が技術的に成立することを確認する

- 手動運用前提での評価ルール確定
- 再現可能な評価ログ取得
- 評価不能（Inconclusive / SKIPPED）を含む三値モデルの確立
- **試験基盤の成立確認**

---

#### F4 v0.2（最初の完了マイルストーン）

**目的**
試験結果を構造化し、再利用可能な形で提供する

- ケース横断での評価結果集約
- 差分傾向の把握が可能な形式への整理
- 他プロジェクトが判断材料として直接利用可能な
  試金石データ一式の提供
- **試験データ提供フェーズの完了**
- F4 v0.2 は、本フェーズのゴールを満たす
  **最初の完了マイルストーン**として位置づける
- 追加の評価観点や提供形式が必要な場合は
  v0.3 以降として切り出す

---

## 7. F5：CI（e2e.yml）整備フェーズ

### 目的

- GitHub Actions 上で Smoke Test を自動実行
- 基盤破壊（UI / submit / probe）の即時検知
- exit code 5（テスト件数 0）の恒久回避

### 必須要素

- Playwright install
- artifact 出力（ログ / スクリーンショット）
- INTERNET 環境専用 CI として設計

---

## 8. F6：LGWAN 対応フェーズ（保留）

本フェーズは、
**サービス事業者による LGWAN 環境提供が開始されるまで着手不可（Blocked）**とする。

- env.yaml による secure-config 切替
- timeout / retry 調整
- 手動実行手順書の整備
- ログ持ち出し制限への対応

---

## 9. F7：運用・保守フェーズ（A/B/C 分割・完了）

F7 は単一フェーズではなく、
**目的と責務の異なる 3 段階（A/B/C）で構成される。**

---

### 9.1 F7-A：運用準備フェーズ

#### 目的

- 運用に入る前提条件を整備し、「入ってはいけない状態」を遮断する

#### 主な内容

- Golden 資産（質問・条例）の凍結と取扱明文化
- 準Golden質問作成ルールの確定
- Runbook（骨子）の整備
- Gate1（RAG Entry Check）設計・実装

#### 性質

- 実運用は行わない
- 判断・評価を行わない

---

### 9.2 F7-B：制御付き実運用試行フェーズ

#### 目的

- Golden QA 実運用に入っても**事故らずに回せることを確認する**

#### 主な内容

- 準Golden質問による少回数・単発試行
- 手動実行・手動記録
- Raw / Execution Context / Summary の取得
- 中断・撤退判断の確認

#### 制約

- 回答品質の評価は禁止
- 自動化・CI 連携は禁止
- 実行回数・実行者は厳密に制限

---

### 9.3 F7-C：拡張試行フェーズ

#### 目的

- F7-B で成立した運用を
  **継続・整理・横展開可能な形に移行する**

#### 主な内容（予定）**

- 試行回数の増加
- 判断ルール・評価軸の整理
- Runbook の実運用版への拡張
- 必要に応じた自動化・CI 連携検討

#### 注意

- F7-C は
  **新設計フェーズとして明示的に開始される**
- F7-B からの暗黙移行は禁止

F7-C までをもって、

- 運用が事故らず回ること
- 記録・中断・判断ルールが機能すること
- 評価・自動化に踏み込まずに運用できること

が確認された。

F7-C は **運用安全性確認の最終フェーズ**であり、
本フェーズ以降は **運用検証ではなく、価値判断に進行する。**

---

## 10. F8：Markdown 価値判断フェーズ（新設・本命）

### 10.1 フェーズの目的（唯一）

F8 の目的は、

> **HTML 形式の条例を Markdown に変換してまで
> Private Knowledge に登録する価値があるかを判断すること**

である。

Markdown 化は目的ではなく、
**価値判断を成立させるための前提作業**として位置づける。

---

### 10.2 主な内容（やること）

- HTML→Markdown 変換作業を **自動化**する

  - 完全性・美しさは要求しない
  - 再実行可能であることを重視する
- 一定量の条例を Markdown 化し、Private Knowledge に登録する
- 各条例に対して **定義済みの 18 問の質問**を実行する
- 回答を **すべて記録**する（Raw Answer）
- 得られた記録をもとに、
  **Markdown 化というコストに見合う価値があるかを判断**する

---

### 10.3 明示的 Non-Goals（やらないこと）

- 回答品質・正確性・優劣の評価
- 指標算出・スコアリング
- CI への統合
- 自動合否判定
- Markdown 変換精度そのものの最適化

---

### 10.4 フェーズの出口（判断）

F8 の出口は、以下のいずれかである。

- **価値あり**：Markdown 化を前提とした次プロジェクトへ進行
- **価値なし**：変換コストに見合わないと判断し、終了
- **保留**：追加材料が必要と判断

※ 結論は Yes / No に限られない。

---

## 11. Roadmap × Design_playwright 対応表（参考）

| Roadmap フェーズ | Design_playwright 節            |
| ------------ | ------------------------------ |
| F2           | 3.1 / 5（Page Object / Locator） |
| F3           | 2 / 6（Test Level / Wait 設計）    |
| F4           | 7 / 8（Test Data / Log）         |
| F5           | 9（CI）                          |
| F6           | 4（LGWAN）                       |

---

## 📌 総括（v1.4）

- F7-C までで **運用安全性の検証は完了**
- F8 を **「Markdown 化の価値判断」に特化した単独フェーズとして新設**
- 自動化は **判断の前提作業として限定的に位置づけ**
- 評価・CI・最適化を持ち込まないことで、目的の純度を維持

本 Roadmap v1.4 は、

> **HTML→Markdown 変換というコストを払う価値があるかを、
> 実運用に近い QA 利用ログを通じて判断する**

という本プロジェクトの真の目的を、
**初めて正確に包含したロードマップ**である。

---
