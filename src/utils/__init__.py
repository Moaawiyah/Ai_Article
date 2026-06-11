"""Utility modules: file IO, logging, LaTeX post-processing, validation.

Submodules are imported directly (e.g. ``from utils.tex_validator import
validate``) to avoid eager-loading optional heavy dependencies at package
import time.
"""

from shared.version import VERSION

__version__ = VERSION
