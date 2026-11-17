# -*- coding: utf-8 -*-
"""#1048 Alchibec — alambic de cuivre gardien des vieilles caves, habité par un gigantesque esprit de feu (Eau / Feu).
A great spherical still of solid hammered copper, riveted at its seams, standing on three iron legs, with an engraved
onion dome, a swan-neck pipe running to its condensing coil, a tap with a red valve wheel, a pressure gauge and a
drop handle. From the dome rises a gigantic spirit of liquid, gaseous fire in a blazing golden brown, towering over
the still: a broad chest, long arms ending in clawed hands that knead alchemical energy, a head crowned with flames,
three pairs of glowing eyes and a huge jagged jaw like a carved lantern. The spirit holds the whole still up in the
air: it floats over old cellars, swaying and staggering as it goes, iron legs dangling; asleep, the spirit sinks
into the dome and the still comes to rest on its legs. Its fire breath melts rock.
Shiny: blue flambé flames (calvados set alight)."""
import math
from modelgen import Model, Cube, rgb
from biped import keys, smooth, pose_sequence
from bovine import sampled, finalize, lerp_keys
from templates import flame
from vessel import copper, iron, gauge, vapour, steam, char_plane, octo, with_faces, bob, lifted, lift_track

SID, DEX = "alchibec", 1048
FRAME_BONES = ("head", "jaw")
HEIGHT_SKIP = ("flame", "steam")

PAL = {
    "copper": rgb("#C46A32"), "copper_dark": rgb("#7A3A1A"), "copper_light": rgb("#F2A764"), "patina": rgb("#4E9A84"),
    "iron": rgb("#3A3634"), "iron_dark": rgb("#1E1C1B"), "brass": rgb("#C9A040"), "dial": rgb("#F2EEE2"),
    "needle": rgb("#C0201A"), "valve": rgb("#B0201A"),
    "spirit_core": rgb("#FFE07A"), "spirit": rgb("#E8952E"), "spirit_edge": rgb("#7A3A12"), "spirit_dark": rgb("#4A1C08"),
    "spirit_deep": rgb("#A8561C"),
    "flame_core": rgb("#FFF6C8"), "flame_mid": rgb("#FFC43A"), "flame_out": rgb("#E8781E"), "flame_tip": rgb("#8A3612"),
    "eye_hot": rgb("#FFFBE0"), "eye_glow": rgb("#FFD040"), "eye_dark": rgb("#3A1404"),
    "mouth": rgb("#3A1404"), "mouth_glow": rgb("#FFF0A0"), "tooth": rgb("#7A3010"),
    "steam": rgb("#EEE6D8"), "steam_light": rgb("#FFFFFF"),
}
SHINY = dict(PAL, **{
    "spirit_core": rgb("#E6F6FF"), "spirit": rgb("#4E9CF0"), "spirit_edge": rgb("#162E7A"), "spirit_dark": rgb("#0A1650"),
    "spirit_deep": rgb("#2858B8"),
    "flame_core": rgb("#FFFFFF"), "flame_mid": rgb("#A8E0FF"), "flame_out": rgb("#3A86E8"), "flame_tip": rgb("#18307A"),
    "eye_hot": rgb("#FFFFFF"), "eye_glow": rgb("#9FE8FF"), "eye_dark": rgb("#0A1440"),
    "mouth": rgb("#0A1440"), "mouth_glow": rgb("#E6FAFF"), "tooth": rgb("#1E3E9A"),
})

BOILER = copper(seed=7, rivets=[12.5, 19.5])
DOME = copper(seed=8, engrave=[(29.5, 32.5)], rivets=[27.5])
PIPE = copper(seed=9)
IRON = {"fn": iron()}
GAUGE = {"fn": gauge}
VALVE = {"base": "valve"}
G = {"glow": True, "shading": False}
SPIRIT = {**vapour(seed=5, center=(0, 52, -3), radius=19, fire=True), **G}
# the head is darker and smoky, so its carved-lantern features blaze out of it
_HEAD = dict(core="spirit", mid="spirit_deep", edge="spirit_edge", seed=6, center=(0, 63, -6), radius=14)
HEADP = {**vapour(fire=True, **_HEAD), **G}
JAW = {**with_faces(vapour(fire=True, **_HEAD), {"up": "mouth_glow"}), **G}
MOUTH_ROOF = {**with_faces(vapour(**_HEAD), {"down": "mouth_glow"}), **G}
ARM = {s: {**vapour(seed=11, center=(20 * s, 55, -12), radius=13, fire=True), **G} for s in (1, -1)}
CLAW = {**vapour(core="spirit_core", mid="spirit", edge="spirit_edge", seed=12, streaks=False), **G}
TIP = {**vapour(core="spirit_edge", mid="spirit_edge", edge="spirit_dark", seed=13, streaks=False), **G}
FLAME = {"fn": flame(), **G}

# angry slanted eyes (+X eye: column 0 = inner side) and two smaller pairs above
EYE1 = ["....OOO", "..OHHHO", "OHHHHO.", ".OOO..."]
EYE2 = ["..OO", "OHHO", "OO.."]
EYE3 = ["OH", "HO"]
EK = {"H": "eye_hot", "O": "eye_glow", "D": "eye_dark"}
GRIN_UP = ["Q..................Q", "QQTTTQQQTTTTQQQTTTQQ", ".QQTQQQQQTTQQQQQTQQ.", "..QQQQQQQQQQQQQQQQ.."]
GRIN_LO = ["..QQQQQQQQQQQQQQQQ..", "...QQQTQQQQQQTQQQ...", "....QTTTQQQQTTTQ....", "......QQQQQQQQ......"]
MK = {"Q": "mouth_glow", "T": "tooth", "D": "mouth"}
LEGS = (("front_left", 5.5, -5.5), ("front_right", -5.5, -5.5), ("back", 0.0, 7.5))

def build():
    m = Model(SID, DEX, (256, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, 0, 0])
    for name, x, z in LEGS:                                                      # three splayed iron legs
        fx, fz = x * 1.2, z * 1.2
        m.bone(f"foot_{name}", "body", [x, 9, z], cubes=[
            Cube([x - 1, 3, z - 1], [2, 8, 2], IRON), Cube([(x + fx) / 2 - 1, 1.5, (z + fz) / 2 - 1], [2, 2, 2], IRON),
            Cube([fx - 1.5, 0, fz - 1.5], [3, 2, 3], IRON)])
    still = []
    for y0, h, r in ((5, 1, 4.5), (6, 1, 6.5), (7, 1, 8), (8, 2, 9.5), (10, 2, 10.5), (12, 8, 11), (20, 2, 10.5),
                     (22, 1, 9.5), (23, 1, 8.5), (24, 1, 7.5), (25, 1, 6.5)):
        still += octo(y0, h, r, BOILER)
    still += octo(26, 1, 6, DOME)                                                 # collar
    for y0, h, r in ((27, 1, 5.5), (28, 1, 6.5), (29, 3, 7), (32, 1, 6.5), (33, 1, 5.5), (34, 1, 4.5), (35, 1, 3.5),
                     (36, 1, 2.5)):                                                # engraved onion dome
        still += octo(y0, h, r, DOME)
    still += [
        # drop handle on its left flank
        Cube([10.5, 20, -3], [2, 1, 1], PIPE), Cube([10.5, 20, 2], [2, 1, 1], PIPE), Cube([12.5, 17, -3], [1, 4, 6], PIPE),
        # pressure gauge on the front shoulder
        Cube([5, 24.5, -9], [2, 2, 2], PIPE), Cube([4, 23.5, -11], [4, 4, 2], GAUGE)]
    m.bone("still", "body", [0, 6, 0], cubes=still)
    # swan-neck pipe from the dome to the condensing coil on its right, down to the tap
    pipe = [Cube([-6, 36, -1], [3, 2, 2], PIPE), Cube([-9, 37, -1], [3, 2, 2], PIPE), Cube([-12, 36, -1], [3, 2, 2], PIPE),
            Cube([-14, 34, -1], [2, 3, 2], PIPE), Cube([-15, 22, -1], [2, 12, 2], PIPE),
            Cube([-15, 15, -1], [2, 7, 2], PIPE), Cube([-15, 14, -5], [2, 2, 6], PIPE), Cube([-13, 18, -1], [3, 1, 2], PIPE),
            Cube([-14.5, 13, -5], [1, 1, 1], PIPE),
            Cube([-15.5, 16, -4.5], [3, 1, 3], VALVE), Cube([-14.5, 15.5, -3.5], [1, 1, 1], IRON)]
    for y in (23, 25.5, 28, 30.5):                                                # coil
        pipe += [Cube([-17, y, -3], [6, 1, 1], PIPE), Cube([-17, y, 2], [6, 1, 1], PIPE),
                 Cube([-17, y, -2], [1, 1, 4], PIPE), Cube([-12, y, -2], [1, 1, 4], PIPE)]
    m.bone("pipe", "still", [-6, 36, 0], cubes=pipe)
    m.bone("steam1", "pipe", [-14, 12, -4.5], cubes=[
        Cube([-15.5, 12, -4.5], [3, 7, 0], {"fn": steam(seed=1), "shading": False}),
        Cube([-14, 12, -6], [0, 7, 3], {"fn": steam(seed=1), "shading": False})])

    # ---------------------------------------------------------------- the fire spirit
    # rising out of the dome like a genie: narrow at the still, a huge hunched chest and shoulders, the head thrust
    # forward over the still, long arms reaching out with clawed hands
    m.bone("spirit", "still", [0, 36, 0], cubes=[
        Cube([-3, 34, -3], [6, 4, 6], SPIRIT), Cube([-5, 37, -4.5], [10, 4, 9], SPIRIT), Cube([-8, 40, -6], [16, 4, 12], SPIRIT),
        Cube([-12, 43, -7], [24, 10, 14], SPIRIT), Cube([-13, 45, -6], [26, 7, 12], SPIRIT),
        Cube([-11, 44, -8], [22, 8, 1], SPIRIT), Cube([-11, 44, 7], [22, 9, 1], SPIRIT),
        Cube([-15, 52, -5.5], [30, 7, 11], SPIRIT), Cube([-13, 59, -4], [26, 1, 8], SPIRIT),
        # trailing wisps on the back
        Cube([-3, 38, 4], [3, 5, 3], SPIRIT), Cube([4, 41, 6], [3, 4, 2], SPIRIT), Cube([-9, 47, 8], [3, 4, 2], SPIRIT)])
    m.bone("head", "spirit", [0, 56, -5], cubes=[
        Cube([-11, 56, -14], [22, 13, 12], HEADP), Cube([-10, 55, -15], [20, 15, 14], HEADP),
        Cube([-10, 55, -16], [20, 14, 1], HEADP), Cube([-9, 56, -1], [18, 12, 1], HEADP),
        Cube([11, 57, -13], [1, 11, 10], HEADP), Cube([-12, 57, -13], [1, 11, 10], HEADP),
        Cube([-10, 70, -14], [20, 1, 12], HEADP), Cube([-7, 71, -12], [14, 1, 8], HEADP),
        Cube([-10, 55, -15.5], [20, 0, 11], MOUTH_ROOF),
        Cube([-10, 55.2, -16.06], [20, 4, 0], {"fn": char_plane(GRIN_UP, MK), **G})])
    m.bone("jaw", "head", [0, 55.5, -4], cubes=[
        Cube([-10.5, 49, -15.5], [21, 6, 12], JAW),
        Cube([-10, 50.8, -15.56], [20, 4, 0], {"fn": char_plane(GRIN_LO, MK), **G})])
    for side, s in (("left", 1), ("right", -1)):
        for k, (rows, x0, y0) in enumerate(((EYE1, 1.0, 61), (EYE2, 5.5, 65.5), (EYE3, 1.0, 66))):
            w, h = len(rows[0]), len(rows)
            ex = x0 if s > 0 else -x0 - w
            grid = rows if s > 0 else [r[::-1] for r in rows]
            name = "eye" if k == 0 else f"eye{k + 1}"
            m.bone(f"{name}_{side}", "head", [ex + w / 2, y0 + h / 2, -16.1], cubes=[
                Cube([ex, y0, -16.1], [w, h, 0], {"fn": char_plane(grid, EK), **G})])
        X = lambda x0, w: x0 if s > 0 else -x0 - w                                  # mirror a cube's x origin
        m.bone(f"arm_{side}", "spirit", [15 * s, 55.5, -1], cubes=[Cube([X(15, 9), 52, -4.5], [9, 7, 7], ARM[s])])
        m.bone(f"forearm_{side}", f"arm_{side}", [21.5 * s, 55.5, -1], cubes=[Cube([X(18, 7), 52, -15], [7, 7, 12], ARM[s])])
        fingers = []
        for fx in (17.5, 20.5, 23.5):
            fingers += [Cube([X(fx, 2), 55, -28], [2, 2, 6], CLAW), Cube([X(fx + 0.5, 1), 54.5, -30], [1, 1, 2], TIP)]
        m.bone(f"hand_{side}", f"forearm_{side}", [21.5 * s, 55.5, -15], cubes=[
            Cube([X(17.5, 8), 51.5, -22], [8, 8, 7], ARM[s]), Cube([X(15.5, 2), 52.5, -21], [2, 2, 5], CLAW),
            Cube([X(15.5, 1), 52.5, -23], [1, 1, 2], TIP)] + fingers)
    # crown of flames, flames on the shoulders, elbows and back
    fl = ((0, 71.5, -8, 8, 12, "head"), (-6, 70.5, -9, 6, 9, "head"), (6, 70.5, -9, 6, 9, "head"), (0, 70.5, -3, 6, 8, "head"),
          (13, 59, 0, 6, 9, "spirit"), (-13, 59, 0, 6, 9, "spirit"), (0, 52, 7, 6, 8, "spirit"),
          (21.5, 59, -8, 4, 6, "forearm_left"), (-21.5, 59, -8, 4, 6, "forearm_right"),
          (11.5, 63, -9, 4, 8, "head"), (-11.5, 63, -9, 4, 8, "head"))
    for k, (x, y, z, w, h, par) in enumerate(fl):
        m.bone(f"flame{k + 1}", par, [x, y, z], cubes=[
            Cube([x - w / 2, y, z], [w, h, 0], FLAME), Cube([x, y, z - w / 2], [0, h, w], FLAME)])
    m.pack()
    return m

# ---------------------------------------------------------------- animations
Q = "q.anim_time"
EYES = [f"{n}_{s}" for n in ("eye", "eye2", "eye3") for s in ("left", "right")]
FLAMES = [f"flame{k}" for k in range(1, 12)]
HOVER = 6.0                 # levitation height (model units); asleep or KO it rests on its legs

def _flames(amp=0.12, speed=1.0, base=1.0):
    out = {}
    for k, f in enumerate(FLAMES):
        fr = round(400 * speed + 37 * k, 1)
        out[f] = {"scale": [base, f"{base}+math.sin({Q}*{fr}+{k * 70})*{amp}+math.sin({Q}*{fr * 1.7:.1f})*{amp / 2}", base],
                  "rotation": [f"math.sin({Q}*{fr / 3:.1f}+{k * 40})*6", 0, f"math.sin({Q}*{fr / 2.5:.1f}+{k * 55})*8"]}
    return out

def _steam(speed=1.0, height=4.0):
    u = f"(({Q}*{round(speed / 3, 4)})-math.floor({Q}*{round(speed / 3, 4)}))"
    return {"steam1": {"position": [f"math.sin({Q}*{round(120 * speed, 1)})*0.6", f"{u}*{height}", 0],
                       "scale": [f"0.5+{u}*0.9", f"0.4+{u}*0.8", f"0.5+{u}*0.9"]}}

def anims(m=None):
    m = m or build()
    a = f"animation.{SID}."
    out = {}

    def arms(p, up=0.0, fwd=0.0, spread=0.0, curl=0.0, t=0.0, wob=1.0):
        for side, s in (("left", 1), ("right", -1)):
            ph = 0 if s > 0 else 1.3
            w = math.sin(t * 2.2 + ph) * wob
            p[f"arm_{side}"] = {"rotation": [-fwd, -s * spread, s * (18 - up + 4 * w)]}
            p[f"forearm_{side}"] = {"rotation": [-8 * w, s * (8 - spread * 0.5), 0]}
            p[f"hand_{side}"] = {"rotation": [curl + 10 * w, 0, s * 6 * w]}
        return p

    # idle: the still staggers (a slow tipsy roll, a hiccup that jolts it), the spirit sways, kneads the air with its
    # claws and looks about; its jaw chatters once
    def dangle(p, t, back=0.0, amp=1.0):
        for k, (name, x, z) in enumerate(LEGS):
            p[f"foot_{name}"] = {"rotation": [back + 4 * amp * math.sin(t * 2.4 + k * 2.1), 0, 3 * amp * math.sin(t * 1.7 + k * 1.3)]}
        return p

    def idle(t):
        w = t * 2 * math.pi / 8
        hic = math.exp(-((t - 5.0) / 0.12) ** 2)
        roll = 3.0 * math.sin(w) + 1.2 * math.sin(3 * w + 0.5)
        p = {"still": {"rotation": [1.2 * math.sin(2 * w), 0, roll - 4 * hic], "position": [0, 0.6 * hic, 0]},
             "spirit": {"rotation": [3 + 2 * math.sin(2 * w + 1), 2 * math.sin(w), -roll * 1.6 + 5 * math.sin(w + 1.1) + 6 * hic]},
             "head": {"rotation": [-2 * math.sin(2 * w), 0, 4 * math.sin(w + 2.0)]},
             "jaw": {"rotation": [max(0.0, 10 * math.sin(math.radians((t - 6.0) * 720))) if 6.0 < t < 7.0 else 0, 0, 0]}}
        dangle(p, t * 2 * math.pi / 8 * 2 / 2.4)
        return arms(p, up=0, fwd=5, curl=0, t=t * 1.3)
    b = sampled(8, 0.05, lifted(idle, lambda t: bob(t, HOVER, 0.8, 4.0)), loop=True)
    b.update(_flames()); b.update(_steam())
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": b}

    # walk: it drifts through the air with a drunken lurch from side to side, iron legs trailing behind
    T = 1.5
    def walk(t):
        lurch = 5.0 * math.sin(2 * math.pi * t / (2 * T))
        p = {"still": {"rotation": [5 + 1.5 * math.sin(2 * math.pi * t / T), 0, lurch]},
             "spirit": {"rotation": [8, 3 * math.sin(2 * math.pi * t / T), -lurch * 1.8]},
             "head": {"rotation": [-4, 0, lurch * 0.8]}}
        dangle(p, t * 2 * math.pi / (2 * T) * 2 / 2.4 * 2, back=12, amp=1.4)
        return arms(p, up=-6, fwd=12, t=t * 2.0, wob=0.6)
    b = sampled(2 * T, 0.05, lifted(walk, lambda t: bob(t, HOVER + 0.5, 0.8, T)), loop=True)
    b.update(_flames(0.18, 1.4)); b.update(_steam(1.5, 3))
    out[a + "ground_walk"] = {"loop": True, "animation_length": 2 * T, "bones": b}

    # battle: the spirit rears up out of the dome and looms forward, arms wide and claws open, jaw ajar
    def battle(t):
        w = math.sin(t * 2 * math.pi / 2.5)
        p = {"still": {"rotation": [0, 0, 1.5 * math.sin(t * 2 * math.pi / 5)]},
             "spirit": {"position": [0, 2.0 + 0.4 * w, 0], "rotation": [10 + 2 * w, 0, 2 * math.sin(t * 2 * math.pi / 5)],
                        "scale": [1.05, 1.05, 1.05]},
             "head": {"rotation": [6, 0, 0]},
             "jaw": {"rotation": [10 + 4 * max(0.0, w), 0, 0]}}
        dangle(p, t * 2 * math.pi / 2.5 / 2.4 * 2.4, amp=0.6)
        return arms(p, up=38, fwd=10, spread=18, curl=-15, t=t * 2.5, wob=0.8)
    b = sampled(2.5, 0.05, lifted(battle, lambda t: bob(t, HOVER + 1.5, 0.5, 2.5)), loop=True)
    b.update(_flames(0.22, 1.8, 1.15)); b.update(_steam(2.5, 5))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 2.5, "bones": b}

    # cry: rears back, then a roar - jaw wide, arms thrown wide, the flames flaring
    L = 2.2
    def cry(t):
        back = lerp_keys([(0, 0), (0.35, 1), (0.6, -0.4), (1.8, -0.3), (2.2, 0)], t)
        jaw = lerp_keys([(0, 0), (0.45, 0), (0.65, 32), (1.7, 28), (2.1, 0)], t)
        sh = math.sin(t * 50) * (1 if 0.65 < t < 1.7 else 0)
        p = {"spirit": {"position": [0, 2.5 * max(0, -back) + 1.0 * max(0, back), 0], "rotation": [-10 * back + 2 * sh, 0, 0],
                        "scale": [1 + 0.06 * max(0, -back) / 0.4] * 3},
             "head": {"rotation": [-8 * back + 1.5 * sh, 0, 0]}, "jaw": {"rotation": [jaw, 0, 0]},
             "still": {"rotation": [0, 0, 0.8 * sh]}}
        e = smooth(t / 0.6) if t < 1.8 else 1 - smooth((t - 1.8) / 0.4)
        p = arms(p, up=60 * e, fwd=-5 * e, spread=25 * e, curl=-30 * e, t=t * 3, wob=0.5)
        for k, f in enumerate(FLAMES):
            g = 1 + 0.6 * e * max(0.0, -back) / 0.4 + 0.1 * math.sin(t * 30 + k)
            p[f] = {"scale": [g, g * 1.2, g]}
        return p
    out[a + "cry"] = {"animation_length": L, "bones": sampled(L, 0.04, lifted(cry, lambda t: HOVER + 1.2 * math.sin(math.pi * t / L)))}

    # sleep: the spirit shrinks back into the dome - only a small drowsy flame peeks out, eyes shut
    sl = {"spirit": {"scale": [0.32, f"0.3+math.sin({Q}*50)*0.015", 0.32], "position": [0, -1.5, 0]},
          "still": {"rotation": [0, 0, f"math.sin({Q}*30)*0.8"]}}
    for e in EYES:
        sl[e] = {"scale": [1, 0.12, 1]}
    sl["jaw"] = {"rotation": [0, 0, 0]}
    sl.update(_flames(0.1, 0.4, 0.8))
    sl.update(_steam(0.4, 3))
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sl}

    out[a + "blink"] = {"animation_length": 0.25, "bones": {e: {"scale": {"0.0": [1, 1, 1], "0.12": [1, 0.12, 1], "0.25": [1, 1, 1]}}
                                                             for e in EYES}}

    # faint: the spirit flickers and collapses back into the still, which reels and keels over
    k0 = {"body": {"rotation": [0, 0, 0]}}
    k1 = {"body": {"rotation": [0, 0, -6]}, "spirit": {"rotation": [-15, 0, 10]}, "head": {"rotation": [-10, 0, 0]},
          "jaw": {"rotation": [25, 0, 0]}}
    k2 = {"body": {"rotation": [0, 0, 7]}, "spirit": {"rotation": [20, 0, -18]}, "head": {"rotation": [20, 0, -10]},
          "jaw": {"rotation": [12, 0, 0]}}
    k3 = {"body": {"rotation": [0, 0, 80]}, "spirit": {"rotation": [30, 0, 12]}, "head": {"rotation": [25, 0, 8]},
          "jaw": {"rotation": [18, 0, 0]}}
    k4 = {"body": {"rotation": [0, 0, 76]}, "spirit": {"rotation": [32, 0, 15]}, "head": {"rotation": [25, 0, 10]},
          "jaw": {"rotation": [20, 0, 0]}}
    fb = pose_sequence(m, [(0, k0), (0.4, k1), (0.9, k2), (1.6, k3), (2.0, k4), (2.6, k3)], length=2.6,
                       skip=tuple(b.name for b in m.bones if b.name.startswith(("steam", "flame", "spirit", "head", "jaw", "eye",
                                                                                  "arm", "forearm", "hand"))))
    lift_track(fb, lambda t: HOVER * (1 - smooth(t / 1.4)))                    # the still drops out of the air
    fb["spirit"].update(keys(scale={0: [1, 1, 1], 0.9: [0.9, 0.9, 0.9], 1.6: [0.45, 0.45, 0.45], 2.6: [0.4, 0.4, 0.4]}))
    for e in EYES:
        fb[e] = keys(scale={0: [1, 1, 1], 1.3: [1, 1, 1], 1.6: [1, 0.12, 1], 2.6: [1, 0.12, 1]})
    for k, f in enumerate(FLAMES):
        fb[f] = keys(scale={0: [1, 1, 1], 0.9: [1.1, 1.3, 1.1], 1.8: [0.3, 0.2, 0.3], 2.6: [0.2, 0.15, 0.2]})
    fb["steam1"] = {"scale": 0}
    out[a + "faint"] = {"animation_length": 2.6, "bones": fb}

    # portrait: looming, claws up beside the head
    pb = arms({"spirit": {"rotation": [8, 0, 0]}, "head": {"rotation": [4, -10, 0]}, "jaw": {"rotation": [8, 0, 0]}},
              up=40, fwd=5, spread=10, curl=-10, wob=0)
    pb = {k: {ch: [round(v, 3) for v in vals] for ch, vals in d.items()} for k, d in pb.items()}
    pb.update(_flames())
    out[a + "portrait"] = {"loop": True, "animation_length": 8, "bones": pb}
    return finalize(out)

def poser():
    from templates import poser as make_poser
    ps = make_poser(SID, portrait=(0.8, [0, -1.6, 0]), profile=(0.45, [0, 1.0, 0]))
    ps["poses"]["standing"]["poseTypes"] = ["STAND", "NONE", "FLOAT"]
    ps["poses"] = {"portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "isBattle": False,
                                "animations": [f"q.bedrock('{SID}', 'portrait')"],
                                "quirks": [f"q.bedrock_quirk('{SID}', 'blink')"]}, **ps["poses"]}
    return ps
