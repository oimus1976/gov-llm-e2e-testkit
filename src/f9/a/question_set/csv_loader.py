from dataclasses import dataclass
from pathlib import Path
from typing import List
import csv


@dataclass(frozen=True)
class QuestionTemplateRow:
    question_id: str
    question_text: str


def load_question_set_from_csv(path: Path) -> List[QuestionTemplateRow]:
    """
    A-0: CSV から質問テンプレ集合を読み込む
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV ファイルが存在しません: {path}")

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        required = {"question_id", "question_text"}
        missing = sorted(required - set(fieldnames))
        if missing:
            raise ValueError(
                f"質問CSVに必要な列が不足しています: {', '.join(missing)}"
            )

        rows: List[QuestionTemplateRow] = []
        for row in reader:
            qid = (row.get("question_id") or "").strip()
            qtext = (row.get("question_text") or "").strip()
            if not qid or not qtext:
                continue
            rows.append(
                QuestionTemplateRow(
                    question_id=qid,
                    question_text=qtext,
                )
            )

    if not rows:
        raise ValueError(f"質問CSVに有効なレコードがありません: {path}")

    return rows
