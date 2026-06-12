"""Immutable project constants (mathematical/physical values and Enum members only)."""

from enum import Enum

DEFAULT_BATCH_SIZE = 100
MAX_FILE_SIZE_MB = 50


class ProcessingMode(Enum):
    """Document-processing speed/quality trade-off mode."""

    FAST = "fast"
    ACCURATE = "accurate"


class SupportedFormat(Enum):
    """File extensions accepted by the document processor."""

    PDF = ".pdf"
    DOCX = ".docx"
    PPTX = ".pptx"
    XLSX = ".xlsx"
    HTML = ".html"
    TXT = ".txt"
    MD = ".md"
