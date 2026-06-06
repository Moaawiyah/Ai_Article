"""PDF validation task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig


def build_validation_task(agent: Agent, config: AppConfig, latex_task: Task) -> Task:
    """Create the PDF readiness validation task."""
    return Task(
        description=(
            "Validate the generated LaTeX/PDF readiness against the assignment checklist.\n"
            "Check explicitly for: cover page, table of contents, chapters/sections, "
            "headers/footers, at least one image placeholder, at least one Python-generated "
            "graph placeholder, at least one table, at least one mathematical formula, "
            "Hebrew-English BiDi section, and bibliography.\n"
            "Return blocking issues, non-blocking polish issues, and a final readiness status."
        ),
        expected_output=(
            "A validation report with pass/fail status for each requirement and ordered "
            "fix recommendations."
        ),
        agent=agent,
        context=[latex_task],
        output_file=str(config.output_root / "pdf" / "validation_report.md"),
    )
