from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class OrdinanceStructure:
    """
    条例の構造事実（条・項の存在）を表すデータ構造。
    意味解釈は一切含まない。
    """

    ordinance_id: str
    articles: List[int]
    paragraphs: Dict[int, List[int]]
