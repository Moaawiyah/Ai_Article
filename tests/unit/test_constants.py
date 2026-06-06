"""Unit tests for constants module."""

from agent_ai.constants import DEFAULT_BATCH_SIZE, MAX_FILE_SIZE_MB, ProcessingMode, SupportedFormat


def test_default_batch_size():
    assert DEFAULT_BATCH_SIZE == 100


def test_max_file_size():
    assert MAX_FILE_SIZE_MB > 0


def test_processing_modes():
    assert ProcessingMode.FAST.value == "fast"
    assert ProcessingMode.ACCURATE.value == "accurate"


def test_supported_formats_include_pdf():
    assert SupportedFormat.PDF.value == ".pdf"


def test_all_formats_have_dot_prefix():
    for fmt in SupportedFormat:
        assert fmt.value.startswith(".")
