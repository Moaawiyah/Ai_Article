"""CrewAI article-generation entry point."""

from crewai import Crew, Process

from agents.latex_formatter import build_latex_formatter
from agents.pdf_validator import build_pdf_validator
from agents.researcher import build_researcher
from agents.reviewer import build_reviewer
from agents.writer import build_writer
from agent_ai.shared.config import PROJECT_TOPIC, AppConfig, build_llm
from tasks.latex_task import build_latex_task
from tasks.research_task import build_research_task
from tasks.review_task import build_review_task
from tasks.validation_task import build_validation_task
from tasks.writing_task import build_writing_task
from utils.file_utils import ensure_output_dirs
from utils.logger import configure_logger


def build_crew(config: AppConfig | None = None) -> Crew:
    """Build the sequential CrewAI pipeline for the article generator."""
    config = config or AppConfig.from_env()
    ensure_output_dirs(config.output_dirs)
    logger = configure_logger(config.log_level)
    llm = build_llm(config)

    researcher = build_researcher(llm)
    writer = build_writer(llm)
    reviewer = build_reviewer(llm)
    latex_formatter = build_latex_formatter(llm)
    pdf_validator = build_pdf_validator(llm)

    research_task = build_research_task(researcher, config)
    # TODO: Insert a RAG retrieval/indexing stage here later, between research and writing.
    writing_task = build_writing_task(writer, config, research_task)
    review_task = build_review_task(reviewer, config, writing_task)
    latex_task = build_latex_task(latex_formatter, config, review_task)
    validation_task = build_validation_task(pdf_validator, config, latex_task)

    logger.info("Built CrewAI pipeline for topic: %s", PROJECT_TOPIC)
    return Crew(
        agents=[researcher, writer, reviewer, latex_formatter, pdf_validator],
        tasks=[research_task, writing_task, review_task, latex_task, validation_task],
        process=Process.sequential,
        verbose=True,
    )


def main() -> None:
    """Run the full five-agent article pipeline."""
    config = AppConfig.from_env()
    crew = build_crew(config)
    crew.kickoff(inputs={"topic": PROJECT_TOPIC})

if __name__ == "__main__":
    main()
