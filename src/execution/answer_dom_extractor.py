from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re

from bs4 import BeautifulSoup, Tag


BS_PARSER = "html.parser"


MARKDOWN_ID_PATTERN = re.compile(r"^markdown-(\d+)$")
NOISE_TAGS = {"svg", "button", "form", "textarea", "nav", "aside"}


@dataclass
class MarkdownCandidate:
    n: int
    element: Tag
    raw_id: str


@dataclass
class DomExtractionObservation:
    candidates: List[int]
    selected: bool
    selected_n: Optional[int]
    parity: Optional[str]
    anchor_dom_selector: Optional[str]
    reason: str
    text_len: int
    errors: List[str]


@dataclass
class ExtractionResult:
    extracted_status: str  # VALID | INVALID
    text: str  # HTML from anchor DOM (empty when INVALID)
    raw_html: str  # minimally cleaned anchor DOM
    raw_text: str  # text content from raw_html
    anchor_dom_selector: Optional[str]
    observation: DomExtractionObservation


# ------------------------------------------------------------
# Existing logic (unchanged)
# ------------------------------------------------------------


def _find_message_received_scope(
    soup: BeautifulSoup,
) -> Tuple[Optional[Tag], List[str]]:
    containers = soup.select(".message-received")
    if not containers:
        return None, ["no message-received elements observed"]
    return containers[-1], []


def _parse_markdown_candidates(html: str) -> Tuple[List[MarkdownCandidate], List[str]]:
    soup = BeautifulSoup(html, BS_PARSER)
    scope, scope_errors = _find_message_received_scope(soup)
    return _parse_markdown_candidates_from_scope(scope, scope_errors)


def _parse_markdown_candidates_from_scope(
    scope: Optional[Tag], initial_errors: List[str]
) -> Tuple[List[MarkdownCandidate], List[str]]:
    candidates: List[MarkdownCandidate] = []
    errors: List[str] = list(initial_errors)

    if scope is None:
        return candidates, errors

    for div in scope.select("div.markdown"):
        raw_id = div.get("id")
        if not isinstance(raw_id, str):
            errors.append("div.markdown missing id")
            continue

        match = MARKDOWN_ID_PATTERN.fullmatch(raw_id.strip())
        if not match:
            errors.append(f"invalid markdown id: {raw_id}")
            continue

        try:
            n = int(match.group(1))
        except Exception:
            errors.append(f"non-numeric markdown id: {raw_id}")
            continue

        candidates.append(MarkdownCandidate(n=n, element=div, raw_id=raw_id))

    return candidates, errors


def _select_latest_even(
    candidates: List[MarkdownCandidate],
) -> Optional[Tuple[MarkdownCandidate, str]]:
    if not candidates:
        return None

    sorted_desc = sorted(candidates, key=lambda c: c.n, reverse=True)
    max_n = sorted_desc[0].n

    for candidate in sorted_desc:
        if candidate.n % 2 == 0:
            parity_note = "even-max" if candidate.n == max_n else "fallback-to-even"
            return candidate, parity_note

    return None


def _extract_candidate_text(candidate: MarkdownCandidate) -> Optional[str]:
    """
    Extract HTML (non-converted) from selected DOM candidate.
    """
    try:
        clone = _clone_scope_for_cleaning(candidate.element)
        if clone is None:
            return None
        return clone.decode()
    except Exception:
        return None


def _clone_scope_for_cleaning(target: Tag) -> Optional[Tag]:
    try:
        fragment = BeautifulSoup(str(target), BS_PARSER)
        return fragment.find()
    except Exception:
        return None


def _apply_noise_filters(root: Tag) -> None:
    for tag_name in NOISE_TAGS:
        for element in root.find_all(tag_name):
            element.decompose()

    for element in root.find_all(attrs={"role": "button"}):
        element.decompose()


def _serialize_clean_html(target: Tag) -> Tuple[str, str]:
    """
    Return (html, text_content) after structural noise removal.
    """
    clone = _clone_scope_for_cleaning(target)
    if clone is None:
        return "", ""

    _apply_noise_filters(clone)
    text_content = clone.get_text(strip=True)
    return clone.decode(), text_content


def _serialize_raw_html(target: Tag) -> Tuple[str, str]:
    """
    Return minimally cleaned anchor DOM (HTML + text).
    """
    return _serialize_clean_html(target)


def extract_answer_dom(html: str, question_text: str) -> ExtractionResult:
    soup = BeautifulSoup(html or "", BS_PARSER)
    scope, scope_errors = _find_message_received_scope(soup)

    candidates, candidate_errors = _parse_markdown_candidates_from_scope(
        scope, scope_errors
    )
    candidate_ns = [c.n for c in candidates]

    selection = _select_latest_even(candidates) if candidates else None

    anchor_dom_selector: Optional[str] = None
    if selection is not None:
        candidate, parity_note = selection
        target_element = candidate.element
        selection_reason = f"selected markdown-{candidate.n} ({parity_note})"
        selected_n = candidate.n
        anchor_dom_selector = (
            f"div.markdown#{candidate.raw_id}"
            if candidate.raw_id
            else f"div.markdown:nth-of-type({candidate.n})"
        )
    elif scope is not None:
        target_element = scope
        parity_note = "fallback-to-scope"
        selection_reason = (
            "fallback to message-received scope (no markdown candidates selected)"
        )
        selected_n = None
        anchor_dom_selector = ".message-received:last-of-type"
    else:
        target_element = None  # type: ignore[assignment]
        parity_note = None
        selection_reason = "no message-received elements observed"
        selected_n = None

    errors: List[str] = list(candidate_errors)

    raw_html = ""
    raw_text = ""
    extracted_html = ""

    if target_element is not None:
        raw_html, raw_text = _serialize_raw_html(target_element)
        extracted_html, _ = _serialize_clean_html(target_element)

    if target_element is None:
        errors.append(selection_reason)
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=False,
            selected_n=None,
            parity=None,
            anchor_dom_selector=None,
            reason="; ".join(errors),
            text_len=0,
            errors=errors,
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            raw_html=raw_html,
            raw_text=raw_text,
            anchor_dom_selector=None,
            observation=observation,
        )

    if not extracted_html.strip():
        errors.append("extracted html empty after noise removal")
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=selection is not None,
            selected_n=selected_n,
            parity=parity_note,
            anchor_dom_selector=anchor_dom_selector,
            reason="; ".join(errors) if errors else selection_reason,
            text_len=0,
            errors=errors,
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            raw_html=raw_html,
            raw_text=raw_text,
            anchor_dom_selector=anchor_dom_selector,
            observation=observation,
        )

    reason_components = [selection_reason] + errors
    observation = DomExtractionObservation(
        candidates=candidate_ns,
        selected=True,
        selected_n=selected_n,
        parity=parity_note,
        anchor_dom_selector=anchor_dom_selector,
        reason="; ".join(reason_components) if reason_components else selection_reason,
        text_len=len(extracted_html),
        errors=errors,
    )
    return ExtractionResult(
        extracted_status="VALID",
        text=extracted_html,
        raw_html=raw_html,
        raw_text=raw_text,
        anchor_dom_selector=anchor_dom_selector,
        observation=observation,
    )


def collect_dom_candidates(html: str) -> Tuple[List[dict], List[str]]:
    """
    Enumerate plausible answer containers for forensics (non-evaluative).
    (Unchanged legacy behavior)
    """
    soup = BeautifulSoup(html or "", BS_PARSER)
    scope, scope_errors = _find_message_received_scope(soup)

    serialized: List[dict] = []
    errors: List[str] = list(scope_errors)

    if scope is None:
        return serialized, errors

    for idx, div in enumerate(scope.select("div.markdown")):
        raw_id = div.get("id")
        classes = div.get("class", [])
        role = div.get("role")

        try:
            text_content = div.get_text(separator="\n", strip=False)
        except Exception:
            text_content = ""

        candidate = {
            "selector_path": f"div.markdown:nth-of-type({idx + 1})",
            "tag": div.name or "",
            "id": raw_id if isinstance(raw_id, str) else None,
            "classes": classes if isinstance(classes, list) else [],
            "role": role if isinstance(role, str) else None,
            "text_len": len(text_content),
            "preview": text_content[:200],
        }

        serialized.append(candidate)

    if not serialized and not errors:
        errors.append("no div.markdown elements within message-received")

    return serialized, errors


# ====== End of File ======
