"""Unit tests for utils.graph_generator (pure math helpers + PNG generation)."""

from __future__ import annotations

import builtins
import math
from pathlib import Path
from unittest.mock import patch

import numpy as np

from utils.graph_generator import (
    _FALLBACK_SERIES,
    _FILENAME,
    _fct_curve,
    _lognormal_params,
    generate_performance_graph,
)


def test_lognormal_params_known_values():
    mu, sigma = _lognormal_params(median=10, p95=50)
    assert mu == math.log(10)
    expected_sigma = (math.log(50) - math.log(10)) / 1.645
    assert sigma == expected_sigma
    assert sigma > 0


def test_lognormal_params_clamps_tiny_median():
    # median < 1 is clamped to 1 → mu == log(1) == 0.0
    mu, _ = _lognormal_params(median=0, p95=5)
    assert mu == 0.0


def test_lognormal_params_sigma_floor_when_p95_le_median():
    # p95 below median would give a non-positive sigma; floor is 0.01
    _, sigma = _lognormal_params(median=100, p95=10)
    assert sigma == 0.01


def test_fct_curve_flat_region_is_linear():
    load = np.array([0.0, 20.0, 40.0, 80.0])
    out = _fct_curve(load, base_fct=2.0, slope=0.01)
    expected = 2.0 + 0.01 * load  # no blow-up at or below 80% load
    assert np.allclose(out, expected)


def test_fct_curve_blows_up_above_saturation():
    out = _fct_curve(np.array([100.0]), base_fct=2.0, slope=0.0)
    # blowup = base*0.5*((100-80)/20)^2 = 2*0.5*1 = 1.0 → 2.0 + 1.0
    assert math.isclose(float(out[0]), 3.0)


def test_fct_curve_monotonic_non_decreasing():
    load = np.linspace(0, 100, 200)
    out = _fct_curve(load, base_fct=1.0, slope=0.02)
    assert np.all(np.diff(out) >= -1e-9)


def _spec():
    return {
        "main": {"name": "HULA", "median_queue": 12, "p95_queue": 45,
                 "base_fct_ms": 1.2, "fct_slope": 0.015},
        "arch_a": {"name": "ECMP", "median_queue": 60, "p95_queue": 200,
                   "base_fct_ms": 4.0, "fct_slope": 0.08},
        "arch_b": {"name": "CONGA", "median_queue": 120, "p95_queue": 380,
                   "base_fct_ms": 8.0, "fct_slope": 0.16},
    }


def test_generate_performance_graph_writes_png(tmp_path: Path):
    out = generate_performance_graph("My Topic", tmp_path, spec=_spec())
    assert out == _FILENAME
    written = tmp_path / _FILENAME
    assert written.exists()
    assert written.stat().st_size > 0


def test_generate_performance_graph_without_spec_uses_fallback(tmp_path: Path):
    out = generate_performance_graph("Topic", tmp_path, spec=None)
    assert out == _FILENAME
    assert (tmp_path / _FILENAME).exists()
    # sanity: fallback series remains the three named architectures
    assert [s["name"] for s in _FALLBACK_SERIES] == ["Main", "Architecture A", "Architecture B"]


def test_generate_performance_graph_truncates_long_topic(tmp_path: Path):
    long_topic = "x" * 120
    out = generate_performance_graph(long_topic, tmp_path, spec=_spec())
    assert out == _FILENAME
    assert (tmp_path / _FILENAME).exists()


def test_generate_performance_graph_returns_none_without_matplotlib(tmp_path: Path):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "matplotlib" or name.startswith("matplotlib"):
            raise ImportError("simulated missing matplotlib")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_fake_import):
        result = generate_performance_graph("Topic", tmp_path, spec=_spec())

    assert result is None
    assert not (tmp_path / _FILENAME).exists()
