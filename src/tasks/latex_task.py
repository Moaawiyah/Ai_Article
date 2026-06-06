"""LaTeX formatting task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig

_INPUT_FILE = "outputs/reviewed/reviewed.md"

_DESCRIPTION = """
You are a LuaLaTeX document formatter.

Read the reviewed article from: outputs/reviewed/reviewed.md
Produce a complete, valid LuaLaTeX source file saved to: outputs/latex/article.tex

---

## 1. Document class and preamble

Use `\\documentclass` with options `[12pt,a4paper]` and class `article`.

Include these packages in the preamble:
- `fontspec` — set main font to Times New Roman
- `polyglossia` — set default language to english, other language to hebrew; define \\hebrewfont with David CLM font
- `geometry` — a4paper, 2.5cm margins on all sides
- `fancyhdr` — enable fancy page style with left header showing section name, right header showing page number, center footer showing article title; set headrulewidth and footrulewidth to 0.4pt
- `amsmath` and `amssymb` — mathematics support
- `graphicx` — include graphics; set graphicspath to `../assets/` (relative to the tex file location in outputs/latex/)
- `booktabs`, `caption`, `float` — for tables and figures
- `hyperref` with hidelinks option
- `biblatex` with backend=biber and style=ieee; add bibliography resource from `references.bib` (the file is in the same directory as the .tex file)
- `microtype` and `setspace` — set onehalfspacing

---

## 2. Document body structure

After `\\begin` document, output in this exact order:

1. Title block: use `\\title` for the article title, `\\author` with name and course/institution on second line, `\\date` set to today, then `\\maketitle`, then `\\thispagestyle` set to empty, then `\\newpage`.

2. Table of contents: `\\tableofcontents` followed by `\\newpage`.

3. All sections from the reviewed article (see conversion rules below).

4. Bibliography: `\\printbibliography` at the end.

5. `\\end` document — this MUST be the last line.

---

## 3. Conversion rules

Apply these rules to every element in outputs/reviewed/reviewed.md:

### Headings
- Markdown `##` → `\\section` command with the heading text in braces
- Markdown `###` → `\\subsection` command
- Markdown `####` → `\\subsubsection` command

### Tables
Convert every Markdown pipe table to a booktabs LaTeX table:
Use `\\begin` table with [H] placement, `\\centering`, `\\begin` tabular with column spec,
`\\toprule`, header row with & separators and `\\\\`, `\\midrule`, data rows, `\\bottomrule`,
`\\end` tabular, `\\caption` with table description, `\\end` table.

### Mathematical formulas
Convert display math (dollar-dollar delimited) blocks to equation environments:
Use `\\begin` equation ... `\\end` equation.
Leave inline single-dollar math unchanged.

### Images and graph placeholders
Convert every Markdown image to a figure environment:
Use `\\begin` figure with [H], `\\centering`, `\\includegraphics` with width=0.85\\textwidth and the image filename in braces, `\\caption` with the alt text, a comment "% ASSET PLACEHOLDER: replace with actual file before compiling", `\\end` figure.

Preserve filenames `architecture_diagram.png` and `task_completion_graph.png` exactly — both must appear in the output.

### Hebrew–English BiDi section
Convert every <!-- RTL --> ... <!-- /RTL --> block to a polyglossia Hebrew environment:
Use `\\begin` hebrew, `\\setRL`, the Hebrew text, `\\end` hebrew.
English text before and after stays in the default language.

### Inline citations
Convert every [N] citation marker to `\\cite` with refN as the key.
Add comment "% FUTURE CITATION AUTOMATION: replace refN with actual BibTeX keys" above the first cite in each section.

### Bold / italic / code
- `**text**` → `\\textbf` with text in braces
- `*text*` → `\\textit` with text in braces
- backtick code → `\\texttt` with text in braces

---

## 4. Rules and constraints

- Do NOT invent content. Convert only what is in outputs/reviewed/reviewed.md.
- All LaTeX environments must be properly opened and closed.
- The output must be syntactically valid LuaLaTeX — no unclosed environments.
- Do not include markdown fences or any Markdown syntax in the output. Pure LaTeX only.
- Preserve all placeholder comments.
- The LAST line of the file must be `\\end` document.
""".strip()

_EXPECTED_OUTPUT = (
    "A single, complete, syntactically valid LuaLaTeX source file (article.tex) containing: "
    "a full preamble with fontspec/polyglossia/fancyhdr/biblatex, a title page, "
    "\\\\tableofcontents, all article sections converted from Markdown, booktabs tables, "
    "equation environments, figure environments for image and graph placeholders, "
    "a polyglossia Hebrew environment for the BiDi section, \\\\cite commands for all "
    "inline citations, and \\\\printbibliography. No Markdown syntax. Pure LaTeX only."
)


def build_latex_task(agent: Agent, config: AppConfig | PipelineConfig, review_task: Task) -> Task:
    """Create the LuaLaTeX formatting task."""
    out = config.output_latex if hasattr(config, "output_latex") else config.output_root / "latex"
    return Task(
        description=_DESCRIPTION,
        expected_output=_EXPECTED_OUTPUT,
        agent=agent,
        context=[review_task],
        output_file=str(out / "article.tex"),
    )
