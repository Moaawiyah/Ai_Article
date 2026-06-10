"""Loads agent skills from skills/<name>/SKILL.md files."""

import re
from dataclasses import dataclass
from pathlib import Path

# CrewAI interpolates {identifier} in backstories — replace with [identifier]
# so LaTeX examples like \begin{document} don't crash interpolate_only.
_CREWAI_VAR = re.compile(r'\{([A-Za-z_][A-Za-z0-9_\-]*)\}')

_SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"

# Words that need exact casing (checked case-insensitively)
_EXACT_CASE: dict[str, str] = {
    "pdf": "PDF",
    "llm": "LLM",
    "api": "API",
    "rag": "RAG",
    "ai": "AI",
    "latex": "LaTeX",
}


def skill_name_to_role(name: str) -> str:
    """Convert a snake_case skill name to a human-readable role string.

    Preserves known acronyms/special words (e.g. 'pdf_validator' → 'PDF Validator',
    'latex_formatter' → 'LaTeX Formatter').
    """
    return " ".join(_EXACT_CASE.get(w.lower(), w.title()) for w in name.split("_"))


@dataclass(frozen=True)
class Skill:
    name: str
    role: str
    description: str
    version: str
    body: str


def load_skill(name: str) -> Skill:
    """Parse skills/<name>/SKILL.md and return a Skill dataclass.

    The file must have YAML frontmatter delimited by '---' lines containing
    at minimum 'name', 'description', and 'version' keys.
    """
    path = _SKILLS_ROOT / name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")

    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text)

    raw_name = frontmatter.get("name", name)
    safe_body = _CREWAI_VAR.sub(r'<<\1>>', body.strip())
    return Skill(
        name=raw_name,
        role=frontmatter.get("role", skill_name_to_role(raw_name)),
        description=frontmatter.get("description", ""),
        version=frontmatter.get("version", "0.0.0"),
        body=safe_body,
    )


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body without a full YAML parser."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end = next((i for i, ln in enumerate(lines[1:], 1) if ln.strip() == "---"), None)
    if end is None:
        return {}, text

    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()

    body = "\n".join(lines[end + 1 :])
    return meta, body
