# src/execution/answer_dom_extractor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re

from bs4 import BeautifulSoup, Tag


BS_PARSER = "html.parser"


MARKDOWN_ID_PATTERN = re.compile(r"^markdown-(\d+)$")


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
    reason: str
    text_len: int
    errors: List[str]


@dataclass
class ExtractionResult:
    extracted_status: str  # VALID | INVALID
    text: str
    observation: DomExtractionObservation


def _collect_data_attributes(element: Tag) -> Dict[str, str]:
    data_attrs: Dict[str, str] = {}
    for attr, value in element.attrs.items():
        if not attr.startswith("data-"):
            continue
        if isinstance(value, list):
            data_attrs[attr] = " ".join(map(str, value))
        else:
            data_attrs[attr] = str(value)
    return data_attrs


def _serialize_markdown_candidate(div: Tag, idx: int) -> Tuple[dict, Optional[str]]:
    raw_id = div.get("id")
    classes = div.get("class", [])
    role = div.get("role")
    data_attrs = _collect_data_attributes(div)

    selector_path = f"div.markdown:nth-of-type({idx + 1})"
    markdown_n: Optional[int] = None
    validation_error: Optional[str] = None

    if isinstance(raw_id, str):
        selector_path = f"div#{raw_id}"
        match = MARKDOWN_ID_PATTERN.fullmatch(raw_id.strip())
        if match:
            try:
                markdown_n = int(match.group(1))
            except Exception:
                validation_error = f"non-numeric markdown id: {raw_id}"
        else:
            validation_error = f"invalid markdown id: {raw_id}"
    else:
        validation_error = "div.markdown missing id"

    try:
        text_content = div.get_text(separator="\n", strip=False)
    except Exception:
        text_content = ""
        if validation_error is None:
            validation_error = "text extraction failed"

    preview = text_content[:200] if isinstance(text_content, str) else ""

    candidate = {
        "selector_path": selector_path,
        "tag": div.name or "",
        "id": raw_id if isinstance(raw_id, str) else None,
        "classes": classes if isinstance(classes, list) else [],
        "role": role if isinstance(role, str) else None,
        "data_attrs": data_attrs,
        "text_len": len(text_content) if isinstance(text_content, str) else 0,
        "preview": preview,
        "markdown_n": markdown_n,
        "valid_markdown_id": validation_error is None and markdown_n is not None,
    }

    return candidate, validation_error


def _find_message_received_scope(soup: BeautifulSoup) -> Tuple[Optional[Tag], List[str]]:
    containers = soup.select(".message-received")
    if not containers:
        return None, ["no message-received elements observed"]
    return containers[-1], []


def _parse_markdown_candidates(html: str) -> Tuple[List[MarkdownCandidate], List[str]]:
    soup = BeautifulSoup(html, BS_PARSER)
    scope, scope_errors = _find_message_received_scope(soup)

    candidates: List[MarkdownCandidate] = []
    errors: List[str] = list(scope_errors)

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

    if not candidates and not errors:
        errors.append("no markdown-n elements within message-received")

    return candidates, errors


def collect_dom_candidates(html: str) -> Tuple[List[dict], List[str]]:
    """
    Enumerate plausible answer containers for forensics (non-evaluative).
    """
    soup = BeautifulSoup(html or "", BS_PARSER)
    scope, scope_errors = _find_message_received_scope(soup)

    serialized: List[dict] = []
    errors: List[str] = list(scope_errors)

    if scope is None:
        return serialized, errors

    for idx, div in enumerate(scope.select("div.markdown")):
        candidate, validation_error = _serialize_markdown_candidate(div, idx)
        serialized.append(candidate)
        if validation_error is not None:
            errors.append(validation_error)

    if not serialized and not errors:
        errors.append("no div.markdown elements within message-received")

    return serialized, errors


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
    Acquire text without normalization to preserve structure (C-5).
    """
    try:
        return candidate.element.get_text(separator="\n", strip=False)
    except Exception:
        return None


def extract_answer_dom(html: str, question_text: str) -> ExtractionResult:
    candidates, errors = _parse_markdown_candidates(html)
    candidate_ns = [c.n for c in candidates]

    if errors:
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=False,
            selected_n=None,
            parity=None,
            reason="; ".join(errors),
            text_len=0,
            errors=errors,
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            observation=observation,
        )

    if not candidates:
        observation = DomExtractionObservation(
            candidates=[],
            selected=False,
            selected_n=None,
            parity=None,
            reason="no markdown-n candidates",
            text_len=0,
            errors=[],
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            observation=observation,
        )

    selection = _select_latest_even(candidates)
    if selection is None:
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=False,
            selected_n=None,
            parity=None,
            reason="no even markdown-n candidates",
            text_len=0,
            errors=[],
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            observation=observation,
        )

    candidate, parity_note = selection
    extracted_text = _extract_candidate_text(candidate)
    if extracted_text is None:
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=True,
            selected_n=candidate.n,
            parity=parity_note,
            reason="text extraction failed (non-modified acquisition not guaranteed)",
            text_len=0,
            errors=[],
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            observation=observation,
        )

    text_len = len(extracted_text)
    if extracted_text.strip() == "":
        observation = DomExtractionObservation(
            candidates=candidate_ns,
            selected=True,
            selected_n=candidate.n,
            parity=parity_note,
            reason="selected markdown text is empty",
            text_len=text_len,
            errors=[],
        )
        return ExtractionResult(
            extracted_status="INVALID",
            text="",
            observation=observation,
        )

    observation = DomExtractionObservation(
        candidates=candidate_ns,
        selected=True,
        selected_n=candidate.n,
        parity=parity_note,
        reason=f"selected markdown-{candidate.n} ({parity_note})",
        text_len=text_len,
        errors=[],
    )
    return ExtractionResult(
        extracted_status="VALID",
        text=extracted_text,
        observation=observation,
    )


# ====== End of File ======
