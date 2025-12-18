# 📘 PROJECT_STATUS v0.6.5

**— F5（CI 整備フェーズ）着手宣言／CI 対象範囲の明確化**

**Last Updated:** 2025-12-18
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 0. フェーズ定義の統一（不変）

本プロジェクトのフェーズ定義は、
**Roadmap v1.2 を唯一の正本**として以下に統一する。

| フェーズ   | 内容                             |
| ------ | ------------------------------ |
| F1     | 設計フェーズ                         |
| F2     | Page Object 実装フェーズ             |
| F3     | Answer Detection & テスト基盤構築フェーズ |
| F4     | RAG 入力差分影響の観測・試験データ提供フェーズ      |
| **F5** | **CI（e2e.yml）整備フェーズ**          |
| F6     | LGWAN 対応フェーズ（保留）               |
| F7     | 運用・保守フェーズ                      |

※ Phase A / B / C 等の暫定呼称は使用しない。

---

## 1. プロジェクトの現在地（要約）

本プロジェクトは現在、

> **「再現可能な E2E テスト基盤（F1–F3）」と
> 「判断材料として利用可能な試金石データ（F4）」が確立された状態で、
> それらを破壊しない最小 CI を構築する段階**

に到達している。

本フェーズ（F5）の目的は、
**品質評価を自動化することではなく、
基盤破壊を即時検知するための CI を整備すること**である。

---

## 2. 完了事項（再確認）

### ✅ F1–F3：E2E 基盤フェーズ（完全完了・Freeze）

以下は **基盤として完成し、変更禁止** 状態である。

#### 設計・統治

* PROJECT_GRAND_RULES v4.2
* Debugging_Principles_v0.2
* Locator_Guide_v0.2
* Design_playwright_v0.1
* Responsibility_Map_v0.1

#### 実装

* Environment Layer（env_loader v0.2.3）
* Page Object（Base / Login / Chat）
* ChatPage.submit v0.6

  * UI 送信責務のみに限定
  * submit_id / SubmitReceipt の意味論確定

#### Answer Detection

* probe v0.2.1（GraphQL / REST 両対応）
* submit–probe 相関設計 v0.2
* pytest-facing Answer Detection API v0.1r

  * page を受け取る低レベル API 境界を正式採用
* 三値判定モデル（PASS / WARN / SKIPPED）

👉 **E2E テスト基盤として完成・凍結済み**

---

## 3. F4 フェーズの到達点（確定）

### ✅ F4 v0.2：試金石データ提供マイルストーン（完了）

F4 の責務は以下に固定されている。

> **HTML / Markdown 等の RAG 入力差分が
> Qommons.AI の応答に与える影響を、
> 他プロジェクトが判断材料として利用可能な
> 「試金石データ」として提供すること**

#### 完了根拠

* Raw / Execution Context / Derived Summary の三層構造を設計・確定
* JSON Schema Draft 2020-12 による構造検証を実施
* 第三者が README のみで利用可能な形で提供可能

#### 明確な非対象（Out of Scope）

* CI 統合
* 自動実行
* 採用／不採用の判断
* 高度な意味理解評価

👉 **F4 は CI 対象ではない（意図的）**

---

## 4. Current Phase（現在のフェーズ）

### ▶ **F5：CI（e2e.yml）整備フェーズ**

本フェーズの目的は、
**GitHub Actions 上で「基盤が壊れていないこと」を
継続的に検証できる状態を作ること**である。

---

## 5. F5 の目的とスコープ（固定）

### 5.1 目的（What）

* Smoke Test / Basic RAG Test を
  GitHub Actions 上で自動実行する
* 基盤破壊（UI 変更・submit/probe 崩壊）を即時検知する
* pytest exit code 5（テスト件数 0）を恒久的に回避する

### 5.2 CI 対象（In Scope）

| テスト種別          | CI 対象 |
| -------------- | ----- |
| Smoke Test     | ✅     |
| Basic RAG Test | ✅     |

### 5.3 CI 非対象（Out of Scope・意図的）

以下は **設計判断として CI に含めない**。

| 項目                       | 理由              |
| ------------------------ | --------------- |
| F4（RAG 評価・試金石データ）        | 手動前提・非決定性・責務外   |
| Advanced RAG（multi-turn） | PASS/FAIL に還元不可 |
| LGWAN 実行                 | 環境未提供（Blocked）  |

👉 「未実装」ではなく **「CI に入れないと決めている」**。

---

## 6. F5 実装方針（最小構成）

* CI は **INTERNET 環境専用**
* `.github/workflows/e2e.yml` を単一 workflow とする
* 実行内容：

  1. Checkout
  2. Python / Playwright セットアップ
  3. Smoke Test
  4. Basic RAG Test
* artifact 出力：

  * ログ
  * スクリーンショット
  * CI summary（日本語）

---

## 7. 既知の制約・リスク（継続認識）

* LLM 応答の非決定性
* UI 変更によるロケータ破壊
* 外部サービス起因の一時失敗

→ これらは **F5 の目的外**であり、
CI 失敗＝品質失敗 と誤解しない設計を維持する。

---

