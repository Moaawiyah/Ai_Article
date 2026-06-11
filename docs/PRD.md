# Product Requirements Document - agent_ai_HW2

## 1. Overview

**Product:** Academic Article Generator and Document Q&A SDK
**Version:** 1.00  
**Audience:** Students and researchers producing a validated academic PDF or querying documents.

The project exposes one SDK for two workflows:

1. Convert a supported document to Markdown and ask an Anthropic-backed question.
2. Generate a researched academic article with a five-agent CrewAI pipeline, render a benchmark graph, compile LuaLaTeX, and validate the PDF.

## 2. Goals and KPIs

| KPI | Target |
|---|---:|
| Full `src/` statement and branch coverage | >= 85% |
| Ruff violations | 0 |
| Source/test file size | <= 150 code lines |
| PDF validation checks | 13/13 |
| Supported document formats | >= 5 |
| Un-gated external API calls | 0 |

## 3. Functional Requirements

### F-01 Document Conversion

- `AgentAISDK.process_document()` converts PDF, DOCX, PPTX, XLSX, HTML, TXT, and Markdown through MarkItDown.
- Missing input files produce a clear `FileNotFoundError`.

### F-02 Document Q&A

- `AgentAISDK.query_document()` sends Markdown and a question to Anthropic.
- `ANTHROPIC_API_KEY` is loaded only from the environment.
- The response is returned as plain text.

### F-03 Article Generation

- `AgentAISDK.generate_article()` is the public entry point.
- CrewAI runs Researcher, Writer, Reviewer, LaTeX Formatter, and PDF Validator tasks sequentially.
- Provider, model, endpoint, topic, output paths, and pricing come from `config/config.yaml`.
- The current default provider is ZhipuAI using `glm-4.7-flashx`; Ollama remains a supported configuration option.

### F-04 API Gatekeeper

- Anthropic, CrewAI kickoff, and fallback graph-spec LLM calls pass through `ApiGatekeeper`.
- The gatekeeper enforces configured minute/hour limits, concurrency, retries, and FIFO admission.
- Queue capacity and time-window durations come from `config/rate_limits.json`.
- A full queue applies blocking backpressure rather than dropping requests.

### F-05 Research and Graph Generation

- The researcher emits a structured comparison and graph-data JSON block.
- If that block is unavailable, the graph-spec service requests structured data through the configured LLM and gatekeeper.
- A deterministic fallback keeps graph generation operational when the LLM path fails.
- Matplotlib generates `outputs/latex/benchmark.png`, which is injected into the Evaluation section.

### F-06 LaTeX and PDF

- The formatter produces LuaLaTeX source with title, contents, sections, headers/footers, table, formula, TikZ, citations, bibliography, and Hebrew-English content.
- The compiler writes `outputs/pdf/article.pdf`.
- Programmatic validation writes `outputs/pdf/validation_report.md`.

### F-07 CLI

- `uv run agent-ai <file> "<question>"` runs document Q&A.
- `uv run agent-ai-article [--topic "..."]` generates the article.
- CLI modules contain argument parsing only and delegate to the SDK.

## 4. Non-Functional Requirements

- **Security:** no committed secrets; environment variables supply provider keys.
- **Quality:** Ruff must pass and full source coverage must remain at least 85%.
- **Maintainability:** modules are limited to 150 code lines and use focused responsibilities.
- **Reliability:** external calls are retried and queued; graph generation has a deterministic fallback.
- **Portability:** Python 3.12 and `uv` are the supported runtime and package workflow.
- **Observability:** stages, token usage, cost estimates, API results, and compilation status are logged.

## 5. Constraints and Scope

- A LuaLaTeX installation is required for PDF compilation.
- Cloud providers require the matching environment key; Ollama requires a running local server.
- The graph is a comparative visualization, not a substitute for independent experimental reproduction.
- GUI and high-volume batch processing are out of scope.

## 6. Acceptance Criteria

- `uv sync --extra dev` completes.
- `uv run ruff check src tests` reports no violations.
- `uv run pytest` passes with coverage measured across all `src/`, including branch coverage.
- No pipeline, task, agent, graph, or logging module is excluded from coverage.
- `outputs/pdf/article.pdf` exists and the validation report passes 13/13 checks.
- README, PLAN, TODO, dedicated mechanism PRDs, prompt log, license, and CI workflow are present.

## 7. Milestones

| Milestone | Status |
|---|---|
| Documentation and package scaffold | Done |
| SDK, configuration, and gatekeeper | Done |
| Five-agent article pipeline | Done |
| Graph generation and LuaLaTeX validation | Done |
| Full-source tests, branch coverage, and Ruff enforcement | Done |
| CI, license, and submission documentation | Done |
