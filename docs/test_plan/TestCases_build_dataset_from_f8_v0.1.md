---
title: Test Cases for build_dataset_from_f8
project: gov-llm-e2e-testkit
phase: F9-D
status: FIX
version: v0.1
date: 2025-12-30
owner: Sumio Nishioka
---

# 🧪 Test Cases: build_dataset_from_f8

本ドキュメントは、  
`build_dataset_from_f8.py` に対する **人間実行前提の確認テストケース**を定義する。

本テストは以下を目的とする：

- dataset 構築処理が **「束ね専用処理」**として正しく機能していること
- F8 run の成果物（answer.md）が **欠落・破壊・再解釈されない**こと
- CLI オプションのエラーハンドリングが **人間に理解可能な形で提供される**こと

---

## 0. 前提条件（共通）

- 事前に F8 run が 1 回以上成功していること
- 正規形ディレクトリ構造は以下であること：

```text
out/
  f8_runs/
    <run_id>/
      entries/
        Qxx/
          answer.md
````

- dataset 正規形は以下とする：

```text
out/
  datasets/
    <dataset_id>/
      dataset.yaml
      entries/
        Qxx/
          answer.md
```

---

## 2. テストケース一覧

### TC-01: 単一 F8 run から dataset を構築できる

#### 目的

- build_dataset_from_f8 が、正規形 F8 run を入力として dataset を生成できることを確認する

#### 手順

```bash
python -m scripts.build_dataset_from_f8 \
  --f8-run out/f8_runs/<run_id> \
  --dataset-id tc01
```

#### 期待結果

- `out/datasets/tc01/` が生成される
- `dataset.yaml` が存在する
- `entries/Qxx/answer.md` が F8 run と同数生成される
- 例外・Traceback が発生しない

---

### TC-02: verify-diff によりコピー完全性を確認できる

#### 目的

- dataset 側の answer.md が source（F8 run）と **完全一致**していることを確認できる

#### 手順

```bash
python -m scripts.build_dataset_from_f8 \
  --f8-run out/f8_runs/<run_id> \
  --dataset-id tc02 \
  --verify-diff
```

#### 期待結果

- 以下のメッセージが表示される：

```text
verify-diff: all answer.md files match exactly
```

- exit code = 0
- dataset の内容は source と byte-level で一致する

#### 補足

- verify-diff は **差分検出ツールではない**
- コピー処理の完全性を確認するための安全チェックである

---

### TC-03: --latest により最新の F8 run を解決できる

#### 目的

- --latest 指定時に、最新の F8 run が一意に解決されることを確認する

#### 手順

```bash
python -m scripts.build_dataset_from_f8 \
  --latest \
  --dataset-id tc03
```

#### 期待結果

- 最新の F8 run が自動的に選択される
- dataset が正常に生成される
- 実行時に run_id が人間に追跡可能な形で解釈できる

---

### TC-04: --latest と --f8-run の同時指定はエラーになる

#### 目的

- 入力指定の曖昧性を排除できていることを確認する

#### 手順

```bash
python -m scripts.build_dataset_from_f8 \
  --latest \
  --f8-run out/f8_runs/<run_id> \
  --dataset-id tc04
```

#### 期待結果

- 処理は実行されない
- 人間に理解可能なエラーメッセージが表示される
- exit code = 1
- Traceback は表示されない

---

### TC-05: f8_runs が存在しない場合のエラーハンドリング

#### 目的

- --latest 指定時に、F8 run が存在しない場合でも
  CLI が安全に失敗できることを確認する

#### 手順

```bash
python -m scripts.build_dataset_from_f8 \
  --latest \
  --dataset-id tc05 \
  --output-root /tmp/empty-dir
```

#### 期待結果

- 以下の形式のエラーメッセージが表示される：

```text
ERROR: cannot resolve latest F8 run
Reason: f8_runs directory not found: <path>

Hint:
- run F8 first (scripts/run_f8_set1_manual.py)
- or specify --f8-run explicitly
```

- exit code = 1
- Python Traceback は表示されない

---

### TC-06: verify-diff は build 後の dataset を再検証するのみである

#### 目的

- verify-diff が **dataset を再生成・修正しない**ことを確認する

#### 手順

1. dataset を生成
2. 同一コマンドを再度 `--verify-diff` 付きで実行

#### 期待結果

- dataset 内容は変更されない
- verify-diff は比較のみを行う
- 副作用（再コピー・上書き）は発生しない

---

## まとめ

- 本テスト群は、build_dataset_from_f8 を  
  **「束ねるだけの処理」**として安全に運用するためのものである
- 内容評価・意味解釈・差分検出は一切行わない
- すべてのテストは **人間実行前提**であり、
  CI 自動化は将来フェーズで検討する

---
