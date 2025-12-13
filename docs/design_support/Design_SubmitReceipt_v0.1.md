# 📦 Design_SubmitReceipt_v0.1

**Component:** ChatPage.submit v0.6  
**Layer:** PageObject / Submission  
**Status:** Formal Design  
**Version:** v0.1  
**Last Updated:** 2025-12-13

---

## 1. Purpose（目的）

本書は、`ChatPage.submit v0.6` が返却する  
**SubmitReceipt** データ構造を正式に定義する。

SubmitReceipt は、  
- UI 送信責務の完了点  
- submit と probe の責務境界  
を **コードレベルで固定**するための構造体である。

本構造は **意図的に最小化されており、将来的に拡張されることを想定しない**。

---

## 2. Positioning（位置づけ）

- SubmitReceipt は **submit() の唯一の返却型**である  
- 回答完了・意味論・検知結果は **一切含まない**  
- Answer Detection Layer（probe）とは **概念的にも物理的にも分離**される

---

## 3. Design Principles（設計原則）

1. One submit() call → One SubmitReceipt  
2. SubmitReceipt MUST NOT contain completion semantics  
3. SubmitReceipt MUST NOT leak probe-layer concepts  
4. SubmitReceipt is immutable once created  
5. This object is intentionally minimal and not expected to grow

---

## 4. Class Definition（Python）

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Any


@dataclass(frozen=True)
class SubmitReceipt:
    """
    SubmitReceipt represents the result of a single UI submission attempt.

    Design principles:
    - One SubmitReceipt corresponds to exactly one submit() call.
    - This object MUST NOT contain any information about answer completion.
    - This object MUST NOT leak probe-layer concepts.
    - This object is intentionally minimal and not expected to grow.
    """

    # Unique identifier generated inside ChatPage.submit()
    submit_id: str

    # Timestamp when UI acceptance was confirmed
    sent_at: datetime

    # Whether the UI accepted the submission (minimal acknowledgement)
    ui_ack: bool

    # Auxiliary diagnostic information for debugging submission failures
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
```

---

## 5. Field Semantics（フィールド定義）

### 5.1 submit_id : str

* ChatPage.submit 内で必ず生成される
* submit / probe 間の **一次相関キー**
* chat_id / message_id ではない

---

### 5.2 sent_at : datetime

* UI が送信を受理したと確認できた時刻
* ネットワーク完了・回答完了とは無関係
* completion 判定には使用しない

---

### 5.3 ui_ack : bool

* submit 成立性の **唯一の公式フラグ**
* 回答が返らないこととは無関係

---

### 5.4 diagnostics : Mapping[str, Any]

* 失敗時・デバッグ時の補助情報
* probe / CI の判定には使用しない
* 読み取り専用データとして扱う

---

## 6. Explicit Non-Goals（明示的に含めないもの）

SubmitReceipt には以下を **含めてはならない**：

* chat_id
* message_id
* rest_answer / graphql_answer
* completion status / duration
* retry / attempt count
* probe result / verdict

---

## 7. Immutability（不変性）

SubmitReceipt は `frozen=True` により不変である。

生成後に情報を追加・変更することは禁止される。
これにより、submit 後に completion 情報が混入する事故を防止する。

---

## 8. Relation to Other Documents

* Design_ChatPage_submit_v0.6
* Responsibility_Map_v0.1
* Debugging_Principles_v0.2

本書はこれらの設計思想を **データ構造として固定化する役割**を持つ。

---

## 9. Summary

SubmitReceipt は、

* 小さく
* 不変で
* 意味論を持たず
* 境界を破らせない

ための **設計装置**である。

この構造が存在する限り、
ChatPage.submit v0.6 の責務は逸脱しない。


---
