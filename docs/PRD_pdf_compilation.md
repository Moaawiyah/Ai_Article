# PRD — PDF Compilation Mechanism

**Version:** 1.00
**Owner:** `src/utils/pdf_compiler.py`

## 1. Goal

Convert `outputs/latex/article.tex` into `outputs/pdf/article.pdf` using
LuaLaTeX, with bibliography resolution, capturing all logs, and never crashing
the caller on compilation failure.

## 2. Background

The CrewAI pipeline emits LaTeX via the LaTeX Formatter agent. The output is
then post-processed by `tex_fixer.strip_tex_fences()` and handed to this
compiler. LuaLaTeX is mandated by §13 of the assignment because it offers
robust Hebrew/Unicode support through `polyglossia` + `fontspec`.

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| F-01 | Compile a `.tex` file with `lualatex --interaction=nonstopmode --halt-on-error`. |
| F-02 | Run **3 passes** so TOC and cross-references stabilise. |
| F-03 | Run `biber` between pass 1 and pass 2 if a `.bcf` file is produced. |
| F-04 | Capture **all** stdout + stderr from every pass to `logs/latex_compile.log`. |
| F-05 | Return a `CompileResult` dataclass — never raise on compilation failure. |
| F-06 | Surface the first `! ...` error line as `error_summary`. |

## 4. Inputs / Outputs / Setup

- **Input:** `tex_path: Path` (must exist), `output_dir: Path`, `log_path: Path`.
- **Output:** `CompileResult(success, pdf_path, tex_path, log_path, elapsed, error_summary)`.
- **Setup:** `lualatex` and `biber` must be on `PATH` (MiKTeX or TeX Live).

## 5. Algorithm

```
1. Resolve all paths; mkdir parents if missing.
2. If tex_path missing → return CompileResult(success=False, error_summary="…").
3. Pass 1: lualatex → capture output.
4. If pass 1 succeeded and .bcf exists → run biber.
5. Pass 2: lualatex (resolves bibliography).
6. Pass 3: lualatex (stabilises TOC page numbers after pass 2 shifts).
7. Write the full transcript to log_path.
8. Return CompileResult with pdf_path if the output PDF exists and no errors.
```

## 6. Edge Cases and Error Handling

| Case | Handling |
|------|----------|
| `lualatex` not on PATH | `error_summary = "lualatex not found on PATH — install MiKTeX or TeX Live"`. |
| `.tex` file does not exist | `error_summary = f"Source file not found: {tex_path}"`. |
| LaTeX error on pass N | Skip remaining passes; return `success=False`. |
| Biber fails | Still attempt passes 2-3 (warnings are acceptable). |
| Subprocess raises any other exception | Capture `str(exc)` as `error_summary`. |

## 7. Acceptance Criteria

- A well-formed `.tex` with `\bibliography{}` produces a non-zero-byte PDF.
- A `.tex` with a deliberate `\undefinedcmd` returns `success=False` and the
  first `! Undefined control sequence` line in `error_summary`.
- The compilation log always contains markers `Pass 1/2`, `Biber`, `Pass 2/3`,
  `Pass 3/3` (when reached).
- Elapsed time is recorded in seconds, accurate to 0.1 s.

## 8. Constraints

- File ≤ 150 LoC (per guideline §3.2). `CompileResult` is split into
  `src/utils/compile_result.py` to honour the limit.
- No business logic outside this module — callers go through the SDK.
- Subprocess calls capture output explicitly; no terminal noise leaks.

## 9. Tests

- Unit: mock `subprocess.run` to simulate success, failure, and `FileNotFoundError`.
- Integration: compile `tests/fixtures/minimal.tex` end-to-end (skipped when
  `lualatex` is not installed).
