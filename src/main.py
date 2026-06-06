"""CrewAI article-generation entry point."""

import time

from crewai import Crew, Process

from agent_ai.shared.config import PipelineConfig
from agents.latex_formatter import build_latex_formatter
from agents.pdf_validator import build_pdf_validator
from agents.researcher import build_researcher
from agents.reviewer import build_reviewer
from agents.writer import build_writer
from tasks.latex_task import build_latex_task
from tasks.research_task import build_research_task
from tasks.review_task import build_review_task
from tasks.validation_task import build_validation_task
from tasks.writing_task import build_writing_task
from utils.file_utils import ensure_output_dirs
from utils.logger import configure_logger, get_logger, timed_stage
from utils.pdf_compiler import compile_pdf
from utils.tex_validator import validate


def build_crew(cfg: PipelineConfig | None = None) -> tuple[Crew, PipelineConfig]:
    """Build the sequential CrewAI pipeline from config.yaml."""
    cfg = cfg or PipelineConfig.load()
    ensure_output_dirs(cfg.output_dirs)

    logger = configure_logger(
        level    = cfg.log_level,
        log_dir  = cfg.log_dir,
        log_file = cfg.log_file,
    )

    logger.info("Pipeline config loaded")
    logger.info("  topic    : %s", cfg.topic)
    logger.info("  author   : %s", cfg.author_name)
    logger.info("  course   : %s", cfg.course_name)
    logger.info("  lecturer : %s", cfg.lecturer_name)
    logger.info("  llm      : %s/%s", cfg.llm_provider, cfg.llm_model)
    logger.info("  outputs  : %s", cfg.output_root)

    llm = cfg.build_llm()

    researcher      = build_researcher(llm)
    writer          = build_writer(llm)
    reviewer        = build_reviewer(llm)
    latex_formatter = build_latex_formatter(llm)
    pdf_validator   = build_pdf_validator(llm)

    research_task   = build_research_task(researcher, cfg)
    writing_task    = build_writing_task(writer, cfg, research_task)
    review_task     = build_review_task(reviewer, cfg, writing_task)
    latex_task      = build_latex_task(latex_formatter, cfg, review_task)
    validation_task = build_validation_task(pdf_validator, cfg, latex_task)

    logger.info("Crew assembled — 5 agents, 5 tasks, sequential process")
    crew = Crew(
        agents=[researcher, writer, reviewer, latex_formatter, pdf_validator],
        tasks =[research_task, writing_task, review_task, latex_task, validation_task],
        process=Process.sequential,
        verbose=True,
    )
    return crew, cfg


def _strip_tex_fences(tex_path) -> None:
    """Remove markdown fences and fix common LLM LaTeX mistakes in article.tex."""
    import re
    text = tex_path.read_text(encoding="utf-8")

    # Strip ```latex ... ``` wrappers
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip())

    # Fix \thispagestyle{} (empty arg) → \thispagestyle{empty}
    cleaned = re.sub(r"\\thispagestyle\s*\{\s*\}", r"\\thispagestyle{empty}", cleaned)

    # Fix \pagestyle{} (empty arg) → \pagestyle{fancy}
    cleaned = re.sub(r"\\pagestyle\s*\{\s*\}", r"\\pagestyle{fancy}", cleaned)

    # Fix \documentclass[...]{} (empty class) → {article}
    cleaned = re.sub(r"(\\documentclass(?:\[[^\]]*\])?)\{\s*\}", r"\1{article}", cleaned)

    # Fix \textsc{} in fancyfoot — small caps often unavailable with fontspec fonts
    cleaned = re.sub(r"\\fancyfoot(\[[^\]]*\])\{\\textsc\{([^}]+)\}\}", r"\\fancyfoot\1{\2}", cleaned)

    # Fix two-sided fancyhead positions [LE]/[RE]/[LO]/[RO] → [L]/[R] for one-sided article
    cleaned = re.sub(r"\\fancyhead\[([LR])[EO]\]", r"\\fancyhead[\1]", cleaned)

    # fancyhdr v5: move \pagestyle{fancy} + headers/footers to after \begin{document}
    # so \thispagestyle doesn't crash. Collect all fancyhdr setup lines from preamble.
    import re as _re
    _fhdr_preamble = _re.compile(
        r"(\\pagestyle\{fancy\}|\\fancyhf\{[^}]*\}|\\fancyhead[^\n]*|\\fancyfoot[^\n]*"
        r"|\\renewcommand\{\\(?:head|foot)rulewidth\}\{[^}]+\}"
        r"|\\setlength\{\\(?:head|foot)rulewidth\}\{[^}]+\})\n",
        _re.MULTILINE,
    )
    preamble_fhdr_lines = _fhdr_preamble.findall(cleaned)
    if preamble_fhdr_lines and r"\begin{document}" in cleaned:
        # Remove them from preamble
        cleaned = _fhdr_preamble.sub("", cleaned)
        # Re-inject after \begin{document}
        inject = "\n" + "\n".join(preamble_fhdr_lines) + "\n"
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + inject, 1)

    # Remove \thispagestyle{} (any arg) — avoids fancyhdr v5 crash on title page
    cleaned = _re.sub(r"\n?\\thispagestyle\{[^}]*\}", "", cleaned)

    # Fix \\ [Word...] in \author/\title — LaTeX parses \\[X] as linebreak with length X.
    # Escape the [ to {[} so it's treated as literal text, not an optional argument.
    cleaned = _re.sub(r"(\\\\)\s+\[", r"\1 {[}", cleaned)

    tex_path.write_text(cleaned + "\n", encoding="utf-8")


def _compile_step(cfg: PipelineConfig, log) -> bool:
    """Run LuaLaTeX on article.tex. Returns True on success (never raises)."""
    tex_path = cfg.output_latex / "article.tex"
    log_path = cfg.log_dir / "latex_compile.log"
    _strip_tex_fences(tex_path)

    log.info("─" * 60)
    log.info("PDF COMPILATION  — LuaLaTeX")
    log.info("  input  : %s", tex_path)
    log.info("  output : %s", cfg.output_pdf / "article.pdf")
    log.info("  passes : 2  (for TOC and cross-references)")

    with timed_stage(log, "LuaLaTeX compilation", str(cfg.output_pdf / "article.pdf")):
        result = compile_pdf(
            tex_path   = tex_path,
            output_dir = cfg.output_pdf,
            log_path   = log_path,
        )

    if result.success:
        log.info("✓ PDF ready: %s  (%.1fs)", result.pdf_path, result.elapsed)
    else:
        log.error("✗ PDF compilation failed")
        log.error("  error     : %s", result.error_summary)
        log.error("  log file  : %s", result.log_path)
        log.error("  .tex file : %s", result.tex_path)
        print()
        print("=" * 60)
        print("PDF COMPILATION FAILED")
        print(f"  Error     : {result.error_summary}")
        print(f"  Log file  : {result.log_path}")
        print(f"  .tex file : {result.tex_path}")
        print("=" * 60)

    return result.success


def _validate_step(cfg: PipelineConfig, log) -> None:
    """Run the programmatic 13-item validator and write validation_report.md."""
    tex_path     = cfg.output_latex / "article.tex"
    pdf_path     = cfg.output_pdf   / "article.pdf"
    log_path     = cfg.log_dir      / "latex_compile.log"
    report_path  = cfg.output_pdf   / "validation_report.md"

    log.info("─" * 60)
    log.info("VALIDATION  — 13-item assignment checklist")
    log.info("  tex      : %s", tex_path)
    log.info("  pdf      : %s", pdf_path)
    log.info("  report   : %s", report_path)

    with timed_stage(log, "Programmatic validation", str(report_path)):
        report = validate(
            tex_path     = tex_path,
            pdf_path     = pdf_path,
            log_path     = log_path,
            report_path  = report_path,
        )

    log.info("Result: %d/13 passed, %d failed", report.passed, report.failed)
    for check in report.checks:
        mark = "✓" if check.passed else "✗"
        log.info("  %s %s", mark, check.name)

    if report.all_passed:
        log.info("✅ All 13 requirements satisfied")
    else:
        log.warning("❌ %d requirement(s) failed — see %s", report.failed, report_path)

    print()
    print("=" * 60)
    print(f"VALIDATION: {report.passed}/13 passed")
    failed = [c for c in report.checks if not c.passed]
    if failed:
        print("Failed:")
        for c in failed:
            print(f"  ✗ {c.name}")
            print(f"    Fix: {c.fix}")
    else:
        print("All requirements satisfied.")
    print(f"Full report: {report_path}")
    print("=" * 60)


def main() -> None:
    """Run the full five-agent article pipeline with per-stage timing."""
    crew, cfg = build_crew()
    log = get_logger("main")

    agent_stages = [
        ("Researcher",      str(cfg.output_research / "research_brief.md")),
        ("Writer",          str(cfg.output_drafts   / "draft.md")),
        ("Reviewer",        str(cfg.output_reviewed / "reviewed.md")),
        ("LaTeX Formatter", str(cfg.output_latex    / "article.tex")),
        ("PDF Validator",   str(cfg.output_pdf      / "agent_validation.md")),
    ]

    log.info("=" * 60)
    log.info("PIPELINE START  — %s", cfg.topic)
    log.info("=" * 60)
    log.info("Stages in order:")
    for i, (name, path) in enumerate(agent_stages, 1):
        log.info("  %d. [%s] → %s", i, name, path)

    pipeline_start = time.perf_counter()

    # ── Step 1: all 5 agents (research → write → review → latex → validate) ─
    try:
        with timed_stage(log, "Agent pipeline (all 5 stages)"):
            crew.kickoff(inputs={"topic": cfg.topic})
    except Exception as exc:
        log.error("Agent pipeline failed: %s", exc)
        raise

    # ── Step 2: compile PDF from article.tex ─────────────────────────────────
    _compile_step(cfg, log)

    # ── Step 3: programmatic 13-item validation → validation_report.md ───────
    _validate_step(cfg, log)

    # ── Step 4: final summary ─────────────────────────────────────────────────
    total = time.perf_counter() - pipeline_start
    log.info("=" * 60)
    log.info("PIPELINE COMPLETE  (%.2fs)", total)
    log.info("Output files:")
    for name, path in agent_stages:
        log.info("  [%s] %s", name, path)
    log.info("  [PDF]        %s", cfg.output_pdf / "article.pdf")
    log.info("  [Validation] %s", cfg.output_pdf / "validation_report.md")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
