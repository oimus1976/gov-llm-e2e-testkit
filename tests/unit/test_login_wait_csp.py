"""Offline tests for LoginPage's CSP-safe URL wait (no browser/network)."""

import re
from unittest.mock import Mock

import pytest

from tests.pages.login_page import LoginPage


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.invalid/chat", True),
        ("https://example.invalid/chat/", True),
        ("https://example.invalid/chat/123e4567", True),
        ("https://example.invalid/chat?next=1", True),
        ("https://example.invalid/chat#top", True),
        ("https://example.invalid/chatty", False),
        ("https://example.invalid/login", False),
    ],
)
def test_wait_pattern_matches_login_destination(url, expected):
    page = Mock()
    login = LoginPage(page, {}, timeout=27000)
    login.wait_for_login_success()
    args, kwargs = page.wait_for_url.call_args
    assert isinstance(args[0], re.Pattern)
    assert bool(args[0].search(url)) is expected
    assert kwargs == {"timeout": 27000}
    page.wait_for_function.assert_not_called()


def test_wait_preserves_error_and_optional_evidence():
    page = Mock()
    failure = TimeoutError("synthetic navigation timeout")
    page.wait_for_url.side_effect = failure
    login = LoginPage(page, {}, timeout=11000)
    login.collect_evidence = Mock()
    with pytest.raises(TimeoutError) as raised:
        login.wait_for_login_success(evidence_dir="fictional")
    assert raised.value is failure
    login.collect_evidence.assert_called_once_with("fictional", "login_failed")
    page.wait_for_function.assert_not_called()


def test_no_evidence_without_directory():
    page = Mock()
    page.wait_for_url.side_effect = RuntimeError("synthetic failure")
    login = LoginPage(page, {}, timeout=1000)
    login.collect_evidence = Mock()
    with pytest.raises(RuntimeError):
        login.wait_for_login_success()
    login.collect_evidence.assert_not_called()
