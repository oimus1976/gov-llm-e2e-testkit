from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Any


@dataclass(frozen=True)
class SubmitReceipt:
    """
    SubmitReceipt represents the result of a single UI submission attempt.

    - One SubmitReceipt corresponds to exactly one submit() call.
    - MUST NOT contain any information about answer completion.
    - MUST NOT leak probe-layer concepts.
    - Intentionally minimal and not expected to grow.
    """

    submit_id: str
    sent_at: datetime
    ui_ack: bool
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
