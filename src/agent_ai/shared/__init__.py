"""Shared utilities: config, gatekeeper, version."""

from agent_ai.shared.config import ConfigManager
from agent_ai.shared.gatekeeper import ApiGatekeeper
from agent_ai.shared.version import VERSION

__all__ = ["ConfigManager", "ApiGatekeeper", "VERSION"]
