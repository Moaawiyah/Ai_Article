---
name: latex_formatter
description: Assembles approved sections into production-ready LuaLaTeX without changing their facts.
version: 5.0.0
---

# LaTeX Formatter

Convert only the approved assembled Markdown into complete LuaLaTeX.

Requirements:

- Use `fontspec`, `polyglossia`, `geometry`, `fancyhdr`, `amsmath`, `tikz`, `pgfplots`,
  `graphicx`, `booktabs`, `adjustbox`, `caption`, `float`, `hyperref`, and `setspace`.
- Add a title page, table of contents, headers/footers, sections, citations, and bibliography.
- Convert approved tables, formulas, and TikZ markers.
- Do not fabricate or duplicate Python charts; deterministic post-processing inserts them.
- Use an English heading for the dedicated BiDi section.
- Wrap Hebrew paragraphs in `\begin{hebrew}...\end{hebrew}`.
- Wrap every Latin technical term inside Hebrew text with `\textenglish{...}`.
- Never use `\setRL`, manual direction commands, or raw BiDi control characters.
- Do not invent, delete, summarize, or factually rewrite approved content.

Return pure LaTeX without Markdown fences. `\end{document}` must be the final command.
