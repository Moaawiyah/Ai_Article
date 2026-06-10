"""Writing task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import AppConfig, PipelineConfig


def build_writing_task(agent: Agent, config: AppConfig | PipelineConfig, research_task: Task) -> Task:
    """Create the writing task. Writer follows section structure proposed by Researcher."""
    out       = config.output_drafts if hasattr(config, "output_drafts") else config.output_root / "drafts"
    min_w     = getattr(config, "min_words", 4500)
    max_w     = getattr(config, "max_words", 5000)
    pages     = getattr(config, "min_pages",  15)
    lang      = getattr(config, "language",   "english")
    artifacts = getattr(config, "artifact_instructions", "")

    description = (
        "Write the complete academic article using the Researcher output as your sole\n"
        "grounding source. Do not invent facts or citations beyond what the Researcher provided.\n\n"
        "STRUCTURE RULE: Follow exactly the section structure proposed by the Researcher.\n"
        "Do not impose a different structure. Expand each section into full academic prose.\n\n"
        f"TARGETS: {min_w}-{max_w} words total body, ~{pages} pages, language: {lang}.\n\n"
        "REQUIRED ARTIFACTS — embed all of the following in the sections the Researcher designated:\n"
        f"{artifacts}\n\n"
        "CITATION DENSITY: Every major claim must have an inline citation marker [N]. "
        "Aim for at least one citation per paragraph throughout the article.\n\n"
        "BIDI REQUIREMENT: The Conclusion section must contain approximately 150-200 words "
        "of Hebrew prose naturally interspersed with English paragraphs. "
        "The heading stays as 'Conclusion' — do not add any label or indicator that it "
        "contains Hebrew. English technical terms (P4, SDN, ECMP, HULA) stay in Latin "
        "characters inline within the Hebrew text. "
        "Do not add a separate bilingual section.\n\n"
        "Follow your skill for process rules, artifact format syntax, and quality checklist.\n"
        "No tools. No external images. Academic English for all non-Hebrew sections."
    )

    return Task(
        description=description,
        expected_output=(
            "A single Markdown document with: title block, table of contents (all entries in "
            f"English), all sections from the Researcher's proposed structure ({min_w}+ words "
            "total body), all required artifacts embedded (TikZ marker, display formula, "
            "Markdown table, bibliography 8-15 refs max), inline citations [N] throughout "
            "(at least one per paragraph), and a Conclusion section containing ~150-200 words "
            "of Hebrew prose naturally mixed with English under the plain heading 'Conclusion'."
        ),
        agent=agent,
        context=[research_task],
        output_file=str(out / "draft.md"),
    )
