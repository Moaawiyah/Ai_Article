"""LaTeX formatting task factory."""

from crewai import Agent, Task

from shared.config import AppConfig, PipelineConfig


def build_latex_task(agent: Agent, config: AppConfig | PipelineConfig, review_task: Task) -> Task:
    """Create the LuaLaTeX formatting task."""
    out = config.output_latex if hasattr(config, "output_latex") else config.output_root / "latex"
    return Task(
        description=(
            "Read outputs/reviewed/reviewed.md and convert it into a complete, valid "
            "LuaLaTeX source file. Save the output to outputs/latex/article.tex.\n\n"
            "Follow your skill instructions exactly. Key rules:\n\n"
            "AUTHOR/COURSE — set author to \"Moa'awiyah \\& Mohammed\" and course to "
            "\"Orchestra Agentic AI\" in the title block.\n\n"
            "PACKAGES — preamble must include: fontspec (setmainfont Times New Roman), "
            "polyglossia (setdefaultlanguage english, setotherlanguage hebrew, "
            "newfontfamily hebrewfont with Script=Hebrew and Times New Roman), "
            "geometry (a4paper, 2.5cm margins), fancyhdr with headheight 15pt, "
            "amsmath, amssymb, tikz with the arrows.meta/positioning/shapes.geometric/calc "
            "libraries, pgfplots, graphicx, booktabs, adjustbox, caption, float, "
            "hyperref with hidelinks, microtype, setspace with onehalfspacing. No biblatex.\n\n"
            "HEADER/FOOTER — pagestyle-fancy and all fancyhdr definitions must appear "
            "AFTER the begin-document command. Use this exact setup after begin-document:\n"
            "  pagestyle fancy, fancyhf empty, fancyhead left with small title text, "
            "  fancyhead right empty, fancyfoot center with thepage.\n\n"
            "BILINGUAL CONCLUSION — the Conclusion section contains Hebrew prose paragraphs "
            "naturally interspersed with English. Convert it as follows:\n"
            "  - The heading is a plain section command with 'Conclusion' — no change.\n"
            "  - Wrap each Hebrew paragraph in a begin-hebrew / end-hebrew environment.\n"
            "  - Inside every hebrew environment, wrap each English word, acronym, or term "
            "in a textenglish command so it renders left-to-right.\n"
            "  - English-only paragraphs in the Conclusion stay as plain LaTeX text.\n"
            "  - Do not use setRL or any manual direction commands.\n"
            "  - Do not add any label or comment indicating the section is bilingual.\n\n"
            "CONVERSIONS:\n"
            "  Level-2 Markdown heading  -> LaTeX section command\n"
            "  Level-3 Markdown heading  -> LaTeX subsection command\n"
            "  Markdown pipe table       -> booktabs tabular environment with H placement\n"
            "  Display math ($$...$$)    -> equation environment\n"
            "  TIKZ comment marker       -> complete tikzpicture figure (see skill)\n"
            "  Numbered citation [N]     -> cite command with refN key\n"
            "  Bold / italic / code      -> textbf / textit / texttt commands\n\n"
            "CITATIONS — convert every [N] marker to a cite command. "
            "Every paragraph should reference at least one bibitem.\n\n"
            "BIBLIOGRAPHY — convert the References section into a thebibliography environment "
            "with bibitem entries, preceded by newpage.\n\n"
            "OUTPUT — pure LaTeX only. No Markdown syntax. No fenced code blocks. "
            "The end-document command must be the very last line."
        ),
        expected_output=(
            "A single complete LuaLaTeX source file (article.tex) with: full preamble "
            "(fontspec, polyglossia with hebrew, fancyhdr, amsmath, tikz, booktabs, "
            "hyperref — no biblatex), maketitle, tableofcontents, all sections converted "
            "from Markdown, a booktabs table, an equation environment, a tikzpicture figure, "
            "a Conclusion section with Hebrew paragraphs in begin-hebrew/end-hebrew environments "
            "and textenglish wrapping for English terms inside them, cite commands for all "
            "citations, and a "
            "thebibliography at the end. Pure LaTeX — no Markdown remaining."
        ),
        agent=agent,
        context=[review_task],
        output_file=str(out / "article.tex"),
    )
