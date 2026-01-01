from __future__ import annotations

import runpy
from pathlib import Path
import sys


def main() -> int:
    target = Path(__file__).resolve().parents[1] / "scripts" / "run_question_resolution.py"
    if not target.is_file():
        print(f"[ERROR] Python スクリプトが見つかりません: {target}")
        return 1

    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
