"""Unit tests for ConfigManager."""

import json

import pytest

from shared.config import ConfigManager


def test_load_setup(config_dir):
    cfg = ConfigManager(config_dir=config_dir)
    assert cfg.get("app")["name"] == "test-app"


def test_get_agent_model(config_dir):
    cfg = ConfigManager(config_dir=config_dir)
    assert cfg.get_agent_model() == "claude-sonnet-4-6"


def test_get_max_tokens(config_dir):
    cfg = ConfigManager(config_dir=config_dir)
    assert cfg.get_max_tokens() == 512


def test_get_rate_limit_default(config_dir):
    cfg = ConfigManager(config_dir=config_dir)
    rl = cfg.get_rate_limit("default")
    assert rl["requests_per_minute"] == 30


def test_get_rate_limit_fallback(config_dir):
    """Unknown service falls back to 'default'."""
    cfg = ConfigManager(config_dir=config_dir)
    rl = cfg.get_rate_limit("nonexistent_service")
    assert "requests_per_minute" in rl


def test_get_env(monkeypatch):
    monkeypatch.setenv("TEST_SECRET", "abc")
    assert ConfigManager.get_env("TEST_SECRET") == "abc"


def test_get_env_missing():
    assert ConfigManager.get_env("DEFINITELY_NOT_SET_XYZ", "fallback") == "fallback"


def test_version_mismatch_raises(tmp_path):
    (tmp_path / "setup.json").write_text(json.dumps({"version": "9.99", "agent": {}, "markitdown": {}}))
    (tmp_path / "rate_limits.json").write_text(
        json.dumps({"rate_limits": {"version": "1.00", "services": {"default": {}}}})
    )
    with pytest.raises(ValueError):
        ConfigManager(config_dir=tmp_path)
