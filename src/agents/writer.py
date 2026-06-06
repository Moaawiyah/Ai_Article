"""Writer agent factory."""

from crewai import Agent

from agent_ai.shared.config import PROJECT_TOPIC


def build_writer(llm=None) -> Agent:
    """Create the Writer agent."""
    return Agent(
        role="Writer Agent",
        goal=(
            "Write a coherent long-form academic article draft using the Researcher "
            f"Agent output as context for {PROJECT_TOPIC}."
        ),
        backstory=(
            "You are an academic technical writer. You transform structured research notes "
            "into clear sections with citations, artifact placeholders, and publication-ready "
            "organization."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
