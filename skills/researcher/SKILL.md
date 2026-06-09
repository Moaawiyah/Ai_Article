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
- [ ] No article prose — only structured notes
- [ ] No invented citations or statistics
