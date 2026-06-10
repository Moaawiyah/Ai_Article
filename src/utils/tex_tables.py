"""Table-float wrapping and column-spec normalization."""

from __future__ import annotations

import re


def fix_tables(tex: str) -> str:
    """Normalize LaTeX tables so wide tabular blocks fit on the page.

    - Convert figure floats that only contain tabular content into table floats.
    - Wrap tabular blocks in adjustbox unless they are already width-limited.
    """
    def _retag_figure(m: re.Match) -> str:
        block = m.group(0)
        if r"\begin{tabular}" not in block:
            return block
        if any(token in block for token in (r"\includegraphics", r"\begin{tikzpicture}")):
            return block
        block = block.replace(r"\begin{figure}", r"\begin{table}", 1)
        block = block.replace(r"\end{figure}", r"\end{table}", 1)
        return block

    tex = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', _retag_figure, tex, flags=re.DOTALL)

    def _wrap(m: re.Match) -> str:
        block = m.group(0)
        if r'\adjustbox' in block or r'\resizebox' in block:
            return block
        block = re.sub(
            r'(\\begin\{tabular\})',
            r'  \\adjustbox{max width=\\textwidth}{\n  \1',
            block, count=1,
        )
        block = re.sub(r'(\\end\{tabular\})', r'\1\n  }', block, count=1)
        return block

    return re.sub(r'\\begin\{table\}.*?\\end\{table\}', _wrap, tex, flags=re.DOTALL)


def fix_table_math(tex: str) -> str:
    """Wrap bare superscripts (e.g. 2^24) inside tabular cells in math mode.

    The tabular environment is a protected region, so fix_text_mode_math skips
    it — but LLM-generated cells can still contain bare ^ superscripts that crash
    compilation with 'Missing $ inserted'. We only touch superscripts here and
    leave & / \\ column and row separators untouched.
    """
    def _wrap_super(body: str) -> str:
        body = re.sub(r"(?<!\$)(\w+)\^\{([^}]*)\}(?!\$)", r"$\1^{\2}$", body)
        body = re.sub(r"(?<!\$)(\w+)\^(\w+)(?!\$)",       r"$\1^{\2}$", body)
        return body

    def _fix(m: re.Match) -> str:
        return m.group(1) + _wrap_super(m.group(2)) + m.group(3)

    return re.sub(
        r"(\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\})(.*?)(\\end\{tabular\})",
        _fix, tex, flags=re.DOTALL,
    )


def fix_tabular_colspec(tex: str) -> str:
    """Convert bare p/m/b column specs (no width arg) to p{3.5cm} so text wraps.

    Leaves p{3cm} and similar already-sized specs untouched.
    """
    def _fix(m: re.Match) -> str:
        spec = m.group(1)
        out: list[str] = []
        i = 0
        while i < len(spec):
            ch = spec[i]
            if ch == "{":
                j = spec.find("}", i)
                out.append(spec[i:j + 1])
                i = j + 1
            elif ch in "pmb":
                nxt = spec[i + 1] if i + 1 < len(spec) else ""
                out.append(ch if nxt in ("{", "[") else "p{3.5cm}")
                i += 1
            else:
                out.append(ch)
                i += 1
        return "\\begin{tabular}{" + "".join(out) + "}"

    return re.sub(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}", _fix, tex)
