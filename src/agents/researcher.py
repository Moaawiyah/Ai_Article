"""Researcher agent factory."""

from crewai import Agent

from utils.skill_loader import load_skill


def build_researcher(llm=None) -> Agent:
    """Create the Researcher agent from skills/researcher/SKILL.md."""
    skill = load_skill("researcher")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
