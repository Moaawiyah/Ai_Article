"""Tests for graph rendering and numerical helpers."""

import numpy as np

from utils.graph_generator import (
    _fct_curve,
    _lognormal_params,
    generate_performance_graph,
)


def test_lognormal_params_are_valid():
    mu, sigma = _lognormal_params(10, 30)
    assert mu > 0
    assert sigma > 0


def test_fct_curve_grows_near_saturation():
    result = _fct_curve(np.array([20, 80, 100]), 1.0, 0.1)
    assert result[0] < result[1] < result[2]


def test_generate_performance_graph_writes_png(tmp_path):
    spec = {
        key: {
            "name": key,
            "median_queue": 10 + index,
            "p95_queue": 30 + index,
            "base_fct_ms": 1 + index,
            "fct_slope": 0.01 + index / 100,
        }
        for index, key in enumerate(("main", "arch_a", "arch_b"))
    }
    filename = generate_performance_graph("A long topic " * 8, tmp_path, spec)
    assert filename == "benchmark.png"
    assert (tmp_path / filename).stat().st_size > 0


def test_generate_performance_graph_uses_fallback(tmp_path):
    assert generate_performance_graph("Topic", tmp_path) == "benchmark.png"
