"""Regions of LaTeX source that other post-processors must never modify.

Math, TikZ, tabular, verbatim, bibliography, and Hebrew environments are
already valid LaTeX as emitted by the formatter and must stay untouched when
the syntax/Hebrew passes scan the surrounding text.
"""

from __future__ import annotations

import re

_PROTECTED = re.compile(
    r"\$\$.*?\$\$"
    r"|\$[^$]*?\$"
    r"|\\\[.*?\\\]"
    r"|\\\(.*?\\\)"
    r"|\\begin\{(equation|align|aligned|tikzpicture|tabular|"
    r"verbatim|lstlisting|thebibliography|hebrew)\*?\}.*?"
    r"\\end\{\1\*?\}",
    re.DOTALL,
)

_PROTECTED_HEB = re.compile(
    _PROTECTED.pattern + r"|\\texthebrew\{[^{}]*\}",
    re.DOTALL,
)
