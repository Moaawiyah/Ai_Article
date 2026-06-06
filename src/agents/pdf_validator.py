"""PDF validator agent factory."""

from crewai import Agent


def build_pdf_validator(llm=None) -> Agent:
    """Create the PDF Validator agent."""
    return Agent(
        role="PDF Validator Agent",
        goal="Validate the LaTeX/PDF deliverable against the assignment checklist.",
        backstory=(
            "You are a final submission validator. You inspect whether the generated "
            "document includes every required academic and formatting element before the "
            "student submits it."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
