# PRD - Six-Agent Section Workflow

## Goal

Generate a validated academic PDF by approving research once and writing the article one
section at a time. Persist every transition so interrupted runs resume without regenerating
approved work.

## Agents and Control Flow

| Agent | Responsibility |
|---|---|
| Researcher | Research package, sources, outline, section contracts, visual specifications |
| Source Verifier | Source, outline, visual-provenance, and BiDi approval |
| Section Writer | One section or one requested rewrite |
| Article Editor | Section approval and progression control |
| LaTeX Formatter | Assemble approved sections into LuaLaTeX |
| Submission Validator | Final evidence-based readiness report |

```text
Researcher <-> Source Verifier
                    |
Section Writer <-> Article Editor
                    |
LaTeX Formatter -> graph insertion -> Submission Validator
                    |
LuaLaTeX compilation -> deterministic validation
```

## Bounded Loops

- Source Verifier can return research at most twice.
- Each section can be returned once.
- Total section returns are limited to `ceil(section_count * 0.33)`.
- A repeated rejection or exhausted total budget stops the run and records the reason.
- Submission Validator does not create another feedback loop.

## Contracts

The research package is JSON containing research Markdown, source registry, at least eight
ordered section specifications, and approved visual specifications. One section must be
named `Hebrew and English in AI Systems` and set `bidi_required=true`.

Section review decisions use `APPROVE` or `REWRITE`. Research decisions use `APPROVE` or
`REVISE`. Submission reports end with an explicit readiness `YES` or `NO`.

## Visuals

Supported academic artifacts are Python charts, tables, formulas, and TikZ diagrams.
Measured data requires source IDs. Unsupported data must be marked estimated. Python charts
are rendered deterministically after formatting and before submission-agent validation.

## BiDi

The dedicated bilingual section contains substantive Hebrew prose with embedded English
technical terms. The formatter uses `polyglossia`, `hebrew` environments, and
`\textenglish{...}`. Manual direction commands and Unicode BiDi controls are forbidden.

## Persistence

Planning, section drafts/reviews/approvals, approved visuals, assembled Markdown, LaTeX,
agent validation, PDF validation, and `run_state.json` are stored below `outputs/`.

## Acceptance Criteria

- `uv run agent-ai-article` preserves the existing CLI.
- Exactly six agent roles are invoked.
- Both feedback loops obey their limits.
- Approved sections are reused on resume.
- Only approved sections and visuals reach LaTeX.
- Submission `NO` stops before compilation.
- Ruff passes and full-source branch coverage remains at least 85%.
