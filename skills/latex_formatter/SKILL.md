---
name: latex_formatter
description: Publication-formatting skill for a CrewAI article generator that maps reviewed article content into a LaTeX structure suitable for compiling a polished academic PDF.
version: 1.0.0
---

# LaTeX Formatter

## Purpose

Use this skill when an agent must prepare article content for LaTeX-based PDF production. This skill focuses on document structure, artifact placement, citation readiness, and bilingual typesetting awareness.

## Instructions

1. Start from the reviewed article draft, not from raw notes.
2. Convert the document into a LaTeX-friendly structure with clean section hierarchy.
3. Ensure the article layout supports the expected deliverables:
   - title and cover information
   - table of contents
   - section hierarchy
   - bibliography references
   - image placement
   - graph placement
   - table placement
   - formula placement
   - Hebrew-English bidirectional section support
4. Normalize headings, lists, captions, references, and cross-references.
5. Mark ambiguous content that may break typesetting, especially around mixed Hebrew-English text.
6. Preserve semantic intent so the PDF validator can inspect the output against the assignment.

## Input Expectations

Expected inputs may include:

- A reviewed Markdown or text draft
- Citation placeholders or bibliography entries
- References to figures, graphs, tables, and formulas
- Constraints for LaTeX engine behavior or bilingual formatting

Inputs should be sufficiently mature that formatting can focus on structure rather than major content invention.

## Output Expectations

Produce a formatting-ready LaTeX representation or formatting plan.

Outputs should include:

- A clean document structure with ordered sections
- Explicit placement points for image, graph, table, and formula
- Citation and bibliography mapping guidance
- Notes for handling Hebrew-English BiDi content safely
- Warnings about content that may fail or degrade in LaTeX/PDF form

The output should be easy for a compilation stage to consume.

## Rules And Constraints

- Do not invent missing article content to patch structural gaps.
- Do not drop citations, captions, or section semantics during conversion.
- Preserve meaning when normalizing markup.
- Keep the skill reusable across article topics that require LaTeX PDF output.
- Treat BiDi handling as a first-class concern, especially for Hebrew mixed with English and formulas.
- Anticipate long-form academic layout needs rather than single-page formatting.
- Focus on formatting intent and structure, not on executing compilation.

## Quality Checklist

- Section hierarchy is complete and coherent.
- Required article artifacts have explicit placement.
- Citation flow is preserved for bibliography generation.
- The document is suitable for a polished academic PDF.
- BiDi-sensitive content has handling notes or safeguards.
- The structure supports a full ~15-page article cleanly.
