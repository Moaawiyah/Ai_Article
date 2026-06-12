"""Shared pytest fixtures."""

import json
from pathlib import Path

import pytest

from shared.gatekeeper import ApiGatekeeper, RateLimitConfig


@pytest.fixture()
def rate_limit_config() -> RateLimitConfig:
    """Minimal rate-limit config for unit tests."""
    return RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        concurrent_max=5,
        retry_after_seconds=0,
        max_retries=2,
        queue_max_depth=10,
        minute_window_seconds=60,
        hour_window_seconds=3600,
    )


@pytest.fixture()
def gatekeeper(rate_limit_config: RateLimitConfig) -> ApiGatekeeper:
    """ApiGatekeeper wired with the test rate-limit config."""
    return ApiGatekeeper(rate_limit_config)


@pytest.fixture()
def config_dir(tmp_path: Path) -> Path:
    """Temporary config directory with minimal valid JSON files."""
    (tmp_path / "setup.json").write_text(
        json.dumps(
            {
                "version": "1.00",
                "app": {"name": "test-app", "env": "test", "log_level": "DEBUG"},
                "markitdown": {"enable_llm_descriptions": False, "supported_extensions": [".pdf"]},
                "agent": {"model": "claude-sonnet-4-6", "max_tokens": 512, "temperature": 0.0},
            }
        )
    )
    (tmp_path / "rate_limits.json").write_text(
        json.dumps(
            {
                "rate_limits": {
                    "version": "1.00",
                    "services": {
                        "default": {
                            "requests_per_minute": 30,
                            "requests_per_hour": 500,
                            "concurrent_max": 5,
                            "retry_after_seconds": 0,
                            "max_retries": 2,
                            "queue_max_depth": 10,
                            "minute_window_seconds": 60,
                            "hour_window_seconds": 3600,
                        }
                    },
                }
            }
        )
    )
    return tmp_path


@pytest.fixture()
def research_package():
    """Valid eight-section package for workflow tests."""
    source_ids = [f"ref{index}" for index in range(1, 9)]
    sections = []
    for index in range(1, 9):
        sections.append(
            {
                "section_id": f"section-{index}",
                "title": (
                    "Hebrew and English in AI Systems"
                    if index == 7
                    else "References"
                    if index == 8
                    else f"Section {index}"
                ),
                "order": index,
                "target_words": 650 if index < 8 else 0,
                "required_topics": ["complete approved source registry"]
                if index == 8
                else ["topic"],
                "source_ids": source_ids if index == 8 else ["ref1"],
                "artifact_ids": (
                    ["visual1"]
                    if index == 5
                    else ["visual2"]
                    if index == 2
                    else ["visual3"]
                    if index == 4
                    else []
                ),
                "acceptance_criteria": ["complete"],
                "bidi_required": index == 7,
            }
        )
    return {
        "research_markdown": "# Research\nGrounded notes.",
        "sources": [
            {
                "id": f"ref{index}",
                "authors": f"Author {index}",
                "title": f"Real Work {index}",
                "venue": "Venue",
                "year": 2020 + index,
                "url_or_doi": f"https://example.org/{index}",
                "verified_confidence": "high",
            }
            for index in range(1, 9)
        ],
        "sections": sections,
        "visuals": [
            {
                "id": "visual1",
                "type": "python_chart",
                "section_id": "section-5",
                "purpose": "Comparison",
                "data_basis": "estimated",
                "sources": ["ref1"],
                "caption": "Comparison chart",
            },
            {
                "id": "visual2",
                "type": "table",
                "section_id": "section-2",
                "purpose": "Compare related approaches",
                "data_basis": "measured",
                "sources": ["ref1", "ref2"],
                "caption": "Comparison of related approaches",
            },
            {
                "id": "visual3",
                "type": "tikz",
                "section_id": "section-4",
                "purpose": "Explain the system architecture",
                "data_basis": "conceptual",
                "sources": ["ref3"],
                "caption": "System architecture",
            },
        ],
    }
