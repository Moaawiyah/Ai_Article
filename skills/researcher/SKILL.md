---
name: researcher
description: Generic academic research skill — researches any topic, proposes article structure, and produces citation-ready notes for downstream writing agents.
version: 3.0.0
---

# Researcher

## Purpose

Given a topic title and a list of required artifact types, research the topic thoroughly
and propose a logical article structure. The section titles and order are your decision —
choose what makes academic sense for this specific topic.

This skill does NOT write the article. It produces structured research notes
and a section proposal that the Writer Agent will use.

---

## Your Output Must Contain

### 1. Proposed Article Structure

A numbered list of sections you decide are appropriate for this topic. For each:
- Section number and title
- 1–2 sentence description of what that section should cover
- Approximate minimum word target (typically 300–500 words per section)

Example format:
```
1. Abstract (150 words) — one-paragraph summary of motivation, approach, and results
2. Introduction (450 words) — context, problem statement, paper outline
3. ...
```

### 2. Research Notes per Section

For each proposed section, provide:
- Key claims and definitions, bullet-pointed
- Inline citation markers: `[CITE: N]` referencing your bibliography list
- Mark uncertain or unverified claims with `[UNCERTAIN]`

### 3. Comparative Architecture Analysis

Identify **exactly 2 related architectures or systems** that are meaningfully comparable to
the main topic. For each one provide:
- Full name and the original paper/source
- Core mechanism (1–3 sentences)
- Key strengths and weaknesses vs. the main topic
- At least one concrete metric or design decision where they differ (e.g. convergence time,
  memory footprint, control-plane involvement, scalability ceiling)

Label these clearly so the Writer can build a side-by-side comparison:
```
Comparative Architecture A: <Name>
  - Mechanism: ...
  - Strengths: ...
  - Weaknesses: ...
  - Key difference from main topic: ...

Comparative Architecture B: <Name>
  - Mechanism: ...
  - Strengths: ...
  - Weaknesses: ...
  - Key difference from main topic: ...
```

### 4. Bibliography Candidates

Numbered list of real, verifiable references. Use this format:
```
[1] Author(s), "Title," Venue/Journal, Year.
[2] ...
```
Provide at least 8 entries. Do not invent references — only list papers or books
you are confident actually exist.

### 5. Artifact Map

For each required artifact type specified in the task, state:
- **In which section** the artifact belongs
- **What specifically** it should show or express

Example:
```
TikZ figure → Section 3 (Architecture): show the system topology with data flow arrows
Display formula → Section 5 (Analysis): the core mathematical update rule
Markdown table → Section 6 (Evaluation): comparison of related approaches on key metrics
Bibliography → Section N (References): numbered entries [1]...[N] from list above
```

### 6. Performance Data Block (machine-readable)

Emit the quantitative comparison used to plot the evaluation figure as a SINGLE fenced
`json` code block, exactly once, with exactly this shape. The downstream pipeline parses
this block directly, so the keys and structure must match precisely:

```json
{
  "main":   {"name": "<main architecture, max 15 chars>",
             "median_queue": <median bottleneck queue length in packets, integer 1-500>,
             "p95_queue":    <95th-percentile queue length, integer > median>,
             "base_fct_ms":  <average FCT in ms at low (0-20%) load, float>,
             "fct_slope":    <FCT increase in ms per 1% extra load, float 0.001-0.5>,
             "data_basis":   "measured" | "estimated",
             "source":       "<paper + figure/table, or basis for the estimate>"},
  "arch_a": {"name": "<Comparative Architecture A, max 15 chars>", "median_queue": ...,
             "p95_queue": ..., "base_fct_ms": ..., "fct_slope": ...,
             "data_basis": "measured" | "estimated", "source": "..."},
  "arch_b": {"name": "<Comparative Architecture B, max 15 chars>", "median_queue": ...,
             "p95_queue": ..., "base_fct_ms": ..., "fct_slope": ...,
             "data_basis": "measured" | "estimated", "source": "..."}
}
```

Rules for this block:
- `main`/`arch_a`/`arch_b` must be the same three systems as your Comparative Architecture
  Analysis (section 3), so the figure agrees with the prose.
- Set `data_basis` to `"measured"` ONLY when recalling actual numbers reported in a real
  paper, and name that paper + figure/table in `source` (e.g. `"HULA, SOSR'16, Fig. 8"`).
  Otherwise set `"estimated"` and describe the basis in `source`. Never invent a citation.
- Report the real measured ranking. Do NOT force the main topic to be the best on every metric.
- Make the three meaningfully different so the plotted curves are visually distinct.

---

## Rules

- Do NOT draft full article prose — research notes only.
- Do NOT invent citations, statistics, or empirical results.
- Mark every uncertain claim with `[UNCERTAIN]` rather than stating it as fact.
- Choose sections based on what this specific topic requires — do not copy a fixed template.
- The bibliography must contain only real works you are confident about.
- Output entirely in English. No Hebrew, no other languages.

---

## Quality Checklist

- [ ] Proposed structure has at least 8 sections with clear descriptions
- [ ] Every section has research notes with `[CITE: N]` markers
- [ ] Bibliography has ≥8 real references in correct format
- [ ] Comparative Architecture Analysis contains exactly 2 named architectures with mechanism, strengths, weaknesses, and key difference
- [ ] Artifact map accounts for every artifact type listed in the task
- [ ] Exactly one machine-readable `json` Performance Data block with main/arch_a/arch_b, each having data_basis + source
- [ ] No article prose — only structured notes
- [ ] No invented citations or statistics
