"""Integration tests for AgentAISDK (no real API calls)."""

from unittest.mock import MagicMock, patch

import pytest

from agent_ai.sdk.sdk import AgentAISDK


@pytest.fixture()
def sdk(config_dir, monkeypatch):
    """AgentAISDK with mocked Anthropic client and valid config."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("sdk.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        instance = AgentAISDK(config_dir=config_dir)
        instance._client = mock_client
        yield instance


def test_get_version(sdk):
    from agent_ai.shared.version import VERSION

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
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(OSError, match="ANTHROPIC_API_KEY"):
        AgentAISDK(config_dir=config_dir)


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
