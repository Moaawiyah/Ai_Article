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


def ensure_tikz_bounded(tex: str) -> str:
    """Wrap each tikzpicture in an adjustbox so it can never exceed the text
    width or page height.

    TikZ uses absolute coordinates, so an LLM-generated diagram (e.g. a long row
    of nodes) can silently overflow the right/bottom margin. ``max width`` /
    ``max totalheight`` only scale the picture *down* when it is too large —
    diagrams that already fit are left untouched. Already-wrapped pictures
    (preceded by adjustbox/resizebox) are skipped to avoid double wrapping.
    """
    def _wrap(m: re.Match) -> str:
        block  = m.group(0)
        prefix = tex[max(0, m.start() - 40):m.start()]
        if "adjustbox" in prefix or "resizebox" in prefix:
            return block
        return (
            "\\adjustbox{max width=\\textwidth, max totalheight=0.9\\textheight}{%\n"
            + block + "\n}"
        )

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _wrap, tex, flags=re.DOTALL,
    )


def fix_tikz_reserved_styles(tex: str) -> str:
    """Rename user-defined TikZ styles whose names collide with reserved pgf keys.

    Only the style *definition* (``name/.style``) and style *references* inside
    option lists (``[name]`` / ``{name, ...}``) are renamed. Built-in usages are
    left untouched so the diagram still compiles: the ``\\node`` command, the
    ``node distance`` key, and ``every name/.style`` (a built-in, not a user
    style) are never rewritten.
    """
    def _fix_pic(m: re.Match) -> str:
        block = m.group(0)
        # User style names only — exclude built-in "every X/.style" definitions.
        defined = set(re.findall(r"(?<!every )(?<![\w])([A-Za-z]\w*)/\.style", block))
        for name in sorted(defined & _TIKZ_RESERVED):
            new = f"{name}node"
            esc = re.escape(name)
            # definition site (never the built-in "every name/.style")
            block = re.sub(r"(?<!every )(?<![\w])" + esc + r"(?=/\.style)", new, block)
            # style references as a standalone token inside [...] or {...} options
            block = re.sub(r"(?<=[\[{,])(\s*)" + esc + r"(\s*)(?=[\]},])",
                           r"\1" + new + r"\2", block)
        return block

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _fix_pic, tex, flags=re.DOTALL,
    )
