"""Writer agent factory."""

from crewai import Agent

from utils.skill_loader import load_skill


def build_writer(llm=None) -> Agent:
    """Create the Writer agent from skills/writer/SKILL.md."""
    skill = load_skill("writer")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
