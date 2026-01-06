"""
Gate1: RAG Entry Check (Schema / Preconditions)

This test file is a *mechanical translation* of:
- Design_ci_rag_entry_v0.1
- Appendix A: F4 Trial Dataset Schema Validation Checklist (Gate1)

IMPORTANT:
- This is NOT a RAG evaluation.
- This is NOT a quality check.
- FAIL means: "RAG QA entry is NOT established".
"""

import json
import os
from pathlib import Path

import pytest


# ------------------------------------------------------------
# Dataset resolver
# ------------------------------------------------------------


def _resolve_dataset_path() -> Path:
    env_path = os.getenv("F4_DATASET_PATH") or os.getenv("F4_TRIAL_DATASET_PATH")
    if env_path:
        return Path(env_path)

    candidates = [
        Path("out/f4_trial_dataset/dataset.json"),
        Path("out/datasets/f4_trial_dataset/dataset.json"),
        Path("data/f4_trial_dataset/dataset.json"),
    ]

    datasets_root = Path("out/datasets")
    if datasets_root.exists():
        discovered = sorted(
            datasets_root.rglob("dataset.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        candidates.extend(discovered)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


# ------------------------------------------------------------
# Test Input Fixture
# ------------------------------------------------------------
@pytest.fixture
def f4_trial_dataset():
    """
    Load f4 trial dataset from dataset.json.

    - Requires raw_evidence / execution_context / derived_summary.
    - Skips the test when dataset.json is absent.
    """
    dataset_path = _resolve_dataset_path()

    if not dataset_path.exists():
        pytest.skip(
            f"dataset.json not found at {dataset_path}. "
            "Generate it beforehand (e.g., via scripts/build_dataset_from_f8.py) "
            "or provide a path via F4_DATASET_PATH."
        )

    try:
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - test setup must surface failure
        pytest.fail(f"failed to load dataset.json at {dataset_path}: {exc}")

    if not isinstance(dataset, dict):
        pytest.fail("dataset.json must decode to an object")

    required_top_level = ["raw_evidence", "execution_context", "derived_summary"]
    missing = [key for key in required_top_level if key not in dataset]
    if missing:
        pytest.fail(
            f"dataset.json missing required keys: {', '.join(missing)} "
            "(must include raw_evidence, execution_context, derived_summary)"
        )

    return dataset


# ============================================================
# 1. Top-level Structure Checks
# ============================================================


def test_top_level_structure(f4_trial_dataset):
    """
    Appendix A: Section 1 (Top-level)

    S-01: dataset MUST be a single JSON object
    S-02: raw_evidence MUST exist
    S-03: execution_context MUST exist
    S-04: derived_summary MUST exist
    S-05: extra top-level keys MUST NOT cause FAIL
    """
    # S-01
    assert isinstance(f4_trial_dataset, dict), "S-01 FAIL: dataset is not an object"

    # S-02 / S-03 / S-04
    assert "raw_evidence" in f4_trial_dataset, "S-02 FAIL: raw_evidence missing"
    assert (
        "execution_context" in f4_trial_dataset
    ), "S-03 FAIL: execution_context missing"
    assert "derived_summary" in f4_trial_dataset, "S-04 FAIL: derived_summary missing"

    # S-05
    # NOTE:
    # Extra keys are explicitly allowed.
    # No assertion here by design.


# ============================================================
# 2. Raw Evidence Layer
# ============================================================


def test_raw_evidence_layer(f4_trial_dataset):
    """
    Appendix A: Section 2 (Raw Evidence)

    R-01: raw_evidence MUST be object or array
    R-02: empty object / array MUST be allowed

    R-NG-01: MUST NOT evaluate content
    R-NG-02: MUST NOT evaluate length, vocabulary, similarity
    """
    raw = f4_trial_dataset.get("raw_evidence")

    # R-01
    assert isinstance(
        raw, (dict, list)
    ), "R-01 FAIL: raw_evidence is not object or array"

    # R-02
    # NOTE:
    # Empty raw_evidence is allowed by design.
    # No assertion for non-emptiness.


# ============================================================
# 3. Execution Context Layer
# ============================================================


def test_execution_context_layer(f4_trial_dataset):
    """
    Appendix A: Section 3 (Execution Context)

    C-01: rag_profile MUST exist
    C-02: case_set MUST exist
    C-03: run_mode MUST exist
    C-04: run_mode MUST be 'collect-only'

    C-05: values MUST be explicitly recorded (no inference)
    """
    ctx = f4_trial_dataset.get("execution_context")
    assert isinstance(ctx, dict), "Execution context must be an object"

    # C-01 / C-02 / C-03
    assert "rag_profile" in ctx, "C-01 FAIL: rag_profile missing"
    assert "case_set" in ctx, "C-02 FAIL: case_set missing"
    assert "run_mode" in ctx, "C-03 FAIL: run_mode missing"

    # C-04
    assert (
        ctx.get("run_mode") == "collect-only"
    ), "C-04 FAIL: run_mode is not 'collect-only'"

    # C-05
    # NOTE:
    # We only check explicit presence.
    # No inference, no defaulting, no guessing.


# ============================================================
# 4. Derived Summary Layer
# ============================================================


def test_derived_summary_layer(f4_trial_dataset):
    """
    Appendix A: Section 4 (Derived Summary)

    D-01: derived_summary MUST be object
    D-02: empty object MUST be allowed

    D-NG-01: MUST NOT require numeric scores
    D-NG-02: MUST NOT expect EHR / HR / Stability
    """
    summary = f4_trial_dataset.get("derived_summary")

    # D-01
    assert isinstance(summary, dict), "D-01 FAIL: derived_summary is not an object"

    # D-02
    # NOTE:
    # Empty summary is explicitly allowed.
    # No assertions on content.


# ============================================================
# 5. Golden Asset Protection
# ============================================================


def test_golden_asset_protection():
    """
    Appendix A: Section 5 (Golden Asset Protection)

    G-01: Golden Question Pool MUST be read-only
    G-02: Golden Ordinance Set MUST NOT be modified
    G-03: Golden assets MUST NOT be consumed by CI

    NOTE:
    Actual detection mechanism is out of scope for this file.
    This test exists as a semantic guardrail.
    """
    pytest.skip(
        "Golden asset protection checks are environment-dependent "
        "and must be implemented in a dedicated safeguard layer."
    )


# ============================================================
# End of Gate1 Entry Tests
# ============================================================
