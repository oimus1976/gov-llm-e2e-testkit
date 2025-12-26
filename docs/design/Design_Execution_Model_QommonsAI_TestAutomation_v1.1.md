---
title: Design Execution Model for Qommons.AI Test Automation
version: v1.1
status: active
category: design
scope: Qommons.AI Test Automation
related:
  - PROJECT_GRAND_RULES.md
  - AI_Development_Standard.md
  - Ops_Web_VSCode_Roundtrip_Guide_v1.1.md
  - Protocol_Web_VSCode_Roundtrip_v1.1.md
---

## 1. 本文書の目的と位置づけ

本ドキュメントは、  
**Qommons.AI テスト自動化プロジェクトにおける AI（ChatGPT / Codex）参加前提を整理した共有文書**である。

- これまでの設計議論・運用議論を集約する
- 「何を合意済みとするか」を明確にする
- 実装・運用のたびに議論を蒸し返さないための基準とする

本書は「最終仕様」ではないが、  
**v1.1 時点での公式な共通認識（Design Judgment）**として扱う。

---

## 2. 本文書と他ドキュメントの関係

本ドキュメントは、本プロジェクトにおける  
**実行モデル（Execution Model）を定義する上位設計文書**である。

- 日々の具体的な作業手順は  
  `Ops_Web_VSCode_Roundtrip_Guide_v1.1.md` に委ねる
- AI（ChatGPT / Codex）との実際のやり取りで使用する  
  厳密な入出力形式・順序・完了条件は  
  `Protocol_Web_VSCode_Roundtrip_v1.1.md` に定義する

本書は、それら下位文書の内容を再定義せず、  
**責務境界・前提条件・設計判断のみを固定する**。

---

## 3. プロジェクトの基本前提

### 3.1 対象システム

- Qommons.AI 上で提供されるチャット / RAG 機能
- 職員・利用者が UI を通じて操作するシステム

### 3.2 技術スタック

- pytest
- Playwright（UI / E2E）
- GitHub Actions（CI）
- Python（python.org 版 + venv）

### 3.3 基本思想

- 設計駆動
- 一次情報（コード・ログ・実行結果）重視
- 再現可能性・証跡の確保
- AI は「魔法の自動化」ではなく **運用対象**

---

## 4. Qommons.AI テストの性質（重要）

### 4.1 UI を含む

- API 単体では評価できない
- 入力・送信・表示・遷移を含むため、UI テスト（Playwright）が不可欠

### 4.2 RAG を含む

- 外部文書・インデックス・検索状態に依存
- 同じ入力でも内部状態により結果が変わりうる

### 4.3 非決定性を含む

- 生成 AI の性質上、完全一致テストは不可能
- 評価は以下を中心に行う：
  - 条件充足（含まれる／含まれない）
  - 振る舞いの観測
  - 実行結果の記録

**→ 本プロジェクトのテストは  
「正解を断定するテスト」ではなく  
「振る舞いを観測・検証・記録するテスト」である。**

---

## 5. Web版 / VS Code / Codex の役割分担

### 5.1 Web版 ChatGPT

**役割**

- 司会
- 設計整理
- 裁定者

**責務**

- 設計意図・前提条件の言語化
- 確定事項／禁止事項の明文化
- VS Code 作業結果の裁定（/critic）
- PROJECT_STATUS / CHANGELOG 反映判断

**やらないこと**

- 実装
- pytest 実行

---

### 5.2 VS Code 拡張（Codex）

#### チャットモード

- 権限：read-only
- 主用途：
  - コード読解
  - diff 案提示
  - 設計逸脱チェック
- 原則：常用モード

#### エージェントモード

- 権限：write-enabled
- 主用途：
  - 機械的修正
  - typo
  - 自明な変更
- 位置づけ：
  - 原則禁止ではない
  - ただし常用しない
  - 実行後は必ずレビューする

---

## 6. Web版 ↔ VS Code 往復運用

### 6.1 基本フロー

```text
Web版（設計・裁定）
↓ 実装ブリーフ
VS Code（実装補佐・レビュー）
↓ 作業要約
docs/vscode_logs（証跡）
↓
Web版（/critic・裁定）
↓
PROJECT_STATUS / CHANGELOG（公式宣言）
```

### 6.2 プロンプトの扱い

- プロンプトは「例」ではなく **制御インターフェース**
- 改変は原則禁止
- 曖昧化＝運用破綻

---

## 7. /critic の定義

- 対象：
  - 事実誤認
  - 推測混入
  - 過剰修正
  - 設計逸脱
  - 判断根拠不備
- 対象外：
  - 人格
  - 文体
- 使用条件：
  - Web版のみ
  - 裁定フェーズ専用

---

## 8. VS Code 作業ログの資産化

- チャット全文は保存しない
- 保存対象：
  - VS CODE 作業要約のみ
- 保存先：

```
docs/vscode_logs/YYYY-MM-DD_<context>.md
```

- 保存後は必ず：
- git add
- git commit
- git push
- STATUS / CHANGELOG 反映要否確認

---

## 9. Markdown 保存に関する前提

- Codex チャットは Markdown 形式で直接エクスポートできない
- UI ログを資産にしようとしない
- 必要な場合は AI に Markdown を再生成させる
- BEGIN / END マーカー方式を使用する

---

## 10. pytest 実行に関する合意（重要）

### 10.1 pytest 実行は必須

- 設計レビューや机上テストだけでは不十分
- **実際にコードが完走するかは実行しないと分からない**
- pytest の実行は品質保証として必須

### 10.2 実行責務の分離

- Codex が pytest を実行可能な場合  
→ Codex が実行し、結果を報告する
- Codex が pytest を実行不可な場合（Playwright 等）  
→ **Codex はその事実を明示し、人間に実行を要求する**

**→ Codex の責務は  
「pytest を実行しない」ことではなく  
「pytest を実行させずに終わらせない」ことである。**

---

## 11. pytest レイヤ分割設計

### 11.1 レイヤ定義

| レイヤ | Codex | 人間 | 内容 |
|-------|-------|------|------|
| unit  | ⭕ | ⭕ | 純ロジック |
| basic | ⭕ | ⭕ | RAG / API / I/O |
| e2e   | ❌ | ⭕ | Playwright / UI |

### 11.2 ディレクトリ構成

```
tests/
├─ unit/
├─ basic/
├─ e2e/
│   └─ conftest.py（Playwright 専用）
└─ pytest.ini
````

### 11.3 Codex 実行範囲

```bash
pytest -m "unit or basic"
````

---

## 12. Python 実行環境（Windows）

- Microsoft Store 版 Python は使用しない
- python.org 版 + venv を使用
- VS Code で `.venv` を明示選択する

---

## 13. 現在地点（v1.1）

- AI（Codex）は正式メンバーとして参加
- 役割・権限・制約は明文化済み
- 技術的制約（Playwright / pytest / sandbox）は設計に昇格済み
- 運用開始可能な状態

---

## 14. 次フェーズ候補

- 本文書を正式 Design 文書として配置
- 既存 tests/ の unit / basic / e2e 棚卸し
- Codex 用 pytest 実行プロンプトの固定化
- CI（GitHub Actions）との完全整合

---

## 最後に（確認）

この **v1.1** は、

- pytest 実行はマスト
- Agent を過剰に縛らない
- 制約は設計に昇格させる

という立場を **正確に反映**している。

---
