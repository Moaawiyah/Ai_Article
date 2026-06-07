"""LaTeX formatting task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig


def build_latex_task(agent: Agent, config: AppConfig | PipelineConfig, review_task: Task) -> Task:
    """Create the LuaLaTeX formatting task."""
    out = config.output_latex if hasattr(config, "output_latex") else config.output_root / "latex"
    return Task(
        description=(
            "Read outputs/reviewed/reviewed.md and convert it into a complete, valid "
            "LuaLaTeX source file. Save the output to outputs/latex/article.tex.\n\n"
            "Follow your skill instructions exactly. Key rules:\n\n"
            "PACKAGES — preamble must include: fontspec (Latin Modern Roman), geometry "
            "(a4paper, 2.5cm margins), fancyhdr, amsmath, amssymb, tikz with the "
            "arrows.meta/positioning/shapes.geometric/calc libraries, pgfplots, "
            "graphicx, booktabs, caption, float, hyperref with hidelinks, microtype, "
            "setspace with onehalfspacing. No polyglossia. No biblatex.\n\n"
            "HEADER/FOOTER — pagestyle-fancy and all fancyhdr definitions must appear "
            "AFTER the begin-document command, never in the preamble.\n\n"
            "CONVERSIONS:\n"
            "  Level-2 Markdown heading  → LaTeX section command\n"
            "  Level-3 Markdown heading  → LaTeX subsection command\n"
            "  Markdown pipe table       → booktabs tabular environment with H placement\n"
            "  Display math ($$...$$)    → equation environment\n"
            "  TIKZ comment marker       → complete tikzpicture figure (see skill)\n"
            "  Numbered citation [N]     → cite command with refN key\n"
            "  Bold / italic / code      → textbf / textit / texttt commands\n\n"
            "BIBLIOGRAPHY — convert the References section and its numbered entries "
            "into a thebibliography environment with bibitem entries.\n\n"
            "OUTPUT — pure LaTeX only. No Markdown syntax. No fenced code blocks. "
            "No Hebrew text or BiDi environments. "
            "The end-document command must be the very last line."
        ),
        expected_output=(
            "A single complete LuaLaTeX source file (article.tex) with: full preamble "
            "(fontspec, fancyhdr, amsmath, tikz, booktabs, hyperref — no biblatex, "
            "no polyglossia), maketitle, tableofcontents, all sections converted from "
            "Markdown, a booktabs table, an equation environment, a tikzpicture figure, "
            "cite commands for all citations, and a thebibliography at the end. "
            "Pure LaTeX — no Markdown remaining."
        ),
        agent=agent,
        context=[review_task],
        output_file=str(out / "article.tex"),
    )
