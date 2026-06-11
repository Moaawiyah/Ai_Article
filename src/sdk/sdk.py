"""AgentAISDK — single entry point for all external consumers."""

import logging
import time
from pathlib import Path

import anthropic

from shared.config import ConfigManager
from shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from shared.version import VERSION

logger = logging.getLogger(__name__)


class AgentAISDK:
    """Public SDK: converts documents to Markdown, queries them, generates articles.

    All GUI, CLI, and third-party consumers must use this class. No business
    logic is allowed outside the SDK layer.

    Input:
        config_dir (Path): optional override for the config directory.
    Output:
        Exposes process_document(), query_document(), generate_article(), get_version().
    Setup:
        process_document/query_document require ANTHROPIC_API_KEY.
        generate_article requires the provider key configured in config.yaml.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        """Bootstrap configuration, gatekeeper, and Anthropic client (lazy)."""
        kwargs = {"config_dir": config_dir} if config_dir else {}
        self._config = ConfigManager(**kwargs)
        self._gatekeepers: dict[str, ApiGatekeeper] = {}
        self._client: anthropic.Anthropic | None = None
        logger.info("AgentAISDK v%s initialised", VERSION)

    def _gatekeeper(self, service: str) -> ApiGatekeeper:
        """Return a cached gatekeeper configured for *service*."""
        if service in self._gatekeepers:
            return self._gatekeepers[service]
        rl = self._config.get_rate_limit(service)
        gatekeeper = ApiGatekeeper(
            RateLimitConfig(
                requests_per_minute=rl["requests_per_minute"],
                requests_per_hour=rl["requests_per_hour"],
                concurrent_max=rl["concurrent_max"],
                retry_after_seconds=rl["retry_after_seconds"],
                max_retries=rl["max_retries"],
                queue_max_depth=rl["queue_max_depth"],
                minute_window_seconds=rl["minute_window_seconds"],
                hour_window_seconds=rl["hour_window_seconds"],
            )
        )
        self._gatekeepers[service] = gatekeeper
        return gatekeeper

    def _anthropic(self) -> anthropic.Anthropic:
        """Lazy-create the Anthropic client only when document Q&A is invoked."""
        if self._client is None:
            api_key = ConfigManager.get_env("ANTHROPIC_API_KEY")
            if not api_key:
                raise OSError("ANTHROPIC_API_KEY environment variable is not set")
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def process_document(self, file_path: str | Path) -> str:
        """Convert *file_path* to Markdown text via markitdown.

        Input:  file_path — path to a supported document file.
        Output: Markdown string extracted from the document.
        """
        from markitdown import MarkItDown  # deferred import for speed

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")
        md = MarkItDown()
        result = md.convert(str(path))
        logger.info("Converted '%s' to Markdown (%d chars)", path.name, len(result.text_content))
        return result.text_content

    def query_document(self, markdown_text: str, question: str) -> str:
        """Ask *question* about *markdown_text* using Claude via the gatekeeper.

        Input:  markdown_text — document content as Markdown.
                question      — natural-language question.
        Output: Claude's answer as a plain string.
        """
        model = self._config.get_agent_model()
        max_tokens = self._config.get_max_tokens()

        client = self._anthropic()

        def _call() -> str:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": f"Document:\n\n{markdown_text}\n\nQuestion: {question}",
                    }
                ],
            )
            return response.content[0].text

        return self._gatekeeper("anthropic").execute(_call)

    def generate_article(self, topic: str | None = None) -> Path:
        """Run the five-agent CrewAI pipeline → benchmark figure → LuaLaTeX → validation.

        Input:  topic — optional override; falls back to ``config.yaml::article.topic``.
        Output: path to the generated ``article.pdf``.
        """
        from pipeline import build_crew
        from pipeline_steps import (
            compile_step,
            graph_step,
            print_token_usage,
            validate_step,
        )
        from utils.logger import get_logger, timed_stage

        crew, cfg = build_crew()
        log = get_logger("sdk.generate_article")
        run_topic = topic or cfg.topic
        t0 = time.perf_counter()

        log.info("=" * 60)
        log.info("ARTICLE GENERATION  — %s", run_topic)
        with timed_stage(log, "Agent pipeline (all 5 stages)"):
            # Route the crew run through the central gatekeeper (§5.1) so the
            # external LLM work is rate-limit-aware, retried on transient
            # failure, and logged like every other API call. CrewAI manages its
            # own per-call LLM traffic internally, so this gates the run as a
            # single unit.
            gatekeeper = self._gatekeeper(cfg.llm_provider)
            result = gatekeeper.execute(crew.kickoff, inputs={"topic": run_topic})

        print_token_usage(result, cfg, log)
        graph_step(cfg, log, gatekeeper)
        compile_step(cfg, log)
        validate_step(cfg, log)

        log.info("ARTICLE GENERATION DONE  (%.2fs)", time.perf_counter() - t0)
        return cfg.output_pdf / "article.pdf"

    def get_version(self) -> str:
        """Return the current SDK version string."""
        return VERSION


def main() -> None:
    """CLI entry point (script registered in pyproject.toml)."""
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="agent-ai document Q&A")
    parser.add_argument("file", help="Path to the document")
    parser.add_argument("question", help="Question to ask about the document")
    args = parser.parse_args()

    sdk = AgentAISDK()
    text = sdk.process_document(args.file)
    answer = sdk.query_document(text, args.question)
    print(answer)
