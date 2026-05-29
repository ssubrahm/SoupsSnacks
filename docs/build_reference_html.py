#!/usr/bin/env python3
"""
Build a standalone HTML reference from SOUPSSNACKS_FULL_STACK_REFERENCE.md

Usage:
    python docs/build_reference_html.py

Output:
    docs/SOUPSSNACKS_FULL_STACK_REFERENCE.html  (self-contained, opens in any browser)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
MD_FILE = DOCS_DIR / "SOUPSSNACKS_FULL_STACK_REFERENCE.md"
CSS_FILE = DOCS_DIR / "reference.css"
HTML_FILE = DOCS_DIR / "SOUPSSNACKS_FULL_STACK_REFERENCE.html"
TEMP_HTML = DOCS_DIR / ".reference_build_temp.html"


SHELL_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="SoupsSnacks v2 full-stack architecture and learning reference">
  <title>SoupsSnacks v2 — Full-Stack Reference</title>
  <style>
{css}
  </style>
</head>
<body>
  <div class="doc-topbar">
    <span class="doc-topbar-title">SoupsSnacks v2 Reference</span>
    <div class="doc-controls">
      <button class="btn-icon" id="toggle-nav" aria-label="Toggle navigation">Menu</button>
      <button class="btn-icon" id="toggle-theme" aria-label="Toggle dark mode">Theme</button>
    </div>
  </div>
  <div class="doc-shell">
    <aside class="doc-sidebar" id="sidebar">
      <div class="doc-sidebar-header">
        <h1>SoupsSnacks v2</h1>
        <p class="subtitle">Full-Stack Reference &amp; Learning Guide</p>
      </div>
      <nav id="sidebar-toc" aria-label="Table of contents"></nav>
    </aside>
    <main class="doc-main">
      <article class="doc-content" id="content">
"""

SHELL_TAIL = """
      </article>
      <footer class="doc-footer">
        SoupsSnacks v2 — generated from SOUPSSNACKS_FULL_STACK_REFERENCE.md
      </footer>
    </main>
  </div>
  <button class="back-to-top" id="back-to-top" aria-label="Back to top">↑</button>
  <script>
(function () {
  const root = document.documentElement;
  const sidebar = document.getElementById('sidebar');
  const sidebarToc = document.getElementById('sidebar-toc');
  const content = document.getElementById('content');
  const pandocToc = document.getElementById('TOC');
  const backToTop = document.getElementById('back-to-top');

  // Move pandoc TOC into sidebar; remove duplicate manual TOC section if present
  if (pandocToc) {
    sidebarToc.appendChild(pandocToc);
  }

  // Remove the manual markdown TOC block (section titled "Table of Contents")
  content.querySelectorAll('h2').forEach(function (h2) {
    if (h2.textContent.trim().toLowerCase() === 'table of contents') {
      var el = h2;
      while (el) {
        var next = el.nextElementSibling;
        el.remove();
        if (!next || next.tagName === 'H2') break;
        el = next;
      }
    }
  });

  // Theme
  var savedTheme = localStorage.getItem('soupssnacks-doc-theme');
  if (savedTheme === 'dark') root.setAttribute('data-theme', 'dark');

  document.getElementById('toggle-theme').addEventListener('click', function () {
    var isDark = root.getAttribute('data-theme') === 'dark';
    if (isDark) {
      root.removeAttribute('data-theme');
      localStorage.setItem('soupssnacks-doc-theme', 'light');
    } else {
      root.setAttribute('data-theme', 'dark');
      localStorage.setItem('soupssnacks-doc-theme', 'dark');
    }
  });

  // Mobile nav
  document.getElementById('toggle-nav').addEventListener('click', function () {
    sidebar.classList.toggle('open');
  });

  sidebarToc.addEventListener('click', function (e) {
    if (window.innerWidth <= 900 && e.target.closest('a')) {
      sidebar.classList.remove('open');
    }
  });

  // Back to top
  window.addEventListener('scroll', function () {
    backToTop.classList.toggle('visible', window.scrollY > 400);
  });
  backToTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // Highlight active TOC link on scroll
  var headings = Array.from(content.querySelectorAll('h2, h3'));
  var tocLinks = sidebarToc.querySelectorAll('a');
  if (headings.length && tocLinks.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var id = entry.target.id;
          tocLinks.forEach(function (a) {
            a.style.fontWeight = a.getAttribute('href') === '#' + id ? '700' : '';
            a.style.color = a.getAttribute('href') === '#' + id ? 'var(--link-hover)' : '';
          });
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
    headings.forEach(function (h) { if (h.id) observer.observe(h); });
  }
})();
  </script>
</body>
</html>
"""


def preprocess_markdown(text: str) -> str:
  """Fix known markdown issues and strip duplicate manual TOC for HTML."""
  # Remove manual TOC (pandoc generates its own for the sidebar)
  text = re.sub(
    r"\n## Table of Contents\n.*?\n---\n",
    "\n",
    text,
    count=1,
    flags=re.DOTALL,
  )
  text = text.replace(
    "](#6-django-backend-deep dive)",
    "](#6-django-backend-deep-dive)",
  )
  return text


def run_pandoc(md_path: Path, out_path: Path) -> None:
  md_content = preprocess_markdown(md_path.read_text(encoding="utf-8"))
  temp_md = DOCS_DIR / ".reference_build_temp.md"
  temp_md.write_text(md_content, encoding="utf-8")
  try:
    cmd = [
      "pandoc",
      str(temp_md),
      "-f",
      "markdown",
      "-t",
      "html5",
      "--standalone",
      "--toc",
      "--toc-depth=3",
      "--section-divs",
      "--highlight-style=tango",
      "--metadata",
      "title=SoupsSnacks v2 Full-Stack Reference",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    out_path.write_text(result.stdout, encoding="utf-8")
  finally:
    temp_md.unlink(missing_ok=True)


def extract_body(html: str) -> str:
  """Pull main content from pandoc standalone HTML."""
  match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
  if not match:
    raise ValueError("Could not find <body> in pandoc output")
  body = match.group(1)
  # Remove pandoc's default title block if present
  body = re.sub(r'<header id="title-block-header">.*?</header>', "", body, flags=re.DOTALL)
  return body.strip()


def build_standalone_html() -> None:
  if not MD_FILE.exists():
    print(f"Missing {MD_FILE}", file=sys.stderr)
    sys.exit(1)
  if not CSS_FILE.exists():
    print(f"Missing {CSS_FILE}", file=sys.stderr)
    sys.exit(1)

  print("Converting markdown with pandoc...")
  run_pandoc(MD_FILE, TEMP_HTML)

  css = CSS_FILE.read_text(encoding="utf-8")
  body = extract_body(TEMP_HTML.read_text(encoding="utf-8"))

  html = SHELL_HEAD.format(css=css) + body + SHELL_TAIL
  HTML_FILE.write_text(html, encoding="utf-8")
  TEMP_HTML.unlink(missing_ok=True)

  size_kb = HTML_FILE.stat().st_size // 1024
  print(f"Wrote {HTML_FILE} ({size_kb} KB)")
  print(f"Open in browser: file://{HTML_FILE}")


if __name__ == "__main__":
  build_standalone_html()
