# ==========================================================
# conftest.py  Sync Playwright v0.2
# ==========================================================

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from pages.login_page import LoginPage
from pages.chat_page import ChatPage
from src.env_loader import load_env

JST = timezone(timedelta(hours=9))


# -------------------------------
# env 読み込み
# -------------------------------
@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config, options


# -------------------------------
# case ディレクトリ
# -------------------------------
@pytest.fixture
def case_dirs(tmp_path):
    def _make(case_id: str, now: datetime):
        base = Path("logs") / now.strftime("%Y%m%d_%H%M%S") / case_id
        log = base / "log"
        assets = base / "assets"
        log.mkdir(parents=True, exist_ok=True)
        assets.mkdir(parents=True, exist_ok=True)
        return log, assets
    return _make


# -------------------------------
# login_page fixture
# -------------------------------
@pytest.fixture
def login_page(page, env_config):
    config, _ = env_config
    return LoginPage(page, config)


# -------------------------------
# chat_page fixture
# -------------------------------
@pytest.fixture
def chat_page(page, env_config):
    config, _ = env_config
    return ChatPage(page, config)


