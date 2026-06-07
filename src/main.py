"""CrewAI article-generation entry point."""

import time

from agent_ai.shared.config import PipelineConfig
from pipeline import build_crew
from utils.logger import get_logger, timed_stage
from utils.pdf_compiler import compile_pdf
from utils.tex_fixer import strip_tex_fences
from utils.tex_validator import validate


def _compile_step(cfg: PipelineConfig, log) -> bool:
    tex_path = cfg.output_latex / "article.tex"
    log_path = cfg.log_dir / "latex_compile.log"
    strip_tex_fences(tex_path)

    log.info("─" * 60)
    log.info("PDF COMPILATION  — LuaLaTeX")
    log.info("  input  : %s", tex_path)
    log.info("  output : %s", cfg.output_pdf / "article.pdf")

    with timed_stage(log, "LuaLaTeX compilation", str(cfg.output_pdf / "article.pdf")):
        result = compile_pdf(tex_path=tex_path, output_dir=cfg.output_pdf, log_path=log_path)

    if result.success:
        log.info("✓ PDF ready: %s  (%.1fs)", result.pdf_path, result.elapsed)
    else:
        log.error("✗ PDF compilation failed — %s", result.error_summary)
        log.error("  log: %s  tex: %s", result.log_path, result.tex_path)
        print(f"\n{'='*60}\nPDF COMPILATION FAILED\n  Error: {result.error_summary}")
        print(f"  Log: {result.log_path}\n{'='*60}")
    return result.success


def _validate_step(cfg: PipelineConfig, log) -> None:
    tex_path    = cfg.output_latex / "article.tex"
    pdf_path    = cfg.output_pdf   / "article.pdf"
    log_path    = cfg.log_dir      / "latex_compile.log"
    report_path = cfg.output_pdf   / "validation_report.md"

    log.info("─" * 60)
    log.info("VALIDATION  — 13-item assignment checklist")

    with timed_stage(log, "Programmatic validation", str(report_path)):
        report = validate(tex_path=tex_path, pdf_path=pdf_path,
                          log_path=log_path, report_path=report_path)

    log.info("Result: %d/13 passed, %d failed", report.passed, report.failed)
    for check in report.checks:
        log.info("  %s %s", "✓" if check.passed else "✗", check.name)

    print(f"\n{'='*60}\nVALIDATION: {report.passed}/13 passed")
    failed = [c for c in report.checks if not c.passed]
    if failed:
        for c in failed:
            print(f"  ✗ {c.name}\n    Fix: {c.fix}")
    else:
        print("All requirements satisfied.")
    print(f"Full report: {report_path}\n{'='*60}")


def main() -> None:
    """Run the full five-agent article pipeline."""
    crew, cfg = build_crew()
    log = get_logger("main")

    stages = [
        ("Researcher",      str(cfg.output_research / "research_brief.md")),
        ("Writer",          str(cfg.output_drafts   / "draft.md")),
        ("Reviewer",        str(cfg.output_reviewed / "reviewed.md")),
        ("LaTeX Formatter", str(cfg.output_latex    / "article.tex")),
        ("PDF Validator",   str(cfg.output_pdf      / "agent_validation.md")),
    ]

    log.info("=" * 60)
    log.info("PIPELINE START  — %s", cfg.topic)
    for i, (name, path) in enumerate(stages, 1):
        log.info("  %d. [%s] → %s", i, name, path)

    t0 = time.perf_counter()

    try:
        with timed_stage(log, "Agent pipeline (all 5 stages)"):
            crew.kickoff(inputs={"topic": cfg.topic})
    except Exception as exc:
        log.error("Agent pipeline failed: %s", exc)
        raise

    _compile_step(cfg, log)
    _validate_step(cfg, log)

    log.info("=" * 60)
    log.info("PIPELINE COMPLETE  (%.2fs)", time.perf_counter() - t0)
    log.info("  [PDF]        %s", cfg.output_pdf / "article.pdf")
    log.info("  [Validation] %s", cfg.output_pdf / "validation_report.md")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
