from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup, Tag

from src.f9.a.ordinance.ordinance_structure import OrdinanceStructure

_DIGIT_TABLE = str.maketrans(
    {
        "０": "0",
        "１": "1",
        "２": "2",
        "３": "3",
        "４": "4",
        "５": "5",
        "６": "6",
        "７": "7",
        "８": "8",
        "９": "9",
    }
)


class OrdinanceStructureLoadError(Exception):
    """構造抽出に失敗した場合の例外。"""

    pass


def _normalize_digits(value: str) -> str:
    return value.translate(_DIGIT_TABLE)


def _parse_int(value: str) -> int:
    normalized = _normalize_digits(value)
    return int(normalized)


def _read_html(html_path: Path) -> str:
    for encoding in ("shift_jis", "utf-8"):
        try:
            return html_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return html_path.read_text(encoding="utf-8", errors="ignore")


def _extract_article_number(article_node: Tag) -> int:
    num_span = article_node.select_one("p.num > span.num")
    text = num_span.get_text(strip=True) if num_span else article_node.get_text(" ", strip=True)
    match = re.search(r"第\s*([0-9０-９]+)", text)
    if not match:
        raise OrdinanceStructureLoadError("条番号を検出できませんでした。")
    return _parse_int(match.group(1))


def _iter_following_clause_nodes(article_node: Tag):
    eline = article_node.find_parent("div", class_="eline")
    block = eline.parent if eline else article_node
    sibling = block.find_next_sibling()
    while sibling:
        if sibling.find("div", class_="article"):
            break
        clause = sibling.find("div", class_="clause")
        if clause:
            yield clause
        sibling = sibling.find_next_sibling()


def _collect_paragraphs(article_node: Tag) -> List[int]:
    paragraphs: List[int] = []

    has_primary_clause = article_node.select_one("span.clause")
    if has_primary_clause:
        paragraphs.append(1)

    for clause_node in _iter_following_clause_nodes(article_node):
        num_span = clause_node.select_one("p.num > span.num")
        if not num_span:
            continue
        num_text = num_span.get_text(strip=True)
        if not num_text:
            continue
        try:
            paragraph_num = _parse_int(num_text)
        except ValueError:
            continue
        if paragraph_num not in paragraphs:
            paragraphs.append(paragraph_num)

    return paragraphs


def _merge_paragraphs(target: Dict[int, List[int]], article_num: int, paragraph_nums: List[int]) -> None:
    if not paragraph_nums and article_num not in target:
        target[article_num] = []
        return

    merged = target.get(article_num, [])
    for num in paragraph_nums:
        if num not in merged:
            merged.append(num)
    target[article_num] = merged


def load_ordinance_structure(reiki_root: Path, ordinance_id: str) -> OrdinanceStructure:
    html_path = reiki_root / f"{ordinance_id}.html"
    if not html_path.is_file():
        raise OrdinanceStructureLoadError(f"条例HTMLが見つかりません: {html_path}")

    html = _read_html(html_path)
    soup = BeautifulSoup(html, "html.parser")

    content_root = soup.select_one("#primaryInner2") or soup
    article_nodes = content_root.select("div.article")
    if not article_nodes:
        raise OrdinanceStructureLoadError("条定義ブロックが見つかりません。")

    articles: List[int] = []
    paragraphs: Dict[int, List[int]] = {}

    for article_node in article_nodes:
        article_num = _extract_article_number(article_node)
        if article_num not in articles:
            articles.append(article_num)

        paragraph_nums = _collect_paragraphs(article_node)
        _merge_paragraphs(paragraphs, article_num, paragraph_nums)

    return OrdinanceStructure(
        ordinance_id=ordinance_id,
        articles=articles,
        paragraphs=paragraphs,
    )
