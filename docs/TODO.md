# Task Tracker - agent_ai_HW2

## Completed

| Task | Priority | Owner | Definition of Done |
|---|---|---|---|
| PRD, architecture plan, mechanism PRDs, and prompt log | High | Project | Documents match current implementation |
| SDK boundary for document Q&A and article generation | High | Project | CLI delegates to `AgentAISDK` |
| Configured providers and environment-only keys | High | Project | No provider/model source edits required |
| FIFO API gatekeeper with backpressure and retries | High | Project | Queue, limits, concurrency, and metrics tested |
| Five-agent CrewAI pipeline | High | Project | Sequential tasks produce configured artifacts |
| Graph data resolution, rendering, and LaTeX injection | High | Project | PNG and graph specification are generated |
| LuaLaTeX compilation and 13-check validation | High | Project | PDF and validation report exist |
| Full-source tests and branch coverage | High | Project | `uv run pytest` passes at >= 85% |
| Ruff compliance | High | Project | `uv run ruff check src tests` passes |
| README, MIT license, and GitHub Actions CI | High | Project | Submission support files are present |

## Maintenance Backlog

| Task | Priority | Status | Definition of Done |
|---|---|---|---|
| Add reproduced benchmark datasets instead of literature-informed estimates | Medium | Planned | Graph inputs come from checked-in experiment data |
| Add provider-specific transient-error classification | Medium | Planned | Permanent errors are not retried |
| Add Windows and Linux PDF compilation CI jobs | Low | Planned | LuaLaTeX artifact is built on both platforms |
| Add a REST adapter over `AgentAISDK` | Low | Backlog | No internal module is exposed directly |

## Definition of Done

- `uv sync --extra dev`
- `uv run ruff check src tests`
- `uv run pytest`
- Coverage includes every module under `src/`, with branch coverage and `fail_under = 85`.
- No source or test file exceeds 150 code lines.
- No secrets are committed.
- Generated PDF validation passes 13/13.
- Documentation and configuration describe the current provider and module layout.
