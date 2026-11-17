# -*- coding: utf-8 -*-
"""Sheep painters for the Rousselin line (Roussin de la Hague): crimped fleece washed by sea spray, dark russet
face and legs, ears held out sideways, slate (schist) hooves, bronze bells, granite horns.
Built on the bovine rig (same quadruped legs, gait and poses)."""
import math
from modelgen import fill, shade, mix, FACE_LIGHT, apply
from bovine import vnoise, light, put, side_cols

def fleece(*, seed=1, tint=0.55, salt=0.0, low=None, curl=1.0, key="wool", dark="wool_dark", shade_key="wool_shade",
           light_key="wool_light", extra=None):
    """Crimped fleece in model space (fn3): cream locks with a grey-brown cast that gathers on the lower body
    (low=(y_top, y_bottom)), each lock outlined by a soft shadow ring and tipped lighter; optional salt crystals
    (sea spray) sparkling at the tips. extra(p, face) -> palette key or None: species overrides."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.1)
            k = extra(p, face) if extra else None
            if k:
                put(px, X, Y, pal[k], f, rnd, 4)
                continue
            # large-scale cast: patches of greyer / browner wool, more of it low on the body
            t = vnoise(p[0] * 0.18 + 3, p[1] * 0.18, p[2] * 0.18, seed) * tint
            if low:
                yt, yb = low
                t += max(0.0, min(1.0, (yt - p[1]) / max(yt - yb, 1e-3))) * 0.45
            col = mix(pal[key], pal[dark], max(0.0, min(1.0, t)))
            # locks: cellular-ish crimp from two octaves of value noise
            u = vnoise(p[0] * 0.9 * curl, p[1] * 0.9 * curl, p[2] * 0.9 * curl, seed + 7)
            v = vnoise(p[0] * 1.9 * curl + 11, p[1] * 1.9 * curl, p[2] * 1.9 * curl, seed + 9)
            w = 0.65 * u + 0.35 * v
            if abs(w - 0.5) < 0.06:
                col = mix(col, pal[shade_key], 0.9)           # shadow between locks
            elif w > 0.64:
                col = mix(col, pal[light_key], 0.7)           # lock tips catching the light
            if salt and face != "down" and rnd.random() < salt and w > 0.6:
                col = pal["salt"]
            put(px, X, Y, col, f, rnd, 2)
    return {"fn3": fn3}

def face_hair(key="face", light_key="face_light", seed=4):
    """Short dark facial hair with a russet sheen (the 'roussin' face), lighter on the bridge of the nose."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            n = vnoise(p[0] * 0.7, p[1] * 0.7, p[2] * 0.7, seed)
            col = mix(pal[key], pal[light_key], 0.35 * n)
            put(px, X, Y, col, light(face, Y - fy, fh, 0.12), rnd, 4)
    return {"fn3": fn3}

def slate_hoof(px, faces, pal, rnd):
    """Schist hoof: blue-grey slate with fine foliation lines and a silvery mica glint, cleft at the front."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                c = pal["slate"]
                if fc in ("north", "south", "east", "west") and j % 2 == 1:
                    c = pal["slate_dark"]
                if rnd.random() < 0.08:
                    c = pal["slate_mica"]
                put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)
    for fc in ("north", "up", "down"):
        x, y, w, h = faces[fc]
        if w >= 2:
            for j in range(h):
                px[x + w // 2, y + j] = pal["slate_dark"]

def schist(px, faces, pal, rnd):
    """Layered schist plate: slate courses with mica sheen."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                c = pal["slate_dark"] if (j + (i // 3)) % 3 == 0 else pal["slate"]
                if rnd.random() < 0.1:
                    c = pal["slate_mica"]
                put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)

def granite(rings=2, along="x"):
    """Granite horn: speckled grey (or rosy) granite - black biotite, white quartz, pink feldspar - with darker
    growth ridges every `rings` texels along the horn."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    r = rnd.random()
                    c = pal["granite"]
                    if r < 0.12:
                        c = pal["granite_dark"]
                    elif r < 0.2:
                        c = pal["granite_light"]
                    elif r < 0.27:
                        c = pal["granite_pink"]
                    k = i if (along == "x" and fc in ("north", "south", "up", "down")) or \
                        (along == "z" and fc in ("east", "west", "up", "down")) else j
                    if rings and k % rings == 0:
                        c = mix(c, pal["granite_dark"], 0.35)
                    put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)
    return fn

def bronze_bell(px, faces, pal, rnd):
    """Bronze bell: warm metal, a bright highlight stripe, dark rim at the mouth (bottom row)."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                c = pal["bronze"]
                if fc in ("north", "east") and i == min(1, w - 1):
                    c = pal["bronze_light"]
                if fc not in ("up", "down") and j == h - 1:
                    c = pal["bronze_dark"]
                if fc == "down":
                    c = pal["bronze_dark"] if (0 < i < w - 1 and 0 < j < h - 1) else pal["bronze"]
                put(px, x + i, y + j, c, FACE_LIGHT[fc] if fc != "down" else 1.0, rnd, 2)

def strap(key="ribbon", dark="ribbon_dark", stud=None):
    """Collar band: colour with darker edges (stitching), optional studs."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            fill(px, x, y, w, h, pal[key], FACE_LIGHT[fc], rnd, 3)
            if fc in ("north", "south", "east", "west") and h >= 2:
                for i in range(w):
                    px[x + i, y] = shade(pal[dark], FACE_LIGHT[fc])
                    px[x + i, y + h - 1] = shade(pal[dark], FACE_LIGHT[fc])
                if stud and h >= 3:
                    for i in range(1, w, 3):
                        px[x + i, y + h // 2] = pal[stud]
    return fn

def sheep_ear(px, faces, pal, rnd):
    """Ear held out sideways: dark russet outside, warm pinkish-brown inside (front / under faces), a darker rim."""
    for fc, (x, y, w, h) in faces.items():
        inner = fc in ("north", "down")
        for j in range(h):
            for i in range(w):
                edge = inner and (j == 0 or j == h - 1)
                c = pal["face"] if (not inner or edge) else (pal["ear_in"] if (i + j) % 3 else pal["ear_in_light"])
                put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)

def muzzle(px, faces, pal, rnd):
    """Sheep muzzle: greyer russet, Y-shaped dark nostrils at the top corners, mouth line under."""
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["muzzle"], FACE_LIGHT[fc], rnd, 3)
    x, y, w, h = faces["north"]
    if w >= 3:
        px[x, y] = pal["nostril"]
        px[x + w - 1, y] = pal["nostril"]
        px[x + w // 2, y + h - 1] = pal["nostril"]
        for i in range(w):
            if h >= 2:
                px[x + i, y + h - 1] = pal["mouth"] if i != w // 2 else pal["nostril"]

# ============================================================================ sleep: curled up, head on the flank
def curled_sleep(m, sp, *, trunk, skip=(), side=1):
    """Head turned back along the flank and laid on the ground / against the fleece (lambs and ewes sleeping),
    searched so that the head never goes through the body and rests low. side=+1: towards the +X flank."""
    from avian import _inv, _samples
    from bovine import copy_pose, rng
    bones = {b.name: b for b in m.bones}
    head_grp = [n for n in bones if n in __import__("biped").descendants(m, "head") and n not in skip
                and not n.startswith("eye")]
    solids = [n for n in trunk if bones[n].cubes]
    best = None
    for ny in rng(40, 120, 9):
        for nx in rng(-10, 50, 7):
            for hx in rng(-20, 40, 7):
                for hz in (0, 20, 40):
                    p = copy_pose(sp)
                    p["neck"] = {"rotation": [nx, ny * side, 0]}
                    p["head"] = {"rotation": [hx, 20 * side, hz * side]}
                    mats = m.mats(p)
                    hp = [apply(mats[n], q) for n in head_grp for c in bones[n].cubes if all(v > 0 for v in c.size)
                          for q in _samples(c)]
                    inside = 0
                    for n in solids:
                        inv = _inv(mats[n])
                        for c in bones[n].cubes:
                            if not all(v > 0 for v in c.size):
                                continue
                            lo = [c.origin[i] + 0.4 for i in range(3)]
                            hi = [c.origin[i] + c.size[i] - 0.4 for i in range(3)]
                            for q in hp:
                                r = apply(inv, q)
                                if all(lo[i] < r[i] < hi[i] for i in range(3)):
                                    inside += 1
                    hmin = min(q[1] for q in hp)
                    if hmin < 0.05:
                        continue
                    hc = [sum(q[i] for q in hp) / len(hp) for i in range(3)]
                    sc = 25.0 * inside + 2.0 * hmin + 0.15 * abs(hc[2]) + 0.01 * (abs(nx) + abs(hx) + hz)
                    if best is None or sc < best[0]:
                        best = (sc, nx, ny, hx, hz)
    _, nx, ny, hx, hz = best
    sp["neck"] = {"rotation": [nx, ny * side, 0]}
    sp["head"] = {"rotation": [hx, 20 * side, hz * side]}
    return sp
