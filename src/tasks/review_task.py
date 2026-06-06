"""Review task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig


def build_review_task(agent: Agent, config: AppConfig | PipelineConfig, writing_task: Task) -> Task:
    """Create the review task that consumes the Writer output."""
    out = config.output_reviewed if hasattr(config, "output_reviewed") else config.output_root / "reviewed"
    return Task(
        description=(
            "You will receive a Markdown article draft. Your job is to improve it and "
            "return the FULL revised article — not a review report, not bullet-point feedback.\n\n"
            "Apply these fixes directly to the article text:\n"
            "- Expand any section shorter than 400 words by adding depth, examples, or subsections.\n"
            "- Ensure every major claim has an inline citation marker [N].\n"
            "- Verify these required elements are present; add them if missing:\n"
            "  * At least one Markdown table (| col | ... |)\n"
            "  * At least one display math formula inside $$...$$ delimiters\n"
            "  * Image placeholder: ![Figure: Multi-Agent Collaboration Architecture](outputs/assets/architecture_diagram.png)\n"
            "  * Graph placeholder: ![Figure: Agent Task Completion Rate](outputs/assets/task_completion_graph.png)\n"
            "  * Hebrew-English BiDi section with <!-- RTL --> ... <!-- /RTL --> markers\n"
            "  * ## Bibliography section at the end\n"
            "- Fix any broken Markdown formatting.\n\n"
            "Output the complete revised article in Markdown. Do not output review notes, "
            "checklists, or a summary of changes — only the article itself."
        ),
        expected_output=(
            "The complete revised Markdown article with all sections, required artifacts "
            "(table, formula, image placeholder, graph placeholder, BiDi section, bibliography), "
            "inline citations, and a minimum of 4,500 words in the body."
        ),
        agent=agent,
        context=[writing_task],
        output_file=str(out / "reviewed.md"),
    )
