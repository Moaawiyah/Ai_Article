"""Top-level resumable six-agent article workflow."""

from __future__ import annotations

from pathlib import Path

from workflow.models import WorkflowState
from workflow.parsing import validate_section_plan
from workflow.prompts import latex_prompt, validation_prompt
from workflow.research_loop import run_research_loop
from workflow.section_loop import run_section
from workflow.storage import WorkflowStorage


class WorkflowError(RuntimeError):
    """Raised when a bounded workflow stage cannot be approved."""


class ArticleWorkflow:
    """Coordinate research, section approval, formatting, and validation."""

    def __init__(self, cfg, runner) -> None:
        self.cfg = cfg
        self.runner = runner
        self.storage = WorkflowStorage(cfg.output_root)

    @property
    def token_usage(self):
        """Expose accumulated provider usage from the stage runner."""
        return getattr(self.runner, "token_usage", None)

    def run(self, topic: str | None = None, after_format=None) -> Path:
        """Run or resume the article workflow and return the expected PDF path."""
        topic = topic or self.cfg.topic
        self.storage.ensure_dirs()
        state = (
            self.storage.load_state(topic)
            if getattr(self.cfg, "resume_enabled", True)
            else WorkflowState(topic=topic)
        )
        try:
            package, sections = self._planning(state)
            state.set_section_budget(len(sections), self.cfg.editor_rejection_ratio)
            self.storage.save_state(state)
            article = self._sections(package, sections, state)
            self._format(package, article, state)
            if after_format:
                after_format()
            self._validate_submission(state)
            state.phase = "complete"
            self.storage.save_state(state)
            return self.cfg.output_pdf / "article.pdf"
        except Exception as exc:
            state.phase = "failed"
            state.failure_reason = str(exc)
            self.storage.save_state(state)
            raise WorkflowError(str(exc)) from exc

    def _planning(self, state):
        if (self.storage.planning / "outline.json").exists() and state.phase != "research":
            package = {
                "research_markdown": (self.storage.planning / "research.md").read_text(
                    encoding="utf-8"
                ),
                "sources": self.storage.read_json(self.storage.planning / "sources.json"),
                "visuals": self.storage.read_json(
                    self.storage.assets / "visual_specs" / "approved.json"
                ),
            }
            sections = self.storage.load_sections()
            validate_section_plan(
                sections,
                package["sources"],
                package["visuals"],
                self.cfg.min_words,
                self.cfg.min_visuals,
            )
            return package, sections
        package, sections, _ = run_research_loop(
            self.runner,
            self.cfg,
            self.storage,
            state,
            self.cfg.max_research_returns,
        )
        compatibility = self.cfg.output_research / "research_brief.md"
        compatibility.parent.mkdir(parents=True, exist_ok=True)
        compatibility.write_text(package["research_markdown"], encoding="utf-8")
        state.phase = "sections"
        self.storage.save_state(state)
        return package, sections

    def _sections(self, package, sections, state) -> str:
        approved = []
        for spec in sections:
            state.current_section = spec.section_id
            section_dir = self.storage.section_dir(spec)
            approved_path = section_dir / "approved.md"
            if approved_path.exists() and spec.section_id in state.approved_sections:
                text = approved_path.read_text(encoding="utf-8")
            else:
                previous = approved[-1] if approved else ""
                text, _ = run_section(
                    self.runner,
                    spec,
                    package["research_markdown"],
                    package["sources"],
                    previous,
                    self.storage,
                    state,
                )
                state.approved_sections.append(spec.section_id)
                self.storage.save_state(state)
            approved.append(text)
        article = "\n\n".join(approved)
        (self.storage.assembled / "article.md").write_text(article, encoding="utf-8")
        state.phase = "formatting"
        self.storage.save_state(state)
        return article

    def _format(self, package, article: str, state) -> None:
        tex_result = self.runner.run(
            "latex_formatter",
            latex_prompt(
                article,
                package["sources"],
                package["visuals"],
                self.cfg.min_pages,
                self.cfg.min_visuals,
            ),
            "Complete pure LuaLaTeX source.",
        )
        self.cfg.output_latex.mkdir(parents=True, exist_ok=True)
        tex_path = self.cfg.output_latex / "article.tex"
        tex_path.write_text(tex_result.text.strip(), encoding="utf-8")
        state.phase = "submission_validation"
        self.storage.save_state(state)

    def _validate_submission(self, state) -> None:
        tex_path = self.cfg.output_latex / "article.tex"
        validation = self.runner.run(
            "submission_validator",
            validation_prompt(tex_path.read_text(encoding="utf-8")),
            "A complete Markdown submission-validation report.",
        )
        self.cfg.output_pdf.mkdir(parents=True, exist_ok=True)
        (self.cfg.output_pdf / "agent_validation.md").write_text(
            validation.text, encoding="utf-8"
        )
        state.phase = "post_processing"
        self.storage.save_state(state)
