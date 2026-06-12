"""Filesystem persistence for resumable article workflows."""

from __future__ import annotations

import json
from pathlib import Path

from workflow.models import SectionSpec, WorkflowState


class WorkflowStorage:
    """Read and write workflow artifacts below one output root."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.planning = root / "planning"
        self.sections = root / "sections"
        self.assembled = root / "assembled"
        self.assets = root / "assets"
        self.state_path = root / "run_state.json"

    def ensure_dirs(self) -> None:
        """Create workflow output directories."""
        for path in (
            self.planning,
            self.sections,
            self.assembled,
            self.assets / "visual_specs",
            self.assets / "generated",
        ):
            path.mkdir(parents=True, exist_ok=True)

    def load_state(self, topic: str) -> WorkflowState:
        """Load matching state or initialize a new run."""
        if not self.state_path.exists():
            return WorkflowState(topic=topic)
        state = WorkflowState.from_dict(self.read_json(self.state_path))
        return state if state.topic == topic else WorkflowState(topic=topic)

    def save_state(self, state: WorkflowState) -> None:
        """Persist workflow state atomically."""
        self.write_json(self.state_path, state.as_dict())

    def section_dir(self, spec: SectionSpec) -> Path:
        """Return and create the directory for a section."""
        path = self.sections / f"{spec.order:02d}-{spec.section_id}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_research(self, package: dict, sections: list[SectionSpec]) -> None:
        """Persist approved planning artifacts and visual specifications."""
        (self.planning / "research.md").write_text(
            package["research_markdown"], encoding="utf-8"
        )
        self.write_json(self.planning / "outline.json", [vars(item) for item in sections])
        self.write_json(self.planning / "sources.json", package["sources"])
        self.write_json(self.assets / "visual_specs" / "approved.json", package["visuals"])

    def load_sections(self) -> list[SectionSpec]:
        """Load approved outline sections."""
        return [SectionSpec.from_dict(item) for item in self.read_json(self.planning / "outline.json")]

    @staticmethod
    def write_json(path: Path, data) -> None:
        """Write pretty UTF-8 JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def read_json(path: Path):
        """Read JSON from *path*."""
        return json.loads(path.read_text(encoding="utf-8"))
