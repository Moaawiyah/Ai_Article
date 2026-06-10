"""Single agent factory — replaces the per-agent build_*.py copy-paste duplication.

Every agent in the crew shares the same construction shape (skill → CrewAI
Agent). The only thing that differs between agents is the skill name, so the
five per-agent files are collapsed into one parametrised function.
"""

from __future__ import annotations

from crewai import Agent

from utils.skill_loader import load_skill


def build_agent(skill_name: str, llm=None) -> Agent:
    """Create a CrewAI Agent from ``skills/<skill_name>/SKILL.md``.

    Input:
        skill_name: directory name under ``skills/`` (e.g. ``"researcher"``).
        llm:        optional CrewAI LLM instance.
    Output:
        A configured ``crewai.Agent``.
    """
    skill = load_skill(skill_name)
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
