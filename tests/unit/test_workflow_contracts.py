"""Tests for workflow schemas, parsing, and persistence."""

import json

import pytest

from workflow.models import SectionSpec, WorkflowState
from workflow.parsing import (
    parse_decision,
    parse_research_package,
    validate_bidi_markdown,
)
from workflow.storage import WorkflowStorage


def test_parse_research_package_requires_bidi(research_package):
    package, sections = parse_research_package(json.dumps(research_package))
    assert package["visuals"][0]["id"] == "visual1"
    assert len(sections) == 8
    assert sections[6].bidi_required

    research_package["sections"][6]["bidi_required"] = False
    research_package["sections"][6]["title"] = "Multilingual Systems"
    with pytest.raises(ValueError, match="BiDi"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_normalizes_structured_markdown(research_package):
    research_package["research_markdown"] = {"summary": "Structured model output"}
    package, _ = parse_research_package(json.dumps(research_package))
    assert isinstance(package["research_markdown"], str)
    assert "Structured model output" in package["research_markdown"]


def test_parse_research_rejects_bad_visual_source(research_package):
    research_package["visuals"][0]["sources"] = ["missing"]
    with pytest.raises(ValueError, match="unknown source"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_requires_three_visuals(research_package):
    research_package["visuals"] = research_package["visuals"][:1]
    with pytest.raises(ValueError, match="at least 3 visuals"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_derives_visual_section_assignment(research_package):
    research_package["sections"][4]["artifact_ids"] = []
    _, sections = parse_research_package(json.dumps(research_package))
    assert "visual1" in sections[4].artifact_ids


def test_parse_research_requires_visual_caption(research_package):
    del research_package["visuals"][0]["caption"]
    with pytest.raises(ValueError, match="missing caption"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_requires_exact_bidi_heading(research_package):
    research_package["sections"][6]["title"] = "Conclusion"
    with pytest.raises(ValueError, match="approved English heading"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_requires_final_references(research_package):
    research_package["sections"][-1]["title"] = "Conclusion"
    with pytest.raises(ValueError, match="Final section"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_normalizes_reference_section_shape(research_package):
    final = research_package["sections"][-1]
    final["title"] = "References / Bibliography"
    final["target_words"] = None
    final["source_ids"] = []
    final["acceptance_criteria"] = "List every approved source"
    _, sections = parse_research_package(json.dumps(research_package))
    assert sections[-1].title == "References"
    assert sections[-1].target_words == 0
    assert len(sections[-1].source_ids) == 8
    assert sections[-1].acceptance_criteria == ["List every approved source"]


def test_parse_research_requires_all_sources_in_references(research_package):
    research_package["sections"][-1]["source_ids"] = ["ref1"]
    with pytest.raises(ValueError, match="every approved source"):
        parse_research_package(json.dumps(research_package))


def test_parse_research_requires_minimum_body_words(research_package):
    for section in research_package["sections"][:-1]:
        section["target_words"] = 100
    with pytest.raises(ValueError, match="at least 4500 words"):
        parse_research_package(json.dumps(research_package))


def test_decision_parser_handles_fence_and_status():
    parsed = parse_decision('```json\n{"status":"approve"}\n```', {"APPROVE"})
    assert parsed["status"] == "APPROVE"
    assert parsed["issues"] == []


def test_bidi_markdown_validation():
    hebrew = " ".join(["מערכת", "חכמה", "מאפשרת", "עבודה"] * 6)
    validate_bidi_markdown(f"{hebrew} עם CrewAI ו Python")
    with pytest.raises(ValueError, match="direction-control"):
        validate_bidi_markdown(f"{hebrew}\u200f CrewAI Python")
    with pytest.raises(ValueError, match="substantive"):
        validate_bidi_markdown("עברית קצרה CrewAI Python")


def test_state_rejection_budgets():
    state = WorkflowState(topic="T")
    state.set_section_budget(8, 0.33)
    assert state.editor_rejection_budget == 3
    state.reject_section("one")
    with pytest.raises(ValueError, match="already returned"):
        state.reject_section("one")
    state = WorkflowState(topic="T", editor_rejection_budget=1)
    state.reject_section("one")
    with pytest.raises(ValueError, match="budget exhausted"):
        state.reject_section("two")


def test_storage_round_trip(tmp_path, research_package):
    storage = WorkflowStorage(tmp_path)
    storage.ensure_dirs()
    state = storage.load_state("Topic")
    storage.save_state(state)
    assert storage.load_state("Topic").topic == "Topic"
    _, sections = parse_research_package(json.dumps(research_package))
    storage.save_research(research_package, sections)
    loaded = storage.load_sections()
    assert loaded[0] == SectionSpec.from_dict(research_package["sections"][0])
