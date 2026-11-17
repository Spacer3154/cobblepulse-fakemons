# -*- coding: utf-8 -*-
"""Shared animation / poser templates and paint helpers (quadrupeds; bipeds live in biped.py).
Bedrock rotation conventions verified in Blockbench:
  +X rotation  = front (-Z) goes down  (head nods down, tail raises)
  +Z rotation: +X side goes down, -X side goes up (right legs splay out with +Z, left wing rises with -Z)
  +X rotation on the jaw = mouth opens"""
from modelgen import fill, shade, mix

# ------------------------------------------------------------------ animations
# Phase offsets (degrees). "walk" = 4-beat lateral-sequence walk of heavy quadrupeds,
# "trot" = diagonal pairs together (lizard-like gait).
GAITS = {
    "walk": {"leg_back_left": 0, "leg_front_left": 90, "leg_back_right": 180, "leg_front_right": 270},
    "trot": {"leg_front_right": 0, "leg_back_left": 0, "leg_front_left": 180, "leg_back_right": 180},
}

def quad_walk(*, gait="walk", speed=360, stride=22, lift=1.5, bob=0.35, pitch=1.5, yaw=3, roll=3, nod=2.5,
              tail=("tail", "tail2"), tail_amp=10, feet=True, sway=(), sway_mul=1.5, extra=None):
    """Step cycle per leg: swing (foot lifted, moving forward) then stance (planted, pushing back).
    Leg -X rotation = foot forward, +Y position = up. The foot bone counter-rotates so the sole stays flat."""
    t = "q.anim_time"
    bones = {}
    for leg, off in GAITS[gait].items():
        ph = f"{t}*{speed}+{off}"
        bones[leg] = {"rotation": [f"-math.sin({ph})*{stride}", 0, 0],
                      "position": [0, f"math.clamp(math.cos({ph}),0,1)*{lift}", 0]}
        if feet:
            foot = leg.replace("leg_", "foot_")
            bones[foot] = {"rotation": [f"math.sin({ph})*{round(stride * 0.8, 1)}-math.clamp(math.cos({ph}),0,1)*14", 0, 0]}
    bones["body"] = {"position": [0, f"math.cos({t}*{2 * speed})*{bob}", 0],
                     "rotation": [f"math.sin({t}*{2 * speed}+90)*{pitch}", f"math.sin({t}*{speed})*{yaw}",
                                  f"math.sin({t}*{speed}+90)*{roll}"]}
    bones["head"] = {"rotation": [f"math.sin({t}*{2 * speed}+60)*{nod}", f"-math.sin({t}*{speed})*{round(yaw * 0.8, 1)}", 0]}
    for i, tb in enumerate(tail):
        bones[tb] = {"rotation": [0, f"math.sin({t}*{speed}-{50 + 40 * i})*{tail_amp + 3 * i}", 0]}
    for bone, axis, amp, ph in sway:
        rot = bones.setdefault(bone, {"rotation": [0, 0, 0]}).setdefault("rotation", [0, 0, 0])
        rot[axis] = f"math.sin({t}*{2 * speed}+{ph})*{round(amp * sway_mul, 2)}"
    for bone, chans in (extra or {}).items():
        bones.setdefault(bone, {}).update(chans)
    return {"loop": True, "animation_length": round(360 / speed, 4), "bones": bones}

def tremble(base, freq=2200, amp=1.5):
    """Molang value that shakes around `base` (used while an animal is calling)."""
    return f"{base}+math.sin(q.anim_time*{freq})*{amp}"

def quad_anims(sid, *, legs_front=("leg_front_right", "leg_front_left"), legs_back=("leg_back_right", "leg_back_left"),
               tail=("tail", "tail2"), sway=(), eyes=("eye_left", "eye_right"), stride=28, speed=450, bob=0.35,
               drop=2.1, head_turn=18, breathe=0.12, battle_extra=None, cry_extra=None, faint_extra=None,
               sleep_extra=None, walk=None, cry=None):
    """walk: kwargs for quad_walk (replaces the simple pendulum walk); cry: (length, bones) custom call."""
    a = f"animation.{sid}."
    fr, fl = legs_front
    br, bl = legs_back

    def sway_bones(freq, amp_mul):
        out = {}
        for bone, axis, amp, ph in sway:
            rot = out.setdefault(bone, {"rotation": [0, 0, 0]})["rotation"]
            rot[axis] = f"math.sin(q.anim_time*{freq}+{ph})*{round(amp * amp_mul, 2)}"
        return out

    def tail_chain(freq, amp, lag=60, up=0):
        out = {}
        for i, t in enumerate(tail):
            out[t] = {"rotation": [up if i == 0 else 0, f"math.sin(q.anim_time*{freq}-{lag * i})*{amp + 4 * i}", 0]}
        return out

    eyes_closed = {e: {"scale": [1, 0.1, 1]} for e in eyes}
    walk_legs = {fr: f"math.sin(q.anim_time*{speed})*{stride}", bl: f"math.sin(q.anim_time*{speed})*{stride}",
                 fl: f"-math.sin(q.anim_time*{speed})*{stride}", br: f"-math.sin(q.anim_time*{speed})*{stride}"}
    anims = {
        a + "ground_idle": {"loop": True, "animation_length": 4, "bones": {
            "torso": {"position": [0, f"math.sin(q.anim_time*90)*{breathe}", 0]},
            "head": {"rotation": ["math.sin(q.anim_time*90-30)*1.5", 0, 0]},
            **tail_chain(45, 8), **sway_bones(90, 1)}},
        a + "ground_walk": {"loop": True, "animation_length": round(720 / speed, 4), "bones": {
            "body": {"position": [0, f"math.abs(math.sin(q.anim_time*{speed}))*{bob}", 0],
                     "rotation": [0, 0, f"math.sin(q.anim_time*{speed})*3"]},
            "head": {"rotation": [0, f"math.sin(q.anim_time*{speed})*-3", 0]},
            **{leg: {"rotation": [expr, 0, 0]} for leg, expr in walk_legs.items()},
            **tail_chain(speed, 12), **sway_bones(speed * 2, 1.5)}},
        a + "battle_idle": {"loop": True, "animation_length": 2, "bones": {
            "body": {"position": [0, "-0.4+math.sin(q.anim_time*180)*0.2", 0]},
            "head": {"rotation": ["6+math.sin(q.anim_time*180-30)*2", 0, 0]},
            **tail_chain(180, 8, up=15), **sway_bones(360, 1.3), **(battle_extra or {})}},
        a + "sleep": {"loop": True, "animation_length": 8, "bones": {
            **eyes_closed,
            "body": {"position": [0, -drop, 0]},
            "torso": {"position": [0, f"math.sin(q.anim_time*45)*{breathe * 0.7}", 0]},
            "head": {"rotation": [10, head_turn, 0]},
            fr: {"rotation": [0, 0, 70]}, br: {"rotation": [0, 0, 70]},
            fl: {"rotation": [0, 0, -70]}, bl: {"rotation": [0, 0, -70]},
            **{t: {"rotation": [0, 30 + 10 * i, 0]} for i, t in enumerate(tail)},
            **sway_bones(45, 0.5), **(sleep_extra or {})}},
        a + "blink": {"animation_length": 0.1667, "bones": {
            e: {"scale": {"0.0": [1, 1, 1], "0.0833": [1, 0.1, 1], "0.1667": [1, 1, 1]}} for e in eyes}},
        a + "cry": {"animation_length": 1.0, "bones": {
            "head": {"rotation": {"0.0": [0, 0, 0], "0.25": [-15, 0, 0], "0.75": [-15, 0, 0], "1.0": [0, 0, 0]}},
            "jaw": {"rotation": {"0.0": [0, 0, 0], "0.25": [20, 0, 0], "0.75": [20, 0, 0], "1.0": [0, 0, 0]}},
            **(cry_extra or {})}},
        a + "faint": {"animation_length": 2.5, "bones": {
            "body": {"rotation": {"0.0": [0, 0, 0], "0.25": [0, 0, 6], "0.5": [0, 0, -6], "0.7": [0, 0, 4],
                                  "1.0": [0, 0, 0]},
                     "position": {"0.0": [0, 0, 0], "0.7": [0, 0, 0], "1.0": [0, -(drop + 0.2), 0],
                                  "1.15": [0, -(drop - 0.2), 0], "1.3": [0, -(drop + 0.2), 0]}},
            "head": {"rotation": {"0.0": [0, 0, 0], "0.3": [-10, 0, 0], "0.7": [0, 0, 10],
                                  "1.0": [14, 25, 8], "1.3": [12, 25, 8]}},
            "jaw": {"rotation": {"1.0": [0, 0, 0], "1.3": [12, 0, 0]}},
            **{e: {"scale": {"0.0": [1, 1, 1], "0.6": [1, 1, 1], "0.75": [1, 0.1, 1]}} for e in eyes},
            fr: {"rotation": {"0.7": [0, 0, 0], "1.0": [0, 0, 75]}}, br: {"rotation": {"0.7": [0, 0, 0], "1.0": [0, 0, 75]}},
            fl: {"rotation": {"0.7": [0, 0, 0], "1.0": [0, 0, -75]}}, bl: {"rotation": {"0.7": [0, 0, 0], "1.0": [0, 0, -75]}},
            **{t: {"rotation": {"0.7": [0, 0, 0], "1.1": [0, -25 - 5 * i, 0]}} for i, t in enumerate(tail)},
            **(faint_extra or {})}},
    }
    if walk is not None:
        anims[a + "ground_walk"] = quad_walk(tail=tail, sway=sway, **walk)
    if cry is not None:
        anims[a + "cry"] = {"animation_length": cry[0], "bones": cry[1]}
    return anims

def poser(sid, portrait=(1.9, [-0.1, -0.55, 0]), profile=(0.95, [0, 0.3, 0])):
    q = lambda name: f"q.bedrock('{sid}', '{name}')"
    blink = [f"q.bedrock_quirk('{sid}', 'blink')"]
    return {
        "portraitScale": portrait[0], "portraitTranslation": portrait[1],
        "profileScale": profile[0], "profileTranslation": profile[1],
        "rootBone": sid,
        "animations": {"cry": f"q.bedrock_stateful('{sid}', 'cry')",
                       "faint": f"q.bedrock_primary('{sid}', 'faint', q.curve('one'))"},
        "poses": {
            "battle-standing": {"poseTypes": ["STAND"], "isBattle": True,
                                "animations": ["q.look('head')", q("battle_idle")], "quirks": blink},
            "standing": {"poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"], "isBattle": False,
                         "animations": ["q.look('head')", q("ground_idle")], "quirks": blink},
            "walking": {"poseTypes": ["WALK", "SWIM"], "animations": ["q.look('head')", q("ground_walk")],
                        "quirks": blink},
            "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]},
        },
    }

# ------------------------------------------------------------------ paint helpers
def eye_fn(px, faces, pal, rnd):
    x, y, w, h = faces["north"]
    fill(px, x, y, w, h, pal["eye"], 1.0)
    px[x, y] = pal["eye_shine"]
    x, y, w, h = faces["south"]
    fill(px, x, y, w, h, pal["eye"], 1.0)

def leaf_plane(key="leaf", vein="leaf_light"):
    def fn(px, faces, pal, rnd):
        for fc in ("up", "down", "north", "south", "east", "west"):
            x, y, w, h = faces[fc]
            if w and h:
                fill(px, x, y, w, h, pal[key], 1.0, rnd)
        for fc in ("up", "down", "east", "west", "north", "south"):
            x, y, w, h = faces[fc]
            if w and h:
                for i in range(w):
                    px[x + i, y + h // 2] = pal[vein]
    return fn

def leaf_shaped(key="leaf", vein="leaf_light", side_veins=True):
    """Leaf plane cut to an ellipse (transparent outside) with a midrib along the long axis."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if w < 2 or h < 2:
                continue
            for j in range(h):
                for i in range(w):
                    dx, dy = (i + 0.5) / w * 2 - 1, (j + 0.5) / h * 2 - 1
                    if dx * dx + dy * dy <= 1.08:
                        px[x + i, y + j] = shade(pal[key], 1.0 + rnd.uniform(-0.05, 0.05))
                    else:
                        px[x + i, y + j] = (0, 0, 0, 0)
            if w >= h:
                for i in range(1, w - 1):
                    px[x + i, y + h // 2] = pal[vein]
                if side_veins:
                    for i in range(2, w - 2, 3):
                        for d in (1, 2):
                            if h // 2 - d >= 0 and px[x + i + d - 1, y + h // 2 - d][3]:
                                px[x + i + d - 1, y + h // 2 - d] = shade(pal[vein], 0.9)
                            if h // 2 + d < h and px[x + i + d - 1, y + h // 2 + d][3]:
                                px[x + i + d - 1, y + h // 2 + d] = shade(pal[vein], 0.9)
            else:
                for j in range(1, h - 1):
                    px[x + w // 2, y + j] = pal[vein]
    return fn

def foliage(apples=0.08):
    """Leafy canopy with scattered cider apples."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    r = rnd.random()
                    if r < 0.18:
                        px[x + i, y + j] = shade(pal["leaf_light"], 1.0)
                    elif r < 0.33:
                        px[x + i, y + j] = shade(pal["leaf"], 0.78)
            if fc == "down" or w < 2 or h < 2:
                continue
            taken = set()
            n = max(1, round(w * h * apples / 3)) if apples else 0
            for _ in range(n * 6):
                if n <= 0:
                    break
                i, j = rnd.randint(0, w - 2), rnd.randint(0, h - 2)
                if any((i + di, j + dj) in taken for di in (-1, 0, 1, 2) for dj in (-1, 0, 1, 2)):
                    continue
                px[x + i, y + j] = pal["apple_streak"]
                px[x + i + 1, y + j] = pal["apple"]
                px[x + i, y + j + 1] = pal["apple"]
                px[x + i + 1, y + j + 1] = pal.get("apple_dark", shade(pal["apple"], 0.75))
                taken |= {(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)}
                n -= 1
    return fn

def bark(px, faces, pal, rnd):
    for fc in ("north", "south", "east", "west"):
        x, y, w, h = faces[fc]
        for i in range(w):
            if (i + rnd.randint(0, 1)) % 3 == 0:
                for j in range(h):
                    if rnd.random() < 0.8:
                        px[x + i, y + j] = pal["bark_dark"]
    for fc in ("up", "down"):
        x, y, w, h = faces[fc]
        fill(px, x, y, w, h, pal["bark"], 1.1, rnd)
        if w > 2 and h > 2:
            px[x + w // 2, y + h // 2] = pal["bark_dark"]

def staves():
    """Barrel lying along Z: planks parallel to Z (stripes) + lid rings on the ends."""
    def fn(px, faces, pal, rnd):
        for fc in ("east", "west"):
            x, y, w, h = faces[fc]
            for j in range(h):
                if j % 3 == 2:
                    for i in range(w):
                        px[x + i, y + j] = pal["wood_dark"]
        for fc in ("up", "down"):
            x, y, w, h = faces[fc]
            for i in range(w):
                if i % 3 == 2:
                    for j in range(h):
                        px[x + i, y + j] = pal["wood_dark"]
        for fc in ("north", "south"):
            x, y, w, h = faces[fc]
            fill(px, x, y, w, h, pal["wood"], 1.05, rnd)
            for i in range(w):
                px[x + i, y] = pal["wood_dark"]; px[x + i, y + h - 1] = pal["wood_dark"]
            for j in range(h):
                px[x, y + j] = pal["wood_dark"]; px[x + w - 1, y + j] = pal["wood_dark"]
            for i in range(2, w - 2):
                px[x + i, y + 2] = shade(pal["wood_dark"], 1.15); px[x + i, y + h - 3] = shade(pal["wood_dark"], 1.15)
            for j in range(2, h - 2):
                px[x + 2, y + j] = shade(pal["wood_dark"], 1.15); px[x + w - 3, y + j] = shade(pal["wood_dark"], 1.15)
            for i in range(3, w - 3):
                if i % 2 == 0:
                    for j in range(3, h - 3):
                        px[x + i, y + j] = shade(pal["wood"], 0.92)
    return fn

def metal(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["hoop"], 1.0, rnd, 3)
        if fc in ("east", "west", "north", "south"):
            for i in range(w):
                px[x + i, y] = pal["hoop_light"]

def closed_eye_lines(cols, row, key="eye"):
    def fn(px, faces, pal, rnd):
        x, y, w, h = faces["north"]
        for c in cols:
            if c < w and row < h:
                px[x + c, y + row] = shade(pal[key], 1.3)
    return fn

def chain(*fns):
    def fn(px, faces, pal, rnd):
        for f in fns:
            f(px, faces, pal, rnd)
    return fn

# ------------------------------------------------------------------ Viking / fire helpers
def flame(keys=("flame_core", "flame_mid", "flame_out", "flame_tip")):
    """Vertical flame tongues on plane cubes: tall pointed centre, shorter jagged sides, hot core low in the middle.
    Base texture keeps a small steady flame; emissive frames (pal['_flame_full']) draw full flickering tongues."""
    def fn(px, faces, pal, rnd):
        full = pal.get("_flame_full", False)
        core, mid, out, tip = (pal[k] for k in keys)
        for fc, (x, y, w, h) in faces.items():
            if w == 0 or h == 0 or fc in ("up", "down"):
                continue
            for i in range(w):
                p = 1 - abs((i + 0.5) / w * 2 - 1)
                hf = 0.25 + 0.75 * p ** 0.8
                if full:
                    hf += rnd.uniform(-0.15, 0.15) + (-0.12 if i % 2 else 0.05)
                else:
                    hf *= 0.6
                ht = max(1, round(h * min(1.0, hf)))
                for j in range(h):
                    r = h - 1 - j
                    if r >= ht:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    f = r / max(ht - 1, 1)
                    if p < 0.34:
                        col = out if f < 0.7 else tip
                    elif f < 0.45 and p > 0.5:
                        col = core
                    elif f < 0.7:
                        col = mid
                    elif f < 0.9:
                        col = out
                    else:
                        col = tip
                    px[x + i, y + j] = col
    return fn

def clinker(px, faces, pal, rnd):
    """Clinker-built hull: overlapping planks (horizontal strakes on the flanks, along Z on top)."""
    for fc in ("east", "west", "north", "south"):
        x, y, w, h = faces[fc]
        for j in range(h):
            if j % 2 == 1:
                for i in range(w):
                    px[x + i, y + j] = pal["hull_dark"]
            elif j % 4 == 0:
                for i in range(w):
                    if rnd.random() < 0.5:
                        px[x + i, y + j] = shade(pal["hull"], 1.08)
    x, y, w, h = faces["up"]
    for i in range(w):
        if i % 3 == 2:
            for j in range(h):
                px[x + i, y + j] = pal["hull_dark"]

def round_shield(a="shield_a", b="shield_b", rim="shield_rim", boss="boss", quarters=False):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if w < 2 or h < 2:
                continue
            for j in range(h):
                for i in range(w):
                    dx, dy = (i + 0.5) / w * 2 - 1, (j + 0.5) / h * 2 - 1
                    d2 = dx * dx + dy * dy
                    if d2 > 1.15:
                        px[x + i, y + j] = (0, 0, 0, 0)
                    elif d2 > 0.9 and w >= 4:
                        px[x + i, y + j] = pal[rim]
                    else:
                        left = dx < 0
                        top = dy < 0
                        px[x + i, y + j] = pal[a] if (left != top if quarters else left) else pal[b]
            if w < 4:   # tiny shield: round silhouette, alternating colour segments, metal boss
                for j in range(h):
                    for i in range(w):
                        corner = i in (0, w - 1) and j in (0, h - 1)
                        px[x + i, y + j] = (0, 0, 0, 0) if corner else (pal[a] if (i + j) % 2 else pal[b])
            cx, cy = x + w // 2, y + h // 2
            px[cx, cy] = pal[boss]
            if w >= 4:
                px[cx - 1, cy] = pal[boss]; px[cx, cy - 1] = pal[boss]; px[cx - 1, cy - 1] = pal[boss]
    return fn

def sail(a="sail_a", b="sail_b", tatter=0.0):
    """Square Viking sail: vertical stripes, weathered, optionally tattered (transparent holes, ragged hem)."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if w < 2 or h < 2:
                continue
            for j in range(h):
                for i in range(w):
                    col = pal[a] if (i // 2) % 2 == 0 else pal[b]
                    px[x + i, y + j] = shade(col, 1.0 - 0.15 * (j / h) + rnd.uniform(-0.04, 0.04))
            if tatter:
                for i in range(w):
                    for j in range(h - 1, h - 1 - rnd.randint(0, max(1, int(h * 0.35))), -1):
                        px[x + i, y + j] = (0, 0, 0, 0)
                for _ in range(int(w * h * tatter)):
                    i, j = rnd.randint(1, w - 2), rnd.randint(1, h - 3)
                    px[x + i, y + j] = (0, 0, 0, 0)
    return fn

def rivets(key="rivet", every=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if w < 2 or h < 2:
                continue
            for i in range(1, w - 1, every):
                px[x + i, y + 1] = pal[key]
                if h > 3:
                    px[x + i, y + h - 2] = pal[key]
    return fn

# ------------------------------------------------------------------ menacing eyes
def slit_eye(px, faces, pal, rnd):
    """Predator eye on a plane: hot upper rim, iris below, vertical slit pupil in the middle column."""
    for fc in ("north", "south"):
        x, y, w, h = faces[fc]
        if not (w and h):
            continue
        for j in range(h):
            for i in range(w):
                px[x + i, y + j] = pal["eye_hot"] if j == 0 else pal["eye"]
        for j in range(h):
            px[x + w // 2, y + j] = pal["pupil"]

def glow_trail(px, faces, pal, rnd):
    """Short spectral streak on the side of the skull."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                edge = i in (0, w - 1)
                px[x + i, y + j] = pal["flame_out"] if edge else pal["eye"]

def sockets(rows, cols, key="socket"):
    """Dark, deep-set eye sockets painted on the skull front (rows/cols ranges, symmetric pairs)."""
    def fn(px, faces, pal, rnd):
        x, y, w, h = faces["north"]
        for j in rows:
            for i in cols:
                if 0 <= i < w and 0 <= j < h:
                    px[x + i, y + j] = shade(pal[key], 1.0 + rnd.uniform(-0.05, 0.05))
    return fn


def land_mount_poses(ps, sid, first=(0, 0.45, 0), third=(0, 0.5, 0)):
    """Turns a ground poser into a land mount (cobblemon:land/horse), like Cobblemon 1.8's Mudsdale:
    unridden poses unchanged, a calmer idle while ridden, a gallop when the rider sprints and a jump pose in the
    air. Conditions are mutually exclusive so exactly one pose fits."""
    qb = lambda n: f"q.bedrock('{sid}', '{n}')"
    blink = [f"q.bedrock_quirk('{sid}', 'blink')"]
    P = ps["poses"]
    airborne = "q.is_ridden && q.in_air"
    order = {"battle-standing": P["battle-standing"],
             "in-air": {"poseTypes": ["STAND", "WALK", "NONE", "FLOAT"], "condition": airborne,
                        "animations": ["q.look('head')", qb("ride_jump")], "quirks": blink, "transformTicks": 5},
             "standing": dict(P["standing"], condition="!q.is_ridden"),
             "mount_idle": {"poseTypes": ["STAND", "NONE", "FLOAT"], "isBattle": False,
                            "condition": "q.is_ridden && !q.in_air",
                            "animations": ["q.look('head')", qb("mount_ground_idle")], "quirks": blink},
             "running": {"poseTypes": ["WALK", "SWIM"], "condition": f"q.is_sprinting && !({airborne})",
                         "animations": ["q.look('head')", qb("ground_run")], "quirks": blink, "transformTicks": 5},
             "walking": dict(P["walking"], condition=f"!q.is_sprinting && !({airborne})"),
             "sleep": P["sleep"]}
    ps["poses"] = order
    ps["firstPersonCameraOffset"] = {"seat_1": list(first)}
    ps["thirdPersonCameraOffset"] = {"seat_1": list(third), "seat_1_reverse": list(third)}
    return ps
