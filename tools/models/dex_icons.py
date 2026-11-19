# -*- coding: utf-8 -*-
"""32x32 Pokédex / PC icons (pixel-art, transparent) rendered from the models of the pack:
python3 -I dex_icons.py <models_dir> <pack_dir>  ->  assets/cobblepulse_ecology/textures/gui/sprites/<species>.png"""
import json, os, sys
models_dir, pack = sys.argv[1:3]
sys.path.insert(0, models_dir)
from PIL import Image
from render3d import load_geo, render, pose_at, Cam

A = os.path.join(pack, "assets/cobblemon")
OUT = os.path.join(pack, "assets/cobblepulse_ecology/textures/gui/sprites")
os.makedirs(OUT, exist_ok=True)
ICONS = {  # species: (folder, model, texture, glow layer or None)
    "zamtrios": ("1054_zamtrios", "zamtrios", "zamtrios", None),
    "goremagala": ("1055_goremagala", "goremagala", "goremagala", None),
    "chaoticgoremagala": ("1056_chaoticgoremagala", "chaoticgoremagala", "chaoticgoremagala", "chaoticgoremagala_glow"),
    "shagarumagala": ("1057_shagarumagala", "shagarumagala", "shagarumagala", "shagarumagala_glow"),
}
for sid, (folder, model, texn, glow) in ICONS.items():
    bones = load_geo(f"{A}/bedrock/pokemon/models/{folder}/{model}.geo.json")
    anims = json.load(open(f"{A}/bedrock/pokemon/animations/{folder}/{model}.animation.json"))["animations"]
    tex = Image.open(f"{A}/textures/pokemon/{folder}/{texn}.png").convert("RGBA")
    if glow:
        tex.alpha_composite(Image.open(f"{A}/textures/pokemon/{folder}/{glow}.png").convert("RGBA"))
    pose = pose_at(anims[f"animation.{model}.ground_idle"], 0.0)
    big = render(bones, tex, Cam(yaw=-38, pitch=14, scale=4, center=(0, 30, 0), size=(800, 800)), pose=pose,
                 bg=(0, 0, 0, 0), ground=False)
    bb = big.getbbox()
    crop = big.crop(bb)
    k = 30 / max(crop.size)
    small = crop.resize((max(1, round(crop.width * k)), max(1, round(crop.height * k))), Image.LANCZOS)
    a = small.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    small.putalpha(a)
    icon = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    icon.alpha_composite(small, ((32 - small.width) // 2, 32 - 1 - small.height))
    # dark outline, as Cobblemon's own icons
    px = icon.load()
    out = icon.copy(); po = out.load()
    for y in range(32):
        for x in range(32):
            if px[x, y][3] == 0 and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and px[x + dx, y + dy][3]
                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                po[x, y] = (24, 20, 30, 255)
    out.save(f"{OUT}/{sid}.png")
    print(sid, small.size)
