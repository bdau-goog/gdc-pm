#!/usr/bin/env python3
"""
verify_templates.py — Per-tab HTML balance gate.

Checks every file in gke/fault-trigger-ui/templates/ for:
  1. <template> / </template> balance
  2. <div> / </div> balance

Also assembles the full shell into a temp file and verifies:
  3. The assembled output contains all 6 tab panel opening tags
  4. All @@INCLUDE markers are resolved (none remain)

Run before building the container:
  python3 scripts/verify_templates.py

Exit 0 = clean. Exit 1 = balance failure (blocks build).
"""

import re
import sys
import os
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
TEMPLATES   = REPO_ROOT / "gke" / "fault-trigger-ui" / "templates"
SHELL_HTML  = REPO_ROOT / "gke" / "fault-trigger-ui" / "index.html"

EXPECTED_TABS = [
    "tab_intro",
    "tab_operations",
    "tab_h1",
    "tab_h2",
    "tab_h3",
    "tab_financials",
    "tab_architecture",
]

def count_tags(text: str, open_re: str, close_re: str) -> tuple[int, int]:
    opens  = len(re.findall(open_re, text))
    closes = len(re.findall(close_re, text))
    return opens, closes

def check_file(path: Path) -> list[str]:
    """Return list of error strings (empty = pass)."""
    errors = []
    text = path.read_text(encoding="utf-8")

    # <template> balance
    t_open, t_close = count_tags(text, r'<template\b', r'</template>')
    if t_open != t_close:
        errors.append(
            f"  <template> imbalance: {t_open} open / {t_close} close "
            f"(delta {t_open - t_close:+d})"
        )

    # <div> balance
    d_open, d_close = count_tags(text, r'<div\b', r'</div>')
    if d_open != d_close:
        errors.append(
            f"  <div> imbalance: {d_open} open / {d_close} close "
            f"(delta {d_open - d_close:+d})"
        )

    return errors

def assemble(shell_text: str) -> str:
    """Perform marker substitution from templates/ directory."""
    result = shell_text
    for name in EXPECTED_TABS:
        tpath = TEMPLATES / f"{name}.html"
        if tpath.exists():
            content = tpath.read_text(encoding="utf-8")
            result = result.replace(f"<!-- @@INCLUDE:{name}@@ -->", content)
    return result

def main():
    all_ok = True

    # ── Step 1: Per-file balance checks ──────────────────────────────────────
    print("=== Per-tab template balance checks ===")
    if not TEMPLATES.exists():
        print(f"FAIL: templates/ directory not found at {TEMPLATES}")
        sys.exit(1)

    tab_files = sorted(TEMPLATES.glob("*.html"))
    if not tab_files:
        print(f"FAIL: no .html files found in {TEMPLATES}")
        sys.exit(1)

    for tfile in tab_files:
        errors = check_file(tfile)
        if errors:
            print(f"FAIL {tfile.name}:")
            for e in errors:
                print(e)
            all_ok = False
        else:
            text = tfile.read_text(encoding="utf-8")
            t_open, _ = count_tags(text, r'<template\b', r'</template>')
            d_open, _ = count_tags(text, r'<div\b', r'</div>')
            print(f"  OK  {tfile.name}  "
                  f"(<template> {t_open}/{t_open}  <div> {d_open}/{d_open})")

    # ── Step 2: Assembly check ────────────────────────────────────────────────
    print("\n=== Assembly check ===")
    if not SHELL_HTML.exists():
        print(f"FAIL: shell index.html not found at {SHELL_HTML}")
        sys.exit(1)

    shell_text = SHELL_HTML.read_text(encoding="utf-8")

    # Verify all expected markers are present in the shell
    missing_markers = []
    for name in EXPECTED_TABS:
        marker = f"<!-- @@INCLUDE:{name}@@ -->"
        if marker not in shell_text:
            missing_markers.append(name)
    if missing_markers:
        print(f"FAIL: shell index.html is missing @@INCLUDE markers for: {missing_markers}")
        all_ok = False
    else:
        print(f"  OK  shell has all {len(EXPECTED_TABS)} @@INCLUDE markers")

    # Assemble and check no markers remain
    assembled = assemble(shell_text)
    remaining = re.findall(r'<!-- @@INCLUDE:[^@]+@@ -->', assembled)
    if remaining:
        print(f"FAIL: unresolved markers in assembled HTML: {remaining}")
        all_ok = False
    else:
        print(f"  OK  all markers resolved")

    # Verify assembled HTML contains expected tab-panel signatures
    EXPECTED_SIGNATURES = [
        ('tab-intro',        "mainTab==='intro'"),
        ('tab-operations',   'id="tab-operations"'),
        ('tab-horizon1',     "mainTab==='horizon1'"),
        ('tab-horizon2',     "mainTab==='horizon2'"),
        ('tab-horizon3',     "mainTab==='horizon3'"),
        ('tab-financials',   'id="tab-financials"'),
        ('tab-architecture', 'id="tab-architecture"'),
    ]
    missing_sigs = []
    for tab_name, sig in EXPECTED_SIGNATURES:
        if sig not in assembled:
            missing_sigs.append(tab_name)
    if missing_sigs:
        print(f"FAIL: assembled HTML missing tab signatures for: {missing_sigs}")
        all_ok = False
    else:
        print(f"  OK  all {len(EXPECTED_SIGNATURES)} tab panel signatures present in assembled HTML")

    # Assembled balance check
    print("\n=== Assembled HTML balance check ===")
    asm_errors = []
    t_open, t_close = count_tags(assembled, r'<template\b', r'</template>')
    if t_open != t_close:
        asm_errors.append(f"  <template> imbalance in assembled: {t_open}/{t_close}")
    d_open, d_close = count_tags(assembled, r'<div\b', r'</div>')
    if d_open != d_close:
        asm_errors.append(f"  <div> imbalance in assembled: {d_open}/{d_close}")

    if asm_errors:
        for e in asm_errors:
            print(f"FAIL{e}")
        all_ok = False
    else:
        print(f"  OK  assembled HTML balanced  "
              f"(<template> {t_open}/{t_close}  <div> {d_open}/{d_close})")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if all_ok:
        print("ALL CHECKS PASSED — safe to build container.")
        sys.exit(0)
    else:
        print("ONE OR MORE CHECKS FAILED — fix before building container.")
        sys.exit(1)

if __name__ == "__main__":
    main()
