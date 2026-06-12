"""Execute one CrewAI agent/task stage through the API gatekeeper."""

from __future__ import annotations

from dataclasses import dataclass

from crewai import Crew, Process, Task

from agents.factory import build_agent
from shared.gatekeeper import ApiGatekeeper

_JSON_AGENTS = {"researcher", "source_verifier", "article_editor"}


@dataclass
class StageResult:
    """Text and token usage returned by one agent stage."""

    text: str
    token_usage: object | None = None


@dataclass
class TokenUsageTotals:
    """Aggregate provider token usage across all workflow stages."""

    prompt_tokens: int = 0
    cached_prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, usage) -> None:
        """Add a provider usage object when available."""
        if usage is None:
            return
        for field in vars(self):
            value = getattr(usage, field, 0) or 0
            setattr(self, field, getattr(self, field) + int(value))


class CrewStageRunner:
    """Build and execute isolated one-agent CrewAI stages."""

    def __init__(self, llm, gatekeeper: ApiGatekeeper) -> None:
        self.llm = llm
        self.gatekeeper = gatekeeper
        self.token_usage = TokenUsageTotals()

    def run(self, agent_name: str, description: str, expected_output: str) -> StageResult:
        """Run one agent task and normalize its result."""
        llm = self.llm
        if agent_name in _JSON_AGENTS and hasattr(llm, "model_copy"):
            llm = llm.model_copy(
                update={"response_format": {"type": "json_object"}}
            )
        agent = build_agent(agent_name, llm)
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
        )
        result = self.gatekeeper.execute(crew.kickoff)
        text = getattr(result, "raw", None) or str(result)
        usage = getattr(result, "token_usage", None)
        self.token_usage.add(usage)
        return StageResult(text=text, token_usage=usage)
