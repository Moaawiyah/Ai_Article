---
name: pdf_validator
description: Final-output validation skill for a CrewAI article generator that checks whether a compiled article PDF satisfies academic, formatting, and assignment-level requirements.
version: 1.0.0
---

# PDF Validator

## Purpose

Use this skill when an agent must validate the final compiled PDF or its expected characteristics before submission. This skill checks the finished deliverable against content, formatting, and completeness requirements.

## Instructions

1. Validate the output against the assignment checklist, not only against visual appearance.
2. Confirm the PDF represents a complete academic article rather than a partial export.
3. Check for the required deliverables:
   - approximately 15 pages of meaningful content
   - citations and bibliography
   - at least one image
   - at least one graph
   - at least one table
   - at least one formula
   - a Hebrew-English bidirectional section
   - evidence of CrewAI team-design discussion in the article content
4. Inspect structural quality:
   - readable headings
   - stable pagination
   - visible captions
   - non-broken references
   - no obviously corrupted BiDi layout
5. Report blocking defects separately from minor polish issues.
6. Provide a pass/fail-style conclusion with targeted remediation guidance.

## Input Expectations

Expected inputs may include:

- A compiled PDF or a detailed PDF export summary
- The reviewed article specification
- Assignment requirements and acceptance criteria
- Known issues from LaTeX formatting or compilation stages

Inputs should provide enough information to assess final deliverable quality, even if validation is partially manual.

## Output Expectations

Produce a validation report for submission readiness.

Outputs should include:

- Overall validation status
- Requirement-by-requirement compliance check
- Blocking issues that prevent submission
- Non-blocking issues that reduce quality
- Recommended fixes ordered by impact

The output should make it obvious whether the article is ready to submit.

## Rules And Constraints

- Do not rewrite article content during validation.
- Do not mark a requirement as satisfied without explicit evidence.
- Distinguish clearly between content defects, formatting defects, and evidence gaps.
- Keep the validation reusable for other academic PDF generation workflows.
- Be strict about assignment artifacts and page-depth expectations.
- Treat broken BiDi rendering, missing bibliography, or absent required visuals as major issues.
- Focus on validation logic and reporting, not on running compilation tools.

## Quality Checklist

- Every assignment requirement is checked explicitly.
- Blocking issues are separated from minor polish findings.
- The report is concrete enough for the crew to act on.
- Visual, citation, formula, and BiDi requirements are all covered.
- The result reflects final-deliverable quality, not draft quality.
