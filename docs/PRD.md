# Product Requirements Document — agent_ai_HW2

## 1. Project Overview

**Name:** agent_ai_HW2 — Document Processing Pipeline with LLM Agents  
**Version:** 1.00  
**Author:** moaawiyahhaj  

### Problem Statement
Users need to extract insights from heterogeneous document formats (PDF, DOCX, PPTX, etc.) without writing bespoke parsing code. An LLM-powered agent should accept a document and a natural-language question and return a structured answer.

### Target Audience
Students and researchers who need automated document Q&A as part of an AI-agents coursework submission.

---

## 2. Goals and Success Metrics

| KPI | Target |
|-----|--------|
| Acceptance criteria coverage | 100 % of functional requirements |
| Test coverage | ≥ 85 % |
| Ruff lint violations | 0 |
| Supported document formats | ≥ 5 |

---

## 3. Functional Requirements

### F-01 — Document Conversion
- System converts any supported file to Markdown via `markitdown`.
- Supported formats: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.txt`, `.md`.

### F-02 — LLM Query
- SDK sends converted Markdown + user question to Claude via `anthropic` SDK.
- Response is returned as a plain string.

### F-03 — Rate Limiting
- All API calls pass through `ApiGatekeeper`.
- Rate limits are read from `config/rate_limits.json` (never hard-coded).

### F-04 — CLI Entry Point
- `agent-ai <file> <question>` prints the answer to stdout.

### F-05 — CrewAI Article Generation
- A three-agent CrewAI crew (Researcher → Writer → Reviewer) generates a ~15-page bilingual academic article on "Mass Production of AI Agents: From PoC to Production".
- Agents run sequentially via `Process.sequential`.
- Output: a complete Markdown document saved to `results/article/article.md`.

### F-06 — Graph Generation
- A `GraphGenerator` produces a matplotlib bar chart (AI framework adoption 2022–2025) saved as `results/article/agents_growth.png`.
- Chart is embedded in the final article.

### F-07 — LaTeX Compilation
- A `MarkdownToLatexBuilder` converts the reviewed Markdown into `article.tex`, `body.tex`, and `article.bib`.
- A `LatexCompiler` runs 4 compilation passes (lualatex × 3 + biber × 1) to produce `results/article/article.pdf`.
- The PDF must include: cover sheet, table of contents, headers/footers, ≥1 image, ≥1 Python graph, ≥1 table, ≥1 mathematical formula, English-Hebrew bidirectional text, bibliography.

### F-08 — Ollama Local LLM
- The CrewAI pipeline uses a local Ollama model (`qwen3:14b`) via `crewai.LLM`.
- No cloud API key is required for article generation.
- Prerequisite: `ollama serve` running on `http://localhost:11434` with `qwen3:14b` pulled.

---

## 4. Non-Functional Requirements
- Security: API key loaded only from environment variable `ANTHROPIC_API_KEY` (used only for document Q&A; article generation uses Ollama).
- Performance: single document query completes in < 30 s under normal network conditions; full article generation completes in < 30 min on a local GPU-accelerated Ollama instance.
- Maintainability: all source files ≤ 150 lines of code.

---

## 5. Assumptions and Constraints
- Requires Python ≥ 3.10.
- `uv` is the sole package manager.
- No GUI; CLI and programmatic SDK only.
- Out of scope: batch processing of hundreds of documents in a single call.

---

## 5. Assumptions and Constraints
- Requires Python ≥ 3.10.
- `uv` is the sole package manager.
- No GUI; CLI and programmatic SDK only.
- Out of scope: batch processing of hundreds of documents in a single call.

---

## 6. Timeline and Milestones

| Phase | Milestone | Status |
|-------|-----------|--------|
| 0 | Documentation update (PRD, PLAN, TODO) | 🔄 |
| 0.5 | Project skills (`.sixth/skills/`) | ⬜ |
| 1 | Core SDK scaffold (existing) | ✅ |
| 2 | Services implementation | ⬜ |
| 3 | Visuals + LaTeX layer | ⬜ |
| 4 | CrewAI pipeline | ⬜ |
| 5 | Tests ≥ 85 % coverage + ruff 0 violations | ⬜ |
| 6 | Full end-to-end PDF generation | ⬜ |
