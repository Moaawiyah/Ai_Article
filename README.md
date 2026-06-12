# agent_ai_HW2 — Academic Article Generator (CrewAI + LuaLaTeX)

A 5-agent [CrewAI](https://docs.crewai.com) pipeline that writes a complete
academic article on a configured topic and produces a polished PDF. The crew
runs **researcher → writer → reviewer → LaTeX formatter → validator**; after the
crew finishes, deterministic post-passes inject a Python-generated benchmark
figure, compile with **LuaLaTeX**, and run a 13-item programmatic checklist
against the assignment requirements.

Final output: `outputs/pdf/article.pdf` plus a `validation_report.md`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for C4 diagrams, ADRs, and interface contracts.

## System Requirements

- Python **3.12** (pinned via `.python-version`)
- [`uv`](https://docs.astral.sh/uv/) package manager
- A **LuaLaTeX** toolchain (e.g. TeX Live / MiKTeX) on `PATH`, with Hebrew
  font support for the bilingual section
- An LLM provider key — by default `ZHIPUAI_API_KEY` (see `config/config.yaml`)

## Installation

```bash
uv sync --extra dev          # installs runtime + test/lint tooling into .venv
export ZHIPUAI_API_KEY=<your-key>   # provider configured in config/config.yaml
```

## Usage

```bash
# Generate the article for the topic in config/config.yaml
uv run agent-ai-article

# …or override the topic
uv run agent-ai-article --topic "Your topic here"
```

The pipeline writes intermediate artifacts under `outputs/` (research brief →
draft → reviewed → `article.tex` → `article.pdf`) and the validation report to
`outputs/pdf/validation_report.md`.

> A secondary document-Q&A entry point (`agent-ai <file> "<question>"`, using
> `markitdown` + the Anthropic API) also lives in the SDK and requires
> `ANTHROPIC_API_KEY`.

## Configuration

Everything is driven from config — no values are hard-coded in source.

| File | Purpose |
|------|---------|
| `config/config.yaml` | Topic, LLM provider/model, page/word targets, required artifacts, output paths, pricing |
| `config/logging_config.json` | Log format and levels |
| `config/rate_limits.json` | Per-service API rate limits (document-Q&A path) |

## Running Tests

```bash
uv run pytest                  # full suite with coverage (threshold 85%)
uv run ruff check src tests    # lint
```

## Project Structure

```
src/
├── main.py            # CLI entry → AgentAISDK.generate_article
├── sdk/sdk.py         # Public SDK (article generation + document Q&A)
├── pipeline.py        # Builds the 5-agent sequential Crew
├── pipeline_steps.py  # Post-crew passes: graph → compile → validate
├── agents/factory.py  # Single parametrised agent factory (skill → Agent)
├── tasks/             # research / writing / review / latex / validation tasks
├── shared/            # config, gatekeeper, pipeline_config, version
└── utils/             # tex_fixer & friends, validators, graph + PDF tooling
skills/                # SKILL.md per agent (researcher, writer, reviewer, …)
config/                # configuration files
outputs/               # generated artifacts (research → drafts → latex → pdf)
tests/                 # unit + integration tests
```

## License

MIT © moaawiyahhaj
