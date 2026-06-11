"""CrewAI task builders for the article pipeline."""

from shared.version import VERSION
from tasks.latex_task import build_latex_task
from tasks.research_task import build_research_task
from tasks.review_task import build_review_task
from tasks.validation_task import build_validation_task
from tasks.writing_task import build_writing_task

__version__ = VERSION
__all__ = [
    "build_research_task",
    "build_writing_task",
    "build_review_task",
    "build_latex_task",
    "build_validation_task",
]
