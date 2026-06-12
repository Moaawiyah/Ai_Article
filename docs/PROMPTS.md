# Prompt Engineering Log

This log documents the prompts used to build the `agent_ai_HW2` project with the
help of AI agents, including context, goals, iterations, and lessons learned.
It satisfies §8.3 of the submission guidelines (Prompt Engineering Log).

---

## 1. Project Scaffolding Prompts

### 1.1 Repository bootstrap
**Goal:** Create the package layout that matches the submission guidelines
(`src/<package>/`, `tests/{unit,integration}/`, `docs/`, `config/`, `outputs/`).

**Prompt (paraphrased):**
> Create a Python project layout following §2.4 of the guidelines. Use `uv` as
> the package manager. Add an SDK layer under `src/sdk/`, a shared
> layer with config, gatekeeper, and version under `src/shared/`, and
> an empty `services/` package. Generate `pyproject.toml` with `ruff` selecting
> `["E","F","W","I","N","UP","B","C4","SIM"]`, `pytest`, `pytest-cov` with
> `fail_under = 85`.

**Outcome:** Initial project skeleton — `pyproject.toml`, `src/`,
`tests/conftest.py`, `.env-example`, `.gitignore`.

**Lesson:** Asking for the *full layout in one prompt* avoided three rounds of
back-and-forth. Including the exact ruff rule set up-front saved a later
config-only iteration.

---

### 1.2 Documentation skeleton
**Prompt:**
> Generate `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` for an LLM-powered
> document Q&A SDK. PRD must include problem statement, KPIs, F-01..F-08
> functional requirements, and non-functional constraints (≤150 lines/file,
> ≥85 % test coverage). Plan must describe SDK → Domain → Infrastructure
> layering. TODO must use checkbox phases.

**Lesson:** Asking for *all three docs in one shot* kept their content aligned
(same KPIs, same phase numbers).

---

## 2. SDK and Gatekeeper Prompts

### 2.1 ApiGatekeeper
**Goal:** Implement a centralised API gatekeeper per §5.1.

**Prompt:**
> Write `src/shared/gatekeeper.py` exposing `ApiGatekeeper.execute()`
> that wraps any callable, enforces a `RateLimitConfig` (requests/minute,
> requests/hour, concurrent_max, retry_after_seconds, max_retries), queues
> overflow requests in FIFO order, and logs every call. Never raise on
> transient errors — retry, then surface failure via a structured exception.
> Limits must come from `config/rate_limits.json`.

**Iteration 1:** The first version hard-coded a 30 RPM default.
**Correction prompt:**
> §7.2 forbids hard-coded config values. Move all defaults to
> `config/rate_limits.json` and read them via `ConfigManager`. The gatekeeper
> constructor must accept only a `RateLimitConfig` dataclass.

**Lesson:** Stating which guideline section was violated (§7.2) instead of just
"this is wrong" produced a clean, minimal fix.

---

### 2.2 SDK entry point
**Prompt:**
> Build `AgentAISDK` exposing `process_document(file_path)` and
> `query_document(markdown, question)`. Use `markitdown` for conversion,
> `anthropic` Claude SDK for the LLM call. Route every Claude call through
> the gatekeeper. Load `ANTHROPIC_API_KEY` only from the environment —
> never accept it as a constructor argument.

**Lesson:** Adding the explicit *"never accept it as a constructor argument"*
clause prevented the model from generating an `api_key=None` parameter that
would have invited misuse.

---

## 3. Original CrewAI Article Pipeline Prompts

This section records the original five-agent implementation for development history.
The current implementation is the six-agent section workflow described in section 8.

### 3.1 Crew topology
**Goal:** Build the five-agent crew (Researcher → Writer → Reviewer → LaTeX
Formatter → PDF Validator) per F-05.

**Prompt:**
> Design a `Crew(process=Process.sequential)` with five agents, each loaded from
> a `skills/<agent>/SKILL.md` file. Each agent must be a thin factory in
> `src/agents/factory.py` that calls `load_skill()`. Each task lives in
> `src/tasks/<name>_task.py` and links to its predecessor via
> `context=[prev_task]`.

**Lesson:** Forcing the "Skill-file backed" pattern from the start meant we
never had giant prompts checked into Python source — they live in
`skills/*/SKILL.md` where editors can review them like docs.

### 3.2 Researcher SKILL prompt
**Goal:** Produce a structured research brief usable by the Writer.

**Prompt template** (excerpt from `skills/researcher/SKILL.md`):
> You are a senior systems-research analyst. Read the topic and produce a
> brief with: (1) abstract, (2) section-by-section outline with target word
> counts, (3) two named comparative architectures (A and B) for later
> benchmarking, (4) bibliography of ≥8 real citations.

**Iteration:** The first draft returned only Architecture A. We added the line
*"You MUST name both Comparative Architecture A and Comparative Architecture B
explicitly."* in capitals, which fixed it on the next run.

**Lesson:** When CrewAI agents skip a sub-task, a single ALL-CAPS imperative
line about the missing field is more reliable than rewording the whole brief.

---

### 3.3 LaTeX Formatter prompt
**Goal:** Convert reviewed Markdown to LuaLaTeX-compilable `article.tex`.

**Prompt highlights** (`skills/latex_formatter/SKILL.md`):
- "Output **only** the `.tex` source — no markdown fences, no commentary."
- "Use `polyglossia` for Hebrew passages."
- "Tables must use `\begin{table}` + `\adjustbox{max width=\textwidth}` to
  prevent page overflow."

**Iterations:**
1. Model added ```` ```latex ```` fences around the output → handled
   post-hoc by `strip_tex_fences()` in `tex_fixer.py`.
2. Model produced bare `tabular` columns of type `p` without a width → fixed by
   `fix_tabular_colspec()` (converts `p` → `p{3.5cm}`).
3. Hebrew sentences were inlined without `\texthebrew{...}` wrappers → fixed by
   `fix_hebrew_runs()`.

**Lesson:** It is cheaper to *post-process LaTeX* than to keep extending the
prompt with more rules. The model degrades on prompts longer than ~1500
tokens, but a 30-line regex pass is deterministic.

---

## 4. Inline LLM Prompts (Graph Spec)

### 4.1 Graph spec extraction
**File:** `src/utils/graph_spec.py`

**Prompt template:**
> You are a data extraction assistant. Read the research brief below and provide
> realistic bottleneck queue distribution parameters for the main architecture
> and the two older/related comparative architectures mentioned in it.
> Output **only** valid JSON — no explanation, no markdown fences:
> `{"main": {...}, "arch_a": {...}, "arch_b": {...}}`
> Rules: main must be best, arch_a/arch_b are legacy systems with longer queues
> and higher FCT. Ensure all three are visually distinct.

**Iterations:**
1. **v1** asked for JSON with no rules → model returned arch_a/arch_b *better*
   than main. Added explicit ranking rule.
2. **v2** returned identical curves for arch_a and arch_b → added
   "Ensure all three are meaningfully different".
3. **v3** wrapped the JSON in ```` ```json ```` → added regex stripper +
   `re.search(r"\{.*\}", raw, re.DOTALL)` as a last-resort fallback.

**Lesson:** A deterministic *fallback dict* (`_FALLBACK` in `graph_fallback.py`)
plus *brief-extracted architecture names* keeps the graph rendering even when
the LLM is unavailable or its response is malformed. The pipeline never breaks
on the visual step.

---

## 5. Test Generation Prompts

### 5.1 Gatekeeper tests
**Prompt:**
> Generate `tests/unit/test_gatekeeper.py` covering: queue overflow,
> requests-per-minute reset, concurrent-max blocking via threads, retry on
> transient failure (raise once, then succeed). Use `pytest.fixture` from
> `conftest.py`. No real network calls.

**Lesson:** Specifying the *exact behaviours to cover* (instead of "test the
gatekeeper") produced four focused tests, each <30 lines, instead of one
80-line monolith.

---

## 6. Recommended Practices Distilled From This Project

| Practice | Why |
|----------|-----|
| Cite the guideline section number when correcting (e.g. "§7.2 forbids X") | Model fixes the *category* of mistake, not just the line. |
| Keep agent prompts in `skills/*/SKILL.md`, not inline strings | Reviewers diff them like docs; version control sees changes clearly. |
| Always provide a deterministic fallback for inline LLM calls | The pipeline must not crash on an upstream LLM hiccup. |
| Prefer post-processing over longer prompts when format drifts | Regex post-passes are deterministic and testable; longer prompts degrade. |
| Add an ALL-CAPS imperative for single-field omissions | More reliable than rewriting the whole prompt. |
| Specify "output **only** X — no explanation, no fences" | Saves a regex strip and reduces parsing failures. |

---

## 7. Prompt Index

| Component | Prompt source |
|-----------|---------------|
| Researcher agent | `skills/researcher/SKILL.md` |
| Writer agent | `skills/writer/SKILL.md` |
| Source Verifier | `skills/source_verifier/SKILL.md` |
| Article Editor | `skills/article_editor/SKILL.md` |
| LaTeX Formatter | `skills/latex_formatter/SKILL.md` |
| Submission Validator | `skills/submission_validator/SKILL.md` |
| Graph spec extraction | `src/utils/graph_spec.py::_PROMPT` |

All inline prompts in source are reviewed under
`ruff check` and pinned to `model = config.llm.model` from `config.yaml` — no
model name is hard-coded in source.

---

## 8. Six-Agent Section Workflow

The current workflow uses small one-agent CrewAI calls controlled by a Python state machine.
Researcher and Source Verifier exchange structured JSON with at most two returns. Section
Writer and Article Editor process one section at a time, with one return per section and an
article-wide `ceil(33%)` rejection budget. LaTeX Formatter consumes approved sections only,
and Submission Validator emits a scored advisory evaluation that cannot block delivery.

The prompts require verifier-approved visual provenance and a dedicated
`Hebrew and English in AI Systems` section. Workflow state and approved outputs are persisted
so retries resume rather than regenerate completed work.
