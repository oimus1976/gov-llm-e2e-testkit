# src/f9/a/ordinance/ordinance_protocol.py

from typing import Protocol


class OrdinanceStructureProtocol(Protocol):
    articles: list[int]
    paragraphs: dict[int, list[int]]
