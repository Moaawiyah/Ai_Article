"""LaTeX formatter agent factory."""

from crewai import Agent


def build_latex_formatter(llm=None) -> Agent:
    """Create the LaTeX Formatter agent."""
    return Agent(
        role="LaTeX Formatter Agent",
        goal="Convert reviewed article content into LuaLaTeX-compatible .tex.",
        backstory=(
            "You are a publication formatter who knows LuaLaTeX, bibliography structure, "
            "figure/table placement, formulas, headers, footers, and Hebrew-English "
            "bidirectional typesetting."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )
