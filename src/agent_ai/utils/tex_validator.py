"""Programmatic validator — checks 9–13 and top-level validate() entry point."""

from __future__ import annotations

import re
from pathlib import Path

from agent_ai.utils.validator_checks import (
    check_formula,
    check_headers_footers,
    check_pdf_exists,
    check_sections,
    check_table,
    check_tex_exists,
    check_title_page,
    check_toc,
)
from agent_ai.utils.validator_types import CheckResult, ValidationReport


def _check_tikz(tex: str) -> CheckResult:
    has_tikz = bool(re.search(r"\\begin\s*\{tikzpicture\}", tex))
    if has_tikz:
        m = re.search(r"(\\begin\s*\{tikzpicture\}[^\n]*)", tex)
        return CheckResult("9. TikZ figure", True, f"`{m.group(1).strip()}`")
    return CheckResult("9. TikZ figure", False, "No `\\begin{tikzpicture}` environment found",
                       "Ensure `<!-- TIKZ: ... -->` marker was converted to a tikzpicture figure")


def _check_citations(tex: str) -> CheckResult:
    cites = re.findall(r"\\cite\{[^}]+\}", tex)
    if len(cites) >= 3:
        preview = ", ".join(f"`{c}`" for c in cites[:2])
        return CheckResult("10. Inline citations", True, f"{len(cites)} `\\cite{{}}` commands — e.g. {preview}")
    if cites:
        return CheckResult("10. Inline citations", False,
                           f"Only {len(cites)} `\\cite` command(s) found (need ≥3)",
                           "Add inline citations throughout the article body")
    return CheckResult("10. Inline citations", False, "No `\\cite{}` commands found",
                       "Ensure `[N]` markers were converted to `\\cite{refN}`")


def _check_english_only(tex: str) -> CheckResult:
    has_hebrew_env  = bool(re.search(r"\\begin\s*\{hebrew\}", tex))
    has_setrl       = r"\setRL" in tex
    has_polyglossia = "polyglossia" in tex
    has_heb_chars   = bool(re.search(r"[֐-׿]", tex))
    violations = (
        (["`\\begin{hebrew}`"] if has_hebrew_env else [])
        + (["`\\setRL`"] if has_setrl else [])
        + (["`polyglossia`"] if has_polyglossia else [])
        + (["Hebrew Unicode chars"] if has_heb_chars else [])
    )
    if violations:
        return CheckResult("11. English only", False, f"Found: {', '.join(violations)}",
                           "Remove all Hebrew/BiDi content — article must be English only")
    return CheckResult("11. English only", True, "No Hebrew environments, polyglossia, or BiDi content found")


def _check_bibliography(tex: str) -> CheckResult:
    has_thebib = bool(re.search(r"\\begin\s*\{thebibliography\}", tex))
    bibitems   = len(re.findall(r"\\bibitem\{", tex))
    if has_thebib and bibitems >= 8:
        return CheckResult("12. Bibliography", True,
                           f"`\\begin{{thebibliography}}` with {bibitems} `\\bibitem` entries")
    if has_thebib:
        return CheckResult("12. Bibliography", False,
                           f"`\\begin{{thebibliography}}` found but only {bibitems} `\\bibitem` entries (need ≥8)",
                           "Add more `\\bibitem` entries to the bibliography")
    return CheckResult("12. Bibliography", False, "No `\\begin{thebibliography}` found",
                       "Convert ## References section to `\\begin{thebibliography}{99}...\\end{thebibliography}`")


def _check_compilation(pdf_path: Path, log_path: Path) -> CheckResult:
    if pdf_path.exists():
        return CheckResult("13. LaTeX compilation", True, f"PDF present at `{pdf_path}`")
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("!"):
                return CheckResult("13. LaTeX compilation", False,
                                   f"Error: `{line.strip()}`",
                                   f"Open `{log_path}` and search for '!' lines")
        return CheckResult("13. LaTeX compilation", False,
                           "PDF not found; no explicit error line in log", f"Review `{log_path}`")
    return CheckResult("13. LaTeX compilation", False, "PDF not found and no compile log exists",
                       "Run `python src/main.py`")


def validate(tex_path: Path, pdf_path: Path, log_path: Path, report_path: Path) -> ValidationReport:
    """Run all 13 checks and write the validation report. Never raises."""
    tex = tex_path.read_text(encoding="utf-8", errors="replace") if tex_path.exists() else ""
    report = ValidationReport(checks=[
        check_tex_exists(tex_path),
        check_pdf_exists(pdf_path),
        check_title_page(tex),
        check_toc(tex),
        check_headers_footers(tex),
        check_sections(tex),
        check_table(tex),
        check_formula(tex),
        _check_tikz(tex),
        _check_citations(tex),
        _check_english_only(tex),
        _check_bibliography(tex),
        _check_compilation(pdf_path, log_path),
    ])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.as_markdown(tex_path, pdf_path, log_path), encoding="utf-8")
    return report
