"""Configuration manager — loads and validates JSON config files."""

import json
import logging
import os
from pathlib import Path

from agent_ai.shared.version import validate_config_version

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"


class ConfigManager:
    """Loads setup.json and rate_limits.json; exposes typed accessors."""

    def __init__(self, config_dir: Path = _CONFIG_DIR) -> None:
        """Load all config files from *config_dir* and validate versions."""
        self._dir = config_dir
        self._setup = self._load("setup.json")
        self._rate_limits = self._load("rate_limits.json")
        validate_config_version(self._setup)
        validate_config_version(self._rate_limits.get("rate_limits", {}))

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def get(self, key: str, default=None):
        """Return a top-level value from setup.json."""
        return self._setup.get(key, default)

    def get_rate_limit(self, service: str = "default") -> dict:
        """Return rate-limit dict for *service* (fallback: default)."""
        services = self._rate_limits["rate_limits"]["services"]
        return services.get(service, services["default"])

    def get_agent_model(self) -> str:
        """Return the configured LLM model name."""
        return self._setup["agent"]["model"]

    def get_max_tokens(self) -> int:
        """Return the configured max-tokens value."""
        return int(self._setup["agent"]["max_tokens"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self, filename: str) -> dict:
        """Read and parse a JSON config file."""
        path = self._dir / filename
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        logger.debug("Loaded config: %s", path)
        return data

    @staticmethod
    def get_env(key: str, default: str = "") -> str:
        """Retrieve a secret from environment variables only."""
        return os.environ.get(key, default)
