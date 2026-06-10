"""Deterministic post-passes that run after the CrewAI crew finishes.

Each function is a thin orchestrator over a utility module so ``main.py``
stays under the 150-LoC budget.
"""

from __future__ import annotations

import re

from shared.config import PipelineConfig
from utils.graph_generator import generate_performance_graph
from utils.graph_spec import generate_graph_spec
from utils.logger import timed_stage
from utils.pdf_compiler import compile_pdf
from utils.tex_fixer import strip_tex_fences
from utils.tex_validator import validate


_TEX_SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def _tex_escape(text: str) -> str:
    """Escape LaTeX special characters in free text (e.g. LLM-supplied sources)."""
    return "".join(_TEX_SPECIALS.get(ch, ch) for ch in text)


def print_token_usage(result, cfg: PipelineConfig, log) -> None:
    """Log token counts and an estimated price for the crew run.

    Prices come from ``cfg.price_*`` (loaded from ``config.yaml`` → ``pricing``).
    """
    usage = getattr(result, "token_usage", None)
    if usage is None:
        log.warning("Token usage not available from provider")
        return
    prompt  = getattr(usage, "prompt_tokens",        0) or 0
    cached  = getattr(usage, "cached_prompt_tokens", 0) or 0
    output  = getattr(usage, "completion_tokens",    0) or 0
    total   = getattr(usage, "total_tokens",         0) or 0
    p_in, p_cache, p_out = cfg.price_input_per_1m, cfg.price_cached_per_1m, cfg.price_output_per_1m
    cost    = (prompt * p_in + cached * p_cache + output * p_out) / 1_000_000
    log.info("─" * 60)
    log.info("TOKEN USAGE & COST")
    log.info("  prompt tokens   : %d  ($%.6f)", prompt, prompt * p_in    / 1_000_000)
    log.info("  cached tokens   : %d  ($%.6f)", cached, cached * p_cache / 1_000_000)
    log.info("  output tokens   : %d  ($%.6f)", output, output * p_out   / 1_000_000)
    log.info("  total tokens    : %d", total)
    log.info("  estimated cost  : $%.4f", cost)
    print(f"\nToken usage — prompt:{prompt}  cached:{cached}  output:{output}  "
          f"total:{total}  cost:${cost:.6f}")


def graph_step(cfg: PipelineConfig, log) -> None:
    """Generate the benchmark figure and inject it into the Evaluation section."""
    log.info("─" * 60)
    log.info("GRAPH GENERATION  — researcher/LLM spec + matplotlib")
    spec = generate_graph_spec(
        brief_path=cfg.output_research / "research_brief.md",
        cfg=cfg,
        spec_out=cfg.output_assets / "graph_spec.json",
    )
    filename = generate_performance_graph(cfg.topic, cfg.output_latex, spec=spec)
    if filename is None:
        return
    tex_path = cfg.output_latex / "article.tex"
    name_a = spec["arch_a"]["name"]
    name_b = spec["arch_b"]["name"]
    series = (spec["main"], spec["arch_a"], spec["arch_b"])
    all_measured = all(s.get("data_basis") == "measured" for s in series)
    sources = ", ".join(
        dict.fromkeys(  # de-dupe, preserve order
            s["source"] for s in series if s.get("source")
        )
    )
    if all_measured and sources:
        basis_note = f"Based on published measurements ({_tex_escape(sources)})."
    elif sources:
        basis_note = (
            f"Curves combine published measurements and literature-informed "
            f"estimates ({_tex_escape(sources)})."
        )
    else:
        basis_note = "Curves are illustrative, literature-informed estimates."
    caption = (
        f"Left: CDF of bottleneck queue length. "
        f"Right: average FCT vs.\\ network load. "
        f"Comparison of {spec['main']['name']} vs.\\ {name_a} vs.\\ {name_b}. "
        f"{basis_note}"
    )
    figure_block = (
        "\n\\begin{figure}[H]\n"
        "  \\centering\n"
        f"  \\includegraphics[width=\\textwidth]{{{filename}}}\n"
        f"  \\caption{{{caption}}}\n"
        "  \\label{fig:perf}\n"
        "\\end{figure}\n"
    )
    source = tex_path.read_text(encoding="utf-8")

    eval_m = re.search(r'\\section\{[^}]*[Ee]valuation[^}]*\}', source)
    if eval_m:
        rest = source[eval_m.end():]
        next_m = re.search(r'\n\\section\{', rest)
        if next_m:
            pos = eval_m.end() + next_m.start()
            source = source[:pos] + "\n" + figure_block + source[pos:]
        else:
            bib = source.find("\\begin{thebibliography}")
            pos = bib if bib != -1 else source.rfind("\\end{document}")
            source = source[:pos] + figure_block + "\n" + source[pos:]
    else:
        bib = source.find("\\begin{thebibliography}")
        if bib != -1:
            source = source[:bib] + figure_block + "\n" + source[bib:]
        else:
            source = source.replace("\\end{document}", figure_block + "\\end{document}")

    tex_path.write_text(source, encoding="utf-8")
    log.info("Graph injected into Evaluation section → %s", cfg.output_latex / filename)


def compile_step(cfg: PipelineConfig, log) -> bool:
    """Run LuaLaTeX over article.tex and surface success/failure."""
    tex_path = cfg.output_latex / "article.tex"
    log_path = cfg.log_dir / "latex_compile.log"
    strip_tex_fences(tex_path, topic=cfg.topic)

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


def validate_step(cfg: PipelineConfig, log) -> None:
    """Run the 13-item assignment checklist and print results."""
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
