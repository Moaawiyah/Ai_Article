"""Data contracts for the section workflow."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field


def _list_value(value) -> list:
    """Normalize one model-produced scalar or list to a list."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


@dataclass
class SectionSpec:
    """One approved article section contract."""

    section_id: str
    title: str
    order: int
    target_words: int
    required_topics: list[str]
    source_ids: list[str]
    artifact_ids: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    bidi_required: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> SectionSpec:
        required = ("section_id", "title", "order", "target_words")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Section missing fields: {', '.join(missing)}")
        return cls(
            section_id=str(data["section_id"]),
            title=str(data["title"]),
            order=int(data["order"]),
            target_words=int(data["target_words"] or 0),
            required_topics=_list_value(data.get("required_topics")),
            source_ids=_list_value(data.get("source_ids")),
            artifact_ids=_list_value(data.get("artifact_ids")),
            acceptance_criteria=_list_value(data.get("acceptance_criteria")),
            bidi_required=bool(data.get("bidi_required", False))
            or data["title"] == "Hebrew and English in AI Systems",
        )


@dataclass
class WorkflowState:
    """Persistent progress and bounded-loop counters."""

    topic: str
    phase: str = "research"
    research_returns: int = 0
    approved_sections: list[str] = field(default_factory=list)
    section_rejections: dict[str, int] = field(default_factory=dict)
    editor_rejections_used: int = 0
    editor_rejection_budget: int = 0
    current_section: str = ""
    failure_reason: str = ""

    def set_section_budget(self, section_count: int, ratio: float) -> None:
        """Set the article-wide rejection budget using ceiling rounding."""
        self.editor_rejection_budget = math.ceil(section_count * ratio)

    def reject_section(self, section_id: str) -> None:
        """Record one rejection while enforcing both rejection limits."""
        count = self.section_rejections.get(section_id, 0)
        if count >= 1:
            raise ValueError(f"Section {section_id} was already returned once")
        if self.editor_rejections_used >= self.editor_rejection_budget:
            raise ValueError("Article-wide section rejection budget exhausted")
        self.section_rejections[section_id] = count + 1
        self.editor_rejections_used += 1

    def as_dict(self) -> dict:
        """Return a JSON-serializable state mapping."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> WorkflowState:
        """Restore state from persisted JSON."""
        return cls(**data)
