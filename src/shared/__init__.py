"""shared — configuration, gatekeeper, and version utilities."""

from shared.config import AppConfig, ConfigManager
from shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from shared.pipeline_config import PipelineConfig
from shared.version import VERSION, validate_config_version

__version__ = VERSION
__all__ = [
    "AppConfig",
    "ConfigManager",
    "ApiGatekeeper",
    "RateLimitConfig",
    "PipelineConfig",
    "VERSION",
    "validate_config_version",
]
