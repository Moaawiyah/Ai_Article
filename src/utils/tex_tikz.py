"""TikZ-specific repairs: node line-breaks and reserved-key style renames."""

from __future__ import annotations

import re

_TIKZ_RESERVED = {
    "id", "name", "node", "at", "to", "every", "scale", "shift",
    "label", "text", "draw", "fill", "color", "shape",
    "above", "below", "left", "right", "anchor",
}


def fix_tikz_node_linebreaks(tex: str) -> str:
    """Add align=center to TikZ nodes whose label contains \\\\ (not allowed in LR mode)."""
    def _fix_pic(m: re.Match) -> str:
        block = m.group(0)

        def _fix_node(nm: re.Match) -> str:
            full  = nm.group(0)
            opts  = nm.group(1)
            label = nm.group(2)
            if "\\\\" not in label:
                return full
            if opts and "align" in opts:
                return full
            if opts:
                new_opts = opts[:-1] + ", align=center]"
                return full.replace(opts, new_opts, 1)
            return full.replace("\\node ", "\\node[align=center] ", 1)

        return re.sub(
            r"\\node(\[[^\]]*\])?\s*(?:\([^)]*\))?\s*\{([^}]*)\}",
            _fix_node, block,
        )

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _fix_pic, tex, flags=re.DOTALL,
    )


def fix_tikz_reserved_styles(tex: str) -> str:
    """Rename user-defined TikZ styles whose names collide with reserved pgf keys."""
    def _fix_pic(m: re.Match) -> str:
        block   = m.group(0)
        defined = set(re.findall(r"([A-Za-z]\w*)/\.style", block))
        for name in sorted(defined & _TIKZ_RESERVED):
            new = f"{name}node"
            block = re.sub(rf"(?<![\w])({re.escape(name)})(?=/\.style)", new, block)
            block = re.sub(rf"(?<![\w/.])({re.escape(name)})(?![\w])", new, block)
        return block

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _fix_pic, tex, flags=re.DOTALL,
    )
