#!/usr/bin/env python3
"""Turns raw app screenshots into the small WebP files the site serves.

    python3 scripts/optimize_shots.py RAW_DIR [--top N] [--bottom N]
        # RAW_DIR has bn/ and en/ with home|result|scammed|family|gd .png. --top and --bottom are the pixels of the
        # capture that belong to Android (status bar, gesture or navigation bar); the defaults suit a phone captured
        # at 1080x2400 with gesture navigation (see the app repo's capture_screenshots.py). A 3-button navigation bar needs about --bottom 135.

The raw PNGs come from the app repo's tools/capture_screenshots.py. Needs Pillow (pip install pillow); the
site build itself does not, because the optimised files are committed. Output: assets/shots/{bn,en}/NAME.webp
at 720 px wide (crisp on phones, about 40-80 KB each), with the phone's own status and gesture bars cropped off.
"""
import json
import pathlib
import sys

from PIL import Image, ImageChops

NAMES = ["home", "result", "scammed", "family"]  # phone screens
PAPER = "gd"  # the print preview of the GD letter: only the white sheet is kept
WIDTH = 720
def option(name, default):
    return int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


TOP, BOTTOM = option("--top", 72), option("--bottom", 40)
ROOT = pathlib.Path(__file__).resolve().parent.parent

def paper_only(image):
    """Crop to the white sheet in a print-preview screenshot (the rest is the print dialog's grey)."""
    mask = image.point(lambda v: 255 if v >= 253 else 0)
    r, g, b = mask.split()
    white = ImageChops.multiply(ImageChops.multiply(r, g), b)
    left, top, right, bottom = white.getbbox()
    # The dialog's grey page bar has white text on it, which would stretch the box down. Drop bottom rows that are not mostly white.
    width = right - left
    while bottom > top and white.crop((left, bottom - 1, right, bottom)).histogram()[255] < 0.9 * width:
        bottom -= 1
    return image.crop((left, top, right, bottom))


raw = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else sys.exit(__doc__)
sizes = {}
for lang in ("bn", "en"):
    for name in NAMES + [PAPER]:
        source = raw / lang / f"{name}.png"
        image = Image.open(source).convert("RGB")
        if name == PAPER:
            image = paper_only(image)
        else:
            image = image.crop((0, TOP, image.width, image.height - BOTTOM))
        height = round(image.height * WIDTH / image.width)
        target = ROOT / "assets/shots" / lang / f"{name}.webp"
        target.parent.mkdir(parents=True, exist_ok=True)
        image.resize((WIDTH, height), Image.LANCZOS).save(target, "WEBP", quality=82, method=6)
        sizes[f"{lang}/{name}"] = [WIDTH, height]
        print(f"{target.relative_to(ROOT)}  {WIDTH}x{height}  {target.stat().st_size // 1024} KB")
# build.py needs each image's size (for width/height attributes) and has no image library
(ROOT / "assets/shots/manifest.json").write_text(json.dumps(sizes, indent=1) + "\n")
