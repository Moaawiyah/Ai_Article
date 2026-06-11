"""Shared pytest fixtures."""

import json
from pathlib import Path

import pytest

from shared.gatekeeper import ApiGatekeeper, RateLimitConfig


@pytest.fixture()
def rate_limit_config() -> RateLimitConfig:
    """Minimal rate-limit config for unit tests."""
    return RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        concurrent_max=5,
        retry_after_seconds=0,
        max_retries=2,
        queue_max_depth=10,
        minute_window_seconds=60,
        hour_window_seconds=3600,
    )


@pytest.fixture()
def gatekeeper(rate_limit_config: RateLimitConfig) -> ApiGatekeeper:
    """ApiGatekeeper wired with the test rate-limit config."""
    return ApiGatekeeper(rate_limit_config)


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    """Temporary config directory with minimal valid JSON files."""
    (tmp_path / "setup.json").write_text(
        json.dumps(
            {
                "version": "1.00",
                "app": {"name": "test-app", "env": "test", "log_level": "DEBUG"},
                "markitdown": {"enable_llm_descriptions": False, "supported_extensions": [".pdf"]},
                "agent": {"model": "claude-sonnet-4-6", "max_tokens": 512, "temperature": 0.0},
            }
        )
    )
    (tmp_path / "rate_limits.json").write_text(
        json.dumps(
            {
                "rate_limits": {
                    "version": "1.00",
                    "services": {
                        "default": {
                            "requests_per_minute": 30,
                            "requests_per_hour": 500,
                            "concurrent_max": 5,
                            "retry_after_seconds": 0,
                            "max_retries": 2,
                            "queue_max_depth": 10,
                            "minute_window_seconds": 60,
                            "hour_window_seconds": 3600,
                        }
                    },
                }
            }
        )
    )
    return tmp_path
