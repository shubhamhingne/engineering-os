#!/usr/bin/env python3
"""Verify that every relative Markdown link in the repository resolves.

Walks all .md files, finds links to local files, and reports any that don't exist. Exits
non-zero (with GitHub Actions annotations) if any link is broken. Functional today — it is the
guard that keeps the docs blueprint navigable as it grows.
"""
from __future__ import annotations

import os
import re
import sys

LINK = re.compile(r"\]\(([^)]+?)(#[^)]*)?\)")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".next"}


def md_files(root: str = ".") -> list[str]:
    out: list[str] = []
    for dirpath, dirnames, names in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        out += [os.path.join(dirpath, n) for n in names if n.endswith(".md")]
    return sorted(out)


def main() -> int:
    broken = checked = 0
    for f in md_files():
        base = os.path.dirname(f)
        with open(f, encoding="utf-8") as fh:
            text = fh.read()
        for m in LINK.finditer(text):
            link = m.group(1).strip()
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            checked += 1
            target = os.path.normpath(os.path.join(base, link))
            if not os.path.exists(target):
                broken += 1
                print(f"::error file={f}::broken link -> {link}")
    print(f"Checked {checked} local links across the repo; {broken} broken.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
