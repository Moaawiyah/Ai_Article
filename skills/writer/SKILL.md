---
name: writer
description: Generic long-form academic writing skill — writes any article following the structure proposed by the Researcher Agent, embedding required artifacts in their designated sections.
version: 3.0.0
---

# Writer

## Purpose

Write the complete academic article by expanding the section structure proposed by the
Researcher Agent into full academic prose. The section titles, order, and content grounding
all come from the Researcher output — do not impose a different structure.

---

## Process Rules

1. Read the Researcher output fully before writing any section.
2. Write sections in the order the Researcher proposed.
3. Each section must reach its minimum word target before moving on.
   If a section is short, add a subsection exploring implications, limitations, or a worked example.
4. Every section with more than one conceptual topic **must** have 2–5 `###` subsections.
   The following sections are **mandatory** for subsections — use these exact headings:
   - Architecture section: `### Hierarchical Topology`, `### Data-Plane Forwarding`
   - P4 Implementation section: `### Parser and Header Extraction`, `### Hash Computation`, `### Output Port Selection`
   - Evaluation section: `### Experimental Setup`, `### Convergence Time`, `### Throughput Analysis`, `### Load Fairness`, `### Control Plane Overhead`
   - Discussion section: `### P4 Complexity`, `### Hardware Dependencies`, `### Dynamic Reconfiguration`, `### Memory Constraints`
   - Related Work section: `### Traditional Load Balancing`, `### SDN-Based Approaches`, `### Programmable Data Planes`
5. The Researcher provides **Comparative Architecture A** and **Comparative Architecture B**.
   Within the existing Related Work subsections, cover both architectures in depth against the
   main topic (mechanism, strengths, weaknesses, one concrete differentiating metric each).
   The Markdown comparison table must include all three systems: main topic + A + B.
5. Use the Researcher's research notes as grounding — expand claims into full explanations
   with definitions, mechanisms, examples, and trade-offs.
6. Every major claim must carry an inline citation marker `[N]` matching the Researcher's bibliography.
7. Do not fabricate statistics or empirical results — mark uncertain values `[UNCERTAIN]`.

---

## Document Structure

Produce the article in this order:

1. **Title block** — title, author placeholder, course placeholder, date placeholder
2. **Abstract** — one paragraph, 150–200 words, summarising motivation and key results
3. **Table of Contents** — list all section numbers and titles
4. **Main sections** — all sections from the Researcher's proposed structure, in order
5. **References / Bibliography** — numbered `[1]...[N]` list from the Researcher's bibliography

---

## Artifact Format Rules

The task specifies required artifacts and which sections they belong to (from the Researcher's
artifact map). Use exactly these formats:

### TikZ Figure
Write this exact comment syntax in the designated section:
```
<!-- TIKZ: <description of what the figure should show> -->
```
The description should be taken from the Researcher's artifact map.
Do NOT generate image files. Do NOT use Markdown image syntax. Use only this marker.

### Display Formula
Write the mathematical formula using `$$` delimiters:
```
$$<LaTeX expression>$$
```
Follow the formula with a sentence explaining each variable.
The formula content comes from the Researcher's artifact map.

### Markdown Table
Write a pipe-formatted table in the designated section:
```
| Column A | Column B | Column C |
|----------|----------|----------|
| value    | value    | value    |
```
The table caption and data come from the Researcher's artifact map.

### Bibliography
End the article with a `## References` section listing every entry from
the Researcher's bibliography in numbered format:
```
[1] Author(s), "Title," *Venue*, Year.
```
Use these same numbers as inline citation markers `[N]` throughout the article.

---

## Quality Checklist

Before finishing, verify:
- [ ] All sections from the Researcher's proposed structure are present
- [ ] Total word count (body only, excluding title block and references) meets the task target
- [ ] Each major section has ≥3 subsections (`###`) with substantive prose
- [ ] `<!-- TIKZ: ... -->` marker is present in the designated section
- [ ] `$$...$$` formula is present in the designated section
- [ ] Markdown comparison table covers main topic + Comparative Architecture A + B
- [ ] References section present with ≥8 numbered entries
- [ ] Inline citations `[N]` appear throughout — every major claim is cited
- [ ] Academic English throughout — no filler, no padding, no informal language
- [ ] No Hebrew, no BiDi markers, no external image syntax

---

## Rules

- Follow the Researcher's section structure exactly — do not add, remove, or reorder sections.
- Do not call any tools. Do not generate images. Do not include Hebrew.
- Do not repeat content across sections; each section adds new information.
- Prefer depth over length: definitions, mechanisms, examples, and trade-offs in every section.
