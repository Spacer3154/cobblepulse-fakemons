# -*- coding: utf-8 -*-
"""#11231 Deviljho — Wyverne brute de Monster Hunter (Dragon / Ténèbres), et sa méga-évolution Deviljho Carnage.

Silhouette of a brute wyvern: hunched barrel body peaking at the shoulders, short bull neck plunging to a head carried
low, a colossal underslung lower jaw (wider and longer than the upper one) bristling with teeth outside the lips and
ending in a golden spiked chin, small eyes under a heavy brow, tiny clawed arms, enormous drumstick thighs on
digitigrade legs with three great toes, and a long heavy tail fringed with two rows of golden spikes. Dark olive scaly
hide, lighter ochre ribbed belly, rows of pale studs along the back, old red scars.

Deviljho Carnage (mega): the rage state pushed to its limit — the muscles swell (chest, neck, thighs), the back turns a
blood-black and splits into glowing crimson veins, a mane of red bristles rises from the skull to the tail, the eyes burn
red and trail light, red lightning crackles around the head and the back, dragon energy drools from the jaws, more and
longer spikes. Shiny: obsidian black (shiny Carnage: violet dragon energy)."""
import math
from modelgen import Model, Cube, rgb, mix, apply, shade, fill
from biped import (Leg, walk, leg_pose, timeline, keys, kf, lowest, drape, standard_anims, lie_legs, pose_sequence,
                   search, descendants, pose_to_bones, smooth)
from bovine import vnoise, put, light, side_cols
from templates import poser as make_poser, tremble

SID, DEX = "deviljho", 11231
FRAME_BONES = ("head", "jaw", "neck")
HEIGHT_SKIP = ("spine", "aura", "bolt", "breath", "drool", "frill", "teeth", "ember")
HITBOX_WIDTH = 2.0
SPECIES_DIR = "monster_hunter"

# ---------------------------------------------------------------------------------------------------- palettes
PAL = {     # olive-brown hide of the reference, golden spike-teeth, pink gape, red-tipped claws
    "skin": rgb("#5B5631"), "skin_dark": rgb("#3C3920"), "skin_light": rgb("#7A7446"), "skin_back": rgb("#4A4529"),
    "scale_line": rgb("#33301B"),
    "belly": rgb("#55522F"), "belly_dark": rgb("#3A3820"), "belly_light": rgb("#6E6B42"),
    "stud": rgb("#8E7A46"), "stud_dark": rgb("#5E5030"),
    "scar": rgb("#8A2A22"), "scar_glow": rgb("#B03024"),
    "spike": rgb("#A88443"), "spike_dark": rgb("#4E3A1E"), "spike_tip": rgb("#DCC27E"),
    "spine": rgb("#5A3A22"), "spine_tip": rgb("#B07C52"),
    "mouth": rgb("#5E1620"), "gum": rgb("#C4505E"), "tongue": rgb("#D88088"), "palate": rgb("#A23A48"),
    "throat": rgb("#3A0A10"),
    "claw": rgb("#3A2A20"), "claw_tip": rgb("#B8412E"),
    "eye": rgb("#F2B21E"), "eye_rim": rgb("#A8281A"), "pupil": rgb("#0A0402"), "eye_shine": rgb("#FFF4C0"),
    "socket": rgb("#1C1A0E"), "eye_glint": rgb("#FFB424"),
    "saliva": rgb("#CFC9A2"), "saliva_tip": rgb("#F2EED8"),
    "ember": rgb("#FF7A2A"), "ember_hot": rgb("#FFE0A0"),
    "nostril": rgb("#1A140A"),
    # dragon energy (special attack breath, mega effects)
    "breath_core": rgb("#FFD2B0"), "breath": rgb("#FF4A2A"), "breath_mid": rgb("#C0121C"), "breath_edge": rgb("#3A0408"),
    "rage": rgb("#3C0C0C"), "rage_dark": rgb("#1E0606"), "vein": rgb("#FF3A20"), "vein_hot": rgb("#FFB08A"),
    "bolt": rgb("#7A0608"), "bolt_core": rgb("#FF4A2E"),
    "smoke": rgb("#241012"), "smoke_dark": rgb("#100808"), "smoke_red": rgb("#5A0E12"), "smoke_glow": rgb("#E8281C"),
    "mouth_glow": rgb("#FF4A24"), "mouth_hot": rgb("#FFC890"),
    "eye_glow": rgb("#FF2A14"), "eye_hot": rgb("#FFF2D8"),
}
SHINY = dict(PAL, **{        # obsidian black, as in the original shiny texture
    "socket": rgb("#060606"),
    "skin": rgb("#242322"), "skin_dark": rgb("#131212"), "skin_light": rgb("#3A3936"), "skin_back": rgb("#1A1918"),
    "scale_line": rgb("#0C0C0C"),
    "belly": rgb("#3A3832"), "belly_dark": rgb("#25231F"), "belly_light": rgb("#504D46"),
    "spine": rgb("#141414"), "spine_tip": rgb("#4A4A48"), "stud": rgb("#6A6250"),
})
MEGA = dict(PAL, **{         # Carnage: darker brown hide, blood-black rage zones, red dragon energy
    "skin": rgb("#514530"), "skin_dark": rgb("#30281A"), "skin_light": rgb("#6E6044"), "skin_back": rgb("#3A2A1E"),
    "scale_line": rgb("#241C12"),
    "scar": rgb("#8A1A14"), "scar_glow": rgb("#FF3A20"),
    "spike": rgb("#B88E44"), "spike_tip": rgb("#E8C880"),
    "spine": rgb("#5A0A0C"), "spine_tip": rgb("#FF5A3A"),
    "eye": rgb("#FF2A14"), "mouth": rgb("#7A1418"), "palate": rgb("#C02A24"), "tongue": rgb("#E0605A"),
})
MEGA_SHINY = dict(MEGA, **{  # obsidian body, violet dragon energy
    "skin": rgb("#201F1E"), "skin_dark": rgb("#0F0E0E"), "skin_light": rgb("#353432"), "skin_back": rgb("#1A1022"),
    "scale_line": rgb("#080808"),
    "belly": rgb("#3A3830"), "belly_dark": rgb("#24221C"), "belly_light": rgb("#54504A"),
    "scar": rgb("#5A1A7A"), "scar_glow": rgb("#C24AFF"),
    "rage": rgb("#24102E"), "rage_dark": rgb("#120818"), "vein": rgb("#C24AFF"), "vein_hot": rgb("#F2D2FF"),
    "bolt": rgb("#4A0A70"), "bolt_core": rgb("#D070FF"),
    "smoke": rgb("#1A0E24"), "smoke_dark": rgb("#0A060E"), "smoke_red": rgb("#3A0E5A"), "smoke_glow": rgb("#B03CFF"),
    "mouth": rgb("#4A145A"), "palate": rgb("#7A2AA0"), "tongue": rgb("#B060C8"), "gum": rgb("#9A50B0"),
    "mouth_glow": rgb("#C04AFF"), "mouth_hot": rgb("#F0D0FF"),
    "spine": rgb("#2A0A3A"), "spine_tip": rgb("#C070FF"),
    "eye_glow": rgb("#D050FF"), "eye_hot": rgb("#FBEAFF"), "eye": rgb("#D050FF"),
    "ember": rgb("#C060FF"), "ember_hot": rgb("#F4D8FF"),
    "breath_core": rgb("#F6DEFF"), "breath": rgb("#C04AFF"), "breath_mid": rgb("#6A12B0"), "breath_edge": rgb("#1A0430"),
})
SHINY_BREATH = {"breath_core": rgb("#FFE6D0"), "breath": rgb("#FF5A2A"), "breath_mid": rgb("#B0101A"), "breath_edge": rgb("#200204")}
SHINY.update(SHINY_BREATH)

GLOW = {"glow": True, "shading": False}

# ---------------------------------------------------------------------------------------------------- painters
def _seg_dist(p, a, b):
    ab = [b[i] - a[i] for i in range(3)]
    ap = [p[i] - a[i] for i in range(3)]
    L2 = sum(v * v for v in ab) or 1e-9
    t = max(0.0, min(1.0, sum(ap[i] * ab[i] for i in range(3)) / L2))
    return math.dist(p, [a[i] + ab[i] * t for i in range(3)])

# old fight scars (world space, rest pose): a few raking claw marks on the flanks, thighs and shoulders
SCARS = []
for sx in (1, -1):
    SCARS += [((8.6 * sx, 40, -14), (9.3 * sx, 33, -8)), ((8.9 * sx, 41, -12), (9.4 * sx, 35, -6.5)),
              ((8.6 * sx, 43, 2), (8.7 * sx, 36, 9)), ((10.9 * sx, 36, 3), (10.9 * sx, 28, 6)),
              ((7.2 * sx, 37, 20), (6.9 * sx, 33, 25))]
SCARS += [((3, 47.5, -16), (-2, 48.5, -9)), ((-4, 47, 0), (1, 47.6, 6))]

def _hpt(ix, iy, iz, seed):
    n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    r = []
    for k in range(3):
        n = (n * 1103515245 + 12345) & 0x7FFFFFFF
        r.append((n >> 8) / float(1 << 23))
    return r

def _veins(p, seed=5, cell=4.2, width=0.36):
    """Crack network (cell edges, F2 - F1 < width) masked by noise so it comes in patches: glowing rage veins."""
    if vnoise(p[0] * 0.15 + 3, p[1] * 0.15, p[2] * 0.15, seed + 3) < 0.38:
        return False
    x, y, z = (v / cell for v in p)
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    d1 = d2 = 9e9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                o = _hpt(ix + dx, iy + dy, iz + dz, seed)
                d = math.dist((x, y, z), (ix + dx + o[0], iy + dy + o[1], iz + dz + o[2]))
                if d < d1:
                    d1, d2 = d, d1
                elif d < d2:
                    d2 = d
    return (d2 - d1) * cell < width

def hide(*, belly=0, back=True, studs=True, mega=False, rage_y=None, rib=2.5, base="skin", rows_top=1, veins=None,
         scars=True, post=None, post_glow=None, plates=(3, 3), **extra):
    """Scaly hide painted in world space so patterns run across cubes.
    belly: bottom rows of the side faces (plus the down face) painted as ribbed belly plates;
    studs: rows of pale studs along the top edges; rage_y: (mega) everything above this height turns blood-black;
    veins: (mega) glowing ridge-noise veins above this height."""
    def classify(c, face, pl, p):
        x0, y0, z0 = c.origin
        w, h, d = c.size
        key, f2 = base, 1.0
        m = vnoise(p[0] * 0.28, p[1] * 0.28, p[2] * 0.28, 3)
        if m > 0.64:
            key = "skin_dark"
        elif m < 0.3:
            key = "skin_light"
        g = vnoise(p[0] * 1.3, p[1] * 1.3, p[2] * 1.3, 9)          # scale relief
        f2 = 0.9 + 0.22 * g
        if plates and face != "down":                                 # staggered scale plates (dark outlines)
            pw, ph = plates
            if face in ("east", "west"):
                u, v = p[2], p[1]
            elif face in ("north", "south"):
                u, v = p[0], p[1]
            else:
                u, v = p[0], p[2]
            row = math.floor(v / ph)
            uu = (u / pw + 0.5 * (row % 2)) % 1.0
            if uu < 0.5 / pw or ((v / ph) % 1.0 < 0.5 / ph and vnoise(u * 0.7, v * 0.7, 1.5, 21) > 0.35):
                f2 *= 0.86
        if back and (face == "up" or (face in ("east", "west", "north", "south") and pl[1] > y0 + h - 1.01)):
            key = "skin_back" if m < 0.7 else "skin_dark"
        if rage_y is not None and p[1] > rage_y + (vnoise(p[0] * 0.5, 1.0, p[2] * 0.5, 4) - 0.5) * 4:
            r = vnoise(p[0] * 0.4 + 2, p[1] * 0.4, p[2] * 0.4, 6)
            key = "rage_dark" if r > 0.58 else "rage"
        if belly and (face == "down" or (face in ("east", "west", "north", "south") and pl[1] < y0 + belly)):
            key = "belly"
            if (p[2] % rib) < 0.75:
                key = "belly_dark"
            elif (p[2] % rib) > rib - 0.6:
                key = "belly_light"
        if studs and face in ("east", "west") and abs(pl[1] - (y0 + h - 1.5)) < 0.51 and int(math.floor(p[2])) % 2 == 0:
            key = "stud"
        if studs and face == "up" and (abs(pl[0] - (x0 + 1.5)) < 0.51 or abs(pl[0] - (x0 + w - 1.5)) < 0.51) \
                and int(math.floor(p[2])) % 2 == 0 and w >= 6:
            key = "stud"
        if scars and any(_seg_dist(p, a, b) < 0.55 for a, b in SCARS):
            key = "scar"
        if veins is not None and p[1] > veins and _veins(p):
            key = "vein"
        return key, f2

    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            key, f2 = classify(c, face, pl, p)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.14) * f2
            if key == "vein":
                put(px, X, Y, pal["vein"], 1.0, rnd, 6)
            else:
                put(px, X, Y, pal[key], f, rnd, 5)
        if post:
            post(px, faces, pal, rnd)

    def glow_fn(px, faces, pal, rnd, c):
        if post_glow:
            post_glow(px, faces, pal, rnd)
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            key, _ = classify(c, face, pl, p)
            if key == "scar":
                put(px, X, Y, pal["scar_glow"], 1.0, rnd, 6)
            elif key == "vein":
                hot = vnoise(p[0] * 0.9, p[1] * 0.9, p[2] * 0.9, 12) > 0.66
                put(px, X, Y, pal["vein_hot"] if hot else pal["vein"], 1.0, rnd, 8)

    d = {"base": base, "fn3": fn3, "glow_fn": glow_fn}
    d.update(extra)
    return d

def spike_fn(along="y"):
    """Golden spike: dark root, golden shaft, pale tip (gradient along the cube's length axis)."""
    def fn(px, faces, pal, rnd):
        for face, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if along == "y":
                        t = 1 - j / max(h - 1, 1) if face not in ("up", "down") else (1.0 if face == "up" else 0.0)
                    else:   # along z (spike pointing back / forward): use the column
                        t = i / max(w - 1, 1) if face in ("east", "west", "up", "down") else 0.5
                    k = "spike_dark" if t < 0.3 else ("spike_tip" if t > 0.8 else "spike")
                    put(px, x + i, y + j, pal[k], light(face, j, h), rnd, 4)
    return {"fn": fn, "base": "spike"}

def spine_fn(px, faces, pal, rnd):
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                t = 1 - j / max(h - 1, 1)
                put(px, x + i, y + j, pal["spine_tip"] if t > 0.75 else pal["spine"], light(face, j, h), rnd, 4)

def tooth_fn(px, faces, pal, rnd):
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                t = j / max(h - 1, 1)
                put(px, x + i, y + j, pal["tooth_dark"] if (t > 0.75 and face != "down") else pal["tooth"],
                    light(face, j, h), rnd, 3)

def tooth_down_fn(px, faces, pal, rnd):    # upper teeth: root at the top
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                t = j / max(h - 1, 1)
                put(px, x + i, y + j, pal["tooth_dark"] if (t < 0.25 and face != "up") else pal["tooth"],
                    light(face, j, h), rnd, 3)

def claw_fn(px, faces, pal, rnd):
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                put(px, x + i, y + j, pal["claw_tip"] if (face == "north" or i == 0 and face in ("east", "west")) else pal["claw"],
                    light(face, j, h), rnd, 3)

def mouth_fn(key="mouth", glow=False):
    """Inside of the mouth on the face that meets the other jaw: pink gums along the rim, red palate with ridges
    (upper jaw) or dark throat with a big pink tongue (lower jaw). glow=True: the emissive pass of the same texels
    (Carnage: the gape burns red)."""
    def fn(px, faces, pal, rnd):
        fc = "up" if key == "jaw" else "down"
        x, y, w, h = faces[fc]
        for j in range(h):
            for i in range(w):
                edge = i == 0 or i == w - 1 or (j == h - 1 if fc == "up" else j == 0)
                if fc == "down":
                    k = "gum" if edge else ("palate" if (j % 3) else "mouth")
                else:
                    k = "gum" if edge else "throat" if j < 2 else "mouth"
                    if not edge and abs(i - (w - 1) / 2) < w * 0.26 and 1 < j < h - 1:
                        k = "tongue"
                if glow:
                    if edge:
                        continue
                    k = "mouth_hot" if (fc == "up" and j < 1 and abs(i - (w - 1) / 2) < 1.5) else (
                        "mouth_glow" if (i + j) % 3 else "breath_mid")
                put(px, x + i, y + j, pal[k], 1.0, rnd, 5)
    return fn

def throat_fn(glow=False):
    """Soft tissue of the gape (seen when the jaws part): red-pink folds, dark hole at the back."""
    def fn(px, faces, pal, rnd):
        for face, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    k = "palate" if (i + j) % 4 else "gum"
                    if face == "north" and abs(i - (w - 1) / 2) < w * 0.22 and j > h * 0.4:
                        k = "throat"
                    if glow:
                        if k == "throat":
                            k = "mouth_hot" if (abs(i - (w - 1) / 2) < 1 and j == h - 2) else "mouth_glow"
                        else:
                            k = "breath_mid"
                    put(px, x + i, y + j, pal[k], 1.0 if glow else light(face, j, h), rnd, 5)
    return fn

def grad_fn(keys):
    """Gradient along the cube's length (+Y in the cube frame): keys[0] at the root, keys[-1] at the tip."""
    def fn(px, faces, pal, rnd):
        n = len(keys)
        for face, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if face == "up":
                        t = 1.0
                    elif face == "down":
                        t = 0.0
                    else:
                        t = 1 - j / max(h - 1, 1)
                    put(px, x + i, y + j, pal[keys[min(n - 1, int(t * n))]], light(face, j, h), rnd, 4)
    return {"fn": fn, "base": keys[0]}

GOLD_ROOT = grad_fn(("spike_dark", "spike"))
GOLD_TIP = grad_fn(("spike", "spike", "spike_tip"))
GOLD_ONE = grad_fn(("spike_dark", "spike", "spike", "spike_tip"))
SPINE = grad_fn(("spine", "spine", "spine_tip"))

def _dir_rot(d):
    """Cube rotation [x, 0, z] that turns the cube's +Y axis toward direction d (see modelgen.rot_m)."""
    n = math.sqrt(sum(v * v for v in d))
    dx, dy, dz = (v / n for v in d)
    return [round(math.degrees(math.asin(max(-1.0, min(1.0, -dz)))), 1), 0, round(math.degrees(math.atan2(dx, dy)), 1)]

def spike(p, d, L=2, w=1, paints=None):
    """A conical spike rooted at p (half sunk into the surface) pointing along d: w=2 gives a 2x2 root + 1x1 tip."""
    x, y, z = p
    rot = _dir_rot(d)
    if w >= 2:
        root, tip = paints or (GOLD_ROOT, GOLD_TIP)
        return [Cube([x - 1, y - 1, z - 1], [2, 2, 2], root, rotation=rot, pivot=[x, y, z]),
                Cube([x - 0.5, y + 1, z - 0.5], [1, max(1, L - 1), 1], tip, rotation=rot, pivot=[x, y, z])]
    one = paints[0] if paints else GOLD_ONE
    return [Cube([x - 0.5, y - 0.5, z - 0.5], [1, L, 1], one, rotation=rot, pivot=[x, y, z])]

EYE_ROWS = {          # 5 x 3, columns from the FRONT: narrowed and slanted (the brow weighs on the front corner)
    False: ["SSSR.", "RIPIS", ".SRS."],
    True: ["GGGG.", "HHPHG", ".GGGS"],
}
EYE_KEYS = {"S": "socket", "R": "eye_rim", "I": "eye", "P": "pupil", "G": "eye_glow", "H": "eye_hot"}
EYE_GLOW = {"I": "eye_glint", "G": "eye_glow", "H": "eye_hot", "P": "pupil"}

def _eye_paint(mega, glow):
    rows = EYE_ROWS[mega]
    def fn(px, faces, pal, rnd, *_):
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face not in ("east", "west"):
                continue
            cols = side_cols(face, w)
            for j, row in enumerate(rows[:h]):
                for fi, ch in enumerate(row[:w]):
                    if ch == ".":
                        continue
                    key = (EYE_GLOW.get(ch) if glow else EYE_KEYS[ch])
                    if key:
                        put(px, x + cols[fi], y + j, pal[key], 1.0, rnd, 2)
    return fn

def eye_fn(mega):
    """Small, narrowed reptilian eye in a dark socket: amber iris (it catches the light: emissive glint), black slit
    pupil, raw red rim. Carnage: burning red with a white-hot ring around the black slit."""
    return {"fn": _eye_paint(mega, False), "glow_fn": _eye_paint(mega, True), "shading": False}

def trail_fn(px, faces, pal, rnd):
    """Light trail behind a burning eye: bright at the eye, thinning out backward."""
    for face, (x, y, w, h) in faces.items():
        if not (w and h):
            continue
        for j in range(h):
            for i in range(w):
                t = i / max(w - 1, 1)
                if face == "west":
                    t = 1 - t
                if t > 0.85 and j != h // 2:
                    continue
                put(px, x + i, y + j, pal["eye_hot"] if t < 0.25 else pal["eye_glow"], 1.0, rnd, 4)

def bolt_fn(seed, branch=0.35):
    """Forked lightning on a transparent plane, running along the plane's length (+Y from the root): straight runs
    broken by sharp kinks, a dark crimson core edged with blazing red (as in the Carnage artwork), and side forks."""
    def fn(px, faces, pal, rnd):
        import random
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face in ("up", "down"):
                continue
            r = random.Random(seed)
            core = set()
            def run(col, j, length, depth):
                drift = r.choice((-1, 1))
                left = r.randint(2, 4)
                while length > 0 and j >= 0:
                    core.add((col, j))
                    if left <= 0:                      # kink: change direction
                        drift = -drift if r.random() < 0.7 else 0
                        left = r.randint(2, 5)
                    nc = col + drift
                    if 1 <= nc <= w - 2:
                        col = nc
                    else:
                        drift = -drift
                    left -= 1
                    if depth < 2 and r.random() < branch / (depth + 2) and length > 5:
                        run(col, j - 1, r.randint(3, 7), depth + 1)
                    j -= 1
                    length -= 1
            run(w // 2, h - 1, h, 0)
            halo = {(c + dc, j + dj) for c, j in core for dc in (-1, 0, 1) for dj in (-1, 0, 1)
                    if abs(dc) + abs(dj) == 1} - core
            for c, j in halo:
                if 0 <= c < w and 0 <= j < h:
                    put(px, x + c, y + j, pal["bolt"], 1.0, rnd, 8)
            for c, j in core:
                put(px, x + c, y + j, pal["bolt_core"], 1.0, rnd, 4)
    return {"fn": fn, **GLOW}

def _smoke_density(i, j, w, h, seed):
    u = (i + 0.5) / w * 2 - 1
    t = (j + 0.5) / h                      # 0 = top of the plane, 1 = root (body side)
    n = vnoise(i * 0.22 + seed * 7.1, j * 0.16, seed * 1.7, seed)
    n2 = vnoise(i * 0.5 + seed, j * 0.45 + 3, seed * 2.3, seed + 5)
    plume = 1 - abs(u + (n - 0.5) * 0.8) * (1.25 - 0.55 * t)
    return plume * (0.35 + 0.75 * t) + (n2 - 0.5) * 0.35

def smoke_fn(seed):
    """Billowing black-red dragon miasma on a transparent plane: dense and red-hot at the root, rising in tongues."""
    def grid(w, h):
        g = {(i, j): _smoke_density(i, j, w, h, seed) for j in range(h) for i in range(w)}
        keep = {k for k, v in g.items() if v >= 0.3}
        # clean-up: no lone pixels (reads as smoke, not confetti)
        return {k: g[k] for k in keep
                if sum((k[0] + di, k[1] + dj) in keep for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 2}
    def fn(px, faces, pal, rnd):
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face in ("up", "down"):
                continue
            for (i, j), dsy in grid(w, h).items():
                k = "smoke_dark" if dsy < 0.45 else ("smoke" if dsy < 0.68 else "smoke_red")
                put(px, x + i, y + j, pal[k], 1.0, rnd, 3)
    def glow(px, faces, pal, rnd, c):
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face in ("up", "down"):
                continue
            for (i, j), dsy in grid(w, h).items():
                fleck = 0.5 < dsy < 0.8 and _hpt(i, j, seed, 77)[0] > 0.86
                if dsy > 0.8 or fleck:
                    put(px, x + i, y + j, pal["smoke_glow"] if dsy > 0.8 else pal["ember"], 1.0, rnd, 10)
    return {"fn": fn, "glow_fn": glow, "shading": False}

def drool_fn(px, faces, pal, rnd):
    for face, (x, y, w, h) in faces.items():
        if not (w and h) or face in ("up", "down"):
            continue
        for i in range(w):
            ln = h if i % 2 == 0 else max(1, h // 2)
            for j in range(ln):
                put(px, x + i, y + j, pal["breath"] if j < ln - 1 else pal["breath_core"], 1.0, rnd, 6)

def saliva_fn(px, faces, pal, rnd):
    for face, (x, y, w, h) in faces.items():
        if not (w and h) or face in ("up", "down"):
            continue
        for i in range(w):
            ln = (h if i == 1 else (h * 2) // 3 if i == 3 else h // 3) if i % 2 else 0
            for j in range(ln):
                put(px, x + i, y + j, pal["saliva"] if j < ln - 1 else pal["saliva_tip"], 1.0, rnd, 4)

def breath_fn(px, faces, pal, rnd):
    """Beam of dragon energy: white-hot core, red body, black-red rim (side faces read across their height)."""
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                if face in ("north", "south"):
                    r = max(abs(i - (w - 1) / 2) / max((w - 1) / 2, 1), abs(j - (h - 1) / 2) / max((h - 1) / 2, 1))
                elif face in ("east", "west"):
                    r = abs(j - (h - 1) / 2) / max((h - 1) / 2, 1)
                else:
                    r = abs(i - (w - 1) / 2) / max((w - 1) / 2, 1) if w > 1 else 0.5
                k = "breath_core" if r < 0.3 else ("breath" if r < 0.62 else ("breath_mid" if r < 0.9 else "breath_edge"))
                put(px, x + i, y + j, pal[k], 1.0, rnd, 5)

# ---------------------------------------------------------------------------------------------------- legs
def leg_paints(mega):
    hd = hide(belly=0, studs=False, mega=mega, veins=26 if mega else None)
    return {"thigh": hd, "shin": hide(belly=0, studs=False, scars=False, veins=20 if mega else None),
            "meta": hide(studs=False, back=False, scars=False), "foot": hide(studs=False, back=False, scars=False),
            "claw": {"fn": claw_fn, "base": "claw"}}

def make_legs(mega):
    th = (12, 15, 5) if mega else (11, 14, 5)
    return [Leg(side, 9.5 * sx, 6, (14, 13, 9), (-28, 38, -18), 3, thigh=th, shin=(8, 8) if mega else (7, 7),
                meta=(6, 6), foot=(9, 10, 3), claws=(-3, 0, 3), paints=leg_paints(mega), claw_len=4, dewclaw=True)
            for side, sx in (("left", 1), ("right", -1))]

LEGS = make_legs(False)
H = LEGS[0].H                    # hip height
TAIL = ("tail", "tail2", "tail3", "tail4", "tail5")

# ---------------------------------------------------------------------------------------------------- model
def build(mega=False):
    legs = make_legs(mega)
    m = Model("deviljho_carnage" if mega else SID, DEX, (256, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, H, 6])
    vy = (H + 4) if mega else None          # veins above the hips (mega)
    for lg in legs:
        lg.build(m)
        x = lg.x
        sx = 1 if x > 0 else -1
        # drumstick thigh: a big rounded muscle mass on the outside and the back of the thigh
        tw = lg.thigh[0]
        m.get(lg.bones[0]).cubes += [
            Cube([x - tw / 2 + (1 if sx > 0 else -1), H - 14, 6 - 9], [tw, 16, 17 if mega else 16],
                 hide(studs=False, veins=vy and H - 10, mega=mega), inflate=0.2),
            Cube([x + (tw / 2 - 1 if sx > 0 else -tw / 2 - 1), H - 9, 6 - 5], [2, 9, 9], hide(studs=False, mega=mega)),
        ]
        # calf muscle at the back of the shin, scutes on the front of the metatarsus
        m.get(lg.bones[1]).cubes.append(Cube([x - 3, H - 14 - 9, 6 + 1], [6, 8, 3], hide(studs=False, back=False, scars=False)))
        m.get(lg.bones[2]).cubes.append(Cube([x - 2.5, H - 14 - 13 - 8, 6 - 3.6], [5, 7, 1], hide(studs=True, back=False, scars=False)))
    # ------------------------------------------------------------------ trunk
    bw = 18 if mega else 17
    m.bone("torso", "body", [0, H, 6], rotation=[-21 if mega else -7, 0, 0], cubes=[
        Cube([-bw / 2, H - 9, -6], [bw, 19, 22], hide(belly=5, rage_y=H + 6 if mega else None, veins=vy, mega=mega)),
        Cube([-(bw - 4) / 2, H + 10, -4], [bw - 4, 3, 18], hide(rage_y=H + 6 if mega else None, veins=vy, mega=mega)),
        Cube([-(bw - 3) / 2, H - 11, -4], [bw - 3, 2, 16], hide(belly=2)),
    ])
    cw = 20 if mega else 18
    m.bone("chest", "torso", [0, H + 4, -5], rotation=[5, 0, 0], cubes=[
        Cube([-cw / 2, H - 9, -22], [cw, 22, 18], hide(belly=6, rage_y=H + 5 if mega else None, veins=vy, mega=mega)),
        Cube([-(cw - 5) / 2, H + 13, -20], [cw - 5, 2, 14], hide(rage_y=H + 5 if mega else None, veins=vy, mega=mega)),
        Cube([-(cw - 4) / 2, H - 12, -20], [cw - 4, 3, 14], hide(belly=3)),
    ] + [Cube([(cw / 2 - 0.5) * sx - (0 if sx > 0 else 2) + (0 if sx > 0 else 0), H - 3, -19], [2, 11, 12],
              hide(studs=False, veins=vy, mega=mega)) for sx in (1, -1)])
    # ------------------------------------------------------------------ dorsal crest: dark spines (red bristles when mega)
    def spines(bone, zs, y, h0=3, lean=-35):
        for k, z in enumerate(zs):
            hh = h0 + (1 if k % 2 == 0 else 0) + (2 if mega else 0)
            m.bone(f"spine_{bone}_{k}", bone, [0, y, z], rotation=[lean, 0, 0], cubes=[
                Cube([-0.5, y - 0.5, z - 0.5], [1, hh, 1], {"fn": spine_fn, "base": "spine"}),
                Cube([-1, y - 0.5, z - 1], [2, max(1, hh // 2), 2], {"fn": spine_fn, "base": "spine"})])
    spines("torso", [-2, 2, 6, 10, 14], H + 12.5)
    spines("chest", [-18, -14.5, -11, -7.5], H + 14.5)
    # ------------------------------------------------------------------ arms (tiny, three hooked claws)
    for side, sx in (("left", 1), ("right", -1)):
        ax = 7.5 * sx
        m.bone(f"arm_{side}", "chest", [ax, H - 5, -18], rotation=[35, 0, -12 * sx], cubes=[
            Cube([ax - 2, H - 13, -20], [4, 9, 4], hide(studs=False, scars=False, belly=0))])
        m.bone(f"forearm_{side}", f"arm_{side}", [ax, H - 12.5, -18], rotation=[-80, 0, 0], cubes=[
            Cube([ax - 1.5, H - 19, -19.5], [3, 7, 3], hide(studs=False, scars=False))] +
            [Cube([ax + ox - 0.5, H - 21, -19.5], [1, 3, 1], {"fn": claw_fn, "base": "claw"}, rotation=[-25, 0, 0],
                  pivot=[ax, H - 19, -19]) for ox in (-1, 1)])
    # ------------------------------------------------------------------ neck (short bull neck plunging forward-down)
    nw = 16 if mega else 14
    m.bone("neck", "chest", [0, H + 3, -20], rotation=[20 if mega else 34, 0, 0], cubes=[
        Cube([-nw / 2, H - 9, -31], [nw, 18, 12], hide(belly=5, rage_y=H + 4 if mega else None, veins=vy, mega=mega)),
        Cube([-(nw - 3) / 2, H + 9, -29], [nw - 3, 2, 9], hide(rage_y=H + 4 if mega else None, veins=vy, mega=mega)),
    ])
    spines("neck", [-28, -24.5, -21], H + 10.5)
    # ------------------------------------------------------------------ head
    rg = None                    # no blood-black on the head: the burning eyes and the cracks stand out
    m.bone("head", "neck", [0, H + 1, -30], rotation=[-36 if not mega else -22, 0, 0], cubes=[
        Cube([-6.5, H - 3, -41], [13, 10, 12], hide(rage_y=rg, veins=vy and H - 8, mega=mega, studs=False,
                                                   plates=(2, 2))),                       # cranium
        Cube([-6, H - 3, -53], [12, 6, 12], hide(back=True, studs=False, rage_y=rg, plates=(2, 2),
                                                  post=mouth_fn("upper"),
                                                  post_glow=mouth_fn("upper", True) if mega else None)),  # upper jaw
        Cube([-5, H + 3, -52], [10, 2, 10], hide(back=True, studs=False, rage_y=rg)),     # snout ridge
        Cube([-7, H + 5, -34], [14, 3, 5], hide(rage_y=rg, veins=vy and H - 8, studs=False)),   # occipital ridge
    ] + [Cube([6.5 * sx - (0 if sx > 0 else 2), H - 4, -36], [2, 6, 6], hide(studs=False, back=False, rage_y=rg))
         for sx in (1, -1)])                                                                  # jaw muscles
    # soft tissue of the gape: hidden in the closed jaw, revealed when the mouth opens
    m.bone("throat", "head", [0, H - 3, -40], cubes=[
        Cube([-5, H - 8, -47], [10, 5, 13], {"fn": throat_fn(), "base": "palate",
                                              **({"glow_fn": lambda px, faces, pal, rnd, c: throat_fn(True)(px, faces, pal, rnd)}
                                                 if mega else {})})])
    # golden spike-teeth of the upper jaw: a spiky "nose" cluster and a ragged row hanging out along both sides
    up = []
    for x in (-3.5, 0, 3.5):
        up += spike([x, H + 4.5, -50.5], (x * 0.12, 1, -0.7), L=3 if x else 4, w=2)
    for x in (-4.5, -1.5, 1.5, 4.5):
        up += spike([x, H + 1, -53], (x * 0.1, 0.25, -1), L=2, w=2 if abs(x) < 2 else 1)
        up += spike([x, H - 2, -53], (x * 0.12, -0.35, -1), L=2)
    for sx in (1, -1):
        for k, z in enumerate((-51.5, -49, -46.5, -44, -41.5)):
            up += spike([6 * sx, H - 2.5, z], (0.8 * sx, -0.7, -0.15), L=3 if k < 3 else 2, w=2 if k % 2 == 0 else 1)
    m.bone("teeth_upper", "head", [0, H - 3, -48], cubes=up)
    # heavy brows over small eyes, studded with little spikes
    for side, sx in (("left", 1), ("right", -1)):
        bx = 6.5 * sx
        m.bone(f"brow_{side}", "head", [bx, H + 5, -36], rotation=[10, 0, -10 * sx], cubes=[
            Cube([bx - 1.25, H + 4, -43], [2, 2, 8], hide(studs=False, back=True, rage_y=rg))] +
            spike([bx + 0.5 * sx, H + 6, -40], (0.4 * sx, 1, 0.4), L=2) + spike([bx + 0.5 * sx, H + 6, -37], (0.4 * sx, 1, 0.5), L=2))
    # eyes: small, set high on the skull behind the snout, just under the brow
    m.bone("eyes", "head", [0, H + 2.5, -39])
    for side, sx in (("left", 1), ("right", -1)):
        ex = 6.55 * sx
        cubes = [Cube([ex, H + 0.5, -42], [0, 3, 5], eye_fn(mega))]
        if mega:
            cubes.append(Cube([ex + 0.05 * sx, H + 1, -38], [0, 2, 12], {"fn": trail_fn, **GLOW}))
        m.bone(f"eye_{side}", "eyes", [ex, H + 2, -39.5], cubes=cubes)
    # crest of spikes at the back of the skull
    fr = []
    for x, L in ((-5, 3), (-2.5, 4), (0, 4), (2.5, 4), (5, 3)):
        fr += spike([x, H + 7.5, -32.5], (x * 0.12, 1, 0.6), L=L + (1 if mega else 0), w=2 if abs(x) < 3 else 1,
                    paints=(SPINE, SPINE) if abs(x) < 3 else (SPINE,))
    m.bone("frill", "head", [0, H + 7, -32], cubes=fr)
    # inner glow of dragon energy (stretched into a beam by the special attack)
    m.bone("breath", "head", [0, H - 3.5, -44], cubes=[
        Cube([-2.5, H - 6, -45], [5, 5, 1], {"fn": breath_fn, **GLOW})])
    # ------------------------------------------------------------------ lower jaw: a colossal spiked mace
    jw = 15 if mega else 14
    jx = jw / 2
    m.bone("jaw", "head", [0, H - 3, -33], cubes=[
        Cube([-7, H - 9, -48], [14, 6, 16], hide(belly=2, studs=False, back=False, plates=(2, 2), post=mouth_fn("jaw"),
                                                 post_glow=mouth_fn("jaw", True) if mega else None)),   # rear
        Cube([-jx, H - 12, -57], [jw, 9, 9], hide(belly=0, studs=False, back=False, scars=False, plates=(2, 2),
                                                     post=mouth_fn("jaw"),
                                                     post_glow=mouth_fn("jaw", True) if mega else None)),  # chin bulb
        Cube([-6, H - 11, -48], [12, 2, 13], hide(belly=2, studs=False, back=False)),                     # throat
    ])
    lo = []
    for k, x in enumerate((-5.5, -2.75, 0, 2.75, 5.5)):              # front of the mace
        for j, y in enumerate((H - 5, H - 8, H - 10.5)):
            lo += spike([x, y, -57], (x * 0.12, 0.25 - 0.3 * j, -1), L=2, w=2 if (k + j) % 2 == 0 else 1)
    for sx in (1, -1):                                             # sides of the mace
        for z in (-55.5, -52.5, -49.5):
            for j, y in enumerate((H - 5, H - 8, H - 10.5)):
                lo += spike([jx * sx, y, z], (sx, 0.2 - 0.3 * j, -0.35), L=2, w=2 if (j + int(z)) % 2 == 0 else 1)
    for x in (-4, -1.3, 1.3, 4):                                   # underside
        for z in (-55, -51.5):
            lo += spike([x, H - 12, z], (x * 0.1, -1, -0.5), L=2, w=1)
    for x in (-5.5, -3.25, -1, 1.25, 3.5, 5.75):                   # rim of teeth around the mouth: they rise
        lo += spike([x - 0.25, H - 3.5, -56.5], (x * 0.05, 1, -0.45), L=3, w=2 if x in (-3.25, 1.25) else 1)
    for sx in (1, -1):
        for k, z in enumerate((-55.5, -53, -50.5, -48, -45.5, -43, -40.5)):
            xx = (jx if z < -48 else 7) * sx
            lo += spike([xx - 0.5 * sx, H - 3.5, z], (0.55 * sx, 1, -0.1), L=3 if k < 5 else 2,
                        w=2 if k % 2 == 0 else 1)
    m.bone("teeth_lower", "jaw", [0, H - 3, -46], cubes=lo)
    # drool: strings of saliva (Carnage: glowing dragon energy) hanging from the corners of the mace
    for side, sx in (("left", 1), ("right", -1)):
        m.bone(f"drool_{side}", "jaw", [6 * sx, H - 10, -52], cubes=[
            Cube([(jx + 0.6) * sx, H - 19, -55], [0, 9, 5], {"fn": drool_fn, **GLOW} if mega else
                 {"fn": saliva_fn, "shading": False})])
    # ------------------------------------------------------------------ tail: thick, raised, curling up, armoured with
    # dark dorsal spikes growing toward the tip, golden spikes along the flanks, a serrated underside and a spiked fan
    segs = [(15, 15, 12, 3), (12, 12, 12, 6), (10, 10, 11, 6), (8, 8, 10, 6), (6, 6, 9, 5)]
    if mega:
        segs = [(16, 16, 12, 2), (13, 13, 12, -2), (11, 10, 11, -2), (8, 8, 10, 2), (6, 6, 9, 6)]
    parent, z, top = "torso", 15, H + 9
    for i, (w, hgt, ln, rot) in enumerate(segs):
        name = TAIL[i]
        y0 = top - hgt
        m.bone(name, parent, [0, top - hgt / 2, z], rotation=[rot, 0, 0], cubes=[
            Cube([-w / 2, y0, z], [w, hgt, ln], hide(belly=max(2, hgt // 4), veins=vy and (top - 3), mega=mega,
                                                    rage_y=(top - 1.5) if mega else None, studs=False,
                                                    plates=(3, 2)))])
        cubes = m.get(name).cubes
        for k in range(ln // 3):                    # dark dorsal spikes, longer toward the tip
            zz = z + 1.5 + 3 * k
            cubes += spike([0, top - 0.5, zz], (0, 1, 0.75), L=2 + i // 2 + (1 if mega else 0), w=2 if i < 4 else 1,
                           paints=(SPINE, SPINE) if i < 4 else (SPINE,))
        for k in range(ln // 3):                    # golden spikes along both upper flanks
            zz = z + 2.5 + 3 * k
            for sx in (1, -1):
                cubes += spike([(w / 2 - 0.5) * sx, top - 1.5, zz], (sx, 0.55, 0.6), L=3 if i < 3 else 2,
                               w=2 if (i < 2 and k % 2 == 0) else 1)
        if i >= 1:                                  # serrated underside
            for k in range(ln // 3):
                zz = z + 1.5 + 3 * k
                cubes += spike([0, y0 + 0.5, zz], (0, -1, 0.8), L=2 + (1 if i >= 3 else 0), paints=(SPINE,))
        parent, z, top = name, z + ln, top - (hgt - segs[min(i + 1, len(segs) - 1)][1]) / 2
    # tail tip: a fan of great spikes
    tip = []
    yc = top - 3
    for d, L in (((0, 1, 0.5), 5), ((0, 0.25, 1), 6), ((0.8, 0.5, 0.8), 4), ((-0.8, 0.5, 0.8), 4), ((0, -0.6, 1), 4),
                 ((0.5, 1, 0.3), 4), ((-0.5, 1, 0.3), 4)):
        tip += spike([d[0] * 1.5, yc + d[1] * 1.5, z - 0.5], d, L=L + (1 if mega else 0), w=2,
                     paints=(SPINE, SPINE))
    m.bone("tail_tip", "tail5", [0, yc, z], rotation=[6, 0, 0], cubes=[
        Cube([-2.5, yc - 2.5, z - 2], [5, 5, 4], hide(studs=False, plates=(3, 2)))] + tip)
    # ------------------------------------------------------------------ mega: draconic aura (miasma + lightning)
    if mega:
        aura = [("aura_head", "head", [0, H + 6, -38], [0, 16, 22], [0, 0, 0]),
                ("aura_neck", "neck", [0, H + 9, -26], [0, 18, 26], [0, 0, 0]),
                ("aura_chest", "chest", [0, H + 13, -14], [0, 18, 28], [0, 0, 0]),
                ("aura_back", "torso", [0, H + 11, 2], [0, 14, 24], [0, 0, 0])]
        for k, (name, par, pv, size, rot) in enumerate(aura):
            x0, y0, z0 = pv
            w, h, d = size
            m.bone(name, par, pv, rotation=rot, cubes=[                      # three crossed planes: volume from every side
                Cube([x0, y0 - 4, z0 - d / 2], [0, h, d], smoke_fn(40 + 3 * k)),
                Cube([x0 - d * 0.4, y0 - 4, z0], [int(d * 0.8), h, 0], smoke_fn(41 + 3 * k)),
                Cube([x0 - d * 0.35, y0 - 5, z0 - d * 0.35], [int(d * 0.7), h - 2, 0], smoke_fn(42 + 3 * k),
                     rotation=[0, 45, 0], pivot=[x0, y0, z0])])
        m.bone("aura_mouth", "jaw", [0, H - 4, -53], cubes=[             # dragon miasma pouring from the jaws
            Cube([0, H - 6, -59], [0, 14, 12], smoke_fn(60)),
            Cube([-5, H - 6, -53], [10, 14, 0], smoke_fn(61))])
        for k, (par, pv) in enumerate((("head", (5, H + 7, -40)), ("head", (-5, H + 6, -46)), ("neck", (8, H + 8, -24)),
                                       ("neck", (-8, H + 9, -27)), ("chest", (9, H + 12, -14)), ("chest", (-9, H + 13, -10)),
                                       ("chest", (3, H + 16, -18)), ("torso", (8, H + 11, 2)), ("torso", (-8, H + 12, 6)),
                                       ("torso", (-2, H + 14, 0)), ("jaw", (7, H - 4, -55)), ("jaw", (-7, H - 4, -50)))):
            x0, y0, z0 = pv
            m.bone(f"ember_{k}", par, list(pv), cubes=[Cube([x0 - 0.5, y0 - 0.5, z0 - 0.5], [1, 1, 1],
                                                           {"base": "ember_hot" if k % 3 == 0 else "ember", **GLOW})])
        bolts = [("bolt_crown_l", "head", [3, H + 8, -38], 30, 9, (0.6, 1, 0.2), "xy"),
                 ("bolt_crown_r", "head", [-3, H + 8, -36], 28, 9, (-0.5, 1, 0.35), "yz"),
                 ("bolt_head_up", "head", [1, H + 6, -42], 30, 9, (0.35, 1, -0.45), "yz"),
                 ("bolt_head_side", "head", [-6, H + 3, -44], 24, 8, (-1, 0.55, -0.4), "xy"),
                 ("bolt_jaw", "jaw", [6, H - 9, -52], 20, 7, (1, -0.25, -0.5), "xy"),
                 ("bolt_neck_l", "neck", [7, H + 6, -26], 32, 9, (1, 0.9, 0.2), "xy"),
                 ("bolt_neck_r", "neck", [-7, H + 5, -27], 28, 9, (-1, 0.8, -0.1), "yz"),
                 ("bolt_back_l", "chest", [8, H + 12, -12], 34, 10, (0.8, 1, 0.5), "yz"),
                 ("bolt_back_r", "torso", [-8, H + 10, 4], 30, 9, (-0.7, 1, 0.6), "xy"),
                 ("bolt_tail", "tail", [5, H + 6, 22], 22, 8, (0.9, 0.7, 0.6), "yz")]
        for k, (name, par, pv, L, wd, d, plane) in enumerate(bolts):
            x0, y0, z0 = pv
            if plane == "yz":
                cube = Cube([x0, y0, z0 - wd / 2], [0, L, wd], bolt_fn(60 + k))
            else:
                cube = Cube([x0 - wd / 2, y0, z0], [wd, L, 0], bolt_fn(60 + k))
            m.bone(name, par, pv, rotation=_dir_rot(d), cubes=[cube])
    m.pack()
    return m

MEGA_ONLY = ("aura_", "bolt_", "drool_", "ember_")
AURA = ("aura_head", "aura_neck", "aura_chest", "aura_back", "aura_mouth")
BOLTS = ("bolt_crown_l", "bolt_crown_r", "bolt_head_up", "bolt_head_side", "bolt_jaw", "bolt_neck_l", "bolt_neck_r",
         "bolt_back_l", "bolt_back_r", "bolt_tail")
EMBERS = tuple(f"ember_{k}" for k in range(12))

# ---------------------------------------------------------------------------------------------------- animations
def S(deg):
    return math.sin(math.radians(deg))

def bump(t, t0, w):
    """Smooth bump (0..1..0) centred on t0, half-width w."""
    x = (t - t0) / w
    return 0.5 * (1 + math.cos(math.pi * x)) if abs(x) < 1 else 0.0

def ramp(t, pts):
    """Piecewise smoothstep through (time, value) points."""
    if t <= pts[0][0]:
        return pts[0][1]
    for (t0, a), (t1, b) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return a + (b - a) * smooth((t - t0) / (t1 - t0)) if t1 > t0 else b
    return pts[-1][1]

def sampled(L, fns, step=0.1, extra_steps=()):
    """{bone: {channel: fn(t) -> [x, y, z]}} -> catmull-rom keyframes sampled every `step` (+ extra times)."""
    ts = sorted({round(k * step, 3) for k in range(int(round(L / step)) + 1)} | {round(t, 3) for t in extra_steps})
    out = {}
    for bone, chans in fns.items():
        for ch, fn in chans.items():
            out.setdefault(bone, {})[ch] = {str(t): kf([round(v, 2) for v in fn(t)]) for t in ts}
    return out

def embers(L, loop=True):
    """Glowing embers drifting up through the miasma and fading out (each on its own cycle)."""
    out = {}
    for k, name in enumerate(EMBERS):
        P0 = 1.5 + 0.37 * (k % 5)
        P = L / max(1, round(L / P0)) if loop else P0
        ph = (k * 0.618) % 1.0
        rise = 9 + 2 * (k % 4)
        dx = 2.5 if k % 2 else -2.5
        pos, sc = {}, {}
        n = int(round(L / 0.1))
        for i in range(n + 1):
            t = round(i * 0.1, 3)
            u = ((t / P) + ph) % 1.0
            pos[str(t)] = [round(dx * S(u * 360) * 0.6, 2), round(rise * u, 2), round(1.5 * S(u * 540), 2)]
            v = round(min(1.0, u * 6) * (1 - u) * 1.6, 2)
            sc[str(t)] = [v, v, v]
        out[name] = {"position": pos, "scale": sc}
    return out

def bolt_flicker(L, t0, t1, every=0.2, size=1.2, seed=0):
    """Lightning that strikes on and off between t0 and t1 (each bolt on its own rhythm)."""
    out = {}
    for j, name in enumerate(BOLTS):
        fr = {0.0: [0, 0, 0]}
        t = t0 + 0.037 * ((j * 7 + seed) % 5)
        while t < t1:
            fr[round(t, 2)] = [size, size, size]
            fr[round(t + 0.06, 2)] = [0, 0, 0]
            t += every + 0.03 * ((j + seed) % 4)
        fr[L] = [0, 0, 0]
        out[name] = {"scale": {str(tt): v for tt, v in sorted(fr.items())}}
    return out

def aura_flare(L, pts):
    """The miasma swells (scale keys from (time, factor) points)."""
    return {name: keys(scale={t: [1 + (f - 1) * 0.8, f, 1 + (f - 1) * 0.8] for t, f in pts}) for name in AURA}

def sway(freq, mul=1.0, mega=False):
    """Molang loops for the effect bones (used by the walk; the other loops are sampled)."""
    q = "q.anim_time"
    out = {"breath": {"scale": [1, 1, 1]}}
    for side in ("left", "right"):
        out[f"drool_{side}"] = {"scale": [1, f"0.8+math.sin({q}*{freq}+{0 if side == 'left' else 90})*0.2", 1],
                                "rotation": [f"math.sin({q}*{freq}+{30 if side == 'left' else 120})*8", 0, 0]}
    if mega:
        for k, name in enumerate(AURA):             # the miasma swirls, swells and rises
            out[name] = {"rotation": [f"math.sin({q}*{freq * 0.5}+{70 * k})*6", f"{q}*{50 + 15 * k}+{45 * k}", 0],
                         "scale": [f"1+math.sin({q}*{freq * 0.8}+{50 * k})*0.12", f"1+math.sin({q}*{freq}+{40 * k})*0.18",
                                   f"1+math.sin({q}*{freq * 0.8}+{50 * k})*0.12"],
                         "position": [0, f"math.sin({q}*{freq * 0.6}+{30 * k})*0.8", 0]}
        for k, name in enumerate(BOLTS):            # lightning crackles on and off, never all at once
            on = f"math.clamp(math.sin({q}*{430 + 97 * k}+{53 * k})*4-2.0,0,1)"
            out[name] = {"scale": [on, on, on], "rotation": [f"math.sin({q}*{900 + 130 * k})*7", 0, 0]}
    return out

def fx_loop(L, mega, intensity=1.0):
    """Sampled loop of the effect bones (drool, miasma, lightning) for a looping animation of length L."""
    f = 360.0 / L
    fns = {}
    for k, side in enumerate(("left", "right")):
        fns[f"drool_{side}"] = {"scale": lambda t, k=k: [1, 0.8 + 0.2 * S(f * 2 * t + 90 * k), 1],
                                "rotation": lambda t, k=k: [8 * S(f * 2 * t + 30 + 90 * k), 0, 0]}
    if mega:
        for k, name in enumerate(AURA):
            fns[name] = {"rotation": lambda t, k=k: [6 * S(f * t + 70 * k), (f * t * (1 + k % 2) + 45 * k) % 360 - 180 * 0, 0],
                         "scale": lambda t, k=k: [intensity * (1 + 0.12 * S(f * 2 * t + 50 * k)),
                                                  intensity * (1 + 0.2 * S(f * 3 * t + 40 * k)),
                                                  intensity * (1 + 0.12 * S(f * 2 * t + 50 * k))],
                         "position": lambda t, k=k: [0, 0.8 * S(f * 2 * t + 30 * k), 0]}
    out = sampled(L, fns, step=0.1)
    if mega:
        for k, name in enumerate(AURA):              # continuous spin: keep the Y angle unwrapped
            out[name]["rotation"] = {t: kf([v["post"][0], round((float(t) * f * (1 + k % 2) + 45 * k), 2), 0])
                                     for t, v in out[name]["rotation"].items()}
        out.update(embers(L))
        every = 0.32 / intensity
        out.update(bolt_flicker(L, 0.05, L - 0.1, every=every, size=1.15))
    return out

def idle_anim(mega):
    """Predator at rest: heavy breathing, head swinging low from side to side and tilting as it scans for prey,
    a few quick sniffs, the drooling jaw hanging open — then a sudden chomp (head jerks, jaws snap shut, claws
    clench), and the scan resumes. Brows always low."""
    L, k = 8.0, (1.3 if mega else 1.0)
    def jaw(t):
        base = 6 * k + 4 * S(90 * t - 60)
        return ramp(t, [(0, base), (5.0, base), (5.38, 36), (5.5, 0), (5.9, base), (8, base)]) if 4.9 < t < 6.0 else base
    def sniff(t):
        return 2.6 * S(1440 * (t - 2.3)) * bump(t, 2.7, 0.45)
    fns = {
        "torso": {"rotation": lambda t: [1.2 * k * S(90 * t) + 2 * bump(t, 5.45, 0.4), 0, 1.6 * k * S(45 * t + 20)]},
        "chest": {"rotation": lambda t: [-0.8 * k * S(90 * t - 20) + 2 * bump(t, 5.5, 0.5), 0, -0.8 * S(45 * t + 20)],
                  "scale": lambda t: [1, 1 + 0.016 * k * S(90 * t), 1 + 0.012 * k * S(90 * t)]},
        "neck": {"rotation": lambda t: [1.5 * S(90 * t - 40) + 3 * bump(t, 2.7, 0.6) - 5 * bump(t, 5.35, 0.35)
                                        + 3 * bump(t, 5.6, 0.3), 11 * k * S(45 * t) + 3 * S(135 * t + 30), 2 * S(45 * t + 60)]},
        "head": {"rotation": lambda t: [-1 * S(90 * t - 60) + sniff(t) - 7 * bump(t, 5.35, 0.3) + 5 * bump(t, 5.6, 0.3),
                                        5 * S(45 * t + 40), 4 * k * S(45 * t + 80) + (0.7 * S(1800 * t) if mega else 0)]},
        "jaw": {"rotation": lambda t: [jaw(t), 0, 0]},
        "brow_left": {"rotation": lambda t: [3 + 4 * bump(t, 5.45, 0.5), 0, 0]},
        "brow_right": {"rotation": lambda t: [3 + 4 * bump(t, 5.45, 0.5), 0, 0]},
        "eye_left": {"scale": lambda t: [1, 0.9 - 0.35 * bump(t, 5.45, 0.35), 1]},
        "eye_right": {"scale": lambda t: [1, 0.9 - 0.35 * bump(t, 5.45, 0.35), 1]},
        "arm_left": {"rotation": lambda t: [3 * S(90 * t) - 15 * bump(t, 5.45, 0.4), 0, 0]},
        "arm_right": {"rotation": lambda t: [3 * S(90 * t + 40) - 15 * bump(t, 5.45, 0.4), 0, 0]},
        "forearm_left": {"rotation": lambda t: [-25 * bump(t, 5.5, 0.45), 0, 0]},
        "forearm_right": {"rotation": lambda t: [-25 * bump(t, 5.5, 0.45), 0, 0]},
        "tail_tip": {"rotation": lambda t: [0, 10 * S(45 * t - 220), 0]},
        "breath": {"scale": lambda t: [1 + 0.1 * S(90 * t), 1 + 0.1 * S(90 * t), 1]},
    }
    for i, tb in enumerate(TAIL):
        fns[tb] = {"rotation": lambda t, i=i: [1.5 * S(90 * t - 40 * i) - 3 * bump(t, 5.5 + 0.08 * i, 0.4),
                                               (6 + 2.5 * i) * S(45 * t - 35 * i), 0]}
    b = sampled(L, fns, step=0.1, extra_steps=[5.3, 5.35, 5.4, 5.45, 5.5, 5.55])
    b.update(fx_loop(L, mega))
    return {"loop": True, "animation_length": L, "bones": b}

def battle_anim(mega):
    """Battle stance: crouched low, weight rolling from side to side, chest heaving with a growl (jaw trembling wide
    open), head low and thrust at the foe, swinging and tilting; twice per loop it snaps its jaws at the air, and once
    it shakes its head violently; the tail lashes; claws clench; brows down, eyes narrowed to slits."""
    L, k = 4.0, (1.3 if mega else 1.0)
    legs = make_legs(mega)
    crouch = -4.0
    def jaw(t):
        base = 24 * k + 1.6 * S(2000 * t)
        for t0 in (1.0, 3.0):
            if t0 - 0.35 < t < t0 + 0.4:
                return ramp(t, [(t0 - 0.35, base), (t0 - 0.1, 40 * k), (t0, 2), (t0 + 0.4, base)])
        return base
    def thrash(t):
        return 15 * k * S(1080 * (t - 2.0)) * bump(t, 2.3, 0.3)
    fns = {
        "torso": {"rotation": lambda t: [6 + 2 * k * S(180 * t), 0, 4 * k * S(90 * t)]},
        "chest": {"rotation": lambda t: [2 + 1.5 * S(180 * t + 40), 0, -2 * S(90 * t)],
                  "scale": lambda t: [1, 1 + 0.025 * k * S(180 * t), 1 + 0.02 * S(180 * t)]},
        "neck": {"rotation": lambda t: [(1 if not mega else 5) + 3 * S(180 * t - 30) - 7 * bump(t, 1.0, 0.3) - 7 * bump(t, 3.0, 0.3),
                                        12 * k * S(90 * t + 20), 3 * S(90 * t)]},
        "head": {"rotation": lambda t: [-16 + 2 * S(180 * t - 60) + 6 * bump(t, 1.0, 0.18) + 6 * bump(t, 3.0, 0.18),
                                        6 * S(90 * t + 60), 5 * S(90 * t + 90) + thrash(t) + (1.2 * S(2300 * t) if mega else 0)]},
        "jaw": {"rotation": lambda t: [jaw(t), 0, 0]},
        "brow_left": {"rotation": lambda t: [8, 0, 0]}, "brow_right": {"rotation": lambda t: [8, 0, 0]},
        "eye_left": {"scale": lambda t: [1.05, 0.72, 1]}, "eye_right": {"scale": lambda t: [1.05, 0.72, 1]},
        "arm_left": {"rotation": lambda t: [-22 + 6 * S(180 * t), 0, -10]},
        "arm_right": {"rotation": lambda t: [-22 + 6 * S(180 * t + 60), 0, 10]},
        "forearm_left": {"rotation": lambda t: [-20 + 14 * S(360 * t), 0, 0]},
        "forearm_right": {"rotation": lambda t: [-20 + 14 * S(360 * t + 90), 0, 0]},
        "tail_tip": {"rotation": lambda t: [0, 22 * k * S(180 * t - 260), 0]},
        "breath": {"scale": lambda t: [1.15 + 0.2 * S(360 * t), 1.15 + 0.2 * S(360 * t), 1]},
    }
    for i, tb in enumerate(TAIL):
        fns[tb] = {"rotation": lambda t, i=i: [6 + 3 * S(180 * t - 40 * i), (12 + 5 * i) * k * S(180 * t - 50 * i), 0]}
    b = sampled(L, fns, step=0.05)
    for bn, r in leg_pose(legs, crouch).items():
        b[bn] = {"rotation": r}
    b["body"] = {"position": [0, crouch, 0]}
    b.update(fx_loop(L, mega, intensity=1.15))
    return {"loop": True, "animation_length": L, "bones": b}

def cry(mega=False):
    """Roar: drops its head and draws breath (chest swelling), rears up tall, throws the head back and to the side with
    the jaws gaping and roars, thrashing the head left and right with the whole body shaking, claws spread, tail
    lashing; the miasma erupts and lightning rains around it (Carnage); slams back down."""
    L = 3.2 if mega else 3.0
    k = 1.3 if mega else 1.0
    b = timeline(LEGS, L, [(0, 0, 0), (0.5, -3.0, 0), (0.9, 1.6, 0), (2.3, 1.2, 0), (2.7, -1.6, 0), (L, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.5: [8, 0, 0], 0.9: [-16, 0, 0], 1.2: [-15, 0, 4], 1.6: [-15, 0, -4],
                                2.0: [-14, 0, 3], 2.3: [-13, 0, 0], 2.7: [4, 0, 0], L: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.5: [6, 0, 0], 0.9: [-12, 0, 0], 2.3: [-10, 0, 0], 2.7: [2, 0, 0], L: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.5: [1.04, 1.06, 1.03], 0.9: [1, 1, 1], L: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.5: [4, 0, 0], 0.9: [-20, 12, 0], 1.2: [-19, -16 * k, 0], 1.5: [-19, 16 * k, 0],
                               1.8: [-18, -14 * k, 0], 2.1: [-17, 10, 0], 2.4: [-10, 0, 0], 2.8: [3, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.5: [-2, 0, 0], 0.9: [-16, 0, 16], 0.95: [tremble(-16, 2200, 3 * k), 0, 14],
                               1.2: [tremble(-15, 2200, 3 * k), 0, -16], 1.5: [tremble(-15, 2200, 3 * k), 0, 16],
                               1.8: [tremble(-14, 2200, 3 * k), 0, -14], 2.2: [tremble(-12, 2200, 3 * k), 0, -4],
                               2.6: [2, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.5: [0, 0, 0], 0.85: [46, 0, 0], 0.95: [tremble(48, 1900, 3.5), 0, 0],
                              2.2: [tremble(46, 1900, 3.5), 0, 0], 2.55: [4, 0, 0], L: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.5: [10, 0, 0], 0.9: [-40, 0, -22 * sx], 2.3: [-36, 0, -20 * sx], L: [0, 0, 0]})
        b[f"forearm_{side}"] = keys(rotation={0: [0, 0, 0], 0.9: [-30, 0, 0], 1.2: [-10, 0, 0], 1.5: [-30, 0, 0],
                                              1.8: [-10, 0, 0], 2.3: [-25, 0, 0], L: [0, 0, 0]})
        b[f"brow_{side}"] = keys(rotation={0: [0, 0, 0], 0.85: [10, 0, 0], 2.3: [10, 0, 0], 2.6: [0, 0, 0], L: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.5: [-4, 0, 0], 0.9: [10, 0, 0], 1.2: [10, 18, 0], 1.5: [10, -18, 0], 1.8: [9, 14, 0],
                               2.1: [9, -10, 0], 2.5: [0, 0, 0], L: [0, 0, 0]})
    for i, tb in enumerate(TAIL[1:], 1):
        a = 16 + 4 * i
        b[tb] = keys(rotation={0: [0, 0, 0], 0.9 + 0.08 * i: [0, 0, 0], 1.2 + 0.08 * i: [0, a, 0], 1.5 + 0.08 * i: [0, -a, 0],
                               1.8 + 0.08 * i: [0, a * 0.7, 0], 2.1 + 0.08 * i: [0, -a * 0.4, 0], 2.6 + 0.08 * i: [0, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.8: [1, 1, 1], 0.9: [1.15, 0.5, 1], 2.3: [1.15, 0.5, 1], 2.5: [1, 1, 1], L: [1, 1, 1]})
    b["breath"] = keys(scale={0: [1, 1, 1], 0.85: [1, 1, 1], 1.0: [1.5, 1.5, 1], 2.2: [1.4, 1.4, 1], 2.5: [1, 1, 1], L: [1, 1, 1]})
    if mega:
        b.update(aura_flare(L, [(0, 1), (0.5, 0.9), (1.0, 1.7), (2.3, 1.55), (2.8, 1.0), (L, 1)]))
        b.update(bolt_flicker(L, 0.9, 2.4, every=0.15, size=1.4))
        b.update(embers(L, loop=False))
    return {"animation_length": L, "bones": b}

def ik_track(legs, length, ks, step=0.05):
    """Legs (feet planted) + body for keys (t, hip_dy, body_dz): the body may move forward/back over planted feet."""
    bones = {}
    n = int(round(length / step))
    for k in range(n + 1):
        t = round(k * step, 3)
        for (t0, h0, z0), (t1, h1, z1) in zip(ks, ks[1:]):
            if t0 <= t <= t1:
                e = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1
                h, z = h0 + (h1 - h0) * e, z0 + (z1 - z0) * e
                break
        else:
            h, z = ks[-1][1], ks[-1][2]
        for b, val in leg_pose(legs, h, -z).items():
            bones.setdefault(b, {"rotation": {}})["rotation"][str(t)] = kf(val)
        bones.setdefault("body", {"position": {}})["position"][str(t)] = kf([0, round(h, 3), round(z, 3)])
    return bones

def physical(mega=False):
    """Savage bite: rears back with the jaws gaping, lunges low and snaps, re-opens and bites a second time, then
    clamps down and thrashes its head from side to side like a dog shaking its prey (body and tail following),
    tears free and recovers, still snarling."""
    L = 1.9
    k = 1.25 if mega else 1.0
    b = ik_track(LEGS, L, [(0, 0, 0), (0.3, 0.6, 3.0), (0.48, -3.0, -7), (0.75, -2.8, -6.5), (1.25, -2.2, -5),
                           (1.55, -0.6, -1), (L, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.3: [-10, 0, 0], 0.48: [12, 0, 0], 0.8: [10, 0, 5 * k], 0.95: [10, 0, -5 * k],
                                1.1: [10, 0, 5 * k], 1.25: [9, 0, 0], L: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.3: [-26, 0, 0], 0.45: [-12, 0, 0], 0.5: [-4, 0, 0], 0.6: [-8, 0, 0],
                               0.72: [-2, 0, 0], 0.8: [-2, 12 * k, 0], 0.9: [-2, -12 * k, 0], 1.0: [-2, 12 * k, 0],
                               1.1: [-2, -12 * k, 0], 1.2: [-2, 6, 0], 1.45: [-8, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.3: [-26, 0, 0], 0.45: [-24, 0, 0], 0.5: [-6, 0, 0], 0.6: [-16, 0, 0],
                               0.72: [-4, 0, 0], 0.8: [-4, 0, 22 * k], 0.9: [-4, 0, -22 * k], 1.0: [-4, 0, 22 * k],
                               1.1: [-4, 0, -22 * k], 1.2: [-4, 0, 10], 1.45: [-10, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.3: [42, 0, 0], 0.45: [46, 0, 0], 0.5: [0, 0, 0], 0.6: [30, 0, 0], 0.72: [0, 0, 0],
                              1.25: [0, 0, 0], 1.45: [20, 0, 0], 1.55: [tremble(18, 1900, 3), 0, 0], 1.75: [6, 0, 0], L: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.3: [14, 0, 0], 0.48: [-10, 0, 0], 0.8: [-6, 14, 0], 1.0: [-6, -14, 0],
                               1.2: [-4, 10, 0], L: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.55: [-6, 0, 0], 0.85: [0, 18, 0], 1.05: [0, -18, 0], 1.25: [0, 12, 0], L: [0, 0, 0]})
    b["tail3"] = keys(rotation={0: [0, 0, 0], 0.6: [0, 0, 0], 0.9: [0, 20, 0], 1.1: [0, -20, 0], 1.3: [0, 14, 0], L: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.3: [-30, 0, -10 * sx], 0.5: [-55, 0, -5 * sx], 1.2: [-45, 0, 0], L: [0, 0, 0]})
        b[f"forearm_{side}"] = keys(rotation={0: [0, 0, 0], 0.3: [10, 0, 0], 0.5: [-35, 0, 0], 1.2: [-30, 0, 0], L: [0, 0, 0]})
        b[f"brow_{side}"] = keys(rotation={0: [0, 0, 0], 0.3: [10, 0, 0], 1.5: [10, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.3: [1.1, 0.55, 1], 1.5: [1.1, 0.55, 1], L: [1, 1, 1]})
    if mega:
        b["breath"] = keys(scale={0: [1, 1, 1], 0.3: [1.6, 1.6, 1], 0.5: [1, 1, 1], L: [1, 1, 1]})
        b.update(aura_flare(L, [(0, 1), (0.3, 1.2), (0.5, 1.6), (1.2, 1.3), (L, 1)]))
        b.update(bolt_flicker(L, 0.45, 1.3, every=0.14, size=1.3))
        b.update(embers(L, loop=False))
    return {"animation_length": L, "bones": b}

def special(mega=False):
    """Dragon breath: rears up and draws in, trembling as dragon energy boils in its jaws (the glow pulses, the chest
    swells), then thrusts the head forward and spews a beam of dragon energy that sweeps side to side, the body
    braced and shaking; the beam dies down and it recovers with a snarl."""
    L = 2.6
    reach = 46 if mega else 38
    b = timeline(LEGS, L, [(0, 0, 0), (0.7, 1.2, 0), (0.95, -1.0, 0), (2.1, -0.8, 0), (L, 0, 0)], step=0.05)
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.7: [-12, 0, 0], 0.72: [-12, 0, "math.sin(q.anim_time*2600)*1.5"],
                                0.95: [6, 0, 0], 2.1: [5, 0, "math.sin(q.anim_time*2400)*1"], L: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.7: [-8, 0, 0], 0.95: [4, 0, 0], 2.1: [4, 0, 0], L: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.7: [1.06, 1.08, 1.04], 0.95: [1, 1, 1], L: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.7: [-26, 0, 0], 0.95: [-6, 0, 0], 1.3: [-6, 12, 0], 1.7: [-6, -12, 0],
                               2.1: [-6, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.7: [-22, 0, 0], 0.95: [tremble(-5, 2400, 1.8), 0, 0],
                               2.1: [tremble(-5, 2400, 1.8), 0, 0], 2.35: [-4, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.45: [12, 0, 0], 0.7: [22, 0, 0], 0.95: [30, 0, 0], 2.1: [28, 0, 0],
                              2.3: [tremble(14, 1900, 3), 0, 0], 2.5: [4, 0, 0], L: [0, 0, 0]})
    b["breath"] = keys(scale={0: [1, 1, 1], 0.3: [1.4, 1.4, 1], 0.45: [1.1, 1.1, 1], 0.6: [1.6, 1.6, 1], 0.75: [1.3, 1.3, 1],
                              0.9: [1.8, 1.8, 2], 1.05: [1.9, 1.9, reach], 1.95: [1.7, 1.7, reach],
                              2.15: [0.6, 0.6, reach * 0.6], 2.25: [0.4, 0.4, 1], L: [1, 1, 1]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.7: [-30, 0, -14 * sx], 2.1: [-28, 0, -12 * sx], L: [0, 0, 0]})
        b[f"brow_{side}"] = keys(rotation={0: [0, 0, 0], 0.7: [10, 0, 0], 2.1: [10, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.7: [1.1, 0.5, 1], 2.1: [1.1, 0.5, 1], L: [1, 1, 1]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.7: [8, 0, 0], 0.95: [-6, 0, 0], 1.3: [-5, 10, 0], 1.7: [-5, -10, 0], L: [0, 0, 0]})
    if mega:
        b.update(aura_flare(L, [(0, 1), (0.7, 1.5), (0.95, 1.8), (2.0, 1.6), (2.4, 1), (L, 1)]))
        b.update(bolt_flicker(L, 0.4, 2.1, every=0.13, size=1.3))
        b.update(embers(L, loop=False))
    return {"animation_length": L, "bones": b}

def recoil(mega=False):
    """Hit: the head is knocked back and aside, the body jolts back over its feet — and it immediately lunges back
    with a snarl, jaws trembling, brows crushed down."""
    L = 0.95
    b = ik_track(LEGS, L, [(0, 0, 0), (0.12, 0.4, 2.0), (0.38, -0.8, -0.8), (L, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.12: [-8, 0, 6], 0.38: [5, 0, -2], L: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.12: [-16, 12, 0], 0.38: [0, -4, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.12: [-14, 0, 14], 0.38: [-6, 0, -4], 0.45: [tremble(-6, 2200, 2.5), 0, 0],
                               0.7: [tremble(-6, 2200, 2.5), 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.12: [22, 0, 0], 0.38: [34, 0, 0], 0.45: [tremble(32, 1900, 3), 0, 0],
                              0.7: [tremble(26, 1900, 3), 0, 0], 0.85: [6, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.1: [1, 0.25, 1], 0.3: [1.1, 0.6, 1], 0.8: [1.1, 0.6, 1], L: [1, 1, 1]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"brow_{side}"] = keys(rotation={0: [0, 0, 0], 0.3: [14, 0, 0], 0.8: [12, 0, 0], L: [0, 0, 0]})
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.12: [-20, 0, -10 * sx], 0.4: [-35, 0, 0], L: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.12: [6, -14, 0], 0.4: [0, 10, 0], L: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.2: [0, -14, 0], 0.5: [0, 12, 0], L: [0, 0, 0]})
    if mega:
        b.update(aura_flare(L, [(0, 1), (0.15, 1.4), (0.4, 1.2), (L, 1)]))
        b.update(bolt_flicker(L, 0.1, 0.6, every=0.12, size=1.3))
        b.update(embers(L, loop=False))
    return {"animation_length": L, "bones": b}

def status(mega=False):
    """Intimidation display (status moves): rears up tall, spreads its little claws, and growls with the jaws wide
    open while shaking its head, then stamps back down."""
    L = 1.9
    b = timeline(LEGS, L, [(0, 0, 0), (0.4, 1.4, 0), (1.4, 1.2, 0), (1.65, -1.4, 0), (L, 0, 0)], step=0.05)
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.4: [-13, 0, 0], 1.4: [-11, 0, 0], 1.65: [4, 0, 0], L: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.4: [-6, 0, 0], 1.4: [-5, 0, 0], L: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.4: [1.05, 1.07, 1.04], 1.4: [1.04, 1.06, 1.03], L: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.4: [-16, 0, 0], 0.6: [-16, 12, 0], 0.8: [-16, -12, 0], 1.0: [-16, 10, 0],
                               1.2: [-14, -6, 0], 1.5: [2, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.4: [-8, 0, 0], 0.6: [-8, 0, 14], 0.8: [-8, 0, -14], 1.0: [-8, 0, 12],
                               1.2: [-6, 0, -6], 1.5: [2, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.35: [36, 0, 0], 0.45: [tremble(38, 1900, 3), 0, 0],
                              1.3: [tremble(36, 1900, 3), 0, 0], 1.55: [4, 0, 0], L: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.4: [-45, 0, -25 * sx], 1.4: [-42, 0, -22 * sx], L: [0, 0, 0]})
        b[f"forearm_{side}"] = keys(rotation={0: [0, 0, 0], 0.4: [-20, 0, 0], 0.7: [-35, 0, 0], 1.0: [-15, 0, 0],
                                              1.3: [-30, 0, 0], L: [0, 0, 0]})
        b[f"brow_{side}"] = keys(rotation={0: [0, 0, 0], 0.4: [10, 0, 0], 1.4: [10, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.4: [1.1, 0.6, 1], 1.4: [1.1, 0.6, 1], L: [1, 1, 1]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.4: [8, 14, 0], 0.7: [8, -14, 0], 1.0: [8, 12, 0], 1.3: [6, -8, 0], L: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.5: [0, 16, 0], 0.8: [0, -16, 0], 1.1: [0, 12, 0], 1.4: [0, -6, 0], L: [0, 0, 0]})
    if mega:
        b.update(aura_flare(L, [(0, 1), (0.4, 1.6), (1.4, 1.5), (1.7, 1), (L, 1)]))
        b.update(bolt_flicker(L, 0.4, 1.4, every=0.16, size=1.3))
        b.update(embers(L, loop=False))
    return {"animation_length": L, "bones": b}

TRUNK = ({"torso", "chest"} | {b for lg in LEGS for b in lg.bones[:2]}
         | {"arm_left", "arm_right", "forearm_left", "forearm_right"})

def _skip(m):
    return tuple(b.name for b in m.bones if b.name.startswith(MEGA_ONLY + ("breath", "eye_")))

def sleep_pose(m, mega=False):
    """Belly on the ground, legs folded under, neck laid forward and turned aside, the huge jaw resting flat on the
    ground, tail curled forward around the body."""
    skip = _skip(m)
    base = {"torso": {"rotation": [6, 0, 0]}, "chest": {"rotation": [6, 0, 0]},
            "arm_left": {"rotation": [45, 0, -8]}, "arm_right": {"rotation": [45, 0, 8]},
            "forearm_left": {"rotation": [40, 0, 0]}, "forearm_right": {"rotation": [40, 0, 0]}}
    pose = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()}
    legs = make_legs(mega)
    lie_legs(m, legs, pose, TRUNK, hip_range=(8.0, 20.0))
    pose.update({k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()})
    head = descendants(m, "head") - set(skip)
    pose["head"] = {"rotation": [10, 12, 4]}
    search(m, pose, "neck", [[nx, 22, 0] for nx in range(-40, 32, 2)], 0.5, head, keep={"neck"}, skip=skip)
    search(m, pose, "head", [[hx, 12, 4] for hx in range(-20, 40, 2)], 0.3, head, keep={"neck"}, skip=skip)
    for tb, yaw, lim in zip(TAIL, (-18, -26, -30, -30, -26), (-30, -18, -14, -10, -8)):
        search(m, pose, tb, [[x, yaw, 0] for x in range(lim, 6, 2)], 0.3, descendants(m, tb) - set(skip), skip=skip)
    return pose

def sleep_anim(m, mega=False):
    q = "q.anim_time"
    b = pose_to_bones(sleep_pose(m, mega))
    b["chest"]["position"] = [0, f"0.3+math.sin({q}*45)*0.35", 0]
    b["torso"]["position"] = [0, f"0.15+math.sin({q}*45-30)*0.2", 0]
    b["jaw"] = {"rotation": [f"2+math.sin({q}*45-60)*1.5", 0, 0]}
    b["tail5"]["rotation"][1] = f"{b['tail5']['rotation'][1]}+math.sin({q}*30)*5"
    for e in ("eye_left", "eye_right"):
        b[e] = {"scale": [1, 0.02, 1]}
    b["breath"] = {"scale": [f"0.9+math.sin({q}*45)*0.1", f"0.9+math.sin({q}*45)*0.1", 1]}
    if mega:
        for k, name in enumerate(AURA):           # asleep, the miasma smoulders low
            b[name] = {"scale": [0.7, f"0.45+math.sin({q}*45+{40 * k})*0.06", 0.7], "rotation": [0, f"{q}*20", 0]}
        for name in BOLTS:
            b[name] = {"scale": [0, 0, 0]}
    return {"loop": True, "animation_length": 8, "bones": b}

def ko_anim(m, mega=False):
    """Death: the blow throws it backward — it reels back over its planted feet (head flung up, jaws gaping), staggers
    a second time, drops its tail to the ground to brace and sinks back onto its haunches; then the legs fold, it lies
    down slowly on its belly, the neck stretches out until the jaw rests on the ground and it rolls a little onto its
    side with a last breath; the eyes close."""
    skip = _skip(m)
    legs = make_legs(mega)
    leg_names = {x for lg in legs for x in lg.bones}
    def stand(h, bz):                     # feet planted while the hips drop by h and the body shifts bz backward
        p = {b: {"rotation": r} for b, r in leg_pose(legs, h, -bz).items()}
        p["body"] = {"rotation": [0, 0, 0], "position": [0, h, bz]}
        return p
    folded = {b: v for b, v in sleep_pose(m, mega).items() if b in leg_names}
    def P(*parts):
        out = {}
        for part in parts:
            for k, v in part.items():
                out[k] = {kk: list(vv) for kk, vv in v.items()}
        return out
    R = lambda **kw: {k: {"rotation": v} for k, v in kw.items()}
    arms = lambda x, z=0: {"arm_left": {"rotation": [x, 0, -z]}, "arm_right": {"rotation": [x, 0, z]},
                           "forearm_left": {"rotation": [x * 0.5, 0, 0]}, "forearm_right": {"rotation": [x * 0.5, 0, 0]}}
    trunk = {b.name for b in m.bones if b.name in TRUNK}
    def settle(p):                        # the belly / folded legs rest on the ground (not the head)
        p["body"]["position"][1] = 0
        p["body"]["position"][1] = -lowest(m, p, only=trunk) + 0.05
    tail_grp = descendants(m, "tail") - set(skip)
    head_grp = descendants(m, "head") - set(skip)
    k0 = P(stand(0, 0))
    k1 = P(stand(0.4, 2.5), R(torso=[-12, 0, 0], chest=[-5, 0, 0], neck=[-20, 0, 0], head=[-16, 0, 0], jaw=[32, 0, 0],
                             tail=[-4, 0, 0]), arms(-30, 14))
    k2 = P(stand(-1.0, 5.0), R(torso=[-16, 0, 5], chest=[-6, 0, 2], neck=[-24, 10, 0], head=[-10, 0, -10], jaw=[24, 0, 0],
                              tail=[-8, 6, 0], tail2=[-4, 4, 0]), arms(-22, 18))
    k3 = P(stand(-6.0, 6.0), R(torso=[-11, 0, -3], chest=[-4, 0, 0], neck=[-12, -6, 0], head=[-4, 0, 6], jaw=[16, 0, 0],
                              tail2=[0, -4, 0], tail3=[4, 0, 0]), arms(8))
    for kp, tgt, yaw in ((k1, 3.0, 0), (k2, 1.5, 6)):          # rearing back: the tail swings low but stays clear
        search(m, kp, "tail", [[x, yaw, 0] for x in range(-36, 30, 2)], tgt, tail_grp, skip=skip)
    search(m, k3, "tail", [[x, -4, 0] for x in range(-36, 30, 2)], 0.2, tail_grp, skip=skip)     # tail braces on the ground
    k4 = P(folded, {"body": {"rotation": [0, 0, 0], "position": [0, 0, 6.0]}},
           R(torso=[3, 0, 0], chest=[5, 0, 0], neck=[4, 0, 0], head=[2, 0, 0], jaw=[8, 0, 0], tail2=[0, 6, 0],
             tail3=[0, 8, 0]), arms(40))
    settle(k4)
    search(m, k4, "neck", [[x, 0, 0] for x in range(-30, 30, 2)], 1.5, head_grp, keep={"neck"}, skip=skip)
    search(m, k4, "tail", [[x, 8, 0] for x in range(-36, 6, 2)], 0.3, tail_grp, skip=skip)
    k5 = P(k4, R(jaw=[12, 0, 0], tail4=[0, 12, 0], tail5=[0, 12, 0]), arms(48, -6))
    k5["body"]["rotation"] = [0, 0, 12]                                                          # rolls a little on its side
    settle(k5)
    k5["head"] = {"rotation": [6, 10, 6]}
    search(m, k5, "neck", [[x, 14, 0] for x in range(-30, 36, 2)], 0.6, head_grp, keep={"neck"}, skip=skip)
    search(m, k5, "head", [[x, 10, 6] for x in range(-24, 34, 2)], 0.3, head_grp, keep={"neck"}, skip=skip)
    search(m, k5, "tail", [[x, 10, -6] for x in range(-36, 6, 2)], 0.3, tail_grp, skip=skip)
    k6 = P(k5)
    k6["chest"]["rotation"][0] = k5["chest"]["rotation"][0] + 3                                  # last breath out
    k6["body"]["position"][1] = k5["body"]["position"][1]
    settle(k6)
    search(m, k6, "neck", [[x, 14, 0] for x in range(-30, 36, 2)], 0.6, head_grp, keep={"neck"}, skip=skip)
    search(m, k6, "tail", [[x, 10, -6] for x in range(-36, 6, 2)], 0.3, tail_grp, skip=skip)
    for kp in (k4, k5, k6):
        kp["body"]["position"][1] = 0
    L = 3.8
    b = pose_sequence(m, [(0, k0), (0.35, k1), (0.8, k2), (1.35, k3), (2.15, k4), (2.95, k5), (3.45, k6), (L, k6)],
                      length=L, step=0.05, skip=skip)
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.55, 1], 0.6: [1, 1, 1], 2.4: [1, 0.8, 1], 3.0: [1, 0.1, 1],
                           3.3: [1, 0.02, 1], L: [1, 0.02, 1]})
    b["breath"] = keys(scale={0: [1, 1, 1], 1.5: [1, 1, 1], 2.6: [0.2, 0.2, 1], L: [0.2, 0.2, 1]})
    if mega:
        for k, name in enumerate(AURA):
            b[name] = keys(scale={0: [1, 1, 1], 0.35: [1.3, 1.5, 1.3], 1.4: [1, 1, 1], 2.6: [0.5, 0.35, 0.5],
                                  3.4: [0.15, 0.05, 0.15], L: [0.15, 0.05, 0.15]})
        for k, name in enumerate(BOLTS):
            fr = {0: [1, 1, 1], 0.1 + 0.03 * k: [0, 0, 0], 0.25 + 0.03 * k: [1.2, 1.2, 1.2], 0.35 + 0.03 * k: [0, 0, 0],
                  0.9 + 0.05 * k: [0.8, 0.8, 0.8], 0.97 + 0.05 * k: [0, 0, 0], L: [0, 0, 0]}
            b[name] = {"scale": {str(round(t, 2)): v for t, v in sorted(fr.items())}}
        for side in ("left", "right"):
            b[f"drool_{side}"] = keys(scale={0: [1, 1, 1], 1.5: [1, 1, 1], 2.6: [1, 0.2, 1], L: [1, 0.2, 1]})
    return {"animation_length": L, "bones": b}

def anims(m=None, mega=False):
    m = m or build(mega)
    sid = "deviljho_carnage" if mega else SID
    k = 1.3 if mega else 1.0
    q = "q.anim_time"
    T = 1.5 if not mega else 1.35
    out = standard_anims(sid, m, make_legs(mega), tail=TAIL, flames=(), sway=lambda f, mul=1.0: sway(f, mul, mega),
                         crouch=-3.0, level=(8, 6), skip=_skip(m), battle_head=-8, idle_amp=1.2 * k,
                         walk_kw=dict(T=T, stride=16, lift=4.5, stance=0.62, bob=0.9,
                                      torso=(1.8, 3.5, 4 * k), tail_amp=(5, 8, 11, 13, 15), arm_amp=6))
    a = f"animation.{sid}."
    out[a + "ground_idle"] = idle_anim(mega)
    out[a + "battle_idle"] = battle_anim(mega)
    # stalking walk: head carried low and thrust forward, swinging to the stride, jaws open and dripping, brows down
    wk = out[a + "ground_walk"]["bones"]
    f = round(360 / T, 3)
    wk["neck"] = {"rotation": [f"7+math.cos({q}*{2 * f}+60)*2", f"math.sin({q}*{f}+90)*6", f"-math.sin({q}*{f})*2"]}
    wk["head"] = {"rotation": [f"-5-math.cos({q}*{2 * f}+90)*2.5", f"-math.sin({q}*{f}+30)*4",
                               f"-math.sin({q}*{f})*3" + (f"+math.sin({q}*1800)*0.7" if mega else "")]}
    wk["jaw"] = {"rotation": [f"{10 * k}+math.sin({q}*{2 * f})*5", 0, 0]}
    wk["brow_left"] = wk["brow_right"] = {"rotation": [5, 0, 0]}
    wk["eye_left"] = wk["eye_right"] = {"scale": [1, 0.85, 1]}
    if mega:
        wk.update(embers(T))
    out[a + "cry"] = cry(mega)
    out[a + "physical"] = physical(mega)
    out[a + "special"] = special(mega)
    out[a + "recoil"] = recoil(mega)
    out[a + "status"] = status(mega)
    out[a + "sleep"] = sleep_anim(m, mega)
    out[a + "faint"] = ko_anim(m, mega)
    for name, an in out.items():          # the beam's glowing disk always starts at its rest size
        an["bones"].setdefault("breath", {"scale": [1, 1, 1]})
        if mega and not name.endswith(("blink", "sleep")):
            an["bones"].update({e: v for e, v in embers(an["animation_length"], an.get("loop", False)).items()
                                if e not in an["bones"]})
    if mega:
        sl = out[a + "sleep"]["bones"]
        for e in EMBERS:
            sl[e] = {"scale": [0, 0, 0]}
    return out

def poser(mega=False):
    sid = "deviljho_carnage" if mega else SID
    p = make_poser(sid, portrait=(0.9, [-0.6, 1.0, 0]), profile=(0.4, [0.0, 1.0, 0]))
    p["rootBone"] = SID
    qp = lambda n: f"q.bedrock_primary('{sid}', '{n}', q.curve('symmetrical_wide'))"
    p["animations"].update(physical=qp("physical"), special=qp("special"), status=qp("status"),
                           recoil=f"q.bedrock_stateful('{sid}', 'recoil')")
    return p
