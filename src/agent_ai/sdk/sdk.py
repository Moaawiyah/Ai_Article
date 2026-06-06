"""AgentAISDK — single entry point for all external consumers."""

import logging
from pathlib import Path

import anthropic

from agent_ai.shared.config import ConfigManager
from agent_ai.shared.gatekeeper import ApiGatekeeper, RateLimitConfig
from agent_ai.shared.version import VERSION

logger = logging.getLogger(__name__)


class AgentAISDK:
    """Public SDK: converts documents to Markdown and queries them with Claude.

    All GUI, CLI, and third-party consumers must use this class. No business
    logic is allowed outside the SDK layer.

    Input:
        config_dir (Path): optional override for the config directory.
    Output:
        Exposes process_document() and query_document() methods.
    Setup:
        Requires ANTHROPIC_API_KEY environment variable.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        """Bootstrap configuration, gatekeeper, and Anthropic client."""
        kwargs = {"config_dir": config_dir} if config_dir else {}
        self._config = ConfigManager(**kwargs)
        rl = self._config.get_rate_limit("anthropic")
        self._gatekeeper = ApiGatekeeper(
            RateLimitConfig(
                requests_per_minute=rl["requests_per_minute"],
                requests_per_hour=rl["requests_per_hour"],
                concurrent_max=rl["concurrent_max"],
                retry_after_seconds=rl["retry_after_seconds"],
                max_retries=rl["max_retries"],
            )
        )
        api_key = ConfigManager.get_env("ANTHROPIC_API_KEY")
        if not api_key:
            raise OSError("ANTHROPIC_API_KEY environment variable is not set")
        self._client = anthropic.Anthropic(api_key=api_key)
        logger.info("AgentAISDK v%s initialised", VERSION)

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

        def _call() -> str:
            response = self._client.messages.create(
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

        return self._gatekeeper.execute(_call)

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
