"""Configuration helpers for the SDK and CrewAI article pipeline."""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from agent_ai.shared.pipeline_config import PipelineConfig
from agent_ai.shared.version import validate_config_version

_CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"

logger = logging.getLogger(__name__)

try:
    PROJECT_TOPIC = PipelineConfig.load().topic
except Exception:
    PROJECT_TOPIC = "Multi-Agent Collaboration Systems: Designing Teams of AI Agents"


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings (legacy — used by SDK layer and existing tests)."""

    output_root: Path
    ollama_model: str
    ollama_base_url: str
    use_ollama: bool
    log_level: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            output_root     = Path(os.getenv("ARTICLE_OUTPUT_ROOT", "outputs")),
            ollama_model    = os.getenv("OLLAMA_MODEL", "qwen3:14b"),
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            use_ollama      = os.getenv("USE_OLLAMA", "true").lower() not in {"0", "false", "no"},
            log_level       = os.getenv("LOG_LEVEL", "INFO"),
        )

    @property
    def output_dirs(self) -> list[Path]:
        return [self.output_root / d for d in ("research", "drafts", "reviewed", "latex", "pdf", "assets")]


def build_llm(config: AppConfig):
    """Create a CrewAI LLM from AppConfig (legacy)."""
    if not config.use_ollama:
        return None
    from crewai import LLM
    model = config.ollama_model
    if not model.startswith("ollama/"):
        model = f"ollama/{model}"
    return LLM(model=model, base_url=config.ollama_base_url)


class ConfigManager:
    """Loads setup.json and rate_limits.json; exposes typed accessors."""

    def __init__(self, config_dir: Path = _CONFIG_DIR) -> None:
        self._dir = config_dir
        self._setup = self._load("setup.json")
        self._rate_limits = self._load("rate_limits.json")
        validate_config_version(self._setup)
        validate_config_version(self._rate_limits.get("rate_limits", {}))

    def get(self, key: str, default=None):
        return self._setup.get(key, default)

    def get_rate_limit(self, service: str = "default") -> dict:
        services = self._rate_limits["rate_limits"]["services"]
        return services.get(service, services["default"])

    def get_agent_model(self) -> str:
        return self._setup["agent"]["model"]

    def get_max_tokens(self) -> int:
        return int(self._setup["agent"]["max_tokens"])

    def _load(self, filename: str) -> dict:
        path = self._dir / filename
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        logger.debug("Loaded config: %s", path)
        return data

    @staticmethod
    def get_env(key: str, default: str = "") -> str:
        return os.environ.get(key, default)
