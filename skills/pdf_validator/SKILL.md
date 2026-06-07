---
name: pdf_validator
description: Validates article.tex content against 13 assignment requirements, producing a structured PASS/FAIL report with evidence and fix suggestions for each item.
version: 2.1.0
---

# PDF Validator

## Purpose

Use this skill when an agent must validate the LaTeX source of an article against
a fixed checklist. The output is a structured, human-readable PASS/FAIL report.

This skill works by inspecting the LaTeX text received as context — no OCR, no
external tools, no over-engineering.

---

## Input

The LaTeX source (`article.tex`) received as context from the LaTeX Formatter agent.

---

## Output

A Markdown validation report with:
- One numbered block per requirement (PASS or FAIL)
- Evidence quote for each block
- A concrete fix suggestion for every FAIL
- A final summary: pass count, fail count, blocking issues, submission readiness

---

## The 13 requirements

| # | Requirement | What to look for in the .tex |
|---|---|---|
| 1 | article.tex exists | Non-empty content, documentclass command present |
| 2 | Compilation readiness | No unclosed environments, `\end` document present |
| 3 | Title page | `\title`, `\author`, `\date`, `\maketitle` commands |
| 4 | Table of contents | `\tableofcontents` command |
| 5 | Headers and footers | fancyhdr package, `\fancyhead`, `\fancyfoot` commands |
| 6 | Sections/chapters | 5 or more `\section` commands |
| 7 | Table | `\begin` tabular environment |
| 8 | Mathematical formula | `\begin` equation or align environment, or inline math |
| 9 | TikZ figure | `\begin{tikzpicture}` environment present inside a figure |
| 10 | Inline citations | `\cite{refN}` commands appear throughout the article |
| 11 | English only | No `\begin{hebrew}`, no `\setRL`, no polyglossia, no Hebrew Unicode (U+0590–U+05FF) |
| 12 | Bibliography | `\begin{thebibliography}` with ≥8 `\bibitem` entries |
| 13 | LaTeX compilation | No fatal structural errors, `\end` document present |

---

## Output format (use exactly this template for each check)

```
### <N>. <Requirement name>
**Status:** PASS  or  FAIL
**Evidence:** <what you found, or what is missing>
**Fix:** <concrete fix — only when FAIL>
```

End with:

```
---
## Summary
**Passed:** X/13
**Failed:** Y/13
**Blocking issues:** <list or "none">
**Ready for submission:** YES  or  NO
```

---

## Rules and constraints

- Do NOT rewrite or fix the article content.
- Do NOT mark a requirement PASS without explicit textual evidence.
- Do NOT skip any of the 13 checks — all must appear in the report.
- Quote specific LaTeX commands or filenames as evidence, not vague statements.
- A check is FAIL if the evidence is absent or structurally broken.
- Blocking issues are those that would prevent compilation or submission.

---

## Quality checklist for this skill

- [ ] All 13 blocks present in the output
- [ ] Each block has Status, Evidence, and Fix (when FAIL)
- [ ] Summary section is at the end
- [ ] Evidence quotes actual LaTeX text, not vague descriptions
- [ ] Fixes are actionable (specific command or package to add)
