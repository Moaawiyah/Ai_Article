# Assignment 03 Task Tracker

This file is our working task plan for the CrewAI and LaTeX article generator.
It reflects the current repository state rather than the original project
scaffold.

## Project Team

| Team member | Primary focus | Review responsibility |
|---|---|---|
| Mohammad Selawe | Architecture, SDK, API gatekeeper, tests, documentation, and submission compliance | Reviews pipeline integration, generated artifacts, and final PDF evidence |
| Moa'awiyah Hajajreh | CrewAI agents and tasks, prompts, article generation, LaTeX, graph generation, and PDF output | Reviews configuration, test results, documentation, and release readiness |

We share topic selection, prompt refinement, debugging, end-to-end runs, output
inspection, and final submission decisions. An owner is responsible for moving
a task to completion; the reviewer confirms the acceptance criteria.

## Status Legend

| Status | Meaning |
|---|---|
| Done | Implemented and verified with repository evidence |
| In progress | Actively being updated or awaiting review |
| Planned | Required before the final submission |
| Optional | Useful improvement that is not required for submission |

## Current Milestone

| Metric | Current result |
|---|---|
| CrewAI workflow | 5 agents, 5 sequential tasks |
| Generated article | HULA: Scalable Load Balancing Using Programmable Data Planes |
| Final PDF | 15 A4 pages |
| Assignment validator | 13/13 checks passed |
| Automated tests | 198 passed |
| Statement coverage | 93.84% |
| Ruff | 0 violations |
| Article provider | Z.AI `glm-4.7-flashx` |
| Development models | Local Ollama/Qwen models |
| Secondary feature | Document conversion and question answering |

---

## Phase 1 - Foundation and Configuration

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence |
|---|---|---|---|---|---|
| FND-01 | Package the project with `pyproject.toml`, `uv.lock`, console scripts, and development dependencies. | Mohammad | Moa'awiyah | Done | `uv sync --extra dev` installs the project and both CLI entry points are registered. |
| FND-02 | Define the public `AgentAISDK` interface for document processing, document Q&A, article generation, and version reporting. | Mohammad | Moa'awiyah | Done | `src/sdk/sdk.py` exposes `process_document`, `query_document`, `generate_article`, and `get_version`. |
| FND-03 | Move article, provider, output, pricing, and graph settings into configuration files. | Mohammad | Moa'awiyah | Done | `config/config.yaml`, `config/setup.json`, and `config/rate_limits.json` are loaded at runtime. |
| FND-04 | Keep secrets outside source control and document all required environment variables. | Mohammad | Moa'awiyah | Done | `.env.example` contains placeholders for Z.AI and Anthropic keys; `.env` is ignored. |
| FND-05 | Support local Ollama/Qwen models for development and Z.AI for final hosted runs without changing pipeline code. | Moa'awiyah | Mohammad | Done | `PipelineConfig.build_llm()` selects the provider from `config/config.yaml`. |
| FND-06 | Record token usage and estimate hosted-model cost after article generation. | Moa'awiyah | Mohammad | Done | `print_token_usage()` reads configured pricing and logs the estimated cost. |

### Phase 1 Acceptance Criteria

- [x] We can install the project using only `uv`.
- [x] We can change the model provider through configuration.
- [x] We do not store API keys in committed source files.
- [x] CLI code delegates business logic to the SDK.

---

## Phase 2 - CrewAI Article Pipeline

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence |
|---|---|---|---|---|---|
| CRW-01 | Define reusable `SKILL.md` instructions for the Researcher, Writer, Reviewer, LaTeX Formatter, and PDF Validator. | Moa'awiyah | Mohammad | Done | Five skill directories exist under `skills/`. |
| CRW-02 | Build a parameterized agent factory that loads role, goal, and instructions from each skill file. | Moa'awiyah | Mohammad | Done | `src/agents/factory.py` creates CrewAI agents through `build_agent()`. |
| CRW-03 | Create one task builder for every agent and connect each task to the previous stage's output. | Moa'awiyah | Mohammad | Done | Five builders exist in `src/tasks/`. |
| CRW-04 | Assemble the agents and tasks with `Process.sequential`. | Moa'awiyah | Mohammad | Done | `src/pipeline.py` builds a five-agent, five-task crew. |
| CRW-05 | Preserve research, draft, review, LaTeX, validation, and graph-spec artifacts for inspection. | Moa'awiyah | Mohammad | Done | Each stage writes to its configured `outputs/` directory. |
| CRW-06 | Route the crew kickoff and graph-spec model call through the central API gatekeeper. | Mohammad | Moa'awiyah | Done | External pipeline calls use `ApiGatekeeper.execute()`. |
| CRW-07 | Add structured logs and stage timing for generation, graphing, compilation, and validation. | Mohammad | Moa'awiyah | Done | Runtime logs identify stage starts, finishes, failures, token usage, and output paths. |

### Phase 2 Acceptance Criteria

- [x] Every agent has a distinct responsibility and artifact.
- [x] The Writer consumes the Researcher output.
- [x] The Reviewer runs before LaTeX conversion.
- [x] A failed external call is retried and reported consistently.
- [x] Intermediate outputs remain available for manual review.

---

## Phase 3 - LaTeX, Visuals, and PDF

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence |
|---|---|---|---|---|---|
| PDF-01 | Convert reviewed Markdown into complete LuaLaTeX source. | Moa'awiyah | Mohammad | Done | `outputs/latex/article.tex` contains a complete document. |
| PDF-02 | Add title, authors, table of contents, sections, headers, footers, table, formula, citations, and bibliography. | Moa'awiyah | Mohammad | Done | The generated LaTeX and validation reports contain evidence for each item. |
| PDF-03 | Add Hebrew-English bidirectional text using Unicode-compatible LaTeX packages. | Moa'awiyah | Mohammad | Done | The document uses `fontspec`, `polyglossia`, a `hebrew` environment, and `\textenglish{}`. |
| PDF-04 | Convert the architecture marker into a native TikZ figure. | Moa'awiyah | Mohammad | Done | `article.tex` contains a `tikzpicture` environment. |
| PDF-05 | Generate the benchmark plot with Python and inject it into the Evaluation section. | Moa'awiyah | Mohammad | Done | `graph_generator.py` creates `benchmark.png`; `figure_inject.py` inserts it into the LaTeX source. |
| PDF-06 | Make graph generation reproducible and provide a fallback data specification. | Mohammad | Moa'awiyah | Done | The generator uses a fixed seed and `graph_fallback.py`. |
| PDF-07 | Add deterministic repair passes for fences, syntax, tables, TikZ, math, and Hebrew formatting. | Moa'awiyah | Mohammad | Done | Repair modules exist under `src/utils/` and have regression tests. |
| PDF-08 | Compile with multiple LuaLaTeX passes and capture compiler output without crashing the SDK. | Moa'awiyah | Mohammad | Done | `compile_pdf()` returns a structured `CompileResult` and writes `logs/latex_compile.log`. |
| PDF-09 | Produce the final 15-page PDF and retain the LaTeX source and plot. | Both | Both | Done | `outputs/pdf/article.pdf`, `outputs/latex/article.tex`, and `outputs/latex/benchmark.png` are present. |

### Phase 3 Acceptance Criteria

- [x] The final document is generated by LuaLaTeX.
- [x] The PDF is approximately 15 pages; the current result is exactly 15.
- [x] The Python plot and TikZ diagram render in the document.
- [x] Hebrew and embedded English technical terms render in the correct direction.
- [x] Compilation failures produce an actionable log and error summary.

---

## Phase 4 - Document and Article Q&A

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence |
|---|---|---|---|---|---|
| QNA-01 | Convert supported documents to Markdown through MarkItDown. | Mohammad | Moa'awiyah | Done | `AgentAISDK.process_document()` accepts PDF, DOCX, PPTX, XLSX, HTML, TXT, and Markdown inputs supported by configuration. |
| QNA-02 | Ask natural-language questions about extracted document content. | Mohammad | Moa'awiyah | Done | `AgentAISDK.query_document()` returns the model's answer as text. |
| QNA-03 | Route Q&A requests through the API gatekeeper and load the Anthropic key lazily. | Mohammad | Moa'awiyah | Done | Q&A uses `ApiGatekeeper.execute()` and creates the Anthropic client only when needed. |
| QNA-04 | Expose the feature through `agent-ai <file> "<question>"`. | Mohammad | Moa'awiyah | Done | The console script processes the file and prints the answer. |
| QNA-05 | Document an example that asks a question about `outputs/pdf/article.pdf`. | Mohammad | Moa'awiyah | In progress | The README contains the command; final wording and commit remain to be reviewed. |

### Phase 4 Acceptance Criteria

- [x] A missing document raises a clear `FileNotFoundError`.
- [x] The Anthropic key is not required for article generation.
- [x] Q&A calls use the same retry and rate-limit infrastructure as other external calls.
- [ ] The final README update containing the article-Q&A example is committed and pushed.

---

## Phase 5 - Testing and Quality Assurance

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence |
|---|---|---|---|---|---|
| QA-01 | Test configuration loading, defaults, missing files, and environment handling. | Mohammad | Moa'awiyah | Done | Configuration unit tests pass. |
| QA-02 | Test gatekeeper FIFO ordering, bounded queues, retries, counters, and concurrency. | Mohammad | Moa'awiyah | Done | Gatekeeper and queue tests pass. |
| QA-03 | Test agent creation, skill loading, task dependencies, and pipeline assembly. | Moa'awiyah | Mohammad | Done | Agent, skill, task, and pipeline tests pass. |
| QA-04 | Test graph parsing, fallback behavior, plot generation, and figure injection. | Moa'awiyah | Mohammad | Done | Graph-related unit tests pass. |
| QA-05 | Test LaTeX repair behavior for fences, tables, TikZ, Hebrew, and syntax errors. | Moa'awiyah | Mohammad | Done | LaTeX post-processing and integration tests pass. |
| QA-06 | Test compiler success, missing tools, malformed LaTeX, and structured failure results. | Mohammad | Moa'awiyah | Done | Compiler tests cover success and failure paths. |
| QA-07 | Test all 13 assignment-validation checks and report generation. | Mohammad | Moa'awiyah | Done | Validator tests and generated reports pass. |
| QA-08 | Maintain at least 85% statement coverage. | Both | Both | Done | Current coverage is 93.84%. |
| QA-09 | Keep Ruff at zero violations across source, tests, and notebooks. | Both | Both | Done | `uv run ruff check .` passes. |
| QA-10 | Run the full automated suite before every final submission commit. | Mohammad | Moa'awiyah | Planned | Record the final command result after all documentation edits are complete. |

### Phase 5 Acceptance Criteria

- [x] `uv run pytest -q` passes.
- [x] Coverage meets the configured 85% threshold.
- [x] `uv run ruff check .` passes.
- [x] External services and compilers are mocked in automated tests where appropriate.
- [ ] Tests and lint are rerun after the remaining documentation work.

---

## Phase 6 - Documentation and Submission

| ID | Actionable task | Owner | Reviewer | Status | Completion evidence / next action |
|---|---|---|---|---|---|
| DOC-01 | Rewrite the README as an Assignment 03 report and developer guide using first-person plural. | Mohammad | Moa'awiyah | Done | README includes the project report, architecture, requirements, results, setup, usage, and screenshots. |
| DOC-02 | Add top-level links to installation instructions and the article-Q&A feature. | Mohammad | Moa'awiyah | In progress | Links are present locally; review, commit, and push them. |
| DOC-03 | Rewrite this TODO as a task-oriented tracker with balanced ownership and acceptance criteria. | Mohammad | Moa'awiyah | In progress | Review this file against the current implementation, then commit it. |
| DOC-04 | Update `docs/PRD.md` to describe the current HULA topic, generated graph, Z.AI final provider, local Ollama testing, and completed features. | Mohammad | Moa'awiyah | Planned | Remove stale statements that graph generation is deferred or Ollama is the only provider. |
| DOC-05 | Update `docs/PLAN.md` to match current artifact names, provider strategy, and implemented architecture. | Mohammad | Moa'awiyah | Planned | Verify every path and diagram against `src/` and `outputs/`. |
| DOC-06 | Review agent skills and prompt documentation for contradictions about Hebrew, bibliography size, and output filenames. | Moa'awiyah | Mohammad | Planned | Align skill rules with the final pipeline behavior without changing proven outputs unnecessarily. |
| DOC-07 | Perform a manual page-by-page PDF review for clipping, unreadable tables, visual placement, BiDi rendering, and citation links. | Moa'awiyah | Mohammad | Planned | Record findings and either fix them or mark the PDF ready. |
| DOC-08 | Verify the final bibliography entries and graph data descriptions against the research brief. | Moa'awiyah | Mohammad | Planned | Confirm references are credible and estimated values are labeled honestly. |
| DOC-09 | Decide which currently untracked evaluation and assignment-support files belong in the submission. | Both | Both | Planned | Add only intentional submission evidence; leave temporary notes untracked. |
| DOC-10 | Run the final test, lint, link, PDF, and validation checks after documentation is synchronized. | Mohammad | Moa'awiyah | Planned | Complete the release checklist below. |
| DOC-11 | Create a descriptive final documentation commit and push it to `origin/main`. | Mohammad | Moa'awiyah | Planned | Confirm local `main` and `origin/main` point to the same commit. |
| DOC-12 | Create an optional `v1.0.0` release tag after both students approve the final submission. | Both | Both | Optional | Tag only after no required task remains open. |

---

## Final Assignment Checklist

| ID | Submission item | Owner | Reviewer | Status |
|---|---|---|---|---|
| SUB-01 | CrewAI agent and task source code | Moa'awiyah | Mohammad | Done |
| SUB-02 | Research, draft, and reviewed Markdown artifacts | Moa'awiyah | Mohammad | Done |
| SUB-03 | LuaLaTeX source | Moa'awiyah | Mohammad | Done |
| SUB-04 | Python graph-generation source and generated plot | Moa'awiyah | Mohammad | Done |
| SUB-05 | TikZ diagram, table, formula, Hebrew-English section, and linked citations | Moa'awiyah | Mohammad | Done |
| SUB-06 | Final 15-page PDF | Both | Both | Done |
| SUB-07 | Programmatic and agent validation reports | Mohammad | Moa'awiyah | Done |
| SUB-08 | Installation, article-generation, and Q&A instructions | Mohammad | Moa'awiyah | In progress |
| SUB-09 | Current PRD, PLAN, TODO, architecture, and prompt documentation | Mohammad | Moa'awiyah | Planned |
| SUB-10 | Final clean test and lint run | Mohammad | Moa'awiyah | Planned |
| SUB-11 | Final repository review and submission approval | Both | Both | Planned |

## Release Checklist

Run these checks from the repository root:

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv run agent-ai-article
```

After the article run:

- [ ] Confirm `outputs/pdf/article.pdf` exists and has approximately 15 pages.
- [ ] Confirm `outputs/pdf/validation_report.md` reports 13/13 passed.
- [ ] Open the PDF and inspect the title page, table of contents, plot, TikZ
      diagram, table, formula, Hebrew-English text, citations, and bibliography.
- [ ] Run an article Q&A smoke test:

```bash
uv run agent-ai outputs/pdf/article.pdf "What are the main conclusions?"
```

- [ ] Confirm README local links resolve.
- [ ] Confirm no secrets or `.env` file are staged.
- [ ] Confirm only intentional source, documentation, and output artifacts are staged.
- [ ] Confirm both students approve the final diff.
- [ ] Commit with a descriptive message and push to `origin/main`.

## Definition of Done

We consider the project complete when:

- All required CrewAI, Markdown, LaTeX, graph, BiDi, citation, and PDF artifacts
  are present.
- The final PDF compiles successfully and passes the 13-item validator.
- The test suite passes with at least 85% coverage.
- Ruff reports zero violations.
- Article generation and document Q&A are documented with reproducible commands.
- PRD, PLAN, TODO, architecture, prompts, and README describe the same current
  implementation.
- No secrets or accidental temporary files are included in the commit.
- Mohammad and Moa'awiyah both review and approve the final submission.
