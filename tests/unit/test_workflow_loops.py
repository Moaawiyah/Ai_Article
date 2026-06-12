"""Tests for the two bounded agent feedback loops."""

import json
from types import SimpleNamespace

import pytest

from workflow.models import SectionSpec, WorkflowState
from workflow.research_loop import run_research_loop
from workflow.runner import StageResult
from workflow.section_loop import run_section
from workflow.storage import WorkflowStorage


class FakeRunner:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def run(self, agent_name, description, expected_output):
        self.calls.append(agent_name)
        return StageResult(next(self.responses))


def test_research_loop_revises_then_approves(tmp_path, research_package):
    package = json.dumps(research_package)
    runner = FakeRunner(
        [
            package,
            '{"status":"REVISE","issues":["source"],"required_changes":["fix"]}',
            package,
            '{"status":"APPROVE","evidence":["ok"]}',
        ]
    )
    storage = WorkflowStorage(tmp_path)
    storage.ensure_dirs()
    state = WorkflowState(topic="Topic")
    cfg = SimpleNamespace(
        artifact_instructions="- chart",
        min_pages=15,
        min_visuals=3,
        min_words=4500,
        max_words=5000,
    )
    _, sections, _ = run_research_loop(runner, cfg, storage, state, 2)
    assert len(sections) == 8
    assert state.research_returns == 1
    assert runner.calls == ["researcher", "source_verifier"] * 2


def test_research_loop_stops_after_two_returns(tmp_path, research_package):
    package = json.dumps(research_package)
    reject = '{"status":"REVISE","issues":["bad"]}'
    runner = FakeRunner([package, reject, package, reject, package, reject])
    storage = WorkflowStorage(tmp_path)
    storage.ensure_dirs()
    with pytest.raises(ValueError, match="allowed verifier"):
        run_research_loop(
            runner,
            SimpleNamespace(
                artifact_instructions="",
                min_pages=15,
                min_visuals=3,
                min_words=4500,
                max_words=5000,
            ),
            storage,
            WorkflowState(topic="T"),
            2,
        )


def test_section_loop_allows_one_rewrite(tmp_path):
    runner = FakeRunner(
        [
            "## Section\nFirst draft with [1].",
            '{"status":"REWRITE","required_changes":["deepen"]}',
            "## Section\nImproved draft with evidence [1].",
            '{"status":"APPROVE"}',
        ]
    )
    storage = WorkflowStorage(tmp_path)
    storage.ensure_dirs()
    state = WorkflowState(topic="T", editor_rejection_budget=1)
    spec = SectionSpec("section", "Section", 1, 100, ["topic"], ["ref1"])
    text, _ = run_section(runner, spec, "research", [], "", storage, state)
    assert "Improved" in text
    assert state.editor_rejections_used == 1
    assert (storage.section_dir(spec) / "approved.md").exists()


def test_section_loop_stops_on_second_rejection(tmp_path):
    runner = FakeRunner(
        [
            "## Section\nDraft [1].",
            '{"status":"REWRITE"}',
            "## Section\nStill bad [1].",
            '{"status":"REWRITE"}',
        ]
    )
    storage = WorkflowStorage(tmp_path)
    storage.ensure_dirs()
    state = WorkflowState(topic="T", editor_rejection_budget=2)
    spec = SectionSpec("section", "Section", 1, 100, [], [])
    with pytest.raises(ValueError, match="already returned"):
        run_section(runner, spec, "", [], "", storage, state)
