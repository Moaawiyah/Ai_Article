# run-tests

Run the full test suite with coverage and lint check. Report pass/fail status.

## What this skill does

1. Runs `uv run ruff check src tests` — zero violations required.
2. Runs `uv run pytest --cov=src --cov-report=term-missing` — all tests must pass, coverage ≥ 85 %.
3. Reports a concise summary: test count, pass/fail, coverage %, and any violations.

## Steps

```bash
# Lint check
uv run ruff check src tests

# Tests with coverage
uv run pytest --cov=src --cov-report=term-missing -v
```

## Interpreting results

- **Ruff**: any output means violations exist — list them and propose fixes.
- **pytest**: show the summary line (`X passed, Y failed, Z errors`).
- **Coverage**: show the `TOTAL` line. If below 85 %, list the files with lowest coverage and suggest what to test.

## Common fixes

- Missing `__init__.py` in a new package → add it.
- Import errors in tests → check `pythonpath = ["src"]` is set in `pyproject.toml`.
- Coverage below threshold → add unit tests for uncovered lines shown in the `term-missing` report.
