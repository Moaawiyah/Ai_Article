"""LaTeX formatter agent factory."""

from crewai import Agent

from utils.skill_loader import load_skill


def build_latex_formatter(llm=None) -> Agent:
    """Create the LaTeX Formatter agent from skills/latex_formatter/SKILL.md."""
    skill = load_skill("latex_formatter")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
