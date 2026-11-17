# -*- coding: utf-8 -*-
"""#1029 Drakflam — bébé de la lignée : même ossature bipède digitigrade, en version poupon. Corps rond presque
dressé, grosse tête portée haute, petits bras, courtes pattes, queue recourbée en étambot avec sa flamme.
Coque de drakkar à clins, petits boucliers, crête, crinière de feu, cornes rabattues."""
from modelgen import Model, Cube, rgb, fill
from templates import closed_eye_lines, flame, clinker, round_shield, eye_fn, leaf_shaped, tremble
from templates import poser as make_poser
from biped import Leg, timeline, keys, standard_anims

SID, DEX = "drakflam", 1029

PAL = {
    "hull": rgb("#C8553A"), "hull_dark": rgb("#8E3426"), "belly": rgb("#F0D9A8"), "fin": rgb("#A63D2C"),
    "claw": rgb("#F3EBC8"), "eye": rgb("#1E1E2A"), "eye_shine": rgb("#FFFFFF"), "mouth": rgb("#8E2A2A"),
    "flame_core": rgb("#FFF2A8"), "flame_mid": rgb("#FFC23A"), "flame_out": rgb("#FF7A1E"), "flame_tip": rgb("#E8452C"),
    "shield_a": rgb("#D9A33A"), "shield_b": rgb("#2F5C8A"), "shield_rim": rgb("#6B4423"), "boss": rgb("#9AA0A8"),
}
SHINY = dict(PAL, **{
    "hull": rgb("#3E3E48"), "hull_dark": rgb("#26262E"), "belly": rgb("#D9D2C2"), "fin": rgb("#2E2E36"),
    "flame_core": rgb("#FFFBE0"), "flame_mid": rgb("#FFE680"), "flame_out": rgb("#FFC94A"), "flame_tip": rgb("#F0A030"),
    "shield_a": rgb("#E8E4D8"), "shield_b": rgb("#3A6EA8"),
})

F = {"fn": flame(), "glow": True, "shading": False}
HULL = {"base": "hull", "fn": clinker}

def head_fn(px, faces, pal, rnd):
    closed_eye_lines((0, 1, 3, 4), 2)(px, faces, pal, rnd)
    x, y, w, h = faces["down"]
    fill(px, x, y, w, h, pal["belly"], 0.95, rnd)

def snout_fn(px, faces, pal, rnd):
    x, y, w, h = faces["north"]
    px[x, y] = pal["hull_dark"]; px[x + w - 1, y] = pal["hull_dark"]
    x, y, w, h = faces["down"]
    fill(px, x, y, w, h, pal["belly"], 0.95, rnd)

def jaw_fn(px, faces, pal, rnd):
    x, y, w, h = faces["up"]
    fill(px, x, y, w, h, pal["mouth"], 1.0, rnd)

LEG_PAINT = {"thigh": HULL, "shin": {"base": "hull"}, "meta": {"base": "hull"}, "foot": {"base": "hull_dark"},
             "claw": {"base": "claw"}}
LEGS = [Leg(side, 2.5 * sx, 1.5, (3, 3, 2), (-25, 35, -15), 1, thigh=(3, 4, 1), shin=(2, 2), meta=(2, 2),
            foot=(3, 4, 1), claws=(-1, 0, 1), paints=LEG_PAINT, claw_len=1, dewclaw=False)
        for side, sx in (("left", 1), ("right", -1))]
H = LEGS[0].H
TAIL = ("tail", "tail2")
FLAMES = ("mane", "mane_back", "tail_flame")

def build():
    m = Model(SID, DEX, (64, 64))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, H, 1.5])
    for lg in LEGS:
        lg.build(m)
    spikes = [Cube([-0.5, H + 2.5, z], [1, 1, 1], {"base": "hull_dark"}, rotation=[30, 0, 0], pivot=[0, H + 2.5, z + 0.5])
              for z in (-0.5, 1.5)]
    m.bone("torso", "body", [0, H, 1.5], rotation=[-22, 0, 0], cubes=[
        Cube([-3, H - 2.5, -1.5], [6, 5, 6], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker})] + spikes)
    m.bone("mane_back", "torso", [0, H + 2.5, 2.5], cubes=[Cube([0, H + 2.5, 2], [0, 2, 3], F)])
    shields = [Cube([3.05 * sx, H - 1.5, -4], [0, 2, 2], {"fn": round_shield(), "shading": False}) for sx in (1, -1)]
    m.bone("chest", "torso", [0, H + 1, -1.5], rotation=[-10, 0, 0], cubes=[
        Cube([-3, H - 2.5, -5], [6, 6, 4], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker})] + shields)
    for side, sx in (("left", 1), ("right", -1)):
        ax = 2.5 * sx
        m.bone(f"arm_{side}", "chest", [ax, H - 0.5, -4], rotation=[20, 0, -10 * sx], cubes=[
            Cube([ax - 0.5, H - 3, -4.5], [1, 3, 1], {"base": "hull"})])
        m.bone(f"forearm_{side}", f"arm_{side}", [ax, H - 2.5, -4], rotation=[-70, 0, 0], cubes=[
            Cube([ax - 0.5, H - 4.5, -4.5], [1, 2, 1], {"base": "hull"}), Cube([ax - 0.5, H - 5, -4.5], [1, 1, 1], {"base": "claw"})])
    # neck rises (absolute -10°): a whelp holds its big head up
    m.bone("neck", "chest", [0, H + 3, -4], rotation=[22, 0, 0], cubes=[
        Cube([-1.5, H + 1, -6], [3, 3, 3], {"base": "hull", "belly": "belly", "belly_faces": ("north",)})])
    m.bone("head", "neck", [0, H + 2.5, -5.5], rotation=[10, 0, 0], cubes=[
        Cube([-2.5, H + 1, -10.5], [5, 5, 5], {"base": "hull", "fn": head_fn}),
        Cube([-1.5, H + 1, -12.5], [3, 2, 2], {"base": "hull", "fn": snout_fn}),
        Cube([1, H + 5.5, -8.5], [1, 1, 3], {"base": "claw"}, rotation=[25, 0, 0], pivot=[1.5, H + 5.5, -7.5]),
        Cube([-2, H + 5.5, -8.5], [1, 1, 3], {"base": "claw"}, rotation=[25, 0, 0], pivot=[-1.5, H + 5.5, -7.5]),
        Cube([2.5, H + 3.5, -8.5], [0, 3, 3], {"fn": leaf_shaped("fin", "hull_dark", False), "shading": False},
             rotation=[0, -25, 0], pivot=[2.5, H + 3.5, -7]),
        Cube([-2.5, H + 3.5, -8.5], [0, 3, 3], {"fn": leaf_shaped("fin", "hull_dark", False), "shading": False},
             rotation=[0, 25, 0], pivot=[-2.5, H + 3.5, -7])])
    m.bone("mane", "head", [0, H + 6, -8], cubes=[Cube([0, H + 6, -10.5], [0, 3, 5], F), Cube([-1.5, H + 6, -8], [3, 3, 0], F)])
    m.bone("jaw", "head", [0, H + 1, -6], cubes=[Cube([-1.5, H, -12.25], [3, 1, 6], {"base": "belly", "fn": jaw_fn})])
    m.bone("eyes", "head", [0, H + 4, -10.5])
    m.bone("eye_left", "eyes", [1.5, H + 4, -10.55], cubes=[Cube([0.5, H + 3, -10.55], [2, 2, 0], {"fn": eye_fn, "shading": False})])
    m.bone("eye_right", "eyes", [-1.5, H + 4, -10.55], cubes=[Cube([-2.5, H + 3, -10.55], [2, 2, 0], {"fn": eye_fn, "shading": False})])
    m.bone("tail", "torso", [0, H + 0.5, 4.5], rotation=[26, 0, 0], cubes=[
        Cube([-1, H - 0.5, 4.5], [2, 2, 4], {"base": "hull", "belly": "belly", "fn": clinker})])
    m.bone("tail2", "tail", [0, H + 0.5, 8.5], rotation=[30, 0, 0], cubes=[Cube([-0.5, H, 8.5], [1, 1, 3], {"base": "hull_dark"})])
    m.bone("tail_flame", "tail2", [0, H + 1, 11.5], rotation=[-34, 0, 0], cubes=[
        Cube([0, H + 1, 10], [0, 4, 3], F), Cube([-1.5, H + 1, 11.5], [3, 4, 0], F)])
    m.pack()
    return m

def sway(freq, mul=1.0):
    q = "q.anim_time"
    return {"mane": {"rotation": [0, 0, f"math.sin({q}*{freq})*{6 * mul}"]},
            "mane_back": {"rotation": [0, 0, f"math.sin({q}*{freq}+90)*{6 * mul}"]},
            "tail_flame": {"rotation": [f"math.sin({q}*{freq})*{8 * mul}", 0, 0]}}

def cry():
    """Whelp's double bark: puffs up, hops on the spot and lets out two snapping barks, flames flaring."""
    L = 1.5
    b = timeline(LEGS, L, [(0, 0, 0), (0.15, -0.7, 0), (0.3, 0.6, 0), (0.42, -0.2, 0), (0.58, 0.6, 0), (0.75, -0.3, 0), (1.5, 0, 0)],
                 step=0.05)
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.15: [5, 0, 0], 0.32: [-8, 0, 0], 0.45: [-3, 0, 0], 0.6: [-9, 0, 0], 0.9: [-2, 0, 0], 1.5: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.15: [1.05, 1.06, 1.04], 0.35: [0.99, 0.98, 1], 1.5: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.15: [8, 0, 0], 0.32: [-8, 0, 0], 0.6: [-10, 0, 0], 1.0: [0, 0, 0], 1.5: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.15: [6, 0, 0], 0.32: [-14, 0, 0], 0.46: [-6, 0, 0], 0.62: [-16, 0, 0], 1.0: [-3, 0, 0], 1.5: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.28: [0, 0, 0], 0.34: [28, 0, 0], 0.46: [6, 0, 0], 0.62: [30, 0, 0], 0.9: [0, 0, 0], 1.5: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.32: [-30, 0, -15 * sx], 0.62: [-34, 0, -18 * sx], 1.0: [0, 0, 0], 1.5: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.32: [10, 18, 0], 0.48: [10, -18, 0], 0.64: [10, 18, 0], 0.82: [6, -10, 0], 1.2: [0, 0, 0], 1.5: [0, 0, 0]})
    for fl in FLAMES:
        b[fl] = keys(scale={0: [1, 1, 1], 0.3: [1, 1, 1], 0.36: [1.3, 1.6, 1.3], 0.48: [1.1, 1.2, 1.1], 0.64: [1.4, 1.7, 1.4], 1.0: [1, 1, 1], 1.5: [1, 1, 1]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 1, 1], 0.36: [1, 0.5, 1], 0.8: [1, 0.5, 1], 0.9: [1, 1, 1], 1.5: [1, 1, 1]})
    return {"animation_length": L, "bones": b}

def anims(m=None):
    m = m or build()
    return standard_anims(SID, m, LEGS, tail=TAIL, flames=FLAMES, sway=sway, crouch=-0.8, level=(22, 10),
                          skip=FLAMES, battle_head=-6, idle_amp=1.3,
                          walk_kw=dict(T=0.5, stride=4, lift=1.4, stance=0.55, bob=0.35, torso=(2, 4, 6),
                                       tail_amp=(10, 14), arm_amp=10),
                          sleep_kw=dict(curl=(35, 40), tail_drop=(-40, -30), head_clear=0.6),
                          cry=cry())

def poser():
    return make_poser(SID, portrait=(2.34, [-0.41, -0.57, 0]), profile=(1.0, [0.0, 0.24, 0]))
