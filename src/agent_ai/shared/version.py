"""Version tracking for the project."""

VERSION = "1.00"
CODE_VERSION = "1.00"
CONFIG_VERSION = "1.00"
RATE_LIMITS_VERSION = "1.00"


def validate_config_version(config: dict, expected: str = CONFIG_VERSION) -> bool:
    """Return True if config version matches expected; raise ValueError otherwise."""
    actual = config.get("version")
    if actual != expected:
        raise ValueError(f"Config version mismatch: expected {expected}, got {actual}")
    return True
