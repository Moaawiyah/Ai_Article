"""Top-level Markdown-to-LaTeX converter.

Composes md_document and md_converters into a full .tex document.
"""

from __future__ import annotations

from agent_ai.utils.md_converters import (
    convert_bibliography,
    convert_bold_italic,
    convert_citations,
    convert_formulas,
    convert_headings,
    convert_images,
    convert_inline_code,
    convert_tables,
    strip_markdown_artifacts,
)
from agent_ai.utils.md_document import build_preamble, build_title_block


def convert(
    markdown: str,
    title: str = "Untitled Article",
    author: str = "[Author Name]",
    course: str = "[Course Name]",
    date: str = "\\today",
) -> str:
    """Convert a full Markdown document to a LuaLaTeX .tex string."""
    body = markdown

    body = convert_bibliography(body)
    body = convert_tables(body)
    body = convert_formulas(body)
    body = convert_images(body)
    body = convert_headings(body)
    body = convert_bold_italic(body)
    body = convert_inline_code(body)
    body = convert_citations(body)
    body = strip_markdown_artifacts(body)

    preamble    = build_preamble()
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
