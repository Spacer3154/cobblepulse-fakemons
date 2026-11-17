# -*- coding: utf-8 -*-
"""#1047 Cruchevados — cruche de grès normande d'où s'échappe un esprit de cidre chaud (Eau / Feu).
A taller pot-bellied stoneware pitcher, brown-orange glaze running in drips over the raw grès of its lower belly,
an elegant handle on one side and a pinched pouring spout on the other. A deep crack on its flank glows with the
heat inside. Part of the liquid has escaped through the neck as a vaporous, half-gaseous spirit topped with two big
swirling eyes and a mischievous grin; its little fluid hands cling to the rim. It floats above the ground, swaying,
and its heady fumes curl from the spout and from the top of its head; asleep, it settles on its foot ring.
Shiny: the green glaze of the Pré-d'Auge potteries, holding a ruby pommeau spirit."""
import math
from modelgen import Model, Cube, rgb
from biped import keys, smooth, pose_sequence
from bovine import sampled, finalize, lerp_keys
from vessel import stoneware, cider, vapour, steam, char_plane, swirl_eye, crack, SWIRL7, EYE_K, bob, lifted, lift_track

SID, DEX = "cruchevados", 1047
FRAME_BONES = ("head",)
HEIGHT_SKIP = ("steam", "wisp")

PAL = {
    "clay": rgb("#D2A06A"), "clay_dark": rgb("#7A4020"), "clay_light": rgb("#E8C190"),
    "glaze": rgb("#B85E22"), "glaze_light": rgb("#E08A40"),
    "cider": rgb("#F2A93A"), "cider_light": rgb("#FFE08A"), "cider_dark": rgb("#C27418"),
    "spirit_core": rgb("#FFE29A"), "spirit": rgb("#F0A442"), "spirit_edge": rgb("#B4622A"),
    "swirl": rgb("#5A2A10"), "swirl_bg": rgb("#FFD98A"),
    "mouth": rgb("#5A2208"), "mouth_glow": rgb("#FFD27A"), "tooth": rgb("#FFF4D6"),
    "crack_hot": rgb("#FFF2B0"), "crack_glow": rgb("#FF8A1E"), "crack_edge": rgb("#6A1A08"),
    "steam": rgb("#F6EEE0"), "steam_light": rgb("#FFFFFF"),
}
SHINY = dict(PAL, **{
    "clay": rgb("#E2D3A8"), "clay_dark": rgb("#5A4A26"), "clay_light": rgb("#F4EAC8"),
    "glaze": rgb("#3F7A2C"), "glaze_light": rgb("#86B84E"),
    "cider": rgb("#C8323E"), "cider_light": rgb("#FF8A86"), "cider_dark": rgb("#801C26"),
    "spirit_core": rgb("#FFC8BE"), "spirit": rgb("#E2505E"), "spirit_edge": rgb("#8A1E30"),
    "swirl": rgb("#4A0A18"), "swirl_bg": rgb("#FFC8BE"), "mouth": rgb("#4A0A18"), "mouth_glow": rgb("#FF8A86"),
})

BELLY = stoneware(seed=21, glaze="glaze", drip_y=12.5, grog=0.05)
GLAZED = stoneware(seed=22, glaze="glaze", drip_y=-99, grog=0.03)
RAW = stoneware(seed=23, base="clay", dark="clay_dark", light_key="clay_light", grog=0.1)
LIQ = {**cider(), "glow": True, "shading": False}
SPIRIT = {**vapour(seed=5, center=(0, 34.5, -1), radius=10.5), "glow": True, "shading": False}
STEM = {**vapour(seed=6, center=(0, 27, 0), radius=6), "glow": True, "shading": False}
CRACK = ["...DHD",
         "..DHOD",
         "..DOH.",
         ".DHHD.",
         "DHOD..",
         ".DOHD.",
         "..DHO.",
         "...DO."]
CRACK_TOP = ["DH.", "HOD", ".D."]
HANDS = {**vapour(mid="spirit_core", core="cider_light", edge="spirit", seed=9), "glow": True, "shading": False}
SMILE = ["MM.....MM", ".MTMTMTM.", "..MMMMM.."]
OPEN = [".MMM.", "MQQQM", "MQQQM", ".MMM."]
EYE_ON = {"fn": None, "glow": True, "shading": False}

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, 0, 0])
    m.bone("jug", "body", [0, 4, 0], cubes=[
        Cube([-5, 4, -4], [10, 1, 8], RAW), Cube([-4, 4, -5], [8, 1, 10], RAW),            # foot ring (raw grès)
        Cube([-7, 5, -5], [14, 2, 10], BELLY), Cube([-5, 5, -7], [10, 2, 14], BELLY),
        # pot belly (three overlapping boxes: almost round)
        Cube([-8, 7, -6], [16, 8, 12], BELLY), Cube([-6, 7, -8], [12, 8, 16], BELLY), Cube([-7.5, 8, -7.5], [15, 6, 15], BELLY),
        Cube([-7, 15, -5], [14, 3, 10], GLAZED), Cube([-5, 15, -7], [10, 3, 14], GLAZED), Cube([-6.5, 15, -6.5], [13, 2, 13], GLAZED),
        Cube([-5, 18, -4], [10, 2, 8], GLAZED), Cube([-4, 18, -5], [8, 2, 10], GLAZED),
        # hollow neck and flared rim
        Cube([-4, 20, -4], [8, 4, 1], GLAZED), Cube([-4, 20, 3], [8, 4, 1], GLAZED),
        Cube([3, 20, -3], [1, 4, 6], GLAZED), Cube([-4, 20, -3], [1, 4, 6], GLAZED),
        Cube([-5, 24, -5], [10, 1, 1], GLAZED), Cube([-5, 24, 4], [10, 1, 1], GLAZED),
        Cube([4, 24, -4], [1, 1, 8], GLAZED), Cube([-5, 24, -4], [1, 1, 8], GLAZED),
        # the crack on its flank, glowing with the heat inside (running up onto the shoulder)
        Cube([0.5, 7, -8.02], [6, 8, 0], {"fn": crack(CRACK), "glow": True, "shading": False}),
        Cube([3.5, 15, -7.02], [3, 3, 0], {"fn": crack(CRACK_TOP), "glow": True, "shading": False})])
    # elegant curved handle on its right side
    m.bone("handle", "jug", [-4, 23, 0], cubes=[                       # rises above its root, then sweeps down
        Cube([-6, 22.5, -1], [2, 2, 2], GLAZED), Cube([-8, 23.5, -1], [2, 2, 2], GLAZED),
        Cube([-10, 22.5, -1], [2, 2, 2], GLAZED), Cube([-11, 19.5, -1], [2, 3, 2], GLAZED),
        Cube([-11.5, 13.5, -1], [2, 6, 2], GLAZED), Cube([-11, 11, -1], [2, 3, 2], GLAZED),
        Cube([-9.5, 10, -1], [2, 2, 2], GLAZED)])
    m.bone("spout", "jug", [4.5, 24.5, 0], rotation=[0, 0, -18], cubes=[                     # pinched pouring lip
        Cube([4.5, 24, -1.5], [3, 1, 3], GLAZED), Cube([4.5, 25, -1.5], [3, 1, 1], GLAZED), Cube([4.5, 25, 0.5], [3, 1, 1], GLAZED)])
    m.bone("spout_base", "jug", [4, 23, 0], cubes=[Cube([4, 22, -2], [2, 2, 4], GLAZED)])
    m.bone("cider", "jug", [0, 22, 0], cubes=[Cube([-3, 22, -3], [6, 1, 6], LIQ)])
    # the spirit: a vapour column rising from the neck, a big round head, little hands gripping the rim
    m.bone("spirit", "jug", [0, 22, 0], cubes=[Cube([-2, 21, -2], [4, 9, 4], STEM), Cube([-3, 26.5, -3], [6, 2, 6], STEM)])
    m.bone("head", "spirit", [0, 32, 0], cubes=[
        Cube([-7.5, 29, -4.5], [15, 11, 9], SPIRIT),
        Cube([-6.5, 29, -5.5], [13, 10, 1], SPIRIT), Cube([-6.5, 30, 4.5], [13, 9, 1], SPIRIT),      # rounder face / back
        Cube([7.5, 30.5, -3.5], [1, 8, 7], SPIRIT), Cube([-8.5, 30.5, -3.5], [1, 8, 7], SPIRIT),    # rounder sides
        Cube([-6.5, 28, -3.5], [13, 1, 7], SPIRIT), Cube([-6.5, 40, -3.5], [13, 1, 7], SPIRIT),
        Cube([-4.5, 41, -2.5], [9, 1, 5], SPIRIT),
        # vapour trailing off the sides of the head
        Cube([8.5, 31, -1], [1, 2, 2], SPIRIT), Cube([-9.5, 32, 0], [1, 2, 2], SPIRIT), Cube([5, 27.5, -2], [2, 1, 2], SPIRIT)])
    m.bone("wisp", "head", [0, 42, 0], cubes=[                                  # curling vapour tuft on top
        Cube([-1, 42, -0.5], [2, 2, 1], SPIRIT), Cube([0, 44, -0.5], [3, 1, 1], SPIRIT), Cube([2, 43, -0.5], [1, 1, 1], SPIRIT)])
    for side, s in (("left", 1), ("right", -1)):
        ex = 0.3 if s > 0 else -7.3
        cx = ex + 3.5
        m.bone(f"eye_{side}", "head", [cx, 36, -5.62])
        rows = SWIRL7 if s > 0 else [r[::-1] for r in SWIRL7]
        m.bone(f"swirl_{side}", f"eye_{side}", [cx, 36, -5.62], cubes=[
            Cube([ex, 32.5, -5.62], [7, 7, 0], {"fn": swirl_eye(rows), "glow": True, "shading": False})])
        hx = 2 if s > 0 else -5
        m.bone(f"hand_{side}", "spirit", [2 * s, 28, -1], cubes=[
            Cube([1.5 if s > 0 else -3.5, 25.5, -4], [2, 3, 3], HANDS),                  # arm
            Cube([hx, 24.5, -5.5], [3, 2, 2], HANDS),                                     # hand on the rim
            Cube([hx, 22.5, -5.6], [1, 2, 1], HANDS), Cube([hx + 2, 23, -5.6], [1, 2, 1], HANDS)])  # fingers over the lip
    m.bone("mouth", "head", [0, 30.5, -5.62], cubes=[Cube([-4.5, 29.2, -5.62], [9, 3, 0], {"fn": char_plane(SMILE, EYE_K), "glow": True, "shading": False})])
    m.bone("mouth_open", "head", [0, 31, -5.3], cubes=[Cube([-2.5, 29.1, -5.3], [5, 4, 0], {"fn": char_plane(OPEN, EYE_K), "glow": True, "shading": False})])
    pnt = lambda k: {"fn": steam(seed=k * 2), "shading": False}
    for k, (bone, par, (sx, sy, sz)) in enumerate((("steam1", "jug", (8.5, 26, 0)), ("steam2", "head", (-5, 41, 1)),
                                                     ("steam3", "head", (5, 41, -1)))):
        m.bone(bone, par, [sx, sy, sz], cubes=[Cube([sx - 1.5, sy, sz], [3, 7, 0], pnt(k)), Cube([sx, sy, sz - 1.5], [0, 7, 3], pnt(k))])
    m.pack()
    return m

# ---------------------------------------------------------------- animations
Q = "q.anim_time"
EYES = ("eye_left", "eye_right")
HOVER = 3.5                 # levitation: the jug (foot ring drafted 4 above the ground) floats 7.5 up

def _steam(speed=1.0, height=4.0):
    out = {}
    for k in range(3):
        ph = k * 0.33
        f = round(120 * speed, 3)
        u = f"(({Q}*{round(speed / 3, 4)}+{ph})-math.floor({Q}*{round(speed / 3, 4)}+{ph}))"
        out[f"steam{k + 1}"] = {"position": [f"math.sin({Q}*{f}+{k * 90})*0.6", f"{u}*{height}", 0],
                                "scale": [f"0.5+{u}*0.9", f"0.4+{u}*0.8", f"0.5+{u}*0.9"],
                                "rotation": [0, f"{Q}*{40 + 15 * k}", 0]}
    return out

def _swirl(speed=90):
    return {"swirl_left": {"rotation": [0, 0, f"{Q}*{-speed}"]}, "swirl_right": {"rotation": [0, 0, f"{Q}*{speed}"]}}

def anims(m=None):
    m = m or build()
    a = f"animation.{SID}."
    out = {}
    simmer = {"cider": {"position": [0, f"math.sin({Q}*240)*0.12", 0]}}
    SK = ("steam", "wisp", "mouth", "eye", "swirl")

    # idle: the jug sways a little (tipsy), the spirit billows and leans with a sly grin, fingers drum on the rim
    def idle(t):
        w = math.radians(t * 60)
        sly = lerp_keys([(0, [0, 0]), (2.6, [0, 0]), (3.0, [14, -10]), (4.2, [14, -10]), (4.6, [0, 0]), (6, [0, 0])], t)
        p = {"jug": {"rotation": [0, 0, 2.0 * math.sin(w)]},
             "spirit": {"rotation": [2 * math.sin(2 * w), 0, -4 * math.sin(w + 0.6) + sly[0] * 0.3],
                        "scale": [1 + 0.03 * math.sin(3 * w), 1 - 0.03 * math.sin(3 * w), 1 + 0.03 * math.sin(3 * w)]},
             "head": {"rotation": [-2 + sly[1] * 0.2, 0, 3 * math.sin(w) + sly[0]]},
             "wisp": {"rotation": [0, 0, 10 * math.sin(3 * w)]}}
        for side, s in (("left", 1), ("right", -1)):
            off = 0.0 if s > 0 else 0.5
            tap = max(0.0, math.sin(math.radians((t + off) * 720))) if 0.6 < t < 2.2 else 0.0
            p[f"hand_{side}"] = {"rotation": [-12 * tap, 0, 0]}
        return p
    b = sampled(6, 0.05, lifted(idle, lambda t: bob(t, HOVER, 0.8, 3.0)), loop=True)
    b.update(simmer); b.update(_steam()); b.update(_swirl())
    out[a + "ground_idle"] = {"loop": True, "animation_length": 6, "bones": b}

    # walk: it glides along, leaning into the motion and swaying, the spirit trailing a little behind
    T = 1.6
    def walk(t):
        ph = 2 * math.pi * t / T
        p = {"jug": {"rotation": [6, 0, 5 * math.sin(ph)]},
             "spirit": {"rotation": [-10, 0, -4 * math.sin(ph - 0.7)]},
             "head": {"rotation": [-2, 0, -3 * math.sin(ph - 1.2)]},
             "wisp": {"rotation": [-20, 0, 8 * math.sin(ph - 1.5)]}}
        for side, s in (("left", 1), ("right", -1)):
            p[f"hand_{side}"] = {"rotation": [8 + 4 * math.sin(2 * ph + s), 0, 0]}
        return p
    b = sampled(T, 0.04, lifted(walk, lambda t: bob(t, HOVER + 0.5, 0.6, T / 2)), loop=True)
    b.update(simmer); b.update(_steam(1.5, 3.0)); b.update(_swirl(140))
    out[a + "ground_walk"] = {"loop": True, "animation_length": T, "bones": b}

    # battle: the spirit rises out of the neck and looms forward, hands up like claws, eyes spinning faster
    def battle(t):
        w = math.sin(math.radians(t * 360))
        p = {"spirit": {"position": [0, 1.5 + 0.3 * w, 0], "rotation": [10 + 2 * w, 0, 0], "scale": [1.06, 1.08, 1.06]},
             "head": {"rotation": [-4, 0, 3 * math.sin(math.radians(t * 180))]},
             "jug": {"rotation": [0, 0, 1.5 * math.sin(math.radians(t * 180))]},
             "wisp": {"rotation": [0, 0, 12 * w]}}
        for side, s in (("left", 1), ("right", -1)):
            pw = math.sin(math.radians(t * 360 + (0 if s > 0 else 180)))
            p[f"hand_{side}"] = {"rotation": [-40 - 8 * pw, 0, -s * (60 + 6 * pw)], "scale": [1.15, 1.15, 1.15]}
        return p
    b = sampled(2, 0.05, lifted(battle, lambda t: bob(t, HOVER + 1.0, 0.6, 2.0)), loop=True)
    b.update({"cider": {"position": [0, f"math.sin({Q}*720)*0.2", 0]}})
    b.update(_steam(2.5, 5.0)); b.update(_swirl(240))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 2, "bones": b}

    # cry: the spirit stretches tall, throws its hands up and laughs, a puff of fumes from the spout and the head
    L = 1.6
    def cry(t):
        e = smooth(t / 0.25) if t < 0.25 else (1.0 if t < L - 0.35 else 1 - smooth((t - (L - 0.35)) / 0.35))
        air = math.sin(math.pi * min(1, max(0, (t - 0.1) / 0.4))) if 0.1 < t < 0.5 else 0.0
        on = 1 if 0.12 < t < L - 0.2 else 0
        laugh = math.sin(math.radians(t * 1400)) * e
        p = {"body": {"position": [0, HOVER + 2.0 * air, 0]},
             "spirit": {"scale": [1 - 0.06 * e, 1 + 0.22 * e, 1 - 0.06 * e], "rotation": [-6 * e, 0, 0]},
             "head": {"rotation": [-14 * e + 3 * laugh, 0, 0]},
             "mouth_open": {"position": [0, 0, -0.35 * on]}, "mouth": {"position": [0, 0, 0.5 * on]},
             "cider": {"position": [0, 0.3 * e, 0]}}
        for side, s in (("left", 1), ("right", -1)):
            p[f"hand_{side}"] = {"rotation": [-20 * e, 0, -s * (55 * e + 12 * laugh)], "position": [3.5 * s * e, 0.5 * e, -0.5 * e]}
        for k in range(3):
            u = max(0.0, min(1.0, (t - 0.2 - 0.1 * k) / 0.9))
            p[f"steam{k + 1}"] = {"position": [0, 7 * u, 0], "scale": [0.5 + 1.3 * u] * 3}
        return p
    b = sampled(L, 0.04, cry)
    b.update(_swirl(300))
    out[a + "cry"] = {"animation_length": L, "bones": b}

    # sleep: no more levitation - the jug settles on its foot ring, the spirit slumps over the rim, eyes shut
    sl = {"body": {"position": [0, -4.0, 0]},
          "spirit": {"position": [0, -2.6, 0], "scale": [f"0.82+math.sin({Q}*60)*0.02", f"0.55-math.sin({Q}*60)*0.02", 0.82],
                     "rotation": [6, 0, 0]},
          "head": {"rotation": [8, 0, f"5+math.sin({Q}*45)*2"]},
          "eye_left": {"scale": [1, 0.15, 1]}, "eye_right": {"scale": [1, 0.15, 1]},
          "hand_left": {"rotation": [10, 0, 0]}, "hand_right": {"rotation": [10, 0, 0]},
          "cider": {"position": [0, f"math.sin({Q}*60)*0.08", 0]}}
    st = _steam(0.4, 3.0)
    for k in (2, 3):
        st[f"steam{k}"] = {"scale": 0}
    sl.update(st)
    out[a + "sleep"] = {"loop": True, "animation_length": 6, "bones": sl}

    out[a + "blink"] = {"animation_length": 0.2, "bones": {e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.15, 1], "0.2": [1, 1, 1]}}
                                                            for e in EYES}}

    # faint: dizzy wobble, the jug tips over on its spout side, the spirit spills out limp and dims
    k0 = {"body": {"rotation": [0, 0, 0]}}
    k1 = {"body": {"rotation": [0, 0, -10]}, "spirit": {"rotation": [-8, 0, 14]}, "head": {"rotation": [0, 0, 10]}}
    k2 = {"body": {"rotation": [0, 0, 9]}, "spirit": {"rotation": [6, 0, -16]}, "head": {"rotation": [0, 0, -12]}}
    k3 = {"body": {"rotation": [0, 0, 84]}, "spirit": {"rotation": [10, 0, -30]},
          "head": {"rotation": [10, 0, -20]}, "hand_left": {"rotation": [30, 0, 20]}, "hand_right": {"rotation": [30, 0, -10]}}
    k4 = {"body": {"rotation": [0, 0, 80]}, "spirit": {"rotation": [12, 0, -36]},
          "head": {"rotation": [12, 0, -24]}, "hand_left": {"rotation": [35, 0, 25]}, "hand_right": {"rotation": [35, 0, -12]}}
    fb = pose_sequence(m, [(0, k0), (0.35, k1), (0.75, k2), (1.4, k3), (1.8, k4), (2.4, k3)], length=2.4,
                       skip=tuple(b.name for b in m.bones if b.name.startswith(("steam", "wisp"))))
    lift_track(fb, lambda t: (HOVER + 4.0) * (1 - smooth(t / 1.2)))          # drops out of the air
    for e in EYES:
        fb[e] = keys(scale={0: [1, 1, 1], 1.2: [1, 1, 1], 1.45: [1, 0.15, 1], 2.4: [1, 0.15, 1]})
    fb["spirit"].update(keys(scale={0: [1, 1, 1], 1.2: [1, 1, 1], 1.8: [0.82, 0.8, 0.82], 2.4: [0.8, 0.78, 0.8]}))
    for k in range(3):
        fb[f"steam{k + 1}"] = {"scale": 0}
    fb.update(_swirl(400))
    out[a + "faint"] = {"animation_length": 2.4, "bones": fb}

    # portrait: the face turned a little toward the viewer, a sly look
    pb = {"head": {"rotation": [0, -12, 4]}, "spirit": {"rotation": [0, 0, 0]}}
    pb.update(simmer); pb.update(_steam()); pb.update(_swirl())
    out[a + "portrait"] = {"loop": True, "animation_length": 6, "bones": pb}
    return finalize(out)

def poser():
    from templates import poser as make_poser
    ps = make_poser(SID, portrait=(1.4, [-0.1, -0.6, 0]), profile=(0.8, [0, 0.4, 0]))
    ps["poses"]["standing"]["poseTypes"] = ["STAND", "NONE", "FLOAT"]
    ps["poses"] = {"portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "isBattle": False,
                                "animations": [f"q.bedrock('{SID}', 'portrait')"],
                                "quirks": [f"q.bedrock_quirk('{SID}', 'blink')"]}, **ps["poses"]}
    return ps
