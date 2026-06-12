"""CrewAI-compatible web search tool."""

from __future__ import annotations

from crewai.tools import BaseTool
from ddgs import DDGS
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    """Input accepted by the web search tool."""

    query: str = Field(description="Search query")


class DuckDuckGoSearchTool(BaseTool):
    """Search the web through DDGS and return concise source records."""

    name: str = "DuckDuckGo web search"
    description: str = "Search the web for current sources and return titles, URLs, and summaries."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        results = DDGS().text(query, max_results=5)
        return "\n\n".join(
            f"Title: {item.get('title', '')}\nURL: {item.get('href', '')}\nSummary: {item.get('body', '')}"
            for item in results
        )
