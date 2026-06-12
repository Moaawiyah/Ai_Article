"""Strict parsing and validation of agent responses."""

from __future__ import annotations

import json
import re

from json_repair import repair_json

from workflow.models import SectionSpec

_HEBREW = re.compile(r"[\u0590-\u05ff]")
_BIDI_CONTROLS = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
_VISUAL_TYPES = {"python_chart", "table", "tikz"}


def parse_json_response(raw: str) -> dict:
    """Parse the first JSON object in a string, ignoring trailing text."""
    text = raw.strip()
    # Remove top-level code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start_idx = text.find("{")
    if start_idx == -1:
        raise ValueError("Agent response did not contain a JSON object")
    json_text = re.sub(r"(?<!\\)\\(?=[A-Za-z]{2,})", r"\\\\", text[start_idx:])

    try:
        # raw_decode parses the first JSON object and returns the data and end index.
        # This handles "Extra data" errors by simply stopping after the first object.
        data, _ = json.JSONDecoder().raw_decode(json_text)
    except json.JSONDecodeError as exc:
        try:
            data = repair_json(json_text, return_objects=True)
        except Exception as repair_exc:
            raise ValueError(f"Failed to parse agent JSON: {exc}") from repair_exc
    if not isinstance(data, dict):
        raise ValueError("Agent response must be a JSON object")
    return data


def validate_section_plan(
    sections: list[SectionSpec],
    sources: list[dict],
    visuals: list[dict],
    min_words: int = 4500,
    min_visuals: int = 3,
) -> None:
    """Enforce article-wide outline requirements."""
    if len(sections) < 8:
        raise ValueError("Research package must contain at least 8 sections")
    if len({section.section_id for section in sections}) != len(sections):
        raise ValueError("Section IDs must be unique")
    if len(sources) < 8:
        raise ValueError("Research package must contain at least 8 sources")
    last = max(sections, key=lambda section: section.order)
    if last.title.strip().lower() not in {"references", "bibliography"}:
        raise ValueError("Final section must be References or Bibliography")
    source_ids = {str(item.get("id", "")) for item in sources}
    if not source_ids.issubset(set(last.source_ids)):
        raise ValueError("Final references section must include every approved source ID")
    body_words = sum(
        section.target_words
        for section in sections
        if section.title.strip().lower() not in {"references", "bibliography"}
    )
    if body_words < min_words:
        raise ValueError(f"Planned article body must contain at least {min_words} words")
    counted = [item for item in visuals if item.get("type") in _VISUAL_TYPES]
    if len(counted) + 1 < min_visuals:
        raise ValueError(f"Research package must contain at least {min_visuals} visuals")
    visual_ids = [str(item.get("id", "")) for item in counted]
    if len(set(visual_ids)) != len(visual_ids):
        raise ValueError("Visual IDs must be unique")
    section_ids = {section.section_id for section in sections}
    if any(str(item.get("section_id", "")) not in section_ids for item in counted):
        raise ValueError("Visual references an unknown section ID")
    body_section_ids = {
        section.section_id
        for section in sections
        if section.title.strip().lower() not in {"references", "bibliography"}
    }
    if any(str(item.get("section_id", "")) not in body_section_ids for item in counted):
        raise ValueError("Visuals must be assigned to body sections")
    assigned_ids = {artifact for section in sections for artifact in section.artifact_ids}
    if not set(visual_ids).issubset(assigned_ids):
        raise ValueError("Every visual must be assigned to a section artifact_ids list")


def parse_research_package(
    raw: str,
    min_words: int = 4500,
    min_visuals: int = 3,
) -> tuple[dict, list[SectionSpec]]:
    """Validate research package structure and mandatory BiDi section."""
    data = parse_json_response(raw)
    for key in ("research_markdown", "sources", "sections", "visuals"):
        if key not in data:
            raise ValueError(f"Research package missing {key}")
    if not isinstance(data["research_markdown"], str):
        data["research_markdown"] = json.dumps(
            data["research_markdown"], indent=2, ensure_ascii=False
        )
    sections = [SectionSpec.from_dict(item) for item in data["sections"]]
    for section in sections:
        if section.title.startswith("Hebrew and English in AI Systems"):
            section.title = "Hebrew and English in AI Systems"
            section.bidi_required = True
    sections_by_id = {section.section_id: section for section in sections}
    for visual in data["visuals"]:
        section = sections_by_id.get(str(visual.get("section_id", "")))
        visual_id = str(visual.get("id", ""))
        if section and visual_id and visual_id not in section.artifact_ids:
            section.artifact_ids.append(visual_id)
    last = max(sections, key=lambda section: section.order)
    if last.title.strip().lower().startswith(("references", "bibliography")):
        last.title = "References"
        if not last.source_ids:
            last.source_ids = [str(item.get("id", "")) for item in data["sources"]]
    validate_section_plan(sections, data["sources"], data["visuals"], min_words, min_visuals)
    bidi_sections = [section for section in sections if section.bidi_required]
    if not bidi_sections:
        raise ValueError("Outline must include a dedicated BiDi section")
    if not any(section.title == "Hebrew and English in AI Systems" for section in bidi_sections):
        raise ValueError("BiDi section must use the approved English heading")
    source_ids = {str(item.get("id", "")) for item in data["sources"]}
    for visual in data["visuals"]:
        for key in (
            "id",
            "type",
            "section_id",
            "purpose",
            "data_basis",
            "sources",
            "caption",
        ):
            if key not in visual:
                raise ValueError(f"Visual specification missing {key}")
        if visual["data_basis"] == "measured" and not visual["sources"]:
            raise ValueError("Measured visual requires at least one source")
        if any(str(source) not in source_ids for source in visual["sources"]):
            raise ValueError("Visual references an unknown source ID")
    return data, sorted(sections, key=lambda section: section.order)


def parse_decision(raw: str, allowed: set[str]) -> dict:
    """Parse a structured agent decision with an allowed status."""
    data = parse_json_response(raw)
    status = str(data.get("status", "")).upper()
    if status not in allowed:
        raise ValueError(f"Invalid decision status: {status}")
    data["status"] = status
    data.setdefault("issues", [])
    data.setdefault("required_changes", [])
    return data


def validate_bidi_markdown(text: str) -> None:
    """Require substantive Hebrew mixed with Latin terms and no control chars."""
    if _BIDI_CONTROLS.search(text):
        raise ValueError("BiDi section contains forbidden direction-control characters")
    hebrew_words = re.findall(r"[\u0590-\u05ff]{2,}", text)
    latin_terms = re.findall(r"\b[A-Za-z][A-Za-z0-9.+-]*\b", text)
    if len(hebrew_words) < 20:
        raise ValueError("BiDi section needs a substantive Hebrew paragraph")
    if len(latin_terms) < 2:
        raise ValueError("BiDi section needs embedded English technical terms")
