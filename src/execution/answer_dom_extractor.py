# src/execution/answer_dom_extractor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import re

from bs4 import BeautifulSoup


MARKDOWN_ID_PATTERN = re.compile(r"^markdown-(\d+)$")


@dataclass
class MarkdownCandidate:
    n: int
    text: str


@dataclass
class ExtractionResult:
    selected: bool
    text: Optional[str] = None
    reason: Optional[str] = None


def parse_markdown_candidates(html: str) -> List[MarkdownCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[MarkdownCandidate] = []

    for div in soup.select("div.markdown"):
        raw_id = div.get("id")
        if not isinstance(raw_id, str):
            continue

        match = MARKDOWN_ID_PATTERN.fullmatch(raw_id.strip())
        if not match:
            continue

        n = int(match.group(1))
        text = div.get_text(separator=" ", strip=True) or ""
        candidates.append(MarkdownCandidate(n=n, text=text))

    return candidates


def select_latest_even(
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


def extract_answer_dom(html: str, question_text: str) -> ExtractionResult:
    candidates = parse_markdown_candidates(html)
    if not candidates:
        return ExtractionResult(
            selected=False,
            reason="no markdown-n candidates",
        )

    selection = select_latest_even(candidates)
    if selection is None:
        return ExtractionResult(
            selected=False,
            reason="no even markdown-n candidates",
        )

    candidate, parity_note = selection
    if not candidate.text.strip():
        return ExtractionResult(
            selected=False,
            reason="selected markdown is empty",
        )

    return ExtractionResult(
        selected=True,
        text=candidate.text,
        reason=f"selected markdown-{candidate.n} ({parity_note})",
    )


# ====== End of File ======
