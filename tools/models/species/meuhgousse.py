# -*- coding: utf-8 -*-
"""#1032 Meuhgousse — veau normand (race Normande) & écume marine des estuaires.
Calf proportions: long legs, short body, big head with large dark eyes ringed by the breed's 'lunettes',
floppy ears, horn buds, wet pink muzzle. Its fleece secretes sea foam: a bubbly foam cape on the back, a foam
forelock between the horn buds and a foam switch at the tail. Sea-blue brindled patches (shiny: real Normande
chestnut brindle)."""
from modelgen import Model, Cube, rgb
from bovine import (make_legs, coat, foam, hoof, add_eye, closed_lids, muzzle_fn, ear_fn, horn_fn, bovine_anims,
                    finalize, SIDES, bovine_poser)

SID, DEX = "meuhgousse", 1032

PAL = {
    "coat": rgb("#F3EEE2"), "patch": rgb("#3F93BE"), "brindle": rgb("#24618E"), "lunette": rgb("#3A86B4"),
    "hoof": rgb("#4F5966"), "hoof_dark": rgb("#2C323B"), "hoof_light": rgb("#6E7986"),
    "muzzle": rgb("#EDA7B0"), "muzzle_wet": rgb("#FBD9DD"), "nostril": rgb("#A85462"), "mouth": rgb("#C46A78"),
    "eye": rgb("#140F0D"), "eye_shine": rgb("#FFFFFF"), "eye_iris": rgb("#6A4024"), "eye_iris2": rgb("#B57A45"),
    "eye_white": rgb("#EEF2F5"), "lash": rgb("#121A26"), "eye_dark": rgb("#1A2433"),
    "ear_in": rgb("#F2B3BC"), "ear_in_light": rgb("#F8CDD3"), "horn": rgb("#EFE6CF"), "horn_tip": rgb("#CDBD98"),
    "foam": rgb("#DDF3FA"), "foam_shade": rgb("#A6DAEC"), "foam_light": rgb("#FFFFFF"), "foam_deep": rgb("#78C3DF"),
}
SHINY = dict(PAL, **{
    "patch": rgb("#94552A"), "brindle": rgb("#4E2B14"), "lunette": rgb("#8A4C24"), "eye_iris": rgb("#A8702A"), "eye_iris2": rgb("#E6B45E"),
    "foam": rgb("#FBF3E3"), "foam_shade": rgb("#EAD8B8"), "foam_light": rgb("#FFFFFF"), "foam_deep": rgb("#D4B98E"),
    "hoof": rgb("#5A4A3C"), "hoof_dark": rgb("#33281F"), "hoof_light": rgb("#7A6656"),
})

# ---------------------------------------------------------------- legs (calf: long, slim cannons, big hooves)
FRONT = dict(x=1.9, z=-5.0, L=(3, 5, 4), a=(22, -6, 0), th=2, thigh=(4, 4, 1), shin=(3, 3), meta=(2, 2), foot=(3, 3, 1.5))
BACK = dict(x=1.9, z=5.0, L=(4, 4, 4), a=(-18, 34, -4), th=2, thigh=(4, 5, 1), shin=(3, 3), meta=(2, 2), foot=(3, 3, 1.5))

# Normande patches in model space (rest pose): flanks, hindquarter, shoulder
BODY_PATCH = [(3.9, 14.0, 1.0, 2.0, 2.6, 3.4), (-3.9, 14.8, -4.5, 2.0, 2.4, 2.4), (-3.7, 13.4, 6.0, 1.8, 2.2, 2.0),
              (2.2, 16.2, 9.0, 1.8, 1.6, 1.2), (3.6, 15.5, -7.0, 1.6, 1.8, 1.6)]
LEG_PATCH = [(3.0, 12.2, 6.2, 1.6, 1.8, 1.8)]
BODY = coat(BODY_PATCH, seed=3)
LEGC = coat(BODY_PATCH + LEG_PATCH, seed=3)
FOAM = {"fn": foam, "shading": False}
LEG_PAINT = {"thigh": LEGC, "shin": LEGC, "meta": {"base": "coat"}, "foot": {"fn": hoof}}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 13.4, 0)

# head: modelled level in the neck's unrotated frame (poll at the neck's front-top), then pitched at the poll
HY, HZ = 17.5, -12.5
# big round calf eyes wrapping the front corners of the skull: 3x3 in front, 2x3 on the side
# big glossy calf eyes wrapping the front corners of the skull (rows top -> bottom, col 0 = outer corner):
# lash flick, then dark eye with a white catch-light, warm brown iris, a lighter glint and a touch of white
EYE = dict(x_edge=4.0, w=3, y0=HY - 4.0, h=4, z_face=HZ - 5.0, d=2, lash_row=2,
           front=["HD.",            # outer lash, rounded upper lid
                  "DSI",            # catch-light, warm brown iris
                  "DEI",            # pupil
                  ".JJ"],           # glossy lower iris
           side_rows=["..", "SI", "EI", "JJ"])
HEAD = coat([(0, HY + 0.6, HZ - 0.5, 2.8, 1.0, 1.6)],
            lunettes=[(sx * 3.0, HY - 2.0, HZ - 5.0, 2.0, 2.2, 1.6) for sx in (1, -1)], space="local", seed=8,
            extra=closed_lids(**EYE))

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 14, 1], cubes=[
        Cube([-3.5, 10.5, -3.5], [7, 7, 12], BODY),
        Cube([-2.5, 9.7, -2.5], [5, 1, 10], BODY),                                   # rounded belly
        Cube([-3, 12, 8.5], [6, 5, 1], BODY),                                        # rump / pin bones
        Cube([-1, 17.2, 7], [2, 1, 2], BODY),                                        # tailhead
        # foam fleece: a bubbly cape along the back
        Cube([-3, 17.5, -3], [6, 1, 5], FOAM), Cube([-2.5, 17.5, 2], [5, 1, 4], FOAM),
        Cube([-2.5, 18.5, -2.5], [3, 1, 3], FOAM), Cube([1, 18.5, -1.5], [2, 1, 2], FOAM),
        Cube([-2, 18.5, 2.5], [2, 1, 2], FOAM), Cube([0.5, 18.5, 3.5], [2, 1, 2], FOAM),
        Cube([3.2, 15.5, -2.5], [1, 2, 3], FOAM), Cube([-4.2, 15.5, 0.5], [1, 2, 3], FOAM)])
    m.bone("chest", "torso", [0, 14, -3.5], cubes=[
        Cube([-3.5, 10, -9.5], [7, 7, 6], BODY),
        Cube([-2.5, 9.2, -8.5], [5, 1, 5], BODY),                                    # brisket
        Cube([-3, 17, -8.5], [6, 1, 5], FOAM), Cube([-2, 18, -8], [4, 1, 3], FOAM), Cube([-1, 19, -7.5], [2, 1, 2], FOAM),
        Cube([3.2, 14.5, -8], [1, 2, 3], FOAM), Cube([-4.2, 14.5, -8], [1, 2, 3], FOAM)])
    m.bone("neck", "chest", [0, 15.5, -8], rotation=[-38, 0, 0], cubes=[
        Cube([-2, 13.5, -12.5], [4, 4, 5], BODY), Cube([-1.5, 17.5, -12], [3, 1, 4], FOAM)])  # neck
    m.bone("head", "neck", [0, HY - 0.5, HZ], rotation=[54, 0, 0], cubes=[
        Cube([-4, HY - 7, HZ - 5], [8, 7, 5], HEAD),                                  # skull, face = north
        Cube([-3, HY - 7, HZ - 7], [6, 3, 2], {"base": "muzzle", "fn": muzzle_fn()}),
        Cube([-1.5, HY, HZ - 3.5], [3, 1, 3], FOAM), Cube([-1, HY + 1, HZ - 3], [2, 1, 2], FOAM),     # forelock
        Cube([-1, HY - 0.5, HZ - 5.4], [2, 1, 1], FOAM)])
    m.bone("jaw", "head", [0, HY - 7, HZ - 3], cubes=[
        Cube([-2.5, HY - 8, HZ - 6.5], [5, 1, 4], {"base": "coat", "up": "mouth", "north": "muzzle"})])
    for side, sx in SIDES:
        m.bone(f"horn_{side}", "head", [2 * sx, HY, HZ - 2], cubes=[
            Cube([2 * sx - 0.5, HY, HZ - 2.5], [1, 1, 1], {"fn": horn_fn()})])
        add_eye(m, "head", side, sx, **EYE)
        eo = 4 if sx > 0 else -8
        m.bone(f"ear_{side}", "head", [4 * sx, HY - 1.5, HZ - 1], rotation=[0, 0, 35 * sx], cubes=[
            Cube([eo, HY - 2.5, HZ - 1.5], [4, 2, 1], {"base": "patch", "fn": ear_fn})])
    m.bone("tail", "torso", [0, 17.2, 8.5], rotation=[12, 0, 0], cubes=[
        Cube([-0.5, 11.2, 8], [1, 6, 1], {"base": "coat"})])
    m.bone("tail_tip", "tail", [0, 11.5, 8.5], cubes=[Cube([-1, 8.5, 7.5], [2, 3, 2], FOAM)])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=(),
                       walk_kw=dict(T=0.9, stride=7, lift=2.0, stance=0.66, bob=0.35, toe_off=20, fold=55, curl=30),
                       cry=dict(L=1.5, t_in=0.25, t_open=0.5, t_close=1.05, neck=-12, head=-18, jaw=12, tremble=1.6))
    return finalize(out)

def poser():
    return bovine_poser(SID, portrait=(1.49, [-0.53, 0.2, 0]), profile=(0.97, [-0.15, 0.28, 0]))
