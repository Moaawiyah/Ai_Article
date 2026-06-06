"""Research task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import PROJECT_TOPIC, AppConfig


def build_research_task(agent: Agent, config: AppConfig) -> Task:
    """Create the direct research task."""
    return Task(
        description=(
            f"Research the topic: {PROJECT_TOPIC}.\n"
            "Gather and summarize information directly; do not use a RAG index or retriever.\n"
            "Produce a structured research brief that covers multi-agent collaboration "
            "patterns, CrewAI sequential team design, local Ollama execution, article "
            "structure, citation candidates, image/graph/table/formula opportunities, "
            "and Hebrew-English BiDi requirements.\n"
            "Mark uncertain facts and citation candidates clearly."
        ),
        expected_output=(
            "A Markdown research brief with section-level notes, key claims, citation "
            "candidates, required artifact ideas, and gaps to verify later."
        ),
        agent=agent,
        output_file=str(config.output_root / "research" / "research_brief.md"),
    )
