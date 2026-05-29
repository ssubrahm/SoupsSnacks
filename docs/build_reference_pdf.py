#!/usr/bin/env python3
"""
Build SoupsSnacks_v2_Reference.pdf from SOUPSSNACKS_FULL_STACK_REFERENCE.md

Usage (from repo root or docs/):
    python docs/build_reference_pdf.py

Requires: fpdf2 (install into .pdf_build_deps via pip install -t .pdf_build_deps fpdf2)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
MD_FILE = DOCS_DIR / "SOUPSSNACKS_FULL_STACK_REFERENCE.md"
PDF_FILE = REPO_ROOT / "SoupsSnacks_v2_Reference.pdf"
DEPS_DIR = REPO_ROOT / ".pdf_build_deps"

# Add local fpdf2 if present
if DEPS_DIR.is_dir():
    sys.path.insert(0, str(DEPS_DIR))

try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not found. Run: pip install -t .pdf_build_deps fpdf2", file=sys.stderr)
    sys.exit(1)


class ReferencePDF(FPDF):
  """PDF with header/footer and Unicode-friendly font."""

  def __init__(self):
    super().__init__()
    self._setup_fonts()

  def _setup_fonts(self):
    # DejaVu supports INR symbol and most punctuation
    font_dir = Path(__file__).parent / "fonts"
    regular = font_dir / "DejaVuSans.ttf"
    bold = font_dir / "DejaVuSans-Bold.ttf"
    if regular.exists() and bold.exists():
      self.add_font("DejaVu", "", str(regular))
      self.add_font("DejaVu", "B", str(bold))
      self._font_family = "DejaVu"
      self._unicode_font = True
    else:
      self._font_family = "Helvetica"
      self._unicode_font = False

  def _set_meta_font(self, size: int = 8):
    style = "" if getattr(self, "_unicode_font", False) else "I"
    self.set_font(self._font_family, style, size)

  def header(self):
    if self.page_no() == 1:
      return
    self._set_meta_font(8)
    self.set_text_color(100, 100, 100)
    self.cell(0, 8, "SoupsSnacks v2 - Full-Stack Reference", align="C")
    self.ln(4)

  def footer(self):
    self.set_y(-12)
    self._set_meta_font(8)
    self.set_text_color(120, 120, 120)
    self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _ascii_safe(text: str) -> str:
  """Replace Unicode punctuation unsupported by core PDF fonts."""
  replacements = {
    "\u2014": "-",  # em dash
    "\u2013": "-",  # en dash
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2192": "->",
    "\u2190": "<-",
    "\u2026": "...",
    "\u20b9": "Rs.",  # INR
    "\u2713": "[x]",
    "\u2717": "[ ]",
  }
  for src, dst in replacements.items():
    text = text.replace(src, dst)
  return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_md_inline(text: str) -> str:
  text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
  text = re.sub(r"`([^`]+)`", r"\1", text)
  text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
  return _ascii_safe(text.strip())


def _is_table_separator(line: str) -> bool:
  return bool(re.match(r"^\|?[\s\-:|]+\|?$", line.strip()))


def _is_diagram_line(line: str) -> bool:
  diagram_chars = set("+-|/\\[]()")
  stripped = line.strip()
  if len(stripped) < 3:
    return False
  if stripped.startswith("```"):
    return False
  # ASCII art / box diagrams
  if sum(1 for c in stripped if c in diagram_chars or c in "\u2500\u2502\u251c") > len(stripped) * 0.3:
    return True
  return stripped.startswith("+") or stripped.startswith("|") or stripped.startswith("\\")


def parse_markdown_to_pdf(md_path: Path, pdf_path: Path) -> None:
  lines = md_path.read_text(encoding="utf-8").splitlines()
  pdf = ReferencePDF()
  pdf.set_auto_page_break(auto=True, margin=18)
  pdf.add_page()

  family = pdf._font_family
  in_code = False
  in_diagram = False
  code_buffer: list[str] = []
  i = 0

  def _write_paragraph(text: str, h: float = 5, font_size: int = 10, style: str = ""):
    pdf.set_x(pdf.l_margin)
    pdf.set_font(family, style, font_size)
    w = pdf.epw
    pdf.multi_cell(w, h, text)

  def flush_code():
    nonlocal code_buffer, in_code
    if not code_buffer:
      return
    pdf.set_font("Courier", "", 7)
    pdf.set_fill_color(245, 245, 245)
    for cl in code_buffer:
      pdf.set_x(pdf.l_margin)
      chunk = cl if len(cl) <= 95 else cl[:92] + "..."
      pdf.multi_cell(pdf.epw, 4, chunk, fill=True)
    pdf.ln(2)
    code_buffer = []
    in_code = False
    pdf.set_font(family, "", 10)

  while i < len(lines):
    raw = lines[i]
    line = raw.rstrip()

    # Fenced code blocks
    if line.strip().startswith("```"):
      if in_code:
        flush_code()
      else:
        in_code = True
        code_buffer = []
      i += 1
      continue

    if in_code:
      code_buffer.append(_ascii_safe(line[:120] if len(line) > 120 else line))
      i += 1
      continue

    # Skip horizontal rules and TOC anchor links only lines
    if re.match(r"^---+$", line.strip()):
      pdf.ln(2)
      i += 1
      continue

    if not line.strip():
      in_diagram = False
      pdf.ln(3)
      i += 1
      continue

    # ASCII diagrams (architecture boxes)
    if _is_diagram_line(line):
      flush_code()
      pdf.set_font("Courier", "", 6)
      pdf.set_x(pdf.l_margin)
      chunk = _ascii_safe(line)
      if len(chunk) > 100:
        chunk = chunk[:97] + "..."
      pdf.multi_cell(pdf.epw, 3.2, chunk)
      in_diagram = True
      i += 1
      continue
    elif in_diagram:
      pdf.ln(2)
      in_diagram = False

    # Headings (most specific first)
    if line.startswith("### "):
      flush_code()
      pdf.ln(1)
      pdf.set_font(family, "B", 11)
      _write_paragraph(_strip_md_inline(line[4:]), h=7, font_size=11, style="B")
      pdf.ln(1)
      i += 1
      continue

    if line.startswith("## "):
      flush_code()
      pdf.ln(2)
      pdf.set_font(family, "B", 14)
      pdf.set_text_color(50, 50, 50)
      _write_paragraph(_strip_md_inline(line[3:]), h=8, font_size=14, style="B")
      pdf.ln(2)
      pdf.set_text_color(0, 0, 0)
      i += 1
      continue

    if line.startswith("# "):
      flush_code()
      pdf.add_page()
      pdf.set_font(family, "B", 20)
      pdf.set_text_color(30, 80, 120)
      _write_paragraph(_strip_md_inline(line[2:]), h=10, font_size=20, style="B")
      pdf.ln(4)
      pdf.set_text_color(0, 0, 0)
      i += 1
      continue

    # Markdown tables
    if "|" in line and line.strip().startswith("|"):
      flush_code()
      table_rows = []
      while i < len(lines) and "|" in lines[i]:
        row_line = lines[i].strip()
        if not _is_table_separator(row_line):
          cells = [c.strip() for c in row_line.strip("|").split("|")]
          table_rows.append([_strip_md_inline(c) for c in cells])
        i += 1
      if table_rows:
        col_count = max(len(r) for r in table_rows)
        width = (pdf.w - pdf.l_margin - pdf.r_margin) / col_count
        pdf.set_font(family, "", 8)
        for ri, row in enumerate(table_rows):
          if ri == 0:
            pdf.set_font(family, "B", 8)
          else:
            pdf.set_font(family, "", 8)
          for ci in range(col_count):
            cell = row[ci] if ci < len(row) else ""
            pdf.cell(width, 6, cell[:40], border=1)
          pdf.ln()
        pdf.set_x(pdf.l_margin)
        pdf.ln(2)
      continue

    # Bullet lists
    if re.match(r"^[-*] ", line) or re.match(r"^\d+\. ", line):
      flush_code()
      pdf.set_font(family, "", 10)
      text = re.sub(r"^[-*] ", "", line)
      text = re.sub(r"^\d+\. ", "", text)
      _write_paragraph("  -  " + _strip_md_inline(text))
      i += 1
      continue

    # Checkbox lines
    if line.strip().startswith("- [ ]"):
      flush_code()
      pdf.set_font(family, "", 10)
      _write_paragraph("  [ ] " + _strip_md_inline(line.strip()[6:]))
      i += 1
      continue

    # Blockquote / note
    if line.startswith(">"):
      flush_code()
      pdf.set_font(family, "" if getattr(pdf, "_unicode_font", False) else "I", 9)
      pdf.set_text_color(80, 80, 80)
      _write_paragraph(_strip_md_inline(line.lstrip("> ").strip()), font_size=9)
      pdf.set_text_color(0, 0, 0)
      i += 1
      continue

    # Normal paragraph
    flush_code()
    pdf.set_font(family, "", 10)
    _write_paragraph(_strip_md_inline(line))
    i += 1

  flush_code()
  pdf.output(str(pdf_path))
  print(f"Wrote {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")


def download_fonts_if_needed() -> None:
  """Fetch or copy DejaVu fonts for better Unicode support."""
  font_dir = DOCS_DIR / "fonts"
  if (font_dir / "DejaVuSans.ttf").exists():
    return
  font_dir.mkdir(exist_ok=True)

  # macOS system paths
  import shutil

  candidates = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
  ]
  for src in candidates:
    if src.exists():
      shutil.copy(src, font_dir / "DejaVuSans.ttf")
      shutil.copy(src, font_dir / "DejaVuSans-Bold.ttf")
      print(f"Using system font: {src.name}")
      return

  try:
    import io
    import urllib.request
    import zipfile

    url = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip"
    print("Downloading DejaVu font pack...")
    with urllib.request.urlopen(url, timeout=60) as resp:
      data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
      for name in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"):
        member = f"dejavu-fonts-ttf-2.37/ttf/{name}"
        zf.extract(member, font_dir)
        extracted = font_dir / member
        extracted.rename(font_dir / name)
      # cleanup extracted folder
      import shutil as sh

      nested = font_dir / "dejavu-fonts-ttf-2.37"
      if nested.exists():
        sh.rmtree(nested)
  except Exception as e:
    print(f"Note: Using Helvetica with ASCII transliteration: {e}")


def try_pandoc_pdf() -> bool:
  """Attempt pandoc PDF if pdflatex is available."""
  try:
    subprocess.run(
      [
        "pandoc",
        str(MD_FILE),
        "-o",
        str(PDF_FILE),
        "--pdf-engine=pdflatex",
        "-V",
        "geometry:margin=1in",
        "-V",
        "fontsize=11pt",
        "--metadata",
        "title=SoupsSnacks v2 Full-Stack Reference",
      ],
      check=True,
      capture_output=True,
    )
    print(f"Wrote {PDF_FILE} via pandoc")
    return True
  except (subprocess.CalledProcessError, FileNotFoundError):
    return False


def main() -> None:
  if not MD_FILE.exists():
    print(f"Missing {MD_FILE}", file=sys.stderr)
    sys.exit(1)

  if try_pandoc_pdf():
    return

  download_fonts_if_needed()
  parse_markdown_to_pdf(MD_FILE, PDF_FILE)


if __name__ == "__main__":
  main()
