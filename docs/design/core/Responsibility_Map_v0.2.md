---
title: Responsibility Map v0.2
project: gov-llm-e2e-testkit
phase: F9
status: FIX
version: v0.2
previous_version: Responsibility Map v0.1
date: 2025-12-29
owner: Sumio Nishioka
Breaking Change: YES（F9-C 前提）
---

# 📌 Responsibility Map v0.2

**— F9-C 完了反映／F9-D 下流整合フェーズ正式基準 —**

## 0. 本ドキュメントの拘束力

- 本書は F9-C（Extracted 正本化）完了を前提とする
- v0.1 前提の実装・schema・運用とは **非互換**
- 本書に反する実装は **設計違反**とみなす

---

## 1. レイヤ構造（確定）

```text
[ Environment Layer ]（env.yaml / env_loader）
        ↓
[ Execution Layer ]（pytest / conftest / browser/context/page）
        ↓
[ PageObject Layer ]（BasePage / LoginPage / ChatPage）
        ↓
[ Answer Extraction Layer ]   ← 回答の意味はここで確定
        ↓
[ Application / Logging Layer ]（writer / rag_entry / schema）
```

---

## 2. 各レイヤの責務

### 2.1 Environment Layer  

#### （env.yaml / env_loader.py）

**責務：**

- INTERNET / LGWAN のプロファイル管理  
- URL / 認証情報の placeholder 定義  
- ブラウザ timeout（browser/page_timeout）の環境別管理  
- プロジェクト全体の環境変数の唯一の定義場所  
- ENV_PROFILE によるプロファイル切替機構の提供  

**非責務（やってはいけない）：**

- ブラウザの起動  
- ログイン処理  
- UI 操作  
- RAG 検証ロジック  
- pytest 実行順序の制御
---

### 2.2 Execution Layer  

#### （pytest / conftest.py / playwright async）

**責務：**

- Playwright browser / context / page の生成  
- env_loader に基づく timeout/headless の適用  
- page に対する default timeout の注入  
- PageObject へ page を渡す  
- CI（e2e.yml）からの “唯一の実行窓口” となる  
- test_plan に定義された順序に従ってテストを実行する

**非責務：**

- UI ロジック  
- HTML/RAG 検証ロジック（これは Application Test Layer）  
- URL/ユーザー名/パスワードの直書き（必ず env.yaml 経由）

---

### 2.3 PageObject Layer  

#### （BasePage / LoginPage / ChatPage）

---

#### BasePage の責務：

- locator strategies（role/label/testid/css）  
- wait / click / find / fill などの共通関数  
- 汎用的な UI 操作の抽象化

**BasePage の明確な非責務：**

- env.yaml の読み込み  
- timeout の適用  
- Browser/Context/Page の生成  
- URL 生成や遷移制御  
- RAG 検証ロジック  

---

#### LoginPage の責務：

- ログインフォーム操作（ユーザー名/パスワード入力）  
- ログイン開始・ログイン完了の検知  

**LoginPage の非責務：**

- 認証情報の保管（env_loader → pytest が持つ）  
- ページ生成  
- timeout 設定  

---

#### ChatPage の責務：

- チャット送信 / 返信取得  
- 送信ボタンの locator 選択  
- 出力部分の抽象化（response_text を返す等）

**ChatPage の非責務：**

- RAG 検証  
- YAML ケースの読み込み  
- ブラウザ起動  
- 環境設定の取り扱い

---

### 2.4 Answer Extraction Layer（最重要）

**構成要素**

- answer_dom_extractor
- Spec_F9-C_DOM_Scope_Rules

**責務**

1. Anchor DOM を一意に決定する
2. UI 上で「回答として提示された DOM スコープ」を確定する
3. 同一 Anchor DOM を起点として以下を生成する
   - **Answer (Extracted)**
   - **Answer (Raw)**
4. UI ノイズを機械的ルール（tag / role / class / aria）で除外する
5. **Metadata.status（VALID / INVALID）を確定する**

**重要な明文化（共通理解）**

- **Answer (Extracted) は HTML 非変換とする**
- DOM 構造・タグ・順序を保持し、意味的変換を行わない

**非責務（禁止）**

- HTML → Markdown 等の意味変換
- 回答内容の評価・正誤判断
- 下流 schema / writer への配慮
- 抽出責務の下流委譲

**成果物（契約）**

成果物                | 必須性    | 備考                        |
| ------------------ | ------ | ------------------------- |
| Answer (Extracted) | **必須** | 評価入力の唯一の正本（HTML 非変換）      |
| Metadata.status    | **必須** | VALID / INVALID           |
| Answer (Raw)       | 条件付き任意 | status=INVALID の場合 **必須** |

---

### 2.5 Application / Logging Layer

#### F4 writer（write_f4_result）

**責務**

- 上流から渡された **確定済み事実**を記録する
- Markdown 形式の枠組み（answer.md 等）を生成する
- Raw / Extracted を **変換せずそのまま埋め込む**

**入力契約（重要・優先順位付き）**

1. **Raw の生成・保存は最優先**
   - Extracted が欠落していても Raw は必ず記録する
2. Extracted が欠落している場合
   - writer は **評価入力としての書き出しを行ってはならない**
   - Extracted 欠落状態を Metadata に明示する
3. writer は
   - Extracted を補完・推測してはならない
   - VALID / INVALID を新たに判断してはならない

**非責務（禁止）**

- Raw / Extracted の意味解釈
- DOM / HTML の再解釈
- 欠落データの補完

👉 writer は **dumb component + 入力契約遵守** に限定される

---

#### rag_entry / dataset schema

**責務**

- Extracted を **必須フィールド**として定義する
- Metadata.status を必須として保持する
- Raw を補助・証拠データとして扱う

**禁止事項**

- Extracted を optional にしてはならない
- Raw を required にしてはならない
- Raw / Extracted を統合してはならない

---

## 3. 各レイヤ間の責務境界図（ASCII）

[ env.yaml ] ---> [ env_loader ]
                     |
                     | provides config
                     v
-------------------------------------------------

| Execution Layer (pytest / runner)              |
| - browser / context / page lifecycle           |
| - orchestration only                           |
-------------------------------------------------
                     |
                     | inject page
                     v
-------------------------------------------------
| PageObject Layer                               |
| BasePage / LoginPage / ChatPage                |
| - UI operation only                            |
-------------------------------------------------
                     |
                     | provide DOM
                     v
-------------------------------------------------
| Answer Extraction Layer   ★意味確定点★        |
| - Anchor DOM decision                         |
| - Extracted / Raw generation                  |
| - VALID / INVALID decision                    |
-------------------------------------------------
                     |
                     | pass facts only
                     v
-------------------------------------------------
| Application / Logging Layer                   |
| - writer                                      |
| - rag_entry                                   |
| - schema                                      |
| - NO judgment                                 |
-------------------------------------------------

## 4. 原則（拘束）

1. 回答の意味は Answer Extraction Layer 以前で確定する
2. 下流は意味を持たない
3. 下流 FAIL は上流仕様を疑う理由にならない

---

## 5. v0.1 → v0.2 の変更理由

- Extracted 正本化の明文化
- Raw の補助・証拠用途固定
- writer の責務縮退（判断不可）
- 下流 schema の自由度制限

本変更は **破壊的変更**であり、巻き戻しは禁止する。

---

## 6. 本マップの目的

- 誤提案（BasePage に env_loader を入れる等）の防止  
- 設計書 / 実装 / pytest / CI の全整合性の確保  
- 今後の機能追加（v0.2/v1.0）で“どこを触るべきか”を迷わない構造づくり  
- 大規模テスト基盤としての長期保守性向上

---

## Appendix A. トレース例（v0.2）

**— RAG Basic 実行時の責務フロー（観測フェーズ）—**

> 本節は、Responsibility_Map v0.2 に定義された
> 各レイヤの責務が、実行時にどのような順序で関与するかを
> **理解補助として示す参考情報**である。
> 本トレースは責務定義そのものではなく、
> 実装・テストの規範を追加するものではない。

---

### トレース手順

1. pytest が `env.yaml` を読み込む（env_loader）
2. browser / context / page を作成し、timeout 等の実行条件を適用
3. `LoginPage` → `ChatPage` を生成
   （page は Execution Layer から PageObject Layer に注入される）
4. RAG YAML を読み込み、test case を展開
5. `ChatPage.send()` を呼び出し、LLM 応答を取得
6. **Answer Extraction Layer** が以下を実行する
   - Anchor DOM を確定
   - Answer (Extracted) / Answer (Raw) を生成
   - Metadata.status（VALID / INVALID）を確定
7. **Application / Logging Layer** が以下を実行する
   - `answer.md` 等の成果物を生成
   - Extracted / Raw をそのまま記録
8. pytest は
   - 実行が完了したかどうかのみを判定する
   - 回答内容の評価・比較・解釈は行わない
9. CI は pytest の exit code を受け取り、
   成否を上位ジョブに伝達する

---

### 補足（重要）

- 本トレースには
  **expected との比較や品質評価は含まれない**
- 回答の意味確定は
  **Answer Extraction Layer で完結している**
- 下流レイヤは
  **確定済み事実を扱うのみで、判断を行わない**

---

## まとめ（設計意図）

- v0.1 の「Application Test Layer による評価トレース」は
  v0.2 では **適用されない**
- v0.2 における RAG Basic 実行は
  **観測・記録を目的としたフロー**である
- 本トレースは
  **責務分離が正しく機能していることを確認するための
  読解用ガイド**である

---
