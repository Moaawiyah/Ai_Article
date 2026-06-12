"""Section Writer and Article Editor feedback loop."""

from __future__ import annotations

from workflow.parsing import parse_decision, validate_bidi_markdown
from workflow.prompts import editor_prompt, section_prompt


def run_section(runner, spec, research, sources, previous, storage, state):
    """Write and approve one section, allowing at most one rewrite."""
    section_dir = storage.section_dir(spec)
    storage.write_json(section_dir / "specification.json", vars(spec))
    feedback = None
    while True:
        result = runner.run(
            "writer",
            section_prompt(spec, research, sources, previous, feedback),
            "One complete Markdown section.",
        )
        draft = result.text.strip()
        (section_dir / "draft.md").write_text(draft, encoding="utf-8")
        if spec.bidi_required:
            validate_bidi_markdown(draft)
        review_result = runner.run(
            "article_editor",
            editor_prompt(spec, draft, previous),
            "A JSON APPROVE or REWRITE decision.",
        )
        review = parse_decision(review_result.text, {"APPROVE", "REWRITE"})
        storage.write_json(section_dir / "review.json", review)
        if review["status"] == "APPROVE":
            (section_dir / "approved.md").write_text(draft, encoding="utf-8")
            return draft, result
        state.reject_section(spec.section_id)
        storage.save_state(state)
        feedback = review
