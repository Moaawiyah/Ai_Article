"""Markdown element converters for the LuaLaTeX pipeline."""

from __future__ import annotations

import re
from pathlib import Path

from utils.md_document import escape


def convert_headings(text: str) -> str:
    text = re.sub(r"^#### (.+)$", lambda m: f"\\subsubsection{{{escape(m.group(1))}}}", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$",  lambda m: f"\\subsection{{{escape(m.group(1))}}}", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$",   lambda m: f"\\section{{{escape(m.group(1))}}}", text, flags=re.MULTILINE)
    return text


def convert_bold_italic(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: f"\\textbf{{{m.group(1)}}}", text)
    text = re.sub(r"\*(.+?)\*",     lambda m: f"\\textit{{{m.group(1)}}}", text)
    return text


def convert_inline_code(text: str) -> str:
    return re.sub(r"`(.+?)`", lambda m: f"\\texttt{{{escape(m.group(1))}}}", text)


def convert_formulas(text: str) -> str:
    def _to_equation(m: re.Match) -> str:
        return f"\\begin{{equation}}\n{m.group(1).strip()}\n\\end{{equation}}"
    return re.sub(r"\$\$(.+?)\$\$", _to_equation, text, flags=re.DOTALL)


def convert_images(text: str) -> str:
    def _to_figure(m: re.Match) -> str:
        caption  = escape(m.group(1).replace("Figure: ", ""))
        filename = Path(m.group(2)).name
        return (
            "\\begin{figure}[H]\n"
            "  \\centering\n"
            f"  \\includegraphics[width=0.85\\textwidth]{{{filename}}}\n"
            f"  \\caption{{{caption}}}\n"
            "  % ASSET PLACEHOLDER\n"
            "\\end{figure}"
        )
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _to_figure, text)


def convert_tables(text: str) -> str:
    _count = [0]

    def _is_numeric_col(cells: list) -> bool:
        non_empty = [c.strip() for c in cells if c.strip()]
        return bool(non_empty) and all(
            re.match(r"^-?[\d.,]+\s*[\%GBMKkms]?$", c) for c in non_empty
        )

    def _to_table(m: re.Match) -> str:
        raw  = m.group(1).strip()
        rows = [r.strip().strip("|").split("|") for r in raw.splitlines()]
        if len(rows) < 2:
            return m.group(0)
        header = rows[0]
        data   = [r for r in rows[2:] if not all(c.strip().startswith("-") for c in r)]
        ncols  = len(header)

        col_align = [
            "r" if _is_numeric_col([row[i] for row in data if i < len(row)]) else "l"
            for i in range(ncols)
        ]
        col_spec = "".join(col_align)

        _count[0] += 1
        label = f"tab:{_count[0]}"

        inner = [
            f"  \\begin{{tabular}}{{{col_spec}}}", "    \\toprule",
            "    " + " & ".join(escape(h.strip()) for h in header) + " \\\\",
            "    \\midrule",
        ]
        for row in data:
            inner.append("    " + " & ".join(escape(c.strip()) for c in row) + " \\\\")
        inner += ["    \\bottomrule", "  \\end{tabular}"]

        lines = ["\\begin{table}[H]", "  \\centering"]
        if ncols >= 4:
            lines.append("  \\resizebox{\\textwidth}{!}{%")
            lines.extend(inner)
            lines.append("  }")
        else:
            lines.extend(inner)
        cap = " & ".join(escape(h.strip()) for h in header)
        lines += [f"  \\caption{{{cap}}}", f"  \\label{{{label}}}", "\\end{table}"]
        return "\n".join(lines)

    return re.compile(r"((?:\|.+\|\n)+)", re.MULTILINE).sub(_to_table, text)


def convert_citations(text: str) -> str:
    return re.sub(r"\[(\d+)\]", lambda m: f"\\cite{{ref{m.group(1)}}}", text)


def convert_bibliography(text: str) -> str:
    return re.compile(r"^## (?:Bibliography|References)\b.*$", re.MULTILINE | re.IGNORECASE).sub(
        lambda _: "\\newpage\n\\begin{thebibliography}{99}", text, count=1
    )


def strip_markdown_artifacts(text: str) -> str:
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^===+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text
