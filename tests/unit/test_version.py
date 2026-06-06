"""Unit tests for version module."""

import pytest

from agent_ai.shared.version import CODE_VERSION, VERSION, validate_config_version


def test_version_format():
    """VERSION should be a non-empty string."""
    assert isinstance(VERSION, str)
    assert len(VERSION) > 0


def test_code_version_matches():
    assert CODE_VERSION == VERSION


def test_validate_config_version_pass():
    assert validate_config_version({"version": "1.00"}) is True


def test_validate_config_version_mismatch():
    with pytest.raises(ValueError, match="version mismatch"):
        validate_config_version({"version": "9.99"})


def test_validate_config_version_missing():
    with pytest.raises(ValueError):
        validate_config_version({})
