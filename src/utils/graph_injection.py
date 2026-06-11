"""Inject a generated benchmark figure into a LaTeX article."""

from __future__ import annotations

import re
from pathlib import Path

_TEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _tex_escape(text: str) -> str:
    """Escape LaTeX special characters in source descriptions."""
    return "".join(_TEX_SPECIALS.get(char, char) for char in text)


def inject_graph(tex_path: Path, filename: str, spec: dict) -> None:
    """Insert a benchmark figure before the section following Evaluation."""
    series = (spec["main"], spec["arch_a"], spec["arch_b"])
    sources = ", ".join(
        dict.fromkeys(item["source"] for item in series if item.get("source"))
    )
    if all(item.get("data_basis") == "measured" for item in series) and sources:
        basis_note = f"Based on published measurements ({_tex_escape(sources)})."
    elif sources:
        basis_note = (
            "Curves combine published measurements and literature-informed "
            f"estimates ({_tex_escape(sources)})."
        )
    else:
        basis_note = "Curves are illustrative, literature-informed estimates."
    caption = (
        "Left: CDF of bottleneck queue length. "
        "Right: average FCT vs.\\ network load. "
        f"Comparison of {spec['main']['name']} vs.\\ {spec['arch_a']['name']} "
        f"vs.\\ {spec['arch_b']['name']}. {basis_note}"
    )
    figure = (
        "\n\\begin{figure}[H]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=\\textwidth]{{{filename}}}\n"
        f"  \\caption{{{caption}}}\n"
        "  \\label{fig:perf}\n"
        "\\end{figure}\n"
    )
    source = tex_path.read_text(encoding="utf-8")
    evaluation = re.search(r"\\section\{[^}]*[Ee]valuation[^}]*\}", source)
    if evaluation:
        following = re.search(r"\n\\section\{", source[evaluation.end() :])
        if following:
            position = evaluation.end() + following.start()
        else:
            bibliography = source.find("\\begin{thebibliography}")
            position = bibliography if bibliography != -1 else source.rfind("\\end{document}")
    else:
        bibliography = source.find("\\begin{thebibliography}")
        position = bibliography if bibliography != -1 else source.rfind("\\end{document}")
    source = source[:position] + "\n" + figure + source[position:]
    tex_path.write_text(source, encoding="utf-8")
