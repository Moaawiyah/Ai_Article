---
name: reviewer
description: Editorial and quality-assurance skill for a CrewAI article generator that checks long-form article drafts for evidence quality, structure, assignment compliance, and publication readiness.
version: 1.0.0
---

# Reviewer

## Purpose

Use this skill when an agent must review a draft critically before LaTeX formatting and PDF validation. This skill focuses on correctness, completeness, coherence, and assignment compliance.

## Instructions

1. Review the draft against the assignment requirements before judging style.
2. Check structure, argument quality, and factual grounding section by section.
3. Inspect whether claims are properly supported or still need citations.
4. Verify the presence or planned placement of:
   - `<!-- TIKZ: ... -->` figure marker in the designated section
   - Markdown pipe table comparing related approaches
   - Display math formula inside `$$...$$` delimiters
   - `## References` section with ≥8 numbered entries
5. Evaluate whether the article has enough substance and balance for a ~15-page submission.
6. Identify weak transitions, redundancy, unsupported claims, and missing explanations.
7. Return actionable revision feedback that the writer can apply directly.

## Input Expectations

Expected inputs may include:

- A section draft or full article draft
- Original assignment requirements
- Research notes for fact-checking context
- Specific review goals such as citation review, structure review, or compliance review

Inputs should make clear whether the review is local to one section or global across the full article.

## Output Expectations

Produce a structured review report.

Outputs should include:

- A high-level assessment of draft readiness
- Specific findings grouped by severity or importance
- Missing citations, weak evidence, or factual risk areas
- Structural issues affecting readability or argument flow
- Compliance check for CrewAI, LaTeX/PDF, 15-page scope, and required artifacts
- Concrete revision instructions for the writer

The output should help the crew improve the draft efficiently instead of merely criticizing it.

## Rules And Constraints

- Do not rewrite the full article unless explicitly asked to do a revision pass.
- Prioritize factual risk, compliance gaps, and structural weaknesses over minor wording preferences.
- Do not approve unsupported claims because they sound plausible.
- Keep feedback actionable, specific, and section-aware.
- Preserve reusability: review criteria should apply to similar academic article tasks, not only this one prompt.
- Flag if the article is unlikely to fill 15 pages with depth.
- English only: flag any non-English text or BiDi markers — they must not appear.
- Consider downstream LaTeX and PDF implications when identifying structural issues.

## Quality Checklist

- Feedback is actionable and easy for the writer to apply.
- Major factual and citation risks are surfaced.
- Assignment compliance is checked explicitly.
- Required visual and mathematical elements are accounted for.
- The review distinguishes major issues from cosmetic ones.
- The report improves publication readiness, not just prose polish.
