"""Human-invoked entrypoint for the synthetic Private Knowledge probe."""

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    from src.knowledge_upload_probe import main

    raise SystemExit(main())
