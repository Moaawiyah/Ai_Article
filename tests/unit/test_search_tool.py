"""Tests for the CrewAI-compatible search adapter."""

from unittest.mock import patch

from crewai.tools import BaseTool

from agents.search_tool import DuckDuckGoSearchTool


def test_search_tool_is_crewai_tool():
    assert isinstance(DuckDuckGoSearchTool(), BaseTool)


def test_search_tool_formats_results():
    records = [{"title": "Paper", "href": "https://example.test", "body": "Summary"}]
    with patch("agents.search_tool.DDGS") as ddgs:
        ddgs.return_value.text.return_value = records
        result = DuckDuckGoSearchTool().run(query="federated learning")
    assert "Title: Paper" in result
    assert "URL: https://example.test" in result
