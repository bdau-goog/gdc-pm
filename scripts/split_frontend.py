#!/usr/bin/env python3
"""
Phase 1 — Frontend modularization (behavior-preserving split)

Splits gke/fault-trigger-ui/index.html into:
  static/styles.css  — extracted CSS block (lines 11–839)
  static/app.js      — extracted JS block (lines 2776–4344)
  index.html         — slim shell (head + CDN scripts + link/script refs + HTML template)

Zero behavior change. Verified with structural assertions before touching any file.
"""

import os
import sys
from pathlib import Path

SRC = Path("gke/fault-trigger-ui/index.html")
STATIC_DIR = Path("gke/fault-trigger-ui/static")

with open(SRC) as f:
    lines = f.readlines()

total = len(lines)
print(f"index.html: {total} lines")

# ── Structural assertions (abort if structure has changed) ────────────────────
def assert_contains(idx, expected, label):
    actual = lines[idx].strip()
    if expected not in actual:
        print(f"ASSERTION FAILED at line {idx+1} ({label})")
        print(f"  expected to contain: {expected!r}")
        print(f"  actual:             {actual!r}")
        sys.exit(1)

assert_contains(9,    "<style>",   "line 10 = <style> open")
assert_contains(839,  "</style>",  "line 840 = </style> close")
assert_contains(840,  "</head>",   "line 841 = </head>")
assert_contains(841,  "<body>",    "line 842 = <body>")
assert_contains(2774, "<script>",  "line 2775 = <script> open")
assert_contains(4344, "</script>", "line 4345 = </script> close")
assert_contains(4345, "</body>",   "line 4346 = </body>")
assert_contains(4346, "</html>",   "line 4347 = </html>")
print("✅ All structural assertions passed")

# ── Extract CSS (lines 11–839 inclusive, 0-indexed: 10–838) ──────────────────
css_lines = lines[10:839]
css_content = "".join(css_lines)
print(f"CSS: {len(css_lines)} lines → static/styles.css")

# ── Extract JS (lines 2776–4344 inclusive, 0-indexed: 2775–4343) ─────────────
js_lines = lines[2775:4344]
js_content = "".join(js_lines)
print(f"JS:  {len(js_lines)} lines → static/app.js")

# ── Build new slim index.html ─────────────────────────────────────────────────
# Head (lines 1–9, CDN scripts) + link to stylesheet
head = "".join(lines[0:9])
head += '  <link rel="stylesheet" href="/static/styles.css">\n'

# Lines 841–2774: </head><body>[blank]<div id="app">...(entire HTML template)
after_head = "".join(lines[840:2774])

# App.js script tag + </body></html>
script_and_footer = '<script src="/static/app.js"></script>\n'
script_and_footer += "".join(lines[4345:4347])

new_html = head + after_head + script_and_footer
new_html_lines = new_html.splitlines()
print(f"New index.html: {len(new_html_lines)} lines (was {total})")

# ── Write files ───────────────────────────────────────────────────────────────
STATIC_DIR.mkdir(parents=True, exist_ok=True)

with open(STATIC_DIR / "styles.css", "w") as f:
    f.write(css_content)

with open(STATIC_DIR / "app.js", "w") as f:
    f.write(js_content)

# Back up original before overwriting
import shutil
shutil.copy(SRC, str(SRC) + ".bak")
print(f"Backed up original → index.html.bak")

with open(SRC, "w") as f:
    f.write(new_html)

print("✅ Split complete.")
print(f"   index.html:      {len(new_html_lines)} lines")
print(f"   static/styles.css: {len(css_lines)} lines")
print(f"   static/app.js:   {len(js_lines)} lines")
print(f"   Total preserved: {len(css_lines) + len(js_lines) + len(new_html_lines)} lines "
      f"(original: {total})")
