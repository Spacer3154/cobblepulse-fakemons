# -*- coding: utf-8 -*-
"""#1046 Bolvados — bolée de cidre normande habitée par un esprit chaleureux (Eau / Feu).
A small footed stoneware cider bowl in warm terracotta, hand-painted with a blue wave band and dots; warm golden cider
shimmers and simmers inside (bubbles, wisps of apple-scented steam); two big mischievous blue eyes and a small smile
on the front; tiny hands of the same golden liquid slip over the rim to show its feelings. Shy but playful: it floats
above the ground, peeks, bobs along and puffs steam when excited; asleep, it settles on its foot ring. Shiny: Rouen faience (white glaze, cobalt decoration) holding
a ruby pommeau."""
import math
from modelgen import Model, Cube, rgb
from biped import keys, kf, smooth, pose_sequence
from bovine import sampled, finalize, lerp_keys
from vessel import stoneware, band_motif, cider, steam, char_plane, EYE_K, settled, bob, lifted, lift_track

SID, DEX = "bolvados", 1046
FRAME_BONES = ("head",)
HEIGHT_SKIP = ("steam", "bubble")

PAL = {
    "clay": rgb("#C8784A"), "clay_dark": rgb("#8E4A2A"), "clay_light": rgb("#E3A274"), "blue": rgb("#2F5FA8"),
    "glaze": rgb("#B2603A"), "glaze_light": rgb("#D68A5A"),
    "cider": rgb("#F2B53A"), "cider_light": rgb("#FFE38A"), "cider_dark": rgb("#C9821E"),
    "steam": rgb("#F4ECDC"), "steam_light": rgb("#FFFFFF"),
    "eye_white": rgb("#FFFFFF"), "eye_iris": rgb("#4FA8F0"), "eye_iris_light": rgb("#A8DEFF"), "eye": rgb("#10223E"),
    "eye_shine": rgb("#FFFFFF"), "eye_ring": rgb("#1E3E70"), "mouth": rgb("#4A2412"), "mouth_glow": rgb("#FFB63A"),
    "tooth": rgb("#FFFFFF"), "eye_hot": rgb("#FFE38A"), "eye_glow": rgb("#FFB63A"), "eye_dark": rgb("#1E3E70"),
}
SHINY = dict(PAL, **{
    "clay": rgb("#EDE7DC"), "clay_dark": rgb("#B9B2A6"), "clay_light": rgb("#FFFFFF"), "blue": rgb("#1E3F9A"),
    "glaze": rgb("#E4DED2"), "glaze_light": rgb("#FFFFFF"),
    "cider": rgb("#C8323E"), "cider_light": rgb("#FF8A86"), "cider_dark": rgb("#801C26"),
    "eye_iris": rgb("#2E6FD8"), "eye_iris_light": rgb("#8FC0FF"), "mouth_glow": rgb("#E8505A"),
})

BOWL = stoneware(seed=2, motif=band_motif(4.5, 9.5, period=6.0, amp=1.0))
PLAIN = stoneware(seed=3)
FOOT = stoneware(seed=4, base="clay_dark", dark="clay_dark", light_key="clay")
RIM = stoneware(seed=5, base="clay_light", dark="clay", light_key="clay_light")
LIQ = {**cider(), "glow": True, "shading": False}
HAND = {**cider(swirl=False), "glow": True, "shading": False}
EYE = [".BBB.", "BSSEB", "BSEEB", "BEEEB", ".LLL."]
SMILE = ["M.....M", ".M...M.", "..MMM.."]
OPEN = ["..MMM..", ".MQQQM.", ".MQQQM.", "..MMM.."]

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, 0, 0])
    m.bone("head", "body", [0, 1, 0], cubes=[
        Cube([-5, 0, -5], [10, 1, 10], FOOT),                                      # foot ring
        Cube([-6.5, 1, -5.5], [13, 1, 11], PLAIN), Cube([-5.5, 1, -6.5], [11, 1, 13], PLAIN),
        Cube([-8, 2, -6], [16, 2, 12], PLAIN), Cube([-6, 2, -8], [12, 2, 16], PLAIN),
        # round-ish (octagonal) painted belly
        Cube([-9.5, 4, -7.5], [19, 6, 15], BOWL), Cube([-7.5, 4, -9.5], [15, 6, 19], BOWL),
        # rim following the octagon
        Cube([-7.5, 10, -9.5], [15, 2, 1], RIM), Cube([-7.5, 10, 8.5], [15, 2, 1], RIM),
        Cube([8.5, 10, -7.5], [1, 2, 15], RIM), Cube([-9.5, 10, -7.5], [1, 2, 15], RIM)] +
        [Cube([7.5 * sx - (1 if sx < 0 else 0), 10, 7.5 * sz - (1 if sz < 0 else 0)], [1, 2, 1], RIM)
         for sx in (1, -1) for sz in (1, -1)])
    m.bone("cider", "head", [0, 10.5, 0], cubes=[Cube([-8.5, 10, -7.5], [17, 1, 15], LIQ),
                                                 Cube([-7.5, 10.01, -8.5], [15, 1, 17], LIQ)])
    for k, (bx, bz) in enumerate(((-3.5, -2), (3, 2.5), (0.5, -5))):           # bubbles
        m.bone(f"bubble{k + 1}", "cider", [bx, 11, bz], cubes=[Cube([bx - 0.5, 10.6, bz - 0.5], [1, 1, 1], HAND)])
    for k, (sx, sz) in enumerate(((-3, 0), (3.5, -2), (0, 3.5))):              # steam wisps (crossed planes)
        pnt = {"fn": steam(seed=k * 2), "shading": False}
        m.bone(f"steam{k + 1}", "head", [sx, 11.5, sz], cubes=[
            Cube([sx - 1.5, 11.5, sz], [3, 7, 0], pnt), Cube([sx, 11.5, sz - 1.5], [0, 7, 3], pnt)])
    for side, s in (("left", 1), ("right", -1)):
        ex = 0.5 if s > 0 else -5.5
        m.bone(f"eye_{side}", "head", [s * 3, 7, -9.55], cubes=[
            Cube([ex, 4.5, -9.55], [5, 5, 0], {"fn": char_plane(EYE, EYE_K)})])
        # tiny hands of cider slipping over the rim
        hx = 9.5 if s > 0 else -12.5
        m.bone(f"hand_{side}", "head", [9 * s, 11.5, -1.5], rotation=[0, 0, -10 * s], cubes=[
            Cube([hx, 9, -3], [3, 4, 3], HAND),
            Cube([hx + 1, 8, -2.5], [1, 1, 1], HAND), Cube([hx + 1, 8, -0.5], [1, 1, 1], HAND)])
    m.bone("mouth", "head", [0, 3.5, -8.06], cubes=[Cube([-3.5, 2, -8.06], [7, 3, 0], {"fn": char_plane(SMILE, EYE_K)})])
    m.bone("mouth_open", "head", [0, 3, -7.8], cubes=[Cube([-3.5, 1.5, -7.8], [7, 4, 0], {"fn": char_plane(OPEN, EYE_K)})])
    m.pack()
    return m

# ---------------------------------------------------------------- animations
Q = "q.anim_time"
HOVER = 6.0                 # levitation height (model units)

def _steam(speed=1.0, height=4.0):
    out = {}
    for k in range(3):
        ph = k * 0.33
        f = round(120 * speed, 3)                                               # one rise per 3 s at speed 1
        u = f"(({Q}*{round(speed / 3, 4)}+{ph})-math.floor({Q}*{round(speed / 3, 4)}+{ph}))"
        out[f"steam{k + 1}"] = {"position": [f"math.sin({Q}*{f}+{k * 90})*0.6", f"{u}*{height}", 0],
                                "scale": [f"0.5+{u}*0.9", f"0.4+{u}*0.8", f"0.5+{u}*0.9"],
                                "rotation": [0, f"{Q}*{40 + 15 * k}", 0]}
    return out

def _bubbles(rate=1.0):
    out = {}
    for k in range(3):
        u = f"(({Q}*{round(rate * (0.7 + 0.25 * k), 3)}+{0.37 * k})-math.floor({Q}*{round(rate * (0.7 + 0.25 * k), 3)}+{0.37 * k}))"
        out[f"bubble{k + 1}"] = {"scale": f"math.max(0,math.sin({u}*180))*1.2", "position": [0, f"{u}*0.6", 0]}
    return out

def anims(m=None):
    m = m or build()
    a = f"animation.{SID}."
    out = {}
    simmer = {"cider": {"position": [0, f"math.sin({Q}*240)*0.12", 0], "rotation": [0, f"{Q}*12", 0]}}

    # idle: shy peeks - looks left / right, hands slip over the rim and wave, a little wiggle; simmering cider
    def idle(t):
        look = lerp_keys([(0, [0, 0]), (1.0, [0, 0]), (1.3, [0, 14]), (2.6, [0, 14]), (2.9, [0, -12]), (4.0, [0, -12]),
                          (4.3, [0, 0]), (8, [0, 0])], t)
        wig = math.exp(-((t - 5.2) / 0.25) ** 2)
        p = {"head": {"rotation": [2 * math.sin(math.radians(t * 90)), look[1], 6 * wig * math.sin(math.radians(t * 1440))]},
             "body": {"scale": [1 + 0.02 * math.sin(math.radians(t * 180)), 1 - 0.02 * math.sin(math.radians(t * 180)),
                                1 + 0.02 * math.sin(math.radians(t * 180))]}}
        for side, s in (("left", 1), ("right", -1)):
            peek = lerp_keys([(0, [0]), (0.4, [1]), (3.4, [1]), (3.8, [0]), (6.0, [0]), (6.4, [1]), (8, [1])], t)[0]
            wave = math.sin(math.radians(t * 540)) * (1 if (s > 0 and 6.6 < t < 7.6) else 0)
            p[f"hand_{side}"] = {"rotation": [0, 0, s * (-10 - 30 * wave)], "position": [0, -3 * (1 - peek), 0],
                                 "scale": [1, 0.4 + 0.6 * peek, 1]}
        return p
    SK = ("steam", "bubble", "mouth", "eye")
    b = sampled(8, 0.05, lifted(settled(m, idle, SK), lambda t: bob(t, HOVER, 0.8, 4.0)), loop=True)
    b.update(simmer); b.update(_steam()); b.update(_bubbles())
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": b}

    # walk: it bobs along through the air, leaning into the motion and rocking, hands trailing on the rim
    T = 1.2
    def hop(t):
        ph = 2 * math.pi * t / T
        p = {"body": {"rotation": [8, 0, 5 * math.sin(ph)],
                      "scale": [1 - 0.03 * math.sin(2 * ph), 1 + 0.04 * math.sin(2 * ph), 1 - 0.03 * math.sin(2 * ph)]},
             "head": {"rotation": [0, 4 * math.sin(ph + 0.8), 0]},
             "cider": {"position": [0, 0.1 * math.sin(2 * ph), 0], "rotation": [-5, 0, -3 * math.sin(ph - 0.6)]}}
        for side, s in (("left", 1), ("right", -1)):
            p[f"hand_{side}"] = {"rotation": [12, 0, s * (-20 + 10 * math.sin(ph + s))]}
        return p
    b = sampled(T, 0.04, lifted(hop, lambda t: bob(t, HOVER + 0.5, 0.9, T / 2)), loop=True)
    b.update(_steam(1.5, 3.0)); b.update(_bubbles(2.0))
    out[a + "ground_walk"] = {"loop": True, "animation_length": T, "bones": b}

    # battle: leans in, hands raised like little fists, cider boiling, quick steam puffs
    def battle(t):
        w = math.sin(math.radians(t * 360))
        p = {"head": {"rotation": [8 + 2 * w, 0, 3 * math.sin(math.radians(t * 180))]},
             "body": {"position": [0, 0.3 * max(0, w), 0]}}
        for side, s in (("left", 1), ("right", -1)):
            pw = math.sin(math.radians(t * 360 + (0 if s > 0 else 180)))
            p[f"hand_{side}"] = {"rotation": [-20, 0, s * (-55 - 15 * pw)], "position": [0, 0.6, 0]}
        return p
    b = sampled(2, 0.05, lifted(settled(m, battle, SK), lambda t: bob(t, HOVER + 1.0, 0.5, 1.0)), loop=True)
    b.update({"cider": {"position": [0, f"math.sin({Q}*720)*0.2", 0]}})
    b.update(_steam(2.5, 5.0)); b.update(_bubbles(3.0))
    out[a + "battle_idle"] = {"loop": True, "animation_length": 2, "bones": b}

    # cry: a happy little hop, mouth opens, hands up, a burst of steam
    L = 1.2
    def cry(t):
        e = smooth(t / 0.2) if t < 0.2 else (1.0 if t < L - 0.3 else 1 - smooth((t - (L - 0.3)) / 0.3))
        air = math.sin(math.pi * min(1, max(0, (t - 0.15) / 0.45))) if 0.15 < t < 0.6 else 0.0
        p = {"body": {"position": [0, HOVER + 2.5 * air, 0], "scale": [1 - 0.05 * air, 1 + 0.1 * air, 1 - 0.05 * air]},
             "head": {"rotation": [-10 * e, 0, 0]},
             "mouth_open": {"position": [0, 0, -0.35 * (1 if 0.1 < t < L - 0.15 else 0)]},
             "mouth": {"position": [0, 0, 0.5 * (1 if 0.1 < t < L - 0.15 else 0)]},
             "cider": {"position": [0, 0.3 * e, 0]}}
        for side, s in (("left", 1), ("right", -1)):
            p[f"hand_{side}"] = {"rotation": [0, 0, s * (-10 - 70 * e + 10 * math.sin(math.radians(t * 900)))],
                                 "position": [0, 0.8 * e, 0]}
        for k in range(3):
            u = max(0.0, min(1.0, (t - 0.2 - 0.08 * k) / 0.8))
            p[f"steam{k + 1}"] = {"position": [0, 7 * u, 0], "scale": [0.5 + 1.2 * u] * 3}
        return p
    out[a + "cry"] = {"animation_length": L, "bones": sampled(L, 0.04, cry)}

    # sleep: no more levitation - it settles on its foot ring, eyes closed, hands tucked in, slow steam
    sl = {"head": {"rotation": [f"4+math.sin({Q}*45)*1.5", 0, f"6+math.sin({Q}*30)*1"]}, "body": {"position": [0, 1.1, 0]},
          "eye_left": {"scale": [1, 0.15, 1]}, "eye_right": {"scale": [1, 0.15, 1]},
          "hand_left": {"position": [0, -3, 0], "scale": [1, 0.4, 1]},
          "hand_right": {"position": [0, -3, 0], "scale": [1, 0.4, 1]},
          "cider": {"position": [0, f"math.sin({Q}*60)*0.08", 0]}}
    sl.update(_steam(0.4, 3.0))
    out[a + "sleep"] = {"loop": True, "animation_length": 6, "bones": sl}

    out[a + "blink"] = {"animation_length": 0.2, "bones": {e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.15, 1], "0.2": [1, 1, 1]}}
                                                            for e in ("eye_left", "eye_right")}}

    # faint: wobbles, tips over onto its side, cider sloshes, hands go limp, eyes shut
    k0 = {"head": {"rotation": [0, 0, 0]}}
    k1 = {"head": {"rotation": [-10, 0, 12]}, "hand_left": {"rotation": [0, 0, -60]}, "hand_right": {"rotation": [0, 0, 60]}}
    k2 = {"head": {"rotation": [6, 0, -14]}, "hand_left": {"rotation": [0, 0, -20]}, "hand_right": {"rotation": [0, 0, 40]}}
    k3 = {"head": {"rotation": [10, 15, 82]}, "hand_left": {"rotation": [0, 0, 30], "position": [0, -1, 0]},
          "hand_right": {"rotation": [0, 0, 10], "position": [0, -1, 0]}, "cider": {"rotation": [0, 0, -40], "position": [-1, -0.5, 0]}}
    k4 = {"head": {"rotation": [10, 15, 78]}, "hand_left": {"rotation": [0, 0, 40], "position": [0, -1.2, 0]},
          "hand_right": {"rotation": [0, 0, 15], "position": [0, -1.2, 0]}, "cider": {"rotation": [0, 0, -35], "position": [-1, -0.6, 0]}}
    fb = pose_sequence(m, [(0, k0), (0.35, k1), (0.75, k2), (1.4, k3), (1.8, k4), (2.4, k3)], length=2.4)
    lift_track(fb, lambda t: HOVER * (1 - smooth(t / 1.2)))                    # drops out of the air
    for e in ("eye_left", "eye_right"):
        fb[e] = keys(scale={0: [1, 1, 1], 0.35: [1, 0.5, 1], 0.6: [1, 1, 1], 1.3: [1, 1, 1], 1.5: [1, 0.15, 1], 2.4: [1, 0.15, 1]})
    for k in range(3):
        fb[f"steam{k + 1}"] = {"scale": 0}
    out[a + "faint"] = {"animation_length": 2.4, "bones": fb}

    # portrait / summary: resting pose, simmering
    pb = {"head": {"rotation": [0, -8, 0]}}
    pb.update(simmer); pb.update(_steam()); pb.update(_bubbles())
    out[a + "portrait"] = {"loop": True, "animation_length": 6, "bones": pb}
    return finalize(out)

def poser():
    from templates import poser as make_poser
    ps = make_poser(SID, portrait=(1.5, [-0.1, -0.2, 0]), profile=(1.0, [0, 0.25, 0]))
    ps["poses"]["standing"]["poseTypes"] = ["STAND", "NONE", "FLOAT"]
    ps["poses"] = {"portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "isBattle": False,
                                "animations": [f"q.bedrock('{SID}', 'portrait')"],
                                "quirks": [f"q.bedrock_quirk('{SID}', 'blink')"]}, **ps["poses"]}
    return ps
