# -*- coding: utf-8 -*-
"""#1034 Normanguer — vache Normande sacrée, protectrice du bocage & lait féerique (Eau / Fée).
A tall, noble Normande cow: long elegant legs, deep body, level topline, long neck held high, refined head with
large gentle eyes (lash line, aqua glints) in the breed's lunettes, and lyre-shaped horns whose tips are glowing
mother-of-pearl. A crest of sea waves runs down the neck to the withers; a crown of apple blossom sits between the
horns; a nacre bell hangs from a leather collar; a forehead pearl marks it as sacred; the udder is pearly pink
(its healing milk). Sea-blue brindled patches (shiny: chestnut brindle, golden nacre)."""
import math
from modelgen import Model, Cube, rgb, mix, shade, fill, FACE_LIGHT
from bovine import (make_legs, coat, foam, hoof, add_eye, closed_lids, muzzle_fn, ear_fn, solid, put, bovine_anims, finalize,
                    SIDES, bovine_poser)

SID, DEX = "normanguer", 1034

PAL = {
    "coat": rgb("#F7F4EE"), "patch": rgb("#5B9DCA"), "brindle": rgb("#3A70A0"), "lunette": rgb("#3F72A4"),
    "hoof": rgb("#8D8F9A"), "hoof_dark": rgb("#5A5C66"), "hoof_light": rgb("#B5B7C2"),
    "muzzle": rgb("#F1B7BF"), "muzzle_wet": rgb("#FCDDE1"), "nostril": rgb("#B66A78"), "mouth": rgb("#CF7F8C"),
    "eye": rgb("#24153A"), "eye_shine": rgb("#FFFFFF"), "eye_iris": rgb("#8A58B8"), "eye_iris2": rgb("#E2B6F2"),
    "eye_white": rgb("#F6F2FA"), "lash": rgb("#1C1424"), "eye_dark": rgb("#2B2140"),
    "ear_in": rgb("#F4BCC6"), "ear_in_light": rgb("#FAD3DA"),
    "horn": rgb("#F3ECDD"), "horn_mid": rgb("#E4D8C0"),
    "nacre": rgb("#FFF6FB"), "nacre_pink": rgb("#F6C3DC"), "nacre_blue": rgb("#B9E6F6"),
    "leather": rgb("#7A4B2C"), "leather_dark": rgb("#4E2F1A"), "brass": rgb("#D9B25A"),
    "petal": rgb("#FFF4F7"), "petal_pink": rgb("#F4B3C8"), "pistil": rgb("#F2D35C"),
    "leaf": rgb("#5E8F3A"), "leaf_dark": rgb("#3F6A28"),
    "udder": rgb("#F6C4CE"), "teat": rgb("#E9A2B1"),
    "wave": rgb("#4A97CD"), "wave_light": rgb("#8CCBEA"), "foam": rgb("#E9F8FD"), "foam_shade": rgb("#B4E0F0"),
    "foam_light": rgb("#FFFFFF"), "foam_deep": rgb("#7CC2E0"),
}
SHINY = dict(PAL, **{
    "patch": rgb("#8E4E25"), "brindle": rgb("#4B2913"), "lunette": rgb("#7A421E"), "eye_iris": rgb("#C8923A"), "eye_iris2": rgb("#F2D08A"),
    "nacre": rgb("#FFF8E6"), "nacre_pink": rgb("#F8D6A6"), "nacre_blue": rgb("#FFE7B0"),
    "wave": rgb("#B98A4C"), "wave_light": rgb("#E6C688"), "foam": rgb("#FFF6E4"), "foam_shade": rgb("#EBD7B2"),
    "foam_deep": rgb("#D2B27C"), "leather": rgb("#5B3A26"), "brass": rgb("#F0CF6A"),
})

# ---------------------------------------------------------------- painters
def nacre(px, faces, pal, rnd):
    """Mother-of-pearl: shifting pink / white / sky-blue sheen with bright glints (different on every emissive
    frame, so it shimmers in game)."""
    keys = ("nacre", "nacre_pink", "nacre_blue")
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                t = (i + j * 0.7 + rnd.random() * 1.6) / 2.2
                a, b = keys[int(t) % 3], keys[(int(t) + 1) % 3]
                c = mix(pal[a], pal[b], t - int(t))
                if rnd.random() < 0.12:
                    c = (255, 255, 255, 255)
                px[x + i, y + j] = c

def wave_crest(period=5, curl=True):
    """Stylised breaking waves on a plane (crest running along Z): deep blue base, lighter water, white foam lip
    curling forward, transparent above the crest line."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h) or fc in ("up", "down", "north", "south"):
                continue
            for i in range(w):
                ph = (i % period) / period
                top = h * (0.45 + 0.55 * (1 - ph) ** 1.2)            # each wave rises then breaks
                for j in range(h):
                    r = h - j                                       # height above the base
                    if r > top + 0.5:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    if r > top - 0.8:
                        c = pal["foam_light"] if rnd.random() < 0.5 else pal["foam"]
                    elif r > top - 1.8:
                        c = pal["wave_light"]
                    else:
                        c = pal["wave"] if (i + j) % 4 else pal["wave_light"]
                    px[x + i, y + j] = c
    return fn

def blossom(px, faces, pal, rnd):
    """Apple-blossom garland: five-petal white / pink flowers with a yellow heart, set in leaves."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                px[x + i, y + j] = shade(pal["leaf"] if (i + j) % 3 else pal["leaf_dark"], FACE_LIGHT[fc])
        for i in range(1, w, 3):
            for j in range(0, h, 2):
                cx = x + min(w - 1, i + (j % 4) // 2)
                cy = y + j
                px[cx, cy] = pal["pistil"]
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = cx + dx, cy + dy
                    if x <= X < x + w and y <= Y < y + h:
                        px[X, Y] = pal["petal_pink"] if rnd.random() < 0.35 else pal["petal"]

def flower(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["petal"], 1.0, rnd, 3)
        if w and h:
            px[x + w // 2, y + h // 2] = pal["pistil"] if fc in ("up", "north") else pal["petal_pink"]

def leather(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        fill(px, x, y, w, h, pal["leather"], FACE_LIGHT[fc], rnd, 4)
        if fc in ("north", "south", "east", "west") and h >= 3:
            for i in range(0, w, 2):
                px[x + i, y + 1] = pal["leather_dark"]
                px[x + i, y + h - 2] = pal["leather_dark"]

def udder_fn(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                c = pal["udder"]
                if rnd.random() < 0.1:
                    c = mix(c, pal["nacre"], 0.6)                  # pearly sheen
                put(px, x + i, y + j, c, FACE_LIGHT[fc], rnd, 3)

# ---------------------------------------------------------------- legs: long and elegant
FRONT = dict(x=3.4, z=-9.0, L=(6, 8, 6), a=(22, -6, 0), th=2, thigh=(5, 6, 2), shin=(4, 4), meta=(3, 3), foot=(4, 4, 2))
BACK = dict(x=3.4, z=9.0, L=(7, 7, 6), a=(-18, 32, -4), th=2, thigh=(5, 7, 2), shin=(4, 5), meta=(3, 3), foot=(4, 4, 2))

PATCH = [(6.6, 21.5, 1.5, 2.6, 4.6, 5.2), (-6.6, 22.0, -5.0, 2.6, 4.0, 4.4), (-6.3, 20.5, 8.0, 2.4, 3.8, 3.4),
         (6.6, 22.5, -11.0, 2.4, 3.6, 3.0), (2.0, 27.0, 10.5, 3.0, 1.6, 2.0), (0.0, 28.6, -10.0, 3.6, 1.2, 3.0),
         (5.0, 18.0, 9.0, 2.0, 3.2, 3.0)]
BODY = coat(PATCH, seed=6, warp=1.3, streak=0.58)
LEGC = coat(PATCH, seed=6, warp=1.3, streak=0.58)
NACRE = {"fn": nacre, "glow": True, "shading": False}
FOAM = {"fn": foam, "shading": False}
WAVE = {"fn": wave_crest(), "shading": False}
LEG_PAINT = {"thigh": LEGC, "shin": LEGC, "meta": {"base": "coat"}, "foot": {"fn": hoof}}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 21, 0)

HY, HZ = 27.0, -22.0
# gentle fairy eyes: outer lash, white catch-light, lilac iris turning pale at the bottom, deep plum pupil
# (rows top -> bottom, col 0 = outer corner)
EYE = dict(x_edge=4.0, w=3, y0=HY - 4.0, h=4, z_face=HZ - 6.0, d=2, lash_row=2,
           front=["HD.",
                  "DSI",
                  "DEJ",
                  ".JJ"],
           side_rows=[".H", "SI", "EJ", "JJ"])
HEAD = coat([(0, HY + 0.6, HZ - 1.5, 3.6, 1.0, 2.2)] + [(sx * 4.3, HY - 2.0, HZ - 1.5, 1.2, 2.0, 2.0) for sx in (1, -1)],
            lunettes=[(sx * 3.1, HY - 2.0, HZ - 6.0, 1.9, 2.3, 1.5) for sx in (1, -1)], space="local", seed=10, warp=0.6,
            extra=closed_lids(**EYE))

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 21, 2], cubes=[
        Cube([-6, 15, -6], [12, 12, 17], BODY),
        Cube([-5, 14, -5], [10, 1, 15], BODY),                                     # belly
        Cube([-5, 17, 11], [10, 9, 1], BODY),                                      # rump
        Cube([-5.5, 27, 7], [11, 1, 3], BODY),                                     # hook bones
        Cube([-1.5, 27, 10], [3, 1, 2], BODY),                                     # tailhead
        Cube([-3, 12, 3.5], [6, 3, 5], {"fn": udder_fn}),                          # pearly udder
        Cube([-2, 11, 4.5], [1, 1, 1], {"base": "teat"}), Cube([1, 11, 4.5], [1, 1, 1], {"base": "teat"}),
        Cube([-2, 11, 6.5], [1, 1, 1], {"base": "teat"}), Cube([1, 11, 6.5], [1, 1, 1], {"base": "teat"})])
    m.bone("chest", "torso", [0, 21, -6], cubes=[
        Cube([-6.5, 14, -14], [13, 14, 8], BODY),
        Cube([-5, 13, -13.5], [10, 1, 6], BODY),                                   # brisket
        Cube([-1.5, 10.5, -14], [3, 3, 5], BODY),                                  # dewlap
        Cube([-5, 28, -13], [10, 1, 6], BODY)])                                    # withers
    m.bone("crest2", "chest", [0, 29, -10], cubes=[Cube([0, 28.8, -13.5], [0, 4, 7], WAVE)])
    m.bone("neck", "chest", [0, 24.5, -13], rotation=[-20, 0, 0], cubes=[
        Cube([-4, 19, -22], [8, 8, 9], BODY),
        Cube([-4.5, 18.5, -18.5], [9, 9, 1], {"fn": leather}),                     # collar
        Cube([-1, 26.6, -19.2], [2, 1, 1], {"fn": solid("brass")})])               # buckle
    m.bone("crest", "neck", [0, 27, -17], cubes=[Cube([0, 26.8, -21.5], [0, 5, 9], WAVE),
                                                 Cube([-0.5, 26.8, -20.5], [1, 1, 8], {"fn": foam, "shading": False})])
    m.bone("bell", "neck", [0, 18.5, -18], cubes=[
        Cube([-0.5, 17.5, -18.5], [1, 1, 1], {"fn": leather}),
        Cube([-1.5, 15, -19.5], [3, 2, 3], NACRE), Cube([-2, 13, -20], [4, 2, 4], NACRE),
        Cube([-0.5, 12, -18.5], [1, 1, 1], {"fn": solid("brass")})])
    for i, (fx, fz) in enumerate(((3.6, -18.6), (-3.6, -18.6), (2.6, -18.8))):    # blossoms tucked in the collar
        m.get("neck").cubes.append(Cube([fx - 0.5, 23 - 2 * i, fz - 0.5], [1, 1, 1], {"fn": flower}))
    m.bone("head", "neck", [0, HY - 0.5, HZ], rotation=[46, 0, 0], cubes=[
        Cube([-4, HY - 8, HZ - 6], [8, 8, 6], HEAD),
        Cube([-3, HY, HZ - 4], [6, 1, 3], HEAD),                                   # poll
        Cube([-3, HY - 8, HZ - 8], [6, 4, 2], {"base": "muzzle", "fn": muzzle_fn()}),
        Cube([-0.5, HY - 2, HZ - 6.4], [1, 1, 1], NACRE),                           # sacred forehead pearl
        Cube([-3.5, HY + 1, HZ - 3.5], [7, 1, 2], {"fn": blossom}),                # apple-blossom crown
        Cube([-1.5, HY + 2, HZ - 3.5], [1, 1, 1], {"fn": flower}), Cube([0.5, HY + 2, HZ - 3], [1, 1, 1], {"fn": flower})])
    m.bone("jaw", "head", [0, HY - 8, HZ - 3], cubes=[
        Cube([-2.5, HY - 9, HZ - 7.5], [5, 1, 5], {"base": "coat", "up": "mouth", "north": "muzzle"})])
    for side, sx in SIDES:
        add_eye(m, "head", side, sx, **EYE)
        eo = 4 if sx > 0 else -8
        m.bone(f"ear_{side}", "head", [4 * sx, HY - 2.5, HZ - 1.5], rotation=[0, 0, 12 * sx], cubes=[
            Cube([eo, HY - 3.5, HZ - 2], [4, 2, 1], {"base": "patch", "fn": ear_fn})])
        # lyre horns: out and up, then the glowing nacre tips flare outwards
        b1 = 3 if sx > 0 else -7
        m.bone(f"horn_{side}", "head", [3 * sx, HY, HZ - 2], rotation=[0, 12 * sx, -8 * sx], cubes=[
            Cube([b1, HY - 1, HZ - 3], [4, 2, 2], {"fn": solid("horn")})])
        b2 = 6 if sx > 0 else -8
        m.bone(f"horn2_{side}", f"horn_{side}", [7 * sx, HY, HZ - 2], rotation=[-8, 0, 40 * sx], cubes=[
            Cube([b2, HY - 0.5, HZ - 3], [2, 4, 2], {"fn": solid("horn_mid")})])
        b3 = 6.5 if sx > 0 else -7.5
        m.bone(f"horn3_{side}", f"horn2_{side}", [7 * sx, HY + 3.5, HZ - 2], rotation=[-25, 0, 30 * sx], cubes=[
            Cube([b3, HY + 3.5, HZ - 2.5], [1, 3, 1], NACRE)])
    m.bone("tail", "torso", [0, 27, 11.5], rotation=[8, 0, 0], cubes=[
        Cube([-1, 16, 11], [2, 11, 2], BODY)])
    m.bone("tail_tip", "tail", [0, 16, 12], cubes=[
        Cube([-1.5, 11, 10.5], [3, 5, 3], FOAM), Cube([-1, 10, 11], [2, 1, 2], FOAM)])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    q = "q.anim_time"
    W = 360 / 1.25
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=(), torso=(0.8, 1.5, 2.0),
                       walk_kw=dict(T=1.25, stride=11, lift=2.8, stance=0.68, bob=0.45, toe_off=18, fold=50, curl=28),
                       battle=dict(theta=2.0, dy=-0.8, neck=8, head=-10, paw="front_right", paw_t=1.3,
                                   ears_back=14, tail_up=10),
                       cry=dict(L=2.8, t_in=0.4, t_open=0.85, t_close=2.1, neck=-12, head=-20, jaw=13, tremble=1.0,
                                extra={"bell": {"rotation": lambda t, e: [8 * e * math.sin(math.radians(t * 420)), 0,
                                                                          5 * e * math.sin(math.radians(t * 300))]}}),
                       idle_extra={"bell": {"rotation": [f"math.sin({q}*90+60)*3", 0, f"math.sin({q}*45)*3"]},
                                   "crest": {"rotation": [0, 0, f"math.sin({q}*90)*2"]},
                                   "crest2": {"rotation": [0, 0, f"math.sin({q}*90-40)*2"]}},
                       walk_extra={"bell": {"rotation": [f"math.sin({q}*{2 * W}+60)*9", 0, f"math.sin({q}*{W})*5"]},
                                   "crest": {"rotation": [0, 0, f"math.sin({q}*{W}+40)*3"]},
                                   "crest2": {"rotation": [0, 0, f"math.sin({q}*{W})*3"]}})
    return finalize(out)

def poser():
    return bovine_poser(SID, portrait=(1.26, [-0.84, 1.03, 0]), profile=(0.6, [-0.17, 0.84, 0]))
