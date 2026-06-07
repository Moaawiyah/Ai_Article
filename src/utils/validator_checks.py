"""Structural checks 1–8 for the programmatic LaTeX validator."""

from __future__ import annotations

import re
from pathlib import Path

from utils.validator_types import CheckResult


def check_tex_exists(tex_path: Path) -> CheckResult:
    if tex_path.exists():
        return CheckResult("1. article.tex exists", True, f"Found at `{tex_path}` ({tex_path.stat().st_size:,} bytes)")
    return CheckResult("1. article.tex exists", False, f"Not found at `{tex_path}`",
                       "Re-run the LaTeX Formatter agent to generate article.tex")


def check_pdf_exists(pdf_path: Path) -> CheckResult:
    if pdf_path.exists():
        return CheckResult("2. article.pdf exists", True, f"Found at `{pdf_path}` ({pdf_path.stat().st_size:,} bytes)")
    return CheckResult("2. article.pdf exists", False, f"Not found at `{pdf_path}`",
                       "Check logs/latex_compile.log — compilation may have failed")


def check_title_page(tex: str) -> CheckResult:
    has_title = bool(re.search(r"\\title\s*\{", tex))
    has_make  = r"\maketitle" in tex
    if has_title and has_make:
        m = re.search(r"\\title\s*\{([^}]{0,60})", tex)
        found = m.group(1).strip() if m else "found"
        return CheckResult("3. Title page", True, f'`\\title{{}}` and `\\maketitle` present — "{found}..."')
    missing = ["`\\title{}`"] * (not has_title) + ["`\\maketitle`"] * (not has_make)
    return CheckResult("3. Title page", False, f"Missing: {', '.join(missing)}",
                       "Add `\\title{...}\\author{...}\\date{...}` before `\\begin{document}`")


def check_toc(tex: str) -> CheckResult:
    if r"\tableofcontents" in tex:
        return CheckResult("4. Table of contents", True, "`\\tableofcontents` command present")
    return CheckResult("4. Table of contents", False, "`\\tableofcontents` not found",
                       "Add `\\tableofcontents\\newpage` after `\\maketitle`")


def check_headers_footers(tex: str) -> CheckResult:
    has_fancy = r"\pagestyle{fancy}" in tex or r"\usepackage{fancyhdr}" in tex
    has_head  = bool(re.search(r"\\fancyhead", tex))
    has_foot  = bool(re.search(r"\\fancyfoot", tex))
    if has_fancy and (has_head or has_foot):
        return CheckResult("5. Headers/footers", True, "`fancyhdr` loaded with `\\fancyhead`/`\\fancyfoot` definitions")
    missing = (["`fancyhdr`"] * (not has_fancy) + ["`\\fancyhead`"] * (not has_head)
               + ["`\\fancyfoot`"] * (not has_foot))
    return CheckResult("5. Headers/footers", False, f"Missing: {', '.join(missing)}",
                       "Add fancyhdr setup after `\\begin{document}`")


def check_sections(tex: str) -> CheckResult:
    sections = re.findall(r"\\section\s*\{([^}]{0,50})", tex)
    if sections:
        preview = ", ".join(f'"{s.strip()}"' for s in sections[:4])
        return CheckResult("6. Sections/chapters", True,
                           f"{len(sections)} section(s): {preview}{'…' if len(sections) > 4 else ''}")
    return CheckResult("6. Sections/chapters", False, "No `\\section{}` commands found",
                       "Ensure `##` Markdown headings were converted to `\\section{}`")


def check_table(tex: str) -> CheckResult:
    n = len(re.findall(r"\\begin\s*\{tabular\}", tex))
    if n:
        return CheckResult("7. Table", True, f"{n} `tabular` environment(s) found")
    return CheckResult("7. Table", False, "No `\\begin{tabular}` found",
                       "Ensure Markdown pipe tables were converted to booktabs environments")


def check_formula(tex: str) -> CheckResult:
    eq  = len(re.findall(r"\\begin\s*\{equation\}", tex))
    aln = len(re.findall(r"\\begin\s*\{align\}", tex))
    inl = len(re.findall(r"(?<!\$)\$(?!\$)[^$]+\$(?!\$)", tex))
    if eq + aln:
        return CheckResult("8. Mathematical formula", True, f"{eq} `equation` + {aln} `align` environment(s)")
    if inl:
        return CheckResult("8. Mathematical formula", True, f"{inl} inline `$...$` expression(s) found")
    return CheckResult("8. Mathematical formula", False, "No equation, align, or inline math found",
                       "Add `\\begin{equation}...\\end{equation}`")
