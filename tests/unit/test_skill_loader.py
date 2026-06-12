"""Unit tests for skill_loader."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from utils.skill_loader import (
    Skill,
    _split_frontmatter,
    load_skill,
    skill_name_to_role,
)


def test_skill_name_to_role_acronyms():
    assert skill_name_to_role("submission_validator") == "Submission Validator"
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
    with patch("utils.skill_loader._SKILLS_ROOT", tmp_path), \
         pytest.raises(FileNotFoundError):
        load_skill("nonexistent")


def test_load_skill_parses_frontmatter(tmp_path):
    skill_dir = tmp_path / "my_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my_skill\ndescription: desc\nversion: 1.0\nrole: Custom Role\n---\nbody {var} here",
        encoding="utf-8",
    )
    with patch("utils.skill_loader._SKILLS_ROOT", tmp_path):
        s = load_skill("my_skill")
    assert isinstance(s, Skill)
    assert s.name == "my_skill"
    assert s.role == "Custom Role"
    assert s.version == "1.0"
    assert "<<var>>" in s.body


def test_all_six_workflow_skills_load():
    names = {
        "researcher",
        "source_verifier",
        "writer",
        "article_editor",
        "latex_formatter",
        "submission_validator",
    }
    assert {load_skill(name).name for name in names} == names
