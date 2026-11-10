"""Draws a fine grain tile: specks of about 0.4 pt each, white for dark grounds
or ink for paper. Needs Pillow.
usage: grain.py assets/grain-dark.png [light|dark]"""
import random
import sys

from PIL import Image

N = 256
on_paper = len(sys.argv) > 2 and sys.argv[2] == "light"
rgb = (28, 25, 25) if on_paper else (255, 255, 255)
rng = random.Random(1919)
im = Image.new("RGBA", (N, N), rgb + (0,))
px = im.load()
for y in range(N):
    for x in range(N):
        r = rng.random()
        if r < 0.26:                       # a speck: most are faint, a few stand out
            a = rng.uniform(0.02, 0.07) if r > 0.05 else rng.uniform(0.07, 0.12)
            px[x, y] = rgb + (int(a * 255),)
im.save(sys.argv[1], optimize=True)
