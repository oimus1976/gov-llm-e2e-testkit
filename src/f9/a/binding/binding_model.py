# src/f9/a/binding/binding_model.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class OrdinanceBinding:
    """
    A-2 の成果物。
    条例IDが束縛されたが、条・項は未解決の状態。
    """

    ordinance_id: str
    question_templates: List[str]
