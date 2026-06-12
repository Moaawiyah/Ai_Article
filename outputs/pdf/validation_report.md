# Validation Report

| File | Path |
|---|---|
| article.tex | `outputs/latex/article.tex` |
| article.pdf | `outputs/pdf/article.pdf` |
| compile log | `logs/latex_compile.log` |

**Result: 13/13 checks passed**

🟢 **All requirements satisfied. Ready for submission.**

---

### 1. article.tex exists
**Status:** ✅ PASS
**Evidence:** Found at `outputs/latex/article.tex` (36,472 bytes)

### 2. article.pdf exists
**Status:** ✅ PASS
**Evidence:** Found at `outputs/pdf/article.pdf` (326,977 bytes)

### 3. Title page
**Status:** ✅ PASS
**Evidence:** `\title{}` and `\maketitle` present — "HULA: Scalable Load Balancing\\Using Programmable Data Plane..."

### 4. Table of contents
**Status:** ✅ PASS
**Evidence:** `\tableofcontents` command present

### 5. Headers/footers
**Status:** ✅ PASS
**Evidence:** `fancyhdr` loaded with `\fancyhead`/`\fancyfoot` definitions

### 6. Sections/chapters
**Status:** ✅ PASS
**Evidence:** 10 section(s): "Abstract", "1. Introduction", "2. Background and Motivation", "3. System Architecture"…

### 7. Table
**Status:** ✅ PASS
**Evidence:** 1 `tabular` environment(s) found

### 8. Mathematical formula
**Status:** ✅ PASS
**Evidence:** 1 `equation` + 0 `align` environment(s)

### 9. TikZ figure
**Status:** ✅ PASS
**Evidence:** `\begin{tikzpicture}[`

### 10. Inline citations
**Status:** ✅ PASS
**Evidence:** 24 `\cite{}` commands — e.g. `\cite{ref1}`, `\cite{ref2}`

### 11. English and Hebrew
**Status:** ✅ PASS
**Evidence:** `\begin{hebrew}` block present with no Hebrew leaking outside it

### 12. Bibliography
**Status:** ✅ PASS
**Evidence:** `\begin{thebibliography}` with 24 `\bibitem` entries

### 13. LaTeX compilation
**Status:** ✅ PASS
**Evidence:** PDF present at `outputs/pdf/article.pdf`
