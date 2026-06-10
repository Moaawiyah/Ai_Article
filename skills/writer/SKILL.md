---
name: writer
description: Generic long-form academic writing skill — writes any article following the structure proposed by the Researcher Agent, embedding required artifacts in their designated sections.
version: 4.0.0
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
6. Use the Researcher's research notes as grounding — expand claims into full explanations
   with definitions, mechanisms, examples, and trade-offs.
7. Every major claim must carry an inline citation marker `[N]` matching the Researcher's
   bibliography. **Aim for at least one `[N]` citation per paragraph** — every claim must be
   traceable to the references list.
8. Do not fabricate statistics or empirical results — mark uncertain values `[UNCERTAIN]`.

---

## Document Structure

Produce the article in this order:

1. **Title block** — title, author placeholder, course placeholder, date placeholder
2. **Abstract** — one paragraph, 150–200 words, summarising motivation and key results
3. **Table of Contents** — list all section numbers and titles (all entries in English)
4. **Main sections** — all sections from the Researcher's proposed structure, in order
5. **Conclusion** — see BiDi requirement below
6. **References / Bibliography** — numbered `[1]...[N]` list from the Researcher's bibliography

---

## Conclusion Section (BiDi — REQUIRED)

The **Conclusion** is the section that demonstrates the Hebrew↔English BiDi capability.
Write it as a natural, mixed-language section — there is **no separate bilingual section**
and **no mention anywhere** that the section contains two languages.

Rules:
- Heading: `## Conclusion` — plain English, nothing else.
- Body: approximately 150–200 words of **Hebrew prose** interspersed with the standard
  English conclusion paragraphs. You may open in English and close in Hebrew, or alternate
  — whichever reads most naturally.
- English technical terms and acronyms (P4, SDN, ECMP, HULA, programmable data plane,
  fat-tree, load balancing, throughput, latency) stay in **Latin characters** naturally
  inline within the Hebrew text.
- Do NOT add any heading, label, comment, or aside that draws attention to the language
  mixing (e.g. no "Hebrew summary:", no "BiDi section", no "multilingual" anywhere).
- Do NOT translate the Hebrew prose to English elsewhere in the article.
- Do NOT use HTML, RTL markers, or direction attributes.

Example of how Hebrew naturally appears inside the Conclusion:
```
## Conclusion

This paper has demonstrated that HULA achieves significant improvements over ECMP
in both throughput and fairness across all tested topologies.

מערכת HULA מוכיחה כי ניתן להשיג איזון עומסים יעיל בסביבות data center מודרניות
באמצעות תכנות שכבת ה-data plane ב-P4. הגישה מאפשרת קבלת החלטות בזמן אמת
ללא תלות ב-CPU, ומביאה לשיפור משמעותי ב-throughput ו-latency.

Future work will explore extending HULA to heterogeneous hardware environments.
```

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
The formula must be substantive, not a trivial one-line placeholder. Prefer a multi-line
expression using `\begin{aligned}...\end{aligned}` inside the `$$...$$` block, combining
the core mapping rule with at least one derived quantity, constraint, or objective.
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
End the article with a `## References` section listing entries from the Researcher's
bibliography in numbered format. Include **8 to 15 entries maximum** — choose the most
cited and most relevant ones:
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
- [ ] `$$...$$` formula is present in the designated section and is mathematically substantive, not a one-line placeholder
- [ ] Markdown comparison table covers main topic + Comparative Architecture A + B
- [ ] References section present with 8–15 numbered entries (no more than 15)
- [ ] Inline citations `[N]` appear throughout — at least one per paragraph in every section
- [ ] Conclusion section contains ~150–200 words of Hebrew prose naturally interspersed with English
- [ ] No label or comment indicates that the section is bilingual — the heading is just "Conclusion"
- [ ] Academic English throughout — no filler, no padding, no informal language

---

## Rules

- Follow the Researcher's section structure exactly — do not add, remove, or reorder sections.
  The Conclusion section (already in the structure) is where the Hebrew text appears.
- Do not call any tools. Do not generate images. Do not include external image syntax.
- Do not repeat content across sections; each section adds new information.
- Prefer depth over length: definitions, mechanisms, examples, and trade-offs in every section.
