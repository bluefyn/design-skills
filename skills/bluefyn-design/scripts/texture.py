#!/usr/bin/env python3
"""Regenerates assets/texture.png, the record texture used on navy grounds.

The texture is the check log set very small. It is shipped as an image so that
its words do not end up in the PDF's text, where they would bury the real copy
for anyone who searches, copies or feeds the PDF to a tool.

    python3 texture.py            (needs a Chromium-based browser; no Python packages)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand as b  # noqa: E402


def find_chrome():
    env = os.environ.get("CHROME")
    if env:
        return env
    for path in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
                 "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"):
        if os.path.exists(path):
            return path
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(name):
            return shutil.which(name)
    raise SystemExit("No Chrome, Chromium or Edge found. Set CHROME=/path/to/browser.")


W, H, SCALE = 612, 340, 2          # points, and device pixels per CSS pixel
svg = b.record_texture(W, H, fs=3.7, seed=9, opacity=1.0)
work = tempfile.mkdtemp(prefix="bluefyn-texture-")
page = os.path.join(work, "t.html")
with open(page, "w") as fh:
    fh.write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}'
             f'svg{{display:block}}</style></head><body>{svg}</body></html>')
out = os.path.join(b.ASSETS, "texture.png")
px = lambda pt: int(round(pt * 96 / 72))
subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={work}/profile",
                "--hide-scrollbars", "--default-background-color=00000000", f"--window-size={px(W)},{px(H)}",
                f"--force-device-scale-factor={SCALE}", f"--screenshot={out}", "file://" + page],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
shutil.rmtree(work, ignore_errors=True)
print("wrote", out, os.path.getsize(out), "bytes")
