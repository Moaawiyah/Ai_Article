# Task Tracker — agent_ai_HW2

## Phase 0 — Documentation Update 🔄

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 0a | Update docs/PRD.md (F-05 to F-08) | High | ✅ Done | moaawiyahhaj |
| 0b | Update docs/PLAN.md (new ADRs, layers, contracts) | High | ✅ Done | moaawiyahhaj |
| 0c | Update docs/TODO.md (new phases) | High | ✅ Done | moaawiyahhaj |

## Phase 0.5 — Project Skills ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| S1 | .sixth/skills/run-pipeline.md | High | ✅ Done | moaawiyahhaj |
| S2 | .sixth/skills/compile-latex.md | High | ✅ Done | moaawiyahhaj |
| S3 | .sixth/skills/check-ollama.md | Medium | ✅ Done | moaawiyahhaj |
| S4 | .sixth/skills/run-tests.md | Medium | ✅ Done | moaawiyahhaj |

## Phase 1 — Documentation ✅

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 1 | Write docs/PRD.md | High | ✅ Done | moaawiyahhaj |
| 2 | Write docs/PLAN.md | High | ✅ Done | moaawiyahhaj |
| 3 | Write docs/TODO.md | High | ✅ Done | moaawiyahhaj |

## Phase 2 — Core Scaffold ✅

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 4 | pyproject.toml with ruff + coverage | High | ✅ Done | moaawiyahhaj |
| 5 | shared/version.py (v1.00) | High | ✅ Done | moaawiyahhaj |
| 6 | shared/config.py (ConfigManager) | High | ✅ Done | moaawiyahhaj |
| 7 | shared/gatekeeper.py (ApiGatekeeper) | High | ✅ Done | moaawiyahhaj |
| 8 | src/sdk.py (AgentAISDK) | High | ✅ Done | moaawiyahhaj |
| 9 | constants.py | Medium | ✅ Done | moaawiyahhaj |
| 10 | .env.example | High | ✅ Done | moaawiyahhaj |
| 11 | .gitignore | High | ✅ Done | moaawiyahhaj |

## Phase 3 — Services ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 12 | services/document_service.py | High | ⬜ Not started | - |
| 13 | services/query_service.py | High | ⬜ Not started | - |
| 14 | tests/unit/test_document_service.py | High | ⬜ Not started | - |
| 15 | tests/unit/test_query_service.py | High | ⬜ Not started | - |

## Phase 4 — Visuals & LaTeX ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 16 | config/article.json | High | ⬜ Not started | - |
| 17 | visuals/graph.py (GraphGenerator) | High | ⬜ Not started | - |
| 18 | visuals/__init__.py | Low | ⬜ Not started | - |
| 19 | tests/unit/test_graph.py | High | ⬜ Not started | - |
| 20 | latex/templates/article.tex.j2 | High | ⬜ Not started | - |
| 21 | latex/builder.py (MarkdownToLatexBuilder) | High | ⬜ Not started | - |
| 22 | latex/__init__.py | Low | ⬜ Not started | - |
| 23 | tests/unit/test_builder.py | High | ⬜ Not started | - |
| 24 | latex/compiler.py (LatexCompiler) | High | ⬜ Not started | - |
| 25 | tests/unit/test_compiler.py | High | ⬜ Not started | - |

## Phase 5 — CrewAI Pipeline Without RAG ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 26 | pyproject.toml — add crewai | High | ✅ Done | Codex |
| 27 | src/config.py (Ollama qwen3:14b adapter) | High | ✅ Done | Codex |
| 28 | src/agents/* five-agent factories | High | ✅ Done | Codex |
| 29 | src/tasks/* five sequential tasks | High | ✅ Done | Codex |
| 30 | src/main.py CrewAI orchestrator | High | ✅ Done | Codex |
| 31 | outputs/* scaffold | Low | ✅ Done | Codex |
| 32 | Reserve TODO for future RAG insertion point | Medium | ✅ Done | Codex |
| 33 | tests/unit/test_agents.py | High | ⬜ Not started | - |
| 34 | tests/unit/test_tasks.py | High | ⬜ Not started | - |
| 35 | tests/integration/test_pipeline.py | High | ⬜ Not started | - |

## Phase 6 — Tests & Quality ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 36 | tests/unit/test_version.py | High | ✅ Done | moaawiyahhaj |
| 37 | tests/unit/test_config.py | High | ✅ Done | moaawiyahhaj |
| 38 | tests/unit/test_gatekeeper.py | High | ✅ Done | moaawiyahhaj |
| 39 | tests/integration/test_sdk.py | High | ✅ Done | moaawiyahhaj |
| 40 | Achieve ≥ 85 % coverage | High | ⬜ Not started | - |
| 41 | Zero ruff violations | High | ⬜ Not started | - |

## Phase 7 — End-to-End Article Generation ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 42 | ollama pull qwen3:14b | High | ⬜ Not started | - |
| 43 | Run full pipeline: uv run python src/main.py | High | ⬜ Not started | - |
| 44 | Verify draft has required article elements | High | ⬜ Not started | - |
| 45 | Verify graph placeholder is present | High | ⬜ Not started | - |
| 46 | Generate LuaLaTeX-compatible article.tex | High | ⬜ Not started | - |
| 47 | Verify validation report: cover, ToC, Hebrew, formula, table, graph, bib | High | ⬜ Not started | - |

## Phase 8 — Final Submission ⬜

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| 48 | Complete README.md | High | ✅ Done | moaawiyahhaj |
| 49 | Git history clean with meaningful commits | Medium | ⬜ Not started | - |

## Definition of Done
- All tests pass (`uv run pytest`)
- Coverage ≥ 85 % (`fail_under = 85` in pyproject.toml)
- Zero Ruff violations (`uv run ruff check src tests`)
- No secrets or hard-coded config values in source code
- `outputs/pdf/validation_report.md` passes the assignment checklist
- README updated with usage examples
