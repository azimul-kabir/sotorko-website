#!/usr/bin/env python3
"""Checks the generated site before it is published. Needs only Python 3.

    python3 scripts/check_site.py

Fails (exit 1) if any local link, image or in-page anchor points at nothing, if a page is missing the
basics (language, title, description, canonical), or if the sitemap lists a page that does not exist.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "en/index.html", "privacy/index.html", "404.html"]
problems = []


def fail(message):
    problems.append(message)
    print("PROBLEM:", message)


for page in PAGES:
    path = ROOT / page
    if not path.exists():
        fail(f"{page} is missing")
        continue
    source = path.read_text()
    base = path.parent

    for needed in ('<html lang="', "<title>", 'name="description"', 'rel="canonical"', 'name="viewport"'):
        if needed not in source:
            fail(f"{page} lacks {needed}")

    for tag in re.findall(r"<img\b[^>]*>", source):
        if "alt=" not in tag:
            fail(f"{page}: an <img> has no alt attribute: {tag[:80]}")
        if "width=" not in tag or "height=" not in tag:
            fail(f"{page}: an <img> has no width/height (the page would jump while loading): {tag[:80]}")

    for ref in re.findall(r'(?:href|src)="([^"]+)"', source):
        if ref.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        target, _, anchor = ref.partition("#")
        if target:
            found = (base / target).resolve() if not target.startswith("/") else (ROOT / target.lstrip("/")).resolve()
            if found.is_dir():
                found = found / "index.html"
            if not found.exists():
                fail(f"{page}: '{ref}' does not exist")
                continue
            linked = found
        else:
            linked = path
        if anchor and linked.suffix == ".html" and f'id="{anchor}"' not in linked.read_text():
            fail(f"{page}: '{ref}' points at an id that is not on the page")

sitemap = (ROOT / "sitemap.xml").read_text()
for url in re.findall(r"<loc>https://[^/]+(/[^<]*)</loc>", sitemap):
    page = ROOT / url.lstrip("/") / "index.html" if url.endswith("/") else ROOT / url.lstrip("/")
    if not page.exists():
        fail(f"sitemap.xml lists {url} but {page.relative_to(ROOT)} does not exist")

if problems:
    print(f"\n{len(problems)} problem(s)")
    sys.exit(1)
print(f"site ok: {len(PAGES)} pages checked")
