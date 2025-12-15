# 📘 PROJECT_STATUS v0.6.2 — F4 フェーズ内設計確定

**Last Updated:** 2025-12-15
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 0. フェーズ定義の統一について（再掲・不変）

本プロジェクトのフェーズ定義は、
**Roadmap v1.1 を唯一の正本**として以下に統一する。

| 区分 | 内容 |
| -- | -- |
| F1 | 設計フェーズ |
| F2 | Page Object 実装フェーズ |
| F3 | Answer Detection & テスト基盤構築フェーズ |
| F4 | RAG 評価基準・比較テストフェーズ |
| F5 | CI（e2e.yml）整備フェーズ |
| F6 | LGWAN 対応フェーズ |
| F7 | 運用・保守フェーズ |

※ Phase A / B / C 等の別系統呼称は使用しない。

---

## 1. プロジェクトの現在地（要約）

本プロジェクトは現在、

> **「RAG 評価をどう自動化するか」ではなく
> 「RAG の差分をどう“誤解なく”測るか」**

に集中する段階にある。

F1–F3 で構築された E2E 基盤は完全に凍結され、
F4 においては **評価観点・運用ルール・再現性**が最優先事項となる。

---

## 2. 完了事項（再確認）

### ✅ F1–F3：E2E 基盤フェーズ（完全完了・凍結）

以下は **基盤として完成・変更禁止（freeze）** 状態である。

#### 設計・構造

- Design_playwright_v0.1
- Locator_Guide_v0.2
- Debugging_Principles_v0.2
- PROJECT_GRAND_RULES v4.2

#### 実装

- Environment Layer（env_loader v0.2.3）
- Page Object（Base / Login / Chat）
- ChatPage.submit v0.6
  - UI送信責務のみに限定
  - submit_id / SubmitReceipt 意味論確定

#### Answer Detection

- probe v0.2.1（GraphQL / REST 両対応）
- submit–probe 相関設計 v0.2
- pytest-facing Answer Detection API v0.1r
  - page を受け取る低レベル API 境界を正式採用

#### CI / 可視化

- CI Correlation Summary Presentation Semantics v0.1
- GitHub Actions summary による日本語相関サマリー
- WARN / INFO を FAIL と誤認しない意味論を保証

👉 **E2E 基盤としての完成条件をすべて満たしている**

---

## 3. F4 事前検証（完了）

### ✅ 部署境界プローブ（Design_rag_f4_dept_boundary_probe_v0.1）

- ナレッジ境界が「部署／アカウント単位」で分離されていることを事前検証
- F4 本体において、HTML / Markdown の差分が
  **他ナレッジの混入によって歪まない**ことを確認

---

## 4. Current Phase（現在のフェーズ）

### ▶ F4：RAG 評価基準・比較テストフェーズ（進行中）

本フェーズでは **E2E 基盤を変更しない**。
評価対象はあくまで **RAG の振る舞い差分**である。

#### 確定事項（評価基準）

- **RAG 評価基準 v0.1（正式決定）**
  - Evidence Hit Rate（条例由来語）
  - Hallucination Rate（無根拠表現）
  - Answer Stability（再現性）
- 絶対評価ではなく **差分評価のみ**

#### 確定事項（ログ設計・v0.1.2）

- **Design_pytest_f4_results_writer v0.1.2 を正式採用**
  - F4 手動運用下における評価結果ログの説明責任を明確化
  - Execution Context（任意メタデータ）を設計上導入
- **login_identity の意味論と責務分離を確定**
  - configured：env.yaml 由来の設定値
  - observed：機械的に観測できた場合のみ（未確認可）
  - login_identity の取得・構築は pytest 実行層の責務
  - writer は取得・推測・検証を行わず、記録専用とする

※ 本更新は F4 フェーズ内の設計確定であり、
  評価基準・フェーズ区分・手動運用方針自体は変更していない。

---

## 5. F4 運用ルールの確定（v0.6.1 での更新点）

### 📌 F4 運用ルール v0.1.5 を正式採用

以下を **F4 フェーズにおける固定ルール**として確定した。

#### ナレッジ構成

- HTML 用／Markdown 用ナレッジは **別テストアカウントで管理**
- 同一アカウント内での
  - ナレッジ削除
  - ナレッジ再投入
  は **v0.1 では行わない**

#### Case 運用

- F4 は **最小 3 ケース（Case1–3）**のみで評価
- Case 間でナレッジの差し替えは行わない
- 質問文は **条例IDを必ず含める**ことで一意化する

#### 実行プロファイル

- `profile` は **記録・識別用メタデータ**
- `--f4-profile` は評価結果ログ識別のために使用
- chat / アカウント / ナレッジの切替は **完全手動**

#### ログ運用

- 結果ログは以下を必須要素とする：
  - case_id
  - profile
  - timestamp
- HTML / Markdown の結果は **別ファイルとして保存**

---

## 6. Out of Scope（F4 v0.1 では扱わない）

- chat_name / ナレッジの自動切替
- ナレッジの自動アップロード・削除
- CI への統合
- 意味的同義語・高度な意味理解評価

※ いずれも **v0.2 以降の検討事項**

---

## 7. リスク・注意点（継続認識）

- LLM 応答の非決定性
- 手動運用に起因する人為ミス
- ナレッジ更新タイミングの差異

→ これらは **基盤問題ではなく評価フェーズの制約**として扱う。

---

## 8. 総括

本プロジェクトは現在、

> **「テストが動く」段階を完全に通過し、
> 「評価を誤解なく実施できる」段階に到達した**

状態にある。

F4 v0.1 は、
**人手でも確実に再現できる評価運用**を完成させることを目的とする。

---

### 次の判断ポイント

- F4 実測結果が十分に蓄積された時点で
  F4 v0.2（部分自動化・高度化）へ進むかを判断する。
