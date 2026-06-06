"""Logging helpers for the article pipeline."""

import logging


def configure_logger(level: str = "INFO") -> logging.Logger:
    """Configure and return the pipeline logger."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger("article_pipeline")
