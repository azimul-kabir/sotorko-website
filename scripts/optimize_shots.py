#!/usr/bin/env python3
"""Turns raw app screenshots into the small WebP files the site serves.

    python3 scripts/optimize_shots.py RAW_DIR          # RAW_DIR has bn/ and en/ with home|result|scammed|family .png

The raw PNGs come from the app repo's tools/capture_screenshots.py. Needs Pillow (pip install pillow); the
site build itself does not, because the optimised files are committed. Output: assets/shots/{bn,en}/NAME.webp
at 720 px wide (crisp on phones, about 40-80 KB each), with the phone's own status and gesture bars cropped off.
"""
import pathlib
import sys

from PIL import Image

NAMES = ["home", "result", "scammed", "family"]
WIDTH = 720
TOP, BOTTOM = 100, 60  # pixels of the 1080x2400 capture that belong to Android (status bar, gesture bar), not the app
ROOT = pathlib.Path(__file__).resolve().parent.parent

raw = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else sys.exit(__doc__)
for lang in ("bn", "en"):
    for name in NAMES:
        source = raw / lang / f"{name}.png"
        image = Image.open(source).convert("RGB")
        image = image.crop((0, TOP, image.width, image.height - BOTTOM))
        height = round(image.height * WIDTH / image.width)
        target = ROOT / "assets/shots" / lang / f"{name}.webp"
        target.parent.mkdir(parents=True, exist_ok=True)
        image.resize((WIDTH, height), Image.LANCZOS).save(target, "WEBP", quality=82, method=6)
        print(f"{target.relative_to(ROOT)}  {WIDTH}x{height}  {target.stat().st_size // 1024} KB")
