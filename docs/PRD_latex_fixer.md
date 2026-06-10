# PRD — LaTeX Post-Processor

**Version:** 1.00
**Owners:**
- `src/agent_ai/utils/tex_fixer.py` — top-level `strip_tex_fences()` driver
- `src/agent_ai/utils/tex_syntax.py` — bracket/citation/text-mode fixes
- `src/agent_ai/utils/tex_tikz.py` — TikZ node + reserved-key fixes
- `src/agent_ai/utils/tex_tables.py` — table float wrapping + column specs
- `src/agent_ai/utils/tex_hebrew.py` — Hebrew/Latin LTR–RTL bridging

## 1. Goal

Take the raw `.tex` source emitted by the LaTeX Formatter agent and
deterministically transform it into a LuaLaTeX-compilable document, repairing
the predictable mistakes LLMs make when generating LaTeX.

## 2. Background

LLM output is not LaTeX-clean: it adds markdown fences, omits `polyglossia`
setup, generates bare `p` column specs, drops `\texthebrew{…}` wrappers, and
introduces stray `_` / `&` in text mode. Rather than make the agent prompt ever
longer (which degrades), we apply a deterministic post-pass.

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| F-01 | Strip leading/trailing markdown fences (```` ```latex … ``` ````). |
| F-02 | Repair empty `\pagestyle{}` / `\thispagestyle{}` / `\documentclass{}`. |
| F-03 | Move `fancyhdr` setup from preamble to after `\begin{document}`. |
| F-04 | Force `\setlength{\headheight}{15pt}` when `fancyhdr` is loaded. |
| F-05 | Wrap every `tabular` in `\adjustbox{max width=\textwidth}{…}`. |
| F-06 | Convert bare `p` / `m` / `b` column specs to `p{3.5cm}` for wrap-safety. |
| F-07 | Wrap text-mode `^{…}` superscripts as `$…^{…}$`. |
| F-08 | Escape stray `_`, `&`, `#` outside protected regions. |
| F-09 | Convert leftover `[N]` citation markers to `\cite{refN}`. |
| F-10 | Detect Hebrew characters → inject `polyglossia` + `\texthebrew{…}` wrappers. |
| F-11 | Inside Hebrew blocks, wrap Latin runs in `\textenglish{…}` (BiDi). |
| F-12 | Rename user TikZ styles colliding with reserved `pgf` keys (e.g. `node` → `nodenode`). |
| F-13 | Add `align=center` to TikZ nodes with `\\` line breaks. |

## 4. Inputs / Outputs / Setup

- **Input:** `tex_path: Path`, `topic: str` (used for the page-header text).
- **Output:** overwrites the file in place with the repaired source.
- **Setup:** no external deps — pure stdlib `re`.

## 5. Protected Regions

The fixer must **never** touch the contents of:

- inline math `$…$`, display math `$$…$$`, `\[ … \]`, `\( … \)`
- `equation`, `align`, `aligned` environments
- `tikzpicture`, `tabular`
- `verbatim`, `lstlisting`
- `thebibliography`
- the `hebrew` environment (handled by a separate Hebrew pass)

A `_PROTECTED` regex skips these segments during text-mode fixes.

## 6. Constraints

- Each file ≤ 150 LoC (guideline §3.2). The original 365-line `tex_fixer.py` is
  split across `tex_syntax.py`, `tex_tikz.py`, `tex_tables.py`, `tex_hebrew.py`.
- Idempotent — running the fixer twice produces the same output.
- Deterministic — no LLM calls, no randomness.

## 7. Acceptance Criteria

- A `.tex` wrapped in ```` ```latex … ``` ```` compiles after one pass.
- A `.tex` containing a Hebrew sentence renders RTL with embedded Latin
  acronyms in LTR.
- A `.tex` with `\begin{tabular}{lpl}` becomes `\begin{tabular}{lp{3.5cm}l}`.
- A `.tex` with a custom TikZ style named `node/.style={…}` is renamed to
  `nodenode/.style={…}` and every reference is updated.

## 8. Tests

- Unit: golden-file tests, one per fixer (`fix_bracket_syntax`,
  `fix_inline_citations`, `fix_text_mode_math`, `fix_tables`,
  `fix_tabular_colspec`, `fix_tikz_node_linebreaks`, `fix_tikz_reserved_styles`,
  `fix_hebrew_ltr`, `fix_hebrew_runs`).
- Integration: feed `outputs/latex/article.tex` through `strip_tex_fences`
  twice — second call must produce a byte-identical file (idempotence).
