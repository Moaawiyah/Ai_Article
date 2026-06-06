"""PDF validation task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig

_DESCRIPTION = """
You are the final validator for the article pipeline. The LaTeX Formatter has
produced article.tex (its content is in your context). Review it and produce
a structured validation report.

---

## Your job: check all 13 requirements

For EACH item below, write one block using this exact format:

### <N>. <Requirement name>
**Status:** PASS  or  FAIL
**Evidence:** <what you found in the tex content, or what is missing>
**Fix:** <concrete fix, only when status is FAIL>

---

## The 13 requirements to check:

**1. article.tex exists**
Confirm you received non-empty LaTeX content in context.
Evidence: note approximate length and presence of the documentclass command.

**2. article.pdf (compilation)**
Check whether the .tex is free of obvious LaTeX errors that would block compilation:
- unclosed \\begin without matching \\end
- undefined commands used without \\newcommand
- missing \\end document at the end
Evidence: report any structural issues found, or state "no obvious blockers".

**3. Title page**
Look for \\title command, \\author command, \\date command, and \\maketitle.
Evidence: quote the title text if found.

**4. Table of contents**
Look for \\tableofcontents.

**5. Headers and footers**
Look for \\usepackage fancyhdr, \\pagestyle fancy, \\fancyhead, \\fancyfoot.

**6. Sections/chapters**
Count \\section occurrences. List the first 4 section titles.
PASS requires at least 5 sections.

**7. Table**
Look for \\begin tabular. Count occurrences.

**8. Mathematical formula**
Look for \\begin equation, \\begin align, or inline math delimited by dollar signs.

**9. Image placeholder**
Look for \\includegraphics pointing to an architecture or diagram image.
Evidence: quote the filename.

**10. Python-generated graph placeholder**
Look for \\includegraphics pointing to a graph or chart image such as task_completion_graph.png.
Evidence: quote the filename.

**11. Hebrew-English BiDi section**
Look for \\begin hebrew, \\setRL, or Hebrew Unicode characters (Unicode range U+0590 to U+05FF).
Evidence: quote the first Hebrew line if found.

**12. Bibliography**
Look for \\printbibliography, \\bibliography command, or \\addbibresource command.

**13. LaTeX compilation readiness**
Scan for common fatal errors:
- unmatched \\begin and \\end pairs
- \\end document present at the very end
- no obvious undefined commands
Evidence: state "structurally valid" or list specific issues.

---

## Summary section (write this at the end)

After all 13 blocks, write:

---
## Summary
**Passed:** X/13
**Failed:** Y/13
**Blocking issues:** (list any FAILs that prevent compilation or submission)
**Ready for submission:** YES  or  NO
""".strip()

_EXPECTED_OUTPUT = (
    "A Markdown validation report with 13 numbered PASS/FAIL blocks (each with evidence "
    "and a fix when failed), followed by a summary section showing pass count, failed count, "
    "blocking issues, and a final YES/NO submission readiness verdict."
)


def build_validation_task(agent: Agent, config: AppConfig | PipelineConfig, latex_task: Task) -> Task:
    """Create the PDF validation task."""
    out = config.output_pdf if hasattr(config, "output_pdf") else config.output_root / "pdf"
    return Task(
        description=_DESCRIPTION,
        expected_output=_EXPECTED_OUTPUT,
        agent=agent,
        context=[latex_task],
        output_file=str(out / "agent_validation.md"),
    )
