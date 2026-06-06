"""Review task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig


def build_review_task(agent: Agent, config: AppConfig, writing_task: Task) -> Task:
    """Create the review task that consumes the Writer output."""
    return Task(
        description=(
            "Review the Writer Agent draft for academic quality, assignment compliance, "
            "structure, citation readiness, and completeness.\n"
            "Check that the draft includes or clearly reserves space for: cover page, table "
            "of contents, chapters/sections, headers/footers, image placeholder, "
            "Python-generated graph placeholder, table, mathematical formula, "
            "Hebrew-English BiDi section, and bibliography."
        ),
        expected_output=(
            "A reviewed Markdown document or review report with concrete fixes, missing "
            "requirements, and readiness status."
        ),
        agent=agent,
        context=[writing_task],
        output_file=str(config.output_root / "reviewed" / "reviewed_article.md"),
    )
