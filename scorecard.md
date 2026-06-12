# Code Scorecard — agent_ai_HW2 — 2026-06-12
Tested against the guidelines in output.md (Table 5 quick-reference card + §17 final checklist).

## Scores
| Category              | Score |
|-----------------------|-------|
| Structure & docs      | 4/5   |
| Architecture & code   | 3/5   |
| Tests & quality       | 4/5   |
| Config & security     | 5/5   |
| Research & viz        | 3/5   |
| Extension & standards | 3/5   |
| **Overall**           | **22/30 (73%)** |

## Hard-gate checklist (Table 5)
- [x] Files ≤ 150 lines (non-blank/non-comment) — all pass; largest is exactly 150 (`src/pipeline_steps.py`)
- [ ] 0 Ruff violations — **11 failures** (E702, all in `notebooks/results_analysis.ipynb`); `src/` and `tests/` are clean
- [x] Coverage ≥ 85% — **91.07%** (127 tests pass)
- [x] uv.lock + pyproject.toml present; no requirements.txt / poetry.lock / Pipfile
- [x] No secrets in code — `src/` grep for `sk-`/`api_key=`/`password=`/`token=` literals: none
- [x] `.env.example` present with placeholders only — file is `.env-example` (hyphen, not `.env.example`)
- [x] `.gitignore` present and ignores `.env` (`src/shared/.gitignore` → `.env`, `*.key`, `*.pem`)
- [x] README.md + docs/PRD.md + docs/PLAN.md + docs/TODO.md present
- [ ] All external calls through the API gatekeeper — **1 direct call bypasses it** (`src/utils/graph_spec.py:115`)
- [x] Config-driven rate limits — `config/rate_limits.json` consumed by `ApiGatekeeper`, not hardcoded
- [x] Version starts at 1.00 — `src/shared/version.py` (`VERSION = "1.00"`)

## Failures (with locations) — hard gates first
1. **API gatekeeper bypass** — `src/utils/graph_spec.py:115` — `litellm.completion(**params)` is called directly, not through `ApiGatekeeper.execute`. The SDK correctly routes `crew.kickoff` (`src/sdk/sdk.py:135`) and `query_document` (`src/sdk/sdk.py:101`) through the gatekeeper, but this graph-spec LLM fallback call escapes rate-limiting/retry/queue/logging. Fix: inject the gatekeeper into `generate_graph_spec` and wrap the call in `gatekeeper.execute(litellm.completion, **params)`.
2. **Ruff: 11 × E702 (multiple statements on one line)** — `notebooks/results_analysis.ipynb` cells 2, 5, 7 (e.g. `ax.set_xlabel(...); ax.set_ylabel(...)`). `ruff check .` exits non-clean. Fix: split semicolon-joined statements (1 is auto-fixable via `ruff check --fix`); or exclude notebooks in `pyproject.toml` if intentional.
3. **49 functions/classes missing docstrings** — nested helpers and enums, e.g. `src/utils/tex_hebrew.py:28` `_wrap_run`, `src/utils/tex_tables.py:54` `_fix`, `src/constants.py:9` `ProcessingMode`, `src/utils/tex_validator.py:21` `_check_tikz`. Public SDK/module/top-level functions are well documented; the gap is inner closures and `Enum` subclasses. §17.2 asks for docstrings on every function/class.
4. **No architecture diagrams** — `docs/` discusses architecture in prose but contains no C4/mermaid/UML diagrams (§17.1 asks for "architecture documentation with clear diagrams"). `.env.example` naming (`.env-example`) also deviates from the checklist spelling — cosmetic only.

## Category notes (evidence)
- **Structure & docs 4/5** — Strong: `README.md` (82 lines, user-guide level), `docs/` with `PRD.md`/`PLAN.md`/`TODO.md`, per-mechanism PRDs (`PRD_graph_generation.md`, `PRD_latex_fixer.md`, `PRD_pdf_compilation.md`, `PRD_crewai_pipeline.md`), and a prompts book (`docs/PROMPTS.md`, 211 lines). Gap: no architecture diagrams.
- **Architecture & code 3/5** — Clean SDK layer (`src/sdk/sdk.py`, single public entry point; CLI `src/main.py` delegates only), central `ApiGatekeeper` with FIFO queue + retry + semaphore, config-driven limits, agent factory (DRY), all files ≤150 lines. Docked for the gatekeeper bypass (#1) and missing docstrings (#3).
- **Tests & quality 4/5** — 127 tests pass, 91.07% coverage, unit + integration split, edge cases covered. Docked because `ruff check .` is not clean (#2) — a hard gate, though confined to the notebook.
- **Config & security 5/5** — `config/*.{yaml,json}` separate from code with version fields, `.env-example` placeholders only, no secrets in `src/`, `.gitignore` covers `.env`/keys, uv + `uv.lock` + `pyproject.toml` as sole package manager.
- **Research & viz 3/5** — `notebooks/results_analysis.ipynb` produces quality graphs; limited systematic parameter experiments / token-cost analysis, and the notebook holds the Ruff violations.
- **Extension & standards 3/5** — Extension points via `src/utils/skill_loader.py` + `skills/` plugins, packaged with a console script in `pyproject.toml`, clean git history. No explicit ISO/IEC 25010 mapping.

## Verdict
**Partially meets the submission bar.** Quality is high (91% coverage, clean SDK + gatekeeper architecture, all files ≤150 lines, full docs set), but two Table-5 hard gates fail: a direct `litellm` call bypassing the gatekeeper (`graph_spec.py:115`) and 11 Ruff violations in the analysis notebook. Both are small, localized fixes — close them and the project clears every hard gate.
