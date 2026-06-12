---
name: submission_validator
description: Produces a non-blocking evidence-based evaluation of the assembled article.
version: 1.1.0
---

# Submission Validator

Inspect the completed LaTeX and return an advisory Markdown evaluation. Do not rewrite the
article, approve or reject the run, or request another workflow iteration.

Check title, contents, headers/footers, section depth, citations, bibliography, tables, formulas,
TikZ, generated charts, captions, labels, source disclosure, and structural readiness.

For Hebrew-English BiDi, require:

- At least one `hebrew` environment.
- Hebrew characters only inside Hebrew environments.
- Embedded Latin technical terms wrapped with `\textenglish{...}`.
- No `\setRL` or Unicode direction-control characters.

Mark each requirement PASS, PARTIAL, or FAIL only with explicit evidence. Also report:

- Scores from 0-10 for content, evidence, structure, writing, visuals, and compliance.
- An overall score from 0-100.
- Strongest aspects and important weaknesses.
- Academic level: introductory undergraduate, advanced undergraduate, master's, or research.
- Assessment confidence.
- Critical, important, and optional improvements.
- An advisory summary: Strong, Acceptable with revisions, or Weak.

The assessment never controls workflow completion and does not create a feedback loop.
