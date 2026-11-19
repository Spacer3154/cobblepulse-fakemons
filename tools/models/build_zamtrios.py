# -*- coding: utf-8 -*-
"""Zamtrios (Monster Hunter) for Cobblemon: models and textures from species/zamtrios.py (rebuilt on the skeleton of
the supplied remaster model, after the reference pictures), animations from the supplied GeckoLib file (src/zamtrios:
keyframes with easing resampled to linear Bedrock keyframes: idle, walk, run, sleep, faint, cry) plus the ones written
here (battle_idle, physical, special, status, swimming, the whole Inflated set).

python3 -I build_zamtrios.py <models_dir> <out_pack_dir> <tmp_dir>

Three models: zamtrios (normal), zamtrios_armor (Ice Armour, glow shells on the ice), zamtrios_inflated (the giant
sac, built at half size and scaled x2 by every animation). Textures: normal / shiny, emissive layer (eyes; the ice of
the armour) — the eyes and the ice glow go out while it sleeps."""
import copy, json, math, os, sys

models_dir, out, tmp = sys.argv[1:4]
sys.path.insert(0, models_dir)
import importlib.util
from gecko import sample, to_bedrock
import portrait_sim
spec = importlib.util.spec_from_file_location("zamtrios_species", os.path.join(models_dir, "species", "zamtrios.py"))
Z = importlib.util.module_from_spec(spec); spec.loader.exec_module(Z)

SRC = os.path.join(models_dir, "src", "zamtrios")
DEX, SID, FOLDER = Z.DEX, Z.SID, Z.FOLDER
A = os.path.join(out, "assets/cobblemon")
TDIR = f"{A}/textures/pokemon/{FOLDER}"
for sub in ("models", "animations", "posers", "resolvers"):
    os.makedirs(f"{A}/bedrock/pokemon/{sub}/{FOLDER}", exist_ok=True)
os.makedirs(TDIR, exist_ok=True); os.makedirs(tmp, exist_ok=True)
FX = Z.FX
BALLOON_K = Z.BALLOON_K

MODELS = {"zamtrios": Z.build("normal"), "zamtrios_armor": Z.build("armor"), "zamtrios_inflated": Z.build("inflated")}
GLOW = tuple(b + "_glow" for b in Z.ICE_BONES)

# ------------------------------------------------------------------------------------------------ animations
SRC_A = json.load(open(f"{SRC}/zamtrios_remaster.animation.json"))["animations"]

def conv(name, t0=0.0, length=None, speed=1.0, loop=None):
    a = SRC_A[name]
    s, L = sample(a, fps=24, length=length, t0=t0, speed=speed)
    return to_bedrock(s, L, a.get("loop") if loop is None else loop)

def kf(points, loop_len=None):
    """{time: vec} with linear keys; a looping channel repeats its first key at the end"""
    d = {f"{t:g}" if t else "0.0": [round(x, 3) for x in v] for t, v in sorted(points.items())}
    return d

def wave(amp, period, length, phase=0.0, axis=0, base=(0, 0, 0), steps=12):
    """sinusoidal channel sampled into keys (loops cleanly when length is a multiple of period)"""
    pts = {}
    for i in range(steps + 1):
        t = length * i / steps
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (t / period) + phase)
        pts[round(t, 4)] = v
    return kf(pts)

def merge(*anims):
    out_ = {}
    for a in anims:
        for b, ch in a.items():
            out_.setdefault(b, {}).update(ch)
    return out_

def anim(length, bones_, loop=None):
    a = {"animation_length": round(length, 4), "bones": bones_}
    if loop is True:
        a["loop"] = True
    elif loop == "hold":
        a["loop"] = "hold_on_last_frame"
    return a

def hide_fx(a, extra=()):
    for b in FX + tuple(extra):
        a["bones"].setdefault(b, {}).setdefault("scale", [0, 0, 0])
    return a

def shift_root(a, dy):
    """lift / lower the whole model (adds to the root position channel)"""
    ch = a["bones"].setdefault("zamtrios", {})
    p = ch.get("position", [0, 0, 0])
    if isinstance(p, list):
        ch["position"] = [p[0], p[1] + dy, p[2]]
    else:
        ch["position"] = {t: [v[0], v[1] + dy, v[2]] for t, v in p.items()}
    return a

def base_set():
    S = {}
    S["ground_idle"] = conv("idle", loop=True)
    S["ground_walk"] = conv("walk", loop=True)
    S["ground_run"] = conv("run", loop=True)
    S["sleep"] = conv("sleep", loop=True)
    S["faint"] = conv("death", loop="hold")
    # cry: the roar, a little faster (head up, jaws wide, tail raised, shock wave on the ground)
    S["cry"] = conv("zamtriosroar", speed=1.35, loop=False)
    L = 2.0
    S["battle_idle"] = anim(L, merge(
        {"zamtrios": {"position": wave(0.8, L, L, axis=1, base=(0, -1.5, 0))}},
        {"body": {"rotation": wave(1.5, L, L, axis=0, base=(3, 0, 0))}},
        {"head": {"rotation": wave(2.5, L, L, phase=0.6, axis=0, base=(-5, 0, 0))}},
        {"jaw": {"rotation": wave(5, L / 2, L, axis=0, base=(10, 0, 0))}},
        {"leftarm": {"rotation": [0, 0, -6]}, "rightarm": {"rotation": [0, 0, 6]}},
        {"leftleg": {"rotation": [0, 0, -4]}, "rightleg": {"rotation": [0, 0, 4]}},
        {"tail1": {"rotation": wave(6, L, L, axis=1, base=(-4, 0, 0))}},
        {"tail2": {"rotation": wave(10, L, L, phase=-0.9, axis=1, base=(-4, 0, 0))}}), loop=True)
    # physical (1.1 s): pulls back, lunges with the jaws wide open and snaps them shut
    S["physical"] = anim(1.1, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .3: [0, -0.5, 6], .5: [0, -2.5, -16], .62: [0, -2.5, -15],
                                     .8: [0, -2, -8], 1.1: [0, -1.5, 0]})},
        "body": {"rotation": kf({0: [3, 0, 0], .3: [-7, 0, 0], .5: [8, 0, 0], .8: [4, 0, 0], 1.1: [3, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .3: [-20, 0, 0], .5: [6, 0, 0], .62: [10, 0, 0], .8: [0, 0, 0],
                                 1.1: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .3: [30, 0, 0], .5: [34, 0, 0], .58: [0, 0, 0], .8: [4, 0, 0],
                                1.1: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .3: [10, 0, -6], .5: [-22, 0, -8], .8: [-6, 0, -6], 1.1: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .3: [10, 0, 6], .5: [-22, 0, 8], .8: [-6, 0, 6], 1.1: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .3: [-14, 8, 0], .5: [6, -10, 0], .8: [0, -4, 0], 1.1: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .3: [-10, 14, 0], .5: [8, -16, 0], .8: [0, -6, 0], 1.1: [-4, 0, 0]})}})
    # special (1.4 s): rears its head, then blasts ice / water straight ahead, jaws wide, braced
    sh = {round(.6 + .08 * i, 3): [4, (2 if i % 2 else -2), 0] for i in range(7)}
    S["special"] = anim(1.4, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .35: [0, 0.5, 2], .6: [0, -2, 4], 1.1: [0, -2, 4],
                                     1.4: [0, -1.5, 0]})},
        "body": {"rotation": kf({0: [3, 0, 0], .35: [-9, 0, 0], .6: [2, 0, 0], 1.1: [2, 0, 0], 1.4: [3, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .35: [-28, 0, 0], **sh, 1.15: [2, 0, 0], 1.4: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .35: [14, 0, 0], .55: [38, 0, 0], 1.1: [38, 0, 0], 1.25: [8, 0, 0],
                                1.4: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .35: [-8, 0, -10], .6: [6, 0, -12], 1.1: [6, 0, -12], 1.4: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .35: [-8, 0, 10], .6: [6, 0, 12], 1.1: [6, 0, 12], 1.4: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .35: [8, 0, 0], .6: [-12, 0, 0], 1.1: [-12, 0, 0], 1.4: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .35: [10, 0, 0], .6: [-16, 0, 0], 1.1: [-16, 0, 0], 1.4: [-4, 0, 0]})}})
    # status (1.2 s): stamps both front feet and shakes itself, head held high
    S["status"] = anim(1.2, {
        "zamtrios": {"position": kf({0: [0, -1.5, 0], .25: [0, 1.5, 0], .4: [0, -2.5, 0], .65: [0, 1, 0],
                                     .8: [0, -2.5, 0], 1.2: [0, -1.5, 0]}),
                     "rotation": kf({0: [0, 0, 0], .45: [0, 0, 5], .6: [0, 0, -5], .75: [0, 0, 4], .9: [0, 0, -3],
                                     1.2: [0, 0, 0]})},
        "head": {"rotation": kf({0: [-5, 0, 0], .3: [-22, 0, 0], .9: [-18, 0, 0], 1.2: [-5, 0, 0]})},
        "jaw": {"rotation": kf({0: [10, 0, 0], .3: [24, 0, 0], .9: [20, 0, 0], 1.2: [10, 0, 0]})},
        "leftarm": {"rotation": kf({0: [0, 0, -6], .25: [-25, 0, -6], .4: [0, 0, -6], .65: [-20, 0, -6],
                                    .8: [0, 0, -6], 1.2: [0, 0, -6]})},
        "rightarm": {"rotation": kf({0: [0, 0, 6], .25: [-25, 0, 6], .4: [0, 0, 6], .65: [-20, 0, 6],
                                     .8: [0, 0, 6], 1.2: [0, 0, 6]})},
        "tail1": {"rotation": kf({0: [-4, 0, 0], .4: [-10, 12, 0], .8: [-10, -12, 0], 1.2: [-4, 0, 0]})},
        "tail2": {"rotation": kf({0: [-4, 0, 0], .4: [-8, 18, 0], .8: [-8, -18, 0], 1.2: [-4, 0, 0]})}})
    # swimming: limbs folded back along the body, the tail sweeps like a shark's
    def swim(L, amp_t, amp_b, paddle):
        return anim(L, merge(
            {"zamtrios": {"position": wave(1.2, L, L, axis=1, base=(0, 2, 0))}},
            {"body": {"rotation": wave(amp_b, L, L, axis=1, base=(0, 0, 0))}},
            {"head": {"rotation": wave(amp_b * 0.8, L, L, phase=math.pi, axis=1, base=(-4, 0, 0))}},
            {"jaw": {"rotation": [6, 0, 0]}},
            {"leftarm": {"rotation": wave(paddle, L, L, axis=0, base=(55, 0, -20))},
             "rightarm": {"rotation": wave(paddle, L, L, phase=math.pi, axis=0, base=(55, 0, 20))},
             "lowerleftarm": {"rotation": [-35, 0, 0]}, "lowerrightarm": {"rotation": [-35, 0, 0]},
             "leftleg": {"rotation": [60, 0, -8]}, "rightleg": {"rotation": [60, 0, 8]},
             "lowerleftleg": {"rotation": [-20, 0, 0]}, "lowerrightleg": {"rotation": [-20, 0, 0]}},
            {"tail1": {"rotation": wave(amp_t, L, L, phase=-0.8, axis=1, base=(0, 0, 0))}},
            {"tail2": {"rotation": wave(amp_t * 1.6, L, L, phase=-1.6, axis=1, base=(0, 0, 0))}}), loop=True)
    S["water_idle"] = swim(3.0, 8, 2, 4)
    S["water_swim"] = swim(1.2, 18, 5, 12)
    for a in S.values():
        hide_fx(a)
    return S

ARM_L = json.loads(os.environ.get("ARM_L", "[0, 25, 0]"))
ARM_R = [ARM_L[0], -ARM_L[1], -ARM_L[2]]
LOW_L = json.loads(os.environ.get("LOW_L", "[-65, 0, 0]"))
LOW_R = [LOW_L[0], -LOW_L[1], -LOW_L[2]]
HEAD_TILT = float(os.environ.get("HEAD_TILT", "20"))
HAND_L = json.loads(os.environ.get("HAND_L", "[55, 0, 0]"))
HAND_R = [HAND_L[0], -HAND_L[1], -HAND_L[2]]

def add_rot(a, bone, dx):
    """tilts a bone (adds dx to the X rotation of every key, or sets it when the bone has no rotation channel)"""
    ch = a["bones"].setdefault(bone, {})
    r = ch.get("rotation", [0, 0, 0])
    if isinstance(r, list):
        ch["rotation"] = [r[0] + dx, r[1], r[2]]
    else:
        ch["rotation"] = {t: [v[0] + dx, v[1], v[2]] for t, v in r.items()}
    return a

def inflated_set():
    """the giant inflated sac: the creature lies on top of it (its rest geometry is lifted by Z.LIFT), the head
    resting on the front slope (HEAD_TILT added to every head key), the fore limbs draped forward with the claws
    beside the head, the hind legs folded inside; the sac breathes (scale x2 = full size) with a heavy bob"""
    K = BALLOON_K
    LF = Z.LIFT
    def sac(points):
        return {"balloon": {"scale": kf({t: [K * v[0], K * v[1], K * v[2]] for t, v in points.items()})}}
    pose = {"leftarm": {"rotation": ARM_L}, "rightarm": {"rotation": ARM_R},
            "lowerleftarm": {"rotation": LOW_L}, "lowerrightarm": {"rotation": LOW_R},
            "lefthand": {"rotation": HAND_L}, "righthand": {"rotation": HAND_R},
            "tail1": {"rotation": [-14, 0, 0]}, "tail2": {"rotation": [-10, 0, 0]}}
    def with_pose(b):
        return merge(pose, b)
    S = {}
    L = 2.4
    breathe = sac({0: [1, 1, 1], L / 2: [1.04, 1.05, 1.04], L: [1, 1, 1]})
    S["ground_idle"] = anim(L, with_pose(merge(breathe,
        {"zamtrios": {"position": wave(1.0, L, L, axis=1, base=(0, 0, 0))}},
        {"head": {"rotation": wave(3, L, L, axis=0, base=(-6, 0, 0))}, "jaw": {"rotation": [6, 0, 0]}},
        {"tail2": {"rotation": wave(8, L, L, axis=1, base=(-10, 0, 0))}})), loop=True)
    S["battle_idle"] = anim(1.6, with_pose(merge(sac({0: [1, 1, 1], .8: [1.06, 1.07, 1.06], 1.6: [1, 1, 1]}),
        {"zamtrios": {"position": wave(1.6, 1.6, 1.6, axis=1, base=(0, 0.5, 0))}},
        {"head": {"rotation": wave(4, 1.6, 1.6, axis=0, base=(-10, 0, 0))}, "jaw": {"rotation": wave(6, .8, 1.6, axis=0, base=(14, 0, 0))}},
        {"leftarm": {"rotation": wave(10, 1.6, 1.6, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(10, 1.6, 1.6, phase=math.pi, axis=0, base=(-10, 0, 32))}})), loop=True)
    S["ground_walk"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .3: [1.05, .95, 1.05], .6: [1, 1, 1], .9: [1.05, .95, 1.05], 1.2: [1, 1, 1]}),
        {"zamtrios": {"rotation": wave(7, 1.2, 1.2, axis=2), "position": wave(1.5, .6, 1.2, axis=1, base=(0, 1.5, 0))}},
        {"leftarm": {"rotation": wave(20, 1.2, 1.2, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(20, 1.2, 1.2, phase=math.pi, axis=0, base=(-10, 0, 32))},
         "leftleg": {"rotation": wave(18, 1.2, 1.2, phase=math.pi, axis=0, base=(0, 0, -38))},
         "rightleg": {"rotation": wave(18, 1.2, 1.2, axis=0, base=(0, 0, 38))}})), loop=True)
    S["sleep"] = anim(3.0, with_pose(merge(sac({0: [1, .97, 1], 1.5: [1.02, 1, 1.02], 3.0: [1, .97, 1]}),
        {"zamtrios": {"position": [0, -1, 0]}, "head": {"rotation": [10, 0, 0]}, "jaw": {"rotation": [0, 0, 0]},
         "tail1": {"rotation": [-4, 18, 0]}, "tail2": {"rotation": [0, 24, 0]}})), loop=True)
    # body slam: hops high, slams down (the sac squashes), bounces back
    S["physical"] = anim(1.1, with_pose(merge(
        sac({0: [1, 1, 1], .25: [.95, 1.08, .95], .5: [1, 1, 1], .58: [1.16, .8, 1.16], .75: [.96, 1.06, .96],
             .9: [1.03, .98, 1.03], 1.1: [1, 1, 1]}),
        {"zamtrios": {"position": kf({0: [0, 0, 0], .25: [0, -1.5, 0], .42: [0, 16, -8], .56: [0, 0, -12],
                                      .75: [0, 3, -10], .9: [0, 0, -6], 1.1: [0, 0, 0]}),
                      "rotation": kf({0: [0, 0, 0], .42: [-12, 0, 0], .56: [8, 0, 0], .9: [0, 0, 0], 1.1: [0, 0, 0]})},
         "head": {"rotation": kf({0: [-6, 0, 0], .42: [-18, 0, 0], .56: [8, 0, 0], 1.1: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .42: [26, 0, 0], .58: [2, 0, 0], 1.1: [6, 0, 0]})}})))
    # special: puffs even bigger and sprays a jet of water from its jaws
    S["special"] = anim(1.4, with_pose(merge(
        sac({0: [1, 1, 1], .4: [1.12, 1.14, 1.12], .6: [1.02, 1.0, 1.02], 1.1: [.98, .97, .98], 1.4: [1, 1, 1]}),
        {"zamtrios": {"position": kf({0: [0, 0, 0], .4: [0, 3, 2], .6: [0, 1, 5], 1.1: [0, 1, 5], 1.4: [0, 0, 0]})},
         "head": {"rotation": kf({0: [-6, 0, 0], .4: [-28, 0, 0], .6: [-14, 0, 0], .85: [-12, 2, 0], 1.0: [-12, -2, 0],
                                  1.1: [-14, 0, 0], 1.4: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .4: [10, 0, 0], .55: [40, 0, 0], 1.1: [40, 0, 0], 1.3: [6, 0, 0],
                                 1.4: [6, 0, 0]})}})))
    # status: rolls a full turn on itself
    S["status"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .6: [1.06, 1.06, 1.06], 1.2: [1, 1, 1]}),
        {"zamtrios": {"rotation": kf({0: [0, 0, 0], .3: [0, 90, 0], .6: [0, 180, 0], .9: [0, 270, 0], 1.2: [0, 360, 0]}),
                      "position": kf({0: [0, 0, 0], .3: [0, 4, 0], .6: [0, 0, 0], .9: [0, 4, 0], 1.2: [0, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .6: [22, 0, 0], 1.2: [6, 0, 0]})}})))
    S["cry"] = anim(1.5, with_pose(merge(sac({0: [1, 1, 1], .4: [1.1, 1.12, 1.1], 1.1: [1.1, 1.12, 1.1], 1.5: [1, 1, 1]}),
        {"head": {"rotation": kf({0: [-6, 0, 0], .4: [-26, 0, 0], .7: [-24, 2, 0], .9: [-24, -2, 0], 1.1: [-24, 0, 0],
                                  1.5: [-6, 0, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .4: [36, 0, 0], 1.1: [36, 0, 0], 1.5: [6, 0, 0]})},
         "zamtrios": {"position": kf({0: [0, 0, 0], .4: [0, 3, 0], 1.1: [0, 3, 0], 1.5: [0, 0, 0]})}})))
    # faint: a last cry, head up, the sac deflates with a wobble and the body slumps
    S["faint"] = anim(2.2, merge(
        sac({0: [1, 1, 1], .4: [1.08, 1.1, 1.08], .7: [1.0, 1.0, 1.0], 1.0: [.8, .75, .8], 1.3: [.6, .55, .6],
             1.6: [.45, .4, .45], 1.9: [.3, .3, .3], 2.2: [.3, .3, .3]}),
        {"zamtrios": {"rotation": kf({0: [0, 0, 0], .7: [0, 0, 0], .85: [0, 12, 3], 1.0: [0, -10, -3],
                                      1.15: [0, 8, 2], 1.3: [0, -6, -2], 1.5: [0, 3, 0], 2.2: [0, 0, 6]}),
                      "position": kf({0: [0, 0, 0], .4: [0, 2, 0], 1.6: [0, -2, 0], 2.2: [0, -3, 0]})},
         "jaw": {"rotation": kf({0: [6, 0, 0], .35: [38, 0, 0], .8: [38, 0, 0], 1.4: [16, 0, 0], 2.2: [20, 0, 0]})},
         # the body sinks back to the ground as the sac empties
         "body": {"position": kf({0: [0, 0, 0], .7: [0, 0, 0], 1.0: [0, -LF * .25, 0], 1.3: [0, -LF * .5, 0],
                                  1.6: [0, -LF * .75, 0], 1.9: [0, -LF, 0], 2.2: [0, -LF, 0]})},
         "head": {"position": kf({0: [0, 0, 0], .7: [0, 0, 0], 1.0: [0, -LF * .25, 0], 1.3: [0, -LF * .5, 0],
                                  1.6: [0, -LF * .75, 0], 1.9: [0, -LF, 0], 2.2: [0, -LF, 0]}),
                  "rotation": kf({0: [-6, 0, 0], .4: [-34, 0, 0], .55: [-32, 3, 0], .7: [-34, -3, 0], 1.2: [-10, 0, 0],
                                  2.2: [14 - HEAD_TILT, 0, 0]})},
         "leftarm": {"rotation": kf({0: ARM_L, 1.4: [-10, 0, -12], 2.2: [0, 0, -40]})},
         "rightarm": {"rotation": kf({0: ARM_R, 1.4: [-10, 0, 12], 2.2: [0, 0, 40]})},
         "lowerleftarm": {"rotation": kf({0: LOW_L, 2.2: [0, 0, 30]})},
         "lowerrightarm": {"rotation": kf({0: LOW_R, 2.2: [0, 0, -30]})},
         "leftleg": {"rotation": kf({0: [0, 0, 0], 2.2: [0, 0, -20]})},
         "rightleg": {"rotation": kf({0: [0, 0, 0], 2.2: [0, 0, 20]})},
         "tail1": {"rotation": kf({0: [-14, 0, 0], 2.2: [4, 10, 0]})},
         "tail2": {"rotation": kf({0: [-10, 0, 0], 2.2: [2, 18, 0]})}}), loop="hold")
    S["water_idle"] = anim(3.0, with_pose(merge(breathe if False else sac({0: [1, 1, 1], 1.5: [1.03, 1.04, 1.03], 3.0: [1, 1, 1]}),
        {"zamtrios": {"position": wave(2, 3.0, 3.0, axis=1, base=(0, 4, 0)), "rotation": wave(4, 3.0, 3.0, axis=2)}})), loop=True)
    S["water_swim"] = anim(1.2, with_pose(merge(sac({0: [1, 1, 1], .6: [1.03, .98, 1.03], 1.2: [1, 1, 1]}),
        {"zamtrios": {"position": wave(1.5, 1.2, 1.2, axis=1, base=(0, 4, 0)), "rotation": wave(5, 1.2, 1.2, axis=2)},
         "leftarm": {"rotation": wave(25, 1.2, 1.2, axis=0, base=(-10, 0, -32))},
         "rightarm": {"rotation": wave(25, 1.2, 1.2, phase=math.pi, axis=0, base=(-10, 0, 32))},
         "tail2": {"rotation": wave(16, 1.2, 1.2, axis=1, base=(-10, 0, 0))}})), loop=True)
    for a in S.values():
        hide_fx(a)
        add_rot(a, "head", HEAD_TILT)                     # the head rests on the front slope of the sac
    return S

def armor_set():
    S = copy.deepcopy(base_set())
    for b in GLOW:                                         # asleep: the ice stops glowing
        S["sleep"]["bones"].setdefault(b, {})["scale"] = [0, 0, 0]
    return S

def finish(S, bones):
    """eyes shut while asleep; drop the channels of bones this model does not have (the source's spray effects)"""
    S["sleep"]["bones"].setdefault("eyes", {})["scale"] = [0, 0, 0]
    for a in S.values():
        for b in [b for b in a["bones"] if b not in bones]:
            del a["bones"][b]
    return S


ANIMS = {}
for name, m in MODELS.items():
    names = {b.name for b in m.bones}
    S = armor_set() if name == "zamtrios_armor" else (inflated_set() if name == "zamtrios_inflated" else base_set())
    ANIMS[name] = finish(S, names)

# ------------------------------------------------------------------------------------------------ posers
def poser(group, geo_bones):
    portrait_sim.set_mode("portrait")
    s, tx, ty = portrait_sim.auto_frame(geo_bones, fill=13.5, below=0.5, names=("head", "jaw"))
    qs, qx, qy = portrait_sim.auto_profile([b for b in geo_bones if b["name"] not in FX and b["name"] != "balloon"])
    q = lambda a: f"q.bedrock('{group}', '{a}')"
    prim = lambda a: f"q.bedrock_primary('{group}', '{a}', q.curve('symmetrical_wide'))"
    return {
        "portraitScale": s, "portraitTranslation": [tx, ty, 0], "profileScale": qs, "profileTranslation": [qx, qy, 0],
        "rootBone": "zamtrios",
        "animations": {"cry": f"q.bedrock_stateful('{group}', 'cry')",
                       "faint": f"q.bedrock_primary('{group}', 'faint', q.curve('one'))",
                       "physical": prim("physical"), "special": prim("special"), "status": prim("status")},
        "poses": {
            "battle-standing": {"poseTypes": ["STAND"], "isBattle": True,
                                "animations": ["q.look('head')", q("battle_idle")]},
            "standing": {"poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"], "isBattle": False,
                         "animations": ["q.look('head')", q("ground_idle")]},
            "walking": {"poseTypes": ["WALK"], "animations": ["q.look('head')", q("ground_walk")]},
            "floating": {"poseTypes": ["FLOAT"], "animations": ["q.look('head')", q("water_idle")]},
            "swimming": {"poseTypes": ["SWIM"], "animations": ["q.look('head')", q("water_swim")]},
            "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]}}}

tops, layers = {}, {}
for name, m in MODELS.items():
    textures = {suf: (lambda p: (m.texture(p), m.texture(dict(p, _only_glow=True), seed=101)))(
        dict(pal, _frost=True) if name == "zamtrios_armor" else pal) for suf, pal in (("", Z.NORMAL), ("_shiny", Z.SHINY))}
    if name == "zamtrios_inflated":
        Z.lift(m)                                          # painted in place, then lifted onto its sac
    g = m.geo()
    gb = g["minecraft:geometry"][0]["bones"]
    json.dump(g, open(f"{A}/bedrock/pokemon/models/{FOLDER}/{name}.geo.json", "w"), indent=1)
    json.dump(g, open(f"{tmp}/{name}.geo.json", "w"))
    an = {"format_version": "1.8.0", "animations": {f"animation.{name}.{k}": v for k, v in ANIMS[name].items()}}
    json.dump(an, open(f"{A}/bedrock/pokemon/animations/{FOLDER}/{name}.animation.json", "w"), indent=1)
    json.dump(an, open(f"{tmp}/{name}.animation.json", "w"))
    json.dump(poser(name, gb), open(f"{A}/bedrock/pokemon/posers/{FOLDER}/{name}.json", "w"), indent=2)
    for suf in ("", "_shiny"):
        img, glow = textures[suf]
        img.save(f"{TDIR}/{name}{suf}.png"); img.save(f"{tmp}/{name}{suf}.png")
        glow.save(f"{TDIR}/{name}{suf}_glow.png"); glow.save(f"{tmp}/{name}{suf}_glow.png")
        prev = img.copy(); prev.alpha_composite(glow); prev.save(f"{tmp}/{name}{suf}_preview.png")
        layers[(name, suf)] = [{"name": "emissive", "texture": f"cobblemon:textures/pokemon/{FOLDER}/{name}{suf}_glow.png",
                                "emissive": True}]
    # height of the standing model (feet to the top of the dorsal fin; ice, effects and the sac excluded)
    lo, hi = m.extent(skip=[b.name for b in m.bones if b.name in FX or b.name == "balloon" or "icearmor" in b.name])
    tops[name] = round(hi[1], 2)
    print(f"{name}: texture {m.tex_size}, {sum(len(b.cubes) for b in m.bones)} cubes, {len(m.bones)} bones, top {hi[1]:.1f}")

tex = lambda n: f"cobblemon:textures/pokemon/{FOLDER}/{n}.png"
res = f"{A}/bedrock/pokemon/resolvers/{FOLDER}"
for order, (name, aspect) in enumerate((("zamtrios", None), ("zamtrios_armor", "zamtrios-armor"),
                                        ("zamtrios_inflated", "zamtrios-inflated"))):
    asp = [aspect] if aspect else []
    json.dump({"species": f"cobblemon:{SID}", "order": order, "variations": [
        {"aspects": asp, "poser": f"cobblemon:{name}", "model": f"cobblemon:{name}.geo", "texture": tex(name),
         "layers": layers[(name, "")]},
        {"aspects": asp + ["shiny"], "texture": tex(name + "_shiny"), "layers": layers[(name, "_shiny")]}]},
        open(f"{res}/{order}_{name}.json", "w"), indent=2)
json.dump({"top_base": tops["zamtrios"], "top_armor": tops["zamtrios_armor"], "top_inflated": tops["zamtrios_inflated"]},
          open(f"{tmp}/zamtrios_tops.json", "w"))
