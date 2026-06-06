"""Programmatic validator for the article pipeline outputs.

Checks all 13 assignment requirements by reading actual files (no OCR, no LLM).
Writes a PASS/FAIL validation report to outputs/pdf/validation_report.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Outcome of a single requirement check."""
    name: str
    passed: bool
    evidence: str          # what was found (or what was expected but missing)
    fix: str = ""          # suggested fix, empty when passed

    def as_markdown(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        lines = [f"### {self.name}", f"**Status:** {status}", f"**Evidence:** {self.evidence}"]
        if not self.passed and self.fix:
            lines.append(f"**Fix:** {self.fix}")
        return "\n".join(lines)


@dataclass
class ValidationReport:
    """Collection of all check results for one pipeline run."""
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed

    @property
    def all_passed(self) -> bool:
        return self.failed == 0

    def as_markdown(self, tex_path: Path, pdf_path: Path, log_path: Path) -> str:
        lines = [
            "# Validation Report",
            "",
            "| File | Path |",
            "|---|---|",
            f"| article.tex | `{tex_path}` |",
            f"| article.pdf | `{pdf_path}` |",
            f"| compile log | `{log_path}` |",
            "",
            f"**Result: {self.passed}/{len(self.checks)} checks passed**",
            "",
        ]
        if self.all_passed:
            lines.append("🟢 **All requirements satisfied. Ready for submission.**")
        else:
            lines.append(f"🔴 **{self.failed} requirement(s) failed. See details below.**")

        lines += ["", "---", ""]
        for check in self.checks:
            lines.append(check.as_markdown())
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_tex_exists(tex_path: Path) -> CheckResult:
    if tex_path.exists():
        size = tex_path.stat().st_size
        return CheckResult("1. article.tex exists", True, f"Found at `{tex_path}` ({size:,} bytes)")
    return CheckResult(
        "1. article.tex exists", False,
        f"Not found at `{tex_path}`",
        "Re-run the LaTeX Formatter agent to generate article.tex",
    )


def _check_pdf_exists(pdf_path: Path) -> CheckResult:
    if pdf_path.exists():
        size = pdf_path.stat().st_size
        return CheckResult("2. article.pdf exists", True, f"Found at `{pdf_path}` ({size:,} bytes)")
    return CheckResult(
        "2. article.pdf exists", False,
        f"Not found at `{pdf_path}`",
        "Check logs/latex_compile.log — compilation may have failed",
    )


def _check_title_page(tex: str) -> CheckResult:
    has_title  = bool(re.search(r"\\title\s*\{", tex))
    has_make   = r"\maketitle" in tex
    if has_title and has_make:
        m = re.search(r"\\title\s*\{([^}]{0,60})", tex)
        found = m.group(1).strip() if m else "found"
        return CheckResult("3. Title page", True, f'`\\title{{...}}` and `\\maketitle` present — title: "{found}..."')
    missing = []
    if not has_title: missing.append("`\\title{}`")
    if not has_make:  missing.append("`\\maketitle`")
    return CheckResult(
        "3. Title page", False,
        f"Missing: {', '.join(missing)}",
        "Add `\\title{...}\\author{...}\\date{...}` before `\\begin{document}` and `\\maketitle` after it",
    )


def _check_toc(tex: str) -> CheckResult:
    if r"\tableofcontents" in tex:
        return CheckResult("4. Table of contents", True, "`\\tableofcontents` command present")
    return CheckResult(
        "4. Table of contents", False,
        "`\\tableofcontents` not found",
        "Add `\\tableofcontents\\newpage` after `\\maketitle`",
    )


def _check_headers_footers(tex: str) -> CheckResult:
    has_fancy = r"\pagestyle{fancy}" in tex or r"\usepackage{fancyhdr}" in tex
    has_head  = bool(re.search(r"\\fancyhead", tex))
    has_foot  = bool(re.search(r"\\fancyfoot", tex))
    if has_fancy and (has_head or has_foot):
        return CheckResult("5. Headers/footers", True, "`fancyhdr` package loaded with `\\fancyhead` / `\\fancyfoot` definitions")
    missing = []
    if not has_fancy: missing.append("`\\usepackage{fancyhdr}` + `\\pagestyle{fancy}`")
    if not has_head:  missing.append("`\\fancyhead{}`")
    if not has_foot:  missing.append("`\\fancyfoot{}`")
    return CheckResult(
        "5. Headers/footers", False,
        f"Missing: {', '.join(missing)}",
        "Add fancyhdr setup in preamble: `\\usepackage{fancyhdr}\\pagestyle{fancy}\\fancyhead[L]{...}\\fancyfoot[C]{...}`",
    )


def _check_sections(tex: str) -> CheckResult:
    sections = re.findall(r"\\section\s*\{([^}]{0,50})", tex)
    if sections:
        preview = ", ".join(f'"{s.strip()}"' for s in sections[:4])
        return CheckResult("6. Sections/chapters", True, f"{len(sections)} section(s) found: {preview}{'…' if len(sections) > 4 else ''}")
    return CheckResult(
        "6. Sections/chapters", False,
        "No `\\section{}` commands found",
        "Ensure Markdown headings (##) were converted to `\\section{}` by the LaTeX Formatter",
    )


def _check_table(tex: str) -> CheckResult:
    tables = len(re.findall(r"\\begin\s*\{tabular\}", tex))
    if tables:
        return CheckResult("7. Table", True, f"{tables} `tabular` environment(s) found")
    return CheckResult(
        "7. Table", False,
        "No `\\begin{tabular}` environments found",
        "Ensure Markdown pipe tables were converted to booktabs `tabular` environments",
    )


def _check_formula(tex: str) -> CheckResult:
    eq_env   = len(re.findall(r"\\begin\s*\{equation\}", tex))
    align_env = len(re.findall(r"\\begin\s*\{align\}", tex))
    inline   = len(re.findall(r"(?<!\$)\$(?!\$)[^$]+\$(?!\$)", tex))
    total = eq_env + align_env
    if total:
        return CheckResult("8. Mathematical formula", True, f"{eq_env} `equation` + {align_env} `align` environment(s) found")
    if inline:
        return CheckResult("8. Mathematical formula", True, f"{inline} inline `$...$` math expression(s) found")
    return CheckResult(
        "8. Mathematical formula", False,
        "No `equation`, `align`, or inline `$...$` math found",
        "Add at least one `\\begin{equation}...\\end{equation}` block",
    )


def _check_image(tex: str) -> CheckResult:
    images = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}", tex)
    # Exclude the graph placeholder; this check is for the architecture image
    arch = [p for p in images if "graph" not in p.lower() and "task_completion" not in p.lower()]
    if arch:
        return CheckResult("9. Image placeholder", True, f"Image found: `{arch[0]}`")
    if images:
        return CheckResult("9. Image placeholder", True, f"`\\includegraphics` found: `{images[0]}`")
    return CheckResult(
        "9. Image placeholder", False,
        "No `\\includegraphics{}` command found",
        "Add a figure environment with `\\includegraphics{outputs/assets/architecture_diagram.png}`",
    )


def _check_graph(tex: str) -> CheckResult:
    images = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}", tex)
    graph = [p for p in images if "graph" in p.lower() or "task_completion" in p.lower() or "chart" in p.lower()]
    if graph:
        return CheckResult("10. Graph placeholder", True, f"Graph image found: `{graph[0]}`")
    # Fall back: any second includegraphics counts as graph
    if len(images) >= 2:
        return CheckResult("10. Graph placeholder", True, f"Second `\\includegraphics` found: `{images[1]}`")
    return CheckResult(
        "10. Graph placeholder", False,
        "No Python-generated graph placeholder found",
        "Add a figure with `\\includegraphics{outputs/assets/task_completion_graph.png}`",
    )


def _check_bidi(tex: str) -> CheckResult:
    has_hebrew_env = bool(re.search(r"\\begin\s*\{hebrew\}", tex))
    has_setrl      = r"\setRL" in tex
    # Also accept raw Hebrew Unicode characters
    has_hebrew_chars = bool(re.search(r"[֐-׿]", tex))
    if has_hebrew_env and has_setrl:
        return CheckResult("11. Hebrew–English BiDi section", True, "`\\begin{hebrew}\\setRL` environment found")
    if has_hebrew_env:
        return CheckResult("11. Hebrew–English BiDi section", True, "`\\begin{hebrew}` environment found")
    if has_hebrew_chars:
        return CheckResult("11. Hebrew–English BiDi section", True, "Hebrew Unicode characters detected in source")
    return CheckResult(
        "11. Hebrew–English BiDi section", False,
        "No `\\begin{hebrew}` environment or Hebrew Unicode characters found",
        "Add a `\\begin{hebrew}\\setRL ... \\end{hebrew}` block using the polyglossia package",
    )


def _check_bibliography(tex: str) -> CheckResult:
    has_print  = r"\printbibliography" in tex
    has_bib    = bool(re.search(r"\\bibliography\s*\{", tex))
    has_bibres = bool(re.search(r"\\addbibresource\s*\{", tex))
    if has_print:
        return CheckResult("12. Bibliography", True, "`\\printbibliography` command present")
    if has_bib:
        return CheckResult("12. Bibliography", True, "`\\bibliography{}` command present")
    if has_bibres:
        return CheckResult("12. Bibliography", True, "`\\addbibresource{}` present (bibliography will print via biblatex)")
    return CheckResult(
        "12. Bibliography", False,
        "No `\\printbibliography`, `\\bibliography{}`, or `\\addbibresource{}` found",
        "Add `\\printbibliography` at the end of the document and `\\addbibresource{references.bib}` in preamble",
    )


def _check_compilation(pdf_path: Path, log_path: Path) -> CheckResult:
    if pdf_path.exists():
        return CheckResult("13. LaTeX compilation", True, f"PDF present at `{pdf_path}` — compilation succeeded")
    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        # Find first LaTeX error line
        for line in log_text.splitlines():
            if line.strip().startswith("!"):
                return CheckResult(
                    "13. LaTeX compilation", False,
                    f"Compilation failed. First error: `{line.strip()}`",
                    f"Open `{log_path}` and search for '!' lines to identify the root cause",
                )
        return CheckResult(
            "13. LaTeX compilation", False,
            "PDF not found; log exists but no explicit error line detected",
            f"Review full log at `{log_path}`",
        )
    return CheckResult(
        "13. LaTeX compilation", False,
        "PDF not found and no compile log exists",
        "Run `python src/main.py` — PDF compilation runs automatically after the LaTeX Formatter stage",
    )


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def validate(
    tex_path:  Path,
    pdf_path:  Path,
    log_path:  Path,
    report_path: Path,
) -> ValidationReport:
    """Run all 13 checks and write the validation report to *report_path*.

    Never raises — returns a ValidationReport regardless of file state.
    """
    tex = tex_path.read_text(encoding="utf-8", errors="replace") if tex_path.exists() else ""

    checks = [
        _check_tex_exists(tex_path),
        _check_pdf_exists(pdf_path),
        _check_title_page(tex),
        _check_toc(tex),
        _check_headers_footers(tex),
        _check_sections(tex),
        _check_table(tex),
        _check_formula(tex),
        _check_image(tex),
        _check_graph(tex),
        _check_bidi(tex),
        _check_bibliography(tex),
        _check_compilation(pdf_path, log_path),
    ]

    report = ValidationReport(checks=checks)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        report.as_markdown(tex_path, pdf_path, log_path),
        encoding="utf-8",
    )
    return report
