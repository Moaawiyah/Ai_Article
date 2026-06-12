"""Unit tests for utils.logger."""

from __future__ import annotations

import logging

import pytest

from utils.logger import (
    _LOGGER_NAME,
    configure_logger,
    get_logger,
    timed_stage,
)


@pytest.fixture()
def clean_logger():
    """Detach all handlers from the pipeline logger before and after each test."""
    logger = logging.getLogger(_LOGGER_NAME)
    saved = logger.handlers[:]
    logger.handlers.clear()
    yield logger
    logger.handlers.clear()
    logger.handlers.extend(saved)


def test_configure_logger_creates_log_dir_and_file(tmp_path, clean_logger):
    log_dir = tmp_path / "logs"
    logger = configure_logger(level="DEBUG", log_dir=log_dir, log_file="run.log")

    assert log_dir.is_dir()
    assert (log_dir / "run.log").exists()
    assert logger.name == _LOGGER_NAME
    assert logger.level == logging.DEBUG


def test_configure_logger_adds_console_and_file_handlers(tmp_path, clean_logger):
    logger = configure_logger(log_dir=tmp_path)

    handler_types = {type(h) for h in logger.handlers}
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types
    assert len(logger.handlers) == 2


def test_configure_logger_console_level_follows_level_arg(tmp_path, clean_logger):
    logger = configure_logger(level="WARNING", log_dir=tmp_path)

    console = next(
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
    )
    file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
    assert console.level == logging.WARNING
    assert file_handler.level == logging.DEBUG


def test_configure_logger_invalid_level_falls_back_to_info(tmp_path, clean_logger):
    logger = configure_logger(level="NOPE", log_dir=tmp_path)

    console = next(
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
    )
    assert console.level == logging.INFO


def test_configure_logger_is_idempotent(tmp_path, clean_logger):
    first = configure_logger(log_dir=tmp_path)
    count_after_first = len(first.handlers)
    second = configure_logger(log_dir=tmp_path)

    assert first is second
    assert len(second.handlers) == count_after_first  # no duplicate handlers


def test_get_logger_returns_child_namespace():
    child = get_logger("research")
    assert child.name == f"{_LOGGER_NAME}.research"


def test_get_logger_without_name_returns_root_namespace():
    root = get_logger()
    assert root.name == _LOGGER_NAME


def test_timed_stage_logs_start_and_end(caplog):
    logger = logging.getLogger(f"{_LOGGER_NAME}.timed")
    logger.propagate = True
    with caplog.at_level(logging.INFO, logger=logger.name), timed_stage(logger, "Writer"):
        pass

    messages = [r.getMessage() for r in caplog.records]
    assert any("STAGE START" in m and "Writer" in m for m in messages)
    assert any("STAGE END" in m and "Writer" in m for m in messages)


def test_timed_stage_logs_output_file(caplog):
    logger = logging.getLogger(f"{_LOGGER_NAME}.timed_out")
    logger.propagate = True
    with caplog.at_level(logging.INFO, logger=logger.name), timed_stage(
        logger, "Latex", output_file="outputs/article.tex"
    ):
        pass

    messages = [r.getMessage() for r in caplog.records]
    assert any("outputs/article.tex" in m for m in messages)


def test_timed_stage_no_output_file_skips_file_log(caplog):
    logger = logging.getLogger(f"{_LOGGER_NAME}.timed_nofile")
    logger.propagate = True
    with caplog.at_level(logging.INFO, logger=logger.name), timed_stage(logger, "Research"):
        pass

    messages = [r.getMessage() for r in caplog.records]
    assert not any("→ file:" in m for m in messages)


def test_timed_stage_logs_error_and_reraises(caplog):
    logger = logging.getLogger(f"{_LOGGER_NAME}.timed_err")
    logger.propagate = True
    with caplog.at_level(logging.ERROR, logger=logger.name), pytest.raises(
        ValueError, match="boom"
    ), timed_stage(logger, "Failing"):
        raise ValueError("boom")

    error_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert any("STAGE ERROR" in m and "ValueError" in m and "boom" in m for m in error_messages)
