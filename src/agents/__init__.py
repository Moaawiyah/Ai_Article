"""CrewAI agent factories for the article pipeline."""

from agents.factory import build_agent
from shared.version import VERSION

__version__ = VERSION
__all__ = ["build_agent"]
