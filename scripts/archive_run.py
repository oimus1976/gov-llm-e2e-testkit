from __future__ import annotations

import shutil
import sys
from pathlib import Path


def create_run_archive(run_root: Path, archive_root: Path | None = None) -> Path:
    run_root = run_root.expanduser().resolve()
    if not run_root.is_dir():
        raise FileNotFoundError(f"run_root does not exist: {run_root}")

    run_id = run_root.name
    archive_root = (
        archive_root.expanduser().resolve() if archive_root else Path("out").resolve()
    )
    archive_root.mkdir(parents=True, exist_ok=True)

    archive_base = archive_root / run_id
    archive_path = archive_base.with_suffix(".zip")
    # If archive already exists, do not fail the run.
    # Emit warning and return existing archive path.
    if archive_path.exists():
        print(
            f"[WARN] Run archive already exists, skipped creation: {archive_path}",
            file=sys.stderr,
        )
        return archive_path

    result = shutil.make_archive(
        base_name=str(archive_base),
        format="zip",
        root_dir=str(run_root.parent),
        base_dir=run_root.name,
    )
    return Path(result)
