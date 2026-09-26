"""Convert photo.png to coloured ASCII art -> art.txt + art_colors.json

Glyph density per cell = mix of darkness, distance from the flat background
colour, and edge strength. Colour per cell = average source colour.
"""
import json
import sys

import numpy as np
from PIL import Image

COLS = int(sys.argv[1]) if len(sys.argv) > 1 else 70
CELL_ASPECT = 0.80
CROP = (170, 105, 560, 655)
RAMP = " .:-=+*#%@"          # weak -> strong
SS = 4                       # supersampling factor

im = Image.open("photo.png").convert("RGB").crop(CROP)
w, h = im.size
rows = round(COLS * (h / w) * CELL_ASPECT)

big = np.asarray(im.resize((COLS * SS, rows * SS), Image.LANCZOS), dtype=np.float32)
bg = np.array([193, 215, 229], dtype=np.float32)

lum = big @ np.array([0.299, 0.587, 0.114], dtype=np.float32) / 255.0
dark = 1.0 - lum
dist = np.linalg.norm(big - bg, axis=2) / 255.0

gx = np.zeros_like(lum)
gy = np.zeros_like(lum)
gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
edge = np.hypot(gx, gy)

d_dark = np.clip((dark - 0.20) / 0.65, 0, 1)
d_dist = np.clip((dist - 0.08) / 0.45, 0, 1)
d_edge = np.clip(edge * 2.0, 0, 1)
feat = np.clip(0.55 * d_dark + 0.30 * d_dist + 0.55 * d_edge, 0, 1)

cells = feat.reshape(rows, SS, COLS, SS).mean(axis=(1, 3))
cells = np.clip(cells / np.percentile(cells, 99.8), 0, 1) ** 0.9

out = []
for r in range(rows):
    out.append("".join(RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))] for v in cells[r]))
open("art.txt", "w").write("\n".join(out) + "\n")

# per-cell colour: average of the block, ignoring outline pixels
wgt = (1.05 - d_edge)[..., None]
col = (big * wgt).reshape(rows, SS, COLS, SS, 3).sum(axis=(1, 3)) / wgt.reshape(rows, SS, COLS, SS, 1).sum(axis=(1, 3))
json.dump(
    [["%02x%02x%02x" % tuple(int(x) for x in px) for px in row] for row in col],
    open("art_colors.json", "w"),
)
print(COLS, "x", rows)
