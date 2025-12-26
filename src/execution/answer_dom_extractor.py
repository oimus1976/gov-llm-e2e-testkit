# src/execution/answer_dom_extractor.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re

from bs4 import BeautifulSoup


# ====== Tunables (暫定) ======
MIN_TEXT_LENGTH = 200
MIN_ACCEPTABLE_LENGTH = 120
UI_TOKEN_EXCLUDE_THRESHOLD = 6
QUESTION_PREFIX_LEN = 20

UI_TOKENS = [
    "Toggle Sidebar",
    "コピー",
    "音声",
    "AIモデル",
    "Web検索",
    "ナレッジ",
    "チャットAI選択",
    "国内リージョン",
]


# ====== Data ======
@dataclass
class Candidate:
    div_index: int  # DOM 全体 index（main 配下）
    text: str
    length: int
    ui_token_count: int
    contains_question: bool


@dataclass
class ExtractionResult:
    selected: bool
    text: Optional[str] = None
    reason: Optional[str] = None


# ====== Utils ======
def normalize_text(s: str) -> str:
    if not s:
        return ""
    # 連続空白の正規化＋前後トリム
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def text_is_empty(s: str) -> bool:
    return not s or not s.strip()


def count_ui_tokens(text: str) -> int:
    cnt = 0
    for tok in UI_TOKENS:
        if tok in text:
            cnt += 1
    return cnt


# ====== Core ======
def enumerate_candidates(html: str, question_text: str) -> List[Candidate]:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None:
        return []

    # DOM 全体 index を確定（S4 の根拠）
    all_divs = list(main.find_all("div"))
    div_index_map = {div: idx for idx, div in enumerate(all_divs)}

    # Primary Path
    primary_divs = main.select('div[class~="message"], div[class~="markdown"]')
    target_divs = primary_divs if primary_divs else all_divs

    q_key = normalize_text(question_text)[:QUESTION_PREFIX_LEN]

    candidates: List[Candidate] = []
    for div in target_divs:
        raw = div.get_text(separator=" ", strip=True)
        text = normalize_text(raw)

        if text_is_empty(text):
            continue
        if len(text) < MIN_TEXT_LENGTH:
            continue

        contains_question = q_key in text if q_key else False
        ui_token_count = count_ui_tokens(text)

        if ui_token_count >= UI_TOKEN_EXCLUDE_THRESHOLD:
            continue

        candidates.append(
            Candidate(
                div_index=div_index_map.get(div, -1),
                text=text,
                length=len(text),
                ui_token_count=ui_token_count,
                contains_question=contains_question,
            )
        )

    return candidates


def select_best_candidate(candidates: List[Candidate]) -> Optional[Candidate]:
    if not candidates:
        return None

    # S1
    non_question = [c for c in candidates if not c.contains_question]
    pool = non_question if non_question else candidates

    # S2 / S3 / S4
    pool_sorted = sorted(
        pool,
        key=lambda c: (
            c.ui_token_count,  # 少ないほど良い
            -c.length,  # 長いほど良い
            -c.div_index,  # 後方ほど良い
        ),
    )

    best = pool_sorted[0]
    if best.length < MIN_ACCEPTABLE_LENGTH:
        return None

    return best


def extract_answer_dom(html: str, question_text: str) -> ExtractionResult:
    candidates = enumerate_candidates(html, question_text)
    best = select_best_candidate(candidates)

    if best is None:
        return ExtractionResult(
            selected=False,
            reason="no suitable dom candidate found",
        )

    return ExtractionResult(
        selected=True,
        text=best.text,
    )


# ====== End of File ======
