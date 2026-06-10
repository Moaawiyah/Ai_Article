"""LaTeX document structure: preamble, title block, and text escape helpers."""

from __future__ import annotations

_PREAMBLE = r"""
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
""".strip()

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


def escape(text: str) -> str:
    """Escape LaTeX special characters in plain text."""
    return text.translate(_LATEX_SPECIAL)


def build_preamble() -> str:
    return _PREAMBLE


def build_title_block(title: str, author: str, course: str, date: str) -> str:
    author_line = f"\\author{{{escape(author)}" + r"\\" + f"\\small{{{escape(course)}}}}}\n"
    return (
        f"\\title{{{escape(title)}}}\n"
        + author_line
        + f"\\date{{{escape(date)}}}\n"
        "\\maketitle\n"
        "\\newpage\n"
    )
