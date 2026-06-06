# run-pipeline

Run the full article generation pipeline end-to-end: CrewAI crew → graph → LaTeX → PDF.

## What this skill does

Executes the complete HW2 article generation workflow in sequence:

1. Verify Ollama is running with `qwen3:14b` available.
2. Run `uv run python -m agent_ai.crew.run` to generate `results/article/article.md` via CrewAI.
3. Confirm `article.md` contains all 8 required elements (cover block, ToC, Hebrew section, table, graph placeholder, image placeholder, formula, bibliography).
4. Run `uv run python -c "from pathlib import Path; from agent_ai.visuals.graph import GraphGenerator; GraphGenerator().generate(Path('results/article'))"` to generate `agents_growth.png`.
5. Report the output path and a brief summary of what was generated.

## Steps

```bash
# Step 1 — check Ollama
ollama list | grep qwen3

# Step 2 — run the crew
uv run python -m agent_ai.crew.run

# Step 3 — generate graph (if not done by run.py already)
uv run python -c "
from pathlib import Path
from agent_ai.visuals.graph import GraphGenerator
out = GraphGenerator().generate(Path('results/article'))
print('Graph saved to:', out)
"
```

After running, report:
- Path to `results/article/article.md`
- Word count of the article
- Whether all 8 required elements are detected (scan the Markdown for: cover block, `## `, Hebrew characters, Markdown table, `<!-- GRAPH:`, `<!-- IMAGE:`, `$$`, bibliography section)
- Path to `results/article/agents_growth.png`

If the run fails, show the last 50 lines of output and suggest the most likely fix.
