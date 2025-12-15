# tests/diagnostic/test_profile_resolution.py

import sys
import pprint

from src.env_loader import load_env


def test_profile_resolution_diagnostic():
    """
    Diagnostic test:
    - Observe which profile is actually selected by env_loader
    - Do NOT assert correctness
    - Only assert that resolution happened
    """

    profile_cfg, options = load_env()

    print("\n===== PYTEST EXECUTION INFO =====")
    print(f"sys.executable: {sys.executable}")
    print(f"sys.argv     : {sys.argv}")

    print("\n===== ENV LOADER RESULT =====")
    print("profile_cfg:")
    pprint.pprint(profile_cfg)

    print("\noptions:")
    pprint.pprint(options)

    # ---- minimal safety assertion (not correctness) ----
    assert profile_cfg is not None, "profile_cfg must not be None"
