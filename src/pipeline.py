"""Builder for the resumable six-agent article workflow."""

from __future__ import annotations

from shared.gatekeeper import ApiGatekeeper
from shared.pipeline_config import PipelineConfig
from utils.file_utils import ensure_output_dirs
from utils.logger import configure_logger
from workflow.orchestrator import ArticleWorkflow
from workflow.runner import CrewStageRunner


def build_workflow(
    gatekeeper: ApiGatekeeper,
    cfg: PipelineConfig | None = None,
) -> tuple[ArticleWorkflow, PipelineConfig]:
    """Build the configured section workflow without executing it."""
    cfg = cfg or PipelineConfig.load()
    ensure_output_dirs(cfg.output_dirs)
    log = configure_logger(
        level=cfg.log_level,
        log_dir=cfg.log_dir,
        log_file=cfg.log_file,
    )
    log.info("Six-agent section workflow configured for %s", cfg.topic)
    runner = CrewStageRunner(cfg.build_llm(), gatekeeper)
    return ArticleWorkflow(cfg, runner), cfg
