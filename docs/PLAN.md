# Architecture & Planning Document — agent_ai_HW2

## 1. Current Architecture

The project now has two surfaces:

- Top-level `src/sdk.py` keeps the existing document conversion and Claude Q&A SDK.
- Top-level `src/main.py` runs the CrewAI article generator for "Multi-Agent Collaboration Systems: Designing Teams of AI Agents".

The article pipeline intentionally works without RAG for now.

## 2. Article Pipeline

```
Researcher Agent
  -> outputs/research/research_brief.md
Writer Agent
  -> outputs/drafts/article_draft.md
Reviewer Agent
  -> outputs/reviewed/reviewed_article.md
LaTeX Formatter Agent
  -> outputs/latex/article.tex
PDF Validator Agent
  -> outputs/pdf/validation_report.md
```

The crew runs with `Process.sequential`, so each task receives the previous task output as context.

## 3. RAG Status

RAG is not part of the current implementation plan.

- Do not create `rag/indexer.py` yet.
- Do not create `rag/retriever.py` yet.
- The Researcher gathers and summarizes information directly.
- The Writer uses the Researcher output as context.
- A future RAG stage can be inserted between Researcher and Writer.

## 4. Local LLM

CrewAI uses local Ollama when configured:

- Default model: `qwen3:14b`
- Default base URL: `http://localhost:11434`
- Environment overrides: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, `USE_OLLAMA`

## 5. Directory Layout

```
src/
  main.py
  config.py
  agents/
    researcher.py
    writer.py
    reviewer.py
    latex_formatter.py
    pdf_validator.py
  tasks/
    research_task.py
    writing_task.py
    review_task.py
    latex_task.py
    validation_task.py
  utils/
    logger.py
    file_utils.py

outputs/
  research/
  drafts/
  reviewed/
  latex/
  pdf/
  assets/
```

## 6. Validation Requirements

The PDF Validator checks for:

- cover page
- table of contents
- chapters/sections
- headers/footers
- at least one image placeholder
- at least one Python-generated graph placeholder
- at least one table
- at least one mathematical formula
- Hebrew-English BiDi section
- bibliography
