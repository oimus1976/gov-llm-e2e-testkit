"""
Offline C-2 DOM extraction verification.

Usage:
- python scripts/verify_dom_extraction_c2.py <after_answer_ready.html>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.execution import answer_dom_extractor as ade

DEFAULT_INPUT = Path(
    "out/f8/20251228/20251228T185721_manual/20251228/manual-test/Q15/after_answer_ready.html"
)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify DOM extraction logic (C-2) using offline HTML."
    )
    parser.add_argument(
        "html_path",
        nargs="?",
        default=str(DEFAULT_INPUT),
        help="Path to after_answer_ready.html",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or [])
    html_path = Path(args.html_path)
    if not html_path.is_file():
        print(f"[ERROR] file not found: {html_path}")
        return 1

    html = html_path.read_text(encoding="utf-8")

    # Scope detection (same parser as extraction).
    soup = BeautifulSoup(html, ade.BS_PARSER)
    message_blocks = soup.select("div.message-received")
    scope = message_blocks[-1] if message_blocks else None
    markdown_blocks = scope.select("div.markdown") if scope is not None else []
    markdown_ids = [md.get("id") for md in markdown_blocks]
    scope_position = len(message_blocks) if scope is not None else None

    extraction = ade.extract_answer_dom(html, question_text="")
    candidates_serialized, candidate_errors = ade.collect_dom_candidates(html)

    selected_n = extraction.observation.selected_n
    parity = extraction.observation.parity or "N/A"
    selection_label = (
        f"markdown-{selected_n} ({parity})" if selected_n is not None else "NONE"
    )

    print(f"HTML_PATH: {html_path}")
    print(f"message_received.count: {len(message_blocks)}")
    if scope is None:
        print("target_scope: NONE")
    else:
        print("target_scope: last message-received")
        print(f"target_scope.position: {scope_position} of {len(message_blocks)}")
    print(f"markdown_in_scope.count: {len(markdown_blocks)}")
    print(f"markdown_ids_in_scope: {markdown_ids}")
    print(f"candidate_ns: {extraction.observation.candidates}")
    print(f"selection: {selection_label}")
    print(f"text_len: {extraction.observation.text_len}")
    print(f"extracted_status: {extraction.extracted_status}")
    print(f"reason: {extraction.observation.reason}")
    print(f"errors: {extraction.observation.errors + candidate_errors}")

    print("candidates_serialized:")
    for idx, candidate in enumerate(candidates_serialized, start=1):
        print(
            f"- [{idx}] id={candidate.get('id')} "
            f"markdown_n={candidate.get('markdown_n')} "
            f"valid_id={candidate.get('valid_markdown_id')} "
            f"text_len={candidate.get('text_len')} "
            f"selector={candidate.get('selector_path')}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
