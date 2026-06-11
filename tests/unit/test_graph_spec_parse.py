"""Unit tests for graph_spec_parse: llm_params, fallback, validation, IO."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from utils.graph_spec_parse import (
    brief_fallback,
    llm_params,
    log_spec,
    validate_and_normalize,
    write_spec,
)


def _cfg(provider):
    return SimpleNamespace(llm_provider=provider, llm_model="m", llm_base_url="http://x")


def test_llm_params_zhipuai(monkeypatch):
    monkeypatch.setenv("ZHIPUAI_API_KEY", "z-key")
    p = llm_params(_cfg("zhipuai"))
    assert p == {"model": "openai/m", "api_base": "http://x", "api_key": "z-key"}


def test_llm_params_ollama():
    assert llm_params(_cfg("ollama")) == {"model": "ollama_chat/m", "api_base": "http://x"}


def test_llm_params_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a-key")
    assert llm_params(_cfg("anthropic")) == {"model": "m", "api_key": "a-key"}


def test_llm_params_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "o-key")
    assert llm_params(_cfg("openai")) == {"model": "m", "api_key": "o-key"}


def test_llm_params_unknown_provider():
    assert llm_params(_cfg("mystery")) == {"model": "m"}


def test_brief_fallback_missing_path_returns_defaults(tmp_path):
    spec = brief_fallback(tmp_path / "nope.md", 5000)
    assert {"main", "arch_a", "arch_b"} <= spec.keys()


def test_brief_fallback_extracts_names_from_brief(tmp_path):
    brief = tmp_path / "brief.md"
    brief.write_text(
        "# Research Brief: HULA Balancing\n"
        "Comparative Architecture A: ECMP\n"
        "Comparative Architecture B: CONGA\n",
        encoding="utf-8",
    )
    spec = brief_fallback(brief, 5000)
    assert "ECMP" in spec["arch_a"]["name"]
    assert "CONGA" in spec["arch_b"]["name"]


def _valid_spec():
    base = {"name": "X", "median_queue": 1, "p95_queue": 2, "base_fct_ms": 0.1, "fct_slope": 0.01}
    return {"main": dict(base), "arch_a": dict(base), "arch_b": dict(base)}


def test_validate_and_normalize_defaults_provenance():
    spec = validate_and_normalize(_valid_spec())
    assert spec["main"]["data_basis"] == "estimated"  # default when absent
    assert spec["main"]["source"] == ""


def test_validate_and_normalize_keeps_measured_and_strips_source():
    s = _valid_spec()
    s["main"]["data_basis"] = "MEASURED"
    s["main"]["source"] = "  HULA, Fig. 8  "
    out = validate_and_normalize(s)
    assert out["main"]["data_basis"] == "measured"
    assert out["main"]["source"] == "HULA, Fig. 8"


def test_validate_and_normalize_missing_key_raises():
    s = _valid_spec()
    del s["arch_b"]
    with pytest.raises(ValueError, match="Missing key"):
        validate_and_normalize(s)


def test_validate_and_normalize_missing_field_raises():
    s = _valid_spec()
    del s["arch_a"]["p95_queue"]
    with pytest.raises(ValueError, match="Missing field"):
        validate_and_normalize(s)


def test_write_spec_writes_json(tmp_path):
    out = tmp_path / "sub" / "spec.json"
    write_spec(_valid_spec(), out)
    assert json.loads(out.read_text())["main"]["name"] == "X"


def test_write_spec_none_path_is_noop():
    write_spec(_valid_spec(), None)  # must not raise


def test_log_spec_runs(caplog):
    log_spec(validate_and_normalize(_valid_spec()), "unit-test")  # smoke: no raise
