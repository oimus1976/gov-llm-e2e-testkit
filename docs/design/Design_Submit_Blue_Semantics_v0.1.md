---
title: "Design_Submit_Blue_Semantics"
version: "v0.1"
status: "frozen"
project: "gov-llm-e2e-testkit"
epic: "F10-A"
scope:
  - diagnostic (run_submit_probe.py)
  - production (run_single_question.py)
decided_at: 2026-01-XX
decision_type: "ui_state_semantics"
owner: "oimus"
related_files:
  - scripts/diagnostic/run_submit_probe.py
  - src/execution/run_single_question.py
  - src/execution/f8_orchestrator.py
tags:
  - submit-gate
  - ui-semantics
  - e2e
  - watchdog
---

# 設計メモ

## Submit Blue Semantics（回答生成完了判定）

### 1. 目的（Why）

F10-A 本番 run において発生していた以下の事故を、**UI 状態に基づく決定的ルール**で防止する。

* 回答生成中に submit が押される
* submit 押下可否の誤判定により、次質問が早期投入される
* 回答クロス汚染（Q17/Q18 同一回答など）

---

### 2. 定義（Decision）

> **本プロジェクトでは、以下を正式定義とする**

**submit ボタンが `blue (text-blue-500)` になった状態 = 回答生成完了**

* 生成途中（streaming / loading 中）は submit は `gray`
* 回答生成が完了すると submit が `blue` に遷移する
* `blue` への遷移は UI 上で一貫して観測され、再現性がある

この定義は **実測（run_submit_probe.py）により確認済み**。

---

### 3. 非定義事項（明示的にやらないこと）

以下は **今回の設計では採用しない**。

* DOM 上の回答本文の長さ・末尾文字による判定
* GraphQL / REST レイヤの完了イベント依存
* 固定 wait（例: 30s / 120s）経過による完了判定

理由：

* 環境差・モデル差に弱い
* 長文時に破綻する
* 検証コストが高い

---

### 4. 判定ロジック（Concept）

#### 状態遷移モデル

```text
gray (busy / generating)
   ↓
blue (ready / generation completed)
   ↓
click submit (immediate)
```

* **gray → blue の遷移がトリガ**
* blue 到達後は「待たない」
* blue 到達後、一定時間 click が発生しなければ watchdog

---

### 5. コードスニペット（検証済みパターン）

#### submit 状態判定（共通関数）

```python
def derive_submit_state(candidates: List[Dict[str, Any]]) -> str:
    # Priority: blue > gray > unknown
    for c in candidates:
        cls = c.get("class") or ""
        if "text-blue-500" in cls:
            return "blue"
    for c in candidates:
        cls = c.get("class") or ""
        if "text-gray-400" in cls and "cursor-not-allowed" in cls:
            return "gray"
    return "unknown"
```

#### 遷移トリガ＋即時 click

```python
if submit_state == "blue" and last_state != "blue":
    click_submit()
```

#### Watchdog（保険）

```python
if blue_seen and elapsed_ms - blue_ts > POST_TRANSITION_WATCHDOG_MS:
    raise SubmitWatchdogError("blue without click")
```

---

### 6. 適用範囲（Scope）

* ✔ run_submit_probe.py（検証用）
* ▶ F10-A 本番 runner（これから移植）
* ✖ pytest Gate1 / Gate2（別途整理）

---

## 本番スクリプトへの実装方針

### 対象ファイル（想定）

* `src/execution/run_single_question.py`
* `src/execution/f8_orchestrator.py`（必要最小限）

---

### 実装ステップ（順番厳守）

#### Step 1. submit-state 判定関数を共通化

* probe で確定した `derive_submit_state` をコピー
* **既存の ui_ack / message_count 判定は削除 or 無効化**

#### Step 2. submit click 条件を一本化

* 条件は **ただ一つ**

```text
submit_state == blue
```

* AND 条件・OR 条件は作らない

---

#### Step 3. watchdog を最小限で導入

* blue 到達後、数秒（例: 3–5s）以内に click されない場合のみ abort
* 通常系では一切待たない

---

#### Step 4. abort 成果物の整理

* abort 時のみ以下を保存

  * submit candidates
  * submit_state
  * elapsed_ms
  * screenshot / html

---
