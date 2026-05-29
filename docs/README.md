# SoupsSnacks documentation

## Full-stack reference

| Format | File | Best for |
|--------|------|----------|
| **HTML (recommended)** | [`SOUPSSNACKS_FULL_STACK_REFERENCE.html`](SOUPSSNACKS_FULL_STACK_REFERENCE.html) | Reading in any browser — sidebar nav, styled tables, code blocks, dark mode |
| **Markdown (source)** | [`SOUPSSNACKS_FULL_STACK_REFERENCE.md`](SOUPSSNACKS_FULL_STACK_REFERENCE.md) | Editing the document |
| **PDF (optional)** | [`../SoupsSnacks_v2_Reference.pdf`](../SoupsSnacks_v2_Reference.pdf) | Printing or offline PDF readers |

### Open the HTML reference

Double-click the file, or from terminal:

```bash
open docs/SOUPSSNACKS_FULL_STACK_REFERENCE.html
```

The HTML file is **self-contained** (CSS embedded) — no internet connection or Cursor required.

Features:
- Sticky sidebar table of contents with jump links
- Syntax-highlighted code blocks
- Styled tables and ASCII diagrams
- Light / dark theme toggle (saved in browser)
- Mobile-friendly layout with menu button
- Print-friendly styles (File → Print)

### Regenerate after editing the Markdown

```bash
# HTML (requires pandoc — already on most dev machines)
python docs/build_reference_html.py

# PDF (optional)
pip install -t .pdf_build_deps fpdf2   # one-time
python docs/build_reference_pdf.py
```

### Supporting files

| File | Purpose |
|------|---------|
| `reference.css` | Theme styles (embedded into HTML on build) |
| `build_reference_html.py` | Markdown → standalone HTML |
| `build_reference_pdf.py` | Markdown → PDF at repo root |
