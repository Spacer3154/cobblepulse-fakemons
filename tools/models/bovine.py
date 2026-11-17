# -*- coding: utf-8 -*-
"""Bovine rig for the Meuhgousse line (calf, marsh bull, sacred Normande cow).

Four hoofed legs with inverse kinematics (biped.Leg): hind legs = femur forward / tibia back (hock) / cannon,
forelegs = humerus back (elbow, bend=-1) / forearm / cannon; the hoof is the foot bone. Leg motion is baked into
catmull-rom keyframes so hooves really stay planted; the upper body uses Molang.

Gait: 4-beat lateral-sequence walk of cattle (left hind, left fore, right hind, right fore), ~68 % stance.
Coat: Normande patches painted in model space (metaballs + noise, brindled streaks), so they run continuously over
cubes and faces; 'lunettes' (dark eye patches) of the breed; optional silt soaking the lower body."""
import math
from modelgen import Cube, fill, shade, mix, FACE_LIGHT, apply
from biped import Leg, walk, keys, kf, smooth, lowest, descendants, pose_sequence, search

GAIT = {"back_left": 0.0, "front_left": 0.75, "back_right": 0.5, "front_right": 0.25}
SIDES = (("left", 1), ("right", -1))

# ============================================================================ noise / coat painting
def _hash(ix, iy, iz, seed):
    n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    n &= 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0

def vnoise(x, y, z, seed=0):
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = smooth(x - ix), smooth(y - iy), smooth(z - iz)
    def L(a, b, t):
        return a + (b - a) * t
    v = [[[_hash(ix + i, iy + j, iz + k, seed) for k in (0, 1)] for j in (0, 1)] for i in (0, 1)]
    return L(L(L(v[0][0][0], v[0][0][1], fz), L(v[0][1][0], v[0][1][1], fz), fy),
             L(L(v[1][0][0], v[1][0][1], fz), L(v[1][1][0], v[1][1][1], fz), fy), fx)

def field(blobs, p, warp, seed):
    """Metaball field of ellipsoid blobs (cx, cy, cz, rx, ry, rz), with a noisy (warped) edge."""
    x, y, z = p
    if warp:
        x += (vnoise(x * 0.4, y * 0.4, z * 0.4, seed) - 0.5) * 2 * warp
        y += (vnoise(x * 0.4 + 5, y * 0.4, z * 0.4, seed + 1) - 0.5) * 2 * warp
        z += (vnoise(x * 0.4, y * 0.4 + 9, z * 0.4, seed + 2) - 0.5) * 2 * warp
    f = 0.0
    for cx, cy, cz, rx, ry, rz in blobs:
        d2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
        f += 1.0 / max(d2, 1e-4) ** 1.5
    return f

def light(face, j, h, grad=0.12):
    t = (j / max(h - 1, 1)) if h > 1 else 0
    g = grad if face in ("north", "south", "east", "west") else 0
    return FACE_LIGHT[face] * (1 + g / 2 - g * t)

def put(px, X, Y, col, f, rnd, noise=4):
    c = shade(col, f)
    if noise:
        k = rnd.randint(-noise, noise)
        c = tuple(max(0, min(255, v + k)) for v in c[:3]) + (c[3],)
    px[X, Y] = c

def coat(blobs=(), *, lunettes=(), base="coat", patch="patch", brindle="brindle", lunette="lunette", mud=None,
         space="world", warp=0.9, seed=3, streak=0.64, extra=None, **paint):
    """Paint dict for a coat cube. blobs: Normande patches; lunettes: eye patches (painted on top);
    mud = dict(y=, key=, dark=, wet=): silt soaking everything below y (ragged line, darker low, wet band above);
    extra(p, face, key) -> key: species hook. space='world' uses rest-pose world positions, 'local' raw cube
    coordinates (heads: patches placed relative to the eyes as modelled)."""
    def fn3(px, faces, pal, rnd, c):
        grid = {}
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl) if space == "world" else pl
            key = None
            if blobs and field(blobs, p, warp, seed) > 1:
                s = vnoise(p[0] * 0.55 + 7, p[1] * 0.17, p[2] * 0.85, seed + 11)
                key = brindle if s > streak else patch
            if lunettes and field(lunettes, p, warp * 0.3, seed + 3) > 1:
                key = lunette
            if extra:
                key = extra(p, face, key)
            grid[(X, Y)] = [face, p, key]
        # clean-up: drop lone patch texels, fill pinholes (keeps patches readable at 16 px / block)
        for (X, Y), cell in grid.items():
            nb = [grid.get((X + dx, Y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            nb = [n for n in nb if n and n[0] == cell[0]]
            same = sum(1 for n in nb if (n[2] is None) == (cell[2] is None))
            if len(nb) >= 2 and same == 0:
                others = [n[2] for n in nb if n[2]]
                cell.append(others[0] if (cell[2] is None and others) else None)
            else:
                cell.append(cell[2])
        for (X, Y), (face, p, _, key) in grid.items():
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, paint.get("gradient", 0.12))
            if mud:
                edge = mud["y"] + (vnoise(p[0] * 0.8, 3.3, p[2] * 0.8, seed + 21) - 0.5) * mud.get("rag", 2.2)
                if p[1] < edge:
                    t = max(0.0, min(1.0, (edge - p[1]) / max(mud["y"], 1) * 1.6 + (rnd.random() - 0.5) * 0.5))
                    c = mix(pal[mud["key"]], pal[mud["dark"]], t)
                    if face == "down" and vnoise(p[0] * 0.7, 1.7, p[2] * 0.7, seed + 31) > 0.55:
                        c = mix(pal[key or base], pal[mud["wet"]], 0.6)        # matted wet hair between clods
                    put(px, X, Y, c, f, rnd, 5)
                    continue
                if p[1] < edge + mud.get("wet_h", 1.5) and face not in ("up",):
                    cur = pal[key or base]
                    put(px, X, Y, mix(cur, pal[mud["wet"]], 0.45), f, rnd, 3)
                    continue
            if key:
                put(px, X, Y, pal[key], f, rnd, 4)
    d = {"base": base, "fn3": fn3}
    d.update(paint)
    return d

# ============================================================================ part painters
def foam(px, faces, pal, rnd):
    """Sea foam: clustered white bubbles with pale aqua shadows, a few bubble rings on larger faces."""
    for fc, (x, y, w, h) in faces.items():
        f = 1 + (FACE_LIGHT[fc] - 1) * 0.5
        for j in range(h):
            for i in range(w):
                r = rnd.random()
                key = "foam_light" if r < 0.2 else "foam_shade" if r < 0.45 else "foam"
                put(px, x + i, y + j, pal[key], f, rnd, 3)
        if w >= 3 and h >= 3:
            for _ in range(max(1, (w * h) // 12)):
                ci, cj = rnd.randint(1, w - 2), rnd.randint(1, h - 2)
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    px[x + ci + di, y + cj + dj] = shade(pal["foam_deep"], f)
                px[x + ci, y + cj] = pal["foam_light"]

def hoof(px, faces, pal, rnd):
    """Cloven hoof: dark horn, cleft down the front, lighter coronet band on top."""
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["hoof"], FACE_LIGHT[fc], rnd, 3)
        if fc in ("north", "south", "east", "west") and h > 1:
            for i in range(w):
                px[x + i, y] = shade(pal["hoof_light"], FACE_LIGHT[fc])
    for fc in ("north", "up", "down"):
        x, y, w, h = faces[fc]
        if w >= 3 and w % 2:
            for j in range(h):
                px[x + w // 2, y + j] = pal["hoof_dark"]

def side_cols(fc, w):
    """Column order from the FRONT (-Z) for a side face (east: col 0 = back, west: col 0 = front)."""
    return list(range(w - 1, -1, -1)) if fc == "east" else list(range(w))

def eye_grid(rows, side_faces=("east", "west"), front=None, lid="lunette"):
    """Eye painted from a character grid, rows top->bottom, columns from the FRONT, on both side faces of an eye
    cube/plane (so it reads right on either side of the head). front: column of chars for the north face."""
    keys = {"E": "eye", "S": "eye_shine", "I": "eye_iris", "L": lid, "W": "eye_white", "H": "lash", "C": "coat",
            "P": "patch", "D": "eye_dark"}
    def fn(px, faces, pal, rnd):
        for fc in side_faces:
            x, y, w, h = faces[fc]
            if not (w and h):
                continue
            cols = side_cols(fc, w)
            for j in range(min(h, len(rows))):
                for k in range(min(w, len(rows[j]))):
                    ch = rows[j][k]
                    if ch == ".":
                        continue
                    px[x + cols[k], y + j] = pal[keys[ch]]
        if front:
            x, y, w, h = faces["north"]
            for j in range(min(h, len(front))):
                for i in range(w):
                    row = front[j]
                    ch = row[min(i, len(row) - 1)]       # 1-char rows fill the whole row; else col 0 = viewer's left
                    if ch != ".":
                        px[x + i, y + j] = pal[keys[ch]]
        for fc in ("up", "down", "south") + (() if front else ("north",)):
            x, y, w, h = faces[fc]
            if w and h:
                fill(px, x, y, w, h, pal[lid], 0.9, rnd, 2)
    return fn

EYE_KEYS = {"E": "eye", "D": "eye_dark", "I": "eye_iris", "J": "eye_iris2", "S": "eye_shine", "W": "eye_white",
            "H": "lash", "L": "lunette"}

def plane_pattern(rows, used, order="direct"):
    """Char-grid painter for a plane cube: draws `rows` on the faces in `used`, everything else transparent.
    order='direct': col 0 = the face's col 0 (north face: viewer's left); 'front': side faces counted from the front.
    '.' = transparent (rounded corners)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            if fc not in used:
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            cols = side_cols(fc, w) if order == "front" else list(range(w))
            for j in range(h):
                row = rows[min(j, len(rows) - 1)]
                for k in range(w):
                    ch = row[k] if k < len(row) else "."
                    px[x + cols[k], y + j] = (0, 0, 0, 0) if ch == "." else pal[EYE_KEYS[ch]]
    return fn

def add_eye(m, parent, side, sx, *, x_edge, w, y0, h, z_face, d, front, side_rows, **_):
    """Eye wrapping the front corner of the skull: a w x h plane just in front of the face and a d x h plane just
    outside the side face, in one bone (blink / sleep = scale Y, which uncovers the closed lids painted on the skull).
    `front` is drawn for the eye on the viewer's LEFT (Bedrock -X, outer corner = col 0) and mirrored for the other."""
    rows = front if sx < 0 else [r[::-1] for r in front]
    x0 = x_edge - w if sx > 0 else -x_edge
    xs = x_edge + 0.03 if sx > 0 else -x_edge - 0.03
    cubes = [Cube([x0, y0, z_face - 0.03], [w, h, 0], {"fn": plane_pattern(rows, ("north",))})]
    if d:
        cubes.append(Cube([xs, y0, z_face], [0, h, d], {"fn": plane_pattern(side_rows, ("east", "west"), "front")}))
    return m.bone(f"eye_{side}", parent, [sx * (x_edge - w / 2), y0 + h / 2, z_face], cubes=cubes)

def closed_lids(x_edge, w, y0, h, z_face, d, lash_row=None, **_):
    """coat(extra=...) hook painting the closed eyes under the eye planes: lunette lids with a dark lash line on
    `lash_row` (counted from the top of the eye area)."""
    mid = y0 + h / 2 if lash_row is None else y0 + h - lash_row - 0.5
    def extra(p, face, key):
        x, y, z = p
        if not (y0 - 0.01 <= y <= y0 + h + 0.01):
            return key
        front = face == "north" and abs(z - z_face) < 0.05 and x_edge - w - 0.01 <= abs(x) <= x_edge + 0.01
        side = face in ("east", "west") and abs(abs(x) - x_edge) < 0.05 and z_face - 0.01 <= z <= z_face + d + 0.01
        if not (front or side):
            return key
        outer = side or abs(x) > x_edge - 1                  # the lash line flicks up at the outer corner
        return "lash" if abs(y - (mid + (1 if outer else 0))) <= 0.5 else "lunette"
    return extra

def muzzle_fn(nostril_rows=(0, 1)):
    """Broad wet muzzle (mufle): pink, comma nostrils at the outer top corners of the nose plate, wet glints,
    dark lip line at the bottom; the nose bridge (up face) turns pink only at the front."""
    def fn(px, faces, pal, rnd):
        x, y, w, h = faces["north"]
        for i, j in ((1, 0), (0, 1), (w - 2, 0), (w - 1, 1)):        # comma-shaped nostrils, outer top corners
            if 0 <= i < w and j < h:
                px[x + i, y + j] = pal["nostril"]
        for i in range(1, w - 1):
            if rnd.random() < 0.5:
                px[x + i, y] = pal["muzzle_wet"]
        for i in range(w):
            px[x + i, y + h - 1] = shade(pal["mouth"], 1.0)
        for fc in ("east", "west"):
            x, y, w, h = faces[fc]
            for k in side_cols(fc, w)[: max(1, w // 2)]:
                px[x + k, y + h - 1] = pal["mouth"]
        x, y, w, h = faces["up"]          # row 0 = back
        for j in range(h - 1):
            for i in range(w):
                px[x + i, y + j] = shade(pal["coat"], FACE_LIGHT["up"])
        for i in range(w):
            px[x + i, y + h - 1] = shade(pal["muzzle"], FACE_LIGHT["up"])
    return fn

def ear_fn(px, faces, pal, rnd):
    """Ear plate facing forward: pink inside with a paler centre and a fringe of coat hair round the edge."""
    x, y, w, h = faces["north"]
    for j in range(h):
        for i in range(w):
            edge = j == 0 or i in (0, w - 1)
            px[x + i, y + j] = shade(pal["patch"] if edge else pal["ear_in"], 1.0 if edge else 1.0 + 0.04 * (j % 2))
    if w >= 3 and h >= 3:
        for i in range(1, w - 1):
            px[x + i, y + h // 2] = pal["ear_in_light"]

def horn_fn(base="horn", tip="horn_tip", along="y"):
    """Horn gradient from base to tip (along = axis of the cube the horn grows along: x, y or z; '-y' etc)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if along in ("y", "-y"):
                        t = j / max(h - 1, 1)
                        t = 1 - t if along == "y" else t
                    else:
                        t = i / max(w - 1, 1) if fc in ("north", "south", "up", "down") else 0.5
                    put(px, x + i, y + j, mix(pal[base], pal[tip], t), FACE_LIGHT[fc], rnd, 3)
    return fn

def fringe(key="coat", tip="coat_wet", drop="water", mud_key=None, density=0.75, seed=5):
    """Shaggy wet hair fringe on a plane (hangs down): strands of random length, darker soaked tips, a few water
    drops below; transparent between ragged ends."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h) or fc in ("up", "down"):
                continue
            for i in range(w):
                L = h if rnd.random() < 0.25 else max(1, int(h * rnd.uniform(0.45, 1.0)))
                for j in range(h):
                    if j >= L:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    t = j / max(h - 1, 1)
                    c = mix(pal[key], pal[tip], min(1, t * 1.3))
                    if mud_key and j >= L - 2:
                        c = mix(c, pal[mud_key], 0.6)
                    put(px, x + i, y + j, c, 1.0 - 0.06 * (i % 2), rnd, 4)
                if L < h - 1 and rnd.random() < 0.3:
                    px[x + i, y + L + 1] = pal[drop]
    return fn

def kelp(keys=("kelp", "kelp_dark", "kelp_light", "wrack"), density=0.8, bladders=0.12):
    """Draped seaweed on a plane: hanging olive / brown fronds of random length (transparent between them),
    a lighter midrib, a few air bladders of bladder wrack."""
    k, kd, kl, wr = keys
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h) or fc in ("up", "down"):
                continue
            for i in range(w):
                if rnd.random() > density:
                    for j in range(h):
                        px[x + i, y + j] = (0, 0, 0, 0)
                    continue
                L = max(2, int(h * rnd.uniform(0.5, 1.0)))
                base = pal[wr] if rnd.random() < 0.35 else pal[k]
                for j in range(h):
                    if j >= L:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    c = base if (i + j) % 3 else pal[kd]
                    if rnd.random() < bladders:
                        c = pal[kl]
                    put(px, x + i, y + j, c, 1.0, rnd, 4)
    return fn

def solid(key, noise=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            fill(px, x, y, w, h, pal[key], FACE_LIGHT[fc], rnd, noise)
    return fn

# ============================================================================ rig
def make_legs(front, back, paints_front, paints_back):
    """front/back: dict(x, z, L, a, th, thigh, shin, meta, foot). Returns 4 Legs, parent 'body'.
    Left = +X (same convention as the other rigs)."""
    legs = []
    for end, spec, paints, bend in (("front", front, paints_front, -1), ("back", back, paints_back, 1)):
        for side, sx in SIDES:
            legs.append(Leg(f"{end}_{side}", spec["x"] * sx, spec["z"], spec["L"], spec["a"], spec["th"],
                            thigh=spec["thigh"], shin=spec["shin"], meta=spec["meta"], foot=spec["foot"], claws=(),
                            paints=paints, claw_len=1, dewclaw=False, bend=bend))
    return legs

def by(legs, name):
    return next(lg for lg in legs if lg.side == name)

def _rot(theta):
    r = math.radians(theta)
    return math.cos(r), math.sin(r)

def hip_world(lg, theta, body_dy, pivot):
    c, s = _rot(theta)
    hy, hz = lg.H - pivot[1], lg.hip_z - pivot[2]
    return pivot[1] + body_dy + c * hy + s * hz, pivot[2] - s * hy + c * hz

def to_frame(theta, dy, dz):
    c, s = _rot(theta)
    return c * dy - s * dz, s * dy + c * dz

def plant(lg, theta=0.0, body_dy=0.0, pivot=(0, 0, 0), foot_dz=0.0, lift=0.0, a3=None, a4=0.0):
    """Absolute leg angles (in the body frame) putting the hoof at its rest spot (+foot_dz, raised by lift) while
    the body is pitched by theta (+ = front down) about `pivot` and moved by body_dy. a3/a4 = WORLD angles of the
    cannon / hoof (None = rest cannon angle)."""
    hy, hz = hip_world(lg, theta, body_dy, pivot)
    ty, tz = lg.th + lift, lg.hip_z + lg.foot_dz + foot_dz
    fy, fz = to_frame(theta, ty - hy, tz - hz)
    return lg.ik(fy, fz, (lg.a[2] if a3 is None else a3) - theta, a4 - theta)

def kneel(lg, theta, body_dy, pivot, knee_dz=0.5, knee_y=1.0, a3=105.0, a4=150.0):
    """Foreleg kneeling on its carpus: carpus at height knee_y, knee_dz in front of the shoulder (world),
    cannon folded back under (world angle a3)."""
    hy, hz = hip_world(lg, theta, body_dy, pivot)
    fy, fz = to_frame(theta, knee_y - hy, (lg.hip_z + knee_dz) - hz)
    return lg.ik_ankle(fy, fz, a3 - theta, a4 - theta)

def legs_pose(legs, angles):
    """{leg: absolute angles} -> pose entries (deltas)."""
    out = {}
    for lg in legs:
        if lg.side in angles:
            for b, d in zip(lg.bones, lg.deltas(angles[lg.side])):
                out[b] = {"rotation": [d, 0, 0]}
    return out

def stance(legs, theta=0.0, body_dy=0.0, pivot=(0, 0, 0), feet=None, body_rot=None):
    """Pose with every hoof planted (feet: {leg: (foot_dz, lift, a3, a4)} overrides) and the body pitched."""
    feet = feet or {}
    ang = {}
    for lg in legs:
        dz, lift, a3, a4 = feet.get(lg.side, (0.0, 0.0, None, 0.0))
        ang[lg.side] = plant(lg, theta, body_dy, pivot, dz, lift, a3, a4)
    pose = legs_pose(legs, ang)
    r = list(body_rot or [0, 0, 0])
    r[0] += theta
    pose["body"] = {"rotation": r, "position": [0, body_dy, 0]}
    return pose

def copy_pose(p):
    return {k: {kk: list(vv) for kk, vv in d.items()} for k, d in p.items()}

def merge(*poses):
    out = {}
    for p in poses:
        for b, chans in p.items():
            for ch, v in chans.items():
                out.setdefault(b, {})[ch] = list(v)
    return out

def add(pose, bone, ch, v):
    cur = pose.setdefault(bone, {}).setdefault(ch, [0, 0, 0])
    pose[bone][ch] = [a + b for a, b in zip(cur, v)]

# ---------------------------------------------------------------------------- sampled animations
def lerp_keys(track, t):
    """track: [(t, value or list)] piecewise smoothstep."""
    if t <= track[0][0]:
        return track[0][1]
    for (t0, v0), (t1, v1) in zip(track, track[1:]):
        if t0 <= t <= t1:
            e = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            if isinstance(v0, (list, tuple)):
                return [a + (b - a) * e for a, b in zip(v0, v1)]
            return v0 + (v1 - v0) * e
    return track[-1][1]

def sampled(length, step, fn, loop=False):
    """Samples fn(t) -> pose at `step` into catmull-rom channels."""
    bones = {}
    n = int(round(length / step))
    for k in range(n + 1):
        t = round(k * step, 3)
        pose = fn(t if not (loop and k == n) else 0.0)
        for b, chans in pose.items():
            for ch, val in chans.items():
                bones.setdefault(b, {}).setdefault(ch, {})[str(t)] = kf([round(x, 2) for x in val])
    return bones

# ---------------------------------------------------------------------------- lying poses
def fold_leg(m, pose, lg, grids, prefer, clear=0.12):
    """Grid search of absolute angles (a1, a2, a3, a4) for one leg so its lowest point rests on the ground
    (>= 0, close to `clear`), closest to the preferred angles. Writes into pose."""
    group = set(lg.bones)
    best = None
    for a1 in grids[0]:
        for a2 in grids[1]:
            for a3 in grids[2]:
                ang = (a1, a2, a3, a3 + grids[3])
                p = dict(pose)
                for b, d in zip(lg.bones, lg.deltas(ang)):
                    p[b] = {"rotation": [d, 0, 0]}
                lo = lowest(m, p, only=group)
                if lo < -0.02:
                    continue
                score = abs(lo - clear) + 0.004 * sum(abs(x - y) for x, y in zip(ang[:3], prefer))
                if best is None or score < best[0]:
                    best = (score, ang)
    ang = best[1] if best else prefer + (prefer[2] + grids[3],)
    for b, d in zip(lg.bones, lg.deltas(ang)):
        pose[b] = {"rotation": [d, 0, 0]}
    return ang

def rng(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]

def sternal(m, legs, trunk, theta=0.0, lean=0.0):
    """Lying on the brisket: belly on the ground, forelegs folded at the carpus (forearm forward, cannon tucked
    back under it), hind legs folded under (femur forward, hock back, cannon forward)."""
    pose = {"body": {"rotation": [theta, 0, lean], "position": [0, 0, 0]}}
    pose["body"]["position"][1] = -lowest(m, pose, only=trunk) + 0.02
    for lg in legs:
        if lg.side.startswith("front"):
            fold_leg(m, pose, lg, (rng(5, 75, 8), rng(-100, -60, 9), rng(70, 130, 7), 25), (40, -85, 100))
        else:
            fold_leg(m, pose, lg, (rng(-95, -45, 11), rng(70, 140, 8), rng(-110, -60, 6), -10), (-70, 105, -85))
    legs_lo = lowest(m, pose, only={b for lg in legs for b in lg.bones})
    if legs_lo < 0:                                # woolly thighs bigger than the folded room: settle on them
        pose["body"]["position"][1] += -legs_lo + 0.02
    return pose

def lay_tail(m, pose, tail, yaw=(30, 25), target=0.25, skip=()):
    """Tail lying on the ground behind / beside the body: each segment lifted back (X) until it just touches the
    ground, then swept sideways (Y)."""
    for i, tb in enumerate(tail):
        grp = descendants(m, tb) - set(skip)
        best = None
        for x in rng(-10, 110, 61):
            p = copy_pose(pose)
            p[tb] = {"rotation": [x, 0, 0]}
            lo = lowest(m, p, only=grp)
            if lo < 0:
                continue
            sc = abs(lo - target)
            if best is None or sc < best[0]:
                best = (sc, x)
        pose[tb] = {"rotation": [best[1] if best else 60, yaw[min(i, len(yaw) - 1)], 0]}
    return pose

# ============================================================================ animations
def bovine_anims(sid, m, legs, *, pivot, walk_kw, torso=(0.8, 1.5, 2.0), chew=1.0, trunk=("torso", "chest"),
                 ears=("ear_left", "ear_right"), tail=("tail", "tail_tip"), eyes=("eye_left", "eye_right"),
                 skip=(), battle=None, cry=None, sleep_kw=None, faint_kw=None, idle_extra=None, walk_extra=None,
                 battle_extra=None, graze_kw=None, ear_axis=1):
    a = f"animation.{sid}."
    q = "q.anim_time"
    out = {}
    names = {b.name for b in m.bones}
    trunk_set = set(trunk)
    for t in trunk:
        trunk_set |= {b for b in descendants(m, t)
                      if not b.startswith(("neck", "head", "ear", "eye", "jaw", "horn", "tail"))}
    trunk_set -= set(skip)

    # ---------------------------------------------------------------- idle: breathing, cud chewing, ear flicks, tail
    env = f"math.clamp(math.sin({q}*45+20)*2.2+0.6,0,1)"
    idle = {"torso": {"rotation": [f"math.sin({q}*90)*0.35", 0, 0]},
            "chest": {"position": [0, f"math.sin({q}*90-30)*0.08", 0]},
            "neck": {"rotation": [f"math.sin({q}*45)*1.5", f"math.sin({q}*45-30)*3", 0]},
            "head": {"rotation": [f"math.sin({q}*45+60)*1.5", f"math.sin({q}*45-70)*4", f"math.sin({q}*45-100)*1.5"]},
            "jaw": {"rotation": [f"{env}*(1.2+math.sin({q}*450)*1.2)*{chew}", f"{env}*math.sin({q}*450+90)*3*{chew}", 0]}}
    for (ear, s), t0 in zip(zip(ears, (1, -1)), (2.0, 5.3)):
        fl = [0, 30 * s * ear_axis, -12 * s]
        idle[ear] = keys(rotation={0: [0, 0, 0], t0 - 0.1: [0, 0, 0], t0: fl, t0 + 0.12: [0, -6 * s * ear_axis, 4 * s],
                                   t0 + 0.25: [x * 0.7 for x in fl], t0 + 0.42: [0, 0, 0], 8: [0, 0, 0]})
    if tail:
        tr = {0: [0, 0, 0], 1.5: [0, 0, 4], 3.2: [0, 0, -3], 3.5: [6, 0, 24], 3.8: [4, 0, -18], 4.1: [3, 0, 12],
              4.5: [0, 0, -4], 6.2: [0, 0, 3], 8: [0, 0, 0]}
        idle[tail[0]] = keys(rotation=tr)
        for i, tb in enumerate(tail[1:], 1):
            idle[tb] = keys(rotation={min(8.0, round(t + 0.12 * i, 2)) if t not in (0, 8) else t: [v[0] * 0.5, 0, v[2] * (0.6 + 0.2 * i)]
                                      for t, v in tr.items()})
    for b, ch in (idle_extra or {}).items():
        idle.setdefault(b, {}).update(ch)
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": idle}

    # ---------------------------------------------------------------- walk (4-beat lateral sequence)
    wk = dict(walk_kw)
    T = wk["T"]
    f = round(360 / T, 3)
    ex = {"neck": {"rotation": [f"math.sin({q}*{2 * f}+40)*2.2", f"math.sin({q}*{f}+20)*2", 0]},
          "head": {"rotation": [f"-math.sin({q}*{2 * f}+70)*1.4", f"-math.sin({q}*{f})*1.5", f"math.sin({q}*{f})*1.2"]},
          "jaw": {"rotation": [0, 0, 0]}}
    for ear, s in zip(ears, (1, -1)):
        ex[ear] = {"rotation": [0, 0, f"math.sin({q}*{2 * f}+{90 if s > 0 else 0})*{3 * s}"]}
    for i, tb in enumerate(tail):
        ex[tb] = {"rotation": [f"math.sin({q}*{2 * f}-{30 * (i + 1)})*{1.5 + i}", 0, f"math.sin({q}*{f}-{50 * (i + 1)})*{5 + 3 * i}"]}
    ex.update(walk_extra or {})
    out[a + "ground_walk"] = walk(legs, phases=GAIT, torso=torso, tail=(), neck=True, arms=(), extra=ex, **wk)

    # ---------------------------------------------------------------- battle: head low, horns forward, pawing
    B = dict(theta=2.5, dy=-0.7, neck=10, head=-12, paw="front_right", paw_t=1.0, ears_back=22, tail_up=14)
    B.update(battle or {})
    paw = B["paw"]
    t0 = B["paw_t"]
    traj = [(0, (0, 0)), (t0, (0, 0)), (t0 + 0.15, (-0.6, 1.8)), (t0 + 0.3, (-1.8, 0.5)), (t0 + 0.38, (-1.8, 0)),
            (t0 + 0.62, (1.5, 0)), (t0 + 0.77, (0.3, 1.6)), (t0 + 0.92, (-1.8, 0.5)), (t0 + 1.0, (-1.8, 0)),
            (t0 + 1.24, (1.3, 0)), (t0 + 1.42, (0.4, 1.0)), (t0 + 1.58, (0, 0)), (4, (0, 0))]
    snort = [(0, 0), (2.9, 0), (3.0, 1), (3.12, -0.4), (3.35, 0.3), (3.6, 0), (4, 0)]

    def battle_pose(t):
        pawing = t0 + 0.05 < t < t0 + 1.55
        th = B["theta"] + (0.6 if pawing else 0) * math.sin(math.pi * min(1, max(0, (t - t0) / 1.6)))
        dz, lift = lerp_keys(traj, t)
        p = stance(legs, th, B["dy"] + 0.08 * math.sin(math.radians(t * 180)), pivot,
                   feet={paw: (dz, lift, None, 25 * max(0.0, lift - 0.6) / 1.2)})
        sn = lerp_keys(snort, t)
        p["neck"] = {"rotation": [B["neck"] + 4 * sn + math.sin(math.radians(t * 180)) * 1.2, 0, 0]}
        p["head"] = {"rotation": [B["head"] - 7 * sn + math.sin(math.radians(t * 180 - 60)) * 1.2, 0,
                                  2.5 * math.sin(math.radians(t * 90))]}
        p["jaw"] = {"rotation": [1 + 3 * max(0, sn), 0, 0]}
        p["torso"] = {"rotation": [0, 0, 1.2 * math.sin(math.radians(t * 90))]}
        for ear, s in zip(ears, (1, -1)):
            p[ear] = {"rotation": [0, B["ears_back"] * s * ear_axis + 3 * math.sin(math.radians(t * 360)), -8 * s]}
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [B["tail_up"] if i == 0 else 4, 0, (8 + 4 * i) * math.sin(math.radians(t * 180 - 50 * i))]}
        for b, ch in (battle_extra or {}).items():
            for c, v in ch.items():
                p.setdefault(b, {})[c] = v(t) if callable(v) else v
        return p
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": sampled(4, 0.05, battle_pose, loop=True)}

    # ---------------------------------------------------------------- sleep: lying on the brisket, chin on the ground
    S = dict(neck_yaw=22, head_roll=8, lean=3)
    S.update(sleep_kw or {})
    sp = sternal(m, legs, trunk_set, lean=S["lean"])
    sp["neck"] = {"rotation": [0, S["neck_yaw"], 0]}
    head_grp = descendants(m, "head") - set(skip)
    best = None
    for nx in rng(0, 60, 25):
        for hx in rng(-30, 40, 15):
            p = copy_pose(sp)
            p["neck"] = {"rotation": [nx, S["neck_yaw"], 0]}
            p["head"] = {"rotation": [hx, 8, S["head_roll"]]}
            lo = lowest(m, p, only=head_grp)
            if lo < 0:
                continue
            sc = abs(lo - 0.15) + 0.01 * abs(hx)
            if best is None or sc < best[0]:
                best = (sc, nx, hx)
    _, nx, hx = best
    sp["neck"] = {"rotation": [nx, S["neck_yaw"], 0]}
    sp["head"] = {"rotation": [hx, 8, S["head_roll"]]}
    sleep_bones = {b: dict(ch) for b, ch in sp.items()}
    sleep_bones["torso"] = {"rotation": [f"math.sin({q}*45)*0.5", 0, 0]}
    sleep_bones["chest"] = {"position": [0, f"0.06+math.sin({q}*45-20)*0.06", 0]}
    for ear, s in zip(ears, (1, -1)):
        sleep_bones[ear] = {"rotation": [0, -8 * s * ear_axis, 18 * s]}
    lay_tail(m, sp, tail, skip=skip)
    for tb in tail:
        sleep_bones[tb] = sp[tb]
    for e in eyes:
        sleep_bones[e] = {"scale": [1, 0.1, 1]}
    sleep_bones["jaw"] = {"rotation": [0, 0, 0]}
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sleep_bones}
    out[a + "_sleep_pose"] = sp      # internal (removed before export)

    # ---------------------------------------------------------------- cry, knock-out, grazing quirk
    out[a + "cry"] = moo(legs, pivot, ears=ears, tail=tail, ear_axis=ear_axis, **(cry or {}))
    out[a + "faint"] = knockout(m, legs, pivot, trunk=trunk_set, ears=ears, tail=tail, eyes=eyes, skip=skip,
                                **(faint_kw or {}))
    out[a + "graze"] = graze(m, legs, pivot, ears=ears, tail=tail, skip=skip, **(graze_kw or {}))

    # ---------------------------------------------------------------- blink
    out[a + "blink"] = {"animation_length": 0.2, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.1, 1], "0.2": [1, 1, 1]}} for e in eyes}}
    return out

# ---------------------------------------------------------------------------- moo
def moo(legs, pivot, *, ears, tail, L=1.8, t_in=0.3, t_open=0.6, t_close=1.35, neck=-14.0, head=-16.0, jaw=14.0,
        yaw=0.0, theta=0.0, tremble=1.4, ear_axis=1, extra=None):
    """Lowing: a short inhale (neck dips, chest fills), then the neck stretches and the muzzle lifts as the mouth
    opens slowly, the call is held with a throaty tremble (and a head swing for a bellow), the mouth closes and
    everything settles. Hooves stay planted."""
    def env(t):
        if t < t_in:
            return 0.0
        if t < t_open:
            return smooth((t - t_in) / (t_open - t_in))
        if t < t_close:
            return 1.0
        return 1 - smooth((t - t_close) / (L - t_close))
    def pose(t):
        e = env(t)
        pre = math.sin(math.pi * min(1, t / t_in)) if t < t_in else 0.0
        hold = 1.0 if t_open <= t <= t_close else 0.0
        trem = math.sin(math.radians(t * 1900)) * tremble * hold
        p = stance(legs, theta * e, -0.15 * pre, pivot)
        p["chest"] = {"position": [0, 0.15 * pre - 0.05 * e, 0]}
        p["torso"] = {"rotation": [-0.8 * e, 0, 0]}
        sw = yaw * math.sin(math.radians((t - t_open) * 300)) * hold
        p["neck"] = {"rotation": [4 * pre + neck * e, 0.4 * sw, 0]}
        p["head"] = {"rotation": [3 * pre + head * e + trem * 0.5, sw, 0]}
        p["jaw"] = {"rotation": [jaw * e + trem, 0, 0]}
        for ear, sg in zip(ears, (1, -1)):
            p[ear] = {"rotation": [0, 18 * sg * ear_axis * e, -10 * sg * e]}
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [16 * e if i == 0 else 6 * e, 0, 4 * math.sin(math.radians(t * 240)) * e]}
        for b, ch in (extra or {}).items():
            for c, v in ch.items():
                p.setdefault(b, {})[c] = v(t, e) if callable(v) else v
        return p
    return {"animation_length": L, "bones": sampled(L, 0.05, pose)}

# ---------------------------------------------------------------------------- graze (quirk)
def graze(m, legs, pivot, *, ears, tail, skip=(), L=5.0, theta=2.0, muzzle="head"):
    """Lowers the head to the grass, crops it with short tugs, then lifts the head while chewing."""
    head_grp = descendants(m, "head") - set(skip)
    base = stance(legs, theta, -0.35, pivot)
    best = None
    for nx in rng(0, 70, 36):
        for hx in rng(-20, 50, 15):
            p = copy_pose(base)
            p["neck"] = {"rotation": [nx, 0, 0]}
            p["head"] = {"rotation": [hx, 0, 0]}
            lo = lowest(m, p, only=head_grp)
            if lo < 0.15:
                continue
            sc = abs(lo - 0.4) + 0.004 * abs(hx - 10)
            if best is None or sc < best[0]:
                best = (sc, nx, hx)
    _, NX, HX = best
    def pose(t):
        e = smooth(t / 0.9) if t < 0.9 else (1.0 if t < 3.5 else 1 - smooth((t - 3.5) / 1.1))
        p = stance(legs, theta * e, -0.35 * e, pivot)
        crop = 0.9 < t < 3.5
        tug = math.sin(math.radians((t - 0.9) * 900)) if crop else 0.0
        pull = max(0.0, math.sin(math.radians((t - 0.9) * 140))) if crop else 0.0
        p["neck"] = {"rotation": [NX * e - 3 * pull, 0, 0]}
        p["head"] = {"rotation": [HX * e - 4 * max(0, tug) - 5 * pull, 6 * pull * (1 if t < 2.2 else -1), 0]}
        chew = 0.0 if t < 3.3 else min(1, (t - 3.3) / 0.3)
        p["jaw"] = {"rotation": [(4 + 4 * tug) * (1 if crop else 0) + chew * (1.5 + 1.5 * math.sin(math.radians(t * 450))),
                                 chew * 3 * math.sin(math.radians(t * 450 + 90)), 0]}
        for ear, sg in zip(ears, (1, -1)):
            p[ear] = {"rotation": [0, -10 * sg * e, 6 * sg * e]}
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [0, 0, (4 + 2 * i) * math.sin(math.radians(t * 120 - 40 * i))]}
        return p
    return {"animation_length": L, "bones": sampled(L, 0.05, pose)}

# ---------------------------------------------------------------------------- knock-out
def lateral(m, legs, trunk, skip=(), roll=84.0):
    """Lying flat on the left flank (+X side down), legs stretched out, upper legs resting on the lower ones,
    neck and head laid on the ground."""
    pose = {"body": {"rotation": [0, 0, roll], "position": [0, 0, 0]}}
    for lg in legs:
        front = lg.side.startswith("front")
        ang = (8, -14, -20, -30) if front else (-12, 24, 18, 30)
        for b, d in zip(lg.bones, lg.deltas(ang)):
            pose[b] = {"rotation": [d, 0, 0]}
    pose["body"]["position"][1] = -lowest(m, pose, only=trunk) + 0.02
    for lg in legs:                 # lower legs: lift the hooves level with the flank; upper legs: droop onto them
        upper = lg.x < 0
        grp = set(lg.bones)
        best = None
        for zr in (rng(-40, 0, 21) if upper else rng(-20, 20, 21)):
            p = copy_pose(pose)
            p[lg.bones[0]]["rotation"][2] = zr
            lo = lowest(m, p, only=grp)
            if lo < 0.0:
                continue
            target = 1.6 if upper else 0.1
            sc = abs(lo - target)
            if best is None or sc < best[0]:
                best = (sc, zr)
        if best:
            pose[lg.bones[0]]["rotation"][2] = best[1]
    neck_grp = descendants(m, "neck") - set(skip)
    head_grp = descendants(m, "head") - set(skip)
    best = None
    for ny in rng(-20, 60, 17):
        for hz in rng(-70, 70, 15):          # head roll: lets wide horns lie flat instead of digging in
            for hy in (0.0, 15.0, 30.0):
                p = copy_pose(pose)
                p["neck"] = {"rotation": [6, ny, 0]}
                p["head"] = {"rotation": [8, hy, hz]}
                if lowest(m, p, only=neck_grp) < -0.02:
                    continue
                lo = lowest(m, p, only=head_grp)
                sc = abs(lo - 0.15) + 0.003 * (abs(ny) + abs(hz) + abs(hy))
                if best is None or sc < best[0]:
                    best = (sc, ny, hy, hz)
    if best:
        pose["neck"] = {"rotation": [6, best[1], 0]}
        pose["head"] = {"rotation": [8, best[2], best[3]]}
    return pose

def kneel_pose(m, legs, pivot):
    """Front knees on the ground, hind legs still standing: searches body pitch / drop for comfortable reaches."""
    fl = [lg for lg in legs if lg.side.startswith("front")]
    bl = [lg for lg in legs if lg.side.startswith("back")]
    best = None
    for th in rng(4, 40, 37):
        for dy in rng(-8, 0, 33):
            sc = 0
            for lg in fl:
                hy, hz = hip_world(lg, th, dy, pivot)
                d = math.hypot(hy - 1.0, hz - (lg.hip_z + 0.5))
                sc += (d / (lg.L[0] + lg.L[1]) - 0.9) ** 2
            for lg in bl:
                hy, hz = hip_world(lg, th, dy, pivot)
                d = math.hypot(lg.th - hy, (lg.hip_z + lg.foot_dz) - hz)
                r = (d - lg.L[2]) / (lg.L[0] + lg.L[1])
                sc += (r - 0.95) ** 2 * 2 + (10 if r > 0.99 else 0)
            if best is None or sc < best[0]:
                best = (sc, th, dy)
    _, th, dy = best
    ang = {lg.side: kneel(lg, th, dy, pivot) for lg in fl}
    ang.update({lg.side: plant(lg, th, dy, pivot) for lg in bl})
    pose = legs_pose(legs, ang)
    pose["body"] = {"rotation": [th, 0, 0], "position": [0, dy, 0]}
    return pose

def knockout(m, legs, pivot, *, trunk, ears, tail, eyes, skip=(), L=3.0, extra=None):
    """Recoil, stagger, the forelegs buckle onto the knees, the hindquarters drop, then it rolls over onto its
    flank, legs out, head laid down, one last breath."""
    trunk = set(trunk)
    k0 = stance(legs, 0, 0, pivot)
    k1 = merge(stance(legs, -3, 0.25, pivot), {"neck": {"rotation": [-10, 0, 0]}, "head": {"rotation": [-12, 0, 0]},
                                                "jaw": {"rotation": [8, 0, 0]}})
    k2 = merge(stance(legs, 1.5, -0.5, pivot, body_rot=[0, 0, 5]),
               {"neck": {"rotation": [10, -8, 0]}, "head": {"rotation": [6, 0, 10]}, "jaw": {"rotation": [4, 0, 0]}})
    k3 = merge(kneel_pose(m, legs, pivot), {"neck": {"rotation": [14, 4, 0]}, "head": {"rotation": [8, 0, -6]}})
    k4 = merge(sternal(m, legs, trunk, lean=4), {"neck": {"rotation": [22, 0, 0]}, "head": {"rotation": [10, 0, 0]}})
    k5 = lateral(m, legs, trunk, skip=skip)
    k5b = copy_pose(k5)
    k5b["jaw"] = {"rotation": [10, 0, 0]}
    ear_l, ear_r = ears
    for k, ev in ((k1, 0), (k2, 0), (k3, 0.4), (k4, 0.8), (k5, 1), (k5b, 1)):
        k[ear_l] = {"rotation": [0, -10, 22 * ev]}
        k[ear_r] = {"rotation": [0, 10, -22 * ev]}
        for i, tb in enumerate(tail):
            k[tb] = {"rotation": [6 * ev, 0, 20 * ev]}
    lay_tail(m, k4, tail, yaw=(25, 20), skip=skip)
    seq = [(0, k0), (0.3, k1), (0.7, k2), (1.15, k3), (1.6, k4), (2.1, k5), (2.6, k5b), (L, k5)]
    bones = pose_sequence(m, seq, length=L, skip=skip)
    bp = bones["body"]["position"]
    y = bp[str(round(2.1, 3))]["post"][1]
    bp["2.2"] = kf([0, round(y + 0.6, 2), 0])
    bp["2.35"] = kf([0, round(y, 2), 0])
    for e in eyes:
        bones[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.6, 1], 0.7: [1, 1, 1], 1.4: [1, 1, 1], 1.65: [1, 0.1, 1], L: [1, 0.1, 1]})
    for b, ch in (extra or {}).items():
        bones.setdefault(b, {}).update(ch)
    return {"animation_length": L, "bones": bones}

def finalize(anims):
    return {k: v for k, v in anims.items() if not k.split(".")[-1].startswith("_")}

def bovine_poser(sid, portrait, profile, graze_quirk=True):
    from templates import poser as make_poser
    ps = make_poser(sid, portrait=portrait, profile=profile)
    if graze_quirk:
        ps["poses"]["standing"]["quirks"] = ps["poses"]["standing"]["quirks"] + [f"q.bedrock_quirk('{sid}', 'graze')"]
    return ps
