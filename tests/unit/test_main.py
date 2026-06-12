"""Unit tests for the article CLI entry point in main.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from main import main


def test_main_passes_topic_to_sdk(capsys):
    mock_sdk = MagicMock()
    mock_sdk.generate_article.return_value = "outputs/pdf/article.pdf"
    with patch("main.AgentAISDK", return_value=mock_sdk), patch(
        "sys.argv", ["agent-ai-article", "--topic", "Networking"]
    ):
        main()

    mock_sdk.generate_article.assert_called_once_with(topic="Networking")
    out = capsys.readouterr().out
    assert "outputs/pdf/article.pdf" in out
    assert "Article PDF" in out


def test_main_defaults_topic_to_none(capsys):
    mock_sdk = MagicMock()
    mock_sdk.generate_article.return_value = "outputs/pdf/article.pdf"
    with patch("main.AgentAISDK", return_value=mock_sdk), patch(
        "sys.argv", ["agent-ai-article"]
    ):
        main()

    mock_sdk.generate_article.assert_called_once_with(topic=None)


def test_main_instantiates_sdk_once():
    mock_cls = MagicMock()
    mock_cls.return_value.generate_article.return_value = "x.pdf"
    with patch("main.AgentAISDK", mock_cls), patch("sys.argv", ["agent-ai-article"]):
        main()

    mock_cls.assert_called_once_with()
