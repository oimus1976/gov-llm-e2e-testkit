#!/usr/bin/env python3
"""
switch_env.py
F9-B: Execution Conditions Freeze
- Copies .env.<network>_<variant> to .env
- File operation only. No execution, no parsing.
"""

from pathlib import Path
import argparse
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]  # repo root
ENV_PREFIX = ".env."
TARGET_ENV = ROOT / ".env"


def list_envs():
    envs = sorted(p.name for p in ROOT.glob(f"{ENV_PREFIX}*"))
    if not envs:
        print("[INFO] No .env.* files found.")
        return
    print("[AVAILABLE .env IDs]")
    for name in envs:
        # show env_id without prefix
        print(f"  - {name[len(ENV_PREFIX):]}")


def main():
    parser = argparse.ArgumentParser(
        description="Switch execution .env by copying .env.<id> to .env (F9-B)"
    )
    parser.add_argument(
        "env_id", nargs="?", help="env identifier (e.g. internet_markdown)"
    )
    parser.add_argument("--list", action="store_true", help="List available .env.*")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show planned operation only"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing .env")

    args = parser.parse_args()

    if args.list:
        list_envs()
        return 0

    if not args.env_id:
        parser.print_usage()
        return 2

    src = ROOT / f"{ENV_PREFIX}{args.env_id}"

    if not src.exists():
        print(f"[ERROR] Source env not found: {src.name}", file=sys.stderr)
        return 1

    if TARGET_ENV.exists() and not args.force:
        print(
            "[ERROR] .env already exists. Use --force to overwrite explicitly.",
            file=sys.stderr,
        )
        return 1

    print("[PLAN]")
    print(f"  source : {src.name}")
    print(f"  target : {TARGET_ENV.name}")

    if args.dry_run:
        print("[DRY-RUN] No files were changed.")
        return 0

    shutil.copyfile(src, TARGET_ENV)
    print("[OK] .env switched successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
