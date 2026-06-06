"""LaTeX formatting task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig


def build_latex_task(agent: Agent, config: AppConfig, review_task: Task) -> Task:
    """Create the LuaLaTeX formatting task."""
    return Task(
        description=(
            "Convert the reviewed article content into a LuaLaTeX-compatible article.tex.\n"
            "The .tex must include a cover page, table of contents, chapters or sections, "
            "headers/footers, image placeholder, Python-generated graph placeholder, table, "
            "mathematical formula, Hebrew-English BiDi section, and bibliography.\n"
            "Use LuaLaTeX-friendly package choices such as fontspec, polyglossia or bidi "
            "where appropriate, and keep placeholder paths under outputs/assets."
        ),
        expected_output=(
            "A complete LuaLaTeX-compatible article.tex document, including comments for "
            "asset placeholders and bibliography entries."
        ),
        agent=agent,
        context=[review_task],
        output_file=str(config.output_root / "latex" / "article.tex"),
    )
