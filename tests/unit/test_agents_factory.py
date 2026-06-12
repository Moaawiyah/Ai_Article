"""Unit tests for agents.factory.build_agent."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.factory import build_agent


def _stub_skill():
    return SimpleNamespace(
        name="researcher",
        role="Senior Researcher",
        description="Research the topic in depth.",
        version="1.0.0",
        body="You are a careful, citation-driven researcher.",
    )


def test_build_agent_maps_skill_fields_to_agent():
    skill = _stub_skill()
    with patch("agents.factory.load_skill", return_value=skill) as mock_load, patch(
        "agents.factory.Agent"
    ) as mock_agent:
        mock_agent.return_value = MagicMock()
        result = build_agent("researcher")

    mock_load.assert_called_once_with("researcher")
    _, kwargs = mock_agent.call_args
    assert kwargs["role"] == skill.role
    assert kwargs["goal"] == skill.description
    assert kwargs["backstory"] == skill.body
    assert kwargs["allow_delegation"] is False
    assert kwargs["verbose"] is True
    assert kwargs["llm"] is None
    assert result is mock_agent.return_value


def test_build_agent_passes_llm_through():
    skill = _stub_skill()
    sentinel_llm = object()
    with patch("agents.factory.load_skill", return_value=skill), patch(
        "agents.factory.Agent"
    ) as mock_agent:
        build_agent("writer", llm=sentinel_llm)

    _, kwargs = mock_agent.call_args
    assert kwargs["llm"] is sentinel_llm


def test_build_agent_propagates_loader_error():
    with patch(
        "agents.factory.load_skill", side_effect=FileNotFoundError("no skill")
    ), patch("agents.factory.Agent") as mock_agent:
        try:
            build_agent("missing")
            raised = False
        except FileNotFoundError:
            raised = True

    assert raised
    mock_agent.assert_not_called()
