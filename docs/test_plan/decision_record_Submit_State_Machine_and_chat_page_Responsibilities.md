了解。
では **Decision Record の正本としてそのまま保存できる体裁**で、

1. **submit state machine（更新版）**
2. **chat_page.py の責務を各 state に対応付け**
3. **現行 submit click ロジックの検証観点を明示**

までを **文章化して一体化**します。
（＝「設計判断＋責務分離＋今後の実装修正の基準」）

以下は **そのまま `decision_record_*.md` に保存できる内容**です。

---

# Decision Record: Submit State Machine and `chat_page.py` Responsibilities

```yaml
---
title: Decision Record – Submit State Machine and chat_page Responsibilities
version: v0.1
date: 2026-01-14
scope:
  - F10-A
  - submit lifecycle
  - chat_page.py responsibilities
status: accepted
related:
  - decision_record_F10A_Submit_Waiting_v0.2.md
  - decision_record_F10A_execution_context_policy_v0.1.md
---
```

## 1. 背景・問題意識

F10-A 実行において以下の問題が観測された。

- 質問が **投入されていないにも関わらず submit が blue のまま待機**
- submit 監視と質問投入の **順序が保証されていない**
- 無制限待ちにした結果、**状態遷移が成立しないままフリーズ**

原因は、
**submit の状態管理が暗黙的かつ分散しており、state machine として定義されていなかったこと**にある。

この Decision Record は、

- submit lifecycle を **state machine として明示**
- `chat_page.py` の責務を **各 state に対応付け**
- 今後の実装・レビューの **正本基準**を確立する

ことを目的とする。

---

## 2. Submit State Machine（更新版）

### 2.1 State 一覧

```text
[S0] IDLE
[S1] QUESTION_INPUTTING
[S2] QUESTION_COMMITTED
[S3] SUBMIT_DISABLED
[S4] SUBMIT_ENABLED
[S5] SUBMIT_CLICKED
[S6] SUBMIT_ACKED
[S7] SUBMIT_UNACKED
[S8] TERMINAL
```

---

### 2.2 状態遷移図（更新版）

```text
[S0] IDLE
  |
  | start_question()
  v
[S1] QUESTION_INPUTTING
  |
  | input_text()
  | + fire input/change
  v
[S2] QUESTION_COMMITTED
  |
  | observe submit state
  v
[S3] SUBMIT_DISABLED
  |
  | submit turns blue
  v
[S4] SUBMIT_ENABLED
  |
  | click_submit_once()
  v
[S5] SUBMIT_CLICKED
  |
  |----------------------------|
  |                            |
  | ui_ack observed            | ui_ack not observed
  v                            v
[S6] SUBMIT_ACKED        [S7] SUBMIT_UNACKED
  |                            |
  v                            v
[S8] TERMINAL            [S8] TERMINAL
```

---

## 3. `chat_page.py` の責務マッピング

### 原則

- `chat_page.py` は **UI state の観測と操作のみを担当**
- 判断・リトライ・例外制御は **run_single_question / orchestrator 側**
- `chat_page.py` 自身は **state machine を跨がない**

---

### 3.1 State × Responsibility 対応表

| State | chat_page.py の責務 |
| --------------------- | ---------------------------------------- |
| S0 IDLE | 初期 DOM 取得、textarea / submit の locator 準備 |
| S1 QUESTION_INPUTTING | textarea に文字列を入力する |
| S2 QUESTION_COMMITTED | **textarea.value を再取得し一致確認** |
| S3 SUBMIT_DISABLED | submit の class / disabled 状態を観測 |
| S4 SUBMIT_ENABLED | submit が blue であることを検出 |
| S5 SUBMIT_CLICKED | **1 回だけ submit.click() を実行** |
| S6 SUBMIT_ACKED | message count 等の UI 変化を観測（任意） |
| S7 SUBMIT_UNACKED | 観測のみ（判断しない） |
| S8 TERMINAL | UI 操作なし |

---

### 3.2 明確に禁止される責務

`chat_page.py` が **やってはいけないこと**：

- QUESTION_COMMITTED を **仮定する**
- submit が blue かどうかを **質問投入前に判断**
- ui_ack の有無で **例外を投げる**
- retry / timeout / 無限ループ制御

---

## 4. submit click ロジックの正規仕様

submit click は **以下の AND 条件が成立した瞬間にのみ発火**する。

```text
(question_committed == true)
AND
(submit_is_blue == true)
AND
(submit_not_clicked_yet)
```

### 補足

- 「blue を待つ」は **QUESTION_COMMITTED 後のみ**
- submit click は **1 問につき 1 回**
- 失敗しても **再 click はしない**

---

## 5. 現行実装に対する検証観点（次工程）

この Decision Record をもとに、以下を **コードレビューで必ず確認**する。

### 検証ポイント

1. QUESTION_COMMITTED を **明示的に通過しているか**
2. submit 監視開始が **S2 以降になっているか**
3. submit click が **S4 でのみ発火しているか**
4. submit click 前に **質問が DOM に存在することを再確認しているか**
5. ui_ack 不在時に **無限待ちループに入っていないか**

---

## 6. 決定事項（Decision）

- submit lifecycle は **本 state machine を正本とする**
- `chat_page.py` の責務は **UI 観測と操作に限定**
- submit 後の成否は **UNGENERATED / GENERATED として記録するが、abort しない**
- 無制限待ちは **state が前進している場合のみ許容**

---
