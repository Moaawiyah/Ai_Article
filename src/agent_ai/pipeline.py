"""CrewAI crew builder for the article pipeline."""

from crewai import Crew, Process

from agent_ai.agents.factory import build_agent
from agent_ai.shared.config import PipelineConfig
from agent_ai.tasks.latex_task import build_latex_task
from agent_ai.tasks.research_task import build_research_task
from agent_ai.tasks.review_task import build_review_task
from agent_ai.tasks.validation_task import build_validation_task
from agent_ai.tasks.writing_task import build_writing_task
from agent_ai.utils.file_utils import ensure_output_dirs
from agent_ai.utils.logger import configure_logger


def build_crew(cfg: PipelineConfig | None = None) -> tuple[Crew, PipelineConfig]:
    """Build the sequential CrewAI pipeline from config.yaml."""
    cfg = cfg or PipelineConfig.load()
    ensure_output_dirs(cfg.output_dirs)

    log = configure_logger(level=cfg.log_level, log_dir=cfg.log_dir, log_file=cfg.log_file)
    log.info("Pipeline config loaded")
    log.info("  topic    : %s", cfg.topic)
    log.info("  llm      : %s/%s", cfg.llm_provider, cfg.llm_model)
    log.info("  outputs  : %s", cfg.output_root)

    llm = cfg.build_llm()

    researcher      = build_agent("researcher",      llm)
    writer          = build_agent("writer",          llm)
    reviewer        = build_agent("reviewer",        llm)
    latex_formatter = build_agent("latex_formatter", llm)
    pdf_validator   = build_agent("pdf_validator",   llm)

    research_task   = build_research_task(researcher, cfg)
    writing_task    = build_writing_task(writer, cfg, research_task)
    review_task     = build_review_task(reviewer, cfg, writing_task)
    latex_task      = build_latex_task(latex_formatter, cfg, review_task)
    validation_task = build_validation_task(pdf_validator, cfg, latex_task)

    log.info("Crew assembled — 5 agents, 5 tasks, sequential process")
    crew = Crew(
        agents  = [researcher, writer, reviewer, latex_formatter, pdf_validator],
        tasks   = [research_task, writing_task, review_task, latex_task, validation_task],
        process = Process.sequential,
        verbose = True,
    )
    return crew, cfg
