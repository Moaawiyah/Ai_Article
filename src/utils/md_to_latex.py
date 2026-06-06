"""Modular Markdown-to-LaTeX converter for LuaLaTeX output.

Each public function handles one structural element.
The top-level convert() function composes them into a full .tex document.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Preamble
# ---------------------------------------------------------------------------

_PREAMBLE = r"""
\documentclass[12pt,a4paper]{article}

% ── Fonts & language ────────────────────────────────────────────────────────
\usepackage{fontspec}
\setmainfont{Times New Roman}

\usepackage{polyglossia}
\setdefaultlanguage{english}
\setotherlanguage{hebrew}
% Hebrew font (requires a Hebrew-capable font installed, e.g. David CLM)
\newfontfamily\hebrewfont[Script=Hebrew]{David CLM}

% ── Page layout ─────────────────────────────────────────────────────────────
\usepackage[a4paper, margin=2.5cm]{geometry}

% ── Headers & footers ───────────────────────────────────────────────────────
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\nouppercase{\leftmark}}   % section name on left
\fancyhead[R]{\thepage}                  % page number on right
\fancyfoot[C]{\small Multi-Agent Collaboration Systems}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% ── Mathematics ─────────────────────────────────────────────────────────────
\usepackage{amsmath}
\usepackage{amssymb}

% ── Figures & tables ────────────────────────────────────────────────────────
\usepackage{graphicx}
\graphicspath{{../assets/}}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{float}

% ── Hyperlinks ──────────────────────────────────────────────────────────────
\usepackage[hidelinks, colorlinks=false]{hyperref}

% ── Bibliography  ───────────────────────────────────────────────────────────
% FUTURE CITATION AUTOMATION: replace the \bibliography command below with
% the path to your generated .bib file and switch to biber as the backend.
\usepackage[backend=biber, style=ieee]{biblatex}
\addbibresource{references.bib}

% ── Misc ────────────────────────────────────────────────────────────────────
\usepackage{microtype}
\usepackage{setspace}
\onehalfspacing
""".strip()


def build_preamble() -> str:
    """Return the LuaLaTeX preamble string."""
    return _PREAMBLE


# ---------------------------------------------------------------------------
# Title page
# ---------------------------------------------------------------------------

def build_title_block(title: str, author: str, course: str, date: str) -> str:
    """Return the LaTeX title-page commands."""
    author_line = f"\\author{{{_escape(author)}" + r"\\" + f"\\small{{{_escape(course)}}}}}\n"
    return (
        f"\\title{{{_escape(title)}}}\n"
        + author_line
        + f"\\date{{{_escape(date)}}}\n"
        "\\maketitle\n"
        "\\thispagestyle{empty}\n"
        "\\newpage\n"
    )


# ---------------------------------------------------------------------------
# Element converters
# ---------------------------------------------------------------------------

def convert_headings(text: str) -> str:
    """Convert Markdown headings to LaTeX section commands.

    ## Heading  → \\section{Heading}
    ### Heading → \\subsection{Heading}
    #### Heading → \\subsubsection{Heading}
    """
    text = re.sub(r"^#### (.+)$", lambda m: f"\\subsubsection{{{_escape(m.group(1))}}}", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$",  lambda m: f"\\subsection{{{_escape(m.group(1))}}}", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$",   lambda m: f"\\section{{{_escape(m.group(1))}}}", text, flags=re.MULTILINE)
    return text


def convert_bold_italic(text: str) -> str:
    """Convert **bold** and *italic* Markdown to LaTeX commands."""
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: f"\\textbf{{{m.group(1)}}}", text)
    text = re.sub(r"\*(.+?)\*",     lambda m: f"\\textit{{{m.group(1)}}}", text)
    return text


def convert_inline_code(text: str) -> str:
    """Convert `inline code` to \\texttt{}."""
    return re.sub(r"`(.+?)`", lambda m: f"\\texttt{{{_escape(m.group(1))}}}", text)


def convert_formulas(text: str) -> str:
    """Convert $$...$$ display-math blocks to LaTeX equation environments.

    Inline $...$ is left unchanged (already valid LaTeX).
    """
    def _to_equation(m: re.Match) -> str:
        inner = m.group(1).strip()
        return f"\\begin{{equation}}\n{inner}\n\\end{{equation}}"

    return re.sub(r"\$\$(.+?)\$\$", _to_equation, text, flags=re.DOTALL)


def convert_images(text: str) -> str:
    """Convert Markdown image syntax to LaTeX figure environments.

    Preserves placeholder paths so they can be swapped for real assets later.
    """
    def _to_figure(m: re.Match) -> str:
        alt  = m.group(1)
        path = m.group(2)
        # Extract a short caption from the alt text
        caption = _escape(alt.replace("Figure: ", ""))
        filename = Path(path).name
        return (
            "\\begin{figure}[H]\n"
            "  \\centering\n"
            f"  \\includegraphics[width=0.85\\textwidth]{{{filename}}}\n"
            f"  \\caption{{{caption}}}\n"
            "  % ASSET PLACEHOLDER: replace filename with actual generated file\n"
            "\\end{figure}"
        )

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _to_figure, text)


def convert_tables(text: str) -> str:
    """Convert Markdown pipe tables to LaTeX booktabs tables."""
    table_pattern = re.compile(
        r"((?:\|.+\|\n)+)",
        re.MULTILINE,
    )

    def _to_table(m: re.Match) -> str:
        raw = m.group(1).strip()
        rows = [r.strip().strip("|").split("|") for r in raw.splitlines()]
        # rows[0] = header, rows[1] = separator (--), rows[2:] = data
        if len(rows) < 2:
            return m.group(0)

        header = rows[0]
        data   = [r for r in rows[2:] if not all(c.strip().startswith("-") for c in r)]
        col_spec = "l" * len(header)

        lines = [
            "\\begin{table}[H]",
            "  \\centering",
            f"  \\begin{{tabular}}{{{col_spec}}}",
            "    \\toprule",
            "    " + " & ".join(_escape(h.strip()) for h in header) + " \\\\",
            "    \\midrule",
        ]
        for row in data:
            cells = " & ".join(_escape(c.strip()) for c in row)
            lines.append(f"    {cells} \\\\")
        lines += [
            "    \\bottomrule",
            "  \\end{tabular}",
            "  \\caption{TODO: add table caption}",
            "\\end{table}",
        ]
        return "\n".join(lines)

    return table_pattern.sub(_to_table, text)


def convert_bidi_blocks(text: str) -> str:
    """Convert <!-- RTL --> ... <!-- /RTL --> markers to polyglossia Hebrew environment."""
    def _to_hebrew(m: re.Match) -> str:
        inner = m.group(1).strip()
        return (
            "\\begin{hebrew}\n"
            "\\setRL\n"          # right-to-left typesetting
            f"{inner}\n"
            "\\end{hebrew}"
        )

    return re.sub(
        r"<!--\s*RTL\s*-->(.*?)<!--\s*/RTL\s*-->",
        _to_hebrew,
        text,
        flags=re.DOTALL,
    )


def convert_citations(text: str) -> str:
    """Convert [N] inline citation markers to LaTeX \\cite{refN} commands.

    FUTURE CITATION AUTOMATION: replace refN keys with real BibTeX keys
    once the .bib file is generated from the bibliography section.
    """
    return re.sub(r"\[(\d+)\]", lambda m: f"\\cite{{ref{m.group(1)}}}", text)


def convert_bibliography(text: str) -> str:
    """Replace a Markdown ## Bibliography section with a LaTeX printbibliography command.

    FUTURE CITATION AUTOMATION: parse the bibliography entries here and
    generate a .bib file automatically before calling \\printbibliography.
    """
    bib_pattern = re.compile(
        r"^## Bibliography\b.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    replacement = (
        "% FUTURE CITATION AUTOMATION: parse entries above and write references.bib\n"
        "\\printbibliography"
    )
    return bib_pattern.sub(lambda _: replacement, text, count=1)


# ---------------------------------------------------------------------------
# Top-level converter
# ---------------------------------------------------------------------------

def convert(
    markdown: str,
    title: str = "Untitled Article",
    author: str = "[Author Name]",
    course: str = "[Course Name, Institution]",
    date: str = "\\today",
) -> str:
    """Convert a full Markdown document to a LuaLaTeX .tex string.

    Conversion order matters — apply structural transforms before inline ones.
    """
    body = markdown

    # Structural transforms
    body = convert_bidi_blocks(body)
    body = convert_bibliography(body)
    body = convert_tables(body)
    body = convert_formulas(body)
    body = convert_images(body)
    body = convert_headings(body)

    # Inline transforms
    body = convert_bold_italic(body)
    body = convert_inline_code(body)
    body = convert_citations(body)

    # Remove any remaining Markdown artifacts
    body = _strip_markdown_artifacts(body)

    preamble   = build_preamble()
    title_block = build_title_block(title, author, course, date)

    return (
        f"{preamble}\n\n"
        "\\begin{document}\n\n"
        f"{title_block}\n"
        "\\tableofcontents\n"
        "\\newpage\n\n"
        f"{body}\n\n"
        "\\end{document}\n"
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_LATEX_SPECIAL = str.maketrans({
    "&":  r"\&",
    "%":  r"\%",
    "$":  r"\$",
    "#":  r"\#",
    "_":  r"\_",
    "{":  r"\{",
    "}":  r"\}",
    "~":  r"\textasciitilde{}",
    "^":  r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
})


def _escape(text: str) -> str:
    """Escape LaTeX special characters in plain text."""
    return text.translate(_LATEX_SPECIAL)


def _strip_markdown_artifacts(text: str) -> str:
    """Remove leftover Markdown syntax that has no LaTeX equivalent."""
    # Horizontal rules
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^===+$", "", text, flags=re.MULTILINE)
    # HTML comments not already converted
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text
