# -*- coding: utf-8 -*-
"""#1037 Gargoylbâtre — gargouille des falaises de la Côte d'Albâtre & rapace (Grand Gravelot, stade final).
A menacing cliff gargoyle: hunched raptor posture, broad chest under a cracked flint breast-plate (the plover's
breast band), thick feathered-stone legs with flint talons, head thrust forward under a heavy flint brow, a hooked
beak sharp as knapped flint, embers glowing in its eyes within the black plover mask, two flint horns swept back
like the Aiguille d'Étretat, a tail ending in a flint needle, weathered chalk plumage with flint seams, cracks,
lichen and moss. Its great wings carry a natural arch through each spread wing and a claw at each wrist.
Rideable: one rider on the saddle of its back; flies (cobblemon:air/bird) and walks (cobblemon:land/horse).
Shiny: sunset-gold chalk with cold blue embers."""
from modelgen import Model, Cube, rgb
from biped import Leg
from avian import (regions, flint, gradient, feathers, tail_fan, bird_lids, add_side_eyes, eye_ring_rules,
                   bird_anims, bird_poser, SIDES)
from bovine import finalize, vnoise

SID, DEX = "gargoylbatre", 1037
FRAME_BONES = ("head", "jaw", "beak")
SCALE_BOOST = 1.2                    # mounts are shown a bit larger than their Pokédex height (as Cobblemon does)
HEIGHT_SKIP = ("horn",)              # 1.6 m to the top of the head; the flint horns rise above it

PAL = {
    "white": rgb("#E6E1D4"), "back": rgb("#B3AA97"), "strata": rgb("#4C505A"), "crack": rgb("#5C574E"),
    "lichen": rgb("#C2B84A"), "moss": rgb("#6E8A3A"),
    "flint": rgb("#262A33"), "flint_dark": rgb("#14171D"), "flint_light": rgb("#46505F"), "flint_glint": rgb("#A8BCD2"),
    "beak": rgb("#C8692A"), "scale": rgb("#B87232"), "claw": rgb("#262A33"),
    "eye": rgb("#1A0A04"), "eye_hot": rgb("#FFE07A"), "eye_ring": rgb("#FF7A2A"), "eye_shine": rgb("#FFF6D0"),
    "lid": rgb("#262A33"), "lash": rgb("#7A2A10"), "eye_dark": rgb("#14171D"),
    "covert": rgb("#B3AA97"), "secondary": rgb("#8E8676"), "primary": rgb("#262A33"), "primary_edge": rgb("#14171D"),
    "wing_bar": rgb("#E6E1D4"), "tail": rgb("#8E8676"), "tail_band": rgb("#262A33"), "tail_tip": rgb("#E6E1D4"),
    "arch_rim": rgb("#6E685C"), "arch": rgb("#3A3A40"),
}
SHINY = dict(PAL, **{
    "white": rgb("#FFF0D6"), "back": rgb("#D3A05C"), "strata": rgb("#6E4628"), "crack": rgb("#8A5A30"),
    "covert": rgb("#D3A05C"), "secondary": rgb("#B07A42"), "tail": rgb("#B07A42"), "wing_bar": rgb("#FFF0D6"),
    "tail_tip": rgb("#FFF0D6"), "lichen": rgb("#E0D070"),
    "flint": rgb("#3A2A3A"), "flint_dark": rgb("#24182A"), "flint_light": rgb("#5E4660"), "flint_glint": rgb("#E6B8D8"),
    "primary": rgb("#3A2A3A"), "primary_edge": rgb("#24182A"), "lid": rgb("#3A2A3A"), "tail_band": rgb("#3A2A3A"),
    "claw": rgb("#3A2A3A"), "eye_dark": rgb("#24182A"), "eye_hot": rgb("#D8FAFF"), "eye_ring": rgb("#4AC8FF"), "lash": rgb("#1A5A8A"),
    "arch": rgb("#5A3A2E"), "arch_rim": rgb("#9A6A40"),
})

def weathered(p, f, key):
    """lichen / moss patches and cracks on the upper stone plumage"""
    if key != "back":
        return key
    n = vnoise(p[0] * 0.45 + 11, p[1] * 0.45, p[2] * 0.45, 31)
    if n > 0.74:
        return "lichen" if vnoise(p[0] * 1.3, p[1] * 1.3, p[2] * 1.3, 5) > 0.45 else "moss"
    c = vnoise(p[0] * 0.9 + 3, p[1] * 0.25, p[2] * 0.9, 77)
    if 0.49 < c < 0.52:
        return "crack"
    return key

LEG_PAINT = {"thigh": {"base": "back"}, "shin": {"base": "back", "fn": gradient("back", "white")},
             "meta": {"base": "scale"}, "foot": {"base": "scale"}, "claw": {"fn": flint}}
LEGS = [Leg(side, 3.6 * sx, 2.5, (5, 6, 4), (-50, 45, -15), 2, thigh=(6, 6, 2), shin=(4, 5), meta=(3, 3),
            foot=(4, 5, 1), claws=(-1.5, 0, 1.5), paints=LEG_PAINT, claw_len=3, dewclaw=True) for side, sx in SIDES]
PIVOT = (0, round(LEGS[0].H, 2), 0)

def on(face, *fs):
    return face in fs
side = lambda f: on(f, "east", "west")
EYE = dict(x_edge=4.0, y0=21.5, h=2, z0=-20.5, d=3)
HEAD = regions([
    (lambda p, f: on(f, "north") and p[1] > 21.0, "white"),                          # white forehead
    (lambda p, f: on(f, "north") and p[1] > 24.0, "flint"),                          # fore-crown band
    (lambda p, f: on(f, "north") and 20.0 < p[1] < 23.5 and abs(p[0]) > 1.5, "flint"),
    (lambda p, f: on(f, "up") and p[2] < -19.0, "flint"),
    (lambda p, f: side(f) and 20.0 < p[1] < 24.5 and p[2] < -16.0, "flint"),         # black mask
    (lambda p, f: side(f) and p[1] > 24.0 and p[2] > -18.5, "white"),                # pale brow streak
    (lambda p, f: side(f) and p[1] < 20.0, "white"),
    (lambda p, f: on(f, "down"), "white"),
    (lambda p, f: on(f, "north") and p[1] <= 20.0, "white"),
    (lambda p, f: on(f, "south") and p[1] < 22, "white"),
] + eye_ring_rules(**EYE, sides_only=True) + [
    (lambda p, f: side(f) and 23.4 <= p[1] <= 24.7 and -21.6 < p[2] < -16.4, "flint"),   # no ring under the brow
] + bird_lids(**EYE, lash_row=1), base="back", scallop=0.05)
CHEST = regions([(lambda p, f: 15.5 < p[1] < 19.5 and not on(f, "up"), "flint"), (lambda p, f: on(f, "up"), "back"),
                 (lambda p, f: on(f, "north") and 15.5 < p[1] < 19.5 and (p[0] * 0.8 + p[1] * 0.6) % 3.1 < 0.45, "flint_light")],
                base="white", strata=(("white",), 3.0))
BODY = regions([(lambda p, f: p[1] > 17.0 or on(f, "up"), "back"),
                (lambda p, f: p[2] < -3.0 and 15.5 < p[1] < 19.5 and not on(f, "up"), "flint")],
               base="white", scallop=0.06, strata=(("back",), 2.2))

def with_weather(paint):
    fn = paint["fn3"]
    def fn3(px, faces, pal, rnd, c):
        fn(px, faces, pal, rnd, c)
        from bovine import put, light
        for face, X, Y, p in c.texels():
            k = weathered(p, face, "back")
            if k != "back":
                cur = px[X, Y]
                if abs(cur[0] - pal["back"][0]) < 40 and abs(cur[2] - pal["back"][2]) < 40:
                    fx, fy, fw, fh = faces[face]
                    put(px, X, Y, pal[k], light(face, Y - fy, fh), rnd, 4)
    return {"fn3": fn3}

def carved_arch(zc, y_base, rw, rh):
    def inside(p, f, k=1.0):
        return side(f) and p[1] > y_base and ((p[2] - zc) / (rw * k)) ** 2 + ((p[1] - y_base) / (rh * k)) ** 2 < 1
    return [(lambda p, f: inside(p, f, 1.3), "arch_rim"), (lambda p, f: inside(p, f), "arch")]
WING = with_weather(regions(carved_arch(3.0, 11.0, 2.4, 4.0), base="back", scallop=0.07, strata=(("back",), 2.2)))
BODYW = with_weather(BODY)
NECK = with_weather(regions([(lambda p, f: on(f, "down", "north") or p[1] < 20.5, "white")], base="back", scallop=0.06))
TAIL = with_weather(regions([(lambda p, f: on(f, "down"), "white")], base="back", strata=(("back",), 2.2)))

def build():
    m = Model(SID, DEX, (256, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 15, 2], rotation=[-10, 0, 0], cubes=[
        Cube([-6, 11, -5], [12, 10, 14], BODYW),
        Cube([-5, 10, -3.5], [10, 1, 11], {"base": "white"}),
        Cube([-5, 21, -4], [10, 1, 12], BODYW)])                                   # saddle of the back
    m.bone("locator_seat_1", "torso", [0, 22, 4], locators={"seat_1": [0, 22, 4]})
    m.bone("chest", "torso", [0, 16, -5], rotation=[-18, 0, 0], cubes=[Cube([-6, 11, -10], [12, 12, 5], CHEST)])
    m.bone("neck", "chest", [0, 21, -8], rotation=[28, 0, 0], cubes=[Cube([-4, 18, -14], [8, 7, 7], NECK)])
    m.bone("head", "neck", [0, 22, -14], cubes=[
        Cube([-4, 18.5, -21], [8, 7, 7], HEAD),
        Cube([-3, 25.5, -20], [6, 1, 5], {"base": "back"}),
        Cube([-2.5, 24, -21.5], [5, 1, 3], {"fn": flint}),                      # flint brow ridge
        Cube([-3, 17.5, -20], [6, 1, 5], {"base": "white"})])
    m.bone("beak", "head", [0, 21, -21], cubes=[
        Cube([-2, 19, -23], [4, 3, 2], {"base": "beak"}),                        # cere
        Cube([-1.5, 19, -25], [3, 3, 2], {"fn": gradient("beak", "flint", axis="x")}),
        Cube([-1, 17, -26], [2, 4, 1], {"fn": flint})])                      # hooked flint tip
    m.bone("jaw", "head", [0, 19.5, -21], cubes=[Cube([-1.5, 18, -25], [3, 1, 4], {"fn": gradient("beak", "flint", axis="x")})])
    add_side_eyes(m, "head", **EYE, rows=["DRR", "AEA"], glow=True)
    for side_, sx in SIDES:                                                      # brows slanting down to the beak
        bx = 2.5 if sx > 0 else -4.5
        m.bone(f"brow_{side_}", "head", [3.5 * sx, 24, -15.5], rotation=[9, 0, 0], cubes=[
            Cube([bx, 23.5, -21.5], [2, 1, 6], {"fn": flint})])
    for side_, sx in SIDES:
        hx = 2 if sx > 0 else -4
        m.bone(f"horn_{side_}", "head", [3 * sx, 25.5, -16], rotation=[18, -15 * sx, 0], cubes=[
            Cube([hx, 25, -16], [2, 2, 6], {"fn": flint})])
        tx_ = 2.5 if sx > 0 else -3.5
        m.bone(f"horn2_{side_}", f"horn_{side_}", [3 * sx, 26, -10], rotation=[10, 0, 0], cubes=[
            Cube([tx_, 25.5, -10], [1, 1, 4], {"fn": flint})])
        x0 = 6 if sx > 0 else -8
        m.bone(f"wing_closed_{side_}", "torso", [7 * sx, 21, -4], rotation=[-8, 0, 0], cubes=[
            Cube([x0, 11, -5], [2, 12, 13], WING),
            Cube([x0, 21, -6], [2, 5, 4], {"base": "back"}),                     # wrist hump above the back
            Cube([x0 + 0.5, 26, -6.5], [1, 2, 1], {"fn": flint}),                # wrist claw
            Cube([x0 + 0.5, 12, 8], [1, 8, 9], {"fn": flint})])                  # flint primaries
        r0 = 6 if sx > 0 else -20
        m.bone(f"wing_open_{side_}", "torso", [6 * sx, 21, -3], cubes=[
            Cube([r0, 20, -4], [14, 2, 2], {"base": "covert"}),
            Cube([r0, 21, -2], [14, 0, 11], feathers(root_x=6 * sx, tip_x=32 * sx, lead_z=-2, chord=11,
                                                     arch=(0.24, 3.2, 6.0)))])
        h0 = 20 if sx > 0 else -32
        m.bone(f"wing_open_{side_}2", f"wing_open_{side_}", [20 * sx, 21, -3], cubes=[
            Cube([h0, 20, -4], [12, 2, 2], {"fn": flint}),
            Cube([19.5 if sx > 0 else -20.5, 22, -3.5], [1, 3, 1], {"fn": flint}),    # wrist claw
            Cube([h0, 21, -2], [12, 0, 12], feathers(root_x=6 * sx, tip_x=32 * sx, lead_z=-2, chord=12,
                                                     primary_from=0.5))])
    m.bone("tail", "torso", [0, 18, 9], rotation=[-12, 0, 0], cubes=[Cube([-3, 16.5, 9], [6, 3, 7], TAIL)])
    m.bone("tail2", "tail", [0, 18, 16], rotation=[-6, 0, 0], cubes=[
        Cube([-1, 17, 16], [2, 2, 4], {"fn": flint}), Cube([-0.5, 17.5, 20], [1, 1, 4], {"fn": flint})])  # flint needle
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    out = bird_anims(SID, m, LEGS, pivot=PIVOT,
                     walk_kw=dict(T=0.95, stride=8, lift=3.0, stance=0.6, bob=0.6, toe_off=15, fold=20, curl=6,
                                  torso=(1.2, 3.0, 3.0)),
                     cfg=dict(scale=1.4, flap_T=0.7, flap_amp=42, fly_T=0.9, head_bob=1.0, tilt=0.2, idle_bob=0.4,
                              tail=("tail", "tail2"), menace=True, ride=True, ride_dy=-1.2, sleep_theta=6, sleep_style="statue",
                              tuck=(-25, 105, 150, 60), tuck_fly=(5, 120, 175, 80), hover_pitch=-18,
                              cry=dict(L=2.0, calls=((0.35, 1.5),), neck=6, head=-14, beak=34, wings=26,
                                       theta=4, tail=-10),                     # lunging screech, wings flared
                              battle=dict(theta=8, dy=-1.4, neck=16, head=-18, wings=18, tail=-8)))
    return finalize(out)

def poser():
    return bird_poser(SID, portrait=(1.2, [-0.6, 1.0, 0]), profile=(0.6, [0, 0.84, 0]), ride=True, menace=True)
