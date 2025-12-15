# ==========================================================
# conftest.py — v0.5 (F4 profile fixture added)
# ==========================================================

import os
import pytest

from src.env_loader import load_env, MissingSecretError
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

# ----------------------------------------------------------
# CI fallback
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
# pytest CLI options
# ----------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--f4-profile",
        action="store",
        default=None,
        help="F4 RAG execution profile (e.g. html / markdown)",
    )


# ----------------------------------------------------------
# env_config Fixture
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def env_config():
    try:
        config, options = load_env()
        return config, options
    except MissingSecretError as e:
        print("[conftest] MissingSecretError detected:", e)
        apply_ci_fallback()
        config, options = load_env()
        return config, options


# ----------------------------------------------------------
# resolved_profile Fixture（F4専用・config非汚染）
# ----------------------------------------------------------
@pytest.fixture
def resolved_profile(request, env_config):
    """
    Resolve F4 execution profile.

    Priority:
      1. CLI option --f4-profile
      2. env.yaml (config["profile"])
      3. fallback: "html"
    """
    config, _ = env_config

    cli_profile = request.config.getoption("--f4-profile")
    if cli_profile:
        return cli_profile

    env_profile = config.get("profile")
    if env_profile:
        return env_profile

    return "html"


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


# ----------------------------------------------------------
# ChatPage Fixture
# ----------------------------------------------------------
@pytest.fixture
def chat_page(page, env_config):
    config, _ = env_config

    # ---- Login ----
    login = LoginPage(page, config)
    login.open()
    login.login()

    # ---- ChatSelectPage ----
    select_page = ChatSelectPage(page, config)
    ai_name = config.get("chat_name", "プライベートナレッジ")
    select_page.open_ai(ai_name)

    # ---- ChatPage 初期化 ----
    chat = ChatPage(page, config)
    return chat


def pytest_report_header(config):
    return "gov-llm-e2e-testkit / pytest configuration active (conftest v0.5)"
