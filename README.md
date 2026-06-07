# agent_ai_HW2 — Document Processing Pipeline with LLM Agents

AI Agents Homework 2 — converts documents to Markdown via `markitdown` and answers
natural-language questions using the Anthropic Claude API.

## System Requirements

- Python ≥ 3.10
- [`uv`](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd agent_ai_HW2

# 2. Copy environment template and fill in your API key
cp .env-example .env
# Edit .env: set ANTHROPIC_API_KEY=<your-key>

# 3. Install dependencies (uv only — never use pip directly)
uv sync --extra dev
```

## Usage

### CLI

```bash
uv run agent-ai path/to/document.pdf "What are the main conclusions?"
```

### Python API

```python
from sdk import AgentAISDK

sdk = AgentAISDK()
markdown = sdk.process_document("report.pdf")
answer   = sdk.query_document(markdown, "Summarise in 3 bullet points.")
print(answer)
```

## Configuration

| File | Purpose |
|------|---------|
| `config/setup.json` | App settings, LLM model, markitdown options |
| `config/rate_limits.json` | Per-service API rate limits |
| `config/logging_config.json` | Log format and levels |
| `.env` | Secrets (git-ignored — copy from `.env-example`) |

All configuration values are read from these files. **No values are hard-coded.**

## Running Tests

```bash
uv run pytest                         # run all tests with coverage
uv run pytest tests/unit/             # unit tests only
uv run pytest tests/integration/      # integration tests only
uv run ruff check src tests           # lint (must be 0 violations)
```

Coverage threshold is set to **85 %** in `pyproject.toml`.

## Project Structure

```
agent_ai_HW2/
├── src/
│   ├── sdk.py              # Public document Q&A entry point (AgentAISDK)
│   ├── config.py           # ConfigManager + article pipeline config
│   ├── gatekeeper.py       # ApiGatekeeper (rate limiting)
│   ├── version.py          # Version tracking (v1.00)
│   ├── constants.py
│   ├── agents/             # CrewAI article agents
│   ├── tasks/              # CrewAI article tasks
│   └── utils/              # Shared article pipeline helpers
├── tests/
│   ├── unit/               # Unit tests (mirrors src/)
│   └── integration/        # Integration tests
├── docs/
│   ├── PRD.md              # Product requirements
│   ├── PLAN.md             # Architecture & planning
│   └── TODO.md             # Task tracker
├── config/                 # JSON configuration files
├── data/                   # Input documents
├── results/                # Experiment outputs
├── notebooks/              # Jupyter analysis notebooks
└── assets/                 # Images and graphs
```

## Contribution Guidelines

- Follow the SDK architecture — all business logic goes through `AgentAISDK`.
- Keep every source file ≤ 150 lines of code.
- Write tests before implementation (TDD: red → green → refactor).
- Use `uv add <pkg>` to add dependencies; never `pip install`.
- No secrets or hard-coded config values in source code.

## License

MIT © moaawiyahhaj
