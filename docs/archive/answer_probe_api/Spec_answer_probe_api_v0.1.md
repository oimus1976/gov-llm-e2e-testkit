# Spec_answer_probe_api_v0.1

pytest から Answer Detection Layer（probe）を正規利用するための最小API仕様

- Project: gov-llm-e2e-testkit
- Context: Phase B（Basic RAG Test v0.1 実装開始）
- Status: **SPEC（承認対象）**
- Date: 2025-12-14

---

## 1. Purpose（目的）

本仕様は、pytest（RAG テスト）から **Answer Detection Layer（probe v0.2.x）** を
**責務境界を壊さず、正規に呼び出すための “最小の接点（API）”** を定義する。

この API は「新機能」ではない。既存の probe 機能を、pytest から再利用可能な形に切り出すための入口である。

---

## 2. Background（背景・上位文脈）

- 例規HTML変換プロジェクトのテスト自動化では、
  「UI の成否」ではなく **“実際に返された回答テキスト”** を機械的に取得し判定したい。
- ChatPage.submit は **送信のみ**（回答取得・完了判定をしない）という責務分離が確定している。
- 回答の意味的完了点は Answer Detection Layer（probe）で扱う設計が確定している。
- よって Basic RAG Test（pytest）は
  `submit → probe → answer_text → keyword判定`
  のパイプラインを成立させる必要がある。

---

## 3. Scope（適用範囲）

### In Scope

- pytest から呼び出せる Python API（関数/クラス）を定義する
- 送信（submit）後の **回答テキスト（raw text）** を取得する
- bounded timeout 内で “完了” を待つ（完了意味論は probe に委譲）
- 観測事実（取得できた/できない、取得元、時刻等）を返す

### Out of Scope（非目標）

- UI / DOM の参照・ストリーミング解釈
- ChatPage の変更
- keyword 判定や RAG 品質評価（テスト側の責務）
- 相関 state（Established 等）を CI 表示セマンティクスとして出力すること
  ※内部で観測メタデータとして保持することは許容（後述）

---

## 4. Responsibility Boundary（責務境界）

本APIは、以下を **MUST** / **MUST NOT** とする。

### MUST

- Answer Detection Layer（probe）の意味的完了検知に従い、回答取得を試みる
- 取得できた場合、**raw answer_text** を返す（加工しない）
- 取得できなかった場合、観測事実として「取得できない」を返せる（例外または結果型）
- submit_id を相関キーとして受け取り、ログ・追跡性を確保する
- submit_id を受け取り、probe の完了検知に従って answer_text を取得する
- chat 境界は probe が内部的に確定する

### MUST NOT

- DOM/UI状態から完了を判定しない
- ChatPage や test 層に chat_id 管理責務を持たせない
- ChatPage.submit の責務（送信）に侵入しない
- probe の完了意味論をこのAPI側で再定義しない
- 「なぜ取れないか」を推測して断定しない
- page は probe 呼び出しのための観測コンテキストとして受け取るが、
  answer_probe 自身が DOM/UI 操作や完了判定を行ってはならない

---

## 5. Terminology（用語）

- **submit_id**: ChatPage.submit が発行する送信試行単位の一次キー
- **chat_id**: 対象チャットを識別する ID
- **answer_text**: assistant の最終回答本文（raw text）
- **completion**: “assistant の non-empty content が観測できた” という意味的完了（probeの責務）

---

## 6. Public API（公開インターフェース）

### 6.1 最小関数（MVP）

```python
def wait_for_answer_text(
    *,
    page: Page,
    submit_id: str,
    timeout_sec: int = 60,
    poll_interval_sec: float = 1.0,
) -> str:
    """
    - page は Answer Detection Layer（probe v0.2）が
      response hook を用いて観測を行うために必要
    - wait_for_answer_text 自身は DOM/UI を操作しない
    """
```

#### 引数要件

- `submit_id`（必須）: ChatPage.submit の送信試行キー（v0.1 では probe 呼び出しの識別用途には使用しない）
- `timeout_sec`: 必須（無限待ち防止。デフォルト 60）
- `poll_interval_sec`: 既定 1.0（最適化は非目標。安全な範囲で）
- `evidence_dir`: 任意（証跡保存先。指定時のみ保存）

#### 戻り値要件

- 取得できた場合、**空でない str** を返す

---

### 6.2 例外仕様（テスト層が扱える形）

- `AnswerTimeoutError`
  - `timeout_sec` 経過までに完了観測ができなかった（理由は推測しない）
- `AnswerNotAvailableError`
  - 観測はできたが `answer_text` が取得できない／空（観測事実として）
- `ProbeExecutionError`
  - `probe` 実行自体が失敗（I/Oや内部例外）。原因は例外チェーンで保持

※ Basic RAG Test v0.1 側では、これらを catch して **Inconclusive** としてログ化できる設計とする（FAIL 断定しない）。

---

### 6.3 将来拡張（v0.1 では Optional）

v0.1 の段階では必須ではないが、将来の追跡性のため Result 型を導入する余地を残す。

```python
@dataclass(frozen=True)
class AnswerProbeResult:
    submit_id: str
    chat_id: str
    status: Literal["completed", "timeout", "not_available"]
    answer_text: str | None
    completed_at: datetime | None
    source: Literal["rest", "graphql", "unknown"]
    message_id: str | None
    diagnostics: dict
```

v0.1 では **関数は str を返す**ことを優先し、Result 型は「内部ログ」または v0.2 以降での採用を検討する。

---

## 7. Completion Semantics（完了意味論の参照）

本APIは完了意味論を自前定義しない。
完了は probe 設計（REST を正、GraphQL は補助）に委譲する。

- chat 境界（chat_id）は probe が通信観測から内部的に特定する。
- answer_probe API は chat_id を外部から受け取らない。
- Primary: REST 由来の観測を正とする（probe 設計に従う）
- Secondary: GraphQL は補助（観測できる場合のみ使用）

※本APIは「完了したら答えを返す／完了しないなら timeout」という枠組みのみ提供する。

---

## 8. Evidence & Logging（証跡とログ）

### MUST（最低限）

- submit_id, chat_id, timeout_sec, 実測の経過時間
- 取得結果（status）と answer_text（取得できた場合のみ）
- 取得元（rest/graphql/unknown を観測できた範囲で）

### MAY（任意）

- evidence_dir が与えられた場合、probe観測ログ（jsonl等）のコピー/生成
  ※ただし個人情報・機密の取り扱いは既存ルールに従う

---

## 9. Compatibility（互換性）

- 既存の scripts / sandbox の probe 実装を **破壊しない**
- env_loader / CI / PageObject の責務境界を **変更しない**
- Basic RAG Test v0.1（pytest）から利用できる最小機能を提供する

---

## 10. Acceptance Criteria（受入条件）

以下を満たせば v0.1 は成立とする。

1. pytest から `wait_for_answer_text()` を import できる
2. submit 後に answer_text を取得できる（少なくとも1ケース）
3. timeout の場合、専用例外（AnswerTimeoutError）で観測事実として扱える
4. DOM/UI に依存しない（実装が DOM を触らない）
5. 責務境界（submit と completion の分離）を侵害しない

---

## 11. Open Items（承認前に “未確定として明示” する事項）

以下は v0.1 実装時に、一次情報（現行コード）を見て確定する。

- 既存 probe 実装の呼び出し単位（どの関数を再利用するか）
- 既存ログ形式（jsonl等）を evidence_dir にどう保存するか（コピーか生成か）
- Result 型（AnswerProbeResult）を v0.1 で採用するか（現状は Optional）
- page は v0.1 では必須引数とする
  （probe v0.2 の response hook 依存による設計上の制約）

---

## 12. Approval（承認）

この Spec を承認後、これを **拘束仕様**として
`Design_answer_probe_api_v0.1.md`（設計書）を起こし、実装に進む。
