"""Writing task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import PROJECT_TOPIC, AppConfig


def build_writing_task(agent: Agent, config: AppConfig, research_task: Task) -> Task:
    """Create the writing task that consumes the Researcher output."""
    # TODO: When RAG is added, pass retrieved context here alongside the research brief.
    return Task(
        description=(
            f"Write a ~15-page academic article draft on: {PROJECT_TOPIC}.\n"
            "Use the Researcher Agent output as your context. Do not assume a RAG retrieval "
            "bundle exists in this version.\n"
            "Include sections/chapters, citations or citation placeholders, an image "
            "placeholder, a Python-generated graph placeholder, at least one table, at "
            "least one mathematical formula, a Hebrew-English BiDi section, and a "
            "bibliography section."
        ),
        expected_output=(
            "A complete Markdown article draft with clear headings, citation placeholders, "
            "required artifact placeholders, formula, table, BiDi section, and bibliography."
        ),
        agent=agent,
        context=[research_task],
        output_file=str(config.output_root / "drafts" / "article_draft.md"),
    )
