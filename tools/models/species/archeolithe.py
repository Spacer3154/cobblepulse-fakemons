# -*- coding: utf-8 -*-
"""#1036 Archéolithe — arches naturelles des falaises d'Étretat & pierre sculptée (Grand Gravelot, stade 2).
A taller, sleeker, serious plover carved from the cliff: longer legs and neck, a longer flint-tipped bill, narrowed
eyes under carved flint brows, a two-plate flint crest, the plover bands turned to bold flint courses, and chalk
plumage layered with flint seams like the cliff face. Its wings are 'sculpted into natural arches': a carved arch
on the folded wing, and an open arch right through each spread wing (the Porte d'Aval) that the sea wind passes
through. Shiny: sunset-gold chalk."""
from modelgen import Model, Cube, rgb
from biped import Leg
from avian import (regions, flint, gradient, feathers, tail_fan, bird_lids, add_side_eyes, eye_ring_rules,
                   bird_anims, bird_poser, SIDES)
from bovine import finalize

SID, DEX = "archeolithe", 1036
FRAME_BONES = ("head", "jaw", "beak")

PAL = {
    "white": rgb("#EEEAE0"), "back": rgb("#C7BFAE"), "strata": rgb("#5A5E68"),
    "flint": rgb("#2A2E38"), "flint_dark": rgb("#171A21"), "flint_light": rgb("#4C5466"), "flint_glint": rgb("#A8BCD2"),
    "beak": rgb("#E07A2A"), "leg": rgb("#E88838"), "claw": rgb("#2A2E38"),
    "eye": rgb("#1A1210"), "eye_shine": rgb("#F2EEE6"), "eye_ring": rgb("#C98A3A"), "eye_iris": rgb("#3A2418"),
    "eye_dark": rgb("#2A2E38"), "lid": rgb("#2A2E38"), "lash": rgb("#C98A3A"),
    "covert": rgb("#C7BFAE"), "secondary": rgb("#9A9282"), "primary": rgb("#2E323C"), "primary_edge": rgb("#1C1F26"),
    "wing_bar": rgb("#EEEAE0"), "tail": rgb("#9A9282"), "tail_band": rgb("#2A2E38"), "tail_tip": rgb("#EEEAE0"),
    "arch_rim": rgb("#8E887A"), "arch": rgb("#5E5A52"),
}
SHINY = dict(PAL, **{
    "white": rgb("#FFF0D6"), "back": rgb("#D9A35C"), "strata": rgb("#7A4E2E"), "covert": rgb("#D9A35C"),
    "secondary": rgb("#B37C42"), "tail": rgb("#B37C42"), "wing_bar": rgb("#FFF0D6"), "tail_tip": rgb("#FFF0D6"),
    "flint": rgb("#3A2A3A"), "flint_dark": rgb("#24182A"), "flint_light": rgb("#5E4660"), "flint_glint": rgb("#E6B8D8"),
    "primary": rgb("#3A2A3A"), "primary_edge": rgb("#24182A"), "lid": rgb("#3A2A3A"), "tail_band": rgb("#3A2A3A"),
    "eye_dark": rgb("#3A2A3A"), "eye_ring": rgb("#7FD0EE"), "lash": rgb("#7FD0EE"), "arch": rgb("#5A3A2E"),
    "arch_rim": rgb("#9A6A40"),
})

LEG_PAINT = {"thigh": {"base": "white"}, "shin": {"base": "white", "fn": gradient("white", "leg")},
             "meta": {"base": "leg"}, "foot": {"base": "leg"}, "claw": {"base": "leg"}}
LEGS = [Leg(side, 2.2 * sx, 1.0, (3, 5, 5), (-40, 35, -8), 1, thigh=(4, 4, 1), shin=(2, 2), meta=(1, 1),
            foot=(1, 3, 0.5), claws=(-1, 1), paints=LEG_PAINT, claw_len=3, dewclaw=False) for side, sx in SIDES]
PIVOT = (0, 12.5, 0)

def on(face, *fs):
    return face in fs
side = lambda f: on(f, "east", "west")
EYE = dict(x_edge=3.0, y0=22.5, h=2, z0=-10.5, d=3)
HEAD = regions([
    (lambda p, f: on(f, "north") and p[1] > 21.0, "white"),
    (lambda p, f: on(f, "north") and p[1] > 24.0, "flint"),                          # fore-crown band
    (lambda p, f: on(f, "north") and 21.0 < p[1] < 23.5 and abs(p[0]) > 1.4, "flint"),
    (lambda p, f: on(f, "north") and p[1] <= 21.0, "white"),
    (lambda p, f: on(f, "up") and p[2] < -10.0, "flint"),
    (lambda p, f: side(f) and 21.0 < p[1] < 25.0 and p[2] < -6.0, "flint"),          # mask
    (lambda p, f: side(f) and p[1] > 25.0 and p[2] > -9.0, "white"),                 # pale brow streak
    (lambda p, f: side(f) and p[1] < 21.0, "white"),
    (lambda p, f: on(f, "down"), "white"),
    (lambda p, f: on(f, "south") and p[1] < 23, "white"),
] + eye_ring_rules(**EYE, sides_only=True) + bird_lids(**EYE, lash_row=1), base="back", scallop=0.05)
CROWN = regions([(lambda p, f: p[2] < -9.5, "flint")], base="back")
CHEST = regions([(lambda p, f: 14.6 < p[1] < 17.6, "flint"), (lambda p, f: on(f, "up"), "back")], base="white",
                strata=(("white",), 3.0))
BODY = regions([(lambda p, f: p[1] > 15.6 or on(f, "up"), "back"),
                (lambda p, f: p[2] < -3.5 and 14.6 < p[1] < 17.6 and not on(f, "up"), "flint")],
               base="white", scallop=0.06, strata=(("back",), 2.0))

def carved_arch(zc, y_base, rw, rh):
    """dark carved arch on the folded wing (sides), opening at its lower edge"""
    def inside(p, f, k=1.0):
        return side(f) and p[1] > y_base and ((p[2] - zc) / (rw * k)) ** 2 + ((p[1] - y_base) / (rh * k)) ** 2 < 1
    return [(lambda p, f: inside(p, f, 1.35), "arch_rim"), (lambda p, f: inside(p, f), "arch")]
WING = regions(carved_arch(1.5, 13.5, 1.8, 2.6), base="back", scallop=0.07, strata=(("back",), 2.0))

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 13, 1], cubes=[
        Cube([-4, 12, -4.5], [8, 6, 11], BODY),
        Cube([-3, 11, -3.5], [6, 1, 9], {"base": "white"}),
        Cube([-3, 18, -3.5], [6, 1, 9], BODY)])
    m.bone("chest", "torso", [0, 15, -4.5], cubes=[Cube([-3, 12, -7], [6, 6, 3], CHEST)])
    m.bone("neck", "chest", [0, 17, -6], cubes=[Cube([-2, 16, -7.5], [4, 5, 3], {"base": "white"})])
    m.bone("head", "neck", [0, 21, -6], cubes=[
        Cube([-3, 20, -11], [6, 6, 7], HEAD),
        Cube([-2, 26, -10], [4, 1, 5], CROWN),
        Cube([-2, 19, -10], [4, 1, 5], {"base": "white"}),
        Cube([2.6, 24.5, -11], [1, 1, 4], {"fn": flint}), Cube([-3.6, 24.5, -11], [1, 1, 4], {"fn": flint})])  # carved brows
    m.bone("crest", "head", [0, 26, -5], rotation=[-42, 0, 0], cubes=[
        Cube([-0.5, 26, -6], [1, 3, 3], {"fn": flint}), Cube([-0.5, 28.5, -5], [1, 2, 2], {"fn": flint})])
    m.bone("beak", "head", [0, 22.5, -11], cubes=[
        Cube([-1, 22, -14], [2, 1, 3], {"fn": gradient("beak", "flint", axis="x")}),
        Cube([-0.5, 22, -16], [1, 1, 2], {"fn": flint}),
        Cube([-0.5, 21.4, -16], [1, 1, 1], {"fn": flint})])                       # small hook
    m.bone("jaw", "head", [0, 22, -11], cubes=[Cube([-1, 21, -14], [2, 1, 3], {"base": "beak"})])
    add_side_eyes(m, "head", **EYE, rows=["DDD", "SEI"])
    for side_, sx in SIDES:
        x0 = 4 if sx > 0 else -5
        m.bone(f"wing_closed_{side_}", "torso", [4.5 * sx, 18.5, -4], cubes=[
            Cube([x0, 13.5, -4], [1, 5, 10], WING),
            Cube([x0, 14, 6], [1, 3, 5], {"fn": flint})])
        r0 = 4 if sx > 0 else -13
        m.bone(f"wing_open_{side_}", "torso", [4 * sx, 17.5, -3], cubes=[
            Cube([r0, 17, -4], [9, 1, 1], {"base": "covert"}),
            Cube([r0, 17.5, -3], [9, 0, 7], feathers(root_x=4 * sx, tip_x=22 * sx, lead_z=-3, chord=7.2,
                                                    arch=(0.27, 2.6, 4.0)))])
        h0 = 13 if sx > 0 else -22
        m.bone(f"wing_open_{side_}2", f"wing_open_{side_}", [13 * sx, 17.5, -3], cubes=[
            Cube([h0, 17, -4], [9, 1, 1], {"fn": flint}),
            Cube([h0, 17.5, -3], [9, 0, 8], feathers(root_x=4 * sx, tip_x=22 * sx, lead_z=-3, chord=8.2))])
    m.bone("tail", "torso", [0, 16.5, 6.5], rotation=[-6, 0, 0], cubes=[Cube([-2, 16, 6.5], [4, 1, 6], {"fn": tail_fan()})])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    out = bird_anims(SID, m, LEGS, pivot=PIVOT,
                     walk_kw=dict(T=0.62, stride=5.5, lift=2.2, stance=0.58, bob=0.3, toe_off=18, fold=22, curl=8,
                                  torso=(0.8, 2.0, 2.0)),
                     cfg=dict(scale=0.9, flap_T=0.42, flap_amp=50, fly_T=0.55, head_bob=1.2, tilt=0.4, idle_bob=0.7,
                              cry=dict(L=1.4, calls=((0.3, 0.75),), neck=-16, head=-20, beak=24, wings=12),
                              battle=dict(theta=5, dy=-0.8, neck=14, head=-10, wings=16, tail=-12)))
    return finalize(out)

def poser():
    return bird_poser(SID, portrait=(1.5, [-0.4, 0.4, 0]), profile=(0.8, [0, 0.54, 0]))
