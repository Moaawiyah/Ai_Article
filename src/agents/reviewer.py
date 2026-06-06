"""Reviewer agent factory."""

from crewai import Agent


def build_reviewer(llm=None) -> Agent:
    """Create the Reviewer agent."""
    return Agent(
        role="Reviewer Agent",
        goal="Review the article draft for correctness, completeness, and assignment fit.",
        backstory=(
            "You are a strict but constructive academic reviewer. You check structure, "
            "citation readiness, required artifacts, and whether the article can become a "
            "credible 15-page submission."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
