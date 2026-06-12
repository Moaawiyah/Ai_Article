# Assignment 03 Project Report: CrewAI and LaTeX Article Generator

We built a multi-agent system that researches, writes, reviews, formats, compiles, and
validates an academic article. Our generated article is titled **“HULA: Scalable Load
Balancing Using Programmable Data Planes.”** We use CrewAI to coordinate five specialized
agents, Matplotlib to generate a benchmark plot, and LuaLaTeX to produce the final PDF.

| Project information | Details |
|---|---|
| Students | Mohammad Selawe and Moa’awiyah Hajajreh |
| Course | AI Orchestration |
| Lecturer | Dr. Segal Yoram |
| Assignment | Assignment 03: Article/Book Generation with CrewAI and LaTeX |
| Final article | HULA: Scalable Load Balancing Using Programmable Data Planes |
| Final result | 15-page A4 PDF |

## Quick Links

- [Final article PDF](outputs/pdf/article.pdf)
- [Generated LaTeX source](outputs/latex/article.tex)
- [Python-generated benchmark plot](outputs/latex/benchmark.png)
- [Programmatic validation report](outputs/pdf/validation_report.md)
- [Agent validation report](outputs/pdf/agent_validation.md)
- [Research brief](outputs/research/research_brief.md)
- [Markdown draft](outputs/drafts/draft.md)
- [Reviewed Markdown](outputs/reviewed/reviewed.md)
- [Architecture documentation](docs/ARCHITECTURE.md)
- [Prompt engineering record](docs/PROMPTS.md)

## 1. Introduction

The goal of Assignment 03 was to build a CrewAI team that creates a structured article or
small book and exports it as a polished LaTeX PDF. We selected HULA because it provides
enough technical depth for architecture discussion, mathematical notation, comparative
analysis, a data-driven plot, a table, citations, and mixed Hebrew-English text.

Our system begins with a configured topic and produces several inspectable intermediate
artifacts. We first generate research notes and a Markdown draft, review the content, convert
the approved result to LuaLaTeX, inject a Python-generated benchmark plot, compile the PDF,
and run a 13-item validation checklist. We kept these stages separate because it made the
pipeline easier to test and debug than generating the final PDF in one step.

## 2. Assignment Requirements

| Requirement | How We Addressed It |
|---|---|
| CrewAI agent team | We use five agents in a sequential CrewAI process. |
| About 15 pages | Our generated PDF contains exactly 15 A4 pages. |
| Cover page | Our generated cover includes the article title, both authors, and the date. We document the course and lecturer in this README. |
| Table of contents | We generate it with LaTeX’s `\tableofcontents` command. |
| Sections | We produce an abstract and nine numbered academic sections. |
| Headers and footers | We configure them with the `fancyhdr` package. |
| Visual content | We include a Python-generated benchmark plot and a native LaTeX/TikZ architecture diagram. |
| Python-generated graph | We generate `benchmark.png` with Matplotlib and inject it into the Evaluation section. |
| Table | We include a comparison table using a LaTeX `tabular` environment. |
| Mathematical formula | We include a display formula using an `equation` environment. |
| Hebrew-English BiDi | We use `polyglossia`, a `hebrew` environment, and `\textenglish{}` for embedded technical terms. |
| Bibliography | We use LaTeX’s inline `thebibliography` environment with 24 `\bibitem` entries. |
| Linked citations | We convert citation markers to `\cite{refN}` and load `hyperref` for navigation. |

## 3. System Overview

Our pipeline follows this data flow:

```mermaid
flowchart LR
    A["Topic and configuration"] --> B["Researcher"]
    B --> C["Writer"]
    C --> D["Reviewer"]
    D --> E["LaTeX Formatter"]
    E --> F["PDF Validator"]
    F --> G["Python graph generation"]
    G --> H["LuaLaTeX compilation"]
    H --> I["13-item validation"]
    I --> J["article.pdf"]
```

We expose the workflow through `AgentAISDK`. The command-line entry point delegates to this
SDK, while `ApiGatekeeper` provides centralized queueing, rate limiting, retries, and logging
for external API work. Runtime values such as the topic, provider, model, output paths, and
word targets come from configuration rather than being embedded in the pipeline code.

## 4. Agent Design

| Agent | Role | Input | Output | Why We Use It |
|---|---|---|---|---|
| Researcher | Organizes sources, article structure, comparison systems, and graph data | Topic and artifact requirements | `research_brief.md` | We separate evidence gathering from prose generation. |
| Writer | Expands the research brief into a structured academic article | Research brief | `draft.md` | We create readable Markdown before handling LaTeX syntax. |
| Reviewer | Checks evidence, structure, clarity, and assignment coverage | Markdown draft | `reviewed.md` | We add a quality gate before formatting. |
| LaTeX Formatter | Converts reviewed Markdown into LuaLaTeX | Reviewed article | `article.tex` | We produce the required professional PDF source. |
| PDF Validator | Inspects the generated LaTeX against the assignment checklist | LaTeX source | `agent_validation.md` | We identify missing document elements before submission. |

We use a sequential process because each stage depends directly on the previous stage’s
artifact. This structure also lets us inspect failures at the research, writing, review, or
formatting stage without rerouting work between agents.

## 5. Workflow and Implementation

### 5.1 Topic and Configuration

We configure the default article topic as "HULA: Scalable Load Balancing
Using Programmable Data Planes" in `config/config.yaml`. The same file stores
the LLM provider and model, article length targets, output directories, pricing values, and
graph-spec parameters. We can override the topic from the command line without editing the
source code.

### 5.2 Research, Writing, and Review

The Researcher proposes the article structure, gathers citation-ready notes, compares HULA
with related architectures, and emits a machine-readable performance-data block. The Writer
turns that material into long-form Markdown with the required formula, table, visual marker,
citations, and conclusion. The Reviewer then checks the draft for unsupported claims,
structural gaps, repetition, and assignment compliance.

### 5.3 Markdown Intermediate Stage

We use Markdown for the research, draft, and review stages because it is easier to inspect
than raw LaTeX. This lets us evaluate the article’s logic and organization before dealing
with compiler-sensitive formatting. The retained intermediate files also show how the
article changes between agents.

### 5.4 LaTeX and PDF Generation

The LaTeX Formatter converts headings, citations, tables, formulas, the TikZ marker, and
Hebrew text into `article.tex`. We use LuaLaTeX because it supports Unicode fonts and
Hebrew-English bidirectional text through `fontspec` and `polyglossia`.

Before compilation, deterministic utilities remove accidental Markdown fences and repair
common table, TikZ, syntax, and Hebrew-formatting problems. The compiler runs multiple
LuaLaTeX passes so the table of contents and references resolve correctly. It also supports
a Biber pass when a generated document contains a `.bcf` file, although our current article
uses the inline `thebibliography` mechanism.

### 5.5 Python Graph Generation

We generate `outputs/latex/benchmark.png` with Matplotlib. The plot contains two panels:
a cumulative distribution of bottleneck queue length and average flow-completion time
against network load. The graph generator uses the Researcher’s structured comparison data,
a fixed random seed for reproducibility, and a fallback data series when no parsed
specification is available. We then inject the image into the article’s Evaluation section.

### 5.6 Bibliography and Citations

We store the current article bibliography directly in `article.tex` using
`\begin{thebibliography}{99}` and `\bibitem{refN}` entries. This is LaTeX’s built-in
bibliography mechanism. We connect claims to these entries using `\cite{refN}` commands,
and `hyperref` makes the citation navigation available in the compiled document.

## 6. Technical Decisions

| Decision | Reason | Alternative Considered |
|---|---|---|
| Five specialized agents | We keep research, writing, review, formatting, and validation responsibilities clear. | One large prompt |
| Sequential CrewAI process | Every stage consumes the previous stage’s artifact. | Hierarchical or parallel execution |
| Markdown before LaTeX | We can review structure and content without LaTeX noise. | Direct LaTeX generation |
| LuaLaTeX | We need reliable Unicode and Hebrew-English BiDi support. | XeLaTeX |
| Deterministic post-processing | We repair recurring syntax patterns predictably instead of relying only on prompts. | Repeated LLM correction loops |
| Separate Matplotlib generator | We make the required graph reproducible and independently testable. | A manually created static image |
| Inline `thebibliography` | We keep citations and bibliography entries in one generated LaTeX artifact. | Separate `.bib` file with Biber |
| Config-driven provider | We can switch provider or model without changing pipeline logic. | Hard-coded model configuration |
| Central API gatekeeper | We apply queueing, rate limits, retries, and logs consistently. | Per-call retry logic |

## 7. Challenges and Solutions

| Challenge | Cause | Our Solution |
|---|---|---|
| CrewAI reported missing template variables | LaTeX braces and examples were interpreted as prompt placeholders. | We revised task prompts and escaped or removed ambiguous template syntax. |
| The model returned fenced LaTeX | Generative output sometimes included Markdown formatting. | We added `strip_tex_fences()` before compilation. |
| Tables failed or overflowed | Generated column specifications were malformed or too wide. | We added table normalization and used `adjustbox` with bounded paragraph columns. |
| Hebrew text produced direction errors | Mixed RTL and LTR text was not consistently wrapped. | We added Hebrew post-processing and used `polyglossia`, `hebrew`, and `\textenglish{}`. |
| TikZ and math caused compilation errors | Generated syntax included reserved styles, missing math delimiters, or invalid alignment. | We added targeted TikZ, math, and syntax repair utilities with regression tests. |
| LLM requests occasionally failed | The hosted provider returned transient network or server errors. | We routed the crew through `ApiGatekeeper` with configured retry and rate-limit behavior. |
| Agent output varied between runs | LLM generation is non-deterministic. | We retained intermediate artifacts and moved graphing, repair, compilation, and final checks into deterministic code. |

## 8. Requirement Verification

| Evidence | Verified Result |
|---|---|
| Crew definition | Five agents and five tasks using `Process.sequential` |
| Final document | `outputs/pdf/article.pdf` |
| PDF format | 15 pages, A4, produced by LuaTeX 1.24.0 |
| Programmatic assignment checks | 13/13 passed |
| Sections | Abstract plus Introduction through Conclusion |
| Visuals | TikZ architecture figure and Matplotlib benchmark plot |
| Citations | 24 `\cite{}` commands |
| Bibliography | 24 inline `\bibitem` entries |
| Automated tests | 198 passed |
| Test coverage | 93.84%, above the configured 85% threshold |
| Static analysis | `uv run ruff check .` passes |

The 13-item validator checks the generated `.tex`, PDF existence, title page, table of
contents, headers and footers, section structure, table, formula, TikZ figure, citations,
Hebrew-English content, bibliography, and successful compilation.

## 9. Team Work Division

| Team member | Main responsibilities |
|---|---|
| Mohammad Selawe | Shared implementation, architecture review, testing, debugging, documentation, and submission verification |
| Moa’awiyah Hajajreh | Shared implementation, agent and pipeline development, LaTeX/PDF work, testing, debugging, and documentation |
| Both | Topic selection, prompt refinement, integration testing, output review, and final requirement verification |

We worked collaboratively rather than dividing the project into isolated parts. we both contributed to reviewing the architecture, debugging the agent-to-LaTeX integration, checking the generated article, and
preparing the submission.

## 10. Results

Our final output is a 15-page article about HULA and programmable data-plane load balancing.
It contains a cover, table of contents, headers and footers, technical sections, a TikZ
architecture diagram, a Python-generated performance plot, a comparison table, a
mathematical formula, a Hebrew-English conclusion, citations, and a bibliography.

The completed run produced the following artifact chain:

```text
outputs/
|-- research/research_brief.md
|-- drafts/draft.md
|-- reviewed/reviewed.md
|-- assets/graph_spec.json
|-- latex/article.tex
|-- latex/benchmark.png
`-- pdf/
    |-- article.pdf
    |-- agent_validation.md
    `-- validation_report.md
```

The recorded final run completed the agent pipeline, generated and injected the graph,
compiled the PDF, and passed all 13 internal validation checks.

## 11. Limitations

Our generated content still requires human review. An agent can produce a complete draft,
but we must check factual claims, reference quality, and whether estimated graph values are
described clearly. The output also depends on the availability and behavior of the selected
LLM provider.

LaTeX remains sensitive to small syntax errors, especially in mixed-language paragraphs,
tables, math, and TikZ. We reduced this risk with deterministic repair functions and tests,
but a new topic or an unusual model response can introduce a pattern that needs another
repair rule. We have primarily validated the full workflow on a limited set of article
topics rather than every possible academic domain.

## 12. Conclusion

We built a complete multi-agent document-generation workflow rather than a single text
prompt. CrewAI gives us clear responsibility boundaries, Markdown gives us inspectable
intermediate content, and deterministic Python and LaTeX tools give us reproducible visual
generation, compilation, and validation.

The main lesson we learned is that agentic generation works best when we combine it with
explicit artifacts, review stages, configuration, automated tests, and deterministic
post-processing. Our final HULA article demonstrates the required long-form structure,
technical visuals, mathematics, bilingual content, citations, and professional PDF output.

## 13. Installation and Usage

### System Requirements

- Python 3.12 is used by the repository’s `.python-version`; the package supports Python
  3.10 or newer.
- [`uv`](https://docs.astral.sh/uv/) manages dependencies and commands.
- LuaLaTeX must be available on `PATH`, normally through MiKTeX or TeX Live.
- The LaTeX installation must include fonts that support Hebrew.
- `ZHIPUAI_API_KEY` is required for the default article-generation provider.
- `ANTHROPIC_API_KEY` is required only for the secondary document Q&A command.

### Setup

```bash
uv sync --extra dev
```

Copy `.env.example` to `.env`, then replace the placeholders with the keys required for the
commands we plan to use:

```dotenv
ZHIPUAI_API_KEY=your-zhipuai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
APP_ENV=development
LOG_LEVEL=INFO
```

### Generate an Article

```bash
# Use the topic configured in config/config.yaml
uv run agent-ai-article

# Override the topic for this run
uv run agent-ai-article --topic "Your topic here"
```

The command writes intermediate artifacts under `outputs/` and returns the path to
`outputs/pdf/article.pdf`.

### Ask a Question About a Document

```bash
uv run agent-ai path/to/document.pdf "What are the main conclusions?"
```

This secondary SDK path converts a supported document to Markdown with MarkItDown and asks
the configured Anthropic model a question about the extracted text.

### Configuration

| File | What We Configure |
|---|---|
| `config/config.yaml` | Topic, article metadata, length targets, provider/model, outputs, pricing, and graph settings |
| `config/logging_config.json` | Logging format and levels |
| `config/rate_limits.json` | API queue, concurrency, retry, and rate-limit values |
| `config/setup.json` | Document conversion and Q&A model settings |

### Tests and Linting

```bash
uv run pytest -q
uv run ruff check .
```

At the time of this README update, we verified **198 passing tests**, **93.84% statement
coverage**, and **zero Ruff violations**.

### Project Structure

```text
src/
|-- main.py                 # Article-generation CLI
|-- sdk/sdk.py              # Public SDK for article generation and document Q&A
|-- pipeline.py             # Five-agent sequential CrewAI pipeline
|-- pipeline_steps.py       # Graph, compilation, and validation post-passes
|-- agents/factory.py       # Skill-backed CrewAI agent factory
|-- tasks/                  # Research, writing, review, LaTeX, and validation tasks
|-- shared/                 # Configuration, gatekeeper, and version
`-- utils/                  # Graph, LaTeX repair, compilation, and validation tools
skills/                     # Agent instructions stored as SKILL.md files
config/                     # Runtime configuration
outputs/                    # Generated research, Markdown, LaTeX, plot, PDF, and reports
tests/                      # Unit and integration tests
docs/                       # Architecture, requirements, plans, and prompt records
```

## Output Examples

We retained the project screenshots as examples of the pipeline execution and generated
document. They complement the reproducible artifacts linked at the top of this README.

| Example | Screenshot |
|---|---|
| Project output example 1 | <img width="720" alt="Project output example 1" src="https://github.com/user-attachments/assets/8731fd90-c873-4272-ac0b-5094955b1236" /> |
| Project output example 2 | <img width="720" alt="Project output example 2" src="https://github.com/user-attachments/assets/8e78e369-bd48-4586-ace4-c9f31cbe79a0" /> |
| Project output example 3 | <img width="720" alt="Project output example 3" src="https://github.com/user-attachments/assets/f94ddf66-bccb-4fe2-9da4-430aa6da8ca2" /> |
| Project output example 4 | <img width="720" alt="Project output example 4" src="https://github.com/user-attachments/assets/a580fa76-cc10-48f3-b316-7e817c55d08e" /> |
| Project output example 5 | <img width="720" alt="Project output example 5" src="https://github.com/user-attachments/assets/502d832c-8b9c-483a-b982-68075620ca14" /> |
| Project output example 6 | <img width="720" alt="Project output example 6" src="https://github.com/user-attachments/assets/f7d82eb0-290e-45d6-8f74-7ef335b8e938" /> |
| Project output example 7 | <img width="720" alt="Project output example 7" src="https://github.com/user-attachments/assets/ce1537d5-7cea-4370-8f91-1af2e6779e02" /> |
| Project output example 8 | <img width="720" alt="Project output example 8" src="https://github.com/user-attachments/assets/dbc350f1-6089-40bc-8b4d-500fc08b3595" /> |
| Project output example 9 | <img width="720" alt="Project output example 9" src="https://github.com/user-attachments/assets/3a024041-7a76-4644-8f2e-9f9e568265f6" /> |
| Project output example 10 | <img width="720" alt="Project output example 10" src="https://github.com/user-attachments/assets/755f0d24-fa91-4310-85f2-70107f60e154" /> |
| Project output example 11 | <img width="720" alt="Project output example 11" src="https://github.com/user-attachments/assets/1a288ca9-c54b-4935-a3f7-1d721f26c7f2" /> |

## License

We distribute this project under the MIT License.
