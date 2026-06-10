"""Unit tests for the CrewAI article pipeline config."""

from pathlib import Path

from agent_ai.shared.config import PROJECT_TOPIC, AppConfig, build_llm
from agent_ai.shared.pipeline_config import PipelineConfig
from agent_ai.utils.file_utils import ensure_output_dirs


def test_project_topic():
    assert PipelineConfig.load().topic == PROJECT_TOPIC
    assert PROJECT_TOPIC.strip()


def test_app_config_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ARTICLE_OUTPUT_ROOT", str(tmp_path / "article_outputs"))
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11435")
    monkeypatch.setenv("USE_OLLAMA", "false")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = AppConfig.from_env()

    assert config.output_root == tmp_path / "article_outputs"
    assert config.ollama_model == "llama3.1"
    assert config.ollama_base_url == "http://localhost:11435"
    assert config.use_ollama is False
    assert config.log_level == "DEBUG"


def test_output_dirs():
    config = AppConfig(
        output_root=Path("outputs"),
        ollama_model="qwen3:14b",
        ollama_base_url="http://localhost:11434",
        use_ollama=True,
        log_level="INFO",
    )

    assert config.output_dirs == [
        Path("outputs/research"),
        Path("outputs/drafts"),
        Path("outputs/reviewed"),
        Path("outputs/latex"),
        Path("outputs/pdf"),
        Path("outputs/assets"),
    ]


def test_build_llm_disabled():
    config = AppConfig(
        output_root=Path("outputs"),
        ollama_model="qwen3:14b",
        ollama_base_url="http://localhost:11434",
        use_ollama=False,
        log_level="INFO",
    )

    assert build_llm(config) is None


def test_ensure_output_dirs(tmp_path):
    paths = [tmp_path / "research", tmp_path / "drafts"]

    ensure_output_dirs(paths)

    assert all(path.is_dir() for path in paths)
