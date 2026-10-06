"""Offline checks: synthetic credentials only, no browser or HTTP requests."""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.env_loader import MissingSecretError, load_env


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "docs/archive/debug/sandbox"


def module_from(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("script", ["inspect_chat_dom.py", "api_poll_test_auto_v0_1.py"])
def test_archived_login_uses_loaded_config(script, capsys):
    module = module_from(ARCHIVE / script)
    config = {"url": "https://example.invalid/login", "username": "synthetic-user", "password": "synthetic-password"}
    page = MagicMock()
    page.click.side_effect = RuntimeError("stop before authentication")
    playwright = MagicMock()
    playwright.chromium.launch.return_value.new_context.return_value.new_page.return_value = page
    with patch.object(module, "load_env", return_value=(config, {})), patch.object(module, "sync_playwright") as start:
        start.return_value.__enter__.return_value = playwright
        with pytest.raises(RuntimeError, match="stop before authentication"):
            module.main()
    page.goto.assert_called_once_with(config["url"])
    assert [call.args[1] for call in page.fill.call_args_list] == [config["username"], config["password"]]
    output = capsys.readouterr().out
    assert config["username"] not in output and config["password"] not in output


@pytest.mark.parametrize("script", ["inspect_chat_dom.py", "api_poll_test_auto_v0_1.py"])
def test_missing_secret_stops_before_browser(script):
    module = module_from(ARCHIVE / script)
    with patch.object(module, "load_env", side_effect=MissingSecretError("missing synthetic secret")), patch.object(module, "sync_playwright") as start:
        with pytest.raises(MissingSecretError):
            module.main()
    start.assert_not_called()


def test_diagnostic_omits_config_values(capsys):
    module = module_from(ROOT / "tests/diagnostic/test_profile_resolution.py")
    config = {"username": "synthetic-user", "password": "synthetic-password", "nested": {"password": "nested-secret"}}
    with patch.object(module, "load_env", return_value=(config, {"extra": "option-secret"})):
        module.test_profile_resolution_diagnostic()
    output = capsys.readouterr().out
    assert all(value not in output for value in ["synthetic-user", "synthetic-password", "nested-secret", "option-secret"])
    assert "username" in output and "password" in output


@pytest.mark.parametrize("profile", ["internet", "lgwan"])
def test_loader_preserves_profile_and_source_precedence(profile, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ENV_PROFILE", profile)
    for key in ["TEST_URL", "TEST_USER", "TEST_PASS"]:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / "env.yaml").write_text('profile: internet\nprofiles:\n  internet: &config\n    url: ${TEST_URL}\n    username: ${TEST_USER}\n    password: ${TEST_PASS}\n  lgwan: *config\noptions: {}\n', encoding="utf-8")
    (tmp_path / ".env").write_text('TEST_USER=common-user\nTEST_PASS=common-password\n', encoding="utf-8")
    (tmp_path / f".env.{profile}").write_text('TEST_URL=https://example.invalid/login\nTEST_USER=profile-user\nTEST_PASS=profile-password\n', encoding="utf-8")
    monkeypatch.setenv("TEST_PASS", "os-password")
    config, options = load_env()
    assert config == {"url": "https://example.invalid/login", "username": "common-user", "password": "os-password"}
    assert options == {}


def test_xhr_sniffer_records_metadata_only(tmp_path, monkeypatch):
    module = module_from(ARCHIVE / "xhr_sniffer_v0_1.py")
    monkeypatch.chdir(tmp_path)
    page = MagicMock()
    playwright = MagicMock()
    playwright.chromium.launch.return_value.new_context.return_value.new_page.return_value = page
    request = MagicMock(resource_type="xhr", url="https://example.invalid/login", method="POST", post_data="synthetic-password", headers={"authorization": "synthetic-token"})
    response = MagicMock(url=request.url, status=200, request=request, headers={"set-cookie": "synthetic-cookie"})
    response.text.side_effect = AssertionError("response payload must not be read")
    with patch.object(module, "sync_playwright") as start, patch("src.env_loader.load_env", return_value=({}, {})), patch("tests.pages.login_page.LoginPage"), patch("tests.pages.chat_select_page.ChatSelectPage"), patch("tests.pages.chat_page.ChatPage"):
        start.return_value.__enter__.return_value = playwright
        module.main()
    handlers = {call.args[0]: call.args[1] for call in page.on.call_args_list}
    handlers["request"](request)
    handlers["response"](response)
    response.text.assert_not_called()
    text = next(tmp_path.glob("sandbox/*/xhr_log.jsonl")).read_text(encoding="utf-8")
    assert all(value not in text for value in ["synthetic-password", "synthetic-token", "synthetic-cookie", "postData", "headers", "body"])
