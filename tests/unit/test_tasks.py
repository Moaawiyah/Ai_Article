"""Unit tests for the five task factories in tasks/*_task.py.

Each ``build_*_task`` is a pure factory that returns a ``crewai.Task``. We patch
the ``Task`` symbol inside each module so no real CrewAI Task (and no LLM) is
constructed, then assert on the kwargs handed to it. Both the
``hasattr``/``getattr`` present and fallback branches are exercised by passing a
rich config and a minimal config respectively.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from tasks.latex_task import build_latex_task
from tasks.research_task import build_research_task
from tasks.review_task import build_review_task
from tasks.validation_task import build_validation_task
from tasks.writing_task import build_writing_task


def _agent():
    return MagicMock(name="agent")


def _full_config(tmp: Path) -> SimpleNamespace:
    """Config with every optional attribute present (the hasattr/getattr branch)."""
    return SimpleNamespace(
        topic="HULA Load Balancing",
        artifact_instructions="- a TikZ diagram\n- a table",
        output_root=tmp,
        output_research=tmp / "research",
        output_drafts=tmp / "drafts",
        output_reviewed=tmp / "reviewed",
        output_latex=tmp / "latex",
        output_pdf=tmp / "pdf",
        min_words=4500,
        max_words=5000,
        min_pages=15,
        language="english",
    )


def _minimal_config(tmp: Path) -> SimpleNamespace:
    """Config with only output_root — forces every fallback branch."""
    return SimpleNamespace(output_root=tmp)


# --------------------------------------------------------------------------- #
# research_task
# --------------------------------------------------------------------------- #


def test_build_research_task_full_config(tmp_path):
    with patch("tasks.research_task.Task") as mock_task:
        build_research_task(_agent(), _full_config(tmp_path))

    _, kwargs = mock_task.call_args
    assert "HULA Load Balancing" in kwargs["description"]
    assert "a TikZ diagram" in kwargs["description"]
    assert kwargs["expected_output"]
    assert kwargs["output_file"] == str(tmp_path / "research" / "research_brief.md")


def test_build_research_task_fallback_config(tmp_path):
    with patch("tasks.research_task.Task") as mock_task:
        build_research_task(_agent(), _minimal_config(tmp_path))

    _, kwargs = mock_task.call_args
    assert "Unknown Topic" in kwargs["description"]
    # artifact_instructions missing -> empty string used, description still present
    assert kwargs["description"].strip()
    assert kwargs["output_file"] == str(tmp_path / "research" / "research_brief.md")


# --------------------------------------------------------------------------- #
# writing_task
# --------------------------------------------------------------------------- #


def test_build_writing_task_full_config(tmp_path):
    research = MagicMock(name="research_task")
    with patch("tasks.writing_task.Task") as mock_task:
        build_writing_task(_agent(), _full_config(tmp_path), research)

    _, kwargs = mock_task.call_args
    assert "4500-5000 words" in kwargs["description"]
    assert kwargs["context"] == [research]
    assert kwargs["output_file"] == str(tmp_path / "drafts" / "draft.md")
    assert kwargs["description"].strip()


def test_build_writing_task_fallback_defaults(tmp_path):
    research = MagicMock(name="research_task")
    with patch("tasks.writing_task.Task") as mock_task:
        build_writing_task(_agent(), _minimal_config(tmp_path), research)

    _, kwargs = mock_task.call_args
    # default min/max words 4500-5000 and default language english
    assert "4500-5000 words" in kwargs["description"]
    assert "english" in kwargs["description"]
    assert kwargs["output_file"] == str(tmp_path / "drafts" / "draft.md")


# --------------------------------------------------------------------------- #
# review_task
# --------------------------------------------------------------------------- #


def test_build_review_task_full_config(tmp_path):
    writing = MagicMock(name="writing_task")
    with patch("tasks.review_task.Task") as mock_task:
        build_review_task(_agent(), _full_config(tmp_path), writing)

    _, kwargs = mock_task.call_args
    assert kwargs["description"].strip()
    assert kwargs["expected_output"]
    assert kwargs["context"] == [writing]
    assert kwargs["output_file"] == str(tmp_path / "reviewed" / "reviewed.md")


def test_build_review_task_fallback_config(tmp_path):
    writing = MagicMock(name="writing_task")
    with patch("tasks.review_task.Task") as mock_task:
        build_review_task(_agent(), _minimal_config(tmp_path), writing)

    _, kwargs = mock_task.call_args
    assert kwargs["output_file"] == str(tmp_path / "reviewed" / "reviewed.md")


# --------------------------------------------------------------------------- #
# latex_task
# --------------------------------------------------------------------------- #


def test_build_latex_task_full_config(tmp_path):
    review = MagicMock(name="review_task")
    with patch("tasks.latex_task.Task") as mock_task:
        build_latex_task(_agent(), _full_config(tmp_path), review)

    _, kwargs = mock_task.call_args
    assert kwargs["description"].strip()
    assert "thebibliography" in kwargs["expected_output"]
    assert kwargs["context"] == [review]
    assert kwargs["output_file"] == str(tmp_path / "latex" / "article.tex")


def test_build_latex_task_fallback_config(tmp_path):
    review = MagicMock(name="review_task")
    with patch("tasks.latex_task.Task") as mock_task:
        build_latex_task(_agent(), _minimal_config(tmp_path), review)

    _, kwargs = mock_task.call_args
    assert kwargs["output_file"] == str(tmp_path / "latex" / "article.tex")


# --------------------------------------------------------------------------- #
# validation_task
# --------------------------------------------------------------------------- #


def test_build_validation_task_full_config(tmp_path):
    latex = MagicMock(name="latex_task")
    with patch("tasks.validation_task.Task") as mock_task:
        build_validation_task(_agent(), _full_config(tmp_path), latex)

    _, kwargs = mock_task.call_args
    assert "13 requirements" in kwargs["description"]
    assert kwargs["expected_output"]
    assert kwargs["context"] == [latex]
    assert kwargs["output_file"] == str(tmp_path / "pdf" / "agent_validation.md")


def test_build_validation_task_fallback_config(tmp_path):
    latex = MagicMock(name="latex_task")
    with patch("tasks.validation_task.Task") as mock_task:
        build_validation_task(_agent(), _minimal_config(tmp_path), latex)

    _, kwargs = mock_task.call_args
    assert kwargs["output_file"] == str(tmp_path / "pdf" / "agent_validation.md")
