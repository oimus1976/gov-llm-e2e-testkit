# scripts/build_dataset_from_f8.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import shutil
import hashlib
import yaml

from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


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
        "schema_version": "dataset.v0.2",
        "dataset_id": dataset_id,
        "source": {
            "type": "f8_run",
            "run_id": f8_run_dir.name,
            "path": str(f8_run_dir.resolve()),
        },
        "generated_at": datetime.now(JST).isoformat(),
        "entries": entries,
    }

    with (dataset_dir / "dataset.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(dataset_yaml, f, allow_unicode=True, sort_keys=False)

    return dataset_dir


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_dataset_diff(*, f8_run_dir: Path, dataset_dir: Path) -> list[str]:
    """
    Compare answer.md files between f8_run_dir and dataset_dir.

    Returns a list of mismatch descriptions. No exceptions are raised
    for missing files; they are reported as mismatches.
    """

    issues: list[str] = []

    source_entries_dir = f8_run_dir / "entries"
    dataset_entries_dir = dataset_dir / "entries"

    if not source_entries_dir.exists():
        issues.append(f"source entries/ missing: {source_entries_dir}")
        return issues

    if not dataset_entries_dir.exists():
        issues.append(f"dataset entries/ missing: {dataset_entries_dir}")
        return issues

    source_q = {p.name for p in source_entries_dir.iterdir() if p.is_dir()}
    dataset_q = {p.name for p in dataset_entries_dir.iterdir() if p.is_dir()}

    for q_id in sorted(source_q | dataset_q):
        source_answer = source_entries_dir / q_id / "answer.md"
        dataset_answer = dataset_entries_dir / q_id / "answer.md"

        if not source_answer.exists():
            issues.append(f"{q_id}: source answer.md missing")
            continue

        if not dataset_answer.exists():
            issues.append(f"{q_id}: dataset answer.md missing")
            continue

        try:
            if _sha256(source_answer) != _sha256(dataset_answer):
                issues.append(f"{q_id}: answer.md differs")
        except OSError as e:
            issues.append(f"{q_id}: read error - {e}")

    return issues


if __name__ == "__main__":
    # 最小の手動実行用（CLI は後回し）
    import argparse
    import sys

    def _resolve_latest_f8_run(output_root: Path) -> Path:
        """
        Resolve the latest f8 run directory under output_root / "f8_runs".

        The latest run is determined by the newest modification time.
        If multiple runs share the same newest time, resolution is ambiguous.
        """

        f8_runs_root = output_root / "f8_runs"
        if not f8_runs_root.exists():
            raise FileNotFoundError(f"f8_runs directory not found: {f8_runs_root}")

        candidates = []
        for path in f8_runs_root.iterdir():
            if not path.is_dir():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError as e:
                raise OSError(f"failed to stat run dir {path}: {e}") from e
            candidates.append((mtime, path))

        if not candidates:
            raise FileNotFoundError(f"no f8 runs found under: {f8_runs_root}")

        latest_mtime = max(mtime for mtime, _ in candidates)
        latest_dirs = [path for mtime, path in candidates if mtime == latest_mtime]

        if len(latest_dirs) > 1:
            names = ", ".join(sorted(p.name for p in latest_dirs))
            raise RuntimeError(f"ambiguous latest f8 run (same mtime): {names}")

        return latest_dirs[0]

    parser = argparse.ArgumentParser(description="Build dataset from F8 run")
    parser.add_argument("--f8-run", type=Path)
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Automatically select the latest f8 run under output_root/f8_runs",
    )
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument(
        "--output-root",
        default=Path("out"),
        type=Path,
        help="Root directory for datasets (default: ./out)",
    )
    parser.add_argument(
        "--verify-diff",
        action="store_true",
        help="Verify answer.md files match source without modifying them",
    )

    args = parser.parse_args()

    if args.latest and args.f8_run:
        parser.error("--latest cannot be used together with --f8-run")

    if not args.latest and not args.f8_run:
        parser.error("either --f8-run or --latest must be provided")

    if args.latest:
        try:
            f8_run_dir = _resolve_latest_f8_run(args.output_root)
        except (FileNotFoundError, ValueError) as e:
            print("ERROR: cannot resolve latest F8 run")
            print(f"Reason: {e}")
            print()
            print("Hint:")
            print("- run F8 first (scripts/run_f8_set1_manual.py)")
            print("- or specify --f8-run explicitly")
            sys.exit(1)
    else:
        f8_run_dir = args.f8_run

    dataset_dir = build_dataset_from_f8(
        f8_run_dir=f8_run_dir,
        dataset_id=args.dataset_id,
        output_root=args.output_root,
    )

    print(f"Dataset created at: {dataset_dir}")

    exit_code = 0

    if args.verify_diff:
        mismatches = verify_dataset_diff(
            f8_run_dir=f8_run_dir,
            dataset_dir=dataset_dir,
        )
        if mismatches:
            print("verify-diff: mismatches detected")
            for msg in mismatches:
                print(f"- {msg}")
            exit_code = 1
        else:
            print("verify-diff: all answer.md files match exactly")

    sys.exit(exit_code)
