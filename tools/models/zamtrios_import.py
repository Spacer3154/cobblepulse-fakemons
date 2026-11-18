# -*- coding: utf-8 -*-
"""Zamtrios (Monster Hunter) for Cobblemon, from the supplied remaster model (src/zamtrios: per-face UV geometry,
GeckoLib animations, normal texture and ice-armour texture).

python3 -I zamtrios_import.py <models_dir> <out_pack_dir> <tmp_dir>

What it does:
* geometry: per-face UV -> box UV (Cobblemon only reads box UV), cube sizes snapped to whole units (centre kept) so
  every face starts on a texel; one 1024x512 atlas re-laid out from the two supplied textures;
* three models sharing the atlas: zamtrios (normal: no ice armour), zamtrios_armor (ice armour + glow shells),
  zamtrios_inflated (the giant inflated sac, built at half size and scaled x2 by every animation);
* the ice armour glows at night through glow shells: copies of the armour cubes, slightly inflated, transparent in
  the base texture and painted only in the emissive layer, hidden while asleep (the glow goes out);
* textures: normal / ice armour / shiny of both (teal -> violet, orange fins -> gold) / emissive glow (normal, shiny);
* animations: GeckoLib keyframes (vector + easing) resampled to linear Bedrock keyframes for idle, walk, run, sleep,
  faint (rears up roaring, collapses) and cry; battle_idle, physical, special, status and swimming are written here;
  the inflated form has its own set (bobbing ball, body slam, deflating faint...)."""
import copy, colorsys, json, math, os, sys

models_dir, out, tmp = sys.argv[1:4]
sys.path.insert(0, models_dir)
from PIL import Image
from gecko import sample, to_bedrock
import portrait_sim

SRC = os.path.join(models_dir, "src", "zamtrios")
DEX, SID = 11233, "zamtrios"
FOLDER = f"{DEX}_{SID}"
A = os.path.join(out, "assets/cobblemon")
TDIR = f"{A}/textures/pokemon/{FOLDER}"
for sub in ("models", "animations", "posers", "resolvers"):
    os.makedirs(f"{A}/bedrock/pokemon/{sub}/{FOLDER}", exist_ok=True)
os.makedirs(TDIR, exist_ok=True); os.makedirs(tmp, exist_ok=True)

FX = ("specialfx1", "specialfx2", "specialfx3", "specialfx4")
ARMOR = ("icearmor", "bodyicearmor")
GLOW = ("icearmor_glow", "bodyicearmor_glow")
BALLOON_C = (0.0, 40.0, 6.0)          # centre and radii of the inflated sac (full size, model units)
BALLOON_R = (44.0, 40.0, 46.0)
BALLOON_K = 2.0                       # built at 1/K size, scaled xK by the animations (a quarter of the texels)

# ------------------------------------------------------------------------------------------------ geometry
src = json.load(open(f"{SRC}/zamtrios_remaster.geo.json"))
geo = src["minecraft:geometry"][0]
bones = geo["bones"]
byname = {b["name"]: b for b in bones}
for name, parent in zip(GLOW, ARMOR):           # glow shells: the armour cubes, a hair larger
    shell = {"name": name, "parent": parent, "pivot": list(byname[parent]["pivot"]), "cubes": []}
    for c in byname[parent]["cubes"]:
        c2 = copy.deepcopy(c); c2["inflate"] = 0.2; c2["_glow"] = True
        shell["cubes"].append(c2)
    bones.append(shell)

def balloon_cubes():
    cx, cy, cz = BALLOON_C                    # centred on the real centre (the scale pivot), radii divided by K
    rx, ry, rz = (v / BALLOON_K for v in BALLOON_R)
    cubes = []
    n = 12
    for k in range(n):
        y0 = cy - ry + 2 * ry * k / n
        y1 = cy - ry + 2 * ry * (k + 1) / n
        ym = (y0 + y1) / 2
        f = math.sqrt(max(0.0, 1 - ((ym - cy) / ry) ** 2))
        a, c = max(1, round(rx * f)), max(1, round(rz * f))
        h = max(1, round(y1 - y0))
        for ax, az in ((a, round(c * 0.72)), (round(a * 0.72), c)):
            cubes.append({"origin": [cx - ax, round(y0, 2), cz - az], "size": [2 * ax, h, 2 * az], "_balloon": True})
    return cubes

bones.append({"name": "balloon", "parent": "body", "pivot": list(BALLOON_C), "cubes": balloon_cubes()})

def snap(bones):
    for b in bones:
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]
            ns = [0 if v == 0 else max(1, int(math.floor(v + 0.5))) for v in s]
            c["origin"] = [round(o[i] + (s[i] - ns[i]) / 2, 4) for i in range(3)]
            c["size"] = ns

def box_rects(u, v, w, h, d):
    return {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "east": (u, v + d, d, h),
            "north": (u + d, v + d, w, h), "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}

def pack(sizes, width):
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][1], -sizes[i][0]))
    sky, pos = [0] * width, {}
    for i in order:
        w, h = sizes[i]
        if not w or not h:
            pos[i] = (0, 0); continue
        best = None
        for x in range(0, width - w + 1):
            y = max(sky[x:x + w])
            if best is None or y < best[1]:
                best = (x, y)
        x, y = best
        for k in range(x, x + w):
            sky[k] = y + h
        pos[i] = (x, y)
    return pos, max(sky)

orig = copy.deepcopy(bones)
snap(bones)
TW, TH = 1024, 512
refs = [(bi, ci) for bi, b in enumerate(bones) for ci, _ in enumerate(b.get("cubes", []))]
sizes = [(2 * bones[bi]["cubes"][ci]["size"][2] + 2 * bones[bi]["cubes"][ci]["size"][0],
          bones[bi]["cubes"][ci]["size"][2] + bones[bi]["cubes"][ci]["size"][1]) for bi, ci in refs]
pos, used = pack(sizes, TW)
assert used <= TH, f"atlas overflow: {used} > {TH}"

tex_src = {k: Image.open(f"{SRC}/{f}").convert("RGBA") for k, f in
           (("normal", "zamtrios_remaster.png"), ("ice", "zamtrios_remaster_ice.png"))}
atlas = {k: Image.new("RGBA", (TW, TH), (0, 0, 0, 0)) for k in tex_src}
glow_mask = Image.new("L", (TW, TH), 0)
balloon_faces = []                       # (rect, face, cube) to paint
for k, (bi, ci) in enumerate(refs):
    c = bones[bi]["cubes"][ci]
    oc = orig[bi]["cubes"][ci]
    w, h, d = c["size"]
    u, v = pos[k]
    c["uv"] = [u, v]
    rects = box_rects(u, v, w, h, d)
    if c.pop("_balloon", False):
        for face, r in rects.items():
            balloon_faces.append((face, r, c))
        continue
    glow = c.pop("_glow", False)
    for face, (rx, ry, fw, fh) in rects.items():
        f = oc["uv"].get(face) if isinstance(oc.get("uv"), dict) else None
        if not fw or not fh or not f:
            continue
        su, sv = f["uv"]; ssx, ssy = f["uv_size"]
        if not ssx or not ssy:
            continue
        tu, tv, tsx, tsy = (rx, ry + fh, fw, -fh) if face == "down" else (rx, ry, fw, fh)
        for j in range(fh):
            for i in range(fw):
                s_, t_ = (rx + i + 0.5 - tu) / tsx, (ry + j + 0.5 - tv) / tsy
                x = min(max(math.floor(su + s_ * ssx), min(su, su + ssx)), max(su, su + ssx) - 1)
                y = min(max(math.floor(sv + t_ * ssy), min(sv, sv + ssy)), max(sv, sv + ssy) - 1)
                for key, img in atlas.items():
                    img.putpixel((rx + i, ry + j), tex_src[key].getpixel((x, y)))
                if glow:
                    glow_mask.putpixel((rx + i, ry + j), 255)

# the inflated sac: teal back with the dark stripes of the head, cream belly, a soft line between them
TEAL, TEAL_D, CREAM, CREAM_D, STRIPE = (32, 196, 190), (22, 150, 150), (222, 222, 196), (196, 196, 170), (14, 46, 52)
def sac_color(px, py, pz):
    cy, ry = BALLOON_C[1], BALLOON_R[1] / BALLOON_K
    px, pz = px - BALLOON_C[0], pz - BALLOON_C[2]
    hgt = (py - cy) / ry                          # -1 bottom .. 1 top
    edge = -0.15 + 0.12 * math.sin(pz * 0.9) + 0.06 * math.sin(px * 1.7)
    if hgt > edge:
        col = TEAL if (int(px * 5) * 7 + int(pz * 5) * 3 + int(py * 5)) % 11 else TEAL_D
        wave_ = math.sin(pz * 0.42 + 0.004 * px * px * 4 + 0.6)
        if hgt > 0.05 and abs(wave_) < 0.16 + 0.05 * hgt:
            col = STRIPE
    else:
        col = CREAM if (int(px * 2) + int(py * 3) + int(pz * 2)) % 9 else CREAM_D
    return col + (255,)

def face_point(face, c, a, b):
    (x0, y0, z0), (sx, sy, sz) = c["origin"], c["size"]
    x1, y1, z1 = x0 + sx, y0 + sy, z0 + sz
    return {"north": (x0 + a, y1 - b, z0), "south": (x1 - a, y1 - b, z1), "east": (x0, y1 - b, z1 - a),
            "west": (x1, y1 - b, z0 + a), "up": (x0 + a, y1, z1 - b), "down": (x0 + a, y0, z1 - b)}[face]

for face, (rx, ry, fw, fh), c in balloon_faces:
    for j in range(fh):
        for i in range(fw):
            p = face_point(face, c, i + 0.5, j + 0.5)
            col = sac_color(*p)
            for img in atlas.values():
                img.putpixel((rx + i, ry + j), col)

# ------------------------------------------------------------------------------------------------ textures
def recolor(img, shiny):
    """shiny: teal -> violet, orange/red fins -> gold, pale ice -> lavender ice"""
    out_ = img.copy()
    px = out_.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if 0.40 <= h <= 0.56 and s > 0.08:
                h = (h + 0.22) % 1.0
                s = min(1.0, s * 0.72)
                v = v * 0.92
            elif (h <= 0.11 or h >= 0.95) and s > 0.35:
                h = 0.12; s = min(1.0, s * 0.85); v = min(1.0, v * 1.05)
            elif 0.56 < h <= 0.60 and s > 0.2:
                h = 0.80
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
            px[x, y] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return out_

def glow_layer(ice):
    """emissive layer: only the glow shells, brightest ice glows most, the dark cracks stay dark"""
    g = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    gp, ip, mp = g.load(), ice.load(), glow_mask.load()
    for y in range(TH):
        for x in range(TW):
            if not mp[x, y]:
                continue
            r, gg, b, a = ip[x, y]
            if not a:
                continue
            lum = (0.3 * r + 0.59 * gg + 0.11 * b) / 255
            if lum < 0.55:
                continue
            k = (lum - 0.55) / 0.45
            gp[x, y] = (min(255, int(r * 0.8 + 50)), min(255, int(gg * 0.9 + 40)), 255, int(70 + 150 * k))
    return g

def hide_glow(img):
    img = img.copy()
    p, mp = img.load(), glow_mask.load()
    for y in range(TH):
        for x in range(TW):
            if mp[x, y]:
                p[x, y] = (0, 0, 0, 0)
    return img

T = {}
T["zamtrios"] = hide_glow(atlas["normal"])
T["zamtrios_shiny"] = recolor(T["zamtrios"], True)
T["zamtrios_armor"] = hide_glow(atlas["ice"])
T["zamtrios_armor_shiny"] = recolor(T["zamtrios_armor"], True)
G = {"normal": glow_layer(atlas["ice"])}
G["shiny"] = recolor(G["normal"], True)
for n, img in T.items():
    img.save(f"{TDIR}/{n}.png"); img.save(f"{tmp}/{n}.png")
os.makedirs(f"{TDIR}/glow", exist_ok=True)
for k, img in G.items():
    img.save(f"{TDIR}/glow/zamtrios_armor_{k}.png"); img.save(f"{tmp}/zamtrios_armor_glow_{k}.png")
for base in ("zamtrios", "zamtrios_shiny"):          # previews with the glow on
    pass

# ------------------------------------------------------------------------------------------------ models
geo["description"].update({"texture_width": TW, "texture_height": TH})
def model(name, drop):
    g = copy.deepcopy(src)
    gg = g["minecraft:geometry"][0]
    gg["description"]["identifier"] = f"geometry.{name}"
    gg["bones"] = [b for b in copy.deepcopy(bones) if b["name"] not in drop]
    for b in gg["bones"]:
        for c in b.get("cubes", []):
            for k in [k for k in c if k.startswith("_")]:
                del c[k]
    return g

MODELS = {"zamtrios": model("zamtrios", ARMOR + GLOW + ("balloon",)),
          "zamtrios_armor": model("zamtrios_armor", ("balloon",)),
          "zamtrios_inflated": model("zamtrios_inflated", ARMOR + GLOW)}

# ------------------------------------------------------------------------------------------------ animations
SRC_A = json.load(open(f"{SRC}/zamtrios_remaster.animation.json"))["animations"]

def conv(name, t0=0.0, length=None, speed=1.0, loop=None):
    a = SRC_A[name]
    s, L = sample(a, fps=24, length=length, t0=t0, speed=speed)
    return to_bedrock(s, L, a.get("loop") if loop is None else loop)

def kf(points, loop_len=None):
    """{time: vec} with linear keys; a looping channel repeats its first key at the end"""
    d = {f"{t:g}" if t else "0.0": [round(x, 3) for x in v] for t, v in sorted(points.items())}
    return d

def wave(amp, period, length, phase=0.0, axis=0, base=(0, 0, 0), steps=12):
    """sinusoidal channel sampled into keys (loops cleanly when length is a multiple of period)"""
    pts = {}
    for i in range(steps + 1):
        t = length * i / steps
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (t / period) + phase)
        pts[round(t, 4)] = v
    return kf(pts)

def merge(*anims):
    out_ = {}
    for a in anims:
        for b, ch in a.items():
            out_.setdefault(b, {}).update(ch)
    return out_

def anim(length, bones_, loop=None):
    a = {"animation_length": round(length, 4), "bones": bones_}
    if loop is True:
        a["loop"] = True
    elif loop == "hold":
        a["loop"] = "hold_on_last_frame"
    return a

def hide_fx(a, extra=()):
    for b in FX + tuple(extra):
        a["bones"].setdefault(b, {}).setdefault("scale", [0, 0, 0])
    return a

def shift_root(a, dy):
    """lift / lower the whole model (adds to the root position channel)"""
    ch = a["bones"].setdefault("zamtrios", {})
    p = ch.get("position", [0, 0, 0])
    if isinstance(p, list):
        ch["position"] = [p[0], p[1] + dy, p[2]]
    else:
        ch["position"] = {t: [v[0], v[1] + dy, v[2]] for t, v in p.items()}
    return a

def base_set():
    S = {}
    S["ground_idle"] = conv("idle", loop=True)
    S["ground_walk"] = conv("walk", loop=True)
    S["ground_run"] = conv("run", loop=True)
    S["sleep"] = conv("sleep", loop=True)
    S["faint"] = conv("death", loop="hold")
    # cry: the roar, a little faster (head up, jaws wide, tail raised, shock wave on the ground)
    S["cry"] = conv("zamtriosroar", speed=1.35, loop=False)
    L = 2.0
    S["battle_idle"] = anim(L, merge(
        {"zamtrios": {"position": wave(0.8, L, L, axis=1, base=(0, -1.5, 0))}},
        {"body": {"rotation": wave(1.5, L, L, axis=0, base=(3, 0, 0))}},
        {"head": {"rotation": wave(2.5, L, L, phase=0.6, axis=0, base=(-5, 0, 0))}},
        {"jaw": {"rotation": wave(5, L / 2, L, axis=0, base=(10, 0, 0))}},
        {"leftarm": {"rotation": [0, 0, -6]}, "rightarm": {"rotation": [0, 0, 6]}},
        {"leftleg": {"rotation": [0, 0, -4]}, "rightleg": {"rotation": [0, 0, 4]}},
        {"tail1": {"rotation": wave(6, L, L, axis=1, base=(-4, 0, 0))}},
        {"tail2": {"rotation": wave(10, L, L, phase=-0.9, axis=1, base=(-4, 0, 0))}}), loop=True)
    # physical (1.1 s): pulls back, lunges with the jaws wide open and snaps them shut
    S["physical"] = anim(1.1, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .3: [0, -0.5, 6], .5: [0, -2.5, -16], .62: [0, -2.5, -15],
                                     .8: [0, -2, -8], 1.1: [0, -1.5, 0]})},
        "body": {"rotation": kf({0: [3, 0, 0], .3: [-7, 0, 0], .5: [8, 0, 0], .8: [4, 0, 0], 1.1: [3, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .3: [-20, 0, 0], .5: [6, 0, 0], .62: [10, 0, 0], .8: [0, 0, 0],
                                 1.1: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .3: [30, 0, 0], .5: [34, 0, 0], .58: [0, 0, 0], .8: [4, 0, 0],
                                1.1: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .3: [10, 0, -6], .5: [-22, 0, -8], .8: [-6, 0, -6], 1.1: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .3: [10, 0, 6], .5: [-22, 0, 8], .8: [-6, 0, 6], 1.1: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .3: [-14, 8, 0], .5: [6, -10, 0], .8: [0, -4, 0], 1.1: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .3: [-10, 14, 0], .5: [8, -16, 0], .8: [0, -6, 0], 1.1: [-4, 0, 0]})}})
    # special (1.4 s): rears its head, then blasts ice / water straight ahead, jaws wide, braced
    sh = {round(.6 + .08 * i, 3): [4, (2 if i % 2 else -2), 0] for i in range(7)}
    S["special"] = anim(1.4, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .35: [0, 0.5, 2], .6: [0, -2, 4], 1.1: [0, -2, 4],
                                     1.4: [0, -1.5, 0]})},
        "body": {"rotation": kf({0: [3, 0, 0], .35: [-9, 0, 0], .6: [2, 0, 0], 1.1: [2, 0, 0], 1.4: [3, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .35: [-28, 0, 0], **sh, 1.15: [2, 0, 0], 1.4: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .35: [14, 0, 0], .55: [38, 0, 0], 1.1: [38, 0, 0], 1.25: [8, 0, 0],
                                1.4: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .35: [-8, 0, -10], .6: [6, 0, -12], 1.1: [6, 0, -12], 1.4: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .35: [-8, 0, 10], .6: [6, 0, 12], 1.1: [6, 0, 12], 1.4: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .35: [8, 0, 0], .6: [-12, 0, 0], 1.1: [-12, 0, 0], 1.4: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .35: [10, 0, 0], .6: [-16, 0, 0], 1.1: [-16, 0, 0], 1.4: [-4, 0, 0]})}})
    # status (1.2 s): stamps both front feet and shakes itself, head held high
    S["status"] = anim(1.2, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .25: [0, 1.5, 0], .4: [0, -2.5, 0], .65: [0, 1, 0],
                                     .8: [0, -2.5, 0], 1.2: [0, -1.5, 0]}),
                     "rotation": kf({0: [0, 0, 0], .45: [0, 0, 5], .6: [0, 0, -5], .75: [0, 0, 4], .9: [0, 0, -3],
                                     1.2: [0, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .3: [-22, 0, 0], .9: [-18, 0, 0], 1.2: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .3: [24, 0, 0], .9: [20, 0, 0], 1.2: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .25: [-25, 0, -6], .4: [0, 0, -6], .65: [-20, 0, -6],
                                    .8: [0, 0, -6], 1.2: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .25: [-25, 0, 6], .4: [0, 0, 6], .65: [-20, 0, 6],
                                     .8: [0, 0, 6], 1.2: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .4: [-10, 12, 0], .8: [-10, -12, 0], 1.2: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .4: [-8, 18, 0], .8: [-8, -18, 0], 1.2: [-4, 0, 0]})}})
    # swimming: limbs folded back along the body, the tail sweeps like a shark's
    def swim(L, amp_t, amp_b, paddle):
        return anim(L, merge(
            {"zamtrios": {"position": wave(1.2, L, L, axis=1, base=(0, 2, 0))}},
            {"body": {"rotation": wave(amp_b, L, L, axis=1, base=(0, 0, 0))}},
            {"head": {"rotation": wave(amp_b * 0.8, L, L, phase=math.pi, axis=1, base=(-4, 0, 0))}},
            {"jaw": {"rotation": [6, 0, 0]}},
            {"leftarm": {"rotation": wave(paddle, L, L, axis=0, base=(55, 0, -20))},
             "rightarm": {"rotation": wave(paddle, L, L, phase=math.pi, axis=0, base=(55, 0, 20))},
             "lowerleftarm": {"rotation": [-35, 0, 0]}, "lowerrightarm": {"rotation": [-35, 0, 0]},
             "leftleg": {"rotation": [60, 0, -8]}, "rightleg": {"rotation": [60, 0, 8]},
             "lowerleftleg": {"rotation": [-20, 0, 0]}, "lowerrightleg": {"rotation": [-20, 0, 0]}},
            {"tail1": {"rotation": wave(amp_t, L, L, phase=-0.8, axis=1, base=(0, 0, 0))}},
            {"tail2": {"rotation": wave(amp_t * 1.6, L, L, phase=-1.6, axis=1, base=(0, 0, 0))}}), loop=True)
    S["water_idle"] = swim(3.0, 8, 2, 4)
    S["water_swim"] = swim(1.2, 18, 5, 12)
    for a in S.values():
        hide_fx(a)
    return S

def inflated_set():
    """the giant inflated ball: limbs spread, the sac breathes (scale x2 = full size), a heavy bob"""
    K = BALLOON_K
    def sac(points):
        return {"balloon": {"scale": kf({t: [K * v[0], K * v[1], K * v[2]] for t, v in points.items()})}}
    pose = {"leftarm": {"rotation": [-10, 0, -32]}, "rightarm": {"rotation": [-10, 0, 32]},
            "lowerleftarm": {"rotation": [0, 0, 18]}, "lowerrightarm": {"rotation": [0, 0, -18]},
            "leftleg": {"rotation": [0, 0, -38]}, "rightleg": {"rotation": [0, 0, 38]},
            "tail1": {"rotation": [-14, 0, 0]}, "tail2": {"rotation": [-10, 0, 0]}}
    def with_pose(b):
        return merge(pose, b)
    S = {}
    L = 2.4
    breathe = sac({0: [1, 1, 1], L / 2: [1.04, 1.05, 1.04], L: [1, 1, 1]})
    S["ground_idle"] = anim(L, with_pose(merge(breathe,
        {"zamtrios": {"position": wave(1.0, L, L, axis=1, base=(0, 0, 0))}},
        {"head": {"rotation": wave(3, L, L, axis=0, base=(-6, 0, 0))}, "jaw": {"rotation": [6, 0, 0]}},
        {"tail2": {"rotation": wave(8, L, L, axis=1, base=(-10, 0, 0))}})), loop=True)
    S["battle_idle"] = anim(1.6, with_pose(merge(sac({0: [1, 1, 1], .8: [1.06, 1.07, 1.06], 1.6: [1, 1, 1]}),
        {"zamtrios": {"position": wave(1.6, 1.6, 1.6, axis=1, base=(0, 0.5, 0))}},
        {"head": {"rotation": wave(4, 1.6, 1.6, axis=0, base=(-10, 0, 0))}, "jaw": {"rotation": wave(6, .8, 1.6, axis=0, base=(14, 0, 0))}},
        {"leftarm": {"rotation": wave(10, 1.6, 1.6, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(10, 1.6, 1.6, phase=math.pi, axis=0, base=(-10, 0, 32))}})), loop=True)
    S["ground_walk"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .3: [1.05, .95, 1.05], .6: [1, 1, 1], .9: [1.05, .95, 1.05], 1.2: [1, 1, 1]}),
        {"zamtrios": {"rotation": wave(7, 1.2, 1.2, axis=2), "position": wave(1.5, .6, 1.2, axis=1, base=(0, 1.5, 0))}},
        {"leftarm": {"rotation": wave(20, 1.2, 1.2, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(20, 1.2, 1.2, phase=math.pi, axis=0, base=(-10, 0, 32))},
         "leftleg": {"rotation": wave(18, 1.2, 1.2, phase=math.pi, axis=0, base=(0, 0, -38))},
         "rightleg": {"rotation": wave(18, 1.2, 1.2, axis=0, base=(0, 0, 38))}})), loop=True)
    S["sleep"] = anim(3.0, with_pose(merge(sac({0: [1, .97, 1], 1.5: [1.02, 1, 1.02], 3.0: [1, .97, 1]}),
        {"zamtrios": {"position": [0, -1, 0]}, "head": {"rotation": [10, 0, 0]}, "jaw": {"rotation": [0, 0, 0]},
         "tail1": {"rotation": [-4, 18, 0]}, "tail2": {"rotation": [0, 24, 0]}})), loop=True)
    # body slam: hops high, slams down (the sac squashes), bounces back
    S["physical"] = anim(1.1, with_pose(merge(
        sac({0: [1, 1, 1], .25: [.95, 1.08, .95], .5: [1, 1, 1], .58: [1.16, .8, 1.16], .75: [.96, 1.06, .96],
             .9: [1.03, .98, 1.03], 1.1: [1, 1, 1]}),
        {"zamtrios": {"position": kf({0: [0, 0, 0], .25: [0, -1.5, 0], .42: [0, 16, -8], .56: [0, 0, -12],
                                      .75: [0, 3, -10], .9: [0, 0, -6], 1.1: [0, 0, 0]}),
                      "rotation": kf({0: [0, 0, 0], .42: [-12, 0, 0], .56: [8, 0, 0], .9: [0, 0, 0], 1.1: [0, 0, 0]})},
         "head": {"rotation": kf({0: [-6, 0, 0], .42: [-18, 0, 0], .56: [8, 0, 0], 1.1: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .42: [26, 0, 0], .58: [2, 0, 0], 1.1: [6, 0, 0]})}})))
    # special: puffs even bigger and sprays a jet of water from its jaws
    S["special"] = anim(1.4, with_pose(merge(
        sac({0: [1, 1, 1], .4: [1.12, 1.14, 1.12], .6: [1.02, 1.0, 1.02], 1.1: [.98, .97, .98], 1.4: [1, 1, 1]}),
        {"zamtrios": {"position": kf({0: [0, 0, 0], .4: [0, 3, 2], .6: [0, 1, 5], 1.1: [0, 1, 5], 1.4: [0, 0, 0]})},
         "head": {"rotation": kf({0: [-6, 0, 0], .4: [-24, 0, 0], .6: [0, 0, 0], .85: [2, 2, 0], 1.0: [2, -2, 0],
                                  1.1: [0, 0, 0], 1.4: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .4: [10, 0, 0], .55: [40, 0, 0], 1.1: [40, 0, 0], 1.3: [6, 0, 0],
                                 1.4: [6, 0, 0]})}})))
    # status: rolls a full turn on itself
    S["status"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .6: [1.06, 1.06, 1.06], 1.2: [1, 1, 1]}),
        {"zamtrios": {"rotation": kf({0: [0, 0, 0], .3: [0, 90, 0], .6: [0, 180, 0], .9: [0, 270, 0], 1.2: [0, 360, 0]}),
                      "position": kf({0: [0, 0, 0], .3: [0, 4, 0], .6: [0, 0, 0], .9: [0, 4, 0], 1.2: [0, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .6: [22, 0, 0], 1.2: [6, 0, 0]})}})))
    S["cry"] = anim(1.5, with_pose(merge(sac({0: [1, 1, 1], .4: [1.1, 1.12, 1.1], 1.1: [1.1, 1.12, 1.1], 1.5: [1, 1, 1]}),
        {"head": {"rotation": kf({0: [-6, 0, 0], .4: [-26, 0, 0], .7: [-24, 2, 0], .9: [-24, -2, 0], 1.1: [-24, 0, 0],
                                  1.5: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .4: [36, 0, 0], 1.1: [36, 0, 0], 1.5: [6, 0, 0]})},
         "zamtrios": {"position": kf({0: [0, 0, 0], .4: [0, 3, 0], 1.1: [0, 3, 0], 1.5: [0, 0, 0]})}})))
    # faint: a last cry, head up, the sac deflates with a wobble and the body slumps
    S["faint"] = anim(2.2, merge(
        sac({0: [1, 1, 1], .4: [1.08, 1.1, 1.08], .7: [1.0, 1.0, 1.0], 1.0: [.8, .75, .8], 1.3: [.6, .55, .6],
             1.6: [.45, .4, .45], 1.9: [.3, .3, .3], 2.2: [.3, .3, .3]}),
        {"zamtrios": {"rotation": kf({0: [0, 0, 0], .7: [0, 0, 0], .85: [0, 12, 3], 1.0: [0, -10, -3],
                                      1.15: [0, 8, 2], 1.3: [0, -6, -2], 1.5: [0, 3, 0], 2.2: [0, 0, 6]}),
                      "position": kf({0: [0, 0, 0], .4: [0, 2, 0], 1.6: [0, -2, 0], 2.2: [0, -3, 0]})},
         "head": {"rotation": kf({0: [-6, 0, 0], .4: [-34, 0, 0], .55: [-32, 3, 0], .7: [-34, -3, 0], 1.2: [-10, 0, 0],
                                  2.2: [14, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .35: [38, 0, 0], .8: [38, 0, 0], 1.4: [16, 0, 0], 2.2: [20, 0, 0]})},
         "leftarm": {"rotation": kf({0: [-10, 0, -32], 1.4: [-10, 0, -12], 2.2: [0, 0, -40]})},
         "rightarm": {"rotation": kf({0: [-10, 0, 32], 1.4: [-10, 0, 12], 2.2: [0, 0, 40]})},
         "lowerleftarm": {"rotation": kf({0: [0, 0, 18], 2.2: [0, 0, 30]})},
         "lowerrightarm": {"rotation": kf({0: [0, 0, -18], 2.2: [0, 0, -30]})},
         "leftleg": {"rotation": kf({0: [0, 0, -38], 2.2: [0, 0, -20]})},
         "rightleg": {"rotation": kf({0: [0, 0, 38], 2.2: [0, 0, 20]})},
         "tail1": {"rotation": kf({0: [-14, 0, 0], 2.2: [4, 10, 0]})},
         "tail2": {"rotation": kf({0: [-10, 0, 0], 2.2: [2, 18, 0]})}}), loop="hold")
    S["water_idle"] = anim(3.0, with_pose(merge(breathe if False else sac({0: [1, 1, 1], 1.5: [1.03, 1.04, 1.03], 3.0: [1, 1, 1]}),
        {"zamtrios": {"position": wave(2, 3.0, 3.0, axis=1, base=(0, 4, 0)), "rotation": wave(4, 3.0, 3.0, axis=2)}})), loop=True)
    S["water_swim"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .6: [1.03, .98, 1.03], 1.2: [1, 1, 1]}),
        {"zamtrios": {"position": wave(1.5, 1.2, 1.2, axis=1, base=(0, 4, 0)), "rotation": wave(5, 1.2, 1.2, axis=2)},
         "leftarm": {"rotation": wave(25, 1.2, 1.2, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(25, 1.2, 1.2, phase=math.pi, axis=0, base=(-10, 0, 32))},
         "tail2": {"rotation": wave(16, 1.2, 1.2, axis=1, base=(-10, 0, 0))}})), loop=True)
    for a in S.values():
        hide_fx(a)
    return S

def armor_set():
    S = copy.deepcopy(base_set())
    for b in GLOW:                                         # asleep: the ice stops glowing
        S["sleep"]["bones"].setdefault(b, {})["scale"] = [0, 0, 0]
    return S

ANIMS = {"zamtrios": base_set(), "zamtrios_armor": armor_set(), "zamtrios_inflated": inflated_set()}

# ------------------------------------------------------------------------------------------------ posers
def poser(group, geo_bones):
    portrait_sim.set_mode("portrait")
    s, tx, ty = portrait_sim.auto_frame(geo_bones, fill=13.5, below=0.5, names=("head", "jaw"))
    qs, qx, qy = portrait_sim.auto_profile([b for b in geo_bones if b["name"] not in FX])
    q = lambda a: f"q.bedrock('{group}', '{a}')"
    prim = lambda a: f"q.bedrock_primary('{group}', '{a}', q.curve('symmetrical_wide'))"
    return {
        "portraitScale": s, "portraitTranslation": [tx, ty, 0], "profileScale": qs, "profileTranslation": [qx, qy, 0],
        "rootBone": "zamtrios",
        "animations": {"cry": f"q.bedrock_stateful('{group}', 'cry')",
                       "faint": f"q.bedrock_primary('{group}', 'faint', q.curve('one'))",
                       "physical": prim("physical"), "special": prim("special"), "status": prim("status")},
        "poses": {
            "battle-standing": {"poseTypes": ["STAND"], "isBattle": True,
                                "animations": ["q.look('head')", q("battle_idle")]},
            "standing": {"poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"], "isBattle": False,
                         "animations": ["q.look('head')", q("ground_idle")]},
            "walking": {"poseTypes": ["WALK"], "animations": ["q.look('head')", q("ground_walk")]},
            "floating": {"poseTypes": ["FLOAT"], "animations": ["q.look('head')", q("water_idle")]},
            "swimming": {"poseTypes": ["SWIM"], "animations": ["q.look('head')", q("water_swim")]},
            "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]}}}

tops = {}
for name, g in MODELS.items():
    gb = g["minecraft:geometry"][0]["bones"]
    json.dump(g, open(f"{A}/bedrock/pokemon/models/{FOLDER}/{name}.geo.json", "w"), indent=1)
    json.dump(g, open(f"{tmp}/{name}.geo.json", "w"))
    an = {"format_version": "1.8.0", "animations": {f"animation.{name}.{k}": v for k, v in ANIMS[name].items()}}
    json.dump(an, open(f"{A}/bedrock/pokemon/animations/{FOLDER}/{name}.animation.json", "w"), indent=1)
    json.dump(an, open(f"{tmp}/{name}.animation.json", "w"))
    json.dump(poser(name, gb), open(f"{A}/bedrock/pokemon/posers/{FOLDER}/{name}.json", "w"), indent=2)
    # height of the standing model (feet to the top of the dorsal fin), effects and the sac excluded
    M = portrait_sim.mats(gb)
    hi = 0.0
    for b in gb:
        if b["name"] in FX or b["name"] == "balloon":
            continue
        for c in b.get("cubes", []):
            o, s_ = c["origin"], c["size"]
            for dx in (0, s_[0]):
                for dy in (0, s_[1]):
                    for dz in (0, s_[2]):
                        hi = max(hi, portrait_sim.apply(M[b["name"]], (o[0] + dx, o[1] + dy, o[2] + dz))[1])
    tops[name] = round(hi, 2)
    print(f"{name}: {sum(len(b.get('cubes', [])) for b in gb)} cubes, {len(gb)} bones, top {hi:.1f}")

tex = lambda n: f"cobblemon:textures/pokemon/{FOLDER}/{n}.png"
glow = lambda k: [{"name": "emissive", "texture": tex(f"glow/zamtrios_armor_{k}"), "emissive": True}]
res = f"{A}/bedrock/pokemon/resolvers/{FOLDER}"
json.dump({"species": f"cobblemon:{SID}", "order": 0, "variations": [
    {"aspects": [], "poser": "cobblemon:zamtrios", "model": "cobblemon:zamtrios.geo", "texture": tex("zamtrios")},
    {"aspects": ["shiny"], "texture": tex("zamtrios_shiny")}]}, open(f"{res}/0_zamtrios_base.json", "w"), indent=2)
json.dump({"species": f"cobblemon:{SID}", "order": 1, "variations": [
    {"aspects": ["zamtrios-armor"], "poser": "cobblemon:zamtrios_armor", "model": "cobblemon:zamtrios_armor.geo",
     "texture": tex("zamtrios_armor"), "layers": glow("normal")},
    {"aspects": ["zamtrios-armor", "shiny"], "texture": tex("zamtrios_armor_shiny"), "layers": glow("shiny")}]},
    open(f"{res}/1_zamtrios_armor.json", "w"), indent=2)
json.dump({"species": f"cobblemon:{SID}", "order": 2, "variations": [
    {"aspects": ["zamtrios-inflated"], "poser": "cobblemon:zamtrios_inflated", "model": "cobblemon:zamtrios_inflated.geo",
     "texture": tex("zamtrios")},
    {"aspects": ["zamtrios-inflated", "shiny"], "texture": tex("zamtrios_shiny")}]},
    open(f"{res}/2_zamtrios_inflated.json", "w"), indent=2)
json.dump({"top_base": tops["zamtrios"], "top_armor": tops["zamtrios_armor"], "top_inflated": tops["zamtrios_inflated"]},
          open(f"{tmp}/zamtrios_tops.json", "w"))
print("atlas", TW, "x", TH, "used rows", used)
