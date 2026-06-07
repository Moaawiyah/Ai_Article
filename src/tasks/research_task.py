"""Research task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig


def build_research_task(agent: Agent, config: AppConfig | PipelineConfig) -> Task:
    """Create the research task. The researcher freely decides section structure."""
    topic     = config.topic if hasattr(config, "topic") else "Unknown Topic"
    out       = config.output_research if hasattr(config, "output_research") else config.output_root / "research"
    artifacts = config.artifact_instructions if hasattr(config, "artifact_instructions") else ""

    description = (
        f"Research topic: {topic}\n\n"
        "Your tasks:\n"
        "1. Research this topic in depth from your knowledge.\n"
        "2. Propose a logical academic article structure — decide section titles and\n"
        "   order yourself based on what makes sense for this topic.\n"
        "3. For each proposed section, write research notes: key claims, definitions,\n"
        "   trade-offs, and inline citation markers [CITE: N].\n"
        "4. Collect bibliography candidates — real, verifiable references only.\n"
        "5. Identify where these required artifacts naturally fit in your proposed structure:\n"
        f"{artifacts}\n\n"
        "Follow your skill for output format and quality rules.\n"
        "Do not draft full article prose — notes only."
    )

    return Task(
        description=description,
        expected_output=(
            "A Markdown research brief with: (1) proposed section structure, "
            "(2) research notes per section with [CITE: N] markers, "
            "(3) bibliography candidates [N] Author, Title, Venue, Year, "
            "(4) artifact map specifying where each required artifact fits and what it shows."
        ),
        agent=agent,
        output_file=str(out / "research_brief.md"),
    )
