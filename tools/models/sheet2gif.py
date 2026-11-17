# -*- coding: utf-8 -*-
"""Split a Blockbench frame sheet into a GIF (+ an enlarged contact strip for review).
Usage: python3 -I sheet2gif.py <sheet.png> <n_frames> <cols> <anim_length_s> <out.gif> [strip.png] [crop l,t,r,b]"""
import sys
from PIL import Image
sheet_p, n, cols, length, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
strip_p = sys.argv[6] if len(sys.argv) > 6 else None
crop = tuple(int(v) for v in sys.argv[7].split(",")) if len(sys.argv) > 7 else None
sheet = Image.open(sheet_p).convert("RGB")
rows = (n + cols - 1) // cols
W, H = sheet.width // cols, sheet.height // rows
frames = []
for i in range(n):
    f = sheet.crop(((i % cols) * W, (i // cols) * H, (i % cols + 1) * W, (i // cols + 1) * H))
    if crop:
        f = f.crop(crop)
    frames.append(f)
dur = max(20, int(round(length / n * 1000)))
pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
pal[0].save(out, save_all=True, append_images=pal[1:], duration=dur, loop=0, disposal=2)
if strip_p:
    pick = [frames[i] for i in range(0, n, max(1, n // 4))][:4]
    strip = Image.new("RGB", (pick[0].width * len(pick), pick[0].height), "white")
    for k, f in enumerate(pick):
        strip.paste(f, (k * f.width, 0))
    strip.save(strip_p)
print(out, len(frames), "frames", dur, "ms")
