# Validation Report

| File | Path |
|---|---|
| article.tex | `outputs/latex/article.tex` |
| article.pdf | `outputs/pdf/article.pdf` |
| compile log | `logs/latex_compile.log` |

**Result: 12/13 checks passed**

🔴 **1 requirement(s) failed. See details below.**

---

### 1. article.tex exists
**Status:** ✅ PASS
**Evidence:** Found at `outputs/latex/article.tex` (19,496 bytes)

### 2. article.pdf exists
**Status:** ✅ PASS
**Evidence:** Found at `outputs/pdf/article.pdf` (20,251 bytes)

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
**Evidence:** 8 section(s): "Introduction", "Background and Motivation", "Bilingual Summary", "HULA Design Overview"…

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
**Evidence:** 7 `\cite{}` commands — e.g. `\cite{ref1}`, `\cite{ref4}`

### 11. English only
**Status:** ❌ FAIL
**Evidence:** Found: `polyglossia`
**Fix:** Remove all Hebrew/BiDi content — article must be English only

### 12. Bibliography
**Status:** ✅ PASS
**Evidence:** `\begin{thebibliography}` with 8 `\bibitem` entries

### 13. LaTeX compilation
**Status:** ✅ PASS
**Evidence:** PDF present at `outputs/pdf/article.pdf`
