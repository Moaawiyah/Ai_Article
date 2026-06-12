"""Tests for isolated one-agent CrewAI execution."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from workflow.runner import CrewStageRunner


def test_stage_runner_builds_one_agent_crew():
    gatekeeper = MagicMock()
    crew_result = SimpleNamespace(raw="output", token_usage="usage")
    gatekeeper.execute.return_value = crew_result
    with (
        patch("workflow.runner.build_agent", return_value="agent") as build_agent,
        patch("workflow.runner.Task", return_value="task") as task_cls,
        patch("workflow.runner.Crew") as crew_cls,
    ):
        crew_cls.return_value.kickoff = MagicMock()
        result = CrewStageRunner("llm", gatekeeper).run("writer", "do", "markdown")
    build_agent.assert_called_once_with("writer", "llm")
    task_cls.assert_called_once()
    gatekeeper.execute.assert_called_once_with(crew_cls.return_value.kickoff)
    assert result.text == "output"
    assert result.token_usage == "usage"


def test_stage_runner_enables_json_mode_for_structured_agents():
    llm = MagicMock()
    structured = object()
    llm.model_copy.return_value = structured
    gatekeeper = MagicMock()
    gatekeeper.execute.return_value = SimpleNamespace(raw='{"status":"ok"}')
    with patch("workflow.runner.build_agent", return_value="agent") as build_agent, patch(
        "workflow.runner.Task", return_value="task"
    ), patch("workflow.runner.Crew"):
        CrewStageRunner(llm, gatekeeper).run("researcher", "do", "json")
    llm.model_copy.assert_called_once_with(
        update={"response_format": {"type": "json_object"}}
    )
    build_agent.assert_called_once_with("researcher", structured)


def test_stage_runner_aggregates_token_usage():
    usage = SimpleNamespace(
        prompt_tokens=10,
        cached_prompt_tokens=2,
        completion_tokens=5,
        total_tokens=17,
    )
    gatekeeper = MagicMock(
        return_value=None,
    )
    gatekeeper.execute.return_value = SimpleNamespace(raw="x", token_usage=usage)
    with patch("workflow.runner.build_agent", return_value="agent"), patch(
        "workflow.runner.Task", return_value="task"
    ), patch("workflow.runner.Crew"):
        runner = CrewStageRunner("llm", gatekeeper)
        runner.run("writer", "do", "markdown")
        runner.run("writer", "do", "markdown")
    assert runner.token_usage.prompt_tokens == 20
    assert runner.token_usage.total_tokens == 34
