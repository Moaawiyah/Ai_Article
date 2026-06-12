"""PipelineConfig — loaded from config.yaml."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_YAML  = _PROJECT_ROOT / "config" / "config.yaml"

logger = logging.getLogger(__name__)


def _load_yaml(path: Path) -> dict:
    """Load a two-level YAML file without PyYAML."""
    data: dict = {}
    current_section: str | None = None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            if not raw[0].isspace() and line.endswith(":"):
                current_section = line[:-1].strip()
                data[current_section] = {}
            elif current_section and ":" in line:
                key, _, value = line.partition(":")
                key   = key.strip()
                value = value.strip()
                if " #" in value:
                    value = value[: value.index(" #")].strip()
                value = value.strip('"').strip("'")
                data[current_section][key] = value
    return data


_ARTIFACT_MAP = {
    "tikz_figure":     "- One TikZ figure using the marker: <!-- TIKZ: <description> -->",
    "markdown_table":  "- One Markdown pipe table comparing related approaches",
    "display_formula": "- One display-math formula using $$...$$ delimiters",
    "bibliography_8":  "- Bibliography with ≥8 real, citable references in [N] Author, Title, Venue, Year format",
}


@dataclass(frozen=True)
class PipelineConfig:
    """All pipeline settings loaded from config.yaml."""

    topic: str
    author_name: str
    course_name: str
    lecturer_name: str

    min_pages: int
    min_words: int
    max_words: int
    language: str
    required_artifacts: str

    llm_provider: str
    llm_model: str
    llm_base_url: str

    log_level: str
    log_dir: Path
    log_file: str

    output_root: Path
    output_research: Path
    output_drafts: Path
    output_reviewed: Path
    output_latex: Path
    output_pdf: Path
    output_assets: Path

    price_input_per_1m:  float
    price_cached_per_1m: float
    price_output_per_1m: float

    graph_spec_max_tokens:  int
    graph_spec_temperature: float
    graph_spec_brief_chars: int

    @classmethod
    def load(cls, yaml_path: Path = _CONFIG_YAML) -> PipelineConfig:
        """Build a PipelineConfig from config.yaml, applying defaults for missing keys."""
        raw        = _load_yaml(yaml_path)
        article    = raw.get("article", {})
        assignment = raw.get("assignment", {})
        llm        = raw.get("llm", {})
        logging_   = raw.get("logging", {})
        outputs    = raw.get("outputs", {})
        pricing    = raw.get("pricing", {})
        gs         = raw.get("graph_spec", {})
        root       = Path(outputs.get("root", "outputs"))
        return cls(
            topic              = article.get("topic",         "Untitled Article"),
            author_name        = article.get("author_name",   "[Author Name]"),
            course_name        = article.get("course_name",   "[Course Name]"),
            lecturer_name      = article.get("lecturer_name", "[Lecturer Name]"),
            min_pages          = int(assignment.get("min_pages",  "15")),
            min_words          = int(assignment.get("min_words",  "4500")),
            max_words          = int(assignment.get("max_words",  "5000")),
            language           = assignment.get("language",  "english"),
            required_artifacts = assignment.get("artifacts", "tikz_figure,markdown_table,display_formula,bibliography_8"),
            llm_provider       = llm.get("provider", "ollama"),
            llm_model          = llm.get("model",    "qwen3:14b"),
            llm_base_url       = llm.get("base_url", "http://localhost:11434"),
            log_level          = logging_.get("level",    "INFO"),
            log_dir            = Path(logging_.get("log_dir",  "logs")),
            log_file           = logging_.get("log_file", "app.log"),
            output_root        = root,
            output_research    = Path(outputs.get("research", str(root / "research"))),
            output_drafts      = Path(outputs.get("drafts",   str(root / "drafts"))),
            output_reviewed    = Path(outputs.get("reviewed", str(root / "reviewed"))),
            output_latex       = Path(outputs.get("latex",    str(root / "latex"))),
            output_pdf         = Path(outputs.get("pdf",      str(root / "pdf"))),
            output_assets      = Path(outputs.get("assets",   str(root / "assets"))),
            price_input_per_1m  = float(pricing.get("input_per_1m_usd",  "0.07")),
            price_cached_per_1m = float(pricing.get("cached_per_1m_usd", "0.01")),
            price_output_per_1m = float(pricing.get("output_per_1m_usd", "0.40")),
            graph_spec_max_tokens  = int(gs.get("max_tokens",     "2000")),
            graph_spec_temperature = float(gs.get("temperature",  "0.1")),
            graph_spec_brief_chars = int(gs.get("brief_chars",    "5000")),
        )

    @property
    def output_dirs(self) -> list[Path]:
        """All output/log directories that must exist before a pipeline run."""
        return [
            self.output_research, self.output_drafts, self.output_reviewed,
            self.output_latex, self.output_pdf, self.output_assets, self.log_dir,
        ]

    @property
    def artifact_instructions(self) -> str:
        """Render the required-artifact list as agent prompt instructions."""
        lines = [
            _ARTIFACT_MAP[t.strip()]
            for t in self.required_artifacts.split(",")
            if t.strip() in _ARTIFACT_MAP
        ]
        return "\n".join(lines) if lines else "- No specific artifact requirements configured"

    def build_llm(self):
        """Construct a CrewAI LLM for the configured provider (ollama/zhipuai)."""
        from crewai import LLM
        if self.llm_provider == "ollama":
            model = self.llm_model if self.llm_model.startswith("ollama/") else f"ollama/{self.llm_model}"
            return LLM(model=model, base_url=self.llm_base_url)
        if self.llm_provider == "zhipuai":
            return LLM(
                model=f"openai/{self.llm_model}",
                api_base=self.llm_base_url,
                api_key=os.environ.get("ZHIPUAI_API_KEY", ""),
            )
        return None
