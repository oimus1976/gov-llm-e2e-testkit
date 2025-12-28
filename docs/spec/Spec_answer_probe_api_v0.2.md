---
title: Design_answer_probe_api_v0.2
project: gov-llm-e2e-testkit
phase: Phase B / F8
status: CONFIRMED
version: v0.2
previous_version: Spec_answer_probe_api_v0.1
date: 2025-12-28
owner: Sumio Nishioka
scope: Answer Detection Layer API
canonical: false
related_specs:
  - Design_dom_extraction_c2
  - Design_execution_model
---

# Design_answer_probe_api_v0.2

## 1. Purpose（目的）

本設計書は、pytest および execution layer から
**Answer Detection Layer（probe）を正規に利用するための API 設計**を定義する。

本 API は以下を目的とする。

- 回答生成プロセスに関する **観測事実** を取得する
- 回答生成の **完了検知** を probe に委譲する
- DOM 抽出（F9-C-2）とは **独立した観測レイヤ** を提供する

本 API は **canonical answer を確定する責務を持たない**。

---

## 2. Positioning（位置づけ）

Answer Probe API は以下の特性を持つ。

- **観測レイヤ（observation layer）**
- **正本ではない**
- **DOM 抽出（F9-C-2）とは直交関係**

```text
submit
  ↓
probe (completion / observation)
  ↓
DOM Extraction (C-2, canonical)
```

probe の成否は Extracted（C-2）の成否を決定しない。

---

## 3. Responsibility Boundary（責務境界）

### 3.1 MUST（必須責務）

- Answer Detection Layer（probe）の完了意味論に従う
- 完了が観測された場合、取得可能な raw answer_text を返す
- 取得できない場合、その事実を  
 「観測結果としての状態（exception object を含む）」として表現する
※ 本 API が送出する例外は、上位制御において  
   execution flow を中断することを意味しない
- bounded timeout 内で待機を終了する
- DOM/UI の構造・状態を一切参照しない
- submit と completion の責務分離を侵害しない

### 3.2 MUST NOT（禁止事項）

- DOM から回答本文を抽出しない
- DOM/UI を用いて完了判定を行わない
- F9-C-2 の成否を推測・補完しない
- probe 側で canonical 判定を行わない
- 「なぜ取得できないか」を推定して断定しない

---

## 4. Terminology（用語）

- **submit_id**
  ChatPage.submit が発行する送信試行単位の識別子  
  （v0.2 では相関用のみ、意味論には使用しない）

- **answer_text**
  probe が観測できた raw な回答本文（空でない場合のみ）

- **completion**
  probe が「回答生成が完了した」と観測できた事実  
  ※完了意味論は probe 実装に委譲する

---

## 5. Public API（公開インターフェース）

### 5.1 API 定義（v0.2）

```python
def wait_for_answer_text(
    *,
    page: Page,
    submit_id: str,
    chat_id: str,
    timeout_sec: int = 60,
) -> str:
    """
    Observe answer completion and attempt to retrieve raw answer text.

    This function does not access DOM or UI state.
    Completion semantics are delegated to the probe implementation.
    """
```

### 5.2 引数仕様

|引数|必須|説明|
|---|---|---|
|page|yes|probe が通信観測を行うための Playwright Page|
|submit_id|yes|相関・証跡用識別子（意味論には使用しない）|
|chat_id|yes|対象チャット境界|
|timeout_sec|yes|bounded waiting（秒）|

---

## 6. 戻り値・例外仕様

### 6.1 正常系

- **str（空でない）**
  - probe が取得できた raw answer_text

### 6.2 例外（観測事実）

#### AnswerTimeoutError

- bounded timeout 内に **完了観測ができなかった**
- 原因推定は行わない

#### AnswerNotAvailableError

- 完了に関連する観測は存在するが
- answer_text を取得できなかった

> この例外は **失敗や品質不良を意味しない**
> 「取得できなかったという観測事実」の表明のみを行う

#### ProbeExecutionError

- probe 実行自体が失敗した
- I/O・内部例外等を含む
- 元例外はチェーンで保持される

---

## 7. Relation to DOM Extraction（C-2）

- 本 API は **C-2 に依存しない**
- probe の成功／失敗は Extracted の成否を決定しない
- DOM 抽出は after_answer_ready.html が存在すれば独立に成立する

```text
probe INVALID
  → DOM Extracted VALID はあり得る

probe VALID
  → DOM Extracted INVALID もあり得る
```

---

## 8. Evidence & Logging（証跡）

### MUST

- submit_id
- chat_id
- timeout_sec
- 完了観測の有無
- 取得結果（text / not_available / timeout）

### MAY

- probe 内部ログの保存
- 通信観測ログ（jsonl 等）

※保存形式・場所は本仕様では拘束しない

---

## 9. Compatibility（互換性）

- 既存 probe 実装（v0.2.x）を破壊しない
- ChatPage / execution / DOM 抽出の責務境界を変更しない
- pytest / F8 execution から利用可能であること

---

## 10. Design Invariants（不変条件）

- probe は **canonical source にならない**
- probe は **DOM に触らない**
- probe failure は **execution failure を意味しない**
- 取得できない場合でも **事実として記録される**

---

## 11. Change Log（要点）

- v0.1 → v0.2
  - canonical 性の否定を明文化
  - C-2 との直交関係を明示
  - AnswerNotAvailableError の意味論を再定義
  - chat_id を明示的引数として確定

---

## 12. Status

本設計書は **CONFIRMED** とする。
以後、probe API の実装・修正は本設計に従うこと。

---
