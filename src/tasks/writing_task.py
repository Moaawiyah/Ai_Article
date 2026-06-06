"""Writing task factory."""

from crewai import Agent, Task

from agent_ai.shared.config import PROJECT_TOPIC, AppConfig, PipelineConfig

_WRITING_DESCRIPTION = f"""
Write a complete, structured academic article on: {PROJECT_TOPIC}.

Use the Researcher Agent output as your sole source of grounding.
Do NOT assume a RAG retrieval bundle exists. Work only from the research brief provided.

---

## STEP 1 — Call tools FIRST (before writing any article text)

You have two tools. Call BOTH now, before writing anything else:

1. Call generate_architecture_diagram with a JSON array of the 5 agents in this pipeline:
   Researcher, Writer, Reviewer, LaTeX Formatter, PDF Validator.
   Each entry needs: name, color (hex), desc (one line), output (filename).

2. Call generate_performance_graph with a JSON object containing:
   title, xlabel, ylabel, labels (the 5 agent names), values (realistic 70-98 integers),
   and colors (hex list matching the diagram).

Do not proceed to writing until both tools return a success message.

---

## STEP 2 — Required document structure (produce every section below, in this order):

### 1. Title block
- Full article title
- Author placeholder: [Author Name]
- Course / institution placeholder: [Course Name, Institution]
- Date placeholder: [Date]

### 2. Abstract
One paragraph (150–250 words) summarising the article's motivation, scope, and key findings.

### 3. Table of Contents
List all 8–10 main section titles with their section numbers (e.g., "1. Introduction").

### 4. Main Sections (8–10 sections)
Write each section with a numbered heading and substantive prose.
MINIMUM LENGTH: each section must be at least 400 words. Do not move to the next section
until the current one reaches this minimum. If you run out of things to say, add a
subsection that explores implications, limitations, or a worked example.

Suggested section titles (adapt based on the research brief):
  1. Introduction
  2. Background and Motivation
  3. Multi-Agent System Architecture
  4. CrewAI Framework and Sequential Workflows
  5. Agent Roles and Responsibilities
  6. Collaboration Patterns and Communication
  7. Local LLM Execution with Ollama
  8. Evaluation and Performance Considerations
  9. Hebrew–English Bidirectional Section  ← REQUIRED (see rules below)
  10. Conclusion and Future Work

Each section must include at least two to three subsections (### level headings)
with their own developed paragraphs. Explain concepts in depth: define terms,
provide examples, discuss trade-offs, and cite relevant literature.

### 5. Required artifacts — embed or place these within the relevant sections:

**Table (Markdown):**
At least one table comparing frameworks, agent roles, or metrics.
Format as a standard Markdown table (| col | col | ... |).

**Mathematical formula:**
At least one formula written in LaTeX math syntax inside $$...$$ delimiters.
Example placement: performance model, complexity bound, or similarity score formula.

**Architecture diagram:**
Both tool calls were done in STEP 1. Insert this exact line where the diagram belongs:
![Figure: Multi-Agent Collaboration Architecture](outputs/assets/architecture_diagram.png)
*Figure 1: High-level architecture of a multi-agent collaboration system.*

**Performance graph:**
Insert this exact line where the graph belongs:
![Figure: Agent Task Completion Rate](outputs/assets/task_completion_graph.png)
*Figure 2: Agent task completion rates generated from pipeline analysis.*

**Markdown table (REQUIRED — do not skip):**
Include at least one pipe-formatted Markdown table comparing agent roles, frameworks, or metrics.
Example format:
| Column A | Column B | Column C |
|---|---|---|
| value | value | value |

**Hebrew–English BiDi section:**
Section 9 MUST contain at least two paragraphs that mix Hebrew and English.
Write the Hebrew text right-to-left using actual Hebrew characters.
Surround Hebrew passages with the markers: <!-- RTL --> ... <!-- /RTL -->
Example structure:
  English intro sentence.
  <!-- RTL -->
  טקסט בעברית כאן.
  <!-- /RTL -->
  English continuation.

### 6. Bibliography
End the article with a `## Bibliography` section.
List at least 6 citation placeholders in the format:
[1] [Author(s), "Title," *Journal/Conference*, Year. URL or DOI placeholder]

Use inline citation markers [1], [2], ... throughout the article body wherever claims are made.

---

## Rules:
- Write in formal academic English (except the BiDi section).
- Every main claim must have an inline citation marker [N].
- Do not fabricate statistics or empirical results; mark uncertain values explicitly.
- The TOTAL article body (excluding title block, TOC, and bibliography) must be at least
  4,500 words. Count your words as you write. If you finish a section short, expand it
  before moving on — do not leave any section under 400 words.
- Each section must contain at least 2–3 subsections with substantive prose.
- Do not pad with repetition; prefer depth: definitions, mechanisms, trade-offs, examples.
- All Markdown headings must use ## for sections, ### for subsections.
""".strip()

_EXPECTED_OUTPUT = (
    "A single Markdown document containing: title block, abstract, table of contents, "
    "8–10 numbered sections with substantive prose, at least one Markdown table, at least "
    "one $$...$$ formula, an image placeholder, a graph placeholder, a Hebrew–English BiDi "
    "section with <!-- RTL --> markers, inline citations [N], and a bibliography."
)


def build_writing_task(agent: Agent, config: AppConfig | PipelineConfig, research_task: Task) -> Task:
    """Create the writing task that consumes the Researcher output."""
    # TODO: When RAG is added, pass retrieved context here alongside the research brief.
    out = config.output_drafts if hasattr(config, "output_drafts") else config.output_root / "drafts"
    return Task(
        description=_WRITING_DESCRIPTION,
        expected_output=_EXPECTED_OUTPUT,
        agent=agent,
        context=[research_task],
        output_file=str(out / "draft.md"),
    )
