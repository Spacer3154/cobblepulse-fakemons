# -*- coding: utf-8 -*-
"""Biped (theropod / brute-wyvern) rig: digitigrade legs (thigh, shin, metatarsus, toes) with inverse
kinematics. Leg motion is baked into catmull-rom keyframes so the feet really stay planted during stance;
the upper body (torso, chest, neck, head, tail, arms) uses Molang.

Sagittal-plane conventions (see modelgen): a segment hanging from a joint with absolute X angle `a`
points along v(a) = (dy, dz) = (-cos a, sin a); a < 0 = forward (-Z), a > 0 = backward."""
import math
from modelgen import Cube

def v(a):
    r = math.radians(a)
    return -math.cos(r), math.sin(r)

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

class Leg:
    def __init__(self, side, x, hip_z, lengths, angles, th, thigh=(6, 7, 3), shin=(4, 4), meta=(3, 3),
                 foot=(5, 6, 1.5), claws=(-1.5, 0, 1.5), paints=None, parent="body", claw_len=2, dewclaw=True,
                 bend=1):
        self.side, self.x, self.hip_z, self.L, self.a, self.th = side, x, hip_z, lengths, angles, th
        self.thigh, self.shin, self.meta, self.foot, self.claws = thigh, shin, meta, foot, claws
        self.paints, self.parent, self.claw_len, self.dewclaw = paints, parent, claw_len, dewclaw
        self.bend = bend          # +1: first joint ends forward (knee, stifle); -1: ends backward (elbow of a forelimb)
        L1, L2, L3 = lengths
        a1, a2, a3 = angles
        self.H = th + sum(L * math.cos(math.radians(a)) for L, a in zip(lengths, angles))
        self.foot_dz = sum(L * math.sin(math.radians(a)) for L, a in zip(lengths, angles))
        self.rest_rel = [a1, a2 - a1, a3 - a2, -a3]
        self.bones = [f"leg_{side}", f"shin_{side}", f"ankle_{side}", f"foot_{side}"]

    # ---------------------------------------------------------------- geometry
    def build(self, m):
        x, H, z = self.x, self.H, self.hip_z
        L1, L2, L3 = self.L
        (wt, dt, top), (ws, ds), (wm, dm) = self.thigh, self.shin, self.meta
        fw, fl, fb = self.foot
        p = self.paints
        r1, r2, r3, r4 = self.rest_rel
        m.bone(self.bones[0], self.parent, [x, H, z], rotation=[r1, 0, 0], cubes=[
            Cube([x - wt / 2, H - L1 - 1, z - dt / 2], [wt, L1 + 1 + top, dt], p["thigh"])])
        m.bone(self.bones[1], self.bones[0], [x, H - L1, z], rotation=[r2, 0, 0], cubes=[
            Cube([x - ws / 2, H - L1 - L2 - 1, z - ds / 2], [ws, L2 + 2, ds], p["shin"])])
        m.bone(self.bones[2], self.bones[1], [x, H - L1 - L2, z], rotation=[r3, 0, 0], cubes=[
            Cube([x - wm / 2, H - L1 - L2 - L3, z - dm / 2], [wm, L3 + 1, dm], p["meta"])])
        ty = H - L1 - L2 - L3
        th = self.th
        front = z + fb - fl
        cubes = [Cube([x - fw / 2, ty - th, front], [fw, th, fl], p["foot"])]
        cl = self.claw_len
        for ox in self.claws:
            cubes.append(Cube([x + ox - 0.5, ty - th, front - cl + 0.5], [1, 1, cl], p["claw"]))
        if self.dewclaw:
            cubes.append(Cube([x - 0.5, ty - th, z + fb], [1, 1, 1], p["claw"]))     # dewclaw at the back
        m.bone(self.bones[3], self.bones[2], [x, ty, z], rotation=[r4, 0, 0], cubes=cubes)

    # ---------------------------------------------------------------- IK
    def ik(self, dy, dz, a3, a4=0.0):
        """Absolute angles placing the toe pivot at (dy, dz) relative to the hip, metatarsus at a3."""
        L1, L2, L3 = self.L
        vy, vz = v(a3)
        Ay, Az = dy - L3 * vy, dz - L3 * vz
        d = math.hypot(Ay, Az)
        d = max(abs(L1 - L2) + 1e-3, min(L1 + L2 - 1e-3, d))
        theta = math.degrees(math.atan2(Az, -Ay))
        cal = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
        a1 = theta - self.bend * math.degrees(math.acos(max(-1, min(1, cal))))
        ky, kz = v(a1)
        a2 = math.degrees(math.atan2(Az - L1 * kz, -(Ay - L1 * ky)))
        return a1, a2, a3, a4

    def ik_ankle(self, dy, dz, a3, a4=0.0):
        """Absolute angles placing the ANKLE at (dy, dz) relative to the hip (used for lying down)."""
        L1, L2, _ = self.L
        d = max(abs(L1 - L2) + 1e-3, min(L1 + L2 - 1e-3, math.hypot(dy, dz)))
        theta = math.degrees(math.atan2(dz, -dy))
        cal = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
        a1 = theta - self.bend * math.degrees(math.acos(max(-1, min(1, cal))))
        ky, kz = v(a1)
        a2 = math.degrees(math.atan2(dz - L1 * kz, -(dy - L1 * ky)))
        return a1, a2, a3, a4

    def deltas(self, ang):
        a1, a2, a3, a4 = ang
        rel = [a1, a2 - a1, a3 - a2, a4 - a3]
        return [round(r - rr, 2) for r, rr in zip(rel, self.rest_rel)]

    def stand(self, hip_dy=0.0, foot_dz=0.0, a3_off=0.0):
        """Deltas for a planted foot (at rest position + foot_dz) with the hip raised/lowered by hip_dy."""
        return self.deltas(self.ik(self.th - (self.H + hip_dy), self.foot_dz + foot_dz, self.a[2] + a3_off))

def leg_pose(legs, hip_dy=0.0, foot_dz=0.0, a3_off=0.0):
    out = {}
    for lg in legs:
        for b, d in zip(lg.bones, lg.stand(hip_dy, foot_dz, a3_off)):
            out[b] = [d, 0, 0]
    return out

def kf(value, smooth_=True):
    return {"post": value, "lerp_mode": "catmullrom"} if smooth_ else value

# -------------------------------------------------------------------- walk
def walk(legs, *, T, stride, lift, stance=0.6, bob=0.5, samples=24, toe_off=28, fold=10, curl=22, phases=None,
         torso=(1.5, 3, 3), tail=("tail", "tail2", "tail3"), tail_amp=(6, 9, 12, 14), neck=True,
         arms=(("arm_left", 1), ("arm_right", -1)), arm_amp=6, extra=None):
    """torso = (pitch, yaw, roll) amplitudes in degrees."""
    phase = phases or {"left": 0.0, "right": 0.5}
    bones = {}
    for k in range(samples + 1):
        u = k / samples
        t = round(T * u, 4)
        bobv = -bob * math.cos(4 * math.pi * u)
        for lg in legs:
            ul = (u + phase[lg.side]) % 1.0
            if ul < stance:
                s = ul / stance
                dz = lg.foot_dz - stride / 2 + stride * s
                up = 0.0
                a3 = lg.a[2] + toe_off * smooth((s - 0.7) / 0.3)
                a4 = 0.0
            else:
                s = (ul - stance) / (1 - stance)
                dz = lg.foot_dz + stride / 2 - stride * smooth(s)
                up = lift * math.sin(math.pi * s)
                a3 = lg.a[2] + toe_off * (1 - smooth(s / 0.6)) + fold * math.sin(math.pi * s)
                a4 = curl * math.sin(math.pi * s)
            ang = lg.ik(lg.th + up - (lg.H + bobv), dz, a3, a4)
            for b, d in zip(lg.bones, lg.deltas(ang)):
                bones.setdefault(b, {"rotation": {}})["rotation"][str(t)] = kf([d, 0, 0])
        bones.setdefault("body", {"position": {}})["position"][str(t)] = kf([0, round(bobv, 3), 0])
    f = round(360 / T, 3)
    q = "q.anim_time"
    P, Y, R = torso
    bones["torso"] = {"rotation": [f"math.cos({q}*{2 * f})*{P}", f"math.sin({q}*{f}+90)*{Y}", f"math.sin({q}*{f})*{R}"]}
    bones["chest"] = {"rotation": [f"-math.cos({q}*{2 * f}+40)*{round(P * 0.5, 2)}", f"-math.sin({q}*{f}+90)*{round(Y * 0.4, 2)}", 0]}
    if neck:
        bones["neck"] = {"rotation": [f"math.cos({q}*{2 * f}+60)*{round(P * 1.2, 2)}", f"-math.sin({q}*{f}+60)*{round(Y * 0.5, 2)}",
                                      f"-math.sin({q}*{f})*{round(R * 0.6, 2)}"]}
    bones["head"] = {"rotation": [f"-math.cos({q}*{2 * f}+90)*{round(P, 2)}", f"-math.sin({q}*{f}+30)*{round(Y * 0.6, 2)}",
                                  f"-math.sin({q}*{f})*{round(R * 0.4, 2)}"]}
    for i, tb in enumerate(tail):
        amp = tail_amp[min(i, len(tail_amp) - 1)]
        bones[tb] = {"rotation": [f"math.cos({q}*{2 * f}-{40 * (i + 1)})*{round(P * 0.8, 2)}",
                                  f"-math.sin({q}*{f}+90-{45 * (i + 1)})*{amp}", 0]}
    for name, sgn in arms:
        bones[name] = {"rotation": [f"math.sin({q}*{f})*{arm_amp * sgn}", 0, 0]}
    for bone, chans in (extra or {}).items():
        bones.setdefault(bone, {}).update(chans)
    return {"loop": True, "animation_length": T, "bones": bones}

# -------------------------------------------------------------------- timelines with IK legs
def timeline(legs, length, keys, step=0.1):
    """keys: list of (time, hip_dy, a3_off) — the hip height curve (smoothstep between keys); feet stay
    planted. Returns bone channels for the legs + body position, densely sampled."""
    bones = {}
    n = int(round(length / step))
    for k in range(n + 1):
        t = round(k * step, 3)
        for (t0, h0, o0), (t1, h1, o1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                e = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1
                h, o = h0 + (h1 - h0) * e, o0 + (o1 - o0) * e
                break
        else:
            h, o = keys[-1][1], keys[-1][2]
        for b, val in leg_pose(legs, h, 0, o).items():
            bones.setdefault(b, {"rotation": {}})["rotation"][str(t)] = kf(val)
        bones.setdefault("body", {"position": {}})["position"][str(t)] = kf([0, round(h, 3), 0])
    return bones

def keys(**track):
    """keys(rotation={t: [x,y,z]}, position=..., scale=...) -> channels with catmull-rom keyframes."""
    return {ch: {str(t): kf(v) for t, v in frames.items()} for ch, frames in track.items()}

# -------------------------------------------------------------------- ground helpers
def lowest(model, pose, only=None, skip=()):
    pts = model.world_points(pose, only=None if only is None else set(only) - set(skip))
    ys = [p[1] for n, ps in pts.items() if (only is None or n in only) and n not in skip for p in ps]
    return min(ys) if ys else 0.0

def descendants(model, name):
    out, frontier = {name}, [name]
    while frontier:
        cur = frontier.pop()
        for b in model.bones:
            if b.parent == cur and b.name not in out:
                out.add(b.name)
                frontier.append(b.name)
    return out

def drape(model, pose, bone, axis=0, lo=-90.0, hi=90.0, target=0.3, skip=()):
    """Rotate `bone` (delta on `axis`) until the lowest point of it and its children touches `target`.
    Searches the side that lowers the part; returns the chosen angle (already written into pose)."""
    group = descendants(model, bone) - set(skip)
    def low(a):
        p = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in pose.items()}
        r = p.setdefault(bone, {}).setdefault("rotation", [0, 0, 0])
        r[axis] = a
        return lowest(model, p, only=group)
    base = pose.get(bone, {}).get("rotation", [0, 0, 0])[axis]
    best = min((abs(low(a) - target), a) for a in [lo + (hi - lo) * i / 180 for i in range(181)])[1]
    pose.setdefault(bone, {}).setdefault("rotation", [0, 0, 0])[axis] = round(best, 2)
    return best

# -------------------------------------------------------------------- lying down / knock-out
def lie_legs(m, legs, pose, trunk, hip_range=(4.0, 12.0), dz_range=(-3.0, 5.0)):
    """Bird-like resting pose: knees forward, shins folded back, metatarsus flat on the ground.
    Searches the hip height and ankle position so that, once the trunk is settled on the ground,
    the feet are on the ground too. Writes legs + body position into `pose`."""
    feet = [lg.bones[3] for lg in legs]
    best = None
    for i in range(17):
        hip_y = hip_range[0] + (hip_range[1] - hip_range[0]) * i / 16
        for j in range(9):
            dz = dz_range[0] + (dz_range[1] - dz_range[0]) * j / 8
            p = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in pose.items()}
            for lg in legs:
                ang = lg.ik_ankle(lg.th - hip_y, dz, -90, 0)
                for b, d in zip(lg.bones, lg.deltas(ang)):
                    p[b] = {"rotation": [d, 0, 0]}
            p["body"] = {"position": [0, hip_y - legs[0].H, 0]}
            low = lowest(m, p, only=trunk)
            p["body"]["position"][1] -= low
            f = lowest(m, p, only=feet)
            score = abs(f) + 0.05 * abs(hip_y - hip_range[0])
            if best is None or score < best[0]:
                best = (score, p)
    pose.clear()
    pose.update(best[1])
    return pose

def faint_anim(m, legs, final_pose, *, length=2.5, t_buckle=0.85, t_land=1.45, buckle=-3.0, skip=(),
               stagger=None, extra=None):
    """0..t_buckle: staggers while the knees give way (IK, feet planted); t_buckle..t_land: topples over,
    with the body re-settled on the ground at every sample so nothing sinks; small bounce; then still."""
    bones = timeline(legs, t_buckle, [(0, 0, 0), (t_buckle * 0.55, -0.6, 0), (t_buckle, buckle, 0)], step=0.05)
    start = {b: {"rotation": r} for b, r in leg_pose(legs, buckle).items()}
    start["body"] = {"position": [0, buckle, 0], "rotation": [0, 0, 0]}
    names = set(final_pose) | set(start)
    n = 10
    last = None
    for k in range(n + 1):
        s = k / n
        e = smooth(s) if k < n else 1.0
        t = round(t_buckle + (t_land - t_buckle) * s, 3)
        pose = {}
        for b in names:
            for ch in ("rotation", "position"):
                a = start.get(b, {}).get(ch, [0, 0, 0])
                z = final_pose.get(b, {}).get(ch, [0, 0, 0])
                pose.setdefault(b, {})[ch] = [x + (y - x) * e for x, y in zip(a, z)]
        pose["body"]["position"][1] = 0
        pose["body"]["position"][1] = -lowest(m, pose, skip=skip) + 0.05
        for b, chans in pose.items():
            for ch, val in chans.items():
                bones.setdefault(b, {}).setdefault(ch, {})[str(t)] = kf([round(x, 2) for x in val])
        last = pose
    for b, chans in last.items():                 # every bone starts from rest
        for ch in chans:
            bones[b][ch].setdefault("0.0", kf([0, 0, 0]))
    y = last["body"]["position"][1]
    bp = bones["body"]["position"]
    bp[str(round(t_land + 0.12, 3))] = kf([0, round(y + 0.7, 2), 0])
    bp[str(round(t_land + 0.3, 3))] = kf([0, round(y, 2), 0])
    for b, chans in last.items():
        for ch, val in chans.items():
            bones[b][ch][str(length)] = kf([round(x, 2) for x in val])
    for bone, chans in (stagger or {}).items():
        for ch, frames in chans.items():
            bones.setdefault(bone, {}).setdefault(ch, {}).update({str(t): kf(v) for t, v in frames.items()})
    for bone, chans in (extra or {}).items():
        bones.setdefault(bone, {}).update(chans)
    return {"animation_length": length, "bones": bones}


# -------------------------------------------------------------------- standard animation set for a biped
def sleep_pose(m, legs, tail, level=(10, 8), arms_fold=40, skip=(), head_clear=1.3, curl=(22, 28, 32, 20),
               tail_drop=(-35, -20, -20)):
    """Lies down like a resting bird: trunk levelled, belly low, legs folded, chin on the ground, tail curled."""
    base = {"torso": {"rotation": [level[0], 0, 0]}, "chest": {"rotation": [level[1], 0, 0]},
            "arm_left": {"rotation": [arms_fold, 0, 0]}, "arm_right": {"rotation": [arms_fold, 0, 0]}}
    pose = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()}
    trunk = ({"torso", "chest"} | {b for lg in legs for b in lg.bones[:2]}
             | {"arm_left", "arm_right", "forearm_left", "forearm_right"})
    lie_legs(m, legs, pose, trunk)
    pose.update({k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()})
    names = {b.name for b in m.bones}
    if "neck" in names:
        drape(m, pose, "neck", 0, 0, 70, target=1.0, skip=skip)
    drape(m, pose, "head", 0, -40, 50, target=head_clear, skip=skip)
    for tb, lim in zip(tail, tail_drop):
        drape(m, pose, tb, 0, lim, 5, target=0.3, skip=skip)
    for tb, yaw in zip(tail, curl):
        pose.setdefault(tb, {"rotation": [0, 0, 0]})["rotation"][1] = yaw
    return pose

def faint_pose(m, legs, tail, level=(10, 6), extra=None, skip=(), roll=82):
    """Final KO pose: toppled onto its left flank, legs limp, neck and head lying on the ground."""
    pose = {"body": {"rotation": [0, 0, roll], "position": [0, 0, 0]}}
    for lg in legs:
        for b, d in zip(lg.bones, lg.deltas((-45, 10, -35, 15))):
            pose[b] = {"rotation": [d, 0, 0]}
    pose.update({"torso": {"rotation": [level[0], 0, 0]}, "chest": {"rotation": [level[1], 0, 0]},
                 "arm_left": {"rotation": [20, 0, 0]}, "arm_right": {"rotation": [30, 0, 20]},
                 "head": {"rotation": [10, 0, 0]}, "jaw": {"rotation": [22, 0, 0]}})
    names = {b.name for b in m.bones}
    if "neck" in names:
        pose["neck"] = {"rotation": [-30, 0, 0]}
    for k, v in (extra or {}).items():
        pose[k] = v
    pose["body"]["position"][1] = round(-lowest(m, pose, skip=skip) + 0.2, 2)
    if "neck" in names:
        drape(m, pose, "neck", 2, -40, 40, target=0.4, skip=skip)
    drape(m, pose, tail[0], 2, -30, 30, target=0.4, skip=skip)
    return pose

def pose_to_bones(pose):
    return {b: {ch: [round(v, 2) if isinstance(v, (int, float)) else v for v in val] for ch, val in chans.items()}
            for b, chans in pose.items()}

def standard_anims(sid, m, legs, *, tail, flames=(), eyes=("eye_left", "eye_right"), sway=lambda f, k=1.0: {},
                   walk_kw=None, crouch=-2.5, idle_amp=1.0, level=(10, 8), arms_fold=40, cry=None,
                   faint_extra=None, skip=(), sleep_kw=None, battle_head=-10):
    a = f"animation.{sid}."
    q = "q.anim_time"
    names = {b.name for b in m.bones}
    has = lambda n: n in names
    out = {}
    k = idle_amp
    idle = {"torso": {"rotation": [f"math.sin({q}*90)*{1.2 * k}", 0, 0]},
            "chest": {"rotation": [f"-math.sin({q}*90-20)*{0.8 * k}", 0, 0]},
            "head": {"rotation": [f"-math.sin({q}*90-60)*{1 * k}", f"math.sin({q}*45-30)*{4 * k}", 0]},
            "jaw": {"rotation": [f"{2 * k}+math.sin({q}*90-60)*{2 * k}", 0, 0]},
            "arm_left": {"rotation": [f"math.sin({q}*90)*3", 0, 0]}, "arm_right": {"rotation": [f"math.sin({q}*90+40)*3", 0, 0]}}
    if has("neck"):
        idle["neck"] = {"rotation": [f"math.sin({q}*90-40)*{1.5 * k}", f"math.sin({q}*45)*{3 * k}", 0]}
    for i, tb in enumerate(tail):
        idle[tb] = {"rotation": [0, f"math.sin({q}*45-{40 * (i + 1)})*{4 + 2 * i}", 0]}
    idle.update(sway(180))
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": idle}
    out[a + "ground_walk"] = walk(legs, tail=tail, neck=has("neck"), extra=sway(560, 1.3), **(walk_kw or {}))
    battle = {b: {"rotation": r} for b, r in leg_pose(legs, crouch).items()}
    battle["body"] = {"position": [0, crouch, 0]}
    battle["torso"] = {"rotation": [f"6+math.sin({q}*180)*1.5", 0, f"math.sin({q}*90)*2"]}
    battle["chest"] = {"rotation": [2, 0, 0]}
    if has("neck"):
        battle["neck"] = {"rotation": [f"-6+math.sin({q}*180-30)*2", 0, 0]}
    battle["head"] = {"rotation": [f"{battle_head}+math.sin({q}*180-60)*2", 0, 0]}
    battle["jaw"] = {"rotation": [f"8+math.sin({q}*180)*5", 0, 0]}
    battle["arm_left"] = {"rotation": [-15, 0, -10]}
    battle["arm_right"] = {"rotation": [-15, 0, 10]}
    for i, tb in enumerate(tail):
        battle[tb] = {"rotation": [8 if i == 0 else 0, f"math.sin({q}*90-{40 * (i + 1)})*{5 + 2 * i}", 0]}
    battle.update(sway(360, 1.3))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": battle}
    sp = pose_to_bones(sleep_pose(m, legs, tail, level=level, arms_fold=arms_fold, skip=skip, **(sleep_kw or {})))
    sp.setdefault("chest", {})["position"] = [0, f"0.15+math.sin({q}*45)*0.15", 0]
    for e in eyes:
        sp[e] = {"scale": [1, 0.1, 1]}
    for fl in flames:
        sp[fl] = {"scale": [0.6, 0.5, 0.6]}
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sp}
    out[a + "blink"] = {"animation_length": 0.25, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.12": [1, 0.1, 1], "0.25": [1, 1, 1]}} for e in eyes}}
    if cry:
        out[a + "cry"] = cry
    stagger = {"torso": {"rotation": {0: [0, 0, 0], 0.25: [0, 0, 7], 0.5: [0, 0, -6], 0.7: [4, 0, 3], 0.85: [0, 0, 0]}},
               "head": {"rotation": {0: [0, 0, 0], 0.3: [-12, 0, 0], 0.6: [0, 0, 12], 0.85: [0, 0, 0]}},
               "jaw": {"rotation": {0: [0, 0, 0], 0.4: [10, 0, 0], 0.85: [0, 0, 0]}}}
    faint = faint_anim(m, legs, faint_pose(m, legs, tail, level=(level[0], level[1] - 2), extra=faint_extra, skip=skip),
                       length=2.5, skip=skip, stagger=stagger, buckle=crouch * 1.3)
    for e in eyes:
        faint["bones"][e] = keys(scale={0: [1, 1, 1], 0.9: [1, 1, 1], 1.1: [1, 0.1, 1], 2.5: [1, 0.1, 1]})
    for fl in flames:
        faint["bones"][fl] = keys(scale={0: [1, 1, 1], 0.8: [1, 1, 1], 1.6: [0.3, 0.15, 0.3], 2.5: [0.3, 0.15, 0.3]})
    out[a + "faint"] = faint
    return out

# -------------------------------------------------------------------- authored pose sequences
def pose_sequence(m, keyposes, *, length, step=0.05, skip=(), clearance=0.05):
    """keyposes: [(time, {bone: {"rotation": [...], "position": [...]}})] (deltas on the rest pose).
    Interpolates every bone between key poses (smoothstep) at `step`, and re-settles the body on the ground at
    each sample (body y = whatever puts the lowest point exactly on the ground: feet when standing, flank when
    lying), so nothing sinks and nothing floats. Returns catmull-rom bone channels."""
    keyposes = sorted(keyposes, key=lambda k: k[0])
    names = {b for _, p in keyposes for b in p} | {"body"}
    bones = {}
    n = int(round(length / step))
    for k in range(n + 1):
        t = round(k * step, 3)
        seg = None
        for (t0, p0), (t1, p1) in zip(keyposes, keyposes[1:]):
            if t0 <= t <= t1:
                seg = (t0, p0, t1, p1)
                break
        if seg is None:
            t0, p0 = keyposes[-1]
            seg = (t0, p0, t0, p0)
        t0, p0, t1, p1 = seg
        e = smooth((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        pose = {}
        for b in names:
            for ch in ("rotation", "position"):
                a, z = p0.get(b, {}).get(ch), p1.get(b, {}).get(ch)
                if a is None and z is None:
                    continue
                a, z = a or [0, 0, 0], z or [0, 0, 0]
                pose.setdefault(b, {})[ch] = [x + (y - x) * e for x, y in zip(a, z)]
        body = pose.setdefault("body", {})
        body.setdefault("position", [0, 0, 0])[1] = 0
        body["position"][1] = -lowest(m, pose, skip=skip) + clearance
        for b, chans in pose.items():
            for ch, val in chans.items():
                bones.setdefault(b, {}).setdefault(ch, {})[str(t)] = kf([round(x, 2) for x in val])
    return bones

def search(m, pose, bone, grid, target, group, keep=None, penalty=0.0, skip=()):
    """Grid search of a rotation for `bone`: brings the lowest point of `group` to `target` while every bone in
    `keep` stays above the ground. grid: list of [x,y,z] candidates. Writes the best into pose."""
    best = None
    for rot in grid:
        p = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in pose.items()}
        p.setdefault(bone, {})["rotation"] = list(rot)
        lo = lowest(m, p, only=group)
        if keep and lowest(m, p, only=keep) < -0.05:
            continue
        score = abs(lo - target) + penalty * sum(abs(v) for v in rot)
        if best is None or score < best[0]:
            best = (score, rot)
    if best:
        pose.setdefault(bone, {})["rotation"] = [round(v, 2) for v in best[1]]
    return best
