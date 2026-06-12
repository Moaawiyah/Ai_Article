"""Unit tests for pipeline.build_crew (5 agents + 5 tasks, sequential)."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import pipeline
from pipeline import build_crew


@pytest.fixture()
def cfg(tmp_path: Path) -> SimpleNamespace:
    """Minimal PipelineConfig stand-in with the attributes build_crew reads."""
    return SimpleNamespace(
        topic="Test Topic",
        llm_provider="ollama",
        llm_model="qwen3:14b",
        output_root=tmp_path / "outputs",
        output_dirs=[tmp_path / "outputs" / "research"],
        log_level="INFO",
        log_dir=tmp_path / "logs",
        log_file="app.log",
        build_llm=MagicMock(return_value=MagicMock(name="llm")),
    )


def _patch_collaborators(stack: ExitStack, **overrides) -> dict:
    """Patch every collaborator build_crew imports into pipeline's namespace."""
    targets = {
        "ensure_output_dirs": patch("pipeline.ensure_output_dirs"),
        "configure_logger": patch("pipeline.configure_logger", return_value=MagicMock()),
        "build_agent": patch("pipeline.build_agent", side_effect=lambda *_: MagicMock()),
        "build_research_task": patch("pipeline.build_research_task", return_value=MagicMock()),
        "build_writing_task": patch("pipeline.build_writing_task", return_value=MagicMock()),
        "build_review_task": patch("pipeline.build_review_task", return_value=MagicMock()),
        "build_latex_task": patch("pipeline.build_latex_task", return_value=MagicMock()),
        "build_validation_task": patch("pipeline.build_validation_task", return_value=MagicMock()),
        "Crew": patch("pipeline.Crew"),
    }
    targets.update(overrides)
    return {name: stack.enter_context(p) for name, p in targets.items()}


def test_build_crew_uses_provided_cfg(cfg):
    with ExitStack() as stack:
        mocks = _patch_collaborators(stack)
        crew, returned_cfg = build_crew(cfg)

    assert returned_cfg is cfg
    cfg.build_llm.assert_called_once()
    mock_crew = mocks["Crew"]
    mock_crew.assert_called_once()
    _, kwargs = mock_crew.call_args
    assert len(kwargs["agents"]) == 5
    assert len(kwargs["tasks"]) == 5
    assert kwargs["process"] is pipeline.Process.sequential
    assert crew is mock_crew.return_value


def test_build_crew_loads_cfg_when_none(cfg):
    with ExitStack() as stack:
        load_patch = stack.enter_context(
            patch.object(pipeline.PipelineConfig, "load", return_value=cfg)
        )
        _patch_collaborators(stack)
        _, returned_cfg = build_crew(None)

    load_patch.assert_called_once()
    assert returned_cfg is cfg


def test_build_crew_builds_five_distinct_agent_roles(cfg):
    with ExitStack() as stack:
        mocks = _patch_collaborators(stack)
        build_crew(cfg)

    roles = [call.args[0] for call in mocks["build_agent"].call_args_list]
    assert roles == ["researcher", "writer", "reviewer", "latex_formatter", "pdf_validator"]


def test_build_crew_passes_research_task_to_writing(cfg):
    research_sentinel = MagicMock(name="research_task")
    with ExitStack() as stack:
        mocks = _patch_collaborators(
            stack,
            build_research_task=patch(
                "pipeline.build_research_task", return_value=research_sentinel
            ),
        )
        build_crew(cfg)

    # writing task is built from (writer_agent, cfg, research_task)
    assert mocks["build_writing_task"].call_args.args[-1] is research_sentinel
