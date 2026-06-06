---
name: writer
description: Long-form academic writing skill for a CrewAI article generator that transforms researcher output into a structured 15-page article draft with citations and required assignment artifacts.
version: 1.0.0
---

# Writer

## Purpose

Use this skill when an agent must draft or revise article sections using the Researcher Agent output as context. The goal is a coherent, citation-ready academic article on multi-agent collaboration systems designed for final LaTeX and PDF production.

## Instructions

1. Start from the article thesis, outline, and current section objective.
2. Use the Researcher Agent output as grounding, not as loose inspiration.
3. Write with a consistent academic voice suitable for a course submission.
4. Build sections that progress logically from motivation to architecture, workflow, evidence, and implications.
5. Ensure the draft supports the assignment requirements:
   - CrewAI-based multi-agent framing
   - clear explanation of CrewAI team collaboration
   - enough substance for ~15 pages
   - citations throughout
   - one image reference
   - one graph reference
   - one table reference
   - one formula or mathematical expression
   - one Hebrew-English bidirectional section
6. Mark places where citations, figures, tables, or formulas belong if they are not yet embedded.
7. Preserve clarity across section boundaries so the reviewer can inspect claims efficiently.

## Input Expectations

Expected inputs may include:

- Article topic and thesis
- Section outline or subsection target
- Research notes from the researcher skill
- Researcher Agent output
- Reviewer revision requests
- Formatting expectations for later LaTeX conversion

Inputs should clearly state whether the task is drafting from scratch, expanding a section, or revising an existing draft.

## Output Expectations

Produce article prose that is ready for review and later formatting.

Outputs should include:

- Section text or full draft text
- Clear section headings and logical transitions
- Citation placeholders or citation-ready references tied to claims
- Explicit placeholders for image, graph, table, and formula when needed
- A clearly marked Hebrew-English BiDi subsection when requested
- Notes on weak areas that need stronger evidence or review

The output should be substantial enough to contribute meaningfully toward a 15-page final article.

## Rules And Constraints

- Do not fabricate citations, quotations, or empirical findings.
- Do not overstate certainty when the evidence is mixed.
- Do not optimize for stylistic flourish over precision.
- Avoid repetitive filler used only to reach page count.
- Keep sections reusable and modular so they can be revised independently.
- Write with downstream LaTeX conversion in mind; avoid structures that are hard to typeset cleanly.
- Ensure the BiDi section is intentional and readable, not a token inclusion.
- When evidence is missing, leave a visible gap marker instead of guessing.

## Quality Checklist

- The draft advances the article thesis clearly.
- Section flow is coherent and suitable for academic reading.
- Claims are grounded in provided research or marked for citation.
- The required artifacts are integrated or explicitly staged.
- The prose can scale to a full 15-page article without padding.
- The writing is compatible with later review and LaTeX formatting.
- The BiDi section is clearly planned and contextually justified.
