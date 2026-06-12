"""Integration tests for AgentAISDK (no real API calls)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from sdk.sdk import AgentAISDK


@pytest.fixture()
def sdk(config_dir, monkeypatch):
    """AgentAISDK with mocked Anthropic client and valid config."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("sdk.sdk.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        instance = AgentAISDK(config_dir=config_dir)
        instance._client = mock_client
        yield instance


def test_get_version(sdk):
    from shared.version import VERSION

    assert sdk.get_version() == VERSION


def test_query_document(sdk):
    mock_response = MagicMock()
    mock_response.content[0].text = "Answer from Claude"
    sdk._client.messages.create.return_value = mock_response

    answer = sdk.query_document("# Doc\nSome content", "What is this?")
    assert answer == "Answer from Claude"
    sdk._client.messages.create.assert_called_once()


def test_process_document_file_not_found(sdk):
    with pytest.raises(FileNotFoundError):
        sdk.process_document("/nonexistent/file.pdf")


def test_missing_api_key_raises(config_dir, monkeypatch):
    """The Anthropic client is created lazily, so the error surfaces on first use."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    sdk = AgentAISDK(config_dir=config_dir)
    with pytest.raises(OSError, match="ANTHROPIC_API_KEY"):
        sdk.query_document("doc", "q?")


def test_generate_article_routes_crew_through_gatekeeper(sdk, tmp_path):
    """generate_article runs the workflow then deterministic post-processing."""
    workflow = MagicMock()
    workflow.token_usage = None
    mock_cfg = SimpleNamespace(topic="Default Topic", output_pdf=tmp_path, llm_provider="default")
    with patch("shared.pipeline_config.PipelineConfig.load", return_value=mock_cfg), \
         patch("pipeline.build_workflow", return_value=(workflow, mock_cfg)), \
         patch("pipeline_steps.print_token_usage"), \
         patch("pipeline_steps.graph_step") as graph_step, \
         patch("pipeline_steps.compile_step"), \
         patch("pipeline_steps.validate_step"):
        workflow.run.side_effect = lambda topic, after_format: after_format()
        pdf = sdk.generate_article(topic="My Topic")

    assert pdf == tmp_path / "article.pdf"
    assert workflow.run.call_args.args[0] == "My Topic"
    graph_step.assert_called_once()


def test_process_document_success(sdk, tmp_path):
    """process_document returns Markdown string when markitdown succeeds."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello world")

    mock_result = MagicMock()
    mock_result.text_content = "# Hello world"
    with patch("markitdown.MarkItDown") as mock_md_cls:
        mock_md_cls.return_value.convert.return_value = mock_result
        result = sdk.process_document(test_file)

    assert result == "# Hello world"
