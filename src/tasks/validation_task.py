"""PDF validation task factory."""

from crewai import Agent, Task

from shared.config import AppConfig, PipelineConfig

_DESCRIPTION = """
You are the final validator for the article pipeline. The LaTeX Formatter has
produced article.tex. Review its content (provided in context) and produce
a structured PASS/FAIL validation report covering all 13 requirements.

For EACH requirement write one block in exactly this format:
  ### N. Requirement name
  **Status:** PASS or FAIL
  **Evidence:** what you found, or what is missing
  **Fix:** concrete fix (only when FAIL)

---

The 13 requirements:

1. article.tex exists — confirm you received non-empty LaTeX content with a documentclass command.

2. Compilation readiness — check for unclosed environments and a missing end-document at the last line.

3. Title page — look for title, author, date, and maketitle commands.

4. Table of contents — look for tableofcontents command.

5. Headers and footers — look for usepackage fancyhdr, pagestyle fancy, fancyhead, fancyfoot.

6. Sections — count section commands; PASS requires at least 5.

7. Table — look for a begin-tabular environment.

8. Mathematical formula — look for begin-equation, begin-align, or inline dollar-sign math.

9. TikZ figure — look for a begin-tikzpicture environment inside a figure. FAIL if absent.

10. Inline citations — look for cite commands throughout the body. PASS requires at least 3.

11. English only — confirm no begin-hebrew, no setRL, no polyglossia, no Hebrew Unicode characters.
    PASS if none of these are found.

12. Bibliography — look for begin-thebibliography with 8 or more bibitem entries.

13. LaTeX compilation readiness — check for unmatched begin/end pairs and end-document as the last line.

---

After all 13 blocks write:

---
## Summary
**Passed:** X/13
**Failed:** Y/13
**Blocking issues:** list any FAILs that prevent compilation or submission
**Ready for submission:** YES or NO
""".strip()

_EXPECTED_OUTPUT = (
    "A Markdown validation report with 13 numbered PASS/FAIL blocks (each with evidence "
    "and a fix when failed), followed by a Summary section with pass count, fail count, "
    "blocking issues, and a YES/NO submission readiness verdict."
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
