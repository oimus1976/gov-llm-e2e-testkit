from pathlib import Path
from typing import List
import csv


def load_question_set_from_csv(path: Path) -> List[str]:
    """
    A-0: CSV から質問テンプレ集合を読み込む
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV ファイルが存在しません: {path}")

    question_texts: List[str] = []

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("text")
            if text:
                question_texts.append(text.strip())

    return question_texts
