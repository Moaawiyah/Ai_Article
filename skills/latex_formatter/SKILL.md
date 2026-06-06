---
name: latex_formatter
description: Converts a reviewed Markdown article into a complete, valid LuaLaTeX source file ready for compilation into a professional academic PDF.
version: 2.1.0
---

# LaTeX Formatter

## Purpose

Use this skill when an agent must transform a reviewed Markdown article into a
production-ready LuaLaTeX `.tex` file. The output must be syntactically correct,
fully structured, and include all required academic document elements.

This skill does NOT compile the PDF. It produces only the `.tex` source.

---

## Input

- File: `outputs/reviewed/reviewed.md`
- Format: Markdown with headings, tables, display math, image syntax,
  RTL BiDi markers, citation markers, and a Bibliography section.

---

## Output

- File: `outputs/latex/article.tex`
- Format: Complete, valid LuaLaTeX source. No Markdown. No fenced code blocks.

---

## Required document structure

Produce the output in this exact order:

1. **Preamble** — packages listed below, in order
2. `\begin` document
3. Title page: `\maketitle`, `\thispagestyle` empty, `\newpage`
4. `\tableofcontents` + `\newpage`
5. All sections (converted from Markdown headings)
6. `\printbibliography`
7. `\end` document — this MUST be the last line

---

## Required packages (do not omit or reorder)

| Package | Purpose |
|---|---|
| `fontspec` | Unicode font selection (LuaLaTeX) |
| `polyglossia` | Hebrew + English bilingual support |
| `geometry` | Page margins (a4paper, 2.5 cm) |
| `fancyhdr` | Headers and footers |
| `amsmath`, `amssymb` | Mathematical environments |
| `graphicx` | Image inclusion |
| `booktabs` | Professional tables |
| `caption`, `float` | Figure/table captions and H placement |
| `hyperref` | Clickable cross-references (hidelinks) |
| `biblatex` (biber) | Bibliography (ieee style) |
| `microtype` | Typographic refinement |
| `setspace` | Line spacing (onehalfspacing) |

---

## Conversion rules

### Headings

Use `\section` command with the heading text for `##` level headings.
Use `\subsection` for `###` level. Use `\subsubsection` for `####` level.
Always use proper LaTeX brace syntax: `\section` followed by the heading in braces.

### Tables

Convert every Markdown pipe table to a booktabs table environment with
H placement, `\toprule`, `\midrule`, `\bottomrule`, and a `\caption`.

### Mathematical formulas

Convert display math (double-dollar delimited) to an equation environment.
Leave inline single-dollar math unchanged.

### Images and graph placeholders

Convert Markdown image syntax to a figure environment with H placement,
`\includegraphics` at 0.85 textwidth, and a `\caption`. Preserve filenames exactly.
Add comment: `% ASSET PLACEHOLDER: replace with actual file before compiling`

### Hebrew-English BiDi section

Convert RTL marker blocks to a polyglossia hebrew environment:
Open with `\begin` hebrew and `\setRL`, include the Hebrew text,
then close with `\end` hebrew.
English text before and after stays in the default language.

### Inline citations

Convert `[N]` citation markers to `\cite` commands with `refN` as the key.
Add this comment above the first cite in each section:
`% FUTURE CITATION AUTOMATION: replace refN with actual BibTeX keys`

### Bibliography section

Replace the Bibliography heading and its entries with:
`% FUTURE CITATION AUTOMATION: parse entries above and generate references.bib`
followed by `\printbibliography`

### Inline formatting

Convert `**text**` to `\textbf` with text in braces.
Convert `*text*` to `\textit` with text in braces.
Convert backtick code to `\texttt` with text in braces.

---

## Rules and constraints

- Do NOT invent content. Convert only what is in the input file.
- The output must be syntactically valid LuaLaTeX with no unclosed environments.
- Do not include Markdown syntax or fenced code blocks anywhere in the output.
- Every section command must be on its own line with a blank line above.
- Do not compile or run the LaTeX compiler. Output `.tex` only.
- Preserve all placeholder comments (ASSET PLACEHOLDER, FUTURE CITATION AUTOMATION).
- The BiDi section is a first-class requirement — never skip or simplify it.

---

## Quality checklist

- [ ] Preamble includes all required packages in the correct order
- [ ] Title page, TOC, and newpage separators are present
- [ ] All Markdown headings converted to section / subsection commands
- [ ] All tables converted to booktabs environments
- [ ] All display math blocks converted to equation environments
- [ ] Both image and graph placeholders converted to figure environments
- [ ] BiDi section wrapped in hebrew environment
- [ ] All citation markers converted to cite commands
- [ ] `\printbibliography` present at end
- [ ] No Markdown syntax remaining in the output
- [ ] No unclosed begin / end pairs
