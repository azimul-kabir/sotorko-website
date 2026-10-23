#!/usr/bin/env python3
"""Collects exactly what the website serves into _site/, ready for Cloudflare (or any static host).

    python3 scripts/stage.py

Copies the generated pages and assets plus the Cloudflare _headers and _redirects, so build scripts, data
and docs are not published when this folder is what Cloudflare serves. Run python3 build.py first.
"""
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
SERVED = ["index.html", "404.html", "sitemap.xml", "robots.txt", "en", "privacy", "assets"]
CONFIG = ["_headers", "_redirects"]  # live at the repo root (where Cloudflare reads them if the whole repo is published) and are copied into _site/ too

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for name in SERVED:
    source = ROOT / name
    if not source.exists():
        raise SystemExit(f"{name} is missing: run python3 build.py first")
    shutil.copytree(source, OUT / name) if source.is_dir() else shutil.copy2(source, OUT / name)
for name in CONFIG:
    shutil.copy2(ROOT / name, OUT / name)
# Tell Cloudflare not to serve the two config files as ordinary pages.
(OUT / ".assetsignore").write_text("_headers\n_redirects\n.assetsignore\n")

size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
print(f"staged {sum(1 for f in OUT.rglob('*') if f.is_file())} files, {size // 1024} KB, in _site/")
