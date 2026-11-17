# -*- coding: utf-8 -*-
"""#1031 Drakkarthor — drakkar fantôme bipède. Ossature de brute-wyverne : dos voûté qui culmine aux épaules,
long cou qui plonge vers une tête basse à lourde mâchoire, petits bras, cuisses massives, pattes digitigrades,
longue queue-contrepoids terminée en étambot. Thème conservé : coque de bois délavé à clins, bastingage,
boucliers, mât et voile rayée en lambeaux, flammes spectrales bleues, yeux luisants."""
import math
from modelgen import Model, Cube, rgb, fill
from templates import closed_eye_lines, flame, clinker, round_shield, sail, bark, tremble, slit_eye, glow_trail, sockets
from biped import (Leg, walk, leg_pose, timeline, keys, lowest, drape, standard_anims, lie_legs, pose_sequence,
                   search, descendants, pose_to_bones)
from templates import poser as make_poser

SID, DEX = "drakkarthor", 1031

PAL = {
    "hull": rgb("#5B6150"), "hull_dark": rgb("#363B30"), "belly": rgb("#8C9A8A"), "rim": rgb("#2C3027"),
    "mast": rgb("#4A3B2C"), "bark": rgb("#4A3B2C"), "bark_dark": rgb("#2E241A"),
    "sail_a": rgb("#9E3A3A"), "sail_b": rgb("#D8D2C0"),
    "shield_a": rgb("#7A5A5A"), "shield_b": rgb("#8A8A70"), "shield_rim": rgb("#4A4A40"), "boss": rgb("#7FE8FF"),
    "claw": rgb("#C9C3B0"), "mouth": rgb("#1E3A5A"),
    "eye": rgb("#5FD8FF"), "eye_shine": rgb("#FFFFFF"), "eye_hot": rgb("#D8FCFF"), "pupil": rgb("#08121C"),
    "socket": rgb("#111512"),
    "flame_core": rgb("#E8FFFF"), "flame_mid": rgb("#8FE6FF"), "flame_out": rgb("#3FA8FF"), "flame_tip": rgb("#2A5CFF"),
}
SHINY = dict(PAL, **{
    "hull": rgb("#CFC8B8"), "hull_dark": rgb("#9C9584"), "belly": rgb("#E8E2D2"), "rim": rgb("#7E7868"),
    "sail_a": rgb("#3A2A4A"), "sail_b": rgb("#6A5A7A"),
    "shield_a": rgb("#5A4A6A"), "shield_b": rgb("#B8B0A0"), "boss": rgb("#A8FF9A"),
    "mouth": rgb("#1E4A2A"), "eye": rgb("#8CFF7A"), "eye_hot": rgb("#EFFFE6"), "pupil": rgb("#071A0B"),
    "flame_core": rgb("#F0FFE8"), "flame_mid": rgb("#A8FF9A"), "flame_out": rgb("#4AE07A"), "flame_tip": rgb("#1FA85A"),
})

F = {"fn": flame(), "glow": True, "shading": False}
HULL = {"base": "hull", "fn": clinker}

def glow_eye(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        if w and h:
            fill(px, x, y, w, h, pal["eye"], 1.0)
            px[x + w // 2, y] = pal["eye_shine"]

def head_fn(px, faces, pal, rnd):
    clinker(px, faces, pal, rnd)
    sockets(range(0, 3), list(range(0, 5)) + list(range(6, 11)))(px, faces, pal, rnd)
    x, y, w, h = faces["down"]
    fill(px, x, y, w, h, pal["belly"], 0.95, rnd)

def snout_fn(px, faces, pal, rnd):
    x, y, w, h = faces["north"]
    px[x + 1, y] = pal["rim"]; px[x + w - 2, y] = pal["rim"]
    x, y, w, h = faces["down"]                       # upper teeth along the front and sides of the snout
    for i in range(0, w, 2):
        px[x + i, y] = pal["claw"]
    for fc in ("north", "east", "west"):
        x, y, w, h = faces[fc]
        for i in range(0, w, 2):
            px[x + i, y + h - 1] = pal["claw"]

def jaw_fn(px, faces, pal, rnd):
    x, y, w, h = faces["up"]
    fill(px, x, y, w, h, pal["mouth"], 1.0, rnd)
    for i in range(0, w, 2):                          # lower teeth: front row and both sides
        px[x + i, y] = pal["claw"]
    for j in range(0, h, 2):
        px[x, y + j] = pal["claw"]; px[x + w - 1, y + j] = pal["claw"]

LEG_PAINT = {"thigh": HULL, "shin": {"base": "hull"}, "meta": {"base": "rim"}, "foot": {"base": "rim"},
             "claw": {"base": "claw"}}
LEGS = [Leg(side, 6.5 * sx, 3, (10, 10, 6), (-30, 38, -22), 2, thigh=(6, 8, 3), shin=(5, 5), meta=(4, 4),
            foot=(6, 7, 2), claws=(-2, 0, 2), paints=LEG_PAINT) for side, sx in (("left", 1), ("right", -1))]
H = LEGS[0].H
TAIL = ("tail", "tail2", "tail3", "tail4")
FLAMES = ("mane", "mane_neck", "flames_left", "flames_right", "tail_flame", "ankle_flame_left", "ankle_flame_right")

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, H, 3])
    for lg in LEGS:
        lg.build(m)
        x, ay = lg.x, H - lg.L[0] - lg.L[1]
        m.bone(f"ankle_flame_{lg.side}", lg.bones[2], [x, ay, 3], cubes=[
            Cube([x, ay - 6, 1], [0, 5, 4], F), Cube([x - 2, ay - 6, 3], [4, 5, 0], F)])
    m.bone("torso", "body", [0, H, 3], rotation=[-10, 0, 0], cubes=[
        Cube([-6.5, H - 5, -3], [13, 10, 12], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker}),
        Cube([-7, H + 4.5, -3], [14, 1, 12], {"base": "rim"}),
        Cube([7, H + 5.5, -2.5], [0, 3, 11], F), Cube([-7, H + 5.5, -2.5], [0, 3, 11], F)])
    shields = [Cube([7.55 * sx, H - 3, z], [0, 4, 4], {"fn": round_shield(), "shading": False})
               for sx in (1, -1) for z in (-12.5, -8)]
    m.bone("chest", "torso", [0, H + 1, -3], rotation=[-8, 0, 0], cubes=[
        Cube([-7.5, H - 6, -14], [15, 13, 11], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker}),
        Cube([-8, H + 6.5, -14], [16, 1, 11], {"base": "rim"})] + shields)
    for side, sx in (("left", 1), ("right", -1)):
        m.bone(f"flames_{side}", "chest", [8 * sx, H + 7.5, -8.5], cubes=[Cube([8 * sx, H + 7.5, -13.5], [0, 3, 10], F)])
    m.bone("mast", "chest", [0, H + 7, -8], rotation=[18, 0, 0], cubes=[
        Cube([-0.5, H + 7, -8.5], [1, 11, 1], {"base": "mast", "fn": bark}),
        Cube([-6, H + 16, -8.5], [12, 1, 1], {"base": "mast", "fn": bark})])
    m.bone("sail", "mast", [0, H + 16, -7.5], cubes=[
        Cube([-5.5, H + 9, -7.5], [11, 7, 0], {"fn": sail(tatter=0.05), "shading": False})])
    for side, sx in (("left", 1), ("right", -1)):
        ax = 5.5 * sx
        m.bone(f"arm_{side}", "chest", [ax, H - 2, -11.5], rotation=[25, 0, -10 * sx], cubes=[
            Cube([ax - 1, H - 8, -12.5], [2, 7, 2], HULL)])
        m.bone(f"forearm_{side}", f"arm_{side}", [ax, H - 7.5, -11.5], rotation=[-75, 0, 0], cubes=[
            Cube([ax - 1, H - 12.5, -12.5], [2, 5, 2], {"base": "hull"}),
            Cube([ax - 1, H - 13.5, -12.5], [1, 1, 1], {"base": "claw"}),
            Cube([ax, H - 13.5, -12.5], [1, 1, 1], {"base": "claw"})])
    # neck plunges forward-down from the shoulder hump (absolute +42°), head re-levelled to +12°
    m.bone("neck", "chest", [0, H + 4, -13], rotation=[60, 0, 0], cubes=[
        Cube([-4.5, H - 3, -23], [9, 9, 10], {"base": "hull", "belly": "belly", "belly_faces": ("north",), "fn": clinker})])
    m.bone("mane_neck", "neck", [0, H + 6, -18], rotation=[-42, 0, 0], cubes=[Cube([0, H + 6, -22.5], [0, 4, 9], F)])
    m.bone("head", "neck", [0, H + 2, -22], rotation=[-30, 0, 0], cubes=[
        Cube([-5.5, H - 1, -33], [11, 7, 11], {"base": "hull", "fn": head_fn}),
        Cube([-4, H - 1, -37], [8, 4, 4], {"base": "hull", "fn": snout_fn}),
    ])
    for side, sx in (("left", 1), ("right", -1)):
        hx = 4 * sx
        m.bone(f"horn_{side}", "head", [hx, H + 5.5, -24], rotation=[-25, 0, 0], cubes=[
            Cube([hx - 0.5, H + 5, -24], [1, 2, 7], {"base": "rim"}),
            Cube([hx - 0.5, H + 6, -18], [1, 3, 1], {"base": "rim"})])
    m.bone("mane", "head", [0, H + 6, -27], cubes=[
        Cube([0, H + 6, -31], [0, 5, 8], F), Cube([-3, H + 6, -26], [6, 5, 0], F)])
    m.bone("jaw", "head", [0, H - 1, -23], cubes=[Cube([-5, H - 4, -37], [10, 3, 14], {"base": "hull", "down": "belly", "fn": jaw_fn})])
    m.bone("eyes", "head", [0, H + 4, -33])
    G = {"fn": slit_eye, "glow": True, "shading": False}
    TR = {"fn": glow_trail, "glow": True, "shading": False}
    m.bone("eye_left", "eyes", [3, H + 4, -33.05], cubes=[
        Cube([1.5, H + 3, -33.05], [3, 2, 0], G), Cube([5.55, H + 3.5, -32], [0, 1, 4], TR)])
    m.bone("eye_right", "eyes", [-3, H + 4, -33.05], cubes=[
        Cube([-4.5, H + 3, -33.05], [3, 2, 0], G), Cube([-5.55, H + 3.5, -32], [0, 1, 4], TR)])
    # heavy brow ridges in a V: low over the inner corners of the eyes, rising outward
    m.bone("brow_left", "head", [0.5, H + 4.2, -32.5], rotation=[0, 0, -18], cubes=[
        Cube([0.5, H + 4.2, -34.2], [6, 1, 3], {"base": "rim"})])
    m.bone("brow_right", "head", [-0.5, H + 4.2, -32.5], rotation=[0, 0, 18], cubes=[
        Cube([-6.5, H + 4.2, -34.2], [6, 1, 3], {"base": "rim"})])
    m.bone("tail", "torso", [0, H + 1, 9], rotation=[14, 0, 0], cubes=[
        Cube([-4.5, H - 3, 9], [9, 8, 10], {"base": "hull", "belly": "belly", "fn": clinker}),
        Cube([0, H + 5, 10], [0, 3, 8], F)])
    m.bone("tail2", "tail", [0, H + 1, 19], rotation=[2, 0, 0], cubes=[
        Cube([-3.5, H - 2, 19], [7, 6, 10], {"base": "hull", "belly": "belly", "fn": clinker}),
        Cube([0, H + 4, 20], [0, 3, 8], F)])
    m.bone("tail3", "tail2", [0, H + 1, 29], rotation=[4, 0, 0], cubes=[
        Cube([-2.5, H - 1, 29], [5, 4, 9], {"base": "hull", "belly": "belly"}),
        Cube([0, H + 3, 30], [0, 2, 7], F)])
    m.bone("tail4", "tail3", [0, H + 1, 38], rotation=[35, 0, 0], cubes=[Cube([-1.5, H - 0.5, 38], [3, 3, 6], {"base": "rim"})])
    m.bone("tail_flame", "tail4", [0, H + 2.5, 44], rotation=[-45, 0, 0], cubes=[
        Cube([0, H + 2.5, 42], [0, 5, 4], F), Cube([-2, H + 2.5, 44], [4, 5, 0], F)])
    m.pack()
    return m

# ---------------------------------------------------------------------------- animations
def sway(freq, mul=1.0):
    q = "q.anim_time"
    return {"flames_left": {"rotation": [f"math.sin({q}*{freq})*{4 * mul}", 0, 0]},
            "flames_right": {"rotation": [f"math.sin({q}*{freq}+90)*{4 * mul}", 0, 0]},
            "mane": {"rotation": [0, 0, f"math.sin({q}*{freq})*{5 * mul}"]},
            "mane_neck": {"rotation": [0, 0, f"math.sin({q}*{freq}+60)*{5 * mul}"]},
            "tail_flame": {"rotation": [f"math.sin({q}*{freq})*{7 * mul}", 0, 0]},
            "sail": {"rotation": [f"math.sin({q}*{freq * 0.5})*{3 * mul}", 0, 0]}}

def cry():
    """Rears up and roars: gathers itself (crouch, neck coiled), rises tall on its hind legs with the chest
    lifted, neck raised, jaws gaping and trembling, arms spread, tail lashing, every flame flaring;
    then slams back down and settles."""
    L = 2.8
    b = timeline(LEGS, L, [(0, 0, 0), (0.45, -2.5, 0), (0.8, 2.0, 0), (1.9, 1.8, 0), (2.25, -1.2, 0), (2.8, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.45: [7, 0, 0], 0.8: [-20, 0, 0], 1.9: [-18, 0, 0], 2.25: [5, 0, 0], 2.8: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.45: [3, 0, 0], 0.8: [-8, 0, 0], 1.9: [-7, 0, 0], 2.25: [2, 0, 0], 2.8: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.45: [14, 0, 0], 0.8: [-30, 0, 0], 1.9: [-28, 0, 0], 2.25: [6, 0, 0], 2.8: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.45: [8, 0, 0], 0.8: [-20, 0, 0], 0.85: [tremble(-20, 2100, 2), 0, 0],
                               1.85: [tremble(-18, 2100, 2), 0, 0], 2.25: [4, 0, 0], 2.8: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.5: [0, 0, 0], 0.8: [40, 0, 0], 0.85: [tremble(40, 1800, 2.5), 0, 0],
                              1.85: [tremble(38, 1800, 2.5), 0, 0], 2.15: [0, 0, 0], 2.8: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.45: [15, 0, 0], 0.8: [-35, 0, -18 * sx], 1.9: [-30, 0, -15 * sx], 2.8: [0, 0, 0]})
        b[f"forearm_{side}"] = keys(rotation={0: [0, 0, 0], 0.8: [-20, 0, 0], 1.9: [-18, 0, 0], 2.8: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.45: [-4, 0, 0], 0.8: [18, 0, 0], 1.0: [18, 18, 0], 1.2: [18, -18, 0], 1.4: [17, 14, 0],
                               1.6: [17, -10, 0], 1.9: [16, 6, 0], 2.3: [0, 0, 0], 2.8: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.9: [0, 0, 0], 1.1: [0, 20, 0], 1.3: [0, -20, 0], 1.5: [0, 15, 0], 1.7: [0, -10, 0],
                                2.0: [0, 5, 0], 2.8: [0, 0, 0]})
    b["tail3"] = keys(rotation={0: [0, 0, 0], 1.0: [0, 0, 0], 1.2: [0, 24, 0], 1.4: [0, -24, 0], 1.6: [0, 16, 0], 1.8: [0, -10, 0],
                                2.1: [0, 4, 0], 2.8: [0, 0, 0]})
    b["sail"] = keys(rotation={0: [0, 0, 0], 0.5: [-6, 0, 0], 0.8: [12, 0, 0], 1.1: [4, 0, 0], 1.4: [10, 0, 0], 1.9: [3, 0, 0], 2.8: [0, 0, 0]})
    for fl in FLAMES:
        b[fl] = keys(scale={0: [1, 1, 1], 0.75: [1, 1, 1], 0.88: [1.35, 1.8, 1.35], 1.85: [1.25, 1.6, 1.25], 2.2: [1, 1, 1], 2.8: [1, 1, 1]})
    for e in ("eye_left", "eye_right"):                     # eyes narrow with fury, brows furrow
        b[e] = keys(scale={0: [1, 1, 1], 0.75: [1, 1, 1], 0.85: [1.1, 0.65, 1], 1.85: [1.1, 0.65, 1], 2.05: [1, 1, 1], 2.8: [1, 1, 1]})
    for br, sg in (("brow_left", -1), ("brow_right", 1)):
        b[br] = keys(rotation={0: [0, 0, 0], 0.4: [0, 0, 4 * sg], 0.85: [0, 0, 10 * sg], 1.85: [0, 0, 10 * sg], 2.1: [0, 0, 0], 2.8: [0, 0, 0]})
    return {"animation_length": L, "bones": b}

TRUNK = ({"torso", "chest"} | {b for lg in LEGS for b in lg.bones[:2]}
         | {"arm_left", "arm_right", "forearm_left", "forearm_right"})
SKIP = FLAMES + ("sail", "eye_left", "eye_right")

def _head_group(m):
    return descendants(m, "head") - set(SKIP)

def sleep_pose(m):
    """Heavy predator asleep: belly on the ground, legs folded under like a resting bird, neck laid out in front
    and turned aside, chin flat on the ground, tail curled forward around the body (crescent)."""
    base = {"torso": {"rotation": [10, 0, 0]}, "chest": {"rotation": [8, 0, 0]},
            "arm_left": {"rotation": [50, 0, -8]}, "arm_right": {"rotation": [50, 0, 8]},
            "forearm_left": {"rotation": [40, 0, 0]}, "forearm_right": {"rotation": [40, 0, 0]},
            "mast": {"rotation": [0, 0, -6]}, "sail": {"rotation": [14, 0, 0]}}
    pose = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()}
    lie_legs(m, LEGS, pose, TRUNK)
    pose.update({k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()})
    head = _head_group(m)
    # neck stretched forward (absolute pitch ~0..+25 deg) and turned aside; head levelled so the jaw lies flat
    grid = [[nx, 30, 0] for nx in range(-62, -24, 2)]
    pose["head"] = {"rotation": [22, 10, 6]}
    search(m, pose, "neck", grid, 0.6, head, keep={"neck"})
    search(m, pose, "head", [[hx, 10, 6] for hx in range(4, 42, 2)], 0.4, head, keep={"neck"})
    for tb, yaw, lim in zip(TAIL, (-24, -34, -40, -36), (-30, -18, -14, -10)):
        search(m, pose, tb, [[x, yaw, 0] for x in range(lim, 6, 2)], 0.3, descendants(m, tb) - set(SKIP))
    return pose

def sleep_anim(m):
    q = "q.anim_time"
    b = pose_to_bones(sleep_pose(m))
    b["chest"]["position"] = [0, f"0.3+math.sin({q}*45)*0.3", 0]                 # slow, deep breathing
    b["torso"]["position"] = [0, f"0.15+math.sin({q}*45-30)*0.15", 0]
    b["jaw"] = {"rotation": [f"3+math.sin({q}*45-60)*2", 0, 0]}
    b["tail4"]["rotation"][1] = f"{b['tail4']['rotation'][1]}+math.sin({q}*30)*4"  # tail tip twitches
    for e in ("eye_left", "eye_right"):
        b[e] = {"scale": [1, 0.02, 1]}
    for fl in FLAMES:                                                                # flames burn low
        b[fl] = {"scale": [f"0.5+math.sin({q}*90)*0.06", f"0.4+math.sin({q}*120)*0.08", 0.5]}
    return {"loop": True, "animation_length": 8, "bones": b}

def ko_anim(m):
    """Collapse of a huge monster: recoils from the blow, staggers, the knees give way and it drops on its chest,
    topples onto its flank, the neck follows and the head slams down (one bounce, jaw falling open), the tail
    flops down last; a final exhale, the sail sags and the spectral flames die out."""
    stand = lambda h: {b: {"rotation": r} for b, r in leg_pose(LEGS, h).items()}
    folded = {b: v for b, v in sleep_pose(m).items() if b in {x for lg in LEGS for x in lg.bones}}
    limp = {b: {"rotation": [round(v["rotation"][0] * 0.55, 2), 0, 0]} for b, v in folded.items()}
    def P(*parts):
        out = {}
        for part in parts:
            for k, v in part.items():
                out[k] = {kk: list(vv) for kk, vv in v.items()}
        return out
    arms = lambda x, z=0: {"arm_left": {"rotation": [x, 0, -z]}, "arm_right": {"rotation": [x, 0, z]}}
    k0 = P(stand(0))
    k1 = P(stand(0.6), {"torso": {"rotation": [-9, 0, 0]}, "chest": {"rotation": [-4, 0, 0]}, "neck": {"rotation": [-16, 0, 0]},
                        "head": {"rotation": [-18, 0, 0]}, "jaw": {"rotation": [24, 0, 0]}, "tail": {"rotation": [8, 0, 0]},
                        "tail2": {"rotation": [4, 0, 0]}}, arms(-25, 12))
    k2 = P(stand(-1.0), {"torso": {"rotation": [6, 0, 7]}, "chest": {"rotation": [2, 0, 2]}, "neck": {"rotation": [14, 10, 0]},
                         "head": {"rotation": [12, 0, -12]}, "jaw": {"rotation": [12, 0, 0]}, "tail": {"rotation": [0, -14, 0]},
                         "tail2": {"rotation": [0, -10, 0]}}, arms(20))
    k3 = P(stand(-2.4), {"torso": {"rotation": [9, 0, -7]}, "chest": {"rotation": [3, 0, -2]}, "neck": {"rotation": [20, -12, 0]},
                         "head": {"rotation": [16, 0, 12]}, "jaw": {"rotation": [8, 0, 0]}, "tail": {"rotation": [-4, 14, 0]},
                         "tail2": {"rotation": [0, 12, 0]}}, arms(25))
    k4 = P(folded, {"body": {"rotation": [4, 0, 0]}, "torso": {"rotation": [14, 0, 0]}, "chest": {"rotation": [10, 0, 0]},
                    "neck": {"rotation": [-6, 0, 0]}, "head": {"rotation": [-10, 0, 0]}, "jaw": {"rotation": [6, 0, 0]},
                    "tail": {"rotation": [-8, 0, 0]}}, arms(45))
    k5 = P(limp, {"body": {"rotation": [2, 0, 74]}, "torso": {"rotation": [10, 0, 0]}, "chest": {"rotation": [6, 0, 0]},
                  "neck": {"rotation": [-14, 0, 0]}, "head": {"rotation": [-12, 0, 0]}, "jaw": {"rotation": [10, 0, 0]},
                  "tail": {"rotation": [12, 0, 0]}, "mast": {"rotation": [0, 0, -10]}}, arms(25, -10))
    # head slams to the ground: search a neck bend (in the toppled frame) that lays the head down
    k6 = P(k5, {"jaw": {"rotation": [16, 0, 0]}, "head": {"rotation": [6, 0, 0]}})
    k6["body"]["position"] = [0, -lowest(m, k5, skip=SKIP), 0]
    head = _head_group(m)
    search(m, k6, "neck", [[x, 0, z] for x in range(-40, 31, 5) for z in range(-50, 51, 5)], 0.3, head,
           keep={"neck", "chest"}, penalty=0.004, skip=SKIP)
    k7 = P(k6, {"neck": {"rotation": [k6["neck"]["rotation"][0] - 6, 0, k6["neck"]["rotation"][2] - 6]},
                "jaw": {"rotation": [10, 0, 0]}})
    k8 = P(k6)
    search(m, k8, "tail", [[x, 0, z] for x in range(-30, 31, 5) for z in range(-50, 51, 5)], 0.3,
           descendants(m, "tail") - set(SKIP), penalty=0.004, skip=SKIP)
    k8["tail2"] = {"rotation": [0, 10, 0]}
    k9 = P(k8, {"chest": {"rotation": [8, 0, 0]}, "sail": {"rotation": [22, 0, 0]}, "mast": {"rotation": [0, 0, -16]},
                "jaw": {"rotation": [18, 0, 0]}})
    for kp in (k6, k7, k8, k9):
        kp["body"].pop("position", None)
    b = pose_sequence(m, [(0, k0), (0.22, k1), (0.55, k2), (0.85, k3), (1.15, k4), (1.55, k5), (1.8, k6),
                          (1.92, k7), (2.05, k6), (2.3, k8), (2.7, k9), (3.0, k9)], length=3.0, step=0.05, skip=SKIP)
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.22: [1, 0.6, 1], 0.5: [1, 1, 1], 1.5: [1, 1, 1], 1.9: [1, 0.02, 1], 3.0: [1, 0.02, 1]})
    for fl in FLAMES:
        b[fl] = keys(scale={0: [1, 1, 1], 0.22: [1.3, 1.5, 1.3], 0.6: [1, 1, 1], 1.6: [0.8, 0.7, 0.8], 2.4: [0.25, 0.1, 0.25],
                            2.8: [0.05, 0.02, 0.05], 3.0: [0.05, 0.02, 0.05]})
    return {"animation_length": 3.0, "bones": b}

def anims(m=None):
    m = m or build()
    out = standard_anims(SID, m, LEGS, tail=TAIL, flames=FLAMES, sway=sway, crouch=-2.5, level=(10, 8),
                         skip=FLAMES + ("sail",),
                         walk_kw=dict(T=1.3, stride=14, lift=4, stance=0.62, bob=0.7, torso=(1.5, 3, 3.5),
                                      tail_amp=(5, 8, 11, 13), arm_amp=6),
                         cry=cry(), faint_extra={"mast": {"rotation": [0, 0, -15]}})
    bt = out[f"animation.{SID}.battle_idle"]["bones"]           # permanent scowl in battle
    bt["brow_left"] = {"rotation": [0, 0, f"-6+math.sin(q.anim_time*180)*1.5"]}
    bt["brow_right"] = {"rotation": [0, 0, f"6-math.sin(q.anim_time*180)*1.5"]}
    bt["eye_left"] = bt["eye_right"] = {"scale": [1, 0.85, 1]}
    out[f"animation.{SID}.sleep"] = sleep_anim(m)
    out[f"animation.{SID}.faint"] = ko_anim(m)
    return out

def poser():
    return make_poser(SID, portrait=(1.0, [-0.68, 0.82, 0]), profile=(0.47, [0.06, 1.04, 0]))
