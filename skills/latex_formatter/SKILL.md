---
name: latex_formatter
description: Converts a reviewed Markdown article into a complete, valid LuaLaTeX source file ready for compilation into a professional academic PDF. Handles TikZ figures, tables, math, and biblatex references.
version: 3.0.0
---

# LaTeX Formatter

## Purpose

Use this skill when an agent must transform a reviewed Markdown article into a
production-ready LuaLaTeX `.tex` file. The output must be syntactically correct,
fully structured, and include all required academic document elements.

This skill does NOT compile the PDF. It produces only the `.tex` source.
The article is English-only — no Hebrew, no polyglossia, no BiDi content.

---

## Input

- File: `outputs/reviewed/reviewed.md`
- Format: Markdown with headings, tables, display math, `<!-- TIKZ: ... -->` markers,
  citation markers `[N]`, and a Bibliography section.

---

## Output

- File: `outputs/latex/article.tex`
- Format: Complete, valid LuaLaTeX source. No Markdown. No fenced code blocks.

---

## Required document structure

Produce the output in this exact order:

1. **Preamble** — packages listed below, in order
2. `\begin{document}`
3. Title page: `\maketitle`, `\newpage`
4. `\tableofcontents` + `\newpage`
5. All sections (converted from Markdown headings)
6. `\printbibliography`
7. `\end{document}` — this MUST be the last line

---

## Required packages (do not omit or reorder)

| Package | Purpose |
|---|---|
| `fontspec` | Unicode font selection (LuaLaTeX) |
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

## Conversion rules

### Headings

- `##` heading → `\section{...}`
- `###` heading → `\subsection{...}`
- `####` heading → `\subsubsection{...}`

Each section command on its own line with a blank line above it.

### Tables

Convert every Markdown pipe table to a booktabs `table` environment:
- Placement: `[H]`
- Use `\toprule`, `\midrule`, `\bottomrule`
- Add `\caption{...}` (never leave it empty) and `\label{tab:...}`
- Centre the table with `\centering`
- **Always** wrap the `tabular` environment with `\adjustbox{max width=\textwidth}{...}` to prevent overflow:
  ```latex
  \adjustbox{max width=\textwidth}{
    \begin{tabular}{...}
      ...
    \end{tabular}
  }
  ```

### Mathematical formulas

- Display math `$$...$$` → `\begin{equation}...\end{equation}`
- Inline `$...$` → leave unchanged
- Preserve all LaTeX math commands (`\max`, `\left`, `\right`, superscripts, subscripts)

### TikZ figure markers

This is the most important conversion rule. When you encounter a comment of the form:
```
<!-- TIKZ: <description> -->
```

Replace it with a complete `\begin{figure}[H]...\end{figure}` containing a hand-written
`tikzpicture` environment that visually represents the description.

**TikZ reserved key warning**: Never name a style after a pgf built-in key. Forbidden style names: `id`, `name`, `node`, `label`, `text`, `draw`, `fill`, `color`, `at`, `to`, `every`, `scale`, `shift`, `above`, `below`, `left`, `right`, `anchor`. Use descriptive names like `mynode`, `ctrl`, `sw`, `arr`, `probe` instead.

For the fat-tree topology marker, generate a TikZ figure like this (adapt as needed):

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
Do not add any comment about "future automation". Every `[N]` in the body must become `\cite{refN}` in the output.

### Bibliography section

Replace the `## References` heading and its numbered list entries with a
`\begin{thebibliography}` environment. Each `[N] Author, "Title," Venue, Year.`
entry becomes a `\bibitem{refN}` item:

```latex
\newpage
\begin{thebibliography}{99}
\bibitem{ref1} Author(s), ``Title,'' \textit{Venue}, Year.
\bibitem{ref2} ...
\end{thebibliography}
```

Always put `\newpage` immediately before `\begin{thebibliography}` so the bibliography starts on a fresh page.

Use `\cite{refN}` for inline citation markers `[N]` throughout the article.

### Inline formatting

- `**text**` → `\textbf{text}`
- `*text*` → `\textit{text}`
- `` `code` `` → `\texttt{code}`

---

## Preamble template

Use this exact preamble structure (fill in the title/author/date from the article):

```latex
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\setmainfont{Times New Roman}
\usepackage[a4paper, margin=2.5cm]{geometry}
\usepackage{fancyhdr}
\setlength{\headheight}{14pt}
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
\author{[Author Name] \\ \small{[Course Name]}}
\date{\today}
```

Place all `\pagestyle{fancy}` and `\fancyhdr` setup lines **after** `\begin{document}`.

---

## Rules and constraints

- Do NOT invent content. Convert only what is in the input file.
- The output must be syntactically valid LuaLaTeX with no unclosed environments.
- Do not include any Markdown syntax or fenced code blocks in the output.
- Every section command must be on its own line with a blank line above.
- Do not compile or run the LaTeX compiler. Output `.tex` source only.
- No Hebrew, no `polyglossia`, no BiDi content of any kind.
- The TikZ figure is a first-class requirement — never skip or simplify it.

---

## Quality checklist

- [ ] Preamble includes all required packages in the correct order
- [ ] `tikz` and `pgfplots` packages present; `\usetikzlibrary` line present
- [ ] Title page and TOC with `\newpage` separators present
- [ ] All `##` headings converted to `\section{}`; `###` to `\subsection{}`
- [ ] All pipe tables converted to booktabs `table` environments
- [ ] All `$$...$$` blocks converted to `equation` environments
- [ ] `<!-- TIKZ: ... -->` marker converted to a full `tikzpicture` figure
- [ ] All `[N]` citation markers converted to `\cite{refN}`
- [ ] `\begin{thebibliography}` present at end before `\end{document}` with ≥8 `\bibitem` entries
- [ ] No Markdown syntax remaining in the output
- [ ] No unclosed `\begin` / `\end` pairs
- [ ] No `polyglossia` or Hebrew environments anywhere
