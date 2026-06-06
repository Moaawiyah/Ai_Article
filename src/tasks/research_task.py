"""Research task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig


def build_research_task(agent: Agent, config: AppConfig | PipelineConfig) -> Task:
    """Create the direct research task."""
    topic = config.topic if isinstance(config, PipelineConfig) else str(config.output_root)
    topic = config.topic if hasattr(config, "topic") else "Multi-Agent Collaboration Systems"
    out   = config.output_research if hasattr(config, "output_research") else config.output_root / "research"

    return Task(
        description=(
            f"Research the topic: {topic}.\n"
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
        output_file=str(out / "research_brief.md"),
    )
