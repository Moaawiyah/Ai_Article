"""Reviewer agent factory."""

from crewai import Agent

from utils.skill_loader import load_skill


def build_reviewer(llm=None) -> Agent:
    """Create the Reviewer agent from skills/reviewer/SKILL.md."""
    skill = load_skill("reviewer")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
