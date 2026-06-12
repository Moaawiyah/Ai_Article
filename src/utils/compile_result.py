"""Outcome dataclass for LuaLaTeX compilation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompileResult:
    """Outcome of a LuaLaTeX compilation attempt."""

    success: bool
    pdf_path: Path | None
    tex_path: Path
    log_path: Path
    elapsed: float
    error_summary: str

    def __str__(self) -> str:
        """One-line human summary of the compile outcome."""
        if self.success:
            return f"[PDF OK]  {self.pdf_path}  ({self.elapsed:.1f}s)"
        return (
            f"[PDF FAIL]  {self.error_summary}\n"
            f"  .tex file : {self.tex_path}\n"
            f"  log file  : {self.log_path}"
        )
