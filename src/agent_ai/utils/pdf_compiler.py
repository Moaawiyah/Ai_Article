"""LuaLaTeX PDF compiler utility.

Compiles a .tex file to PDF without crashing the caller on failure.
All subprocess output is captured and saved to a log file.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from agent_ai.utils.compile_result import CompileResult

_LUALATEX = shutil.which("lualatex") or "lualatex"
_BIBER    = shutil.which("biber") or "biber"
_COMPILE_LOG = Path("logs") / "latex_compile.log"


def compile_pdf(
    tex_path: Path,
    output_dir: Path,
    log_path: Path = _COMPILE_LOG,
) -> CompileResult:
    """Compile *tex_path* with LuaLaTeX, saving all output to *log_path*.

    Runs 3 passes plus a biber pass so TOC and cross-references resolve.
    Returns a CompileResult — never raises.
    """
    tex_path   = tex_path.resolve()
    output_dir = output_dir.resolve()
    log_path   = log_path.resolve()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not tex_path.exists():
        return CompileResult(
            success=False, pdf_path=None, tex_path=tex_path, log_path=log_path,
            elapsed=0.0, error_summary=f"Source file not found: {tex_path}",
        )

    cmd = [
        _LUALATEX,
        "--interaction=nonstopmode",
        "--halt-on-error",
        f"--output-directory={output_dir}",
        str(tex_path),
    ]

    t0 = time.perf_counter()
    all_output: list[str] = []
    error_summary = ""
    env_bibinputs = {"BIBINPUTS": str(tex_path.parent) + ":"}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_path.parent)
        all_output.append(f"\n{'='*60}\nPass 1/2\n{'='*60}\n" + result.stdout + result.stderr)
        if result.returncode != 0:
            error_summary = _extract_error(result.stdout + result.stderr)

        bcf = output_dir / tex_path.with_suffix(".bcf").name
        if not error_summary and bcf.exists():
            biber_env = {**os.environ, **env_bibinputs}
            biber_result = subprocess.run(
                [_BIBER, tex_path.stem],
                capture_output=True, text=True, cwd=output_dir, env=biber_env,
            )
            all_output.append(f"\n{'='*60}\nBiber\n{'='*60}\n"
                              + biber_result.stdout + biber_result.stderr)

        if not error_summary:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_path.parent)
            all_output.append(f"\n{'='*60}\nPass 2/3\n{'='*60}\n" + result.stdout + result.stderr)
            if result.returncode != 0:
                error_summary = _extract_error(result.stdout + result.stderr)

        if not error_summary:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_path.parent)
            all_output.append(f"\n{'='*60}\nPass 3/3\n{'='*60}\n" + result.stdout + result.stderr)
            if result.returncode != 0:
                error_summary = _extract_error(result.stdout + result.stderr)

    except FileNotFoundError:
        error_summary = "lualatex not found on PATH — install MiKTeX or TeX Live"
    except Exception as exc:
        error_summary = str(exc)

    elapsed = time.perf_counter() - t0

    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write(f"Compilation of: {tex_path}\n")
        fh.write(f"Command: {' '.join(cmd)}\n")
        fh.write("".join(all_output))

    pdf_candidate = output_dir / tex_path.with_suffix(".pdf").name
    success = not error_summary and pdf_candidate.exists()

    return CompileResult(
        success=success,
        pdf_path=pdf_candidate if success else None,
        tex_path=tex_path,
        log_path=log_path,
        elapsed=elapsed,
        error_summary=error_summary,
    )


def _extract_error(output: str) -> str:
    """Return the first LaTeX error line from compiler output."""
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("!"):
            return stripped
    lines = [ln for ln in output.splitlines() if ln.strip()]
    return lines[-1].strip() if lines else "Unknown compilation error"
