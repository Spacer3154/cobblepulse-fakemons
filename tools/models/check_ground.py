# -*- coding: utf-8 -*-
"""Replays every animation of a species through forward kinematics (Molang + catmull-rom keyframes) and reports
how the model meets the ground: lowest point over time, feet contact, and any part sinking below y=0.
Usage: python3 -I check_ground.py <models_dir> <species_id> [samples]"""
import importlib.util, math, os, re, sys
models_dir, sid = sys.argv[1:3]
samples = int(sys.argv[3]) if len(sys.argv) > 3 else 24
sys.path.insert(0, models_dir)
spec = importlib.util.spec_from_file_location(sid, os.path.join(models_dir, "species", f"{sid}.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def molang(expr, t):
    if isinstance(expr, (int, float)):
        return float(expr)
    e = expr.replace("q.r.dive(0)", "1").replace("q.anim_time", "T").replace("math.sin", "S").replace("math.cos", "C")
    e = e.replace("math.clamp", "CL").replace("math.abs", "abs").replace("math.floor", "FL").replace("math.max", "MX") \
         .replace("math.min", "MN").replace("math.pow", "PW").replace("math.sqrt", "SQ")
    return float(eval(e, {"__builtins__": {}}, {"T": t, "S": lambda d: math.sin(math.radians(d)),
                                                 "C": lambda d: math.cos(math.radians(d)), "abs": abs,
                                                 "CL": lambda v, a, b: max(a, min(b, v)), "FL": math.floor, "MX": max,
                                                 "MN": min, "PW": pow, "SQ": math.sqrt}))

def vec(v, t):
    v = v["post"] if isinstance(v, dict) else v
    return [molang(c, t) for c in v]

def channel(val, t, length, loop):
    if isinstance(val, (int, float, str)):
        v = molang(val, t)
        return [v, v, v]
    if isinstance(val, list):
        return [molang(c, t) for c in val]
    ks = sorted(((float(k), v) for k, v in val.items()), key=lambda kv: kv[0])
    if loop and length:
        t = t % length
    if t <= ks[0][0]:
        return vec(ks[0][1], t)
    if t >= ks[-1][0]:
        return vec(ks[-1][1], t)
    for i in range(len(ks) - 1):
        (t0, a), (t1, b) = ks[i], ks[i + 1]
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0
            p0 = vec(ks[max(0, i - 1)][1], t); p1 = vec(a, t); p2 = vec(b, t); p3 = vec(ks[min(len(ks) - 1, i + 2)][1], t)
            return [0.5 * ((2 * y1) + (-y0 + y2) * u + (2 * y0 - 5 * y1 + 4 * y2 - y3) * u * u + (-y0 + 3 * y1 - 3 * y2 + y3) * u ** 3)
                    for y0, y1, y2, y3 in zip(p0, p1, p2, p3)]

def pose_at(anim, t):
    pose = {}
    for bone, chans in anim["bones"].items():
        for ch in ("rotation", "position"):
            if ch in chans:
                pose.setdefault(bone, {})[ch] = channel(chans[ch], t, anim.get("animation_length", 0), anim.get("loop", False))
    return pose

model = mod.build()
anims = mod.anims(model) if "m" in mod.anims.__code__.co_varnames else mod.anims()
glow = {b.name for b in model.bones if b.cubes and all(isinstance(c.paint, dict) and c.paint.get("glow") for c in b.cubes)}
planes = {b.name for b in model.bones if b.cubes and all(0 in c.size for c in b.cubes)}
feet = [b.name for b in model.bones if b.name.startswith("foot_")]
skip = glow | planes | {b.name for b in model.bones if b.name.startswith("wing_open")}
print(f"{sid}: {len(model.bones)} bones; ignoring glow/plane bones {sorted(skip)}")
for name, anim in anims.items():
    if name.endswith("blink"):
        continue
    L = anim.get("animation_length", 2) or 2
    lows, flo, sink = [], [], []
    for k in range(samples + 1):
        t = L * k / samples
        pose = pose_at(anim, t)
        pts = model.world_points(pose)
        y_all = min(p[1] for n, ps in pts.items() if n not in skip for p in ps)
        y_feet = min(p[1] for n in feet for p in pts[n]) if feet else y_all
        worst = min(((min(p[1] for p in ps), n) for n, ps in pts.items() if ps and n not in skip))
        lows.append(round(y_all, 2)); flo.append(round(y_feet, 2))
        if worst[0] < -0.35:
            sink.append((round(t, 2), worst[1], round(worst[0], 2)))
    print(f"  {name.split('.')[-1]:12} lowest {min(lows):6.2f}..{max(lows):6.2f} | feet {min(flo):6.2f}..{max(flo):6.2f}"
          + (f" | SINKS {sink[:4]}" if sink else " | ok"))
