# Design_answer_probe_api_v0.1

pytest から Answer Detection Layer（probe）を正規利用する最小API設計

* Project: gov-llm-e2e-testkit
* Phase: B（Basic RAG Test v0.1）
* Status: **Design（Approved Spec v0.1 に基づく）**
* Date: 2025-12-14

---

## 0. Authority（根拠）

本設計は、承認済みの **Spec_answer_probe_api_v0.1** に従う。
本設計は「新機能」ではなく、既存の Answer Detection Layer（probe）を **pytest から正規に呼ぶための最小接点**を定義する。

---

## 1. Purpose（目的）

* pytest（Basic RAG Test）から、submit 後の **answer_text（raw）** を取得できるようにする
* DOM/UI に依存せず、完了意味論は **probe に委譲**する
* 取得できない場合は **例外で観測事実として扱う**（理由の推測はしない）
* v0.1 では **evidence_dir への保存を行わない**（動作確認優先）

---

## 2. Scope（適用範囲）

### In Scope

* `src/answer_probe.py`（pytest から import 可能な入口）を追加
* `wait_for_answer_text()` の API と、例外体系を定義
* probe 既存実装の呼び出しを **ラップする**（再実装しない）

### Out of Scope

* UI/Dom を用いた完了判定
* ChatPage / submit の変更
* keyword 判定（テスト側責務）
* Result 型の必須化（将来検討：v0.2 以降）
* evidence_dir 等への証跡保存（v0.1では不採用）

---

## 3. Responsibility Boundary（責務境界）

### MUST

* submit_id / chat_id を受け取り、probe の完了検知に従って answer_text を取得する
* timeout を設け、無限待ちを防止する
* 取得できない場合は **観測事実として例外**を投げる（推測しない）

### MUST NOT

* DOM/UI から完了を判定しない
* probe の完了意味論をこの層で再定義しない
* 「なぜ取れないか」を推測して断定しない
* 証跡ファイル保存を v0.1 で必須化しない（※明示的に不採用）

---

## 4. Public API（公開API）

### 4.1 Module

* `src/answer_probe.py`

### 4.2 Function（v0.1）

```python
def wait_for_answer_text(
    *,
    submit_id: str,
    chat_id: str,
    timeout_sec: int = 60,
    poll_interval_sec: float = 1.0,
) -> str:
    """
    - probe を利用し、submit_id / chat_id に対応する完了済み回答テキスト（raw str）を返す
    - v0.1 では証跡保存は行わない
    """
```

#### Parameters

* `submit_id`（必須）: ChatPage.submit の送信試行キー
* `chat_id`（必須）: 観測対象チャット境界
* `timeout_sec`（任意/既定 60）: v0.1 では運用で調整（既定は固定）
* `poll_interval_sec`（任意/既定 1.0）: 監視間隔（最適化は非目標）

#### Returns

* `answer_text: str`（非空が期待値）

---

## 5. Exception Model（例外体系）

v0.1 は **例外ベース**（承認済み判断）。

### 5.1 Exceptions

* `AnswerTimeoutError`

  * timeout_sec 経過までに完了観測ができなかった（原因は推測しない）
* `AnswerNotAvailableError`

  * 観測はできたが、answer_text が取得できない／空（観測事実）
* `ProbeExecutionError`

  * probe 呼び出し自体が失敗（I/O、内部例外など）
  * 例外チェーン（cause）を保持する

### 5.2 Usage expectation（pytest側）

* Basic RAG Test はこれら例外を捕捉し、**Inconclusive** としてログ化できる（FAIL断定しない）

---

## 6. Completion Semantics（完了意味論）

本APIは完了意味論を自前定義しない。
完了は **Answer Detection Layer（probe）** の意味論に委譲する。

* Primary: REST 由来の観測を正とする（probe設計に従う）
* Secondary: GraphQL は補助（観測できるなら記録対象、ただし v0.1 は返値 str のみ）

---

## 7. Internal Design（内部設計）

### 7.1 Adapter（内部抽象：実装依存の隔離）

v0.1 では「probe の既存コード」を直接参照する前提だが、
pytest から見える入口（answer_probe）を安定させるため、内部では薄いアダプタ層を置く。

#### Internal interface（設計上の形）

```python
class _ProbeClient:
    def wait_for_answer_text(self, submit_id: str, chat_id: str, timeout_sec: int, poll_interval_sec: float) -> str:
        ...
```

* `_ProbeClient` の具体実装が「既存 probe 実装の呼び出し」に責務を持つ
* v0.1 は最小でよい（将来差し替え可能にするための形）

### 7.2 “既存probe実装”の利用方針

* answer_probe は **probe を再実装しない**
* 既存の probe 実装（scripts / src 内の現物）から、必要最小の呼び出し単位を利用する
* どの関数・クラスを呼ぶかは **一次情報（現行コード）を見て確定**する（推測しない）

---

## 8. No Evidence Saving in v0.1（v0.1 では証跡保存しない）

承認済み判断により、v0.1 は以下を採用する。

* `evidence_dir` 引数を **公開APIに含めない**
* probeログ・jsonlコピー等の保存処理を **実装しない**
* 動作確認と責務分離の成立を優先し、証跡は v0.2 以降で検討する

---

## 9. Files & Placement（作成・変更対象）

### 9.1 New

* `src/answer_probe.py`（公開API + 例外 + 内部アダプタ）

### 9.2 Modify（接続）

* `tests/rag/test_rag_basic_v0_1.py`

  * `from src.answer_probe import wait_for_answer_text` を成立させる
  * 例外捕捉（Inconclusive）を導入するかは v0.1 実装時に判断（テスト仕様と整合させる）

---

## 10. Acceptance Criteria（受入条件）

1. pytest から `src.answer_probe.wait_for_answer_text` を import できる
2. submit 後の回答テキストを取得できる（少なくとも1ケース）
3. timeout は `AnswerTimeoutError` として観測事実で扱える
4. DOM/UI に依存しない（answer_probe が DOM を触らない）
5. 既存 probe 実装を破壊しない（再実装しない）

---

## 11. Open Items（一次情報で確定する項目）

※ここは推測せず、現行コード確認で確定する。

* probe の“呼び出し単位”の確定（どのモジュール/関数をラップするか）
* 取得する answer_text の定義（raw textの取り出し箇所・整形有無：基本は整形なし）
* timeout/poll の実装方式（sleep + 再取得、既存probeに依存、など）

---

## 12. Non-Goals（明示的にやらないこと）

* Result 型必須化（v0.2以降の検討事項）
* evidence_dir 保存（v0.2以降の検討事項）
* 相関 state / CI presentation semantics の導入（Phase B v0.1 では扱わない）

---
