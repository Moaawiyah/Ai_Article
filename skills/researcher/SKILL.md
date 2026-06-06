---
name: researcher
description: Direct research and summarization skill for a CrewAI article generator that produces a citation-ready knowledge base for a long-form article on multi-agent collaboration systems.
version: 1.0.0
---

# Researcher

## Purpose

Use this skill when an agent must gather, organize, and prioritize source material for an article about multi-agent collaboration systems, especially when the downstream crew includes writing, review, LaTeX formatting, and PDF validation stages.

This skill is responsible for building a trustworthy research foundation for a ~15-page article on "Multi-Agent Collaboration Systems: Designing Teams of AI Agents".

## Instructions

1. Start from the article objective, target length, and required deliverables.
2. Break the topic into research themes that support a coherent academic structure.
3. Prioritize themes that are necessary for the assignment:
   - CrewAI team design and sequential workflows
   - Multi-agent collaboration patterns and responsibilities
   - direct research summaries for the Writer Agent
   - LaTeX/PDF publication requirements
   - Citations and bibliography readiness
   - Visual assets: image, graph, and table
   - Mathematical formulation or formal notation
   - Hebrew-English bidirectional section requirements
4. Collect high-signal evidence, definitions, terminology, and contrasting viewpoints.
5. Distinguish clearly between facts, interpretations, open questions, and missing evidence.
6. Organize findings into reusable notes for downstream agents, grouped by section or claim.
7. Surface research gaps early so the Writer Agent can compensate intentionally.

## Input Expectations

Expected inputs may include:

- Article title or topic
- Assignment requirements and deliverables
- Desired section outline or proposed thesis
- Available source notes, documents, URLs, or citations
- Constraints on article length, tone, or publication format

Inputs should be sufficient to determine what must be proven, illustrated, cited, and formatted in the final article.

## Output Expectations

Produce structured research notes that are ready for downstream use.

Outputs should include:

- A proposed topic breakdown or section map
- Key claims supported by evidence summaries
- Citation candidates tied to specific claims or sections
- Identified gaps, ambiguities, or weakly supported areas
- Suggested opportunities for:
  - one image
  - one graph
  - one table
  - one formula
  - one Hebrew-English BiDi subsection

The output should be concise, source-aware, and easy for the Writer Agent to reuse without reinterpreting the research intent.

## Rules And Constraints

- Do not draft the full article body.
- Do not invent citations, statistics, or source authority.
- Prefer primary, technical, or academically credible sources when available.
- Keep notes reusable across topics; avoid hard-coding a single article structure unless the assignment requires it.
- Separate evidence from speculation.
- Favor traceable claims that can survive reviewer scrutiny.
- When evidence is weak, say so explicitly instead of smoothing it over.
- Research should support a 15-page article, not a short blog post.
- Ensure the research plan leaves room for CrewAI process explanation and publication-quality artifacts.

## Quality Checklist

- The research covers all assignment-mandated components.
- Major claims have source candidates or explicit evidence gaps.
- Notes are organized for downstream writing and review.
- The material supports academic tone rather than marketing language.
- The article can plausibly reach 15 pages without filler.
- Visual and formula opportunities are identified intentionally.
- The BiDi section is accounted for rather than added as an afterthought.
