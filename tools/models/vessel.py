# -*- coding: utf-8 -*-
"""Materials and helpers for the Bolvados line (cider bowl -> stoneware jug -> copper still with a fire spirit).

Painters work in model space (fn3) where a pattern must run continuously over several cubes (painted bands on a
stoneware belly, glaze drips, copper rivet rows), else per face. Glowing parts (warm cider, the vapour spirit, the
fire spirit, ember eyes) are emissive: their frames are painted again with another seed, so they shimmer in game."""
import math
from modelgen import Cube, fill, shade, mix, FACE_LIGHT, apply
from bovine import vnoise, light, put, side_cols

# ============================================================================ stoneware / clay
def stoneware(*, base="clay", dark="clay_dark", light_key="clay_light", glaze=None, drip_y=None, motif=None, seed=1,
              grog=0.08):
    """Thrown stoneware (fn3): warm clay with grog specks and faint throwing rings; optional glaze ('key') above
    drip_y with runs dripping down; motif(p, face) -> palette key for painted decoration (wins over everything)."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.12)
            k = motif(p, face) if motif else None
            if k:
                put(px, X, Y, pal[k], f, rnd, 2)
                continue
            col = pal[base]
            ring = (p[1] * 2.0) % 2.0
            if face in ("north", "south", "east", "west") and ring < 0.35:
                col = mix(col, pal[dark], 0.25)                       # throwing rings
            if glaze and drip_y is not None:
                run = drip_y - 2.5 * max(0.0, vnoise(p[0] * 0.9 + p[2] * 0.9, 1.0, 0.0, seed + 5) - 0.45) * 2.2
                if p[1] > run or face == "up":
                    col = mix(pal[glaze], pal[glaze + "_light"], 0.25 * (1 if (X + Y) % 5 == 0 else 0))
            if rnd.random() < grog:
                col = mix(col, pal[dark if rnd.random() < 0.6 else light_key], 0.6)
            put(px, X, Y, col, f, rnd, 3)
    return {"fn3": fn3}

def band_motif(y0, y1, *, wave="blue", dot="blue", period=6.0, amp=1.0, dots=True, sides=("north", "south", "east", "west")):
    """Hand-painted faience-style decoration between y0 and y1: framing lines, a blue wave and a dot in each
    trough, laid along each face (the wave follows the face's horizontal coordinate, so it stays clean)."""
    def motif(p, face):
        if face not in sides:
            return None
        h = p[0] if face in ("north", "south") else p[2]
        u = 2 * math.pi * h / period
        mid = (y0 + y1) / 2
        w = mid + amp * math.sin(u)
        wa = mid + amp * math.sin(2 * math.pi * (h - 0.5) / period)
        wb = mid + amp * math.sin(2 * math.pi * (h + 0.5) / period)
        if abs(p[1] - w) < 0.5 or min(wa, wb) - 0.5 < p[1] < max(wa, wb) + 0.5 and abs(p[1] - w) < 1.0:
            return wave                                               # continuous wave line
        if dots and abs(math.cos(u)) < 0.35 and abs(p[1] - (mid - 1.6 * amp * math.copysign(1, math.sin(u)))) < 0.5:
            return dot
        if abs(p[1] - y0) < 0.45 or abs(p[1] - y1) < 0.45:
            return wave
        return None
    return motif

# ============================================================================ liquids and spirits
def cider(*, key="cider", light_key="cider_light", dark="cider_dark", swirl=True, seed=3):
    """Warm golden cider seen from above: slow spiral swirl of lighter streaks, shimmering glints (new on every
    emissive frame)."""
    def fn3(px, faces, pal, rnd, c):
        cx = c.origin[0] + c.size[0] / 2
        cz = c.origin[2] + c.size[2] / 2
        for face, X, Y, pl in c.texels():
            col = pal[key]
            r = math.hypot(pl[0] - cx, pl[2] - cz)
            a = math.atan2(pl[2] - cz, pl[0] - cx)
            if swirl and face == "up":
                s = math.sin(a * 2 + r * 1.3)
                if s > 0.7:
                    col = mix(col, pal[light_key], 0.6)
                elif s < -0.8:
                    col = mix(col, pal[dark], 0.35)
            if face != "up":
                col = mix(col, pal[dark], 0.25)
            if rnd.random() < 0.06:
                col = pal[light_key]
            put(px, X, Y, col, 1.0, rnd, 3)
    return {"fn3": fn3}

def vapour(*, core="spirit_core", mid="spirit", edge="spirit_edge", seed=5, streaks=True, center=None, radius=None,
           fire=False):
    """Vapour / liquid-fire body (fn3). With center/radius: pillow-shaded like a glowing blob (bright heart, deeper
    colour toward the silhouette, so stacked boxes read round); without: hot core low, darker smoky rim at the cube
    edges. Sinuous rising wisps of the core colour; re-rolled on each emissive frame so it shimmers."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            fx, fy, fw, fh = faces[face]
            i, j = X - fx, Y - fy
            p = apply(c.world, pl)
            if center is not None:
                d = math.dist(p, center) / radius
                if d < 0.55:
                    col = mix(pal[core], pal[mid], d / 0.55)
                else:
                    col = mix(pal[mid], pal[edge], min(1.0, (d - 0.55) / 0.5) * 0.8)
                if face == "up":
                    col = mix(col, pal[core], 0.2)
            else:
                edge_d = min(i, j, fw - 1 - i, fh - 1 - j) if fw > 2 and fh > 2 else 1
                col = pal[mid]
                if edge_d == 0 and face not in ("up", "down"):
                    col = mix(pal[mid], pal[edge], 0.6)
                t = j / max(fh - 1, 1)                                     # 0 top .. 1 bottom
                col = mix(col, pal[core], 0.35 * t)
            if fire and face not in ("up", "down"):
                hz = p[0] if face in ("north", "south") else p[2]
                f1 = math.sin(hz * 0.9 + 1.6 * math.sin(p[1] * 0.33 + seed) + 0.6 * math.sin(p[1] * 0.9) + rnd.random() * 0.25)
                if f1 > 0.86:
                    col = mix(col, pal[core], 0.55)                   # rising tongues of brighter fire
                elif f1 < -0.92:
                    col = mix(col, pal[edge], 0.45)                   # darker smoky licks
            elif streaks:
                s = math.sin(p[0] * 1.1 + p[2] * 0.7 + 2.0 * math.sin(p[1] * 0.45 + seed) + rnd.random() * 0.5)
                if s > 0.94:
                    col = mix(col, pal[core], 0.55)
            put(px, X, Y, col, 1.0, rnd, 3)
    return {"fn3": fn3}

def steam(key="steam", light_key="steam_light", seed=0):
    """Wisp of apple-scented steam on a plane: a thin sinuous curl (cutout), thicker low, breaking up near the top."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    px[x + i, y + j] = (0, 0, 0, 0)
            if not (w and h):
                continue
            for j in range(h):
                t = 1 - j / max(h - 1, 1)                        # 1 at the top
                c = (w - 1) / 2 + math.sin(j * 0.9 + seed) * (w - 1) * 0.35
                width = 2 if (t < 0.45 and w >= 3) else 1
                if t > 0.75 and (j + seed) % 2 == 0:
                    continue                                      # breaking up at the top
                for d in range(width):
                    i = int(round(c)) + d
                    if 0 <= i < w:
                        px[x + i, y + j] = pal[light_key] if (j + d) % 3 == 0 else pal[key]
    return fn

# ============================================================================ copper
def copper(*, base="copper", dark="copper_dark", light_key="copper_light", patina="patina", rivets=None, seed=7,
           engrave=None):
    """Hammered copper (fn3): planished dimples, warm highlights on top faces, a little verdigris low down,
    rivet rows at the given heights (rivets=[y,...]) and engraved bands (engrave=[(y0, y1)])."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.18)
            n = vnoise(p[0] * 1.6, p[1] * 1.6, p[2] * 1.6, seed)
            col = mix(pal[base], pal[light_key], 0.45) if n > 0.68 else (mix(pal[base], pal[dark], 0.4) if n < 0.25 else pal[base])
            if face == "up" or (Y - fy) == 0:
                col = mix(col, pal[light_key], 0.3)
            v = vnoise(p[0] * 0.5, p[1] * 0.5 + 4, p[2] * 0.5, seed + 3)
            if v > 0.78 and p[1] < 6:
                col = mix(col, pal[patina], 0.6)
            if rivets and face in ("north", "south", "east", "west"):
                for ry in rivets:
                    if abs(p[1] - ry) < 0.5:
                        col = mix(pal[dark], col, 0.4)
                        if (X + Y) % 3 == 0:
                            col = pal[light_key]
            if engrave:
                for e0, e1 in engrave:
                    if e0 <= p[1] <= e1 and face != "up":
                        if (int(p[0] * 2) + int(p[2] * 2) + int(p[1] * 2)) % 3 == 0:
                            col = mix(col, pal[dark], 0.55)
            put(px, X, Y, col, f, rnd, 3)
    return {"fn3": fn3}

def iron(key="iron", dark="iron_dark"):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    put(px, x + i, y + j, pal[dark] if (i + j) % 4 == 0 else pal[key], FACE_LIGHT[fc], rnd, 4)
    return fn

def gauge(px, faces, pal, rnd):
    """Pressure gauge: brass ring, white dial with a red needle (front face)."""
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["brass"], FACE_LIGHT[fc], rnd, 3)
    x, y, w, h = faces["north"]
    for j in range(1, h - 1):
        for i in range(1, w - 1):
            px[x + i, y + j] = pal["dial"]
    if w >= 3 and h >= 3:
        px[x + w // 2, y + h // 2] = pal["needle"]
        px[x + w // 2 + (1 if w > 3 else 0), y + max(1, h // 2 - 1)] = pal["needle"]

# ============================================================================ faces
def char_plane(rows, keys, mirror=False):
    """Plane painted from a character grid on its north face (col 0 = viewer's left), '.' transparent."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            for j in range(h):
                row = rows[min(j, len(rows) - 1)]
                if mirror:
                    row = row[::-1]
                for i in range(w):
                    ch = row[i] if i < len(row) else "."
                    px[x + i, y + j] = (0, 0, 0, 0) if ch == "." else pal[keys[ch]]
    return fn

SWIRL7 = ["DDDDDDD",
          "DLLLLLD",
          "DLDDDLD",
          "DLDLDLD",
          "DLDLLLD",
          "DLDDDDD",
          "DLLLLLL"]

def swirl_eye(rows=SWIRL7, line="swirl", bg="swirl_bg", disc=True):
    """Big hypnotic swirl eye (a square pixel spiral on a pale disc). The plane is meant to spin on its Z axis
    (Molang), so the four corners are left transparent to keep the silhouette round while it turns."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            for j in range(h):
                for i in range(w):
                    corner = disc and (i in (0, w - 1)) and (j in (0, h - 1))
                    ch = rows[min(j, len(rows) - 1)][min(i, len(rows[0]) - 1)]
                    px[x + i, y + j] = (0, 0, 0, 0) if corner else pal[line if ch == "D" else bg]
    return fn

def crack(rows, keys=None):
    """Glowing crack on a plane (cutout): 'H' white-hot, 'O' glow, 'D' dark burnt lip; hot pixels flicker between
    frames (each emissive frame is repainted with another seed)."""
    keys = keys or {"H": "crack_hot", "O": "crack_glow", "D": "crack_edge"}
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            for j in range(h):
                row = rows[min(j, len(rows) - 1)]
                for i in range(w):
                    ch = row[i] if i < len(row) else "."
                    if ch == ".":
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    if ch in "HO" and rnd.random() < 0.3:
                        ch = "O" if ch == "H" else "H"
                    px[x + i, y + j] = pal[keys[ch]]
    return fn

EYE_K = {"W": "eye_white", "B": "eye_iris", "L": "eye_iris_light", "E": "eye", "S": "eye_shine", "R": "eye_ring",
         "M": "mouth", "T": "tooth", "H": "eye_hot", "O": "eye_glow", "D": "eye_dark", "Q": "mouth_glow",
         "C": "clay", "K": "clay_dark"}

def with_faces(paint, overrides, noise=3):
    """Run a paint's painter, then flood given faces with a palette key ({'up': 'mouth_glow'}) - the inside of a
    mouth on the top of a jaw, say."""
    def fn3(px, faces, pal, rnd, c):
        if "fn3" in paint:
            paint["fn3"](px, faces, pal, rnd, c)
        for face, key in overrides.items():
            x, y, w, h = faces[face]
            for j in range(h):
                for i in range(w):
                    put(px, x + i, y + j, pal[key], 1.0, rnd, noise)
    out = {k: v for k, v in paint.items() if k != "fn3"}
    out["fn3"] = fn3
    return out

def octo(y0, h, r, paint, cz=0.0):
    """One octagonal layer of a round vessel (a ring of radius r): two crossed boxes plus a diagonal one, so a stack
    of layers reads as a sphere / dome."""
    w = round(r * 0.68 * 2) / 2
    d = round(r * 0.86 * 2) / 2
    return [Cube([-r, y0, cz - w], [2 * r, h, 2 * w], paint), Cube([-w, y0, cz - r], [2 * w, h, 2 * r], paint),
            Cube([-d, y0, cz - d], [2 * d, h, 2 * d], paint)]

# ============================================================================ levitation
def bob(t, h, amp=0.7, period=2.0, phase=0.0):
    """Height of a levitating body at time t: hovering h above the ground with a slow bob (period must divide the
    animation length so loops stay seamless)."""
    return h + amp * math.sin(2 * math.pi * t / period + phase)

def lifted(fn, f, bone="body"):
    """Wraps a pose function: adds f(t) to the bone's height (levitation)."""
    def g(t):
        p = fn(t)
        b = p.setdefault(bone, {})
        pos = list(b.get("position", [0, 0, 0]))
        pos[1] += f(t)
        b["position"] = pos
        return p
    return g

def lift_track(bones, f, bone="body"):
    """Adds f(t) to the height of an already keyed bone (e.g. a pose_sequence faint that starts in the air and
    sinks to the ground)."""
    ch = bones.setdefault(bone, {}).setdefault("position", {"0.0": [0, 0, 0]})
    for k, v in list(ch.items()):
        val = v["post"] if isinstance(v, dict) else v
        val = list(val)
        val[1] = round(val[1] + f(float(k)), 4)
        if isinstance(v, dict):
            v["post"] = val
        else:
            ch[k] = val
    return bones

# ============================================================================ animation helper
def settled(m, fn, skip=(), clearance=0.0):
    """Wraps a pose function so nothing goes through the ground: when the lowest solid point dips below 0 (a tilted
    pot rocking on its foot), the body is raised just enough. Airborne poses are left alone."""
    from biped import lowest
    names = {b.name for b in m.bones}
    sk = {n for n in names if n.startswith(tuple(skip))}
    def g(t):
        p = fn(t)
        lo = lowest(m, {k: v for k, v in p.items() if "scale" not in v or k == "body"}, skip=sk)
        if lo < clearance:
            b = p.setdefault("body", {})
            pos = list(b.get("position", [0, 0, 0]))
            pos[1] += clearance - lo
            b["position"] = pos
        return p
    return g
