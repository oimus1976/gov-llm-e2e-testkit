"""
Offline DOM verification script.

Purpose:
- Verify containment relationship between div.markdown and div.message-received
- Compare browser-intended structure vs BeautifulSoup reconstructed DOM

Input:
- after_answer_ready.html

Non-Goals:
- No extraction logic
- No VALID / INVALID judgment
- No normalization or repair
"""

from pathlib import Path
from bs4 import BeautifulSoup, Tag

HTML_PATH = Path(
    "out/f8/20251228/20251228T185721_manual/20251228/manual-test/Q15/after_answer_ready.html"
)

OUTPUT_PATH = Path("verify_dom_scope.txt")


def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    lines = []

    # --- Basic counts ---
    message_blocks = soup.select("div.message-received")
    markdown_blocks = soup.select("div.markdown")

    lines.append(f"message-received count: {len(message_blocks)}")
    lines.append(f"markdown count: {len(markdown_blocks)}")
    lines.append("")

    # --- For each markdown, check containment ---
    for idx, md in enumerate(markdown_blocks):
        md_id = md.get("id")
        location = "OUTSIDE message-received"

        parent = md.parent
        while parent and isinstance(parent, Tag):
            classes = parent.get("class", [])
            if (
                parent.name == "div"
                and isinstance(classes, list)
                and "message-received" in classes
            ):
                location = "INSIDE message-received"
                break
            parent = parent.parent

        lines.append(f"[markdown {idx}] id={md_id} -> {location}")

    # --- Write result ---
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
