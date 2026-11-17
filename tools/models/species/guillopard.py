# -*- coding: utf-8 -*-
"""#1051 Guillopard — léopard souverain légendaire (Acier / Électrik), Guillaume le Conquérant et les deux léopards
d'or de l'héraldique normande.
A powerful, long-legged leopard: deep navy coat strewn with darker rosettes, golden chest, belly, throat and
cheeks, golden filigree swirls on the brow, the cheeks and the shoulders, fierce glowing pale-blue eyes under dark
brows. A mane of golden flames crackling with blue electricity rises from the head and runs down the nape. Above the
head floats a crown of five golden lightning bolts (a blue diamond in the front one) on a ring of light. Golden greaves
engraved with violet lines on the forelegs, golden hocks, dark paws with claws, golden flame wisps round the lower
legs, and a long tail turning into a huge plume of golden flame that curls up at the end. Lightning arcs crackle
around it. Shiny: the arms of Normandy, a golden leopard with crimson flames ("de gueules à deux léopards d'or")."""
import math, random
from modelgen import Model, Cube, rgb, mix, apply, shade, FACE_LIGHT
from biped import Leg, walk, keys, kf, smooth, lowest, descendants
from bovine import (SIDES, GAIT, vnoise, put, light, side_cols, stance, legs_pose, copy_pose, sampled, lerp_keys,
                    knockout, lay_tail, fold_leg, rng, finalize, bovine_poser)

SID, DEX = "guillopard", 1051
FRAME_BONES = ("head", "jaw")
HEIGHT_SKIP = ("crown", "mane", "ear", "spark", "tail", "plume", "flame")     # 2.4 m to the top of the skull
HITBOX_WIDTH = 2.2

PAL = {
    "coat": rgb("#22306A"), "coat_dark": rgb("#141C44"), "coat_light": rgb("#3A4E94"),
    "spot": rgb("#080C22"), "rosette_in": rgb("#1C285C"),
    "gold": rgb("#E8B43C"), "gold_light": rgb("#FCE28E"), "gold_dark": rgb("#B37E1E"), "cream": rgb("#F7E3A6"),
    "metal": rgb("#E8B436"), "metal_hi": rgb("#FFF2B0"), "metal_dark": rgb("#966414"),
    "engrave": rgb("#7A56CC"), "engrave_dark": rgb("#4A3192"),
    "flame_deep": rgb("#F2A21C"), "flame": rgb("#FFD84C"), "flame_tip": rgb("#FFF6C0"),
    "spark": rgb("#7FE4FF"), "spark_core": rgb("#EAFBFF"), "spark_deep": rgb("#3AA4F2"),
    "eye": rgb("#E8FBFF"), "eye_glow": rgb("#78DCFF"), "eye_dark": rgb("#070A1C"),
    "nose": rgb("#0E1230"), "nose_hi": rgb("#2C3670"), "mouth": rgb("#3A0E1E"), "tongue": rgb("#C45672"),
    "fang": rgb("#F4F0E2"), "claw": rgb("#262634"), "claw_hi": rgb("#5C5C70"), "pupil": rgb("#0B1A3A"),
    "halo": rgb("#8CE6FF"), "halo_core": rgb("#F2FCFF"), "gem": rgb("#3EC4FF"), "gem_hi": rgb("#D8F6FF"),
    "ear_in": rgb("#E6C066"),
}
SHINY = dict(PAL, **{        # "de gueules à deux léopards d'or": golden leopard, crimson flames and armour
    "coat": rgb("#DFA328"), "coat_dark": rgb("#B07816"), "coat_light": rgb("#F6CC5A"),
    "spot": rgb("#6C1A10"), "rosette_in": rgb("#C6801C"),
    "gold": rgb("#FFF0C6"), "gold_light": rgb("#FFFBEA"), "gold_dark": rgb("#D6B472"), "cream": rgb("#FFF8E4"),
    "metal": rgb("#C8202C"), "metal_hi": rgb("#FF6E5E"), "metal_dark": rgb("#760C14"),
    "engrave": rgb("#FFD44A"), "engrave_dark": rgb("#C89A1E"),
    "flame_deep": rgb("#B80E1C"), "flame": rgb("#FF3A2C"), "flame_tip": rgb("#FFB4A2"),
    "spark": rgb("#FFD84A"), "spark_core": rgb("#FFF6CC"), "spark_deep": rgb("#FF8A1E"),
    "eye_glow": rgb("#FFB43C"), "eye": rgb("#FFF6E2"), "pupil": rgb("#5A1206"),
    "nose": rgb("#3A1406"), "nose_hi": rgb("#6A2A12"),
    "halo": rgb("#FFD84A"), "halo_core": rgb("#FFF8D6"), "gem": rgb("#FF2A3A"), "gem_hi": rgb("#FFC4C4"),
    "ear_in": rgb("#FFF0C6"),
})
G = {"glow": True, "shading": False}

# ============================================================================ painters
def _h(a, b, seed):
    n = (int(a) * 73856093) ^ (int(b) * 19349663) ^ (seed * 83492791)
    return ((n * 2654435761) & 0xFFFFFFFF) / 0xFFFFFFFF

def nearest(u, v, seed, cell):
    """Jittered-grid nearest point: (distance, angle, cell hash)."""
    cu, cv = math.floor(u / cell), math.floor(v / cell)
    best = (9e9, 0.0, 0.0)
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            a, b = cu + du, cv + dv
            pu = (a + 0.2 + 0.6 * _h(a, b, seed)) * cell
            pv = (b + 0.2 + 0.6 * _h(b, a, seed + 1)) * cell
            d = math.hypot(u - pu, v - pv)
            if d < best[0]:
                best = (d, math.atan2(v - pv, u - pu), _h(a, b, seed + 7))
    return best

def face_uv(face, p):
    if face in ("east", "west"):
        return p[2], p[1]
    if face in ("north", "south"):
        return p[0], p[1]
    return p[0], p[2]

def seg_dist(px_, py_, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px_ - ax) * dx + (py_ - ay) * dy) / L2))
    return math.hypot(px_ - ax - t * dx, py_ - ay - t * dy)

def poly_marks(spec, width=0.55):
    """spec: {face_group: [(key, [(a, b), ...]), ...]} with face groups 'front' (north: x, y), 'top' (up: x, z) and
    'side' (east/west: z, y; mirrored on both sides through |x|). Coordinates are the modelled (rest, local)
    positions. Returns marks(pl, face) -> palette key or None."""
    def marks(pl, face):
        if face == "north":
            grp, a, b = "front", pl[0], pl[1]
        elif face == "up":
            grp, a, b = "top", pl[0], pl[2]
        elif face in ("east", "west"):
            grp, a, b = "side", pl[2], pl[1]
        else:
            return None
        for key, pts in spec.get(grp, ()):
            for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                if seg_dist(a, b, ax, ay, bx, by) < width:
                    return key
        return None
    return marks

def curl(cx, cy, r, a0, a1, n=6, sx=1.0):
    """Points of a small arc (a curl at the end of a filigree line)."""
    return [(cx + sx * r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]

def leopard(seed=3, cell=8.0, gold=None, small=False, marks=None, local=False, plain=()):
    """Navy coat (fn3) with leopard rosettes (broken dark rings round a darker centre) or small solid spots,
    soft fur noise; `gold(p, pl, face)` -> True paints the golden underside instead; `marks(pl, face)` overlays
    golden filigree. Rosettes are laid out in world space (or modelled space if local)."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = pl if local else apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.14)
            n = vnoise(p[0] * 0.2, p[1] * 0.2, p[2] * 0.2, seed)
            col = mix(pal["coat"], mix(pal["coat_dark"], pal["coat_light"], max(0.0, min(1.0, 0.5 + (n - 0.5) * 1.1))), 0.4)
            if gold and gold(p, pl, face):
                s = vnoise(p[0] * 0.5, p[1] * 0.9, p[2] * 0.5, seed + 5)
                col = mix(pal["gold_dark"], pal["gold_light"], 0.25 + 0.6 * s)
            elif face not in plain:
                u, v = face_uv(face, p)
                cc = cell * (0.55 if small else 1.0)
                d, ang, hh = nearest(u, v, seed, cc)
                if small:
                    if d < cc * 0.26:
                        col = pal["spot"]
                else:
                    r = cc * 0.38
                    if d < r - 1.3:
                        col = mix(col, pal["rosette_in"], 0.8)
                    elif d < r and (ang / (2 * math.pi) * 3 + hh * 3) % 1.0 > 0.2:
                        col = pal["spot"]
            if marks:
                k = marks(pl, face)
                if k:
                    col = pal[k]
            put(px, X, Y, col, f, rnd, 2)
    return {"fn3": fn3}

def goldfur(seed=4, marks=None, light_top=True):
    """Golden fur: streaky warm gold, lighter on top faces."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.12)
            s = vnoise(p[0] * 0.6, p[1] * 1.1, p[2] * 0.6, seed)
            col = mix(pal["gold_dark"], pal["gold_light"], 0.2 + 0.65 * s)
            if face == "up" and light_top:
                col = mix(col, pal["cream"], 0.35)
            if marks:
                k = marks(pl, face)
                if k:
                    col = pal[k]
            put(px, X, Y, col, f, rnd, 2)
    return {"fn3": fn3}

def metal(px, faces, pal, rnd):
    """Golden greave: bright rim on top, dark rim at the bottom, a highlight streak, violet engraved chevrons."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = pal["metal"]
                if fc in ("north", "south", "east", "west"):
                    if j == 0:
                        col = pal["metal_hi"]
                    elif j == h - 1:
                        col = pal["metal_dark"]
                    elif i == 1:
                        col = mix(pal["metal"], pal["metal_hi"], 0.55)
                    elif i in (1, w - 2) and 0 < j < h - 1:
                        col = pal["engrave"] if j % 3 else pal["engrave_dark"]
                elif fc == "up":
                    col = pal["metal_hi"] if (i + j) % 2 else pal["metal"]
                px[x + i, y + j] = shade(col, FACE_LIGHT[fc] if fc != "up" else 1.0)

def flame(u0, U, v0, V, n=4, seed=1, lean=0.35, axis="z", root=0.25, glow=True, width=1.0, spark=0.45):
    """Tongues of golden flame on a plane, crackling with electric blue at the edges. axis='z': the plane is
    vertical along Z (faces east/west, u = z); axis='x': vertical along X (faces north/south, u = x).
    Tongues rise from v0 up to V, leaning by `lean` along +u per unit of height."""
    rr = random.Random(seed)
    tongues = []
    for k in range(n):
        c = u0 + U * (k + 0.5) / n + rr.uniform(-0.18, 0.18) * U / n
        tongues.append((c, V * rr.uniform(0.6, 1.0), U / n * rr.uniform(0.7, 0.95) * width))
    faces_ok = ("east", "west") if axis == "z" else ("north", "south")
    def inside(u, v):
        dv = v - v0
        if dv < 0:
            return None
        if dv < V * root and u0 <= u <= u0 + U:
            return dv / V
        for c, h, w in tongues:
            if dv < h:
                t = dv / h
                if abs(u - (c + lean * dv)) < w * (1 - t) ** 0.75:
                    return dv / V
        return None
    def fn3(px, faces, pal, rnd, cube):
        for face, X, Y, pl in cube.texels():
            if face not in faces_ok:
                px[X, Y] = (0, 0, 0, 0)
                continue
            u = pl[2] if axis == "z" else pl[0]
            v = pl[1]
            t = inside(u, v)
            if t is None:
                px[X, Y] = (0, 0, 0, 0)
                continue
            edge = any(inside(u + du, v + dv) is None for du, dv in ((0.9, 0), (-0.9, 0), (0, 0.9)))
            col = pal["flame_deep"] if t < 0.3 else pal["flame"] if t < 0.68 else pal["flame_tip"]
            if edge and rnd.random() < spark:
                col = pal["spark"] if rnd.random() < 0.7 else pal["spark_core"]
            elif rnd.random() < 0.05:
                col = pal["spark_core"]
            px[X, Y] = col
    d = {"fn3": fn3}
    if glow:
        d.update(G)
    return d

def plume(z0, L, ac, h0, h1, seed=1, axis="y", tip=0.0):
    """Tail plume of long golden flame-fur strands along +Z, widening from h0 to h1, ragged wispy edges with blue
    electric glints; axis='y': vertical plane (faces east/west, across = y); 'x': horizontal plane (up/down)."""
    faces_ok = ("east", "west") if axis == "y" else ("up", "down")
    def env(z, a):
        t = (z - z0) / L
        if t < -0.05 or t > 1.08 + tip:
            return None
        e = (h0 + (h1 - h0) * max(0.0, min(1.0, t))) / 2
        s = math.floor((a - ac) * 0.9 + 0.5)
        e *= 1 + 0.2 * math.sin(z * 1.3 + s * 2.4 + seed)
        if t > 1.0:
            if not tip and abs(a - ac) > e * 0.6:
                return None
            reach = 1.0 + tip * (0.35 + 0.65 * ((s * 7 + seed * 3) % 5) / 4)      # flame tongues of uneven length
            if t > reach:
                return None
            e *= 1 - 0.5 * (t - 1.0) / max(tip, 0.01)
        d = abs(a - ac)
        return None if d > e else d / max(e, 0.5)
    def fn3(px, faces, pal, rnd, cube):
        for face, X, Y, pl in cube.texels():
            if face not in faces_ok:
                px[X, Y] = (0, 0, 0, 0)
                continue
            a = pl[1] if axis == "y" else pl[0]
            r = env(pl[2], a)
            if r is None:
                px[X, Y] = (0, 0, 0, 0)
                continue
            strand = math.sin((a - ac) * 2.2 + 1.2 * math.sin(pl[2] * 0.7 + seed))
            col = pal["flame_tip"] if r < 0.25 else pal["flame"] if strand > -0.2 else pal["flame_deep"]
            if r > 0.78:
                col = pal["spark"] if rnd.random() < 0.55 else pal["flame"]
            if rnd.random() < 0.04:
                col = pal["spark_core"]
            px[X, Y] = col
    return {"fn3": fn3, **G}

SPIKE = [(0.5, 0.0), (0.88, 0.36), (0.62, 0.4), (0.96, 0.7), (0.72, 0.73), (0.86, 1.0), (0.14, 1.0), (0.3, 0.62),
         (0.05, 0.6), (0.36, 0.26)]          # crown point: a zigzag spike, tip at the top (y down)
BOLT = [(0.48, 0.0), (1.0, 0.0), (0.68, 0.4), (1.0, 0.4), (0.2, 1.0), (0.4, 0.55), (0.0, 0.55)]

def in_poly(x, y, poly):
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

def bolt(poly=BOLT, body="metal", edge="spark", up=True, gem=False):
    """Lightning bolt cut out of a plane (any orientation), tip at the top if up; edge outline glows."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h) or fc in ("up", "down") and min(w, h) < 2:
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            def ins(i, j):
                if not (0 <= i < w and 0 <= j < h):
                    return False
                u, v = (i + 0.5) / w, (j + 0.5) / h
                return in_poly(u, 1 - v if up else v, poly)
            for j in range(h):
                for i in range(w):
                    if not ins(i, j):
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    e = not all(ins(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    col = pal[edge] if e else pal[body]
                    if not e and body == "metal" and (i + j) % 4 == 0:
                        col = pal["metal_hi"]
                    if gem and abs((i + 0.5) / w - 0.5) / 0.2 + abs((j + 0.5) / h - 0.66) / 0.13 <= 1:
                        col = pal["gem_hi"] if j < h * 0.47 else pal["gem"]
                    px[x + i, y + j] = col
    return {"fn": fn, **G}

def ring(width=1.0):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            R = min(w, h) / 2 - 0.3
            for j in range(h):
                for i in range(w):
                    d = math.hypot(i + 0.5 - w / 2, j + 0.5 - h / 2)
                    if R - width <= d <= R:
                        px[x + i, y + j] = pal["halo_core"] if (i * 3 + j) % 5 == 0 else pal["halo"]
                    else:
                        px[x + i, y + j] = (0, 0, 0, 0)
    return {"fn": fn, **G}

EYE_KEYS = {"E": "eye", "G": "eye_glow", "K": "eye_dark", "S": "spark_core", "P": "pupil", "L": "gold_light"}

def grid_plane(rows, keys=EYE_KEYS, used=("north",), mirror=False, glow=True):
    """Char grid on the faces in `used` (north: col 0 = viewer's left), transparent elsewhere and on '.'."""
    rows = [r[::-1] for r in rows] if mirror else rows
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    ch = rows[min(j, len(rows) - 1)][i] if (fc in used and i < len(rows[0])) else "."
                    px[x + i, y + j] = (0, 0, 0, 0) if ch == "." else pal[keys[ch]]
    d = {"fn": fn}
    if glow:
        d.update(G)
    return d

def side_grid(rows, keys=EYE_KEYS, glow=True):
    """Char grid on the side faces of a YZ plane, columns counted from the front (both sides read the same)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            cols = side_cols(fc, w) if fc in ("east", "west") else None
            for j in range(h):
                for k in range(w):
                    ch = rows[min(j, len(rows) - 1)][k] if (cols is not None and k < len(rows[0])) else "."
                    xx = x + (cols[k] if cols is not None else k)
                    px[xx, y + j] = (0, 0, 0, 0) if ch == "." else pal[keys[ch]]
    d = {"fn": fn}
    if glow:
        d.update(G)
    return d

def chin_fn(px, faces, pal, rnd):
    """Small golden chin with a dark lower-lip line along its top front edge and a paler tuft underneath."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = mix(pal["gold_dark"], pal["gold_light"], 0.35 + 0.4 * ((i * 7 + j * 3) % 5) / 4)
                if fc == "down":
                    col = pal["cream"]
                put(px, x + i, y + j, col, FACE_LIGHT[fc], rnd, 2)

def nose_fn(px, faces, pal, rnd):
    """Nose leather: an inverted triangle (the lower corners are cut away), a lighter glint on top."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = pal["nose"]
                if fc == "up" or (fc == "north" and j == 0 and 0 < i < w - 1):
                    col = pal["nose_hi"]
                mid = (w // 2 - 1, w // 2) if w % 2 == 0 else (w // 2,)
                if fc in ("north", "south") and j == h - 1 and i not in mid or fc in ("east", "west") and j == h - 1:
                    col = (0, 0, 0, 0)
                px[x + i, y + j] = col

def pad_fn(left, spots=True):
    """Whisker pad: golden fur, a few dark whisker spots, one dark pixel at the inner bottom corner (the branch of
    the cat's inverted-Y mouth)."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            fx, fy, fw, fh = faces[face]
            s = vnoise(pl[0] * 0.8, pl[1] * 1.2, pl[2] * 0.8, 9)
            col = mix(pal["gold_dark"], pal["gold_light"], 0.35 + 0.55 * s)
            i, j = X - fx, Y - fy
            inner = (i == 0) if left else (i == fw - 1)
            if spots and face == "north" and j == fh - 1 and inner:
                col = pal["nose"]                                   # mouth under the nose
            elif spots and face == "north" and j == 1 and i in ((1, 3) if left else (0, 2)):
                col = shade(pal["nose"], 1.5)                       # whisker spots
            put(px, X, Y, col, light(face, j, fh, 0.1), rnd, 2)
    return {"fn3": fn3}

def ear_fn(px, faces, pal, rnd):
    """Rounded leopard ear: navy outside with a dark rim, golden inside (front face) with paler tufts."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = pal["coat_dark"] if j == 0 else pal["coat"]
                if fc == "north":
                    edge = i in (0, w - 1) or j == 0
                    col = pal["coat_dark"] if edge else (pal["ear_in"] if (i + j) % 3 else pal["cream"])
                px[x + i, y + j] = shade(col, FACE_LIGHT[fc])

def solid(key, noise=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    put(px, x + i, y + j, pal[key], FACE_LIGHT[fc], rnd, noise)
    return fn

# ---------------------------------------------------------------------------- golden filigree
def mirror_x(pts):
    return [(-a, b) for a, b in pts]

_TOP_L = [(-0.7, -37.6), (-1.8, -36.4), (-2.6, -35.0), (-2.2, -33.4), (-3.2, -32.0), (-4.6, -31.4)] + \
         curl(-4.6, -30.3, 1.1, -90, -280, 6, 1.0)[1:]
_SIDE = [(-38.0, 36.3), (-36.6, 36.8), (-35.0, 36.4), (-34.0, 35.4)] + curl(-34.8, 34.8, 1.0, 30, 310, 7)[1:]
_DIAMOND = [(0, 37.8), (-0.9, 36.6), (0, 35.3), (0.9, 36.6), (0, 37.8)]
HEAD_MARKS = poly_marks({
    "top": [("gold", _TOP_L), ("gold", mirror_x(_TOP_L)), ("gold", [(0, -37.6), (0, -35.8)])],
    "front": [("gold", _DIAMOND),
              ("eye_dark", [(2.1, 34.9), (4.4, 34.5), (6.9, 35.4)]), ("eye_dark", [(-2.1, 34.9), (-4.4, 34.5), (-6.9, 35.4)]),
              ("gold", [(6.4, 36.5), (7.0, 36.9)]), ("gold", [(-6.4, 36.5), (-7.0, 36.9)])],
    "side": [("gold", _SIDE)],
})
SHOULDER_MARKS = poly_marks({"side": [("gold", [(-20.5, 31.0), (-18.4, 32.2), (-16.0, 31.6), (-15.0, 29.8)] +
                                               curl(-16.1, 29.2, 1.1, 20, 300, 7)[1:])]})
MUZZLE_MARKS = poly_marks({"front": [("nose", [(0, 31.4), (0, 28.6)])],
                           "side": [("nose", [(-41.8, 28.5), (-39.5, 28.6), (-38.3, 29.2)])]}, width=0.5)

def belly(y):
    return lambda p, pl, face: face == "down" or p[1] < y
NECK_GOLD = lambda p, pl, face: face == "down" or pl[1] < 28.5

COAT = leopard()
COAT_S = leopard(seed=5, small=True)
HEADC = leopard(seed=11, small=True, marks=HEAD_MARKS, local=True, plain=("north",))
GOLD = goldfur()
GOLD_H = goldfur(seed=8, marks=HEAD_MARKS)
METAL = {"fn": metal}
CLAW = {"fn": solid("claw", 2)}

# ============================================================================ legs: long, powerful, digitigrade paws
LEGP_F = {"thigh": leopard(seed=21, small=True), "shin": COAT_S, "meta": GOLD, "foot": COAT_S, "claw": CLAW}
LEGP_B = {"thigh": leopard(seed=23), "shin": COAT_S, "meta": GOLD, "foot": COAT_S, "claw": CLAW}
LEGS = []
for _side, _sx in SIDES:
    LEGS.append(Leg(f"front_{_side}", 5.5 * _sx, -14, (10, 9, 5), (25, -5, -20), 3, thigh=(6, 7, 5), shin=(4, 5),
                    meta=(4, 4), foot=(6, 6, 2), claws=(-2.0, -0.7, 0.7, 2.0), paints=LEGP_F, claw_len=2,
                    dewclaw=False, bend=-1))
for _side, _sx in SIDES:
    LEGS.append(Leg(f"back_{_side}", 5.5 * _sx, 13, (11, 10, 8), (-30, 45, -10), 3, thigh=(7, 9, 5), shin=(4, 6),
                    meta=(4, 4), foot=(6, 6, 2), claws=(-2.0, -0.7, 0.7, 2.0), paints=LEGP_B, claw_len=2,
                    dewclaw=False, bend=1))
PIVOT = (0, 26.5, 0)
SEAT = (0, 33.3, 1.0)
TAIL = ("tail", "tail2", "tail3", "tail4", "tail5", "tail6")
MANES = ("mane_head", "mane_crest", "mane1", "mane3")
SPARKS = ("spark_left", "spark_right", "spark_tail", "spark_hip")
PLUMES = ("plume2", "plume3", "plume4", "plume5", "plume6")
FLAMES = tuple(f"flame_{e}_{s}" for e in ("front", "back") for s in ("left", "right"))
EARS = ("ear_left", "ear_right")
EYES = ("eye_left", "eye_right")
EYE_ROWS = ["KKKK.", "GEPEG", ".GPGK"]      # front, outer corner at col 0, slit pupil
EYE_SIDE = ["KL", "GK", "K."]                 # outer corner on the side of the skull, from the front; L = golden liner
WHISKERS = ["...wWw", "WWWw..", "..wWWw", "......"]          # inner end at col 0 (+X side)
WHISKER_KEYS = {"W": "spark_core", "w": "spark"}

def build():
    m = Model(SID, DEX, (512, 512))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
        x, z, H = lg.x, lg.hip_z, lg.H
        L1, L2, L3 = lg.L
        ty = H - L1 - L2 - L3
        sx = 1 if x > 0 else -1
        if lg.side.startswith("front"):
            (ws, ds) = lg.shin
            m.get(lg.bones[1]).cubes.extend([                                       # engraved golden greave
                Cube([x - ws / 2 - 0.5, H - L1 - L2 + 0.5, z - ds / 2 - 0.5], [ws + 1, L2 - 2, ds + 1], METAL),
                Cube([x - ws / 2 - 0.5, H - L1 - 1.5, z - ds / 2 - 0.5], [ws + 1, 2, ds + 1], METAL)])   # elbow cop
            m.get(lg.bones[0]).cubes.append(Cube([x - 3.5, H - 6, z - 3.5], [7, 8, 7], leopard(seed=31, small=True)))
        else:
            (wm, dm) = lg.meta
            m.get(lg.bones[2]).cubes.append(                                        # golden hock armour
                Cube([x - wm / 2 - 0.5, ty + 1.5, z - dm / 2 - 0.5], [wm + 1, L3 - 3, dm + 1], METAL))
            m.get(lg.bones[0]).cubes.append(Cube([x - 4, H - 8, z - 4.5], [8, 9, 9], leopard(seed=33)))   # haunch
        # toes on top of the paw, golden flame wisps rising behind the lower leg
        fz = z + lg.foot[2] - lg.foot[1]
        m.get(lg.bones[3]).cubes.extend([Cube([x + o - 0.5, ty, fz], [1, 1, 2], COAT_S) for o in (-2.0, -0.7, 0.7, 2.0)])
        m.bone(f"flame_{lg.side}", lg.bones[2], [x, ty, z], cubes=[
            Cube([x, ty, z + 1], [0, 8, 6], flame(z + 1, 6, ty, 8, n=3, seed=40 + int(z) + sx, lean=0.35)),
            Cube([x - 3, ty, z + 2.2], [6, 7, 0], flame(x - 3, 6, ty, 7, n=3, seed=50 + int(z) + sx, axis="x", lean=0.0))])

    # ---------------------------------------------------------------- trunk: deep chest, tucked waist, haunches
    m.bone("torso", "body", [0, 27, 0], cubes=[
        Cube([-6, 20, -7], [12, 12, 15], leopard(seed=3, gold=belly(22))),           # waist, tucked belly
        Cube([-7, 20, 8], [14, 14, 11], leopard(seed=4, gold=belly(22))),            # hindquarters
        Cube([7, 22, 8], [1, 11, 10], leopard(seed=6)), Cube([-8, 22, 8], [1, 11, 10], leopard(seed=7)),   # haunch muscles
        Cube([-6, 34, 9], [12, 1, 8], COAT),                                         # rump
        Cube([-5, 32, -5], [10, 1, 12], COAT),                                       # back line
        Cube([-2, 30, 19], [4, 3, 1], COAT)])                                        # root of the tail
    m.bone("locator_seat_1", "torso", list(SEAT), locators={"seat_1": list(SEAT)})   # rider on the back
    m.bone("chest", "torso", [0, 27, -7], cubes=[
        Cube([-7, 18, -21], [14, 15, 14], leopard(seed=8, gold=belly(23), marks=SHOULDER_MARKS)),
        Cube([-6, 18, -22], [12, 12, 1], GOLD), Cube([-5, 19, -23], [10, 9, 1], GOLD),   # golden breast
        Cube([7, 22, -20], [1, 10, 8], leopard(seed=9, marks=SHOULDER_MARKS)),       # shoulder muscles
        Cube([-8, 22, -20], [1, 10, 8], leopard(seed=10, marks=SHOULDER_MARKS)),
        Cube([-6.5, 33, -19], [13, 1, 9], COAT), Cube([-4.5, 34, -18], [9, 1, 6], COAT)])   # shoulder blades
    m.bone("mane3", "chest", [0, 34.5, -17], cubes=[                                 # flames running down the withers
        Cube([s * 1.6, 34, -19], [0, 7, 11], flame(-19, 11, 34, 7, n=3, seed=7 + k, lean=1.0, width=1.2),
             rotation=[0, 0, 12 * s], pivot=[s * 1.6, 34, -15]) for k, (_, s) in enumerate(SIDES)])

    # ---------------------------------------------------------------- neck (raised 40°), golden throat, nape mane
    m.bone("neck", "chest", [0, 30, -18], rotation=[-40, 0, 0], cubes=[
        Cube([-6, 25, -30], [12, 11, 12], leopard(seed=12, gold=NECK_GOLD)),
        Cube([-5, 24, -29], [10, 1, 10], GOLD),
        Cube([6, 26, -29], [1, 9, 10], leopard(seed=13)), Cube([-7, 26, -29], [1, 9, 10], leopard(seed=14)),
        Cube([-2.5, 36, -30], [5, 2, 12], GOLD)])                                     # golden nape ridge
    m.bone("mane1", "neck", [0, 37, -27], cubes=[
        Cube([0, 37.5, -31], [0, 11, 14], flame(-31, 14, 37.5, 11, n=4, seed=3, lean=0.8, width=1.25))] + [
        Cube([s * 2.4, 37, -30], [0, 9, 12], flame(-30, 12, 37, 9, n=4, seed=4 + k, lean=0.85, width=1.2),
             rotation=[0, 0, 15 * s], pivot=[s * 2.4, 37, -26]) for k, (_, s) in enumerate(SIDES)])

    # ---------------------------------------------------------------- head (level again), modelled in the neck frame
    m.bone("head", "neck", [0, 31, -30], rotation=[40, 0, 0], cubes=[
        Cube([-7, 29, -38], [14, 9, 10], HEADC),                                     # broad round cranium
        Cube([-6, 38, -37], [12, 1, 8], HEADC),                                      # domed forehead
        Cube([-6, 30, -28], [12, 7, 2], HEADC),                                      # back of the skull
        Cube([-8, 29, -37], [16, 5, 7], GOLD_H),                                     # wide golden cheekbones
        Cube([-4.5, 28, -42], [9, 5, 4], leopard(seed=15, small=True, local=True, marks=MUZZLE_MARKS,
                                                 gold=lambda p, pl, f: f in ("north", "down") or pl[1] < 31.5)),   # short muzzle
        Cube([-3.5, 33, -42], [7, 1, 4], leopard(seed=16, small=True, local=True, gold=lambda p, pl, f: f == "north")),
        Cube([-2, 34, -41], [4, 1, 3], HEADC),                                       # nasal ridge up to the brow
        Cube([-2, 31.6, -43.2], [4, 2, 1], {"fn": nose_fn}),                         # nose leather
        Cube([-4.7, 28.4, -43], [4, 3, 2], pad_fn(False)), Cube([0.7, 28.4, -43], [4, 3, 2], pad_fn(True)),   # whisker pads
        Cube([-4.2, 27.7, -42.7], [3, 1, 1], pad_fn(False, False)), Cube([1.2, 27.7, -42.7], [3, 1, 1], pad_fn(True, False)),  # round lips
        Cube([-3.5, 28.02, -41.5], [7, 0, 8], {"base": "mouth"}),                    # palate
        Cube([1.8, 26.9, -42.4], [1, 2, 1], {"base": "fang"}), Cube([-2.8, 26.9, -42.4], [1, 2, 1], {"base": "fang"}),   # canine tips
        # golden cheek ruff: tufts swept back and down
        Cube([8.05, 24, -37], [0, 9, 9], flame(-37, 9, 24, 9, n=3, seed=12, lean=0.7, width=1.2, glow=False),
             rotation=[-62, 0, 0], pivot=[8.05, 30, -33]),
        Cube([-8.05, 24, -37], [0, 9, 9], flame(-37, 9, 24, 9, n=3, seed=13, lean=0.7, width=1.2, glow=False),
             rotation=[-62, 0, 0], pivot=[-8.05, 30, -33])])
    m.bone("jaw", "head", [0, 29, -34], cubes=[
        Cube([-3, 26, -41.5], [6, 2, 4], {"fn": chin_fn}),                           # small recessed chin
        Cube([-5, 26, -38], [10, 3, 6], GOLD),                                       # jaw
        Cube([-3.5, 27.98, -41.5], [7, 0, 8], {"base": "mouth"}),
        Cube([-2.5, 27.2, -40.8], [5, 1, 6], {"base": "tongue"}),
        Cube([1.6, 28, -41.8], [1, 1, 1], {"base": "fang"}), Cube([-2.6, 28, -41.8], [1, 1, 1], {"base": "fang"})])
    for side, s in SIDES:                                                    # fierce brows slanting down to the nose
        m.bone(f"brow_{side}", "head", [s * 1.8, 37, -38.2], cubes=[
            Cube([1.8 if s > 0 else -6.8, 36.6, -38.7], [5, 1, 1], {"base": "coat_dark"}, rotation=[0, 0, -14 * s],
                 pivot=[s * 1.8, 37, -38.2])])
    for side, s in SIDES:
        x0 = 2.0 if s > 0 else -7.0
        m.bone(f"eye_{side}", "head", [s * 4.5, 34.9, -38], cubes=[
            Cube([x0, 33.4, -38.03], [5, 3, 0], grid_plane(EYE_ROWS, mirror=(s > 0))),
            Cube([s * 7.03, 33.4, -38], [0, 3, 2], side_grid(EYE_SIDE))])
        X = (lambda a, w: a if s > 0 else -a - w)
        wx = 4.7 if s > 0 else -10.7                                          # crackling electric whiskers
        m.get("head").cubes.append(Cube([wx, 27.6, -42.4], [6, 4, 0], grid_plane(WHISKERS, keys=WHISKER_KEYS, mirror=(s < 0))))
        m.bone(f"ear_{side}", "head", [s * 5.5, 38, -32], rotation=[-10, 0, 26 * s], cubes=[
            Cube([X(3.5, 4), 38, -33], [4, 3, 2], {"fn": ear_fn}),
            Cube([X(4, 3), 41, -32.6], [3, 1, 1], {"fn": ear_fn})])
    # mane of golden flames rising from the head and streaming back
    m.bone("mane_head", "head", [0, 38.5, -33], cubes=[
        Cube([-3, 38, -33], [6, 2, 4], GOLD)] + [
        Cube([xo, 38.2, -37], [0, h, 14], flame(-37, 14, 38.2, h, n=4, seed=21 + k, lean=0.7, width=1.35),
             rotation=[0, 0, rz], pivot=[xo, 38.2, -31])
        for k, (xo, h, rz) in enumerate(((0, 15, 0), (2.4, 13, 14), (-2.4, 13, -14), (4.6, 10, 30), (-4.6, 10, -30)))])
    m.bone("mane_crest", "head", [0, 38.5, -30], rotation=[-25, 0, 0], cubes=[
        Cube([-7, 37.5, -30], [14, 13, 0], flame(-7, 14, 37.5, 13, n=5, seed=24, axis="x", lean=0.0, width=1.35)),
        Cube([-5.5, 37.5, -27.5], [11, 11, 0], flame(-5.5, 11, 37.5, 11, n=4, seed=25, axis="x", lean=0.0, width=1.35))])
    # floating crown of lightning bolts on a ring of light
    CY = 59                                                                    # well above the mane
    m.bone("crown", "head", [0, CY, -33], rotation=[-10, 0, 0])               # tilt, bob
    m.bone("crown_spin", "crown", [0, CY, -33])                                # turns round its axis
    m.bone("crown_ring", "crown_spin", [0, CY, -33], cubes=[
        Cube([-8.5, CY, -41.5], [17, 0, 17], ring()), Cube([-7.5, CY + 0.6, -40.5], [15, 0, 15], ring())])
    for k, (phi, w, h, gem) in enumerate(((0, 7, 14, True), (72, 6, 11, False), (144, 5, 9, False), (-144, 5, 9, False),
                                          (-72, 6, 11, False))):
        px_, pz_ = 7.4 * math.sin(math.radians(phi)), -33 - 7.4 * math.cos(math.radians(phi))
        m.bone(f"crown_spike{k + 1}", "crown_spin", [px_, CY, pz_], cubes=[
            Cube([px_ - w / 2, CY, pz_], [w, h, 0], bolt(SPIKE, edge="flame", gem=gem, up=False), rotation=[-10, -phi, 0],
                 pivot=[px_, CY, pz_])])

    # ---------------------------------------------------------------- tail: hangs, then sweeps up into a curling plume
    segs = (("tail", "torso", 19, 9, -30, 0, 0), ("tail2", "tail", 28, 8, 12, 4, 9),
            ("tail3", "tail2", 36, 8, 32, 9, 15), ("tail4", "tail3", 44, 8, 38, 15, 21),
            ("tail5", "tail4", 52, 8, 40, 21, 27), ("tail6", "tail5", 60, 8, 46, 27, 25))
    for k, (name, par, z0, L, rx, h0, h1) in enumerate(segs):
        y0 = 31.5
        w = 3 if k < 3 else 2
        m.bone(name, par, [0, y0, z0], rotation=[rx, 0, 0],
               cubes=[Cube([-w / 2, y0 - w / 2, z0], [w, w, L + 1], COAT if k == 0 else GOLD)])
        if h1:                                   # the flame plume is its own bone (laid flat when it lies down)
            H = max(h0, h1)
            tip = 0.9 if k == len(segs) - 1 else 0.0
            ext = round(L * tip)
            Hd = round(H * 0.85)
            m.bone(f"plume{k + 1}", name, [0, y0, z0], cubes=[
                Cube([0, y0 - H / 2 - 0.5, z0 - 1], [0, H + 1, L + 3 + ext], plume(z0 - 1, L + 2, y0, h0, h1, seed=k, tip=tip)),
                Cube([-H * 0.4 - 0.5, y0, z0 - 1], [round(H * 0.8) + 1, 0, L + 3 + ext],
                     plume(z0 - 1, L + 2, 0, h0 * 0.8, h1 * 0.8, seed=k + 9, axis="x", tip=tip))] + [
                Cube([0, y0 - Hd / 2 - 0.5, z0 - 0.5], [0, Hd + 1, L + 2 + ext],
                     plume(z0 - 0.5, L + 1.5, y0, h0 * 0.85, h1 * 0.85, seed=k + 20 + j, tip=tip),
                     rotation=[0, 0, rz], pivot=[0, y0, z0]) for j, rz in enumerate((45, -45))])

    # ---------------------------------------------------------------- crackling lightning arcs (they flicker)
    arc = lambda up: bolt(body="spark_core", edge="spark", up=up)
    m.bone("spark_left", "chest", [8, 31, -16], cubes=[
        Cube([8.2, 23, -24], [0, 15, 11], arc(False), rotation=[0, 0, -10], pivot=[8.2, 31, -16])])
    m.bone("spark_right", "chest", [-8, 31, -16], cubes=[
        Cube([-8.2, 25, -23], [0, 12, 9], arc(False), rotation=[0, 0, 10], pivot=[-8.2, 31, -16])])
    m.bone("spark_hip", "torso", [-8, 28, 14], cubes=[Cube([-8.3, 22, 8], [0, 11, 9], arc(True))])
    m.bone("spark_tail", "tail3", [0, 31.5, 40], cubes=[
        Cube([-4, 35, 37], [8, 10, 0], arc(True), rotation=[0, 30, 0], pivot=[0, 35, 40])])
    m.pack()
    return m

# ============================================================================ animations
Q = "q.anim_time"

CROWN_SPIKES = tuple(f"crown_spike{k + 1}" for k in range(5))

def fx(period=8.0, turns=1, spark=-4.6, crown_y=0.0, flare=0.0, speed=None):
    """Living crown and flames (Molang; every period divides the loop so it never jumps):
    the crown bobs and wobbles and turns `turns` times per loop (0 = sways), its rings turn the other way and
    pulse, its five spikes rise and fall in a wave running round it; the mane flickers (and flares by `flare`);
    the lightning arcs crackle on and off."""
    fb = round(360 / period, 3)
    speed = speed or 8.0 / period
    out = {"crown": {"position": [0, f"{crown_y}+math.sin({Q}*{fb})*0.8", 0],
                     "rotation": [f"math.sin({Q}*{fb}+90)*3", 0, f"math.sin({Q}*{fb}+40)*2"]},
           "crown_spin": {"rotation": [0, f"{Q}*{round(fb * turns, 3)}" if turns else f"math.sin({Q}*{fb})*14", 0]},
           "crown_ring": {"rotation": [0, f"-{Q}*{round(fb * 2 * max(turns, 1), 3)}", 0],
                          "scale": [f"1+math.sin({Q}*{fb * 4})*0.05", 1, f"1+math.sin({Q}*{fb * 4})*0.05"]}}
    for k, b in enumerate(CROWN_SPIKES):
        out[b] = {"position": [0, f"math.sin({Q}*{fb * 2}-{72 * k})*0.8", 0],
                  "scale": [1, f"1+math.clamp(math.sin({Q}*{fb * 2}-{72 * k}),0,1)*0.15", 1]}
    for k, b in enumerate(MANES):
        out[b] = {"rotation": [f"math.sin({Q}*{fb * 4}-{60 * k})*2.5", f"math.sin({Q}*{fb * 2}-{50 * k})*3", 0],
                  "scale": [1 + flare * 0.4, f"{1 + flare}+math.sin({Q}*{fb * 8}-{70 * k})*0.06", 1 + flare * 0.4]}
    for k, b in enumerate(SPARKS):
        f = round(540 * speed * (1 + 0.37 * k), 1)
        v = f"math.clamp(math.sin({Q}*{f}+{k * 97})*6{spark:+},0,1)"
        out[b] = {"scale": [v, v, v]}
    return out

def tail_wave(f, amp=(3, 4, 5, 6, 7, 8), lag=45, pitch=(1.5, 2, 2.5, 3, 3, 3)):
    return {tb: {"rotation": [f"math.sin({Q}*{f}-{lag * i}+60)*{pitch[i]}", f"math.sin({Q}*{f}-{lag * i})*{amp[i]}", 0]}
            for i, tb in enumerate(TAIL)}

def lie_leg(m, pose, lg, g1, g2, g3, prefer, w_mid=1.0):
    """Leg lying on the ground: grid search of absolute angles with the paw flat (a4 = 0) so that the paw and
    the middle segment (forearm / metatarsus) both rest on the ground, nothing below it, closest to `prefer`."""
    best = None
    mid = {lg.bones[1]} if lg.side.startswith("front") else {lg.bones[2]}
    for a1 in g1:
        for a2 in g2:
            for a3 in g3:
                ang = (a1, a2, a3, 0.0)
                p = dict(pose)
                for b, d in zip(lg.bones, lg.deltas(ang)):
                    p[b] = {"rotation": [d, 0, 0]}
                lo = lowest(m, p, only=set(lg.bones))
                if lo < -0.05:
                    continue
                foot = lowest(m, p, only={lg.bones[3]})
                mid_lo = lowest(m, p, only=mid)
                sc = abs(foot - 0.05) + w_mid * abs(mid_lo - 0.3) + 0.004 * sum(abs(x - y) for x, y in zip(ang[:3], prefer))
                if best is None or sc < best[0]:
                    best = (sc, ang)
    for b, d in zip(lg.bones, lg.deltas(best[1])):
        pose[b] = {"rotation": [d, 0, 0]}
    return best[1]

def sphinx(m, trunk, skip):
    """Lying like a sphinx: belly down, forelegs stretched out in front with the paws flat, hind legs folded along
    the flanks, chin resting on the forepaws."""
    pose = {"body": {"rotation": [0, 0, 0], "position": [0, 0, 0]}}
    pose["body"]["position"][1] = -lowest(m, pose, only=trunk) + 0.05
    for lg in LEGS:
        if lg.side.startswith("front"):
            ang = lie_leg(m, pose, lg, rng(0, 90, 19), rng(-110, -70, 9), rng(-110, -70, 5), (40, -90, -90))
        else:
            ang = lie_leg(m, pose, lg, rng(-120, -40, 17), rng(40, 170, 14), rng(-110, -60, 6), (-85, 110, -88), w_mid=0.6)
        pose[f"flame_{lg.side}"] = {"rotation": [round(-(ang[2] - lg.a[2]), 2), 0, 0]}   # flames keep rising
    legs_lo = lowest(m, pose, only={b for lg in LEGS for b in lg.bones})
    if legs_lo < 0:
        pose["body"]["position"][1] += -legs_lo + 0.02
    head_grp = descendants(m, "head") - set(skip)
    best = None
    for nx in rng(-10, 60, 29):
        for hx in rng(-30, 40, 15):
            p = copy_pose(pose)
            p["neck"] = {"rotation": [nx, 0, 0]}
            p["head"] = {"rotation": [hx, 0, 0]}
            lo = lowest(m, p, only=head_grp)
            if lo < 0:
                continue
            sc = abs(lo - 3.2) + 0.01 * abs(hx)
            if best is None or sc < best[0]:
                best = (sc, nx, hx)
    _, nx, hx = best
    pose["neck"] = {"rotation": [nx, 0, 0]}
    pose["head"] = {"rotation": [hx, 0, 3]}
    return pose

def faint(m, trunk, skip, L=3.0):
    """Knock-out: recoils, staggers, the forelegs buckle, it sinks on its belly, then rolls onto its flank, the long
    tail lying flat behind it; the crown flickers out and drops, the flames die down."""
    from bovine import kneel_pose, sternal, lateral, merge
    from biped import pose_sequence
    k0 = stance(LEGS, 0, 0, PIVOT)
    k1 = merge(stance(LEGS, -3, 0.25, PIVOT), {"neck": {"rotation": [-12, 0, 0]}, "head": {"rotation": [-10, 0, 0]},
                                                "jaw": {"rotation": [14, 0, 0]}})
    k2 = merge(stance(LEGS, 1.5, -0.6, PIVOT, body_rot=[0, 0, 5]),
               {"neck": {"rotation": [10, -8, 0]}, "head": {"rotation": [6, 0, 10]}, "jaw": {"rotation": [6, 0, 0]}})
    k3 = merge(kneel_pose(m, LEGS, PIVOT), {"neck": {"rotation": [14, 4, 0]}, "head": {"rotation": [8, 0, -6]}})
    k4 = merge(sternal(m, LEGS, trunk, lean=4), {"neck": {"rotation": [24, 0, 0]}, "head": {"rotation": [10, 0, 0]}})
    k5 = lateral(m, LEGS, trunk, skip=skip)
    flat = [-8, -10, -22, -26, -28, -30]                 # uncurl the tail so it lies along the ground
    for k, ev in ((k1, 0), (k2, 0.2), (k3, 0.5), (k5, 1)):
        for i, tb in enumerate(TAIL):
            k[tb] = {"rotation": [flat[i] * ev, 0, 0]}
    lay_tail(m, k4, TAIL, yaw=(30, 20, 15, 12, 10, 10), target=2.6, skip=skip)
    for k, ev in ((k1, 0), (k2, 0.2), (k3, 0.5), (k4, 0.8), (k5, 1)):
        for side, sg in SIDES:
            k[f"ear_{side}"] = {"rotation": [-10 * ev, 0, 24 * sg * ev]}
        for pb in PLUMES:
            k[pb] = {"rotation": [0, 0, 90 if k is k4 else 0]}
    k5b = copy_pose(k5)
    k5b["jaw"] = {"rotation": [10, 0, 0]}
    seq = [(0, k0), (0.3, k1), (0.7, k2), (1.15, k3), (1.6, k4), (2.1, k5), (2.6, k5b), (L, k5)]
    bones = pose_sequence(m, seq, length=L, skip=tuple(skip) + TAIL)
    for pb in PLUMES:
        bones[pb]["scale"] = keys(scale={0: [1, 1, 1], 1.15: [1, 1, 1], 1.6: [0.3, 0.9, 1], 2.1: [0.5, 0.8, 0.8],
                                         L: [0.5, 0.7, 0.8]})["scale"]
    for e in EYES:
        bones[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.6, 1], 0.7: [1, 1, 1], 1.4: [1, 1, 1], 1.65: [1, 0.1, 1], L: [1, 0.1, 1]})
    bones["crown"] = keys(position={0: [0, 0, 0], 0.6: [0, 1.5, 0], 2.1: [0, -3, 0], L: [0, -3.5, 0]},
                          scale={0: [1, 1, 1], 1.6: [0.9, 0.9, 0.9], 2.4: [0.4, 0.4, 0.4], L: [0, 0, 0]})
    bones["crown_spin"] = keys(rotation={0: [0, 0, 0], 1.0: [0, 150, 0], 2.0: [0, 230, 0], L: [0, 260, 0]})
    for k, sb_ in enumerate(CROWN_SPIKES):
        bones[sb_] = keys(position={0: [0, 0, 0], 0.6: [0, 1.0, 0], 1.8: [0, -1.2 - 0.3 * k, 0], L: [0, -1.5, 0]})
    for bname in MANES:
        bones[bname] = keys(scale={0: [1, 1, 1], 1.0: [1, 1.1, 1], 2.6: [0.6, 0.3, 0.6], L: [0.5, 0.25, 0.5]})
    for bname in SPARKS:
        bones[bname] = keys(scale={0: [1, 1, 1], 0.4: [0, 0, 0], L: [0, 0, 0]})
    return {"animation_length": L, "bones": bones}

def roar(L=2.4):
    """Cry: a deep breath, then it lifts its head and roars, jaws wide, mane flaring, the crown flashing up and
    every arc crackling; a forepaw grips the ground."""
    def pose(t):
        up = lerp_keys([(0, 0), (0.35, -0.3), (0.65, 1), (1.85, 1), (2.4, 0)], t)
        jaw = lerp_keys([(0, 0), (0.55, 0), (0.75, 36), (1.75, 32), (2.15, 0)], t)
        sh = math.sin(t * 70) * (1 if 0.75 < t < 1.75 else 0)
        p = stance(LEGS, -5 * max(0.0, up), -0.3 * up, PIVOT)
        p["chest"] = {"position": [0, 0.15 * up, 0]}
        p["neck"] = {"rotation": [-14 * up, 0, 0]}
        p["head"] = {"rotation": [-12 * up + 1.2 * sh, 0, 0]}
        p["jaw"] = {"rotation": [jaw + 1.5 * sh, 0, 0]}
        for i, tb in enumerate(TAIL):
            p[tb] = {"rotation": [8 * up if i == 0 else 4 * up, 10 * up * math.sin(t * 5 - 0.7 * i), 0]}
        for side, s in SIDES:
            p[f"ear_{side}"] = {"rotation": [-20 * max(0.0, up), 0, 22 * s * max(0.0, up)]}
        e = max(0.0, up)
        for k, b in enumerate(MANES):
            p[b] = {"rotation": [-8 * e, 0, 0], "scale": [1 + 0.15 * e, 1 + 0.35 * e + 0.05 * sh, 1 + 0.15 * e]}
        p["crown"] = {"position": [0, 2.5 * e, 0], "scale": [1 + 0.15 * e] * 3, "rotation": [0, 0, 0]}
        p["crown_spin"] = {"rotation": [0, 720 * smooth(t / L), 0]}
        p["crown_ring"] = {"rotation": [0, -360 * smooth(t / L), 0], "scale": [1 + 0.25 * e, 1, 1 + 0.25 * e]}
        for k, sb_ in enumerate(CROWN_SPIKES):
            p[sb_] = {"position": [0, 1.5 * e * (1 + 0.3 * math.sin(t * 12 - 1.26 * k)), 0], "scale": [1, 1 + 0.25 * e, 1]}
        for side, sg in SIDES:
            p[f"brow_{side}"] = {"rotation": [0, 0, -10 * sg * e], "position": [0, -0.3 * e, 0]}
        for k, b in enumerate(SPARKS):
            v = 1.0 if (0.7 < t < 1.8 and math.sin(t * 40 + 1.9 * k) > -0.6) else 0.0
            p[b] = {"scale": [v, v, v]}
        return p
    return {"animation_length": L, "bones": sampled(L, 0.05, pose)}

def anims(m=None):
    m = m or build()
    a = f"animation.{SID}."
    out = {}
    names = {b.name for b in m.bones}
    skip = {n for n in names if n.startswith(("crown", "mane", "spark", "plume", "flame"))}
    trunk = {"torso", "chest"} | {b for t in ("torso", "chest") for b in descendants(m, t)
                                   if not b.startswith(("neck", "head", "ear", "eye", "jaw", "tail", "mane", "crown", "spark",
                                                        "plume", "flame"))}
    trunk -= skip

    # ---------------------------------------------------------------- idle: regal stance, slow breathing, tail swaying
    idle = {"torso": {"rotation": [f"math.sin({Q}*45)*0.5", 0, 0]},
            "chest": {"position": [0, f"math.sin({Q}*45-30)*0.1", 0]},
            "neck": {"rotation": [f"math.sin({Q}*45)*1.2", f"math.sin({Q}*22.5-30)*4", 0]},
            "head": {"rotation": [f"math.sin({Q}*45+60)*1.5", f"math.sin({Q}*22.5-70)*7", f"math.sin({Q}*45-100)*1.5"]},
            "jaw": {"rotation": [f"math.clamp(math.sin({Q}*45-60)*3-2,0,1)*3", 0, 0]}}
    for (ear, s), t0 in zip(zip(EARS, (1, -1)), (2.2, 5.6)):
        idle[ear] = keys(rotation={0: [0, 0, 0], t0 - 0.1: [0, 0, 0], t0: [8, 18 * s, 6 * s], t0 + 0.14: [-2, -5 * s, 0],
                                   t0 + 0.3: [4, 9 * s, 3 * s], t0 + 0.45: [0, 0, 0], 8: [0, 0, 0]})
    idle.update(tail_wave(45))
    idle["tail6"] = {"rotation": [f"math.sin({Q}*45-225)*4+math.clamp(math.sin({Q}*90+20)*4-3,0,1)*10",
                                  f"math.sin({Q}*45-180)*9", 0]}
    idle.update(fx(8.0, 1))
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": idle}

    # ---------------------------------------------------------------- walk: smooth prowl, head level, tail swinging
    T = 1.4
    f = round(360 / T, 3)
    ex = tail_wave(f, amp=(4, 5, 6, 7, 8, 9), lag=50)
    ex["jaw"] = {"rotation": [0, 0, 0]}
    for ear, s in zip(EARS, (1, -1)):
        ex[ear] = {"rotation": [0, 0, f"math.sin({Q}*{2 * f}+{90 if s > 0 else 0})*{2 * s}"]}
    ex.update(fx(T, 0, speed=2.0))
    out[a + "ground_walk"] = walk(LEGS, phases=GAIT, T=T, stride=13, lift=3.8, stance=0.62, bob=0.55, samples=32,
                                  toe_off=25, fold=30, curl=35, torso=(0.6, 2.2, 1.6), tail=(), neck=True, arms=(), extra=ex)

    # ---------------------------------------------------------------- battle: the sovereign stands its ground
    # Square stance, one forepaw forward, weight on the shoulders, head lowered a little and perfectly steady, a
    # fixed glare under frowning brows (narrowed eyes), ears up, a low growl, the tail held low and still but for
    # the tip; the mane flares and the crown turns faster.
    def battle_pose(t):
        w = math.sin(2 * math.pi * t / 4)
        growl = lerp_keys([(0, 0), (2.1, 0), (2.4, 1), (3.1, 1), (3.5, 0), (4, 0)], t)
        p = stance(LEGS, 1.4 + 0.25 * w, -0.9 + 0.12 * w, PIVOT, feet={"front_right": (-2.5, 0.0, None, 0.0)})
        p["chest"] = {"position": [0, 0.08 * w, 0]}
        p["neck"] = {"rotation": [7 + 0.6 * w, 0, 0]}
        trem = math.sin(t * 55) * 0.5 * growl
        p["head"] = {"rotation": [-5 - 0.6 * w + trem, 0, 0]}
        p["jaw"] = {"rotation": [1.5 + 4 * growl, 0, 0]}
        twitch = math.exp(-((t - 1.0) / 0.08) ** 2)
        for side, sg in SIDES:
            p[f"ear_{side}"] = {"rotation": [-6 - 4 * growl, 6 * sg * twitch, 6 * sg]}
            p[f"brow_{side}"] = {"rotation": [0, 0, -9 * sg], "position": [0, -0.35, 0]}
            p[f"eye_{side}"] = {"scale": [1, 0.72, 1]}
        flick = math.exp(-((t - 3.0) / 0.18) ** 2)
        for i, tb in enumerate(TAIL):
            sway = (1.5 + 0.8 * i) * math.sin(2 * math.pi * t / 4 - 0.5 * i)
            p[tb] = {"rotation": [-8 if i == 0 else (-4 if i < 3 else 0), sway + (14 * flick if i >= 4 else 0), 0]}
        return p
    b = sampled(4, 0.1, battle_pose, loop=True)
    b.update(fx(4.0, 1, spark=-3.2, flare=0.15))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": b}

    # ---------------------------------------------------------------- cry
    out[a + "cry"] = roar()

    # ---------------------------------------------------------------- sleep: sphinx pose, tail curled round
    sp = sphinx(m, trunk, skip)
    lay_tail(m, sp, TAIL, yaw=(50, 30, 25, 22, 20, 20), target=2.6, skip=skip)
    sb = {k: dict(v) for k, v in sp.items()}
    for pb in PLUMES:                            # plume planes rolled flat on the ground beside it
        sb[pb] = {"rotation": [0, 0, 90], "scale": [0.3, 0.9, 1]}
    sb["torso"] = {"rotation": [f"math.sin({Q}*45)*0.6", 0, 0]}
    sb["chest"] = {"position": [0, f"0.06+math.sin({Q}*45-20)*0.08", 0]}
    for ear, s in zip(EARS, (1, -1)):
        sb[ear] = {"rotation": [10, 0, 20 * s]}
    for e in EYES:
        sb[e] = {"scale": [1, 0.1, 1]}
    sb["jaw"] = {"rotation": [0, 0, 0]}
    sb.update(fx(8.0, 1, spark=-5.8, crown_y=-6.0, speed=0.5))
    for side, sg in SIDES:
        sb[f"brow_{side}"] = {"rotation": [0, 0, 8 * sg], "position": [0, -0.2, 0]}       # relaxed
    for bname in MANES:
        sb[bname]["scale"] = [0.8, f"0.7+math.sin({Q}*90)*0.04", 0.8]
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sb}

    # ---------------------------------------------------------------- knock-out: collapses on its flank, crown fades
    out[a + "faint"] = faint(m, trunk, skip)

    out[a + "blink"] = {"animation_length": 0.2, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.1, 1], "0.2": [1, 1, 1]}} for e in EYES}}

    # ---------------------------------------------------------------- ridden: calm idle, bounding gallop, pounce
    out[a + "mount_ground_idle"] = {"loop": True, "animation_length": 8,
                                    "bones": {k: v for k, v in idle.items() if k != "jaw"}}
    RT = 0.56
    rf = round(360 / RT, 3)
    ex = {"jaw": {"rotation": [f"2+math.sin({Q}*{rf})*1.5", 0, 0]},
          "neck": {"rotation": [f"6+math.sin({Q}*{rf}+60)*3", 0, 0]},
          "head": {"rotation": [f"-6-math.sin({Q}*{rf}+90)*3", 0, 0]}}
    stream = (24, -6, -14, -16, -18, -20)            # the tail streams out behind, its curl loosened
    for i, tb in enumerate(TAIL):
        ex[tb] = {"rotation": [f"{stream[i]}+math.sin({Q}*{rf}-{50 * i})*{2 + i}", f"math.sin({Q}*{rf / 2:.3f}-{40 * i})*{2 + i}", 0]}
    for side, sg in SIDES:
        ex[f"ear_{side}"] = {"rotation": [-18, 0, 14 * sg]}
    ex.update(fx(RT, 0, spark=-3.0, flare=0.12, speed=3.0))
    out[a + "ground_run"] = walk(LEGS, T=RT, stride=19, lift=5.5, stance=0.34, bob=1.0, samples=32, toe_off=30, fold=70,
                                 curl=55, phases={"back_left": 0.0, "back_right": 0.08, "front_left": 0.5, "front_right": 0.58},
                                 torso=(4.5, 1.0, 1.0), tail=(), neck=True, arms=(), extra=ex)
    jump = {"body": {"rotation": [-7, 0, 0], "position": [0, 1.2, 0]},
            "neck": {"rotation": [4, 0, 0]}, "head": {"rotation": [-4, 0, 0]}, "jaw": {"rotation": [4, 0, 0]}}
    for lg in LEGS:                                  # a pounce: forelegs reaching forward, hind legs stretched back
        ang = (-55, -75, -70, -60) if lg.side.startswith("front") else (45, 80, 70, 60)
        for bn, d in zip(lg.bones, lg.deltas(ang)):
            jump[bn] = {"rotation": [d, 0, 0]}
    for i, tb in enumerate(TAIL):
        jump[tb] = {"rotation": [stream[i] + 4, f"math.sin({Q}*{rf}-{40 * i})*{2 + i}", 0]}
    for side, sg in SIDES:
        jump[f"ear_{side}"] = {"rotation": [-20, 0, 16 * sg]}
    jump.update(fx(RT, 0, spark=-2.5, flare=0.15, speed=3.0))
    out[a + "ride_jump"] = {"loop": True, "animation_length": RT, "bones": jump}
    return finalize(out)

def poser():
    from templates import land_mount_poses
    ps = bovine_poser(SID, portrait=(1.0, [-0.6, 1.5, 0]), profile=(0.5, [0, 1.0, 0]), graze_quirk=False)
    return land_mount_poses(ps, SID, first=(0, 0.45, 0), third=(0, 0.6, 0.5))
