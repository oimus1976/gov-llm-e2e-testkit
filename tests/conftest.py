# ==========================================================
# conftest.py  v0.21
# env_loader v0.2 互換 / Secrets fallback 対応 / CI 安定化
# ==========================================================

import os
import pytest
from datetime import datetime
from src.env_loader import load_env


# ----------------------------------------------------------
#  fixture: env_config
#  - env.yaml の読み込み
#  - Secrets（GitHub Actions）不足時の fallback（安全設計）
# ----------------------------------------------------------
@pytest.fixture(scope="session")
def env_config():
    """
    env.yaml → load_env(v0.2) で読み込み
    さらに URL/USER/PASS の fallback を補完して返す
    """

    config, options = load_env()

    # ------------------------------------------------------
    # 1. URL fallback
    # ------------------------------------------------------
    config["url"] = (
        config.get("url")
        or os.getenv("QOMMONS_URL")
        or "https://qommons.ai"     # 公式デフォルト
    )

    # ------------------------------------------------------
    # 2. USER fallback
    # ------------------------------------------------------
    config["username"] = (
        config.get("username")
        or os.getenv("QOMMONS_USERNAME")
        or "dummy"                  # ログイン不要テスト用
    )

    # ------------------------------------------------------
    # 3. PASSWORD fallback
    # ------------------------------------------------------
    config["password"] = (
        config.get("password")
        or os.getenv("QOMMONS_PASSWORD")
        or "dummy"
    )

    return config, options


# ----------------------------------------------------------
#  fixture: case_dirs
#  - ログ + スクショを格納するディレクトリを生成
# ----------------------------------------------------------
@pytest.fixture
def case_dirs(tmp_path_factory):
    def _make(case_id: str, timestamp):
        base = tmp_path_factory.mktemp(case_id)

        # Markdown ログ / raw logs
        log_dir = base / "logs"
        log_dir.mkdir(exist_ok=True)

        # screenshot / dom etc
        assets_dir = base / "assets"
        assets_dir.mkdir(exist_ok=True)

        return str(log_dir), str(assets_dir)

    return _make


# ----------------------------------------------------------
#  Pytest設定（表示改善）
# ----------------------------------------------------------
def pytest_report_header(config):
    return "gov-llm-e2e-testkit / pytest configuration active (v0.21)"
