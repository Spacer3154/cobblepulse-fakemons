# -*- coding: utf-8 -*-
"""#1030 Vikinav — même ossature de brute-wyverne que Drakkarthor, en plus jeune et plus trapu :
navire de chêne cerclé de fer riveté, boucliers, casque à nasal, cornes de fer, crinière et étambot enflammés.
Moins voûté que son évolution : cou plus court, tête portée à hauteur des épaules."""
from modelgen import Model, Cube, rgb, fill
from templates import closed_eye_lines, flame, clinker, round_shield, metal, rivets, chain, tremble, eye_fn, slit_eye, sockets
from templates import poser as make_poser
from biped import Leg, timeline, keys, standard_anims

SID, DEX = "vikinav", 1030

PAL = {
    "hull": rgb("#A3543A"), "hull_dark": rgb("#6E3424"), "belly": rgb("#E8CFA0"), "fin": rgb("#7A3626"),
    "hoop": rgb("#6E737C"), "hoop_light": rgb("#A9AFB8"), "rivet": rgb("#3E4249"),
    "claw": rgb("#F3EBC8"), "eye": rgb("#FF8A1E"), "eye_hot": rgb("#FFE27A"), "pupil": rgb("#1A0804"),
    "socket": rgb("#24100A"), "eye_shine": rgb("#FFFFFF"), "mouth": rgb("#8E2A2A"),
    "flame_core": rgb("#FFF2A8"), "flame_mid": rgb("#FFC23A"), "flame_out": rgb("#FF7A1E"), "flame_tip": rgb("#E8452C"),
    "shield_a": rgb("#D9A33A"), "shield_b": rgb("#2F5C8A"), "shield_rim": rgb("#B07A44"), "boss": rgb("#B8BEC6"),
}
SHINY = dict(PAL, **{
    "hull": rgb("#3E3E48"), "hull_dark": rgb("#26262E"), "belly": rgb("#D9D2C2"), "fin": rgb("#2E2E36"),
    "hoop": rgb("#C9A440"), "hoop_light": rgb("#F2DA7A"), "rivet": rgb("#8A6A20"),
    "flame_core": rgb("#FFFBE0"), "flame_mid": rgb("#FFE680"), "flame_out": rgb("#FFC94A"), "flame_tip": rgb("#F0A030"),
    "shield_a": rgb("#E8E4D8"), "shield_b": rgb("#3A6EA8"),
    "eye": rgb("#FFC93A"), "eye_hot": rgb("#FFF8D0"), "socket": rgb("#101014"),
})

F = {"fn": flame(), "glow": True, "shading": False}
IRON = {"base": "hoop", "fn": chain(metal, rivets())}
HULL = {"base": "hull", "fn": clinker}

def head_fn(px, faces, pal, rnd):
    sockets(range(1, 3), range(0, 8))(px, faces, pal, rnd)
    x, y, w, h = faces["down"]
    fill(px, x, y, w, h, pal["belly"], 0.95, rnd)

def snout_fn(px, faces, pal, rnd):
    x, y, w, h = faces["north"]
    px[x + 1, y] = pal["hull_dark"]; px[x + w - 2, y] = pal["hull_dark"]
    x, y, w, h = faces["down"]
    for i in range(0, w, 2):
        px[x + i, y] = pal["claw"]

def jaw_fn(px, faces, pal, rnd):
    x, y, w, h = faces["up"]
    fill(px, x, y, w, h, pal["mouth"], 1.0, rnd)
    px[x, y] = pal["claw"]; px[x + w - 1, y] = pal["claw"]
    px[x + 2, y] = pal["claw"]; px[x + w - 3, y] = pal["claw"]

def greave(px, faces, pal, rnd):
    """iron greave on the lower part of the shin"""
    for fc in ("north", "south", "east", "west"):
        x, y, w, h = faces[fc]
        fill(px, x, y + h - 3, w, 3, pal["hoop"], 1.0, rnd, 3)
        for i in range(w):
            px[x + i, y + h - 3] = pal["hoop_light"]

LEG_PAINT = {"thigh": HULL, "shin": {"base": "hull", "fn": greave}, "meta": {"base": "hull_dark"},
             "foot": {"base": "hull_dark"}, "claw": {"base": "claw"}}
LEGS = [Leg(side, 4.5 * sx, 2, (6, 6, 4), (-28, 36, -20), 2, thigh=(4, 6, 2), shin=(3, 3), meta=(3, 3),
            foot=(4, 5, 1.5), claws=(-1.5, 0, 1.5), paints=LEG_PAINT) for side, sx in (("left", 1), ("right", -1))]
H = LEGS[0].H
TAIL = ("tail", "tail2", "tail3")
FLAMES = ("mane", "mane_neck", "mane_back", "tail_flame")

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, H, 2])
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, H, 2], rotation=[-14, 0, 0], cubes=[
        Cube([-4.5, H - 3.5, -2], [9, 7, 9], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker}),
        Cube([-5, H - 4, 3], [10, 8, 1], IRON)])
    m.bone("mane_back", "torso", [0, H + 3.5, 2], cubes=[Cube([0, H + 3.5, -1], [0, 3, 7], F)])
    shields = [Cube([5.6 * sx, H - 2.5, -9], [0, 4, 4], {"fn": round_shield(), "shading": False}) for sx in (1, -1)]
    m.bone("chest", "torso", [0, H + 1, -2], rotation=[-8, 0, 0], cubes=[
        Cube([-5, H - 4.5, -10], [10, 10, 8], {"base": "hull", "belly": "belly", "belly_rows": 2, "fn": clinker}),
        Cube([-5.5, H - 5, -5], [11, 11, 1], IRON)] + shields)
    for side, sx in (("left", 1), ("right", -1)):
        ax = 4 * sx
        m.bone(f"arm_{side}", "chest", [ax, H - 1.5, -8.5], rotation=[25, 0, -10 * sx], cubes=[
            Cube([ax - 1, H - 6, -9.5], [2, 5, 2], HULL)])
        m.bone(f"forearm_{side}", f"arm_{side}", [ax, H - 5.5, -8.5], rotation=[-75, 0, 0], cubes=[
            Cube([ax - 1, H - 9, -9.5], [2, 4, 2], {"base": "hull", "fn": greave}),
            Cube([ax - 1, H - 10, -9.5], [1, 1, 1], {"base": "claw"}), Cube([ax, H - 10, -9.5], [1, 1, 1], {"base": "claw"})])
    m.bone("neck", "chest", [0, H + 3.5, -9.5], rotation=[45, 0, 0], cubes=[
        Cube([-3, H - 1.5, -16], [6, 6, 7], {"base": "hull", "belly": "belly", "belly_faces": ("north",), "fn": clinker})])
    m.bone("mane_neck", "neck", [0, H + 4.5, -12.5], rotation=[-23, 0, 0], cubes=[Cube([0, H + 4.5, -15.5], [0, 3, 6], F)])
    m.bone("head", "neck", [0, H + 1.5, -15.5], rotation=[-20, 0, 0], cubes=[
        Cube([-4, H - 1, -23], [8, 6, 8], {"base": "hull", "fn": head_fn}),
        Cube([-3, H - 1, -26], [6, 3, 3], {"base": "hull", "fn": snout_fn}),
        Cube([-4.5, H + 4, -23.5], [9, 2, 9], IRON),
        Cube([-0.5, H + 1.5, -23.75], [1, 3, 1], {"base": "hoop", "fn": metal})])
    for side, sx in (("left", 1), ("right", -1)):
        bx = 4.5 if sx > 0 else -7.5
        ux = 6.5 if sx > 0 else -7.5
        m.bone(f"horn_{side}", "head", [4.5 * sx, H + 5, -19.5], cubes=[
            Cube([bx, H + 4.5, -20], [3, 1, 1], {"base": "hoop", "fn": metal}),
            Cube([ux, H + 5.5, -20], [1, 3, 1], {"base": "hoop", "fn": metal}),
            Cube([ux, H + 8.5, -20.5], [1, 1, 1], {"base": "hoop_light"})])
    m.bone("mane", "head", [0, H + 6, -19], cubes=[Cube([0, H + 6, -22], [0, 4, 6], F), Cube([-2, H + 6, -18.5], [4, 4, 0], F)])
    m.bone("jaw", "head", [0, H - 1, -16], cubes=[Cube([-3, H - 3, -25.5], [6, 2, 10], {"base": "hull", "down": "belly", "fn": jaw_fn})])
    m.bone("eyes", "head", [0, H + 3, -23])
    G = {"fn": slit_eye, "glow": True, "shading": False}                 # embers glowing behind the helmet guards
    m.bone("eye_left", "eyes", [2.2, H + 3, -23.05], cubes=[Cube([0.7, H + 2, -23.05], [3, 2, 0], G)])
    m.bone("eye_right", "eyes", [-2.2, H + 3, -23.05], cubes=[Cube([-3.7, H + 2, -23.05], [3, 2, 0], G)])
    # "spectacle" guards of a Viking helmet: brow plates sloping down to the nasal (V), outer rims
    m.bone("brow_left", "head", [0.5, H + 3.6, -23.6], rotation=[0, 0, -16], cubes=[
        Cube([0.5, H + 3.6, -24.1], [4, 1, 1], {"base": "hoop", "fn": metal})])
    m.bone("brow_right", "head", [-0.5, H + 3.6, -23.6], rotation=[0, 0, 16], cubes=[
        Cube([-4.5, H + 3.6, -24.1], [4, 1, 1], {"base": "hoop", "fn": metal})])
    m.get("head").cubes += [Cube([3.7, H + 1.5, -24.1], [1, 3, 1], {"base": "hoop", "fn": metal}),
                            Cube([-4.7, H + 1.5, -24.1], [1, 3, 1], {"base": "hoop", "fn": metal})]
    m.bone("tail", "torso", [0, H + 1, 7], rotation=[18, 0, 0], cubes=[
        Cube([-3, H - 2, 7], [6, 5, 7], {"base": "hull", "belly": "belly", "fn": clinker})])
    m.bone("tail2", "tail", [0, H + 1, 14], rotation=[2, 0, 0], cubes=[
        Cube([-2, H - 1.5, 14], [4, 4, 7], {"base": "hull", "belly": "belly", "fn": clinker})])
    m.bone("tail3", "tail2", [0, H + 1, 21], rotation=[35, 0, 0], cubes=[
        Cube([-1, H - 0.5, 21], [2, 3, 4], {"base": "hull_dark"}), Cube([-1.5, H - 1, 24], [3, 4, 1], {"base": "hoop", "fn": metal})])
    m.bone("tail_flame", "tail3", [0, H + 1.5, 25], rotation=[-41, 0, 0], cubes=[
        Cube([0, H + 1.5, 23.5], [0, 5, 4], F), Cube([-2, H + 1.5, 25.5], [4, 5, 0], F)])
    m.pack()
    return m

def sway(freq, mul=1.0):
    q = "q.anim_time"
    return {"mane": {"rotation": [0, 0, f"math.sin({q}*{freq})*{5 * mul}"]},
            "mane_neck": {"rotation": [0, 0, f"math.sin({q}*{freq}+60)*{5 * mul}"]},
            "mane_back": {"rotation": [0, 0, f"math.sin({q}*{freq}+120)*{5 * mul}"]},
            "tail_flame": {"rotation": [f"math.sin({q}*{freq})*{7 * mul}", 0, 0]}}

def cry():
    """War bellow: braces and shakes its iron horns, then straightens up and bellows with the neck stretched,
    jaws wide and trembling, arms spread, tail lashing, flames roaring up; settles back."""
    L = 2.3
    b = timeline(LEGS, L, [(0, 0, 0), (0.35, -1.4, 0), (0.75, 1.2, 0), (1.6, 1.0, 0), (1.9, -0.6, 0), (2.3, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.35: [5, 0, 0], 0.75: [-14, 0, 0], 1.6: [-12, 0, 0], 1.9: [3, 0, 0], 2.3: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.35: [10, 0, 0], 0.75: [-16, 0, 0], 1.6: [-14, 0, 0], 1.9: [4, 0, 0], 2.3: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.1: [6, 14, 0], 0.22: [6, -14, 0], 0.35: [8, 0, 0], 0.75: [-12, 0, 0],
                               0.8: [tremble(-12, 2000, 1.8), 0, 0], 1.55: [tremble(-11, 2000, 1.8), 0, 0], 1.9: [2, 0, 0], 2.3: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.4: [0, 0, 0], 0.75: [34, 0, 0], 0.8: [tremble(34, 1700, 2), 0, 0],
                              1.55: [tremble(32, 1700, 2), 0, 0], 1.8: [0, 0, 0], 2.3: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.35: [12, 0, 0], 0.75: [-30, 0, -16 * sx], 1.6: [-26, 0, -14 * sx], 2.3: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.75: [12, 0, 0], 0.95: [12, 16, 0], 1.15: [12, -16, 0], 1.35: [11, 12, 0],
                               1.6: [10, -6, 0], 2.0: [0, 0, 0], 2.3: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.85: [0, 0, 0], 1.05: [0, 18, 0], 1.25: [0, -18, 0], 1.45: [0, 12, 0], 1.7: [0, -6, 0], 2.3: [0, 0, 0]})
    for fl in FLAMES:
        b[fl] = keys(scale={0: [1, 1, 1], 0.7: [1, 1, 1], 0.82: [1.4, 1.8, 1.4], 1.55: [1.3, 1.6, 1.3], 1.9: [1, 1, 1], 2.3: [1, 1, 1]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.7: [1, 1, 1], 0.8: [1, 0.55, 1], 1.55: [1, 0.55, 1], 1.7: [1, 1, 1], 2.3: [1, 1, 1]})
    for br, sg in (("brow_left", -1), ("brow_right", 1)):
        b[br] = keys(rotation={0: [0, 0, 0], 0.35: [0, 0, 4 * sg], 0.8: [0, 0, 9 * sg], 1.55: [0, 0, 9 * sg], 1.8: [0, 0, 0], 2.3: [0, 0, 0]})
    return {"animation_length": L, "bones": b}

def anims(m=None):
    m = m or build()
    out = standard_anims(SID, m, LEGS, tail=TAIL, flames=FLAMES, sway=sway, crouch=-1.6, level=(14, 8),
                          skip=FLAMES, battle_head=-8,
                          walk_kw=dict(T=0.95, stride=8, lift=2.5, stance=0.6, bob=0.45, torso=(1.5, 3, 3),
                                       tail_amp=(6, 9, 12), arm_amp=6),
                          sleep_kw=dict(curl=(25, 30, 30), tail_drop=(-35, -25, -10)),
                          cry=cry())
    bt = out[f"animation.{SID}.battle_idle"]["bones"]           # permanent scowl in battle
    bt["brow_left"] = {"rotation": [0, 0, "-6+math.sin(q.anim_time*180)*1.5"]}
    bt["brow_right"] = {"rotation": [0, 0, "6-math.sin(q.anim_time*180)*1.5"]}
    bt["eye_left"] = bt["eye_right"] = {"scale": [1, 0.85, 1]}
    return out

def poser():
    return make_poser(SID, portrait=(1.29, [-0.63, 0.5, 0]), profile=(0.72, [-0.01, 0.66, 0]))
