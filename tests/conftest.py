# ==========================================================
# conftest.py  — v0.3 (CI Fallback Fix: Guaranteed)
# ==========================================================
import os
import pytest
from src.env_loader import load_env, MissingSecretError


# ----------------------------------------------------------
# CI fallback（Secrets 未設定時でも Smoke Test を動かすため）
# ----------------------------------------------------------
CI_DEFAULTS = {
    "QOMMONS_URL": "https://qommons.ai",
    "QOMMONS_USERNAME": "dummy",
    "QOMMONS_PASSWORD": "dummy",
}


def apply_ci_fallback():
    print("[conftest] Applying CI fallback defaults...")
    for key, value in CI_DEFAULTS.items():
        if not os.getenv(key):
            os.environ[key] = value


# ----------------------------------------------------------
# env_config Fixture
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def env_config():

    # 1️⃣ load_env() を試す
    try:
        config, options = load_env()
        return config, options

    # 2️⃣ MissingSecretError が出たら fallback を適用して再ロード
    except MissingSecretError as e:
        print("[conftest] MissingSecretError detected:", e)
        apply_ci_fallback()

        # 再ロード（この時点で MissingSecretError は絶対に起きない）
        config, options = load_env()
        return config, options


# ----------------------------------------------------------
# case_dirs Fixture（変更なし）
# ----------------------------------------------------------
@pytest.fixture
def case_dirs(tmp_path_factory):
    def _make(case_id, timestamp):
        base = tmp_path_factory.mktemp(f"{case_id}_{timestamp:%Y%m%d_%H%M%S}")
        log_dir = base / "log"
        asset_dir = base / "assets"
        log_dir.mkdir()
        asset_dir.mkdir()
        return str(log_dir), str(asset_dir)

    return _make


def pytest_report_header(config):
    return "gov-llm-e2e-testkit / pytest configuration active (conftest v0.3)"
