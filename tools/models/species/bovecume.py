# -*- coding: utf-8 -*-
"""#1033 Bovécume — vache / taureau normand dans la boue et les marécages (Eau / Sol).
A heavy young marsh bull: deep chest, muscular hump on the withers, thick neck carried low, broad head with short
forward-curving horns and small heavy-lidded eyes under a soaked forelock. Its coat is gorged with salt water and
silt: shaggy fringes drip under the belly, the brisket and the dewlap, the legs and lower body are caked with
estuary mud up to the knees, and wrack seaweed hangs over the hump and a horn. Sea-teal brindled Normande patches
and 'lunettes' (shiny: chestnut brindle, dark peat mud)."""
from modelgen import Model, Cube, rgb
from bovine import (make_legs, coat, hoof, add_eye, closed_lids, muzzle_fn, ear_fn, solid, fringe, kelp, vnoise, bovine_anims,
                    finalize, SIDES, bovine_poser)

SID, DEX = "bovecume", 1033

PAL = {
    "coat": rgb("#E3E5DF"), "coat_wet": rgb("#AFBDC0"), "patch": rgb("#2E7189"), "brindle": rgb("#1A485C"),
    "lunette": rgb("#21546A"), "water": rgb("#9FD8EE"),
    "mud": rgb("#7C6C55"), "mud_dark": rgb("#4D4235"), "wet": rgb("#98A29C"),
    "hoof": rgb("#3A3631"), "hoof_dark": rgb("#211F1C"), "hoof_light": rgb("#575047"),
    "horn": rgb("#E6DCBF"), "horn_mid": rgb("#BFAF8C"), "horn_tip": rgb("#4A4338"),
    "muzzle": rgb("#9E7C82"), "muzzle_wet": rgb("#C2A8AC"), "nostril": rgb("#4C3337"), "mouth": rgb("#6C4950"),
    "eye": rgb("#120C0A"), "eye_shine": rgb("#E8E0D0"), "eye_iris": rgb("#6E3420"), "eye_iris2": rgb("#A0542E"),
    "eye_white": rgb("#ECE8DE"), "lash": rgb("#120C0A"), "eye_dark": rgb("#16100D"),
    "ear_in": rgb("#C49C9E"), "ear_in_light": rgb("#D4B2B4"),
    "kelp": rgb("#5B6D2A"), "kelp_dark": rgb("#3A4719"), "kelp_light": rgb("#93A447"), "wrack": rgb("#7A6727"),
}
SHINY = dict(PAL, **{
    "coat": rgb("#ECE5D8"), "coat_wet": rgb("#BFB4A2"), "patch": rgb("#8A4A22"), "brindle": rgb("#472612"),
    "lunette": rgb("#5E3016"), "mud": rgb("#5C5248"), "mud_dark": rgb("#332D28"), "wet": rgb("#A39886"),
    "eye_iris": rgb("#5A2A14"), "eye_iris2": rgb("#8E4A22"),
})

# ---------------------------------------------------------------- legs: short, thick, heavy hooves
FRONT = dict(x=3.6, z=-8.5, L=(5, 6, 5), a=(22, -6, 0), th=2, thigh=(5, 6, 2), shin=(4, 4), meta=(3, 3), foot=(4, 4, 2))
BACK = dict(x=3.6, z=8.5, L=(6, 6, 5), a=(-18, 32, -4), th=2, thigh=(5, 6, 2), shin=(4, 5), meta=(3, 3), foot=(4, 4, 2))

PATCH = [(6.6, 17.5, 3.0, 2.6, 4.6, 5.6), (6.4, 19.0, -6.0, 2.4, 3.6, 3.0), (-6.6, 18.0, -3.5, 2.6, 4.2, 5.0),
         (-6.2, 16.5, 8.5, 2.4, 3.8, 3.4), (6.9, 17.5, -11.0, 2.4, 3.6, 3.0), (0.0, 27.0, -9.5, 5.0, 2.2, 4.4),
         (3.0, 21.5, 11.6, 2.8, 2.4, 1.6), (5.0, 14.0, 8.5, 2.0, 3.0, 3.0), (-2.5, 23.2, 4.0, 2.6, 1.2, 3.0)]

def splash(p, face, key):
    """mud splashes thrown up on the flanks and legs"""
    if p[1] < 15 and vnoise(p[0] * 0.9 + 3, p[1] * 0.9, p[2] * 0.9, 77) > 0.8:
        return "mud"
    return key

MUD_BODY = dict(y=11.8, key="mud", dark="mud_dark", wet="wet", rag=2.6, wet_h=1.6)
MUD_LEGS = dict(y=7.5, key="mud", dark="mud_dark", wet="wet", rag=2.8, wet_h=1.8)
BODY = coat(PATCH, mud=MUD_BODY, extra=splash, seed=5, warp=1.5, streak=0.56)
LEGC = coat(PATCH, mud=MUD_LEGS, extra=splash, seed=5, warp=1.5, streak=0.56)
FR = {"fn": fringe("coat", "coat_wet", "water", mud_key="mud"), "shading": False}
FRP = {"fn": fringe("patch", "brindle", "water", mud_key="mud"), "shading": False}
FRH = {"fn": fringe("coat", "coat_wet", "water"), "shading": False}
KELP = {"fn": kelp(), "shading": False}
LEG_PAINT = {"thigh": LEGC, "shin": LEGC, "meta": LEGC, "foot": {"fn": hoof}}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 17.7, 0)

# head: modelled level in the neck's unrotated frame, poll at the neck's front-top
HY, HZ = 24.5, -20.0
# deep-set bull eyes: a heavy lid sloping down towards the nose (frown), white of the eye at the outer corner,
# red-brown iris with a dull glint (rows top -> bottom, col 0 = outer corner)
EYE = dict(x_edge=3.5, w=3, y0=HY - 4.5, h=4, z_face=HZ - 7.0, d=0, lash_row=2,
           front=[".DD",            # heavy lid sloping down towards the nose
                  "WSD",            # white of the eye, glint
                  "IEI",            # red-brown iris, pupil
                  "JII"],
           side_rows=["DD"])
HEAD = coat([(sx * 4.8, HY - 5.0, HZ - 3.5, 1.6, 4.6, 4.4) for sx in (1, -1)] + [(0, HY + 0.6, HZ - 2.5, 4.4, 1.5, 3.0)],
            lunettes=[(sx * 2.4, HY - 2.5, HZ - 7.0, 2.6, 2.4, 1.2) for sx in (1, -1)], space="local", seed=9,
            extra=closed_lids(**EYE),
            warp=1.0, streak=0.56)

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 18, 2], cubes=[
        Cube([-6, 11, -5], [12, 12, 16], BODY),
        Cube([-5, 10, -4], [10, 1, 13], BODY),                                     # belly
        Cube([-5, 13, 11], [10, 9, 1], BODY),                                      # rump
        Cube([-1.5, 22.5, 9.5], [3, 1, 2], BODY),                                  # tailhead
        Cube([6.05, 8.5, -4], [0, 3, 14], FR), Cube([-6.05, 8.5, -4], [0, 3, 14], FR)])   # dripping belly fringe
    m.bone("chest", "torso", [0, 18, -5], cubes=[
        Cube([-6.5, 10, -13], [13, 14, 8], BODY),
        Cube([-5, 9, -12.5], [10, 1, 6], BODY),                                    # brisket
        Cube([-5.5, 24, -13], [11, 2, 9], BODY), Cube([-4.5, 26, -12], [9, 2, 7], BODY),
        Cube([-3, 28, -11], [6, 1, 4], BODY),                                      # muscular hump on the withers
        Cube([6.55, 7.5, -12.5], [0, 3, 7], FR), Cube([-6.55, 7.5, -12.5], [0, 3, 7], FR),
        Cube([-4.5, 6.5, -13.55], [9, 4, 0], FR),                                  # brisket beard
        # wrack seaweed draped over the hump and hanging down the shoulders
        Cube([-3.5, 29, -10], [7, 1, 3], {"fn": solid("kelp")}),
        Cube([3.05, 25.5, -10], [0, 4, 3], KELP), Cube([-3.05, 25.5, -10], [0, 4, 3], KELP),
        Cube([4.55, 23.5, -10.5], [0, 4, 4], KELP), Cube([-4.55, 23.5, -10.5], [0, 4, 4], KELP),
        Cube([5.55, 19.5, -11], [0, 6, 4], KELP), Cube([-5.55, 20.5, -10], [0, 5, 3], KELP)])
    m.bone("neck", "chest", [0, 21, -12.5], rotation=[12, 0, 0], cubes=[
        Cube([-4.5, 15, -20], [9, 9, 8], BODY),
        Cube([-1.5, 12.5, -19.5], [3, 3, 6], BODY),                                # dewlap
        Cube([0, 9.5, -19.5], [0, 3, 6], FRP)])
    m.bone("head", "neck", [0, HY - 0.5, HZ], rotation=[10, 0, 0], cubes=[
        Cube([-4.5, HY - 9, HZ - 7], [9, 9, 7], HEAD),
        Cube([-3.5, HY, HZ - 5], [7, 1, 4], HEAD),                                 # poll
        Cube([-3.5, HY - 9, HZ - 10], [7, 4, 3], {"base": "muzzle", "fn": muzzle_fn()}),
        Cube([-3.5, HY - 1.5, HZ - 7.6], [7, 3, 0], FRH)])                         # soaked forelock
    m.bone("jaw", "head", [0, HY - 9, HZ - 3.5], cubes=[
        Cube([-3, HY - 10, HZ - 9.5], [6, 1, 6], {"base": "coat", "up": "mouth", "north": "muzzle"})])
    for side, sx in SIDES:
        add_eye(m, "head", side, sx, **EYE)
        eo = 4.5 if sx > 0 else -9.5
        m.bone(f"ear_{side}", "head", [4.5 * sx, HY - 3, HZ - 2.5], rotation=[0, 0, 40 * sx], cubes=[
            Cube([eo, HY - 4, HZ - 3], [5, 2, 1], {"base": "patch", "fn": ear_fn})])
        b1 = 4 if sx > 0 else -8
        m.bone(f"horn_{side}", "head", [4 * sx, HY - 0.5, HZ - 2], rotation=[0, 0, -12 * sx], cubes=[
            Cube([b1, HY - 1.5, HZ - 3], [4, 2, 2], {"fn": solid("horn")})])
        b2 = 6.5 if sx > 0 else -8.5
        m.bone(f"horn2_{side}", f"horn_{side}", [7.5 * sx, HY - 0.5, HZ - 2], rotation=[-22, 16 * sx, 0], cubes=[
            Cube([b2, HY - 1.5, HZ - 5], [2, 2, 3], {"fn": solid("horn_mid")})]
            + ([Cube([7.5, HY - 5.5, HZ - 4.5], [0, 5, 2], KELP)] if sx > 0 else []))
        b3 = 7 if sx > 0 else -8
        m.bone(f"horn3_{side}", f"horn2_{side}", [7.5 * sx, HY - 0.5, HZ - 5], rotation=[-22, 10 * sx, 0], cubes=[
            Cube([b3, HY - 1, HZ - 7], [1, 1, 2], {"fn": solid("horn_tip")})])
    m.bone("tail", "torso", [0, 22.5, 11.5], rotation=[10, 0, 0], cubes=[
        Cube([-1, 13.5, 11], [2, 9, 2], BODY)])
    m.bone("tail_tip", "tail", [0, 13.5, 12], cubes=[
        Cube([-1.5, 9, 10.5], [3, 5, 3], {"fn": fringe("coat_wet", "mud", "water"), "shading": False}),
        Cube([-1, 10, 11], [2, 4, 2], {"base": "mud"})])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=(), torso=(1.0, 2.0, 2.5),
                       walk_kw=dict(T=1.15, stride=9, lift=2.4, stance=0.68, bob=0.5, toe_off=18, fold=50, curl=28),
                       battle=dict(theta=3.5, dy=-1.0, neck=14, head=-18, paw="front_right", paw_t=0.9,
                                   ears_back=10, tail_up=10),
                       cry=dict(L=2.3, t_in=0.35, t_open=0.75, t_close=1.7, neck=4, head=-8, jaw=12, yaw=9,
                                theta=1.5, tremble=1.2))
    return finalize(out)

def poser():
    return bovine_poser(SID, portrait=(1.24, [-0.84, 0.37, 0]), profile=(0.67, [-0.23, 0.73, 0]))
