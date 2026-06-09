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
            "PACKAGES — preamble must include: fontspec, polyglossia (BiDi support), geometry "
            "(a4paper, 2.5cm margins), fancyhdr, amsmath, amssymb, tikz with the "
            "arrows.meta/positioning/shapes.geometric/calc libraries, pgfplots, "
            "graphicx, booktabs, caption, float, hyperref with hidelinks, microtype, "
            "setspace with onehalfspacing. No biblatex.\n\n"
            "HEADER/FOOTER — pagestyle-fancy and all fancyhdr definitions must appear "
            "AFTER the begin-document command, never in the preamble.\n\n"
            "CONVERSIONS:\n"
            "  Level-2 Markdown heading  → LaTeX section command\n"
            "  Level-3 Markdown heading  → LaTeX subsection command\n"
            "  Markdown pipe table       → booktabs tabular environment with H placement\n"
            "  Display math ($$...$$)    → equation environment\n"
            "  TIKZ comment marker       → complete tikzpicture figure (see skill)\n"
            "  Numbered citation [N]     → cite command with refN key\n"
            "  Bold / italic / code      → textbf / textit / texttt commands\n"
            "  Inline Hebrew sentences   → wrap each Hebrew run in texthebrew so it renders RTL; "
            "all section headings stay English (no Hebrew in headings or table of contents)\n\n"
            "BIBLIOGRAPHY — convert the References section and its numbered entries "
            "into a thebibliography environment with bibitem entries.\n\n"
            "OUTPUT — pure LaTeX only. No Markdown syntax. No fenced code blocks. "
            "Hebrew sentences wrapped in texthebrew; all headings English. "
            "The end-document command must be the very last line."
        ),
        expected_output=(
            "A single complete LuaLaTeX source file (article.tex) with: full preamble "
            "(fontspec, polyglossia with Hebrew, fancyhdr, amsmath, tikz, booktabs, hyperref — "
            "no biblatex), maketitle, tableofcontents, all sections converted from "
            "Markdown, one bilingual section (English heading) with Hebrew wrapped in texthebrew, "
            "a booktabs table, an equation environment, a tikzpicture figure, "
            "cite commands for all citations, and a thebibliography at the end. "
            "Pure LaTeX — no Markdown remaining."
        ),
        agent=agent,
        context=[review_task],
        output_file=str(out / "article.tex"),
    )
