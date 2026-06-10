"""Review task factory."""

from crewai import Agent, Task

from shared.config import AppConfig, PipelineConfig


def build_review_task(agent: Agent, config: AppConfig | PipelineConfig, writing_task: Task) -> Task:
    """Create the review task that consumes the Writer output."""
    out = config.output_reviewed if hasattr(config, "output_reviewed") else config.output_root / "reviewed"
    return Task(
        description=(
            "You will receive a Markdown article draft. Your job is to improve it and "
            "return the FULL revised article — not a review report, not bullet-point feedback.\n\n"
            "Apply these fixes directly to the article text:\n"
            "- Expand any section shorter than 400 words by adding depth, examples, or subsections.\n"
            "- Ensure every major claim has an inline citation marker [N] — aim for at least "
            "one citation per paragraph.\n"
            "- Verify these required elements are present; add them if missing:\n"
            "  * Exactly one <!-- TIKZ: description --> marker in the designated section\n"
            "  * At least one Markdown pipe table (| col | ... |)\n"
            "  * At least one display math formula inside $$...$$ delimiters\n"
            "  * ## References section at the end with 8-15 numbered entries (max 15)\n"
            "- Verify every multi-topic section has >= 2 ### subsections; if any section "
            "lacks them, split its prose into named subsections (e.g. ### Setup, ### Results).\n"
            "- Fix any broken Markdown formatting.\n"
            "- English only for all non-Hebrew content: remove any stray Hebrew text from "
            "English sections, BiDi markers, or <!-- RTL --> blocks.\n"
            "- PRESERVE all Hebrew prose in the Conclusion section intact. Do not remove, "
            "translate, or move the Hebrew text. Do not add any label indicating it is bilingual.\n\n"
            "Output the complete revised article in Markdown. Do not output review notes, "
            "checklists, or a summary of changes — only the article itself."
        ),
        expected_output=(
            "The complete revised Markdown article with all sections, required artifacts "
            "(<!-- TIKZ: ... --> marker, Markdown table, display formula, bibliography 8-15 refs max), "
            "inline citations [N] throughout (at least one per paragraph), a 'Bilingual Summary' "
            "Conclusion section containing Hebrew prose naturally mixed with English, "
            "and a minimum of 4,500 words in the body. "
            "All section headings in English."
        ),
        agent=agent,
        context=[writing_task],
        output_file=str(out / "reviewed.md"),
    )
