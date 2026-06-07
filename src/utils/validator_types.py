"""Data types for the programmatic LaTeX validator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CheckResult:
    """Outcome of a single requirement check."""
    name: str
    passed: bool
    evidence: str
    fix: str = ""

    def as_markdown(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        lines = [f"### {self.name}", f"**Status:** {status}", f"**Evidence:** {self.evidence}"]
        if not self.passed and self.fix:
            lines.append(f"**Fix:** {self.fix}")
        return "\n".join(lines)


@dataclass
class ValidationReport:
    """Collection of all check results for one pipeline run."""
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed

    @property
    def all_passed(self) -> bool:
        return self.failed == 0

    def as_markdown(self, tex_path: Path, pdf_path: Path, log_path: Path) -> str:
        lines = [
            "# Validation Report", "",
            "| File | Path |", "|---|---|",
            f"| article.tex | `{tex_path}` |",
            f"| article.pdf | `{pdf_path}` |",
            f"| compile log | `{log_path}` |", "",
            f"**Result: {self.passed}/{len(self.checks)} checks passed**", "",
        ]
        if self.all_passed:
            lines.append("🟢 **All requirements satisfied. Ready for submission.**")
        else:
            lines.append(f"🔴 **{self.failed} requirement(s) failed. See details below.**")
        lines += ["", "---", ""]
        for check in self.checks:
            lines.append(check.as_markdown())
            lines.append("")
        return "\n".join(lines)
