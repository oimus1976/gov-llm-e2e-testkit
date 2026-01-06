---
title: F10-A 本番 run 手順書（customized_question_set.json → answer.md）
project: gov-llm-e2e-testkit
phase: F10-A
version: v1.0
status: active
last_updated: 2026-01-06
owner: Sumio Nishioka
---

## 0. 目的
条例別カスタマイズ質問セット（JSON）を入力として、F10-A本番 run を実行し、
以下の成果物を run_id 単位で確定生成する。

- out/<run_id>/answer/<ordinance_id>/<question_fs_id>/answer.md
- out/<run_id>/manifest.yaml
- out/<run_id>/execution_meta.yaml
- out/<run_id>/README.md

※ 回答内容の評価・再解釈は行わない（evaluation_performed=false）。

---

## 1. 前提（成立条件）
### 1.1 Git状態
- main が origin/main と一致していること
- working tree clean であること

確認:
```bash
git status
git log --oneline -5
````

### 1.2 入力データ（Git管理外）

* `data/customized_question_sets/` が存在し、条例IDごとのディレクトリがある
* 各条例ディレクトリに `customized_question_set.json` がある

例:

```
data/customized_question_sets/
  ├─ k518RG00000022/
  │   └─ customized_question_set.json
  ├─ k518RG00000059/
  │   └─ customized_question_set.json
  └─ ...
```

確認:

```bash
ls data/customized_question_sets
ls data/customized_question_sets/<条例ID>/customized_question_set.json
```

※ `data/customized_question_sets/` は Git に add/commit しない。

---

## 2. run_id の決定（重複禁止）

run_id は `YYYYMMDD_HHMM_<short_label>` とする。
例: `20260107_0910_golden10x18`

ルール:

* 同じ run_id を再利用しない（上書き防止）
* 迷ったら日時を更新して新規 run_id にする

---

## 3. OUTPUT_ROOT の設定（必須）

### 3.1 PowerShell

```powershell
$env:OUTPUT_ROOT="out/20260107_0910_golden10x18"
```

### 3.2 Git Bash

```bash
export OUTPUT_ROOT=out/20260107_0910_golden10x18
```

確認:

```bash
echo $OUTPUT_ROOT
```

停止条件:

* OUTPUT_ROOT が空なら実行しない。

---

## 4. まずスモーク（単一条例で動作確認）

OOM回避と早期異常検知のため、最初は必ず単一条例で実行する。

実行:

```bash
python scripts/run_question_set.py
```

対話で選ぶ（想定）:

* 単一条例処理（1 ordinance）
* 対象条例IDを指定

実行中チェック（必須）:

* 質問投入時、先頭に `（条例ID：<id>）` が付与されていること

  * 例: `（条例ID：k518RG00000022）この条例の...`

停止条件:

* 条例ID前置が付与されていない → その時点で止めてログを保存する。

---

## 5. 成果物の検証（単一条例スモーク）

### 5.1 ディレクトリ構造

```bash
tree out/20260107_0910_golden10x18
```

最低限の期待:

```
out/<run_id>/
  ├─ answer/
  │   └─ <ordinance_id>/
  │      └─ <question_fs_id>/
  │         └─ answer.md
  ├─ execution_meta.yaml
  ├─ manifest.yaml
  └─ README.md
```

### 5.2 execution_meta.yaml（目視）

必須確認:

* run_id が一致
* executed_at / generated_at がある
* evaluation_performed: false
* ordinance_set / question_pool / execution_account が記録されている（実装の仕様どおり）

### 5.3 manifest.yaml（目視）

必須確認:

* schema_version が `manifest_v0.1`
* `answer.md` への相対パスが列挙される
* question_id と question_fs_id の対応が追える（仕様どおり）

---

## 6. 本番（複数条例を処理）

スモークがOKなら、同様に run_question_set.py を実行し、対話で

* 全条例（all ordinances）
  または
* 複数選択
  を実行する。

OOM対策（推奨）:

* まず「少数条例（2〜3）」→安定確認→残り、の2段階に分割する
* 実行途中でブラウザが重くなったら、いったんプロセス終了→新 run_id で再開

再開ルール:

* 途中で落ちた run は再利用しない（run_id を新しくする）
* 既に生成済みの条例は再実行しない（必要なら次runで除外選択）

---

## 7. 生成物の扱い（Git運用）

### 7.1 コミット対象

* scripts/src/docs などの実装・仕様・手順書

### 7.2 コミットしない

* `data/customized_question_sets/`（入力）
* `out/`（成果物）
* `run/`（もしあれば実行生成物）

---

## 8. 完了条件（Done判定）

* 対象条例すべてについて answer.md が生成されている
* manifest.yaml / execution_meta.yaml / README.md が存在する
* execution_meta.yaml で evaluation_performed=false
* run_id とフォルダ名が一致している

---

## 9. トラブル時の一次情報採取（推測禁止）

必ず保存/共有する:

* 実行コマンド全文
* 直前 50 行のログ
* `tree out/<run_id>`（生成途中でも）
* `execution_meta.yaml` / `manifest.yaml`（生成済みなら）

---

```

---

## 次の最小の一手
この手順書どおりに、まず **単一条例スモーク**をやりましょう。  
あなたの環境だと PowerShell / Git Bash どちらで回します？（コマンドは同じですが、環境変数の設定だけ分岐します）
```
