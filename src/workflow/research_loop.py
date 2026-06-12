"""Researcher and Source Verifier feedback loop."""

from __future__ import annotations

from workflow.parsing import parse_decision, parse_research_package
from workflow.prompts import research_prompt, verification_prompt


def run_research_loop(runner, cfg, storage, state, max_returns: int):
    """Run research verification with a finite return budget."""
    feedback = None
    package = None
    sections = None
    while state.research_returns <= max_returns:
        result = runner.run(
            "researcher",
            research_prompt(
                state.topic,
                cfg.artifact_instructions,
                cfg.min_pages,
                cfg.min_words,
                cfg.max_words,
                cfg.min_visuals,
                feedback,
                package,
            ),
            "A valid research-package JSON object.",
        )
        package, sections = parse_research_package(
            result.text,
            cfg.min_words,
            cfg.min_visuals,
        )
        decision_result = runner.run(
            "source_verifier",
            verification_prompt(package, cfg.min_visuals),
            "A JSON APPROVE or REVISE decision.",
        )
        decision = parse_decision(decision_result.text, {"APPROVE", "REVISE"})
        storage.write_json(storage.planning / "verification.json", decision)
        if decision["status"] == "APPROVE":
            storage.save_research(package, sections)
            return package, sections, result
        if state.research_returns >= max_returns:
            raise ValueError("Research package failed after the allowed verifier returns")
        state.research_returns += 1
        storage.save_state(state)
        feedback = decision
    raise ValueError("Research loop terminated unexpectedly")
