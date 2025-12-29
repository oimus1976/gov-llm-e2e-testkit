# scripts/build_dataset_from_f8.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil
import yaml


def build_dataset_from_f8(
    *,
    f8_run_dir: Path,
    dataset_id: str,
    output_root: Path,
) -> Path:
    """
    Build dataset from a normalized F8 run directory.

    Preconditions:
    - f8_run_dir follows the normative layout:
      f8_runs/<run_id>/entries/Qxx/answer.md
    - answer.md is already finalized (rag_entry confirmed)

    This function:
    - does NOT parse answer.md
    - does NOT reinterpret Extracted / Raw
    - only copies finalized artifacts
    """

    if not f8_run_dir.exists():
        raise FileNotFoundError(f"f8_run_dir not found: {f8_run_dir}")

    entries_dir = f8_run_dir / "entries"
    if not entries_dir.exists():
        raise FileNotFoundError(f"entries/ not found under: {f8_run_dir}")

    dataset_dir = output_root / "datasets" / dataset_id
    dataset_entries_dir = dataset_dir / "entries"
    dataset_entries_dir.mkdir(parents=True, exist_ok=True)

    entries = []

    for q_dir in sorted(entries_dir.iterdir()):
        if not q_dir.is_dir():
            continue

        answer_md = q_dir / "answer.md"
        if not answer_md.exists():
            # 設計上は「なければスキップ」。
            # VALID / INVALID の判断はここではしない。
            continue

        target_q_dir = dataset_entries_dir / q_dir.name
        target_q_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(answer_md, target_q_dir / "answer.md")

        entries.append(
            {
                "id": q_dir.name,
                "path": f"entries/{q_dir.name}/answer.md",
            }
        )

    dataset_yaml = {
        "dataset_id": dataset_id,
        "source": {
            "type": "f8_run",
            "run_id": f8_run_dir.name,
            "path": str(f8_run_dir.resolve()),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }

    with (dataset_dir / "dataset.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(dataset_yaml, f, allow_unicode=True, sort_keys=False)

    return dataset_dir


if __name__ == "__main__":
    # 最小の手動実行用（CLI は後回し）
    import argparse

    parser = argparse.ArgumentParser(description="Build dataset from F8 run")
    parser.add_argument("--f8-run", required=True, type=Path)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--output-root", default=Path("."), type=Path)

    args = parser.parse_args()

    out = build_dataset_from_f8(
        f8_run_dir=args.f8_run,
        dataset_id=args.dataset_id,
        output_root=args.output_root,
    )

    print(f"Dataset created at: {out}")
