"""Build the benchmark figure's LaTeX block and inject it into article.tex.

Split out of ``pipeline_steps.py`` so each module stays a thin orchestrator under
the 150-LoC budget. ``inject_figure`` owns caption wording (with source
provenance) and the placement logic that drops the figure into the Evaluation
section, falling back to before the bibliography / end of document.
"""

from __future__ import annotations

import re
from pathlib import Path

_TEX_SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def _tex_escape(text: str) -> str:
    """Escape LaTeX special characters in free text (e.g. LLM-supplied sources)."""
    return "".join(_TEX_SPECIALS.get(ch, ch) for ch in text)


def _build_caption(spec: dict) -> str:
    """Compose the figure caption, noting whether curves are measured or estimated."""
    name_a, name_b = spec["arch_a"]["name"], spec["arch_b"]["name"]
    series = (spec["main"], spec["arch_a"], spec["arch_b"])
    all_measured = all(s.get("data_basis") == "measured" for s in series)
    # de-dupe sources while preserving order
    sources = ", ".join(dict.fromkeys(s["source"] for s in series if s.get("source")))
    if all_measured and sources:
        basis_note = f"Based on published measurements ({_tex_escape(sources)})."
    elif sources:
        basis_note = (
            f"Curves combine published measurements and literature-informed "
            f"estimates ({_tex_escape(sources)})."
        )
    else:
        basis_note = "Curves are illustrative, literature-informed estimates."
    return (
        f"Left: CDF of bottleneck queue length. "
        f"Right: average FCT vs.\\ network load. "
        f"Comparison of {spec['main']['name']} vs.\\ {name_a} vs.\\ {name_b}. "
        f"{basis_note}"
    )


def _place(source: str, figure_block: str) -> str:
    """Return *source* with *figure_block* inserted at the best location.

    Preference order: after the Evaluation section, else before the
    bibliography, else just before ``\\end{document}``.
    """
    eval_m = re.search(r'\\section\{[^}]*[Ee]valuation[^}]*\}', source)
    if eval_m:
        next_m = re.search(r'\n\\section\{', source[eval_m.end():])
        if next_m:
            pos = eval_m.end() + next_m.start()
            return source[:pos] + "\n" + figure_block + source[pos:]
        bib = source.find("\\begin{thebibliography}")
        pos = bib if bib != -1 else source.rfind("\\end{document}")
        return source[:pos] + figure_block + "\n" + source[pos:]
    bib = source.find("\\begin{thebibliography}")
    if bib != -1:
        return source[:bib] + figure_block + "\n" + source[bib:]
    return source.replace("\\end{document}", figure_block + "\\end{document}")


def inject_figure(tex_path: Path, filename: str, spec: dict, log) -> None:
    """Insert the generated benchmark figure (with caption) into ``tex_path``."""
    figure_block = (
        "\n\\begin{figure}[H]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=\\textwidth]{{{filename}}}\n"
        f"  \\caption{{{_build_caption(spec)}}}\n"
        "  \\label{fig:perf}\n"
        "\\end{figure}\n"
    )
    source = tex_path.read_text(encoding="utf-8")
    tex_path.write_text(_place(source, figure_block), encoding="utf-8")
    log.info("Graph injected into Evaluation section → %s", tex_path.parent / filename)
