"""Tests for logging helpers and thin CLI adapters."""

import logging
from unittest.mock import MagicMock, patch

import pytest

import main as article_main
from sdk import sdk as sdk_module
from utils import logger as logger_module


def test_configure_logger_is_idempotent(tmp_path):
    named = logging.getLogger("article_pipeline")
    old_handlers = list(named.handlers)
    named.handlers.clear()
    try:
        first = logger_module.configure_logger("DEBUG", tmp_path, "test.log")
        second = logger_module.configure_logger("INFO", tmp_path, "test.log")
        assert first is second
        assert len(first.handlers) == 2
        assert (tmp_path / "test.log").exists()
    finally:
        for handler in named.handlers:
            handler.close()
        named.handlers[:] = old_handlers


def test_get_logger_returns_pipeline_child():
    assert logger_module.get_logger("child").name == "article_pipeline.child"
    assert logger_module.get_logger().name == "article_pipeline"


def test_timed_stage_logs_success_and_error(monkeypatch):
    log = MagicMock()
    times = iter((1.0, 2.5, 3.0, 4.0))
    monkeypatch.setattr(logger_module.time, "perf_counter", lambda: next(times))
    with logger_module.timed_stage(log, "ok", "out"):
        pass
    with pytest.raises(ValueError), logger_module.timed_stage(log, "bad"):
        raise ValueError("boom")
    assert log.info.call_count >= 3
    log.error.assert_called_once()


def test_article_cli_delegates_to_sdk(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["agent-ai-article", "--topic", "T"])
    with patch("main.AgentAISDK") as sdk_cls:
        sdk_cls.return_value.generate_article.return_value = "article.pdf"
        article_main.main()
    sdk_cls.return_value.generate_article.assert_called_once_with(topic="T")
    assert "article.pdf" in capsys.readouterr().out


def test_document_cli_delegates_to_sdk(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["agent-ai", "doc.pdf", "question"])
    with patch("sdk.sdk.AgentAISDK") as sdk_cls:
        sdk_cls.return_value.process_document.return_value = "markdown"
        sdk_cls.return_value.query_document.return_value = "answer"
        sdk_module.main()
    sdk_cls.return_value.query_document.assert_called_once_with("markdown", "question")
    assert "answer" in capsys.readouterr().out
