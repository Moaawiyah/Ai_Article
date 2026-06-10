"""Unit tests for skill_loader, graph_fallback, compile_result, pdf_compiler."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agent_ai.utils.compile_result import CompileResult
from agent_ai.utils.graph_fallback import extract_arch_names, fallback_spec
from agent_ai.utils.graph_spec import _extract_brief_spec, generate_graph_spec
from agent_ai.utils.pdf_compiler import _extract_error, compile_pdf
from agent_ai.utils.skill_loader import (
    Skill,
    _split_frontmatter,
    load_skill,
    skill_name_to_role,
)

# ────────────────────────────────────────────────────────────────────
# skill_loader
# ────────────────────────────────────────────────────────────────────

def test_skill_name_to_role_acronyms():
    assert skill_name_to_role("pdf_validator") == "PDF Validator"
    assert skill_name_to_role("latex_formatter") == "LaTeX Formatter"
    assert skill_name_to_role("simple_writer") == "Simple Writer"


def test_split_frontmatter_with_valid_yaml():
    text = "---\nname: x\ndescription: y\n---\nBody text"
    meta, body = _split_frontmatter(text)
    assert meta["name"] == "x"
    assert meta["description"] == "y"
    assert "Body text" in body


def test_split_frontmatter_no_delimiters():
    meta, body = _split_frontmatter("just body")
    assert meta == {}
    assert body == "just body"


def test_split_frontmatter_unterminated():
    meta, body = _split_frontmatter("---\nname: x\nBody without close")
    assert meta == {}


def test_load_skill_missing_raises(tmp_path):
    with patch("agent_ai.utils.skill_loader._SKILLS_ROOT", tmp_path), \
         pytest.raises(FileNotFoundError):
        load_skill("nonexistent")


def test_load_skill_parses_frontmatter(tmp_path):
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my_skill\ndescription: desc\nversion: 1.0\nrole: Custom Role\n---\nbody {var} here",
        encoding="utf-8",
    )
    with patch("agent_ai.utils.skill_loader._SKILLS_ROOT", tmp_path):
        s = load_skill("my_skill")
    assert isinstance(s, Skill)
    assert s.name == "my_skill"
    assert s.role == "Custom Role"
    assert s.version == "1.0"
    assert "<<var>>" in s.body


# ────────────────────────────────────────────────────────────────────
# graph_fallback
# ────────────────────────────────────────────────────────────────────

def test_fallback_spec_has_all_keys():
    spec = fallback_spec()
    assert {"main", "arch_a", "arch_b"} <= spec.keys()
    for v in spec.values():
        assert {"name", "median_queue", "p95_queue", "base_fct_ms", "fct_slope"} <= v.keys()


def test_fallback_spec_independent_copies():
    a = fallback_spec()
    a["main"]["name"] = "MUTATED"
    b = fallback_spec()
    assert b["main"]["name"] != "MUTATED"


def test_extract_arch_names_from_brief():
    brief = (
        "# Research Brief: HULA Load Balancing\n\n"
        "Comparative Architecture A: **ECMP (legacy)**\n"
        "Comparative Architecture B: CONGA.\n"
    )
    main, a, b = extract_arch_names(brief)
    assert main == "HULA Load Bala"[:15] or main == "HULA Load Balan"[:15] or "HULA" in main
    assert "ECMP" in a
    assert "CONGA" in b


def test_extract_arch_names_fallback_when_missing():
    main, a, b = extract_arch_names("nothing here")
    assert main == "Main"
    assert a == "Architecture A"
    assert b == "Architecture B"


def test_extract_brief_spec_from_fenced_json():
    brief = """
## 3. Comparative Architecture Analysis

Comparative Architecture A: NVGRE
Comparative Architecture B: CONGA

```json
{
  "main": {
    "name": "HULA",
    "median_queue": 12,
    "p95_queue": 35,
    "base_fct_ms": 0.45,
    "fct_slope": 0.04,
    "data_basis": "measured",
    "source": "HULA, Fig. 8"
  },
  "arch_a": {
    "name": "NVGRE",
    "median_queue": 45,
    "p95_queue": 110,
    "base_fct_ms": 0.85,
    "fct_slope": 0.18,
    "source": "Estimated from NVGRE evaluation"
  },
  "arch_b": {
    "name": "CONGA",
    "median_queue": 70,
    "p95_queue": 190,
    "base_fct_ms": 1.05,
    "fct_slope": 0.22,
    "data_basis": "estimated",
    "source": "CONGA, approximate trend"
  }
}
```
"""
    spec = _extract_brief_spec(brief)

    assert spec is not None
    assert spec["main"]["name"] == "HULA"
    assert spec["main"]["data_basis"] == "measured"
    assert spec["arch_a"]["data_basis"] == "estimated"
    assert spec["arch_a"]["source"] == "Estimated from NVGRE evaluation"


def test_extract_brief_spec_returns_none_when_json_shape_is_wrong():
    brief = """
```json
{"unexpected": true}
```
"""
    assert _extract_brief_spec(brief) is None


def test_generate_graph_spec_prefers_embedded_researcher_block(tmp_path):
    brief_path = tmp_path / "research_brief.md"
    spec_out = tmp_path / "graph_spec.json"
    brief_path.write_text(
        """
# Research Brief: HULA

```json
{
  "main": {
    "name": "HULA",
    "median_queue": 12,
    "p95_queue": 35,
    "base_fct_ms": 0.45,
    "fct_slope": 0.04,
    "data_basis": "measured",
    "source": "HULA, Fig. 8"
  },
  "arch_a": {
    "name": "NVGRE",
    "median_queue": 45,
    "p95_queue": 110,
    "base_fct_ms": 0.85,
    "fct_slope": 0.18,
    "data_basis": "estimated",
    "source": "Estimated from NVGRE evaluation"
  },
  "arch_b": {
    "name": "CONGA",
    "median_queue": 70,
    "p95_queue": 190,
    "base_fct_ms": 1.05,
    "fct_slope": 0.22,
    "data_basis": "estimated",
    "source": "CONGA, approximate trend"
  }
}
```
""",
        encoding="utf-8",
    )
    cfg = SimpleNamespace(graph_spec_brief_chars=5000)

    with patch("agent_ai.utils.graph_spec._llm_params", side_effect=AssertionError("LLM path should not run")):
        spec = generate_graph_spec(brief_path=brief_path, cfg=cfg, spec_out=spec_out)

    assert spec["main"]["name"] == "HULA"
    assert spec["arch_b"]["name"] == "CONGA"
    assert '"data_basis": "measured"' in spec_out.read_text(encoding="utf-8")


# ────────────────────────────────────────────────────────────────────
# compile_result
# ────────────────────────────────────────────────────────────────────

def test_compile_result_str_success():
    cr = CompileResult(
        success=True,
        pdf_path=Path("/tmp/article.pdf"),
        tex_path=Path("/tmp/article.tex"),
        log_path=Path("/tmp/log"),
        elapsed=1.5,
        error_summary="",
    )
    assert "[PDF OK]" in str(cr)
    assert "1.5s" in str(cr)


def test_compile_result_str_failure():
    cr = CompileResult(
        success=False,
        pdf_path=None,
        tex_path=Path("/tmp/article.tex"),
        log_path=Path("/tmp/log"),
        elapsed=0.5,
        error_summary="! Missing $",
    )
    s = str(cr)
    assert "[PDF FAIL]" in s
    assert "Missing $" in s


# ────────────────────────────────────────────────────────────────────
# pdf_compiler
# ────────────────────────────────────────────────────────────────────

def test_extract_error_returns_first_bang_line():
    output = "Normal output\n! LaTeX Error: foo\nmore\n"
    assert _extract_error(output) == "! LaTeX Error: foo"


def test_extract_error_falls_back_to_last_line():
    output = "no bang\nlast line\n"
    assert _extract_error(output) == "last line"


def test_extract_error_empty():
    assert "Unknown" in _extract_error("")


def test_compile_pdf_missing_source(tmp_path):
    result = compile_pdf(
        tex_path=tmp_path / "missing.tex",
        output_dir=tmp_path / "out",
        log_path=tmp_path / "log.log",
    )
    assert result.success is False
    assert "not found" in result.error_summary


def test_compile_pdf_lualatex_missing(tmp_path):
    tex = tmp_path / "x.tex"
    tex.write_text("\\documentclass{article}\\begin{document}hi\\end{document}", encoding="utf-8")
    with patch("agent_ai.utils.pdf_compiler.subprocess.run", side_effect=FileNotFoundError):
        result = compile_pdf(
            tex_path=tex,
            output_dir=tmp_path / "out",
            log_path=tmp_path / "log.log",
        )
    assert result.success is False
    assert "lualatex not found" in result.error_summary
