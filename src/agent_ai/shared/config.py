"""Configuration helpers for the SDK and CrewAI article pipeline."""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from agent_ai.shared.version import validate_config_version

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_DIR   = _PROJECT_ROOT / "config"
_CONFIG_YAML  = _PROJECT_ROOT / "config.yaml"

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Load a YAML file without requiring PyYAML — simple key:value parser.

    Handles two-level nested keys only (sufficient for config.yaml).
    """
    data: dict = {}
    current_section: str | None = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip()
            # Skip blanks and comments
            if not line or line.lstrip().startswith("#"):
                continue
            # Top-level key (no leading spaces, ends with colon)
            if not raw[0].isspace() and line.endswith(":"):
                current_section = line[:-1].strip()
                data[current_section] = {}
            # Nested key: value
            elif current_section and ":" in line:
                key, _, value = line.partition(":")
                key   = key.strip()
                value = value.strip()
                # Strip inline comments before removing quotes
                if " #" in value:
                    value = value[: value.index(" #")].strip()
                value = value.strip('"').strip("'")
                data[current_section][key] = value
    return data


# ---------------------------------------------------------------------------
# PipelineConfig — loaded from config.yaml
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PipelineConfig:
    """All pipeline settings loaded from config.yaml.

    This is the single source of truth for topic, author, LLM, and paths.
    """

    # Article metadata
    topic: str
    author_name: str
    course_name: str
    lecturer_name: str

    # LLM settings
    llm_provider: str
    llm_model: str
    llm_base_url: str

    # Logging
    log_level: str
    log_dir: Path
    log_file: str

    # Output directories
    output_root: Path
    output_research: Path
    output_drafts: Path
    output_reviewed: Path
    output_latex: Path
    output_pdf: Path
    output_assets: Path

    @classmethod
    def load(cls, yaml_path: Path = _CONFIG_YAML) -> "PipelineConfig":
        """Parse config.yaml and return a PipelineConfig instance."""
        raw = _load_yaml(yaml_path)
        logger.debug("Loaded pipeline config from %s", yaml_path)

        article = raw.get("article", {})
        llm     = raw.get("llm", {})
        logging_ = raw.get("logging", {})
        outputs = raw.get("outputs", {})

        root = Path(outputs.get("root", "outputs"))
        return cls(
            topic         = article.get("topic",         "Untitled Article"),
            author_name   = article.get("author_name",   "[Author Name]"),
            course_name   = article.get("course_name",   "[Course Name]"),
            lecturer_name = article.get("lecturer_name", "[Lecturer Name]"),
            llm_provider  = llm.get("provider", "ollama"),
            llm_model     = llm.get("model",    "qwen3:14b"),
            llm_base_url  = llm.get("base_url", "http://localhost:11434"),
            log_level     = logging_.get("level",    "INFO"),
            log_dir       = Path(logging_.get("log_dir",  "logs")),
            log_file      = logging_.get("log_file", "app.log"),
            output_root     = root,
            output_research = Path(outputs.get("research", str(root / "research"))),
            output_drafts   = Path(outputs.get("drafts",   str(root / "drafts"))),
            output_reviewed = Path(outputs.get("reviewed", str(root / "reviewed"))),
            output_latex    = Path(outputs.get("latex",    str(root / "latex"))),
            output_pdf      = Path(outputs.get("pdf",      str(root / "pdf"))),
            output_assets   = Path(outputs.get("assets",   str(root / "assets"))),
        )

    @property
    def output_dirs(self) -> list[Path]:
        """All output directories that must exist before the pipeline runs."""
        return [
            self.output_research,
            self.output_drafts,
            self.output_reviewed,
            self.output_latex,
            self.output_pdf,
            self.output_assets,
            self.log_dir,
        ]

    def build_llm(self):
        """Create a CrewAI LLM from config. Returns None if provider is not ollama."""
        if self.llm_provider != "ollama":
            return None
        from crewai import LLM
        model = self.llm_model
        if not model.startswith("ollama/"):
            model = f"ollama/{model}"
        return LLM(model=model, base_url=self.llm_base_url)


# ---------------------------------------------------------------------------
# AppConfig — legacy dataclass kept for backward compatibility with SDK tests
# ---------------------------------------------------------------------------

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
        """Load config from environment variables (legacy path)."""
        return cls(
            output_root    = Path(os.getenv("ARTICLE_OUTPUT_ROOT", "outputs")),
            ollama_model   = os.getenv("OLLAMA_MODEL", "qwen3:14b"),
            ollama_base_url= os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            use_ollama     = os.getenv("USE_OLLAMA", "true").lower() not in {"0", "false", "no"},
            log_level      = os.getenv("LOG_LEVEL", "INFO"),
        )

    @property
    def output_dirs(self) -> list[Path]:
        return [
            self.output_root / "research",
            self.output_root / "drafts",
            self.output_root / "reviewed",
            self.output_root / "latex",
            self.output_root / "pdf",
            self.output_root / "assets",
        ]


def build_llm(config: AppConfig):
    """Create a CrewAI LLM from AppConfig (legacy — used by SDK layer)."""
    if not config.use_ollama:
        return None
    from crewai import LLM
    model = config.ollama_model
    if not model.startswith("ollama/"):
        model = f"ollama/{model}"
    return LLM(model=model, base_url=config.ollama_base_url)


# ---------------------------------------------------------------------------
# ConfigManager — SDK JSON config loader (unchanged)
# ---------------------------------------------------------------------------

# Re-export PROJECT_TOPIC from config.yaml so existing imports keep working
try:
    PROJECT_TOPIC = PipelineConfig.load().topic
except Exception:
    PROJECT_TOPIC = "Multi-Agent Collaboration Systems: Designing Teams of AI Agents"


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
