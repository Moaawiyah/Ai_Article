"""CrewAI article-generation entry point."""

import time

from agent_ai.shared.config import PipelineConfig
from pipeline import build_crew
from utils.logger import get_logger, timed_stage
from utils.pdf_compiler import compile_pdf
from utils.tex_fixer import strip_tex_fences
from utils.tex_validator import validate

_PRICE_INPUT    = 0.07   # $ per 1 000 prompt tokens
_PRICE_CACHED   = 0.01   # $ per 1 000 cached-input tokens
_PRICE_OUTPUT   = 0.40   # $ per 1 000 completion tokens


def _print_token_usage(result, log) -> None:
    usage = getattr(result, "token_usage", None)
    if usage is None:
        log.warning("Token usage not available from provider")
        return
    prompt  = getattr(usage, "prompt_tokens",        0) or 0
    cached  = getattr(usage, "cached_prompt_tokens",  0) or 0
    output  = getattr(usage, "completion_tokens",     0) or 0
    total   = getattr(usage, "total_tokens",           0) or 0
    cost    = (prompt * _PRICE_INPUT + cached * _PRICE_CACHED + output * _PRICE_OUTPUT) / 1000
    log.info("─" * 60)
    log.info("TOKEN USAGE & COST")
    log.info("  prompt tokens   : %d  ($%.4f)", prompt, prompt  * _PRICE_INPUT  / 1000)
    log.info("  cached tokens   : %d  ($%.4f)", cached, cached  * _PRICE_CACHED / 1000)
    log.info("  output tokens   : %d  ($%.4f)", output, output  * _PRICE_OUTPUT / 1000)
    log.info("  total tokens    : %d", total)
    log.info("  estimated cost  : $%.4f", cost)
    print(f"\nToken usage — prompt:{prompt}  cached:{cached}  output:{output}  "
          f"total:{total}  cost:${cost:.4f}")


def _graph_step(cfg: PipelineConfig, log) -> None:
    from utils.graph_generator import generate_performance_graph
    filename = generate_performance_graph(cfg.topic, cfg.output_latex)
    if filename is None:
        return
    tex_path = cfg.output_latex / "article.tex"
    figure_block = (
        "\n\\begin{figure}[H]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=0.85\\textwidth]{{{filename}}}\n"
        "  \\caption{Performance comparison: HULA vs.\\ ECMP under increasing network load.}\n"
        "  \\label{fig:perf}\n"
        "\\end{figure}\n"
    )
    source = tex_path.read_text(encoding="utf-8")
    source = source.replace("\\end{document}", figure_block + "\\end{document}")
    tex_path.write_text(source, encoding="utf-8")
    log.info("Graph injected → %s", cfg.output_latex / filename)


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
            result = crew.kickoff(inputs={"topic": cfg.topic})
    except Exception as exc:
        log.error("Agent pipeline failed: %s", exc)
        raise

    _print_token_usage(result, log)
    _graph_step(cfg, log)
    _compile_step(cfg, log)
    _validate_step(cfg, log)

    log.info("=" * 60)
    log.info("PIPELINE COMPLETE  (%.2fs)", time.perf_counter() - t0)
    log.info("  [PDF]        %s", cfg.output_pdf / "article.pdf")
    log.info("  [Validation] %s", cfg.output_pdf / "validation_report.md")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
