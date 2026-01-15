# tests/pages/chat_page.py
#
# ChatPage — Submission API v0.6 (rc2)
#
# Responsibility:
#   - UI submission only
#   - No completion semantics
#   - No answer extraction
#
# Design references:
#   - Design_ChatPage_submit_v0.6
#   - Design_SubmitReceipt_v0.1
#   - Locator_Guide_v0.2
#
# Notes:
#   - Submission uses HTML form submit (semantic & stable).
#   - No button locator is used.
#

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Mapping, Any, Dict
import uuid
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.pages.base_page import BasePage
# ----------------------------------------------------------------------
# IMPORTANT:
# SubmitReceipt MUST be imported from the single source of truth.
# ----------------------------------------------------------------------
from tests.models.submit_receipt import SubmitReceipt  # ← 共通定義（要配置）


# ----------------------------------------------------------------------
# ChatPage
# ----------------------------------------------------------------------

class ChatPage(BasePage):
    """
    ChatPage — UI submission only (v0.6-rc2)

    MUST NOT:
      - judge answer completion
      - access REST / GraphQL
      - parse assistant messages
      - interpret streaming states
    """

    # ------------------------------------------------------------------
    # Locator definitions
    # ------------------------------------------------------------------
    # NOTE:
    # - MESSAGE_INPUT is stable and confirmed.
    # - Submission is performed via HTML form submit (no button locator).
    MESSAGE_INPUT = "#message"  # confirmed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(
        self,
        message: str,
        *,
        evidence_dir: Optional[Path] = None,
    ) -> SubmitReceipt:
        """
        Submit a message via UI and return a SubmitReceipt.

        Completion semantics are explicitly OUT OF SCOPE.
        """

        submit_id = str(uuid.uuid4())

        diagnostics: Dict[str, Any] = {
            "submit_id": submit_id,
            "phase": "ui_submit",
        }

        try:
            # ----------------------------------------------------------
            # 1. Locate input box
            # ----------------------------------------------------------
            input_box = self.page.locator(self.MESSAGE_INPUT)
            input_box.wait_for(state="visible", timeout=self.timeout)

            # ----------------------------------------------------------
            # 2. Fill message
            # ----------------------------------------------------------
            input_box.fill(message)

            # ----------------------------------------------------------
            # 3. Submit via HTML form (semantic & stable)
            #    Prefer requestSubmit(); fallback to Enter key.
            # ----------------------------------------------------------
            try:
                # nearest ancestor <form> from the input box
                form = input_box.locator("xpath=ancestor::form[1]")
                form.evaluate("f => f.requestSubmit()")
            except Exception:
                # Fallback: Enter key triggers form submit
                input_box.press("Enter")

            # ----------------------------------------------------------
            # 4. Minimal UI acknowledgement check
            #    (input box becomes empty)
            # ----------------------------------------------------------
            ui_ack = self._wait_for_input_clear(input_box)

            sent_at = datetime.now(timezone.utc)

            diagnostics.update({
                "ui_ack": ui_ack,
                "sent_at": sent_at.isoformat(),
            })

            return SubmitReceipt(
                submit_id=submit_id,
                sent_at=sent_at,
                ui_ack=ui_ack,
                diagnostics=diagnostics,  # Mapping[str, Any]
            )

        except PlaywrightTimeoutError as e:
            diagnostics.update({
                "error": "timeout",
                "detail": str(e),
            })
            self._capture_evidence(evidence_dir, submit_id)
            raise

        except Exception as e:
            diagnostics.update({
                "error": "unexpected",
                "detail": str(e),
            })
            self._capture_evidence(evidence_dir, submit_id)
            raise

    # ------------------------------------------------------------------
    # Internal helpers (UI-level only)
    # ------------------------------------------------------------------

    def _wait_for_input_clear(self, input_box, *, max_wait_sec: float = 3.0) -> bool:
        """
        Wait until the input box value becomes empty.

        This is the ONLY acknowledgement signal used by submit v0.6.
        """
        start = time.time()

        while time.time() - start < max_wait_sec:
            try:
                value = input_box.input_value()
            except Exception:
                # input box lost → treat as failure
                return False

            if value == "":
                return True

            time.sleep(0.1)

        return False

    def _capture_evidence(
        self,
        evidence_dir: Optional[Path],
        submit_id: str,
    ) -> None:
        """
        Capture minimal evidence on failure.

        Evidence is best-effort and must not affect control flow.
        This method is diagnostic-only and outside submit semantics.
        """
        if evidence_dir is None:
            return

        try:
            evidence_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = evidence_dir / f"submit_failure_{submit_id}.png"
            self.page.screenshot(path=str(screenshot_path))
        except Exception:
            # Evidence capture must never raise
            pass
