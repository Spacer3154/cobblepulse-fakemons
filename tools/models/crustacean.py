# -*- coding: utf-8 -*-
"""Crustacean rig for the Homarbleu line (blue lobster -> armoured Viking lobster).

Eight walking legs, each three bones: coxa (yaw, Y), merus (elevation, Z) and dactyl tip ('foot_*', bend, Z), solved by
inverse kinematics in the body frame so the tips stay planted on the ground whatever the body does (walk, crouch,
battle stance). Claws (chelipeds) = arm / wrist / claw palm with fixed finger / movable finger. Antennae and the
abdomen are chains animated with phase-shifted Molang waves. Wing-free, so the poser only switches land / water.

Conventions (game, see modelgen): +X left, front -Z; Z: +s*a lowers the tip of a limb pointing to side s;
Y: +a moves a +X point forward."""
import math
from modelgen import Cube, fill, shade, mix, FACE_LIGHT, apply, compose, translate, rot_m
from biped import keys, kf, smooth, lowest, descendants, pose_sequence
from bovine import vnoise, light, put, side_cols, sampled, copy_pose, merge, lerp_keys, rng
from avian import _inv

SIDES = (("left", 1), ("right", -1))

# ============================================================================ painters
def shell(key="shell", joint="shell_joint", sheen="shell_sheen", axis="z", seed=1, speck=0.06, crust=None, barn=None):
    """Lobster shell (fn3, model space): satin base with a soft highlight on the upper faces, darker joint bands at
    both ends of the segment along `axis`, fine speckles. crust=(key, threshold, scale): limestone crust patches;
    barn=key: little barnacle rings painted where the crust is thickest."""
    ai = {"x": 0, "y": 1, "z": 2}[axis]
    def fn3(px, faces, pal, rnd, c):
        lo, hi = c.origin[ai], c.origin[ai] + c.size[ai]
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.14)
            col = pal[key]
            if face == "up" or (face in ("north", "south", "east", "west") and Y - fy == 0):
                col = mix(col, pal[sheen], 0.35)                          # satin highlight
            d = min(pl[ai] - lo, hi - pl[ai]) if hi - lo >= 2 else 9
            if d < 0.6 and face not in (("north", "south") if axis == "z" else ()):
                col = mix(col, pal[joint], 0.7)                           # joint between segments
            n = vnoise(p[0] * 1.3, p[1] * 1.3, p[2] * 1.3, seed)
            if n > 1 - speck * 4:
                col = mix(col, pal[sheen], 0.25)
            elif n < speck * 3:
                col = mix(col, pal[joint], 0.35)
            if crust:
                ck, thr, sc = crust
                v = vnoise(p[0] * sc + 5, p[1] * sc, p[2] * sc + 3, seed + 17)
                if v > thr and face != "down":
                    col = mix(col, pal[ck], 0.55 + 0.4 * (v - thr) / max(1 - thr, 1e-3))
                    if barn and v > thr + (1 - thr) * 0.6 and rnd.random() < 0.35:
                        col = pal[barn]
                w = vnoise(p[0] * 0.35, p[1] * 0.35 + 9, p[2] * 0.35, seed + 23)
                if w > 0.74:
                    col = mix(col, pal["patina"], 0.3)                    # sea patina
            put(px, X, Y, col, f, rnd, 3)
    return {"fn3": fn3}

def stripes(a="ant_a", b="ant_b", period=2, along="z"):
    """Antenna bands (light blue / white) along the segment."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if along == "z" and fc in ("east", "west"):
                        k = i
                    elif along == "z" and fc in ("up", "down"):
                        k = j
                    else:
                        k = 0
                    put(px, x + i, y + j, pal[a] if (k // period) % 2 == 0 else pal[b], FACE_LIGHT[fc], rnd, 2)
    return fn

def solid(key, noise=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            fill(px, x, y, w, h, pal[key], FACE_LIGHT[fc], rnd, noise)
    return fn

def serrated(key="shell", tooth="tooth", inner="east"):
    """Claw finger with a row of small teeth on the inner edge (bottom row of the side face facing the other finger)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            fill(px, x, y, w, h, pal[key], FACE_LIGHT[fc], rnd, 3)
            if fc == "up" and w >= 1:
                for j in range(h):
                    px[x + (0 if inner == "west" else w - 1), y + j] = shade(pal[tooth], 1.0) if j % 2 == 0 else shade(pal[key], 0.85)
            if fc in ("east", "west") and h >= 1 and fc == inner:
                for i in range(w):
                    for j in range(h):
                        if (i + j) % 2 == 0:
                            px[x + i, y + j] = shade(pal[tooth], 1.0)
    return fn

def blade(edge="blade_edge", steel="blade", rune="rune"):
    """Bearded Viking axe blade on a 1-thick plate (side faces = the blade's flat): a half-moon cut out of the plate
    (transparent outside), bulging to the front and hanging lower than it rises (the 'beard'), steel-blue sheen,
    bright honed edge along the curve, a band of runes near the haft."""
    def inside(i, j, w, h):
        # i: 0 at the front edge .. w-1 at the haft; j: 0 top .. h-1 bottom
        cy = h * 0.42
        rx, ry_up, ry_dn = w - 0.3, h * 0.42, h * 0.58
        ry = ry_up if j < cy else ry_dn
        return ((w - 1 - i) / rx) ** 2 + ((j - cy) / ry) ** 2 <= 1.0
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if fc in ("east", "west") and w >= 3 and h >= 3:
                cols = side_cols(fc, w)
                for j in range(h):
                    for k in range(w):
                        X, Y = x + cols[k], y + j
                        if not inside(k, j, w, h):
                            px[X, Y] = (0, 0, 0, 0)
                            continue
                        outer = not inside(k - 1, j, w, h) or not inside(k, j - 1, w, h) or not inside(k, j + 1, w, h)
                        if outer:
                            c = pal[edge]
                        elif k >= w - 2 and j % 2 == 1 and 2 < j < h - 3:
                            c = pal[rune]
                        else:
                            c = mix(pal[steel], pal["blade_dark"], 0.35 * k / max(w - 1, 1))
                        put(px, X, Y, c, 1.0, rnd, 2)
            else:
                for j in range(h):
                    for i in range(w):
                        put(px, x + i, y + j, pal[edge] if fc in ("north", "down") else pal["blade_dark"], FACE_LIGHT[fc], rnd, 2)
    return fn

def shield_face(rim="shell_joint", boss="shell_sheen", plank="shell", band="crust"):
    """Viking round shield painted on the outer face of the parrying claw: dark rim, a lighter band, radial planks
    and a central boss."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    cx, cy = (w - 1) / 2, (h - 1) / 2
                    r = math.hypot((i - cx) / max(cx, 0.5), (j - cy) / max(cy, 0.5))
                    if r > 1.05 and fc in ("east", "west"):
                        c = pal[plank]
                    elif r > 0.82:
                        c = pal[rim]
                    elif r > 0.68:
                        c = pal[band]
                    elif r < 0.3:
                        c = pal[boss]
                    else:
                        c = shade(pal[plank], 0.85 if (i + j) % 3 == 0 else 1.0)
                    put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)
    return fn

def eye_ball(ring="eye_ring", white="eye_white", pupil="eye", shine="eye_shine", iris="eye_iris", inner_left=True):
    """Big cartoon eye on a stalk: white eyeball outlined in dark navy with rounded (transparent) corners; the front
    face has a big glossy pupil with a catch-light, the side faces a pupil at the front edge (looking forward)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    corner = w >= 4 and h >= 4 and i in (0, w - 1) and j in (0, h - 1)
                    edge = i in (0, w - 1) or j in (0, h - 1)
                    px[x + i, y + j] = (0, 0, 0, 0) if corner else (pal[ring] if edge else shade(pal[white], FACE_LIGHT[fc] ** 0.5))
            if fc == "north" and w >= 4 and h >= 4:
                # 2x2 glossy pupil low on the inner side (towards the nose), catch-light, an iris glint
                c0 = 1 if inner_left else w - 3
                for j in range(h - 3, h - 1):
                    for i in range(c0, c0 + 2):
                        px[x + i, y + j] = pal[pupil]
                px[x + c0 + (0 if inner_left else 1), y + h - 3] = pal[shine]
                px[x + c0 + (1 if inner_left else 0), y + h - 2] = pal[iris]
            if fc in ("east", "west") and w >= 3 and h >= 4:
                cols = side_cols(fc, w)
                for j in range(2, h - 1):
                    px[x + cols[1], y + j] = pal[pupil]
    return fn

def glow_eye(px, faces, pal, rnd):
    """Small fierce ember eye (emissive): hot core, darker red rim."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                edge = (i in (0, w - 1) or j in (0, h - 1)) and w > 1 and h > 1
                c = pal["eye_glow_rim"] if edge else pal["eye_glow"]
                if not edge and rnd.random() < 0.3:
                    c = pal["eye_glow_hot"]
                px[x + i, y + j] = c

def ember_eye(inner_left=True):
    """Small piercing ember eye (emissive), front face 3 x 2: glowing orange with a dark vertical slit pupil and a
    hot highlight at the outer top (the slanted brow above gives the frown); the other faces glow darker so it reads
    as an ember set deep in its socket."""
    rows = ["OKH", "OKO"]
    def fn(px, faces, pal, rnd):
        keys = {"R": "eye_glow_rim", "K": "eye_slit", "H": "eye_glow_hot", "O": "eye_glow"}
        for fc, (x, y, w, h) in faces.items():
            if fc == "north" and w == 3 and h == 2:
                for j in range(2):
                    row = rows[j] if inner_left else rows[j][::-1]     # highlight at the outer corner
                    for i in range(3):
                        c = pal[keys[row[i]]]
                        if row[i] == "O" and rnd.random() < 0.25:
                            c = mix(c, pal["eye_glow_hot"], 0.45)        # flicker between emissive frames
                        px[x + i, y + j] = c
                continue
            for j in range(h):
                for i in range(w):
                    px[x + i, y + j] = pal["eye_glow_rim"] if (i + j) % 2 else mix(pal["eye_glow_rim"], pal["eye_glow"], 0.4)
    return fn

def barnacle(px, faces, pal, rnd):
    """Acorn barnacle: chalky plates with a dark slit at the top."""
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["barnacle"], FACE_LIGHT[fc], rnd, 6)
        if fc == "up" and w and h:
            px[x + w // 2, y + h // 2] = pal["barnacle_dark"]

def fan(key="shell", edge="shell_sheen", joint="shell_joint"):
    """Tail fan (telson + uropods) on a horizontal plane: five rounded blades, paler fringed edge."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if fc not in ("up", "down"):
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            for j in range(h):                       # row 0 = back (+Z): the fan's free edge
                for i in range(w):
                    blade_w = w / 5
                    k = i / blade_w
                    u = k - math.floor(k)
                    round_cut = j == 0 and (u < 0.2 or u > 0.8)
                    if round_cut:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    c = pal[edge] if j <= 0 else pal[key]
                    if u < 0.12 or u > 0.88:
                        c = mix(c, pal[joint], 0.5)
                    put(px, x + i, y + j, c, 1.0 if fc == "up" else 0.8, rnd, 3)
    return fn

# ============================================================================ legs (IK)
class CLeg:
    """Walking leg: coxa (yaw) -> merus (Z elevation, length L1) -> dactyl 'foot' (Z bend, length L2).
    root: hinge point (model space, rest); foot: (x, z) where the tip stands at rest."""
    def __init__(self, i, side, s, root, foot, L1, L2, t1=1, t2=1, paints=None, parent="body", tip=True):
        self.i, self.side, self.s = i, side, s
        self.root, self.foot0 = tuple(root), tuple(foot)
        self.L1, self.L2, self.t1, self.t2 = L1, L2, t1, t2
        self.paints, self.parent, self.tip = paints or {}, parent, tip
        self.bones = [f"coxa_{side}{i}", f"merus_{side}{i}", f"foot_{side}{i}"]
        self.ground = t2 * 0.18                     # slanted dactyl: its lower corner meets the ground
        self.rest = self.solve((foot[0], self.ground, foot[1]))

    def solve(self, F):
        """Absolute (yaw Y, merus Z, foot Z) for a tip target F in the rest frame of the body."""
        s = self.s
        rx, ry, rz = self.root
        dx, dy, dz = F[0] - rx, F[1] - ry, F[2] - rz
        psi = math.degrees(math.atan2(-dz, dx) if s > 0 else math.atan2(dz, -dx))
        h = math.hypot(dx, dz)
        L1, L2 = self.L1, self.L2
        D = max(abs(L1 - L2) + 1e-3, min(L1 + L2 - 1e-3, math.hypot(h, dy)))
        phi = math.atan2(dy, h)
        a = phi + math.acos(max(-1.0, min(1.0, (L1 * L1 + D * D - L2 * L2) / (2 * L1 * D))))   # knee up
        kx, ky = L1 * math.cos(a), L1 * math.sin(a)
        g = math.atan2(dy - ky, h - kx)
        alpha, beta = math.degrees(a), math.degrees(g - a)
        self._g = g                                   # absolute dactyl angle (radians, below horizontal < 0)
        return (psi, -s * alpha, -s * beta)

    def tip_target(self, F):
        """Solve twice so the dactyl's lower corner (not its axis) meets the ground: a slanted segment of
        thickness t reaches t/2 * cos(angle) below its axis tip."""
        self.solve(F)
        y = self.t2 / 2 * abs(math.cos(self._g)) + 0.02
        return self.solve((F[0], F[1] - self.ground + y, F[2]))

    def deltas(self, ang):
        return [ang[k] - self.rest[k] for k in range(3)]

    def build(self, m):
        s = self.s
        rx, ry, rz = self.root
        r = self.rest
        p = self.paints
        x0 = rx if s > 0 else rx - self.L1
        m.bone(self.bones[0], self.parent, [rx, ry, rz], rotation=[0, round(r[0], 3), 0],
               cubes=[Cube([rx - 0.5, ry - 0.5, rz - 0.5], [1, 1, 1], p.get("coxa", p.get("merus")))] if p.get("coxa_cube", True) else [])
        m.bone(self.bones[1], self.bones[0], [rx, ry, rz], rotation=[0, 0, round(r[1], 3)], cubes=[
            Cube([x0, ry - self.t1 / 2, rz - self.t1 / 2], [self.L1, self.t1, self.t1], p.get("merus"))])
        kx = rx + s * self.L1
        x1 = kx if s > 0 else kx - self.L2
        cubes = [Cube([x1, ry - self.t2 / 2, rz - self.t2 / 2], [self.L2, self.t2, self.t2], p.get("foot"))]
        if self.tip and p.get("tip"):
            xt = kx + self.L2 - 1 if s > 0 else kx - self.L2
            cubes.append(Cube([xt, ry - self.t2 / 2, rz - self.t2 / 2], [1, self.t2, self.t2], p["tip"], inflate=0.03))
        m.bone(self.bones[2], self.bones[1], [kx, ry, rz], rotation=[0, 0, round(r[2], 3)], cubes=cubes)

def body_matrix(pivot, rot=(0, 0, 0), pos=(0, 0, 0)):
    return compose(translate(*[p + q for p, q in zip(pivot, pos)]), rot_m(list(rot)), translate(*[-p for p in pivot]))

def legs_for_body(legs, pivot, rot=(0, 0, 0), pos=(0, 0, 0), feet=None, spread=1.0, follow_yaw=True):
    """Leg deltas planting every tip for a body pose. feet: {bone_name_of_leg[0]: (dx, lift, dz)} offsets (world).
    Rest feet turn with the body's yaw (follow_yaw) so a body turned sideways keeps its stance."""
    B = body_matrix(pivot, rot, pos)
    Binv = _inv(B)
    Y = body_matrix(pivot, (0, rot[1], 0)) if follow_yaw else body_matrix(pivot)
    out = {}
    for lg in legs:
        fx, fz = lg.foot0
        rx, _, rz = lg.root
        fx, fz = rx + (fx - rx) * spread, rz + (fz - rz) * spread
        w = apply(Y, (fx, lg.ground, fz))
        off = (feet or {}).get(lg.bones[0], (0, 0, 0))
        w = (w[0] + off[0], lg.ground + off[1], w[2] + off[2])
        F = apply(Binv, w)
        d = lg.deltas(lg.tip_target(F) if off[1] == 0 and abs(rot[0]) < 25 and abs(rot[2]) < 25 else lg.solve(F))
        out[lg.bones[0]] = {"rotation": [0, d[0], 0]}
        out[lg.bones[1]] = {"rotation": [0, 0, d[1]]}
        out[lg.bones[2]] = {"rotation": [0, 0, d[2]]}
    return out

def crab_walk(legs, pivot, *, T, stride, lift, travel=(0.0, -1.0), phases, stance=0.55, samples=24, body=None,
              extra=None, yaw=0.0):
    """Walk cycle: tips slide back along `travel` (world, unit (x, z)) during stance and swing forward with `lift`.
    body(u) -> (rot, pos) of the body bone (u = 0..1 over the cycle); yaw: body turned (crab-like sideways trot)."""
    bones = {}
    tx, tz = travel
    for k in range(samples + 1):
        u = k / samples
        t = round(T * u, 4)
        rot, pos = body(u) if body else ((0, 0, 0), (0, 0, 0))
        rot = (rot[0], rot[1] + yaw, rot[2])
        feet = {}
        for lg in legs:
            ul = (u + phases[lg.bones[0]]) % 1.0
            if ul < stance:
                q = ul / stance
                d = stride / 2 - stride * q
                up = 0.0
            else:
                q = (ul - stance) / (1 - stance)
                d = -stride / 2 + stride * smooth(q)
                up = lift * math.sin(math.pi * q)
            feet[lg.bones[0]] = (tx * d, up, tz * d)
        pose = legs_for_body(legs, pivot, rot, pos, feet=feet)
        pose["body"] = {"rotation": list(rot), "position": list(pos)}
        for b, chans in pose.items():
            for ch, v in chans.items():
                bones.setdefault(b, {}).setdefault(ch, {})[str(t)] = kf([round(x, 3) for x in v])
    for b, ch in (extra or {}).items():
        bones.setdefault(b, {}).update(ch)
    return {"loop": True, "animation_length": T, "bones": bones}

def tetrapod(legs, offset=0.0):
    """Alternating tetrapod gait (L1 R2 L3 R4 | R1 L2 R3 L4)."""
    ph = {}
    for lg in legs:
        grp = (lg.i + (0 if lg.s > 0 else 1)) % 2
        ph[lg.bones[0]] = (0.5 * grp + offset * lg.i) % 1.0
    return ph

# ============================================================================ claws, antennae, tail
def claw(m, side, s, *, parent, shoulder, arm, wrist, palm, finger, pincer, paints, arm_rot=(0, 0, 0),
         wrist_rot=(0, 0, 0), claw_rot=(0, 0, 0), extra_palm=()):
    """Cheliped. Dimensions are (width x, height y, length z) boxes laid forward (-Z) from each hinge;
    finger = fixed finger (inner side), pincer = movable finger (outer side, opens by yaw).
    Bones: arm_{side} > wrist_{side} > claw_{side} > pincer_{side}."""
    x, y, z = shoulder
    aw, ah, al = arm
    m.bone(f"arm_{side}", parent, [x, y, z], rotation=list(arm_rot), cubes=[
        Cube([x - aw / 2, y - ah / 2, z - al], [aw, ah, al], paints["arm"])])
    z1 = z - al
    ww, wh, wl = wrist
    m.bone(f"wrist_{side}", f"arm_{side}", [x, y, z1], rotation=list(wrist_rot), cubes=[
        Cube([x - ww / 2, y - wh / 2, z1 - wl], [ww, wh, wl], paints["wrist"])])
    z2 = z1 - wl
    pw, ph, pl = palm
    fw, fh, fl = finger
    cubes = [Cube([x - pw / 2, y - ph / 2, z2 - pl], [pw, ph, pl], paints["palm"])]
    xi = x - s * (pw / 2 - fw / 2)                      # fixed finger on the inner side
    cubes.append(Cube([xi - fw / 2, y - ph / 2, z2 - pl - fl], [fw, fh, fl], paints["finger"]))
    cubes.extend(extra_palm)
    m.bone(f"claw_{side}", f"wrist_{side}", [x, y, z2], rotation=list(claw_rot), cubes=cubes)
    qw, qh, ql = pincer
    xo = x + s * (pw / 2 - qw / 2)
    yo = y - ph / 2 + fh                                 # movable finger sits on top / outside
    m.bone(f"pincer_{side}", f"claw_{side}", [xo, y, z2 - pl], cubes=[
        Cube([xo - qw / 2, y - ph / 2, z2 - pl - ql], [qw, qh, ql], paints["pincer"])])

def antenna(m, side, s, *, parent, base, segs, thick=1, paint=None, rest=None):
    """Chain of segments laid forward (-Z) from base; rest = [(rx, ry, rz)] per segment (curve)."""
    x, y, z = base
    prev = parent
    names = []
    for k, L in enumerate(segs):
        name = f"antenna_{side}{k + 1}"
        r = rest[k] if rest else (0, 0, 0)
        t = thick[k] if isinstance(thick, (list, tuple)) else thick
        pt = paint[k] if isinstance(paint, (list, tuple)) else paint
        m.bone(name, prev, [x, y, z], rotation=[r[0], r[1] * s, r[2] * s], cubes=[
            Cube([x - t / 2, y - t / 2, z - L - (1 if k else 0)], [t, t, L + (1 if k else 0)], pt)])
        prev, z = name, z - L
        names.append(name)
    return names

def abdomen(m, *, parent, start, segs, paints, fan_size, fan_paint, rest=-6):
    """Segmented tail laid back (+Z) from `start`; segs = [(w, h, L)]; ends with the tail fan."""
    x, y, z = start
    prev = parent
    names = []
    for k, (w, h, L) in enumerate(segs):
        name = f"tail{k + 1}"
        m.bone(name, prev, [x, y, z], rotation=[rest, 0, 0], cubes=[
            Cube([x - w / 2, y - h / 2, z - (0.5 if k else 0) * 0], [w, h, L], paints[k % len(paints)])])
        prev, z = name, z + L
        names.append(name)
    fw, fl = fan_size
    m.bone("tail_fan", prev, [x, y, z], rotation=[rest, 0, 0], cubes=[
        Cube([x - fw / 2, y - segs[-1][1] / 2 + 0.3, z - 0.5], [fw, 0, fl], fan_paint)])
    names.append("tail_fan")
    return names

# ============================================================================ animations
def crust_anims(sid, m, legs, *, pivot, cfg):
    """cfg: walk(dict T, stride, lift, yaw, stance), scale, body_h (rest body pivot height), claws=(left, right),
    antennae=[names per side], tail=[names], eyes=(eye_left, eye_right), stalks, battle, cry, sleep_drop, heavy,
    ride (bool)."""
    a = f"animation.{sid}."
    q = "q.anim_time"
    out = {}
    names = {b.name for b in m.bones}
    has = lambda n: n in names
    sc = cfg.get("scale", 1.0)
    ants = cfg.get("antennae", {})
    tail = cfg.get("tail", [])
    eyes = cfg.get("eyes", ("eye_left", "eye_right"))
    heavy = cfg.get("heavy", False)

    def ant_wave(amp=1.0, speed=1.0, base=(0, 0)):
        ch = {}
        for side, s in SIDES:
            for k, n in enumerate(ants.get(side, [])):
                f = round(90 * speed, 3)
                ph = 35 * k + (0 if s > 0 else 70)
                ch[n] = {"rotation": [f"{base[0]}+math.sin({q}*{f}-{ph})*{round(4 * amp * (0.6 + 0.25 * k), 2)}",
                                      f"{round(base[1] * s, 2)}+math.sin({q}*{round(f * 0.7, 3)}-{ph + 20})*{round(5 * amp * (0.6 + 0.25 * k), 2)}", 0]}
        return ch

    def tail_wave(amp=1.0, speed=1.0, base=0.0):
        return {n: {"rotation": [f"{base}+math.sin({q}*{round(90 * speed, 3)}-{40 * k})*{round(amp * (1 + 0.3 * k), 2)}", 0, 0]}
                for k, n in enumerate(tail)}

    def claw_pose(side, s, arm=(0, 0, 0), wrist=(0, 0, 0), clw=(0, 0, 0), open_=0.0):
        return {f"arm_{side}": {"rotation": [arm[0], arm[1] * s, arm[2] * s]},
                f"wrist_{side}": {"rotation": [wrist[0], wrist[1] * s, wrist[2] * s]},
                f"claw_{side}": {"rotation": [clw[0], clw[1] * s, clw[2] * s]},
                f"pincer_{side}": {"rotation": [0, -s * open_, 0]}}

    # ---------------------------------------------------------------- idle: antennae sway, claws flex, a little snap
    def idle_pose(t):
        br = math.sin(math.radians(t * 90))
        p = legs_for_body(legs, pivot, (0.6 * br, 0, 0), (0, 0.08 * br * sc, 0))
        p["body"] = {"rotation": [0.6 * br, 0, 0], "position": [0, 0.08 * br * sc, 0]}
        snap = [(0, 0), (2.2, 0), (2.35, 1), (2.5, 0.1), (2.62, 0.8), (2.8, 0), (8, 0)]
        for side, s in SIDES:
            sw = math.sin(math.radians(t * 45 + (0 if s > 0 else 120)))
            o = lerp_keys(snap, t) * (1 if s > 0 else 0.4) * cfg.get("snap", 22)
            p.update(claw_pose(side, s, arm=(2 * sw, 2 * sw, 0), wrist=(0, 3 * sw, 0), clw=(-3 * sw, 0, 0), open_=4 + o))
        if has("head"):
            p["head"] = {"rotation": [0.8 * br, 2.5 * math.sin(math.radians(t * 45)), 0]}
        for side, s in SIDES:
            if has(f"stalk_{side}"):
                p[f"stalk_{side}"] = {"rotation": [4 * math.sin(math.radians(t * 90 + 40 * s)),
                                                   8 * math.sin(math.radians(t * 45 + 60 * s)), 0]}
        return p
    idle = sampled(8, 0.05, idle_pose, loop=True)
    idle.update(ant_wave(1.0, 1.0))
    idle.update(tail_wave(1.2, 1.0, base=0))
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": idle}

    # ---------------------------------------------------------------- walk (sideways trot for the light one)
    W = dict(T=0.6, stride=4, lift=1.5, yaw=0.0, stance=0.55, bob=0.15)
    W.update(cfg.get("walk", {}))
    yaw = W["yaw"]
    tr = (math.sin(math.radians(0)), -1.0)
    def body_w(u):
        b = math.sin(4 * math.pi * u)
        return ((0.8 * b if heavy else 0.4 * b, 0, (1.5 if heavy else 0.8) * math.sin(2 * math.pi * u)),
                (0, W["bob"] * sc * (0.5 + 0.5 * b), 0))
    ex = {}
    ex.update(ant_wave(1.4, 2.0, base=(-4, 0)))
    ex.update(tail_wave(1.0, 2.0))
    f = round(360 / W["T"], 3)
    for side, s in SIDES:
        ex[f"arm_{side}"] = {"rotation": [f"math.sin({q}*{f})*2", f"{s}*math.sin({q}*{f}+90)*3", 0]}
        ex[f"pincer_{side}"] = {"rotation": [0, f"{-s}*(4+math.sin({q}*{2 * f})*2)", 0]}
    out[a + "ground_walk"] = crab_walk(legs, pivot, T=W["T"], stride=W["stride"], lift=W["lift"], travel=(0.0, -1.0),
                                       phases=tetrapod(legs, W.get("ripple", 0.06)), stance=W["stance"],
                                       body=body_w, extra=ex, yaw=yaw)

    # ---------------------------------------------------------------- battle: low stance, claws up and open
    B = dict(dy=-1.0, pitch=-6, arm=(-30, 18, 0), wrist=(-10, 10, 0), clw=(-10, 0, 0), open_=26)
    B.update(cfg.get("battle", {}))
    def battle_pose(t):
        w = math.sin(math.radians(t * 180))
        p = legs_for_body(legs, pivot, (B["pitch"] + 1.2 * w, 0, 1.5 * math.sin(math.radians(t * 90))),
                          (0, (B["dy"] + 0.15 * w) * sc, 0), spread=1.08)
        p["body"] = {"rotation": [B["pitch"] + 1.2 * w, 0, 1.5 * math.sin(math.radians(t * 90))],
                     "position": [0, (B["dy"] + 0.15 * w) * sc, 0]}
        snap = max(0.0, math.sin(math.radians(t * 360 * 1.5))) ** 6
        for side, s in SIDES:
            ph = 0 if s > 0 else 90
            ww = math.sin(math.radians(t * 180 + ph))
            p.update(claw_pose(side, s, arm=(B["arm"][0] + 4 * ww, B["arm"][1] + 3 * ww, B["arm"][2]),
                               wrist=B["wrist"], clw=B["clw"], open_=B["open_"] - 24 * snap * (1 if s > 0 else 0)))
        for b, fn in cfg.get("battle_extra", {}).items():
            p[b] = fn(t)
        return p
    battle = sampled(4, 0.05, battle_pose, loop=True)
    battle.update(ant_wave(1.6, 2.0, base=(-10, 8)))
    battle.update(tail_wave(1.5, 2.0, base=cfg.get("battle_tail", 6)))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": battle}

    # ---------------------------------------------------------------- cry: rears up, claws raised, snaps
    C = dict(L=1.4, rear=-12, dy=0.6, arm=(-50, 24, 0), clack=((0.45, 0.6), (0.75, 0.9)), open_=34)
    C.update(cfg.get("cry", {}))
    def cry_pose(t):
        L = C["L"]
        e = smooth(t / 0.3) if t < 0.3 else (1.0 if t < L - 0.35 else 1 - smooth((t - (L - 0.35)) / 0.35))
        cl = 0.0
        for t0, t1 in C["clack"]:
            if t0 <= t <= t1:
                cl = math.sin(math.pi * (t - t0) / (t1 - t0))
        p = legs_for_body(legs, pivot, (C["rear"] * e, 0, 0), (0, C["dy"] * e * sc, 0))
        p["body"] = {"rotation": [C["rear"] * e, 0, 0], "position": [0, C["dy"] * e * sc, 0]}
        for side, s in SIDES:
            p.update(claw_pose(side, s, arm=(C["arm"][0] * e, C["arm"][1] * e, 0), wrist=(-10 * e, 8 * e, 0),
                               clw=(-12 * e, 0, 0), open_=4 + (C["open_"] * e) * (1 - cl)))
        for side, s in SIDES:
            for k, n in enumerate(ants.get(side, [])):
                p[n] = {"rotation": [-14 * e * (1 if k == 0 else 0.4) + 6 * cl, s * 10 * e, 0]}
        for k, n in enumerate(tail):
            p[n] = {"rotation": [8 * e if k == 0 else 4 * e, 0, 0]}
        return p
    out[a + "cry"] = {"animation_length": C["L"], "bones": sampled(C["L"], 0.05, cry_pose)}

    # ---------------------------------------------------------------- sleep: settled low, claws tucked, antennae down
    S = dict(drop=-0.8, spread=1.25, arm=(0, -22, 0), wrist=(10, -30, 0), clw=(14, 0, 0))
    S.update(cfg.get("sleep", {}))
    body_h = cfg["body_h"]
    best = None
    for dy in rng(0, -body_h, 40):
        p = legs_for_body(legs, pivot, (2, 0, 0), (0, dy, 0), spread=S["spread"])
        p["body"] = {"rotation": [2, 0, 0], "position": [0, dy, 0]}
        lo = lowest(m, p, skip=set(n for side in ants for n in ants[side]) | set(tail) | {b for b in names if b.startswith(("arm", "wrist", "claw", "pincer"))})
        if lo >= -0.03:
            best = (dy, p)
    dy, sp = best
    for side, s in SIDES:
        sp.update(claw_pose(side, s, arm=S["arm"], wrist=S["wrist"], clw=S["clw"], open_=0))
    # claws laid down: the lowest arm pitch that keeps the claw on (not in) the ground
    for side, s in SIDES:
        grp = descendants(m, f"arm_{side}")
        ok = None
        for ax in rng(-70, 70, 57):
            pp = copy_pose(sp)
            pp[f"arm_{side}"]["rotation"][0] = ax
            if lowest(m, pp, only=grp) >= 0.05:
                ok = ax
        if ok is not None:
            sp[f"arm_{side}"]["rotation"][0] = ok
    sleep = {b: dict(ch) for b, ch in sp.items()}
    sleep["torso"] = {"rotation": [f"math.sin({q}*45)*0.6", 0, 0]}
    for side, s in SIDES:
        for k, n in enumerate(ants.get(side, [])):
            sleep[n] = {"rotation": [f"{12 if k == 0 else 4}+math.sin({q}*30-{30 * k})*1.5", s * 6, 0]}
        if has(f"stalk_{side}"):
            sleep[f"stalk_{side}"] = {"rotation": [35, s * 15, 0]}
    for e in eyes:
        sleep[e] = {"scale": [1, 0.15, 1]}
    for k, n in enumerate(tail):
        sleep[n] = {"rotation": [4 + (2 if k else 0), 0, 0]}
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sleep}

    # ---------------------------------------------------------------- blink
    out[a + "blink"] = {"animation_length": 0.25, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.15, 1], "0.25": [1, 1, 1]}} for e in eyes}}

    # ---------------------------------------------------------------- faint: recoil, legs give way, rolls over
    k0 = legs_for_body(legs, pivot)
    k1 = merge(legs_for_body(legs, pivot, (-10, 0, 0), (0, 0.6 * sc, 0)), {"body": {"rotation": [-10, 0, 0], "position": [0, 0.6 * sc, 0]}})
    for side, s in SIDES:
        k1.update(claw_pose(side, s, arm=(-35, 25, 0), wrist=(-10, 10, 0), open_=30))
    k2 = merge(copy_pose(sp), {"body": {"rotation": [6, 0, 8], "position": [0, dy, 0]}})
    for side, s in SIDES:
        k2.update(claw_pose(side, s, arm=(25, 10, 0), wrist=(0, -10, 0), open_=12))
    curl = {}
    for lg in legs:
        curl[lg.bones[0]] = {"rotation": [0, 8 * lg.s * (lg.i - 2), 0]}
        curl[lg.bones[1]] = {"rotation": [0, 0, -lg.s * 35]}
        curl[lg.bones[2]] = {"rotation": [0, 0, lg.s * 70]}
    k3 = merge(copy_pose(k2), curl, {"body": {"rotation": [8, 15, cfg.get("roll", 75)], "position": [0, 0, 0]}})
    for side, s in SIDES:
        k3.update(claw_pose(side, s, arm=(20, -10 if s > 0 else 30, 0), wrist=(0, -20, 0), open_=18))
    for side, s in SIDES:
        for k, n in enumerate(ants.get(side, [])):
            for kp, v in ((k1, -12), (k2, 10), (k3, 14)):
                kp[n] = {"rotation": [v if k == 0 else v * 0.4, s * 12, 0]}
    k4 = copy_pose(k3)
    for lg in legs:
        k4[lg.bones[2]] = {"rotation": [0, 0, lg.s * 85]}
    seq = [(0, k0), (0.3, k1), (0.8, k2), (1.6, k3), (2.1, k4), (2.6, k3), (3.0, k4)]
    fb = pose_sequence(m, seq, length=3.0, skip=set(cfg.get("faint_skip", ())))
    for e in eyes:
        fb[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.5, 1], 0.6: [1, 1, 1], 1.5: [1, 1, 1], 1.8: [1, 0.15, 1], 3.0: [1, 0.15, 1]})
    out[a + "faint"] = {"animation_length": 3.0, "bones": fb}

    # ---------------------------------------------------------------- water: float (legs paddle) and swim (tail beats)
    def float_pose(t):
        w = math.sin(math.radians(t * 120))
        p = {"body": {"rotation": [2 * w, 0, 1.5 * math.sin(math.radians(t * 60))], "position": [0, 0.3 * w * sc, 0]}}
        for lg in legs:
            ph = 40 * lg.i + (0 if lg.s > 0 else 90)
            p[lg.bones[0]] = {"rotation": [0, 10 * math.sin(math.radians(t * 240 - ph)), 0]}
            p[lg.bones[1]] = {"rotation": [0, 0, -lg.s * (10 + 8 * math.sin(math.radians(t * 240 - ph)))]}
            p[lg.bones[2]] = {"rotation": [0, 0, lg.s * (-10 + 6 * math.sin(math.radians(t * 240 - ph - 50)))]}
        for side, s in SIDES:
            p.update(claw_pose(side, s, arm=(-8, 10, 0), wrist=(0, 6, 0), open_=6 + 4 * w))
        return p
    fl = sampled(3, 0.05, float_pose, loop=True)
    fl.update(ant_wave(1.8, 1.0, base=(-6, 10)))
    fl.update(tail_wave(4.0, 1.33, base=-4))
    out[a + "water_idle"] = {"loop": True, "animation_length": 3, "bones": fl}
    SW = cfg.get("swim_T", 0.9)
    fq = round(360 / SW, 3)
    sw = {"body": {"rotation": [f"-4+math.sin({q}*{fq})*3", 0, 0], "position": [0, f"math.sin({q}*{fq}-60)*{0.5 * sc}", 0]}}
    for lg in legs:
        sw[lg.bones[0]] = {"rotation": [0, f"{-lg.s * 25}", 0]}          # legs swept back along the body
        sw[lg.bones[1]] = {"rotation": [0, 0, f"{-lg.s}*(20+math.sin({q}*{fq}-{30 * lg.i})*6)"]}
        sw[lg.bones[2]] = {"rotation": [0, 0, f"{lg.s * -30}"]}
    for side, s in SIDES:
        sw.update({k: {"rotation": [v["rotation"][0], v["rotation"][1], v["rotation"][2]]}
                   for k, v in claw_pose(side, s, arm=(-6, -14, 0), wrist=(0, -12, 0), clw=(0, -6, 0), open_=2).items()})
    for k, n in enumerate(tail):
        sw[n] = {"rotation": [f"math.sin({q}*{fq}-{50 * k})*{8 + 5 * k}", 0, 0]}
    sw.update(ant_wave(1.0, 2.5, base=(4, -14)))
    out[a + "water_swim"] = {"loop": True, "animation_length": SW, "bones": sw}
    # ---------------------------------------------------------------- portrait: claws lowered and spread so the face shows
    P_ = cfg.get("portrait_claws", (0, -30, 0))
    pp = legs_for_body(legs, pivot)
    for side, s in SIDES:
        pp.update(claw_pose(side, s, arm=P_, wrist=(0, -10, 0), open_=8))
    pb = {b: dict(ch) for b, ch in pp.items()}
    pb.update(ant_wave(0.8, 1.0, base=cfg.get("portrait_ant", (0, 0))))
    if cfg.get("portrait_yaw"):
        pb["body"] = {"rotation": [0, cfg["portrait_yaw"], 0]}
    out[a + "portrait"] = {"loop": True, "animation_length": 8, "bones": pb}
    out[a + "_sleep_pose"] = sp
    return out

def crust_poser(sid, portrait, profile, *, ride=False):
    qb = lambda n: f"q.bedrock('{sid}', '{n}')"
    blink = [f"q.bedrock_quirk('{sid}', 'blink')"]
    look = "q.look('head')"
    nr = {"condition": "!q.is_ridden"} if ride else {}
    poses = {
        "battle-standing": {"poseTypes": ["STAND"], "isBattle": True, "isUnderWater": False,
                            "animations": [look, qb("battle_idle")], "quirks": blink},
        "underwater-battle": {"poseTypes": ["STAND", "FLOAT"], "isBattle": True, "isUnderWater": True,
                              "animations": [look, qb("water_idle")], "quirks": blink},
        "portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "animations": [qb("portrait")], "quirks": blink},
        "standing": {"poseTypes": ["STAND", "NONE"], "isBattle": False, "isUnderWater": False, **nr,
                     "animations": [look, qb("ground_idle")], "quirks": blink},
        "walking": {"poseTypes": ["WALK"], "isUnderWater": False, **nr, "animations": [look, qb("ground_walk")], "quirks": blink},
        "float": {"poseTypes": ["FLOAT", "STAND"], "isTouchingWater": True, "isUnderWater": True, **nr,
                  "animations": [look, qb("water_idle")], "quirks": blink},
        "swim": {"poseTypes": ["SWIM", "WALK"], "isTouchingWater": True, **nr, "animations": [look, qb("water_swim")],
                 "quirks": blink},
        "sleep": {"poseTypes": ["SLEEP"], "animations": [qb("sleep")]},
    }
    if ride:
        poses.update({
            "mount_idle": {"poseTypes": ["STAND", "NONE"], "isBattle": False, "isUnderWater": False, "condition": "q.is_ridden",
                           "animations": [look, qb("ground_idle")], "quirks": blink},
            "mount_walk": {"poseTypes": ["WALK"], "isUnderWater": False, "condition": "q.is_ridden",
                           "animations": [look, qb("ground_walk")], "quirks": blink},
            "mount_float": {"poseTypes": ["FLOAT", "STAND"], "isTouchingWater": True, "isUnderWater": True,
                            "condition": "q.is_ridden", "animations": [look, qb("water_idle")], "quirks": blink},
            "mount_swim": {"poseTypes": ["SWIM", "WALK", "FLOAT"], "isTouchingWater": True, "condition": "q.is_ridden",
                           "animations": [qb("water_swim")], "quirks": blink},
        })
    out = {"portraitScale": portrait[0], "portraitTranslation": portrait[1],
           "profileScale": profile[0], "profileTranslation": profile[1], "rootBone": sid}
    if ride:
        out["firstPersonCameraOffset"] = {"seat_1": [0, 0.45, 0]}
        out["thirdPersonCameraOffset"] = {"seat_1": [0, 0.5, 0], "seat_1_reverse": [0, 0.5, 0]}
    out["animations"] = {"cry": f"q.bedrock_stateful('{sid}', 'cry')",
                         "faint": f"q.bedrock_primary('{sid}', 'faint', q.curve('one'))"}
    out["poses"] = poses
    return out
