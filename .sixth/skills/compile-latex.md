# compile-latex

Compile the article LaTeX source into a PDF using the 4-pass lualatex + biber workflow.

## What this skill does

Runs the full LaTeX compilation sequence required for the bilingual Hebrew-English article:
1. `lualatex` (pass 1) — initial compilation
2. `biber` — resolve bibliography references
3. `lualatex` (pass 2) — incorporate bibliography
4. `lualatex` (pass 3) — finalize cross-references and TOC

## Prerequisites

- `lualatex` must be installed (MiKTeX or TeX Live). Check with `lualatex --version`.
- `biber` must be installed. Check with `biber --version`.
- `results/article/article.tex`, `body.tex`, and `article.bib` must exist.

## Steps

```bash
cd results/article

# Pass 1
lualatex --interaction=nonstopmode article.tex

# Bibliography
biber article

# Pass 2
lualatex --interaction=nonstopmode article.tex

# Pass 3 (final)
lualatex --interaction=nonstopmode article.tex
```

## After compiling

Check that `results/article/article.pdf` exists. Open it (on macOS: `open results/article/article.pdf`) and verify:
- [ ] Cover page renders with title, author, date, course, institution
- [ ] Table of contents with page numbers
- [ ] Headers (course + institution) and footer (page number) on every page
- [ ] Bar chart (`agents_growth.png`) renders
- [ ] Hebrew text flows right-to-left
- [ ] Mathematical formula renders
- [ ] Comparison table renders
- [ ] Bibliography with ≥8 references

## Troubleshooting

If lualatex fails, show the last 100 lines of `article.log` for diagnosis.
If biber fails, check that `\addbibresource{article.bib}` is in the preamble and `article.bib` exists in the same directory.
If Hebrew text does not render, verify that `FreeSerif` font is available: `fc-list | grep -i free`.
