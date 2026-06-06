# Architecture & Planning Document — agent_ai_HW2

## 1. Architecture Overview (C4 — Container Level)

```
External Consumer (CLI / third-party)
          │
          ▼
  ┌─────────────┐       ┌─────────────────────┐
  │  AgentAISDK │       │    CrewPipeline      │  ← Article generation entry point
  └──────┬──────┘       └──────────┬──────────┘
         │                         │
    ┌────┴────┐            ┌───────┴────────┐
    │ Services│            │   crew/        │  ← Researcher, Writer, Reviewer agents
    └────┬────┘            └───────┬────────┘
         │                         │
  ┌──────┴──────────────────────────────────────┐
  │ Infrastructure Layer                         │
  │  ApiGatekeeper      ← Rate limiting, retry  │
  │  ConfigManager      ← JSON config loader    │
  │  markitdown (ext)   ← Document conversion  │
  │  anthropic SDK(ext) ← Document Q&A LLM     │
  │  Ollama (local)     ← Article generation   │
  │  crewai (ext)       ← Agent orchestration  │
  └──────────────────────────────────────────────┘
         │
  ┌──────┴──────────────────────┐
  │ Output Layer                │
  │  visuals/GraphGenerator     │  ← matplotlib PNG
  │  latex/MarkdownToLatexBuilder│ ← .tex + .bib
  │  latex/LatexCompiler        │  ← PDF via lualatex
  └──────────────────────────────┘
```

## 2. Key Architectural Decisions (ADRs)

### ADR-001 — SDK as single entry point
**Decision:** All business logic is exposed exclusively via `AgentAISDK`.  
**Rationale:** Prevents leakage of internal modules to consumers; enables future swap of LLM provider without breaking callers.  
**Trade-offs:** Slightly more boilerplate in the SDK class.

### ADR-002 — ApiGatekeeper for all external API calls
**Decision:** Every `anthropic` call is wrapped in `ApiGatekeeper.execute()`.  
**Rationale:** Centralised rate-limit enforcement; retries and logging in one place.  
**Trade-offs:** Adds latency on first call (lock acquisition).

### ADR-003 — uv as sole package manager
**Decision:** `uv` replaces `pip`/`venv`.  
**Rationale:** Required by course guidelines; reproducible lock files.

### ADR-004 — Ollama local LLM for CrewAI pipeline
**Decision:** CrewAI agents use `qwen3:14b` via local Ollama (`http://localhost:11434`), not the Anthropic cloud API.  
**Rationale:** User preference; no API cost; privacy; works offline.  
**Trade-offs:** Requires local GPU/CPU resources; slower than cloud API; no billing meter needed.

### ADR-005 — Three-agent sequential CrewAI crew
**Decision:** Researcher → Writer → Reviewer with `Process.sequential`.  
**Rationale:** Clear data dependency chain; each agent's output is the next agent's context; simple to debug.  
**Trade-offs:** No parallelism; total latency is sum of all three agents.

## 3. Data Flow

```
file_path ──▶ process_document() ──▶ markitdown ──▶ markdown_text
                                                          │
question ──────────────────────────────────────────────▶ query_document()
                                                          │
                                              ApiGatekeeper.execute()
                                                          │
                                              anthropic.messages.create()
                                                          │
                                                        answer
```

## 4. Directory Layout

```
agent_ai_HW2/
├── src/agent_ai/
│   ├── __init__.py
│   ├── constants.py
│   ├── sdk/sdk.py              # Public SDK (document Q&A)
│   ├── services/
│   │   ├── document_service.py # DocumentService
│   │   └── query_service.py    # QueryService
│   ├── crew/
│   │   ├── _llm.py             # Ollama LLM factory (qwen3:14b)
│   │   ├── agents.py           # Researcher, Writer, Reviewer
│   │   ├── tasks.py            # Research, Write, Review tasks
│   │   ├── pipeline.py         # CrewPipeline orchestrator
│   │   └── run.py              # CLI entry point
│   ├── latex/
│   │   ├── builder.py          # Markdown → .tex + .bib
│   │   ├── compiler.py         # lualatex × 3 + biber × 1 → PDF
│   │   └── templates/
│   │       └── article.tex.j2  # Jinja2 LaTeX template (Hebrew/English)
│   ├── visuals/
│   │   └── graph.py            # GraphGenerator → agents_growth.png
│   └── shared/
│       ├── config.py           # ConfigManager
│       ├── gatekeeper.py       # ApiGatekeeper
│       └── version.py          # Version tracking
├── tests/
│   ├── conftest.py
│   ├── unit/                   # per-module unit tests
│   └── integration/            # end-to-end mocked tests
├── docs/                       # PRD, PLAN, TODO
├── config/
│   ├── setup.json
│   ├── rate_limits.json
│   ├── logging_config.json
│   └── article.json            # article metadata
├── .sixth/skills/              # project-level Claude Code skills
├── data/                       # Input documents
├── results/article/            # generated .md, .tex, .bib, .pdf
├── notebooks/
└── assets/                     # images for article
```

## 5. API Contracts

### `AgentAISDK.process_document(file_path)`
- **Input:** `str | Path` — path to supported document
- **Output:** `str` — Markdown content
- **Raises:** `FileNotFoundError`

### `AgentAISDK.query_document(markdown_text, question)`
- **Input:** `str`, `str`
- **Output:** `str` — Claude's answer
- **Raises:** `RuntimeError` after max retries exhausted

### `CrewPipeline.run(output_dir)`
- **Input:** `Path` (default `results/article`)
- **Output:** `Path` — path to the reviewed `article.md`
- **Side effects:** writes `article.md`, `agents_growth.png`, `article.tex`, `body.tex`, `article.bib`, `article.pdf` under `output_dir`

### `GraphGenerator.generate(output_dir)`
- **Input:** `Path`
- **Output:** `Path` — path to `agents_growth.png`

### `MarkdownToLatexBuilder.build(markdown_path, metadata, assets_dir, output_dir)`
- **Input:** `Path`, `dict`, `Path`, `Path`
- **Output:** `tuple[Path, Path]` — `(article.tex, article.bib)`

### `LatexCompiler.compile(tex_path)`
- **Input:** `Path` — path to main `.tex` file
- **Output:** `Path` — path to compiled `.pdf`
- **Raises:** `RuntimeError` if any lualatex/biber pass fails
