---
name: latex_formatter
description: Converts a reviewed Markdown article into a complete, valid LuaLaTeX source file ready for compilation into a professional academic PDF. Handles TikZ figures, tables, math, biblatex references, and Hebrew/English BiDi sections.
version: 4.0.0
---

# LaTeX Formatter

## Purpose

Use this skill when an agent must transform a reviewed Markdown article into a
production-ready LuaLaTeX `.tex` file. The output must be syntactically correct,
fully structured, and include all required academic document elements, including
the Hebrew/English bilingual section.

This skill does NOT compile the PDF. It produces only the `.tex` source.

---

## Input

- File: `outputs/reviewed/reviewed.md`
- Format: Markdown with headings, tables, display math, `<!-- TIKZ: ... -->` markers,
  citation markers `[N]`, a bilingual section with Hebrew body text, and a Bibliography section.

---

## Output

- File: `outputs/latex/article.tex`
- Format: Complete, valid LuaLaTeX source. No Markdown. No fenced code blocks.

---

## Required document structure

Produce the output in this exact order:

1. **Preamble** — packages listed below, in order
2. `\begin{document}`
3. Header/footer setup (pagestyle, fancyhf — see template below)
4. Title page: `\maketitle`, `\newpage`
5. `\tableofcontents` + `\newpage`
6. All sections (converted from Markdown headings)
7. `\newpage` then `\begin{thebibliography}` at the end
8. `\end{document}` — this MUST be the last line

---

## Required packages (do not omit or reorder)

| Package | Purpose |
|---|---|
| `fontspec` | Unicode font selection (LuaLaTeX) |
| `polyglossia` | Bidirectional text / Hebrew support |
| `geometry` | Page margins (a4paper, 2.5 cm) |
| `fancyhdr` | Headers and footers |
| `amsmath`, `amssymb` | Mathematical environments |
| `tikz` | Native LaTeX figures |
| `pgfplots` | Data plots within TikZ |
| `graphicx` | Image inclusion (fallback) |
| `booktabs` | Professional tables |
| `adjustbox` | Resize wide tables to fit page width |
| `caption`, `float` | Figure/table captions and H placement |
| `hyperref` | Clickable cross-references (hidelinks) |
| `microtype` | Typographic refinement |
| `setspace` | Line spacing (onehalfspacing) |

After `\usepackage{tikz}` add this line:
```
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,calc}
```

---

## Preamble template

Use this exact preamble structure (fill in the title/author/date from the article):

```latex
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage{polyglossia}
\setdefaultlanguage{english}
\setotherlanguage{hebrew}
\newfontfamily\hebrewfont[Script=Hebrew]{Times New Roman}
\usepackage[a4paper, margin=2.5cm]{geometry}
\usepackage{fancyhdr}
\setlength{\headheight}{15pt}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,calc}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{graphicx}
\graphicspath{{./}}
\usepackage{booktabs}
\usepackage{adjustbox}
\usepackage{caption}
\usepackage{float}
\usepackage[hidelinks]{hyperref}
\usepackage{microtype}
\usepackage{setspace}
\onehalfspacing

\title{HULA: Scalable Load Balancing\\Using Programmable Data Planes}
\author{Moa'awiyah \& Mohammed \\ \small{Orchestra Agentic AI}}
\date{\today}
```

Place all `\pagestyle{fancy}` and `\fancyhdr` setup **after** `\begin{document}`, using
this exact block:

```latex
\begin{document}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small HULA: Scalable Load Balancing Using Programmable Data Planes}
\fancyhead[R]{}
\fancyfoot[C]{\thepage}
```

---

## Conversion rules

### Headings

- `##` heading → `\section{...}`
- `###` heading → `\subsection{...}`
- `####` heading → `\subsubsection{...}`

Each section command on its own line with a blank line above it.
All headings stay in English — even the bilingual section heading.

### Tables

Convert every Markdown pipe table to a booktabs `table` environment:
- Placement: `[H]`
- Use `\toprule`, `\midrule`, `\bottomrule`
- Add `\caption{...}` (never leave it empty) and `\label{tab:...}`
- Centre the table with `\centering`
- **Always** wrap the `tabular` environment with `\adjustbox{max width=\textwidth}{...}`:
  ```latex
  \adjustbox{max width=\textwidth}{
    \begin{tabular}{l p{4cm} p{4cm}}
      ...
    \end{tabular}
  }
  ```
- **Column spec rules:**
  - Use `l`, `c`, `r` only for short/numeric columns (IDs, numbers, short labels).
  - For any column that contains descriptive text or sentences, use `p{Xcm}` so the
    text wraps and the row grows taller instead of overflowing. Typical widths:
    - Short description (≤10 words): `p{3cm}`
    - Medium description (10–20 words): `p{4cm}`
    - Long description (20+ words): `p{5cm}`
  - Never use a bare `p` without a width argument.

### Mathematical formulas

- Display math `$$...$$` → `\begin{equation}...\end{equation}`
- Inline `$...$` → leave unchanged
- Preserve all LaTeX math commands (`\max`, `\left`, `\right`, superscripts, subscripts)

### TikZ figure markers

When you encounter a comment of the form:
```
<!-- TIKZ: <description> -->
```

Replace it with a complete `\begin{figure}[H]...\end{figure}` containing a hand-written
`tikzpicture` that visually represents the description.

**TikZ reserved key warning**: Never name a style after a pgf built-in key. Forbidden style names:
`id`, `name`, `node`, `label`, `text`, `draw`, `fill`, `color`, `at`, `to`, `every`, `scale`,
`shift`, `above`, `below`, `left`, `right`, `anchor`. Use descriptive names like `mynode`,
`ctrl`, `sw`, `arr`, `probe` instead.

For a fat-tree / data-plane topology, use this reference implementation:

```latex
\begin{figure}[H]
  \centering
  \begin{tikzpicture}[
    node distance=1.6cm,
    spine/.style={draw, rectangle, fill=blue!25, minimum width=1.5cm, minimum height=0.65cm, font=\small},
    leaf/.style={draw,  rectangle, fill=green!25, minimum width=1.5cm, minimum height=0.65cm, font=\small},
    srv/.style={draw,   rectangle, fill=gray!20,  minimum width=1.1cm, minimum height=0.55cm, font=\scriptsize},
    arr/.style={-{Stealth[length=4pt]}, thick},
    probe/.style={-{Stealth[length=4pt]}, dashed, red, thick},
  ]
    % Spine layer
    \node[spine] (s1) {Spine 1};
    \node[spine, right=2.2cm of s1] (s2) {Spine 2};
    % Leaf layer
    \node[leaf, below left=1.4cm and 0.4cm of s1]  (l1) {Leaf 1};
    \node[leaf, below right=1.4cm and 0.4cm of s1] (l2) {Leaf 2};
    \node[leaf, below left=1.4cm and 0.4cm of s2]  (l3) {Leaf 3};
    \node[leaf, below right=1.4cm and 0.4cm of s2] (l4) {Leaf 4};
    % Server layer
    \node[srv, below left=1.2cm and 0.0cm of l1]  (sv1) {Srv 1};
    \node[srv, below right=1.2cm and 0.0cm of l1] (sv2) {Srv 2};
    \node[srv, below left=1.2cm and 0.0cm of l4]  (sv7) {Srv 7};
    \node[srv, below right=1.2cm and 0.0cm of l4] (sv8) {Srv 8};
    % Data-plane edges (top-down)
    \draw[arr] (s1)--(l1); \draw[arr] (s1)--(l2);
    \draw[arr] (s2)--(l3); \draw[arr] (s2)--(l4);
    \draw[arr] (l1)--(sv1); \draw[arr] (l1)--(sv2);
    \draw[arr] (l4)--(sv7); \draw[arr] (l4)--(sv8);
    % HULA probes (bottom-up, dashed red)
    \draw[probe] (sv1) -- node[left, font=\tiny]{probe} (l1);
    \draw[probe] (l1)  -- node[left, font=\tiny]{probe} (s1);
  \end{tikzpicture}
  \caption{Fat-tree topology with HULA utilization probes (dashed arrows propagate bottom-up).}
  \label{fig:fat-tree}
\end{figure}
```

### Inline citations

Convert every `[N]` citation marker to `\cite{refN}` — no exceptions, no placeholders.
Every major claim in every section **must** have a `\cite{refN}` command.
Aim for at least one `\cite` per paragraph in the body.

### Bibliography section

Replace the `## References` heading and its numbered list with a `\begin{thebibliography}`
environment. Start with `\newpage`. Include **8 to 15 entries maximum** — if the source has
more than 15 references, include only the 15 most important ones.

```latex
\newpage
\begin{thebibliography}{99}
\bibitem{ref1} Author(s), ``Title,'' \textit{Venue}, Year.
\bibitem{ref2} ...
\end{thebibliography}
```

### Inline formatting

- `**text**` → `\textbf{text}`
- `*text*` → `\textit{text}`
- `` `code` `` → `\texttt{code}`

### Hebrew text inside the Conclusion section

The Conclusion section contains Hebrew prose naturally interspersed with English paragraphs.
The section heading is `\section{Conclusion}` — a completely plain English heading; do NOT
add any label, comment, or indicator that it is bilingual.

Conversion rules:
1. Convert `\section{Conclusion}` normally — no change to the heading.
2. For each paragraph (or block of consecutive lines) that is written in Hebrew, wrap it in
   a `begin-hebrew` / `end-hebrew` environment:
   ```latex
   \begin{hebrew}
   מערכת \textenglish{HULA} מספקת איזון עומסים...
   \end{hebrew}
   ```
3. Inside every `begin-hebrew` block, wrap every English word, acronym, or technical term in
   `\textenglish{...}` so it renders left-to-right within the RTL paragraph.
4. English-only paragraphs in the Conclusion remain as plain LaTeX text — no special wrapping.
5. Do NOT use `\setRL` or any manual direction commands.
6. Do NOT add a separate section for the Hebrew content — it lives inside `\section{Conclusion}`.

---

## Rules and constraints

- Do NOT invent content. Convert only what is in the input file.
- The output must be syntactically valid LuaLaTeX with no unclosed environments.
- Do not include any Markdown syntax or fenced code blocks in the output.
- Every section command must be on its own line with a blank line above.
- Do not compile or run the LaTeX compiler. Output `.tex` source only.
- The TikZ figure is a first-class requirement — never skip or simplify it.

---

## Quality checklist

- [ ] Preamble includes all required packages (fontspec, polyglossia, fancyhdr, amsmath, tikz, booktabs, hyperref)
- [ ] `polyglossia` block present: setdefaultlanguage english, setotherlanguage hebrew, hebrewfont
- [ ] `tikz` and `pgfplots` packages present; `\usetikzlibrary` line present
- [ ] fancyhdr setup is AFTER `\begin{document}`: topic on left, empty right, `\thepage` center footer
- [ ] Title page and TOC with `\newpage` separators present
- [ ] All `##` headings converted to `\section{}`; `###` to `\subsection{}`; all headings in English
- [ ] All pipe tables converted to booktabs `table` environments with adjustbox; column spec uses l/c/r
- [ ] All `$$...$$` blocks converted to `equation` environments
- [ ] `<!-- TIKZ: ... -->` marker converted to a full `tikzpicture` figure
- [ ] All `[N]` citation markers converted to `\cite{refN}`; at least one cite per paragraph
- [ ] Conclusion section's Hebrew paragraphs wrapped in `\begin{hebrew}...\end{hebrew}` with `\textenglish{}` for English terms inside; heading is plain `\section{Conclusion}`
- [ ] `\begin{thebibliography}` present at end with 8–15 `\bibitem` entries, preceded by `\newpage`
- [ ] No Markdown syntax remaining in the output
- [ ] No unclosed `\begin` / `\end` pairs
