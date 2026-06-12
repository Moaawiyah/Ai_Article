"""Article-generation CLI entry point — thin wrapper over ``AgentAISDK``.

Per §4.1 of the guidelines, all business logic lives in the SDK layer. This
module only parses CLI args and delegates to ``sdk.generate_article``.
"""

from __future__ import annotations

import argparse
import logging

from sdk.sdk import AgentAISDK
from shared.pipeline_config import PipelineConfig


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

    import os
    if os.environ.get("AGENT_LLM_PROVIDER"):
        print(f"Using pre-configured provider: {os.environ.get('AGENT_LLM_PROVIDER')}")
    else:
        print("\nSelect LLM Provider for Article Generation:")
        print("1. Ollama (Local)")
        print("2. OpenAI")
        print("3. Google Gemini")
        print("4. ZhipuAI (GLM)")
        print("5. Groq")
        choice = input("Enter choice (1-5) [1]: ").strip() or "1"

        if choice == "1":
            os.environ["AGENT_LLM_PROVIDER"] = "ollama"
            model = input("Enter Ollama model [llama3]: ").strip() or "llama3"
            os.environ["AGENT_LLM_MODEL"] = model
            os.environ["AGENT_LLM_BASE_URL"] = "http://localhost:11434"
            print(f"\n[!] Please ensure Ollama is running and you have run 'ollama pull {model}'")
        elif choice == "2":
            os.environ["AGENT_LLM_PROVIDER"] = "openai"
            model = input("Enter OpenAI model [gpt-4o]: ").strip() or "gpt-4o"
            os.environ["AGENT_LLM_MODEL"] = model
            if not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = input("Enter OPENAI_API_KEY: ").strip()
        elif choice == "3":
            os.environ["AGENT_LLM_PROVIDER"] = "gemini"
            model = input("Enter Gemini model [gemini-1.5-pro]: ").strip() or "gemini-1.5-pro"
            os.environ["AGENT_LLM_MODEL"] = model
            if not os.environ.get("GEMINI_API_KEY"):
                os.environ["GEMINI_API_KEY"] = input("Enter GEMINI_API_KEY: ").strip()
        elif choice == "4":
            os.environ["AGENT_LLM_PROVIDER"] = "zhipuai"
            model = input("Enter ZhipuAI model [glm-4]: ").strip() or "glm-4"
            os.environ["AGENT_LLM_MODEL"] = model
            os.environ["AGENT_LLM_BASE_URL"] = "https://api.z.ai/api/paas/v4/"
            if not os.environ.get("ZHIPUAI_API_KEY"):
                os.environ["ZHIPUAI_API_KEY"] = input("Enter ZHIPUAI_API_KEY: ").strip()
        elif choice == "5":
            os.environ["AGENT_LLM_PROVIDER"] = "groq"
            model = input("Enter Groq model [llama3-70b-8192]: ").strip() or "llama3-70b-8192"
            os.environ["AGENT_LLM_MODEL"] = model
            if not os.environ.get("GROQ_API_KEY"):
                os.environ["GROQ_API_KEY"] = input("Enter GROQ_API_KEY: ").strip()
        else:
            print("Invalid choice, defaulting to Ollama.")
            os.environ["AGENT_LLM_PROVIDER"] = "ollama"
            os.environ["AGENT_LLM_MODEL"] = "llama3"
            os.environ["AGENT_LLM_BASE_URL"] = "http://localhost:11434"
            print("\n[!] Please ensure Ollama is running and you have run 'ollama pull llama3'")

    sdk = AgentAISDK()

    topic = args.topic
    if not topic:
        default_topic = PipelineConfig.load().topic
        print(f"\nEnter Article Topic (Leave blank for default: '{default_topic}'):")
        topic = input("> ").strip() or default_topic

    pdf_path = sdk.generate_article(topic=topic)
    print(f"\nArticle PDF: {pdf_path}")


if __name__ == "__main__":
    main()
