"""Structured logging for the article pipeline.

Sets up simultaneous console (INFO+) and file (DEBUG+) handlers.
Provides a timed_stage() context manager that logs start, end, and
elapsed time for each pipeline stage.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from pathlib import Path

_LOGGER_NAME = "article_pipeline"
_FMT_CONSOLE = "%(asctime)s  %(levelname)-8s  %(message)s"
_FMT_FILE    = "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s"
_DATE_FMT    = "%Y-%m-%d %H:%M:%S"


def configure_logger(
    level: str = "INFO",
    log_dir: Path = Path("logs"),
    log_file: str = "app.log",
) -> logging.Logger:
    """Configure the pipeline logger with console and file handlers.

    Safe to call multiple times — handlers are only added once.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_file

    root_logger = logging.getLogger(_LOGGER_NAME)
    if root_logger.handlers:
        return root_logger  # already configured

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(logging.DEBUG)  # capture everything; handlers filter

    # Console handler — INFO and above
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)
    ch.setFormatter(logging.Formatter(_FMT_CONSOLE, datefmt=_DATE_FMT))

    # File handler — DEBUG and above (full detail)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_FMT_FILE, datefmt=_DATE_FMT))

    root_logger.addHandler(ch)
    root_logger.addHandler(fh)

    root_logger.info("Logger ready — writing to %s", log_path.resolve())
    return root_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a child logger under the pipeline namespace."""
    return logging.getLogger(f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME)


@contextmanager
def timed_stage(logger: logging.Logger, stage: str, output_file: str | None = None):
    """Context manager that logs start, end, elapsed time, and output path.

    Usage:
        with timed_stage(logger, "Writer", "outputs/drafts/draft.md"):
            crew.kickoff(...)
    """
    logger.info("▶ STAGE START  — %s", stage)
    t0 = time.perf_counter()
    try:
        yield
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        logger.error(
            "✗ STAGE ERROR  — %s  (%.2fs)  %s: %s",
            stage, elapsed, type(exc).__name__, exc,
        )
        raise
    else:
        elapsed = time.perf_counter() - t0
        logger.info("■ STAGE END    — %s  (%.2fs)", stage, elapsed)
        if output_file:
            logger.info("  → file: %s", output_file)
