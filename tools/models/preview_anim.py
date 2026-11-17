# -*- coding: utf-8 -*-
"""Animation previews without Blockbench: python3 preview_anim.py <sid> <out_prefix> [anim[:frames] ...]
Writes <out_prefix>.gif (all animations in sequence, real time) and <out_prefix>_sheet.png (contact sheet).
Spread wings are hidden on the ground and folded wings in the air, like the poser does."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from render3d import load_geo, render, pose_at, Cam, sheet

AIR = ("air_", "mount_air", "ride_dive")

def frames(sid, specs, *, tmp="tmp", size=(360, 300), yaw=-40, pitch=14, scale=None, suffix="", menace=False):
    b = load_geo(f"{tmp}/{sid}.geo.json")
    tp = f"{tmp}/{sid}{suffix}_preview.png"
    tex = Image.open(tp if os.path.exists(tp) else f"{tmp}/{sid}{suffix}.png")
    A = json.load(open(f"{tmp}/{sid}.animation.json"))["animations"]
    ys = [c["origin"][1] + c["size"][1] for bb in b for c in bb.get("cubes", []) if not bb["name"].startswith("wing_open")]
    top = max(ys)
    sc = scale or size[1] / (top * 1.55)
    out = []
    for name, n in specs:
        a = A[f"animation.{sid}.{name}"]
        L = a.get("animation_length", 1.0)
        air = name.startswith(AIR) or (menace and name in ("battle_idle", "battle_cry"))
        hidden = ("wing_closed_left", "wing_closed_right") if air else ("wing_open_left", "wing_open_right")
        cy = top * (0.62 if air else 0.45)
        for k in range(n):
            t = L * k / n
            im = render(b, tex, Cam(yaw=yaw, pitch=pitch, scale=sc, center=(0, cy, 0), size=size),
                        pose=pose_at(a, t), hidden=hidden, ground=not air)
            ImageDraw.Draw(im).text((8, 6), f"{name}  {t:.2f}s", fill=(90, 90, 90, 255))
            out.append((im, L / n))
    return out

if __name__ == "__main__":
    sid, prefix = sys.argv[1], sys.argv[2]
    specs = []
    for s in sys.argv[3:]:
        name, _, n = s.partition(":")
        specs.append((name, int(n or 12)))
    import glob
    pz = glob.glob(f"../../src/main/resources/assets/cobblemon/bedrock/pokemon/posers/*_{sid}/{sid}.json")
    menace = bool(pz) and any(tp.get("part") == "wing_open_left" and tp.get("isVisible") for tp in
                              json.load(open(pz[0]))["poses"]["battle-standing"].get("transformedParts", []))
    fr = frames(sid, specs, menace=menace)
    ims = [f for f, _ in fr]
    pal = [im.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=128) for im in ims]
    pal[0].save(prefix + ".gif", save_all=True, append_images=pal[1:],
                duration=[max(30, int(d * 1000)) for _, d in fr], loop=0)
    step = max(1, len(ims) // 16)
    sheet(ims[::step][:16], 4).save(prefix + "_sheet.png")
    print(prefix, len(ims), "frames")
