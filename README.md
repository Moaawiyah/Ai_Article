# agent-ai

Python SDK and CLI for document Q&A and five-agent academic article generation. The article workflow produces research, reviewed Markdown, LuaLaTeX, a benchmark graph, a compiled PDF, and a 13-check validation report.

## Requirements

- Python 3.12 (`.python-version`)
- [`uv`](https://docs.astral.sh/uv/)
- LuaLaTeX through TeX Live or MiKTeX for PDF compilation
- A provider key matching `config/config.yaml`

The default article provider is ZhipuAI:

```powershell
$env:ZHIPUAI_API_KEY = "your-key"
```

Document Q&A uses Anthropic:

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
```

## Installation

```bash
uv sync --extra dev
```

Do not use `pip`, a manually created virtual environment, or `requirements.txt`.

## Usage

Generate an article using the configured topic:

```bash
uv run agent-ai-article
```

Override the topic:

```bash
uv run agent-ai-article --topic "Your academic topic"
```

Ask a question about a document:

```bash
uv run agent-ai path/to/document.pdf "What are the main findings?"
```

The final PDF is written to `outputs/pdf/article.pdf`. Intermediate files are under `outputs/research`, `outputs/drafts`, `outputs/reviewed`, `outputs/latex`, and `outputs/assets`.

## Configuration

| File | Purpose |
|---|---|
| `config/config.yaml` | Topic, provider, model, endpoint, output paths, article targets, and token pricing |
| `config/rate_limits.json` | Per-provider limits, retries, queue capacity, and rate-window durations |
| `config/setup.json` | Document Q&A model and conversion settings |
| `config/logging_config.json` | Logging defaults |
| `.env-example` | Environment-variable placeholders |

To use Ollama, set `llm.provider`, `llm.model`, and `llm.base_url` in `config/config.yaml`, then ensure the configured model is available locally.

## Architecture

`AgentAISDK` is the public boundary. Both CLIs delegate to it. Article generation builds five CrewAI agents, passes external work through `ApiGatekeeper`, generates and injects a graph, compiles LuaLaTeX, and validates the result.

```text
CLI -> AgentAISDK -> ApiGatekeeper -> CrewAI/provider
               \-> graph -> TeX repair -> LuaLaTeX -> validator
```

Detailed C4, sequence, deployment, contracts, ADRs, and extension points are in `docs/PLAN.md`.

## Quality Checks

```bash
uv run ruff check src tests
uv run pytest
```

Coverage is measured across every module under `src/`, including branch coverage, and fails below 85%. Tests mock paid APIs and do not require network access.

GitHub Actions runs the same checks for pushes and pull requests.

## Troubleshooting

- **`ruff` or `pytest` not found:** run `uv sync --extra dev`.
- **Missing provider key:** set the environment variable for the provider selected in `config/config.yaml`.
- **LuaLaTeX not found:** install TeX Live or MiKTeX and ensure `lualatex` is on `PATH`.
- **Ollama connection refused:** start `ollama serve` and confirm the configured model is pulled.
- **PDF compilation failure:** inspect `logs/latex_compile.log` and `outputs/pdf/validation_report.md`.

## Project Structure

```text
src/
  sdk/              public SDK
  shared/           configuration, versioning, gatekeeper
  agents/           CrewAI agent factory
  tasks/            stage task contracts
  utils/            graph, LaTeX, logging, compilation, validation
tests/
  unit/
  integration/
docs/               PRD, architecture, task tracker, prompt log, mechanism PRDs
config/             versioned runtime configuration
skills/             agent skill instructions
outputs/            generated artifacts
```

## Contributing

1. Create a feature branch and keep changes scoped.
2. Add or update tests for every public behavior.
3. Keep source and test files at or below 150 code lines.
4. Run Ruff and pytest before opening a pull request.
5. Update PRD, PLAN, TODO, and README when behavior or architecture changes.

Use descriptive commit messages and do not commit API keys, `.env`, generated caches, or local toolchain files.

## License and Credits

Licensed under the MIT License. See `LICENSE`.

Built with CrewAI, Anthropic, MarkItDown, LiteLLM, Matplotlib, pytest, Ruff, and uv. Third-party packages retain their respective licenses.
