# Design_run_probe_once_v0.1.1  
**Version:** v0.1.1  
**Status:** Approved  
**Scope:** QA 実行フェーズ専用 “probe 起動スクリプト” の正式設計

---

## 1. Purpose（目的）

本設計書は、Answer Detection Layer（probe v0.2.1）の  
**QA 試験を 1 回だけ実行するための補助スクリプト**  
`run_probe_once.py` の振る舞いを定義する。

probe 本体（`probe_v0_2.py`）は  
**GraphQL createData の観測・回答抽出** を担当するが、

- 「Qommons.AI へのログイン」
- 「チャット画面の準備」
- 「page / chat_id の取得」
- 「probe 実行環境のセットアップ」
- 「実行結果の保存とログの収集」

は probe の責務外であり、  
本スクリプトがそれを担当する。

**目的：QA 実行を再現性高く 1 コマンドで行える状態にする。**

---

## 2. Position in Architecture（アーキテクチャ内の役割）

run_probe_once は  
**Startup Layer（運転層）と probe（観測層）の間を接続する “実行ユーティリティ”**。

```

Startup Template v3.1
└── prepare_chat()   # page / context / chat_id の取得
└── run_probe_once.py      ← 本設計の対象
└── probe_v0_2.run_graphql_probe()
└── sandbox/xhr_probe_YYYYMMDD/

```

**CI と独立し、sandbox 専用ツールとして位置づける。**

---

## 3. Responsibilities（責務）

### 🎯 run_probe_once.py の責務（Do）

1. **Startup Template の prepare_chat() を呼び出す**  
   - ログイン  
   - チャット画面の安定到達  
   - chat_id の取得  
   - Playwright Page/BrowserContext の生成

2. **probe_v0_2.run_graphql_probe(page, chat_id, capture_seconds)** を起動  
   - capture_seconds の標準値は **常に 30 秒**  
   - CLI で変更可能だが、**30 秒を基準とした QA 前提を崩さない**

3. **結果（summary.json, graphql_probe.jsonl）の保存パスを出力する**

4. **終了後、必ずブラウザをクリーンに閉じる（close()）**

5. **例外発生時にも context/browser を確実に破棄する**

6. **exit code を返す（成功: 0 / 失敗: 1）**  
   - QA フェーズでの再試行判定を明確化するため

---

### 🚫 run_probe_once.py の非責務（Don’t）

- probe の内部ロジックを変更しない  
- 回答抽出処理を行わない  
- env_loader の設定を変更しない  
- pytest / CI への統合は行わない  
- ChatPage.ask の代替実装を行わない  
- デバッグ用 DOM キャプチャ機能を持たない（必要なら別モジュール）

---

## 4. Inputs / Outputs（入力と出力）

### ✔ Inputs

| 名称 | 説明 | 取得元 |
|------|------|---------|
| env_loader の設定（URL, EMAIL, PASSWORD） | Qommons.AI へのログイン情報 | env_loader v0.2.3 |
| Playwright browser context | prepare_chat() により生成 | Startup Template v3.1 |
| chat_id | prepare_chat() 内で取得 | ChatPage DOM or API |

※ run_probe_once は **自分で env をロードしない**  
（Startup Template に委譲）

---

### ✔ Outputs

| 出力物 | 形式 | 説明 |
|--------|------|------|
| summary.json | JSON | probe v0.2.1 の集計結果（Schema Freeze） |
| graphql_probe.jsonl | JSON Lines | XHR / GraphQL すべての一次情報 |
| 標準出力 | Text | 保存ディレクトリ、chat_id、probe 時間、exit code |

---

## 5. Flow（処理フロー）

以下が **run_probe_once の正式フロー**：

1. **環境ロード（env_loader v0.2.3）**
2. **prepare_chat() を呼び出し、以下を取得：**
   - `browser`, `context`, `page`
   - `chat_id`（生成されたチャット識別子）

3. **probe_v0_2.run_graphql_probe(page, chat_id, capture_seconds=30)** を実行  
   - CLI 指定があれば capture_seconds を上書き  
   - デフォルト 30 秒は常に QA の基準値

4. **結果ディレクトリ（sandbox/xhr_probe_YYYYMMDD/）を標準出力に表示**

5. **finally ブロックで context / browser を確実に close()**

6. **終了時に exit code を返す（成功:0 / 失敗:1）**

---

## 6. CLI Interface（オプション仕様）

本バージョンでは必要最低限のインタフェースを定義する。

```

python -m sandbox.run_probe_once [--seconds N] [--headless]

```

### Optional Args：

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `--seconds` | 30 | probe の観測時間（QA 基準値） |
| `--headless` | false | Playwright の headless モード切替 |

※ probe 機能には影響しない “実行環境の切替” のみを許可。

---

## 7. Error Handling（エラーハンドリング）

### run_probe_once が扱うべき例外：

- prepare_chat() の失敗  
- probe 実行中の例外  
- Playwright 起動失敗  
- ネットワーク断などの runtime error  

### ポリシー：

1. **例外内容を標準出力へ通知（推測なし）**  
2. **結果ディレクトリ生成が失敗した場合も通知**  
3. **context/browser を必ず close()（finally）**  
4. **プロセス exit code を 1 にして終了する**

---

## 8. Non-functional Requirements（非機能要求）

- Playwright の安定性を損なう処理を行わない  
- probe 本体の速度に影響を与えない  
- DOM 依存ロジックを決して追加しない  
- ログパスのフォーマットは probe 本体と一致させること  
- CI に影響を与えない（sandbox 実行専用）  

---

## 9. Future Extensions（将来拡張）

以下は **v0.1.1 の対象外**：

- probe_batch モード  
- ChatPage.ask v0.6 との統合  
- Test Plan Self-check mode  

---

## 10. Version / Revision

| Version | Description |
|---------|-------------|
| v0.1 | 初版（PENTA review 前） |
| v0.1.1 | PENTA 指摘（標準観測時間の明記、exit code 仕様）を反映した正式版 |

---
