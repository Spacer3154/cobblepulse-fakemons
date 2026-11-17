# -*- coding: utf-8 -*-
"""Bird rig for the Étreroch line (shore-bird -> chalk-arch bird -> cliff gargoyle).

Legs are biped.Leg (femur hidden forward in the belly, tibiotarsus back to the 'heel', tarsus down to the toes),
so feet stay planted with IK in walks and stances. Wings exist twice, like Cobblemon's own birds: folded wings
for the ground poses and spread wings (arm + hand, feather planes) for flight; the poser toggles their visibility.
Painting works on texel positions (fn3) with ordered region rules, which suits a plover's crisp bands
(white forehead, black fore-crown and mask, white collar, black breast band)."""
import math
from modelgen import Cube, fill, shade, mix, FACE_LIGHT, apply
from biped import Leg, walk, keys, kf, smooth, lowest, descendants, pose_sequence, search, leg_pose
from bovine import (vnoise, put, light, plane_pattern, side_cols, EYE_KEYS, plant, stance, legs_pose, copy_pose,
                    merge, sampled, lerp_keys, fold_leg, rng, finalize)

EYE_KEYS.update({"R": "eye_ring", "A": "eye_hot", "B": "brow"})
SIDES = (("left", 1), ("right", -1))
# Wing directions (game convention, see modelgen): s = +1 left wing (+X), -1 right wing.
#   Z: +s*a lowers the wing tip, -s*a raises it.   Y: -s*a sweeps the tip back (towards the tail), +s*a forward.
#   For a folded wing (lying along +Z), Y = +s*a swings its back end outward, away from the body.
HIDE_OPEN = {f"wing_open_{side}": {"scale": 0} for side, _ in SIDES}       # ground animations (as Cobblemon's birds)
HIDE_CLOSED = {f"wing_closed_{side}": {"scale": 0} for side, _ in SIDES}   # flight animations

# ============================================================================ painters
def regions(rules, *, base, seed=1, scallop=0.0, strata=None, noise=4, grad=0.1):
    """fn3 painter. rules: [(pred(p, face) -> bool, key)], the last matching rule wins (else `base`).
    scallop: feather-edge shading strength; strata=(keys, spacing): darker chalk / flint seams along y."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            key = base
            for pred, k in rules:
                if pred(p, face):
                    key = k
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, grad)
            col = pal[key]
            if scallop and key not in ("flint", "flint_dark", "eye", "beak", "beak_tip", "leg"):
                if (math.floor(p[2] * 1.0) + 2 * math.floor(p[1] * 0.5) + (1 if face in ("up", "down") else 0)) % 3 == 0:
                    f *= 1 - scallop
            if strata and key in strata[0]:
                if abs((p[1] + 0.25 * math.sin(p[2] * 0.7 + p[0])) % strata[1]) < 0.55:
                    col = mix(col, pal["strata"], 0.55)
            put(px, X, Y, col, f, rnd, noise)
    return {"fn3": fn3}

def flint(px, faces, pal, rnd):
    """Knapped flint: blue-black with conchoidal ripples and a few sharp glints."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                r = rnd.random()
                c = pal["flint_light"] if r < 0.12 else pal["flint_dark"] if r < 0.32 else pal["flint"]
                put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 2)
        if w >= 2 and h >= 2:
            px[x + rnd.randrange(w), y] = pal["flint_glint"]

def solid(key, noise=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            fill(px, x, y, w, h, pal[key], FACE_LIGHT[fc], rnd, noise)
    return fn

def gradient(k0, k1, axis="y", invert=False):
    """Colour ramp along a face (e.g. orange bill to a flint tip)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if axis == "y":
                        t = j / max(h - 1, 1)
                    else:
                        t = i / max(w - 1, 1)
                    t = 1 - t if invert else t
                    put(px, x + i, y + j, mix(pal[k0], pal[k1], t), FACE_LIGHT[fc], rnd, 3)
    return fn

def feathers(*, root_x, tip_x, lead_z, chord, keys=("covert", "secondary", "primary"), bar="wing_bar",
             arch=None, notch=3, seed=3, primary_from=0.55):
    """Spread-wing feather plane (horizontal, faces up/down) painted in model space (fn3):
    coverts along the leading edge, a pale wing bar, secondaries, dark primaries on the outer hand, feather
    separations and a ragged trailing edge (transparent notches). arch=(centre 0..1 of span, half width, height in
    units): a natural arch cut through the inner wing (Étretat's Porte d'Aval), outlined in dark stone."""
    cov, sec, pri = keys
    span = tip_x - root_x
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            if face not in ("up", "down"):
                px[X, Y] = (0, 0, 0, 0)
                continue
            s = (p[0] - root_x) / span                       # 0 at the root, 1 at the tip
            dz = p[2] - lead_z                              # depth behind the leading edge
            u = dz / chord
            fx_ = math.floor(abs(p[0]))
            tipcut = 1.0 - 0.18 * ((fx_ % notch) / max(notch - 1, 1))      # ragged trailing edge
            if arch and abs(p[0] - (root_x + arch[0] * span)) < arch[1] + 1.0:
                tipcut = 1.0                                # solid stone sill under the arch
            if s > 0.85:
                tipcut -= (s - 0.85) * 2.2                  # rounded wing tip
            if u > tipcut:
                px[X, Y] = (0, 0, 0, 0)
                continue
            if arch:                                        # arch-shaped window: rounded top towards the
                ac, hw, ah = arch                           # leading edge, sill one row from the trailing edge
                xc = root_x + ac * span
                sill, topz = chord - 1.0, chord - 1.0 - ah
                dx = abs(p[0] - xc)
                def is_in(dx_, dz_):
                    if not (dx_ < hw and topz < dz_ < sill):
                        return False
                    return not (dz_ < topz + 1.0 and dx_ > hw - 1.0)      # rounded shoulders
                if is_in(dx, dz):
                    px[X, Y] = (0, 0, 0, 0)
                    continue
                if any(is_in(dx + ox, dz + oz) for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    put(px, X, Y, pal["arch_rim"], 1.0 if face == "up" else 0.85, rnd, 2)
                    continue
            if u < 0.28:
                key = cov
            elif u < 0.4:
                key = bar
            else:
                key = pri if s > primary_from else sec
            f = 1.0 if face == "up" else 0.82
            if fx_ % notch == 0 and u > 0.35:
                f *= 0.8                                    # feather separation
            put(px, X, Y, pal[key], f, rnd, 4)
    return {"fn3": fn3}

def folded_primaries(key="primary", edge="primary_edge", notch=2):
    """Closed-wing primaries on a vertical plane (faces east/west), tips ragged towards the back."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if fc not in ("east", "west"):
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            cols = side_cols(fc, w)                         # from the front
            for j in range(h):
                for k in range(w):
                    back = k / max(w - 1, 1)
                    lim = h - 1 - int(back * (h - 1) * 0.7) - (k % notch)
                    if j > lim:
                        px[x + cols[k], y + j] = (0, 0, 0, 0)
                        continue
                    c = pal[edge] if j == lim or k % notch == 0 else pal[key]
                    put(px, x + cols[k], y + j, c, 1.0, rnd, 3)
    return fn

def tail_fan(key="tail", band="tail_band", tip="tail_tip"):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    c = pal[key]
                    if fc in ("up", "down") and j <= 1:            # row 0 = back: dark band, pale tip
                        c = pal[tip] if j == 0 else pal[band]
                    put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)
    return fn

def bird_lids(x_edge, y0, h, z0, d, lash_row=None):
    """coat extra / region rule helper: closed eyelids painted on the head sides under the eye planes."""
    mid = y0 + h / 2 if lash_row is None else y0 + h - lash_row - 0.5
    def rule_lid(p, face):
        return face in ("east", "west") and abs(abs(p[0]) - x_edge) < 0.05 and y0 - 0.01 <= p[1] <= y0 + h + 0.01 \
            and z0 - 0.01 <= p[2] <= z0 + d + 0.01
    def rule_lash(p, face):
        return rule_lid(p, face) and abs(p[1] - mid) <= 0.5
    return [(rule_lid, "lid"), (rule_lash, "lash")]

def eye_ring_rules(x_edge, y0, h, z0, d, key="eye_ring", width=1.0, sides_only=False, **_):
    """A ring painted on the head sides around the eye plane (corners left out so it reads round)."""
    def ring(p, face):
        if face not in ("east", "west") or abs(abs(p[0]) - x_edge) > 0.05:
            return False
        iny = y0 - width <= p[1] <= y0 + h + width
        inz = z0 - width <= p[2] <= z0 + d + width
        core = y0 <= p[1] <= y0 + h and z0 <= p[2] <= z0 + d
        corner = (p[1] < y0 or p[1] > y0 + h) and (p[2] < z0 or p[2] > z0 + d)
        if sides_only:                                   # thin ring: only above / below and at the front
            return iny and inz and not core and not corner and not (p[2] > z0 + d)
        return iny and inz and not core and not corner
    return [(ring, key)]

def add_side_eyes(m, parent, *, x_edge, y0, h, z0, d, rows, key_fn=None, glow=False):
    """Bird eyes: a d x h plane just outside each side of the head (rows counted from the front)."""
    paint = {"fn": plane_pattern(rows, ("east", "west"), "front")}
    if glow:
        paint.update(glow=True, shading=False)
    for side, sx in SIDES:
        xs = x_edge + 0.03 if sx > 0 else -x_edge - 0.03
        m.bone(f"eye_{side}", parent, [xs, y0 + h / 2, z0 + d / 2], cubes=[Cube([xs, y0, z0], [0, h, d], paint)])

# ============================================================================ leg poses
def tucked(legs, a=(-25, 105, 150, 60)):
    """Legs folded back under the tail for flight."""
    return legs_pose(legs, {lg.side: a for lg in legs})

def perched(m, legs, trunk, theta=0.0):
    """Sitting on the belly, tarsi flat on the ground pointing forward (birds rest on their 'heels')."""
    pose = {"body": {"rotation": [theta, 0, 0], "position": [0, 0, 0]}}
    pose["body"]["position"][1] = -lowest(m, pose, only=trunk) + 0.02
    for lg in legs:
        group = set(lg.bones)
        best = None
        for a1 in rng(-130, -20, 23):
            for a2 in rng(40, 175, 16):
                for a3 in rng(-120, -40, 9):
                    ang = (a1, a2, a3, a3 + 5)
                    p = dict(pose)
                    for b, d in zip(lg.bones, lg.deltas(ang)):
                        p[b] = {"rotation": [d, 0, 0]}
                    lo = lowest(m, p, only=group)
                    sc = 10 * max(0.0, -lo) + abs(lo - 0.1) + 0.004 * (abs(a1 + 70) + abs(a2 - 120) + abs(a3 + 85))
                    if best is None or sc < best[0]:
                        best = (sc, ang)
        for b, d in zip(lg.bones, lg.deltas(best[1])):
            pose[b] = {"rotation": [d, 0, 0]}
    pose["body"]["position"][1] += -min(0.0, lowest(m, pose, skip={b.name for b in m.bones if b.name.startswith("wing_open")})) + 0.02
    return pose

# ============================================================================ geometry tests
def _inv(mt):
    """inverse of a rigid 4x4 (rotation + translation)"""
    r = [[mt[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][k] * mt[k][3] for k in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0, 0, 0, 1]]

def _samples(c):
    o, sz = c.origin, c.size
    pts = []
    for fx in (0, 0.5, 1):
        for fy in (0, 0.5, 1):
            for fz in (0, 0.5, 1):
                pts.append((o[0] + sz[0] * fx, o[1] + sz[1] * fy, o[2] + sz[2] * fz))
    return pts

def sleep_score(m, pose, head_grp, solid_bones, style="back"):
    mats = m.mats(pose)
    bones = {b.name: b for b in m.bones}
    hp = [apply(mats[n], p) for n in head_grp for c in bones[n].cubes if all(v > 0 for v in c.size) for p in _samples(c)]
    inside, tops = 0, []
    xs, zs = [p[0] for p in hp], [p[2] for p in hp]
    for n in solid_bones:
        inv = _inv(mats[n])
        for c in bones[n].cubes:
            if not all(v > 0 for v in c.size):
                continue
            lo = [c.origin[i] + 0.35 for i in range(3)]
            hi = [c.origin[i] + c.size[i] - 0.35 for i in range(3)]
            for p in hp:
                q = apply(inv, p)
                if all(lo[i] < q[i] < hi[i] for i in range(3)):
                    inside += 1
            for q in _samples(c):                       # body surface under the head
                w = apply(mats[n], q)
                if min(xs) - 0.5 <= w[0] <= max(xs) + 0.5 and min(zs) - 0.5 <= w[2] <= max(zs) + 0.5:
                    tops.append(w[1])
    hmin = min(p[1] for p in hp)
    sc = 40.0 * inside
    if style == "statue":
        if hmin < 0.05:
            sc += 100.0
        hc = apply(mats["head"], bones["head"].pivot)
        r = pose["neck"]["rotation"], pose["head"]["rotation"]
        return sc + 0.35 * hc[1] + 0.01 * (abs(r[0][0]) + abs(r[1][0]))
    if "beak" in bones:                                 # bill laid on the back, not in the air
        bp = [apply(mats["beak"], p) for c in bones["beak"].cubes if all(v > 0 for v in c.size) for p in _samples(c)]
        if tops:
            sc += 1.5 * abs(min(p[1] for p in bp) - (max(tops) - 0.3))
    if tops:
        sc += 3.0 * abs(hmin - (max(tops) - 0.6))      # resting on the back / shoulders
    else:
        sc += 30.0                                      # head off the body
    if hmin < 0.05:
        sc += 100.0
    hz = apply(mats["head"], bones["head"].pivot)[2]
    if "beak" in bones:
        bz = apply(mats["beak"], bones["beak"].pivot)[2]
        sc += 2.0 * max(0.0, 2.5 - (bz - hz))          # bill pointing to the tail
    r = pose["neck"]["rotation"], pose["head"]["rotation"]
    sc += 0.01 * (abs(r[0][0]) + abs(r[1][0])) + 0.004 * abs(r[1][1] - 170)
    return sc

# ============================================================================ wing motion
def flap(T, amp=55.0, up=12.0, hand=1.25, lag=40.0, sweep=18.0, pivot_up=0.0):
    """Molang flap for the spread wings: shoulder (Z), hand lagging behind, hand sweeping back on the upstroke."""
    q = "q.anim_time"
    f = round(360 / T, 3)
    out = {}
    for side, s in SIDES:
        # shoulder Z = s*(sin*amp - up): the wing goes down while cos > 0 (downstroke), reaching forward (Y)
        out[f"wing_open_{side}"] = {"rotation": [f"math.cos({q}*{f})*3", f"{s}*math.cos({q}*{f})*{round(sweep * 0.35, 1)}",
                                                 f"{s}*(math.sin({q}*{f})*{amp}-{up})"]}
        # hand: follows with a lag and folds back during the upstroke
        out[f"wing_open_{side}2"] = {"rotation": [0, f"{-s}*math.clamp(-math.cos({q}*{f}-{lag}),0,1)*{sweep}",
                                                  f"{s}*math.sin({q}*{f}-{lag})*{round(amp * (hand - 1) + 8, 1)}"]}
    return out

def glide_wings(sway=4.0, T=4.0):
    q = "q.anim_time"
    f = round(360 / T, 3)
    out = {}
    for side, s in SIDES:
        out[f"wing_open_{side}"] = {"rotation": [f"math.sin({q}*{f})*1.5", -s * 4, f"{s}*(-6+math.sin({q}*{f}+{90 * s})*{sway})"]}
        out[f"wing_open_{side}2"] = {"rotation": [0, -s * 6, f"{s}*(2+math.sin({q}*{f}+40)*{sway * 0.6})"]}
    return out

# ============================================================================ animations
def bird_anims(sid, m, legs, *, pivot, walk_kw, cfg):
    """cfg keys: neck_y (head height for searches), flap_T, flap_amp, hover_pitch, cry(dict), battle(dict),
    menace (bool: battle with spread wings), ride (bool), tail=('tail',), crest=() ..."""
    a = f"animation.{sid}."
    q = "q.anim_time"
    out = {}
    names = {b.name for b in m.bones}
    has = lambda n: n in names
    tail = cfg.get("tail", ("tail",))
    eyes = ("eye_left", "eye_right")
    skip = set(cfg.get("skip", ())) | {b.name for b in m.bones if b.name.startswith("wing_open")}
    trunk = {"torso", "chest"} | {b for t in ("torso", "chest") if has(t) for b in descendants(m, t)
                                   if not b.startswith(("neck", "head", "beak", "jaw", "eye", "crest", "tail", "horn", "brow", "wing"))}
    trunk -= skip
    bob = cfg.get("idle_bob", 1.0)

    # ---------------------------------------------------------------- idle: bird head snaps, bobbing, tail flicks
    def idle_pose(t):
        p = {}
        snaps = [(0, (0, 0, 0)), (0.7, (0, 0, 0)), (0.82, (0, 26, 0)), (2.1, (0, 26, 0)), (2.22, (-6, -18, 0)),
                 (3.0, (-6, -18, 0)), (3.12, (-4, -10, 14 * cfg.get("tilt", 1))), (4.0, (-4, -10, 14 * cfg.get("tilt", 1))),
                 (4.12, (0, 0, 0)), (6, (0, 0, 0))]
        hx, hy, hz = lerp_keys([(tt, list(v)) for tt, v in snaps], t)
        bobv = math.exp(-((t - 4.6) / 0.18) ** 2) * bob                       # a plover bob
        p["head"] = {"rotation": [hx + 10 * bobv, hy, hz]}
        p["neck"] = {"rotation": [4 * bobv + math.sin(math.radians(t * 60)) * 1.5, hy * 0.25, 0]}
        p["torso"] = {"rotation": [6 * bobv + math.sin(math.radians(t * 120)) * 0.6, 0, 0],
                      "position": [0, math.sin(math.radians(t * 120)) * 0.08 * cfg.get("scale", 1), 0]}
        flick = math.exp(-((t - 2.3) / 0.12) ** 2) + 0.6 * math.exp(-((t - 5.3) / 0.1) ** 2)
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [-16 * flick if i == 0 else -6 * flick, 0, 0]}
        shuffle = math.exp(-((t - 5.0) / 0.2) ** 2)
        for side, s in SIDES:
            p[f"wing_closed_{side}"] = {"rotation": [0, 0, -s * 7 * shuffle]}
        for b, fnc in cfg.get("idle_extra", {}).items():
            p[b] = fnc(t)
        return p
    out[a + "ground_idle"] = {"loop": True, "animation_length": 6, "bones": {**sampled(6, 0.05, idle_pose, loop=True), **HIDE_OPEN}}

    # ---------------------------------------------------------------- walk: quick running steps, head steady
    T = walk_kw["T"]
    f = round(360 / T, 3)
    ex = {"head": {"rotation": [f"-math.cos({q}*{2 * f}+80)*{cfg.get('head_bob', 2)}", f"-math.sin({q}*{f})*2", 0]},
          "neck": {"rotation": [f"math.cos({q}*{2 * f}+40)*{cfg.get('head_bob', 2) * 0.7}", 0, 0]}}
    for side, s in SIDES:
        ex[f"wing_closed_{side}"] = {"rotation": [0, 0, f"-{s}*(1+math.sin({q}*{2 * f})*1.5)"]}
    for i, tb in enumerate(tail):
        ex[tb] = {"rotation": [f"math.cos({q}*{2 * f}-{40 * (i + 1)})*3", f"math.sin({q}*{f})*4", 0]}
    out[a + "ground_walk"] = walk(legs, torso=walk_kw.get("torso", (1.0, 2.5, 3.0)), tail=(), neck=True, arms=(),
                                   extra=ex, **{k: v for k, v in walk_kw.items() if k != "torso"})
    out[a + "ground_walk"]["bones"].update(HIDE_OPEN)

    # ---------------------------------------------------------------- battle: crouched, head forward, wings ready
    B = dict(theta=4.0, dy=-0.6, neck=12, head=-8, wings=12, tail=-12)
    B.update(cfg.get("battle", {}))
    def battle_pose(t):
        w = math.sin(math.radians(t * 180))
        p = stance(legs, B["theta"], B["dy"] + 0.08 * w * cfg.get("scale", 1), pivot)
        p["neck"] = {"rotation": [B["neck"] + 1.5 * w, 0, 0]}
        p["head"] = {"rotation": [B["head"] - 1.5 * w, 6 * math.sin(math.radians(t * 90)), 0]}
        if has("jaw"):
            p["jaw"] = {"rotation": [3 + 3 * max(0, math.sin(math.radians(t * 360))), 0, 0]}
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [B["tail"] if i == 0 else -4, 4 * math.sin(math.radians(t * 180)), 0]}
        for side, s in SIDES:
            p[f"wing_closed_{side}"] = {"rotation": [0, s * B["wings"] * 0.4, -s * (B["wings"] + 3 * w)]}
        for b, fnc in cfg.get("battle_extra", {}).items():
            p[b] = fnc(t)
        return p
    battle = sampled(4, 0.05, battle_pose, loop=True)
    if cfg.get("menace"):        # intimidation display: wings raised high and arched forward like a cloak (mantling)
        M_ = dict(lift=40, fwd=14, droop=34, hand_fwd=12)
        M_.update(cfg.get("mantle", {}))
        for side, s in SIDES:
            battle[f"wing_open_{side}"] = {"rotation": [f"-8+math.sin({q}*90)*2", f"{s}*({M_['fwd']}+math.sin({q}*90)*3)",
                                                        f"{s}*(-{M_['lift']}+math.sin({q}*90)*4)"]}
            battle[f"wing_open_{side}2"] = {"rotation": [0, f"{s * M_['hand_fwd']}", f"{s}*({M_['droop']}+math.sin({q}*90-40)*5)"]}
        battle.update(HIDE_CLOSED)
    else:
        battle.update(HIDE_OPEN)
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": battle}

    # ---------------------------------------------------------------- sleep: sitting, head turned back on the shoulder
    sp = perched(m, legs, trunk, theta=cfg.get("sleep_theta", -4))
    # head turned back and laid on the back, bill towards the tail (plover roosting); the search keeps it out of
    # the body and the folded wings and resting on them
    head_grp = (descendants(m, "head") - skip) - set(eyes)
    solid_bones = [b for b in trunk | {f"wing_closed_{sd}" for sd, _ in SIDES} if has(b)]
    best = None
    if cfg.get("sleep_style") == "statue":          # gargoyle: head bowed onto the chest, like a carved statue
        for nx in rng(0, 80, 9):
            for hx in rng(-10, 60, 8):
                for dy in (0.0, -1.0, -2.0):
                    pp = copy_pose(sp)
                    pp["neck"] = {"rotation": [nx, 0, 0], "position": [0, dy * cfg.get("scale", 1), 0]}
                    pp["head"] = {"rotation": [hx, 0, 0]}
                    sc = sleep_score(m, pp, head_grp, solid_bones, style="statue")
                    if best is None or sc < best[0]:
                        best = (sc, nx, dy, hx, 0)
    else:
        for nx in rng(-70, 0, 8):                   # neck tilted back over the shoulders (X first, no yaw)
            for dy in (0.0, -1.0, -2.0):            # and pulled in
                for hy in (150, 165, 180):          # head turned to face the tail
                    for hx in rng(-30, 40, 8):
                        pp = copy_pose(sp)
                        pp["neck"] = {"rotation": [nx, 0, 0], "position": [0, dy * cfg.get("scale", 1), 0]}
                        pp["head"] = {"rotation": [hx, hy, 8]}
                        sc = sleep_score(m, pp, head_grp, solid_bones)
                        if best is None or sc < best[0]:
                            best = (sc, nx, dy, hx, hy)
    _, nx, dy, hx, hy = best
    sp["neck"] = {"rotation": [nx, 0, 0], "position": [0, dy * cfg.get("scale", 1), 0]}
    sp["head"] = {"rotation": [hx, hy, 8 if hy else 0]}
    tail_rest = -6
    if has(tail[0]):                                        # long tails: raise just enough to clear the ground
        tgrp = descendants(m, tail[0]) - skip
        for a0 in rng(-6, 40, 47):
            pp = copy_pose(sp)
            for i, tb in enumerate(tail):
                pp[tb] = {"rotation": [a0 if i == 0 else -6, 0, 0]}
            if lowest(m, pp, only=tgrp) >= 0.3:
                tail_rest = a0
                break
    sleep = {b: dict(ch) for b, ch in sp.items()}
    sleep["torso"] = {"rotation": [f"math.sin({q}*60)*0.8", 0, 0]}
    for e in eyes:
        sleep[e] = {"scale": [1, 0.1, 1]}
    for i, tb in enumerate(tail):
        sleep[tb] = {"rotation": [tail_rest if i == 0 else -6, 0, 0]}
    for side, s in SIDES:
        sleep[f"wing_closed_{side}"] = {"rotation": [0, 0, -s * 3]}
    sleep.update(HIDE_OPEN)
    out[a + "sleep"] = {"loop": True, "animation_length": 6, "bones": sleep}

    # ---------------------------------------------------------------- blink
    out[a + "blink"] = {"animation_length": 0.2, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.1, 1], "0.2": [1, 1, 1]}} for e in eyes}}

    # ---------------------------------------------------------------- cry
    C = dict(L=1.2, calls=((0.25, 0.45), (0.6, 0.85)), neck=-14, head=-22, beak=22, wings=10, tail=-14, theta=-4,
             spread=False)
    C.update(cfg.get("cry", {}))
    def cry_pose(t):
        L = C["L"]
        e = smooth(t / 0.2) if t < 0.2 else (1.0 if t < L - 0.25 else 1 - smooth((t - (L - 0.25)) / 0.25))
        op = 0.0
        for t0, t1 in C["calls"]:
            if t0 <= t <= t1:
                op = math.sin(math.pi * (t - t0) / (t1 - t0))
        p = stance(legs, C["theta"] * e, 0.0, pivot)
        p["neck"] = {"rotation": [C["neck"] * e, 0, 0]}
        p["head"] = {"rotation": [C["head"] * e - 4 * op, 0, 0]}
        if has("jaw"):
            p["jaw"] = {"rotation": [C["beak"] * op, 0, 0]}
        if has("beak"):
            p["beak"] = {"rotation": [-C["beak"] * 0.25 * op, 0, 0]}
        for i, tb in enumerate(tail):
            p[tb] = {"rotation": [C["tail"] * op if i == 0 else 0, 0, 0]}
        for side, s in SIDES:
            p[f"wing_closed_{side}"] = {"rotation": [0, s * C["wings"] * op * 0.5, -s * C["wings"] * op]}
            if C["spread"]:
                p[f"wing_open_{side}"] = {"rotation": [0, 0, s * (-30 * e - 12 * op)]}
                p[f"wing_open_{side}2"] = {"rotation": [0, 0, s * (-15 * e)]}
        return p
    out[a + "cry"] = {"animation_length": C["L"], "bones": {**sampled(C["L"], 0.05, cry_pose), **HIDE_OPEN}}
    # cries played over other poses are additive: no legs / body there (battle stance, flight)
    upper = ("neck", "head", "jaw", "beak") + tuple(tail)
    def cry_upper(t, wings=True):
        p = {b: v for b, v in cry_pose(t).items() if b in upper or (wings and b.startswith("wing_closed"))}
        return p
    out[a + "battle_cry"] = {"animation_length": C["L"], "bones": sampled(C["L"], 0.05, lambda t: cry_upper(t, not cfg.get("menace")))}
    out[a + "air_cry"] = {"animation_length": C["L"], "bones": {**sampled(C["L"], 0.05, lambda t: cry_upper(t, False)), **HIDE_CLOSED}}

    # ---------------------------------------------------------------- knock-out: legs give way, topples on its side
    k0 = stance(legs, 0, 0, pivot)
    k1 = merge(stance(legs, -6, 0.2, pivot), {"neck": {"rotation": [-14, 0, 0]}, "head": {"rotation": [-16, 0, 8]}})
    for side, s in SIDES:
        k1[f"wing_closed_{side}"] = {"rotation": [0, s * 10, -s * 22]}
    k2 = merge(stance(legs, 10, -1.2 * cfg.get("scale", 1), pivot, body_rot=[0, 0, 6]),
               {"neck": {"rotation": [18, 0, 0]}, "head": {"rotation": [10, 0, -12]}})
    k3 = merge(perched(m, legs, trunk, theta=6), {"neck": {"rotation": [30, 0, 0]}, "head": {"rotation": [14, 0, 0]}})
    k4 = {"body": {"rotation": [0, 0, cfg.get("roll", 80)], "position": [0, 0, 0]}}
    k4.update(legs_pose(legs, {lg.side: (-30, 40, 10, 30) for lg in legs}))
    for lg in legs:
        if lg.x < 0:
            k4[lg.bones[0]]["rotation"][2] = -12
    k4["neck"] = {"rotation": [10, 30, 0]}
    k4["head"] = {"rotation": [6, 20, 0]}
    for side, s in SIDES:
        k4[f"wing_closed_{side}"] = {"rotation": [0, 0, (-28 if s < 0 else 4)]}
    for i, tb in enumerate(tail):
        k4[tb] = {"rotation": [0, 10, 0]}
    best = None
    for ny in rng(-20, 70, 19):
        for nz in rng(-40, 40, 9):
            pp = copy_pose(k4)
            pp["neck"] = {"rotation": [10, ny, nz]}
            lo_t = lowest(m, pp, only=trunk)
            lo_h = lowest(m, pp, only=descendants(m, "neck") - skip)
            sc = abs(lo_h - lo_t - 0.3) + 0.004 * (abs(ny) + abs(nz))
            if best is None or sc < best[0]:
                best = (sc, ny, nz)
    k4["neck"] = {"rotation": [10, best[1], best[2]]}
    k5 = copy_pose(k4)
    if has("jaw"):
        k5["jaw"] = {"rotation": [14, 0, 0]}
    seq = [(0, k0), (0.3, k1), (0.75, k2), (1.2, k3), (1.75, k4), (2.2, k5), (2.6, k4)]
    bones = pose_sequence(m, seq, length=2.6, skip=skip)
    for e in eyes:
        bones[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.5, 1], 0.6: [1, 1, 1], 1.4: [1, 1, 1], 1.7: [1, 0.1, 1], 2.6: [1, 0.1, 1]})
    bones.update(HIDE_OPEN)
    out[a + "faint"] = {"animation_length": 2.6, "bones": bones}

    # ---------------------------------------------------------------- flight
    FT = cfg.get("flap_T", 0.5)
    tk = tucked(legs, cfg.get("tuck", (-25, 105, 150, 60)))
    hover = {b: dict(ch) for b, ch in tk.items()}
    hover.update(flap(FT, amp=cfg.get("flap_amp", 55)))
    hp = cfg.get("hover_pitch", -22)
    fq = round(360 / FT, 3)
    hover["body"] = {"rotation": [hp, 0, 0], "position": [0, f"math.sin({q}*{fq}-90)*{0.5 * cfg.get('scale', 1)}", 0]}
    hover["neck"] = {"rotation": [-hp * 0.7, 0, 0]}
    hover["head"] = {"rotation": [-hp * 0.3, 0, 0]}
    for i, tb in enumerate(tail):
        hover[tb] = {"rotation": [20 if i == 0 else 6, 0, 0]}
    hover.update(HIDE_CLOSED)
    out[a + "air_idle"] = {"loop": True, "animation_length": FT, "bones": hover}

    FT2 = cfg.get("fly_T", FT * 1.3)
    fq2 = round(360 / FT2, 3)
    fly = {b: dict(ch) for b, ch in tucked(legs, cfg.get("tuck_fly", (5, 120, 175, 80))).items()}
    fly.update(flap(FT2, amp=cfg.get("flap_amp", 55) * 0.8, up=4))
    fly["body"] = {"rotation": [f"-4+math.sin({q}*{fq2})*2", 0, 0], "position": [0, f"math.sin({q}*{fq2}-90)*{0.4 * cfg.get('scale', 1)}", 0]}
    fly["neck"] = {"rotation": [f"-6-math.sin({q}*{fq2})*2", 0, 0]}
    fly["head"] = {"rotation": [f"4+math.sin({q}*{fq2})*1.5", 0, 0]}
    for i, tb in enumerate(tail):
        fly[tb] = {"rotation": [f"-4+math.sin({q}*{fq2}-60)*3", 0, 0]}
    fly.update(HIDE_CLOSED)
    out[a + "air_fly"] = {"loop": True, "animation_length": FT2, "bones": fly}

    glide = {b: dict(ch) for b, ch in tucked(legs, cfg.get("tuck_fly", (5, 120, 175, 80))).items()}
    glide.update(glide_wings())
    glide["body"] = {"rotation": [f"2+math.sin({q}*90)*1.5", 0, f"math.sin({q}*45)*4"]}
    glide["neck"] = {"rotation": [-6, 0, 0]}
    glide["head"] = {"rotation": [4, f"math.sin({q}*45+40)*5", 0]}
    glide.update(HIDE_CLOSED)
    out[a + "air_glide"] = {"loop": True, "animation_length": 8, "bones": glide}

    if cfg.get("ride"):
        rk = cfg.get("ride_dy", -1.0)
        mi = copy_pose(stance(legs, 2.0, rk, pivot))
        mgi = {b: dict(ch) for b, ch in mi.items()}
        mgi["neck"] = {"rotation": [f"6+math.sin({q}*60)*1.5", 0, 0]}
        mgi["head"] = {"rotation": [f"-6+math.sin({q}*60-40)*1.5", f"math.sin({q}*30)*6", 0]}
        for side, s in SIDES:
            mgi[f"wing_closed_{side}"] = {"rotation": [0, s * 6, -s * 10]}
        mgi.update(HIDE_OPEN)
        out[a + "mount_ground_idle"] = {"loop": True, "animation_length": 6, "bones": mgi}
        mw = walk(legs, torso=(1.5, 2.0, 2.0), tail=(), neck=True, arms=(), extra=ex,
                  **{k: v for k, v in dict(walk_kw, T=walk_kw["T"] * 1.2, bob=walk_kw.get("bob", 0.5) * 1.2).items() if k != "torso"})
        mw["bones"].update(HIDE_OPEN)
        out[a + "mount_ground_walk"] = mw
        out[a + "mount_air_idle"] = out[a + "air_idle"]
        mf = {b: dict(ch) for b, ch in fly.items()}
        mf["body"] = {"rotation": [f"math.sin({q}*{fq2})*1.5", 0, 0], "position": [0, f"math.sin({q}*{fq2}-90)*{0.3 * cfg.get('scale', 1)}", 0]}
        out[a + "mount_air_fly"] = {"loop": True, "animation_length": FT2, "bones": mf}
        out[a + "mount_air_glide"] = out[a + "air_glide"]
        d = "math.clamp(q.r.dive(0),0,1)"            # layered over air_glide: wings swept back into a stoop
        dive = {}
        for side, s in SIDES:
            dive[f"wing_open_{side}"] = {"rotation": [0, f"{-s * 38}*{d}", f"{s * 8}*{d}"]}
            dive[f"wing_open_{side}2"] = {"rotation": [0, f"{-s * 42}*{d}", f"{s * 6}*{d}"]}
        dive["body"] = {"rotation": [f"18*{d}", 0, 0]}
        dive["neck"] = {"rotation": [f"-12*{d}", 0, 0]}
        dive["head"] = {"rotation": [f"-6*{d}", 0, 0]}
        dive.update(HIDE_CLOSED)
        out[a + "ride_dive"] = {"loop": True, "animation_length": 1, "bones": dive}
    return out

# ============================================================================ poser
def bird_poser(sid, portrait, profile, *, ride=False, menace=False, seats=None):
    qb = lambda n: f"q.bedrock('{sid}', '{n}')"
    blink = [f"q.bedrock_quirk('{sid}', 'blink')"]
    look = "q.look('head')"
    closed = [{"part": f"wing_open_{s}", "isVisible": False} for s, _ in SIDES] + \
             [{"part": f"wing_closed_{s}", "isVisible": True} for s, _ in SIDES]
    opened = [{"part": f"wing_open_{s}", "isVisible": True} for s, _ in SIDES] + \
             [{"part": f"wing_closed_{s}", "isVisible": False} for s, _ in SIDES]
    both = [{"part": f"wing_{k}_{s}", "isVisible": True} for k in ("open", "closed") for s, _ in SIDES]
    nr = {"condition": "!q.is_ridden"} if ride else {}
    air_cry = {"cry": f"q.bedrock_stateful('{sid}', 'air_cry')"}
    poses = {
        "standing": {"poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"], "isBattle": False, **nr,
                     "animations": [look, qb("ground_idle")], "quirks": blink, "transformedParts": closed},
        # menace: both wing sets enabled, battle_idle hides the folded pair (scale 0) and faint the spread pair
        "battle-standing": {"poseTypes": ["STAND"], "isBattle": True,
                            "animations": [look, qb("battle_idle")], "quirks": blink,
                            "namedAnimations": {"cry": f"q.bedrock_stateful('{sid}', 'battle_cry')"},
                            "transformedParts": both if menace else closed},
        "walking": {"poseTypes": ["WALK"], **nr, "animations": [look, qb("ground_walk")], "quirks": blink,
                    "transformedParts": closed},
        "hover": {"poseTypes": ["HOVER", "FLOAT"], **nr, "animations": ["q.pitch_tilt('body')", look, qb("air_idle")], "quirks": blink,
                  "namedAnimations": air_cry, "transformedParts": opened},
        "fly": {"poseTypes": ["FLY", "SWIM"], **nr, "animations": ["q.pitch_tilt('body')", qb("air_fly")], "quirks": blink,
                "namedAnimations": air_cry, "transformedParts": opened},
        "sleep": {"poseTypes": ["SLEEP"], "animations": [qb("sleep")], "transformedParts": closed},
    }
    if ride:
        poses.update({
            "mount_idle": {"poseTypes": ["STAND"], "isBattle": False, "condition": "q.has_entity && q.is_ridden && !q.in_air",
                           "animations": [look, qb("mount_ground_idle")], "quirks": blink, "transformedParts": closed},
            "mount_walk": {"poseTypes": ["WALK"], "isBattle": False, "condition": "q.has_entity && q.is_ridden && !q.in_air",
                           "animations": [look, qb("mount_ground_walk")], "quirks": blink, "transformedParts": closed},
            "mount_hovering": {"poseTypes": ["HOVER"], "condition": "!q.is_gliding && q.is_ridden && q.has_entity",
                               "animations": [look, qb("mount_air_idle")], "quirks": blink, "namedAnimations": air_cry,
                               "transformedParts": opened},
            "mount_fly": {"poseTypes": ["FLY"], "condition": "!q.is_gliding && q.is_ridden && q.has_entity",
                          "animations": [qb("mount_air_fly")], "quirks": blink, "namedAnimations": air_cry,
                          "transformedParts": opened},
            "glide": {"poseTypes": ["FLY"], "condition": "q.is_gliding", "isBattle": False,
                      "animations": [qb("air_glide"), {"condition": "q.is_ridden", "animation": qb("ride_dive")}],
                      "quirks": blink, "namedAnimations": air_cry, "transformedParts": opened},
        })
    out = {"portraitScale": portrait[0], "portraitTranslation": portrait[1],
           "profileScale": profile[0], "profileTranslation": profile[1], "rootBone": sid}
    if ride:
        out["firstPersonCameraOffset"] = {"seat_1": [0, 0.45, 0]}
        out["thirdPersonCameraOffset"] = {"seat_1": [0, 0.4, 1], "seat_1_reverse": [0, 0.4, 1]}
    out["animations"] = {"cry": f"q.bedrock_stateful('{sid}', 'cry')",
                         "faint": f"q.bedrock_primary('{sid}', 'faint', q.curve('one'))"}
    out["poses"] = poses
    return out
