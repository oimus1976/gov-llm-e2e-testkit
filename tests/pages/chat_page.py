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
    SUBMIT_BUTTON_SELECTORS = (
        "#chat-send-button",
        "[data-testid='chat-send']",
        "button[type='submit']",
    )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(
        self,
        message: str,
        *,
        evidence_dir: Optional[Path] = None,
        wait_for_blue: bool = False,
        blue_wait_timeout_sec: float = 10.0,
        ack_timeout_sec: float = 3.0,
        timeline_poll_ms: int = 100,
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

            if wait_for_blue:
                submit_button, selected_selector, candidates = self._collect_submit_candidates()
                diagnostics.update(
                    {
                        "submit_candidates": candidates,
                        "submit_button_selector": selected_selector,
                        "submit_wait_mode": "wait_for_blue",
                        "submit_blue_timeout_sec": blue_wait_timeout_sec,
                        "submit_ack_timeout_sec": ack_timeout_sec,
                        "submit_timeline_poll_ms": timeline_poll_ms,
                    }
                )

                if submit_button is None:
                    diagnostics.update(
                        {
                            "ui_ack": False,
                            "reason": "submit_button_not_found",
                        }
                    )
                    sent_at = datetime.now(timezone.utc)
                    return SubmitReceipt(
                        submit_id=submit_id,
                        sent_at=sent_at,
                        ui_ack=False,
                        diagnostics=diagnostics,
                    )

                wait_result = self._wait_for_submit_blue(
                    submit_button,
                    timeout_sec=blue_wait_timeout_sec,
                    poll_ms=timeline_poll_ms,
                )
                diagnostics.update(wait_result)

                if wait_result.get("first_blue_ms") is None:
                    diagnostics.update(
                        {
                            "ui_ack": False,
                            "reason": "blue_never_observed_timeout",
                        }
                    )
                    sent_at = datetime.now(timezone.utc)
                    return SubmitReceipt(
                        submit_id=submit_id,
                        sent_at=sent_at,
                        ui_ack=False,
                        diagnostics=diagnostics,
                    )

                click_result = "ok"
                clicked_at_ms = int(wait_result.get("first_blue_ms") or 0)
                try:
                    clicked_at_ms = int(
                        (time.time() - wait_result["start_time"]) * 1000
                    )
                    submit_button.click()
                except Exception as exc:
                    click_result = f"error: {exc}"

                diagnostics.update(
                    {
                        "clicked_at_ms": clicked_at_ms,
                        "click_result": click_result,
                    }
                )

                if click_result != "ok":
                    diagnostics.update(
                        {
                            "ui_ack": False,
                            "reason": "submit_click_failed",
                        }
                    )
                    sent_at = datetime.now(timezone.utc)
                    return SubmitReceipt(
                        submit_id=submit_id,
                        sent_at=sent_at,
                        ui_ack=False,
                        diagnostics=diagnostics,
                    )

            else:
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
            ui_ack = self._wait_for_input_clear(
                input_box, max_wait_sec=ack_timeout_sec
            )
            if not ui_ack and wait_for_blue:
                diagnostics["reason"] = "submit_ack_timeout"

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

    def _collect_submit_candidates(self):
        candidates = []
        selected = None
        selected_selector = None
        for selector in self.SUBMIT_BUTTON_SELECTORS:
            locator = self.page.locator(selector)
            try:
                count = locator.count()
            except Exception:
                count = 0
            candidates.append({"selector": selector, "count": count})
            if selected is None and count > 0:
                selected = locator.first
                selected_selector = selector
        return selected, selected_selector, candidates

    def _wait_for_submit_blue(self, locator, *, timeout_sec: float, poll_ms: int) -> Dict[str, Any]:
        start = time.time()
        timeline = []
        first_gray_ms = None
        first_blue_ms = None
        last_snapshot = None

        while time.time() - start < max(timeout_sec, 0.1):
            t_ms = int((time.time() - start) * 1000)
            try:
                class_attr = locator.get_attribute("class") or ""
            except Exception:
                class_attr = ""
            try:
                disabled = locator.is_disabled()
            except Exception:
                disabled = False

            state = self._resolve_submit_state(class_attr, disabled)
            snapshot = (state, class_attr, disabled)
            if snapshot != last_snapshot:
                timeline.append(
                    {
                        "t_ms": t_ms,
                        "class": class_attr,
                        "disabled": disabled,
                        "state": state,
                    }
                )
                last_snapshot = snapshot

            if state == "gray" and first_gray_ms is None:
                first_gray_ms = t_ms
            if state == "blue" and first_blue_ms is None:
                first_blue_ms = t_ms
                break

            time.sleep(max(poll_ms, 10) / 1000.0)

        return {
            "start_time": start,
            "first_gray_ms": first_gray_ms,
            "first_blue_ms": first_blue_ms,
            "submit_timeline": timeline,
        }

    @staticmethod
    def _resolve_submit_state(class_attr: str, disabled: bool) -> str:
        class_lower = (class_attr or "").lower()
        is_blue = "blue" in class_lower
        is_gray = "gray" in class_lower or "grey" in class_lower
        if disabled and not is_blue:
            is_gray = True
        if is_blue and not disabled:
            return "blue"
        if is_gray:
            return "gray"
        return "unknown"

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
