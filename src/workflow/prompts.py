"""Prompt builders for the six-agent workflow."""

from __future__ import annotations

import json

from workflow.models import SectionSpec


def research_prompt(
    topic: str,
    artifacts: str,
    min_pages: int,
    min_words: int,
    max_words: int,
    min_visuals: int,
    feedback: dict | None = None,
    previous: dict | None = None,
) -> str:
    """Build the initial or revision research-package prompt."""
    correction = ""
    if feedback:
        correction = (
            "\nRevise the prior package and correct every verifier issue.\nPrior package:\n"
            + json.dumps(previous or {}, ensure_ascii=False)
            + "\nVerifier feedback:\n"
            + json.dumps(feedback, ensure_ascii=False)
        )
    return f"""
Research the academic topic: {topic}
Required artifact types:
{artifacts}
{correction}

The final compiled article must be at least {min_pages} pages and the body must contain
{min_words}-{max_words} words, excluding the references list.
The section plan MUST end with a "Bibliography" or "References" section. That final
section must contain every approved source ID and must be written after all body sections.

Return ONLY valid JSON with:
- research_markdown: detailed section research notes with citation IDs and one fenced
  graph-performance JSON block using main/arch_a/arch_b.
- sources: array of objects with id, authors, title, venue, year, url_or_doi, verified_confidence.
- sections: ordered array with section_id, title, order, target_words, required_topics,
  source_ids, artifact_ids, acceptance_criteria, bidi_required.
- visuals: array with id, type (python_chart/table/formula/tikz), section_id, purpose,
  data_basis, sources, caption, and type-specific fields.

Include one dedicated section titled "Hebrew and English in AI Systems" with
bidi_required=true. It must require a substantive Hebrew paragraph containing natural
English technical terms such as CrewAI, LaTeX, LLM, RAG, Python, or API.
Use source IDs ref1, ref2, and so on. Use at least 8 sections total, including the final
References/Bibliography section, and at least 8 real sources. Allocate at least
{min_words} target words across body sections; do not count the references section.
Specify at least {min_visuals} useful academic visuals selected according to the topic from
python_chart, table, and tikz. The pipeline's deterministic performance chart counts as one,
so specify at least {min_visuals - 1} additional tables or TikZ diagrams. Formulas do not
count toward this minimum. Give every visual
a unique ID, caption, purpose, source basis, and body-section placement, and include each
visual ID in that section's artifact_ids.
The graph JSON must provide median_queue, p95_queue, base_fct_ms, fct_slope,
data_basis, and source for main, arch_a, and arch_b. Mark unsupported data estimated.
"""


def verification_prompt(package: dict, min_visuals: int = 3) -> str:
    """Build the source-verification and outline-approval prompt."""
    return f"""
Audit this research package:
{json.dumps(package, ensure_ascii=False)}

Check source plausibility and metadata, claim support, section order and completeness,
assignment coverage, visual provenance, and the dedicated Hebrew-English BiDi section.
Require at least {min_visuals} relevant charts, tables, or diagrams in total, counting the
pipeline's deterministic performance chart. Other visuals need unique IDs and assigned
body sections. Reject decorative or redundant visuals and measured visuals without a
traceable source. The BiDi section must require at least
one substantive Hebrew paragraph with embedded English technical terms.

Return ONLY JSON:
{{"status":"APPROVE|REVISE","issues":[],"required_changes":[],"evidence":[]}}
"""


def section_prompt(
    spec: SectionSpec,
    research: str,
    sources: list[dict],
    previous_section: str,
    feedback: dict | None = None,
) -> str:
    """Build a section-writing or rewrite prompt."""
    correction = json.dumps(feedback or {}, ensure_ascii=False)
    is_references = spec.title.strip().lower() in {"references", "bibliography"}
    writing_rules = (
        "This is the final references section. List every approved source in a consistent "
        "numbered academic format using its source ID. Do not add prose or unapproved sources."
        if is_references
        else "Do not include the whole-article references list in this body section."
    )
    return f"""
Write only this article section in Markdown:
{json.dumps(vars(spec), ensure_ascii=False)}

Approved research:
{research}
Approved sources:
{json.dumps(sources, ensure_ascii=False)}
Previous approved section for continuity:
{previous_section}
Rewrite feedback:
{correction}

Use ## for the section heading, [N] citation markers, and only approved source IDs.
Include required academic visual markers/specifications where assigned. Do not include
references for the whole article unless this is the final references section.
{writing_rules}
If bidi_required=true, write a substantive Hebrew
paragraph with embedded English technical terms, but no HTML, LaTeX direction commands,
or Unicode BiDi control characters. Return Markdown only.
"""


def editor_prompt(spec: SectionSpec, draft: str, previous_section: str) -> str:
    """Build the per-section editorial gate prompt."""
    return f"""
Review this section against its approved specification.
Specification: {json.dumps(vars(spec), ensure_ascii=False)}
Previous approved section:
{previous_section}
Draft:
{draft}

Check required topics, factual grounding, citation markers, academic quality, continuity,
word-target depth, and assigned visuals. For a BiDi section, require substantive Hebrew,
embedded English technical terms, and no direction-control characters.

Return ONLY JSON:
{{"status":"APPROVE|REWRITE","issues":[],"required_changes":[],
"citation_issues":[],"continuity_issues":[]}}
"""


def latex_prompt(
    article: str,
    sources: list[dict],
    visuals: list[dict],
    min_pages: int = 15,
    min_visuals: int = 3,
) -> str:
    """Build the final formatter prompt from approved sections."""
    return f"""
Convert the approved article below to complete LuaLaTeX. Use the source registry for a
final thebibliography containing every approved source, and the approved visual
specifications for tables, formulas, TikZ, and
  generated-chart placement. For python_chart specifications, leave chart placement and
  rendering to deterministic post-processing; do not invent chart data or duplicate the chart.
Render every approved table and TikZ specification, preserve every generated-chart placement,
and ensure the document contains at least {min_visuals} charts, tables, or diagrams.

For the dedicated Hebrew-English section, use an English section heading, wrap Hebrew
paragraphs in begin{{hebrew}}/end{{hebrew}}, and wrap every embedded Latin technical term
with textenglish{{...}}. Use polyglossia and never use setRL.

Sources: {json.dumps(sources, ensure_ascii=False)}
Visuals: {json.dumps(visuals, ensure_ascii=False)}
Article:
{article}

Return pure LaTeX only, ending with end{{document}}.
The compiled document is required to be at least {min_pages} pages; preserve the approved body depth
and use normal academic spacing rather than artificial blank pages.
"""


def validation_prompt(tex: str) -> str:
    """Build the non-blocking article-evaluation prompt."""
    return f"""
Evaluate this completed LaTeX article. This is an advisory assessment only: do not approve,
reject, stop, rewrite, or request another pipeline iteration.

Assess:
- requirement checks with PASS/PARTIAL/FAIL and concrete evidence;
- academic quality, organization, depth, clarity, coherence, and citation quality;
- visual, mathematical, bibliography, and Hebrew-English BiDi quality;
- strongest aspects and important weaknesses;
- academic level (introductory undergraduate, advanced undergraduate, master's, or research);
- numerical scores from 0-10 for content, evidence, structure, writing, visuals, and compliance;
- overall score from 0-100 and confidence in the assessment;
- prioritized improvements separated into critical, important, and optional.

End with an advisory readiness summary such as Strong, Acceptable with revisions, or Weak.
The readiness summary is informational and must never be phrased as a pipeline decision.
Do not use `Ready for submission: YES/NO`.

LaTeX:
{tex}
"""
