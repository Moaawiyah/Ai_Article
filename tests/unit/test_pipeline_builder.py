"""Tests for six-agent workflow construction."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pipeline import build_workflow


def test_build_workflow_wires_runner_and_storage(tmp_path):
    cfg = SimpleNamespace(
        topic="Topic",
        output_dirs=[tmp_path],
        log_level="INFO",
        log_dir=tmp_path,
        log_file="app.log",
        build_llm=MagicMock(return_value="llm"),
        output_root=tmp_path,
    )
    gatekeeper = MagicMock()
    with (
        patch("pipeline.ensure_output_dirs") as ensure,
        patch("pipeline.configure_logger") as configure,
        patch("pipeline.CrewStageRunner") as runner_cls,
        patch("pipeline.ArticleWorkflow") as workflow_cls,
    ):
        workflow, returned = build_workflow(gatekeeper, cfg)
    assert workflow is workflow_cls.return_value
    assert returned is cfg
    ensure.assert_called_once_with(cfg.output_dirs)
    runner_cls.assert_called_once_with("llm", gatekeeper)
    configure.assert_called_once()
