"""Writer agent factory."""

from crewai import Agent

from utils.figure_tools import generate_architecture_diagram, generate_performance_graph
from utils.skill_loader import load_skill


def build_writer(llm=None) -> Agent:
    """Create the Writer agent from skills/writer/SKILL.md."""
    skill = load_skill("writer")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        tools=[generate_architecture_diagram, generate_performance_graph],
        allow_delegation=False,
        verbose=True,
    )
