# PRD — LLM-Driven Graph Specification & Rendering

**Version:** 1.00
**Owners:**
- `src/agent_ai/utils/graph_spec.py` — LLM call that produces the JSON spec
- `src/agent_ai/utils/graph_fallback.py` — deterministic fallback profiles
- `src/agent_ai/utils/graph_generator.py` — matplotlib rendering

## 1. Goal

Produce a publication-grade performance figure (`benchmark.png`) for the article
that compares the main architecture against two legacy/comparative
architectures. The figure must be injected into the `Evaluation` section of
`article.tex`.

## 2. Background

The assignment (§13.1) requires at least one Python-generated graph in the
article. To keep the figure topic-relevant, an LLM call extracts realistic
performance parameters from the research brief and emits a structured JSON
spec; the renderer then draws the CDF and FCT curves.

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| F-01 | Read `outputs/research/research_brief.md` (truncated to 5 KB). |
| F-02 | Call the configured LLM (`config.yaml::llm`) and parse JSON. |
| F-03 | Validate the schema (`main`, `arch_a`, `arch_b`, each with 5 fields). |
| F-04 | On any error (LLM unavailable, empty response, malformed JSON, schema mismatch) → fall back to `_FALLBACK` profile, but **rename** the three architectures using names extracted from the brief. |
| F-05 | Save the spec to `outputs/assets/graph_spec.json` for inspection. |
| F-06 | Render a two-panel figure: left = CDF of bottleneck queue length, right = mean FCT vs. network load. |
| F-07 | Save the figure to `outputs/latex/benchmark.png` (300 DPI). |

## 4. Inputs / Outputs / Setup

- **Input:** `brief_path: Path`, `cfg: PipelineConfig`, `spec_out: Path | None`.
- **Output:** `dict` with shape `{"main": {...}, "arch_a": {...}, "arch_b": {...}}`.
- **Setup:** `litellm` installed; provider creds set via env var per provider.

## 5. Algorithm

```
1. If litellm missing or brief missing → return _FALLBACK.
2. Read brief (truncated 5 KB) → format the prompt.
3. Call litellm.completion(model, messages, max_tokens=2000, temperature=0.1).
4. Strip ``` fences, regex-extract the first {...} block → json.loads.
5. Validate keys + fields. On failure → fallback with brief-extracted names.
6. Persist spec_out (if provided).
7. Return the validated spec.
```

## 6. Edge Cases

| Case | Handling |
|------|----------|
| `litellm` not installed | Use `_FALLBACK`. |
| Brief file missing | Use `_FALLBACK`. |
| LLM returns empty string | Use `_FALLBACK` + brief-extracted names. |
| LLM returns JSON wrapped in fences | Strip fences + regex-extract. |
| Schema validation fails | Use `_FALLBACK` + brief-extracted names. |
| Brief parse fails to find names | Use literal `"Architecture A"` / `"Architecture B"`. |

## 7. JSON Schema

```json
{
  "main":   {"name": "<≤15 chars>", "median_queue": int, "p95_queue": int,
             "base_fct_ms": float, "fct_slope": float},
  "arch_a": { … same … },
  "arch_b": { … same … }
}
```

## 8. Constraints

- Files ≤ 150 LoC each.
- No hard-coded API keys — pulled from env vars per provider (`ZHIPUAI_API_KEY`,
  `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`).
- The pipeline must **never** crash on graph generation — fallback path
  guarantees a usable spec.

## 9. Acceptance Criteria

- For a well-formed research brief with two named architectures, the LLM path
  produces a spec whose `main.name` matches the paper subject.
- For a broken/empty brief, `_FALLBACK` is returned and `benchmark.png` still
  renders.
- The rendered figure shows three visually distinct curves on each panel.
- File `graph_spec.json` exists after every run.

## 10. Tests

- Unit: mock `litellm.completion` to return valid + invalid JSON; assert
  fallback behaviour.
- Unit: feed a fixture brief into `_extract_arch_names` and assert the parsed
  trio.
- Integration (skipped without litellm + provider keys): real LLM call,
  schema check.
