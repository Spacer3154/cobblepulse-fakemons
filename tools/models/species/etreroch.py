# -*- coding: utf-8 -*-
"""#1035 Étreroch — oiseau des falaises de craie d'Étretat & silex, d'après le Grand Gravelot (Charadrius hiaticula).
Small, round and friendly: big head, short stubby orange bill tipped with flint, large dark eyes ringed in gold,
the plover's crisp pattern turned to stone — chalk-white forehead, throat, collar and belly, knapped-flint
fore-crown band, mask and breast band, chalk-grey back with fine strata, orange legs. Shiny: sunset-gold chalk."""
from modelgen import Model, Cube, rgb
from biped import Leg
from avian import (regions, flint, solid, gradient, feathers, folded_primaries, tail_fan, bird_lids, add_side_eyes,
                   eye_ring_rules,
                   bird_anims, bird_poser, SIDES)
from bovine import finalize

SID, DEX = "etreroch", 1035
FRAME_BONES = ("head", "jaw", "beak")

PAL = {
    "white": rgb("#F4F2EC"), "back": rgb("#B3A894"), "strata": rgb("#8E8577"),
    "flint": rgb("#2A2E38"), "flint_dark": rgb("#181B22"), "flint_light": rgb("#4A5263"), "flint_glint": rgb("#9FB3C8"),
    "beak": rgb("#F08A2C"), "beak_tip": rgb("#2A2E38"), "leg": rgb("#F0963A"), "claw": rgb("#2A2E38"),
    "eye": rgb("#1C1410"), "eye_shine": rgb("#FFFFFF"), "eye_ring": rgb("#E8B848"), "eye_iris": rgb("#4A2E1E"),
    "lid": rgb("#2A2E38"), "lash": rgb("#F6C840"),
    "covert": rgb("#B3A894"), "secondary": rgb("#8C8274"), "primary": rgb("#2E323C"), "primary_edge": rgb("#1C1F26"),
    "wing_bar": rgb("#F4F2EC"), "tail": rgb("#8C8274"), "tail_band": rgb("#2A2E38"), "tail_tip": rgb("#F4F2EC"),
    "arch_rim": rgb("#5E5A52"),
}
SHINY = dict(PAL, **{
    "white": rgb("#FFF1DA"), "back": rgb("#D6A15E"), "strata": rgb("#B07E44"), "covert": rgb("#D6A15E"),
    "secondary": rgb("#B07E44"), "tail": rgb("#B07E44"), "wing_bar": rgb("#FFF1DA"), "tail_tip": rgb("#FFF1DA"),
    "flint": rgb("#3A2A3A"), "flint_dark": rgb("#24182A"), "flint_light": rgb("#5E4660"), "flint_glint": rgb("#E6B8D8"),
    "primary": rgb("#3A2A3A"), "primary_edge": rgb("#24182A"), "lid": rgb("#3A2A3A"), "tail_band": rgb("#3A2A3A"),
    "eye_ring": rgb("#86D6F2"), "lash": rgb("#86D6F2"),
})

LEG_PAINT = {"thigh": {"base": "white"}, "shin": {"base": "white", "fn": gradient("white", "leg")},
             "meta": {"base": "leg"}, "foot": {"base": "leg"}, "claw": {"base": "leg"}}
LEGS = [Leg(side, 1.6 * sx, 0.5, (2, 3, 3), (-40, 35, -8), 1, thigh=(3, 3, 1), shin=(1, 1), meta=(1, 1),
            foot=(1, 2, 0.5), claws=(-1, 1), paints=LEG_PAINT, claw_len=2, dewclaw=False) for side, sx in SIDES]
H = LEGS[0].H                      # hip height ~7.95
D = -2.0                           # body block placed relative to the original layout
PIVOT = (0, 8, 0)

# ---------------------------------------------------------------- plumage pattern (rules in model space)
HX, HY0, HZ0 = 3.5, 13.0, -8.5                 # head box 7 x 6 x 6 (round, cute)
EYE = dict(x_edge=HX, y0=15.0, h=3, z0=-7.5, d=3)
def on(face, *fs):
    return face in fs
side = lambda f: on(f, "east", "west")
HEAD = regions([
    (lambda p, f: True, "back"),
    # front: black fore-crown band, white forehead, black lores running into the mask, white chin
    (lambda p, f: on(f, "north") and p[1] > 14.0, "white"),
    (lambda p, f: on(f, "north") and p[1] > 18.0, "flint"),
    (lambda p, f: on(f, "north") and 14.0 < p[1] < 16.5 and abs(p[0]) > 1.4, "flint"),
    (lambda p, f: on(f, "north") and 16.5 < p[1] < 18.0 and abs(p[0]) > 2.4, "flint"),
    (lambda p, f: on(f, "up") and p[2] < -7.5, "flint"),
    # sides: black mask through the eye, pale brow behind it, white chin and throat
    (lambda p, f: side(f) and 14.0 < p[1] < 18.0 and p[2] < -3.5, "flint"),
    (lambda p, f: side(f) and p[1] > 18.0 and p[2] > -6.5, "white"),
    (lambda p, f: side(f) and p[1] < 14.0, "white"),
    (lambda p, f: on(f, "down"), "white"),
    (lambda p, f: on(f, "south") and p[1] < 16, "white"),
] + eye_ring_rules(**EYE) + bird_lids(**EYE, lash_row=1), base="back", scallop=0.05)
CROWN = regions([(lambda p, f: p[2] < -6.5, "flint")], base="back")
CHEST = regions([(lambda p, f: 9.4 < p[1] < 11.6, "flint"), (lambda p, f: on(f, "up"), "back")], base="white")
BODY = regions([(lambda p, f: p[1] > 10.6 or on(f, "up"), "back"),
                (lambda p, f: p[2] < -2.5 and 9.4 < p[1] < 11.6 and not on(f, "up"), "flint")],      # breast band wraps
               base="white", scallop=0.07, strata=(("back",), 1.5))
WING = regions([], base="back", scallop=0.08, strata=(("back",), 1.5))
PRIM = {"fn": flint}

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    y = lambda v: v + D
    m.bone("torso", "body", [0, y(10), 0], cubes=[
        Cube([-3, y(9), -3.5], [6, 5, 8], BODY),
        Cube([-2, y(8), -2.5], [4, 1, 6], {"base": "white"}),                     # round belly
        Cube([-2, y(14), -2.5], [4, 1, 6], WING)])                                # round back
    m.bone("chest", "torso", [0, y(11.5), -3.5], cubes=[Cube([-2.5, y(9.5), -5.5], [5, 5, 2], CHEST)])
    m.bone("neck", "chest", [0, y(13.5), -4.5], cubes=[Cube([-2, y(13), -6], [4, 3, 2], {"base": "white"})])
    m.bone("head", "neck", [0, 14.5, -5], cubes=[
        Cube([-HX, HY0, HZ0], [7, 6, 6], HEAD),
        Cube([-3, HY0 + 6, HZ0 + 1], [6, 1, 4], CROWN),                          # rounded crown
        Cube([-3, HY0 - 1, HZ0 + 1], [6, 1, 4], {"base": "white"})])             # round throat
    m.bone("beak", "head", [0, 15, -8.5], cubes=[
        Cube([-1, 14.5, -10.5], [2, 1, 2], {"base": "beak"}),
        Cube([-0.5, 14.5, -11.5], [1, 1, 1], {"fn": flint})])
    m.bone("jaw", "head", [0, 14.5, -8.5], cubes=[Cube([-1, 13.5, -10.5], [2, 1, 2], {"base": "beak"})])
    add_side_eyes(m, "head", **EYE, rows=["SEE", "EEE", "EEI"])
    for side_, sx in SIDES:
        x0 = 3 if sx > 0 else -4
        m.bone(f"wing_closed_{side_}", "torso", [3.5 * sx, y(14), -3], cubes=[
            Cube([x0, y(10.5), -3], [1, 4, 7], WING),
            Cube([x0, y(11), 4], [1, 2, 4], PRIM)])                               # dark primaries over the tail
        r0 = 3 if sx > 0 else -9
        m.bone(f"wing_open_{side_}", "torso", [3 * sx, y(13.5), -1.5], cubes=[
            Cube([r0, y(13), -2], [6, 1, 1], {"base": "covert"}),
            Cube([r0, y(13.5), -1], [6, 0, 4], feathers(root_x=3 * sx, tip_x=15 * sx, lead_z=-1, chord=4.5))])
        h0 = 9 if sx > 0 else -15
        m.bone(f"wing_open_{side_}2", f"wing_open_{side_}", [9 * sx, y(13.5), -1.5], cubes=[
            Cube([h0, y(13), -2], [6, 1, 1], {"base": "primary"}),
            Cube([h0, y(13.5), -1], [6, 0, 5], feathers(root_x=3 * sx, tip_x=15 * sx, lead_z=-1, chord=5.5))])
    m.bone("tail", "torso", [0, y(12.5), 4.5], rotation=[-8, 0, 0], cubes=[Cube([-1.5, y(12), 4.5], [3, 1, 4], {"fn": tail_fan()})])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    out = bird_anims(SID, m, LEGS, pivot=PIVOT,
                     walk_kw=dict(T=0.42, stride=3.2, lift=1.6, stance=0.55, bob=0.22, toe_off=18, fold=20, curl=8,
                                  torso=(0.8, 2.0, 2.0)),
                     cfg=dict(scale=0.6, flap_T=0.28, flap_amp=60, fly_T=0.34, head_bob=1.5,
                              cry=dict(L=1.1, calls=((0.2, 0.42), (0.55, 0.85)), neck=-10, head=-18, beak=26, wings=8),
                              battle=dict(theta=6, dy=-0.5, neck=10, head=-6, wings=14, tail=-15)))
    return finalize(out)

def poser():
    return bird_poser(SID, portrait=(2.0, [-0.4, -0.6, 0]), profile=(1.0, [0, 0.24, 0]))
