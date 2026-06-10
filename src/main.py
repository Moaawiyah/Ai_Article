"""Article-generation CLI entry point — thin wrapper over ``AgentAISDK``.

Per §4.1 of the guidelines, all business logic lives in the SDK layer. This
module only parses CLI args and delegates to ``sdk.generate_article``.
"""

from __future__ import annotations

import argparse
import logging

from sdk.sdk import AgentAISDK


def main() -> None:
    """CLI: ``agent-ai-article [--topic "..."]`` → produces ``outputs/pdf/article.pdf``."""
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Generate an academic article PDF.")
    parser.add_argument(
        "--topic",
        default=None,
        help="Article topic (defaults to config.yaml::article.topic).",
    )
    args = parser.parse_args()

    sdk = AgentAISDK()
    pdf_path = sdk.generate_article(topic=args.topic)
    print(f"\nArticle PDF: {pdf_path}")


if __name__ == "__main__":
    main()
