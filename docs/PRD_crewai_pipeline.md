# PRD — CrewAI Article Generation Pipeline

**Version:** 1.00
**Owners:**
- `src/agent_ai/pipeline.py` — Crew assembly
- `src/agent_ai/main.py` — orchestrator entry point
- `src/agent_ai/agents/` — five thin agent factories
- `src/agent_ai/tasks/` — five linked CrewAI tasks
- `skills/<agent>/SKILL.md` — agent prompts

## 1. Goal

Generate a ~15-page bilingual academic article from a single topic string,
using a five-agent sequential CrewAI crew, ending with a validated PDF and a
13-item assignment-readiness report.

## 2. Background

This pipeline satisfies F-05 of the parent PRD and §13 of the assignment.
Each agent has a single responsibility, a SKILL.md prompt, and is wired into a
`Crew(process=Process.sequential)` so the output of agent *n* becomes the
context of agent *n+1*.

## 3. Agent Topology

| Order | Agent | Input | Output |
|-------|-------|-------|--------|
| 1 | Researcher | `topic` | `outputs/research/research_brief.md` |
| 2 | Writer | research brief | `outputs/drafts/draft.md` |
| 3 | Reviewer | draft | `outputs/reviewed/reviewed.md` |
| 4 | LaTeX Formatter | reviewed markdown | `outputs/latex/article.tex` |
| 5 | PDF Validator | article.tex | `outputs/pdf/agent_validation.md` |

After the crew finishes, three deterministic post-passes run:

1. **Graph step** — LLM-derived spec + matplotlib rendering → inject
   `\includegraphics` into the Evaluation section.
2. **Compile step** — `strip_tex_fences` then 3-pass LuaLaTeX +
   biber → `outputs/pdf/article.pdf`.
3. **Validate step** — 13 programmatic checks → `outputs/pdf/validation_report.md`.

## 4. Functional Requirements

| ID | Requirement |
|----|-------------|
| F-01 | Each agent reads its prompt from `skills/<name>/SKILL.md`, never inline. |
| F-02 | Tasks link via `context=[prev_task]` (Sequential process). |
| F-03 | All paths come from `config.yaml::outputs` — no hard-coded paths. |
| F-04 | Provider/model selectable via `config.yaml::llm.{provider,model,base_url}`. |
| F-05 | Token usage from the crew result is logged with per-token cost. |
| F-06 | Pipeline never crashes on a single agent failure — log and continue. |
| F-07 | Final 13-item validation report exits 0 if all checks pass. |

## 5. Inputs / Outputs / Setup

- **Input:** `config.yaml`, `skills/*/SKILL.md`, an LLM provider that is live.
- **Output:** `outputs/pdf/article.pdf` + `outputs/pdf/validation_report.md`.
- **Setup:** Provider API key in env (`ZHIPUAI_API_KEY`, `ANTHROPIC_API_KEY`,
  `OPENAI_API_KEY`, or `OLLAMA_BASE_URL`).

## 6. Cost Model

| Token Class | Price (`$/1M`) |
|-------------|---------------|
| Prompt input | 0.07 |
| Cached prompt | 0.01 |
| Completion | 0.40 |

These constants live in `pipeline_steps.py`. A full run typically uses
~120 K prompt + ~40 K completion tokens (~$0.025/run).

## 7. Constraints

- Each agent / task module ≤ 150 LoC.
- No business logic in `main.py` — only orchestration of pipeline steps.
- Crew assembly is testable in isolation via `build_crew(cfg)` returning
  `(Crew, PipelineConfig)` without invoking `kickoff`.

## 8. Failure Modes

| Failure | Handling |
|---------|----------|
| LLM provider down | Each step logs error; subsequent steps still attempt. Graph step uses fallback profile. |
| LaTeX compile error | `_compile_step` logs `error_summary`, returns `False`; validation step still runs and reports missing PDF. |
| Validation finds <13 / 13 | Exit code 0 (warnings only); failed checks printed with fix hints. |

## 9. Acceptance Criteria

- A fresh `outputs/` directory is produced after one `uv run python -m agent_ai.main`.
- `outputs/pdf/article.pdf` is ≥ 200 KB and ≥ 10 pages.
- `validation_report.md` reports ≥ 11/13 checks passing on a clean run.
- Token usage line appears in `logs/app.log` with input/output/total counts.

## 10. Tests

- Unit: `build_crew(cfg)` returns a `Crew` with exactly 5 agents and 5 tasks.
- Unit: cost-calc helper produces correct cents for fixed token inputs.
- Integration: tiny topic + Ollama mock → end-to-end produces all artefacts in
  a tmpdir.
