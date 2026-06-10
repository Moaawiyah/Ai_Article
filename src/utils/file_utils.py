"""File-system helpers for pipeline outputs."""

from pathlib import Path


def ensure_output_dirs(paths: list[Path]) -> None:
    """Create output directories required by the pipeline."""
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
