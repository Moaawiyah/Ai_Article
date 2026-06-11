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
    """generate_article runs the crew via the gatekeeper and returns the PDF path."""
    mock_crew = MagicMock()
    mock_cfg = SimpleNamespace(topic="Default Topic", output_pdf=tmp_path)
    with patch("pipeline.build_crew", return_value=(mock_crew, mock_cfg)), \
         patch("pipeline_steps.print_token_usage"), \
         patch("pipeline_steps.graph_step"), \
         patch("pipeline_steps.compile_step"), \
         patch("pipeline_steps.validate_step"), \
         patch.object(sdk._gatekeeper, "execute", wraps=sdk._gatekeeper.execute) as spy:
        pdf = sdk.generate_article(topic="My Topic")

    assert pdf == tmp_path / "article.pdf"
    mock_crew.kickoff.assert_called_once_with(inputs={"topic": "My Topic"})
    spy.assert_called_once()  # the crew run is routed through the gatekeeper (§5.1)


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
