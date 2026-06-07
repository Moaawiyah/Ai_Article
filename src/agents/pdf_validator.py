"""PDF validator agent factory."""

from crewai import Agent

from utils.skill_loader import load_skill


def build_pdf_validator(llm=None) -> Agent:
    """Create the PDF Validator agent from skills/pdf_validator/SKILL.md."""
    skill = load_skill("pdf_validator")
    return Agent(
        role=skill.role,
        goal=skill.description,
        backstory=skill.body,
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
