"""End-to-end tests for the resumable workflow state machine."""

import json
from types import SimpleNamespace

from workflow.orchestrator import ArticleWorkflow
from workflow.runner import StageResult


class QueueRunner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def run(self, agent_name, description, expected_output):
        self.calls.append(agent_name)
        return StageResult(self.responses.pop(0))


def _config(tmp_path):
    return SimpleNamespace(
        topic="Topic",
        artifact_instructions="- chart",
        min_pages=15,
        min_visuals=3,
        min_words=4500,
        max_words=5000,
        output_root=tmp_path,
        output_research=tmp_path / "research",
        output_latex=tmp_path / "latex",
        output_pdf=tmp_path / "pdf",
        max_research_returns=2,
        editor_rejection_ratio=0.33,
    )


def _responses(package):
    responses = [json.dumps(package), '{"status":"APPROVE"}']
    hebrew = " ".join(["מערכת", "חכמה", "מאפשרת", "מחקר"] * 6)
    for section in package["sections"]:
        body = (
            f"## {section['title']}\n{hebrew} עם CrewAI ו Python [1]."
            if section["bidi_required"]
            else f"## {section['title']}\nGrounded section content [1]."
        )
        responses.extend([body, '{"status":"APPROVE"}'])
    responses.extend(
        [
            "\\documentclass{article}\\begin{document}\\end{document}",
            "# Article Evaluation\n**Advisory summary:** Strong",
        ]
    )
    return responses


def test_full_workflow_uses_six_roles_and_persists(tmp_path, research_package):
    runner = QueueRunner(_responses(research_package))
    workflow = ArticleWorkflow(_config(tmp_path), runner)
    result = workflow.run()
    assert result == tmp_path / "pdf" / "article.pdf"
    assert runner.calls[:2] == ["researcher", "source_verifier"]
    assert runner.calls.count("writer") == 8
    assert runner.calls.count("article_editor") == 8
    assert runner.calls[-2:] == ["latex_formatter", "submission_validator"]
    state = json.loads((tmp_path / "run_state.json").read_text(encoding="utf-8"))
    assert state["phase"] == "complete"
    assert len(state["approved_sections"]) == 8
    assert (tmp_path / "assembled" / "article.md").exists()


def test_resume_skips_research_and_approved_sections(tmp_path, research_package):
    first = QueueRunner(_responses(research_package))
    ArticleWorkflow(_config(tmp_path), first).run()
    resumed = QueueRunner(
        [
            "\\documentclass{article}\\begin{document}\\end{document}",
            "# Article Evaluation\n**Advisory summary:** Strong",
        ]
    )
    ArticleWorkflow(_config(tmp_path), resumed).run()
    assert resumed.calls == ["latex_formatter", "submission_validator"]


def test_negative_submission_evaluation_does_not_block_run(tmp_path, research_package):
    responses = _responses(research_package)
    responses[-1] = "**Advisory summary:** Weak\n\nCritical weaknesses remain."
    workflow = ArticleWorkflow(_config(tmp_path), QueueRunner(responses))
    result = workflow.run()
    assert result == tmp_path / "pdf" / "article.pdf"
    state = json.loads((tmp_path / "run_state.json").read_text(encoding="utf-8"))
    assert state["phase"] == "complete"
    report = (tmp_path / "pdf" / "agent_validation.md").read_text(encoding="utf-8")
    assert report == "**Advisory summary:** Weak\n\nCritical weaknesses remain."
