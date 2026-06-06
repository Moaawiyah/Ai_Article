"""Researcher agent factory."""

from crewai import Agent

from agent_ai.shared.config import PROJECT_TOPIC


def build_researcher(llm=None) -> Agent:
    """Create the Researcher agent."""
    return Agent(
        role="Researcher Agent",
        goal=(
            "Gather and summarize direct background information for an academic article "
            f"about {PROJECT_TOPIC}."
        ),
        backstory=(
            "You are a careful academic researcher who prepares structured research briefs. "
            "You work without a RAG index in this version, so you clearly distinguish known "
            "concepts, citation candidates, and gaps that need later verification."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
