"""Tests for agent, task, and crew construction."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from agents.factory import build_agent
from pipeline import build_crew
from tasks.latex_task import build_latex_task
from tasks.research_task import build_research_task
from tasks.review_task import build_review_task
from tasks.validation_task import build_validation_task
from tasks.writing_task import build_writing_task


def _config(tmp_path: Path):
    return SimpleNamespace(
        topic="Test Topic",
        output_root=tmp_path,
        output_research=tmp_path / "research",
        output_drafts=tmp_path / "drafts",
        output_reviewed=tmp_path / "reviewed",
        output_latex=tmp_path / "latex",
        output_pdf=tmp_path / "pdf",
        output_assets=tmp_path / "assets",
        output_dirs=[tmp_path / "research"],
        artifact_instructions="- graph",
        min_words=100,
        max_words=200,
        min_pages=2,
        language="english",
        log_level="INFO",
        log_dir=tmp_path / "logs",
        log_file="app.log",
        llm_provider="test",
        llm_model="model",
        build_llm=MagicMock(return_value="llm"),
    )


def test_build_agent_uses_skill():
    skill = SimpleNamespace(role="Researcher", description="Goal", body="Backstory")
    with patch("agents.factory.load_skill", return_value=skill), patch(
        "agents.factory.Agent"
    ) as agent_cls:
        result = build_agent("researcher", llm="llm")
    assert result is agent_cls.return_value
    agent_cls.assert_called_once_with(
        role="Researcher",
        goal="Goal",
        backstory="Backstory",
        llm="llm",
        allow_delegation=False,
        verbose=True,
    )


def test_task_builders_create_expected_outputs(tmp_path):
    cfg = _config(tmp_path)
    agent = MagicMock()
    previous = MagicMock()
    cases = [
        ("tasks.research_task.Task", build_research_task, (agent, cfg), "research_brief.md"),
        ("tasks.writing_task.Task", build_writing_task, (agent, cfg, previous), "draft.md"),
        ("tasks.review_task.Task", build_review_task, (agent, cfg, previous), "reviewed.md"),
        ("tasks.latex_task.Task", build_latex_task, (agent, cfg, previous), "article.tex"),
        (
            "tasks.validation_task.Task",
            build_validation_task,
            (agent, cfg, previous),
            "agent_validation.md",
        ),
    ]
    for target, builder, args, filename in cases:
        with patch(target) as task_cls:
            assert builder(*args) is task_cls.return_value
            assert task_cls.call_args.kwargs["output_file"].endswith(filename)


def test_build_crew_wires_five_agents_and_tasks(tmp_path):
    cfg = _config(tmp_path)
    agents = [MagicMock(name=f"agent-{i}") for i in range(5)]
    tasks = [MagicMock(name=f"task-{i}") for i in range(5)]
    with (
        patch("pipeline.ensure_output_dirs") as ensure_dirs,
        patch("pipeline.configure_logger") as configure_logger,
        patch("pipeline.build_agent", side_effect=agents) as agent_builder,
        patch("pipeline.build_research_task", return_value=tasks[0]),
        patch("pipeline.build_writing_task", return_value=tasks[1]),
        patch("pipeline.build_review_task", return_value=tasks[2]),
        patch("pipeline.build_latex_task", return_value=tasks[3]),
        patch("pipeline.build_validation_task", return_value=tasks[4]),
        patch("pipeline.Crew") as crew_cls,
    ):
        crew, returned_cfg = build_crew(cfg)
    assert crew is crew_cls.return_value
    assert returned_cfg is cfg
    ensure_dirs.assert_called_once_with(cfg.output_dirs)
    configure_logger.assert_called_once()
    assert agent_builder.call_count == 5
    assert crew_cls.call_args.kwargs["agents"] == agents
    assert crew_cls.call_args.kwargs["tasks"] == tasks
