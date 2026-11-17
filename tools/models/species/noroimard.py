# -*- coding: utf-8 -*-
"""#1041 Noroimard — homard géant des grands fonds & guerrier viking (Eau / Acier).
A massive, squat living fortress anchored to the seabed: a deep night-blue, almost metallic shell, rough with
limestone crust, sea patina and acorn barnacles like the breakwater blocks of the Norman coast; small piercing eyes
glowing like embers under a heavy brow; a thick rostrum like a rocky spur; short, thick antennae armoured at the
base; short, thick legs planted wide. Its right claw is a Viking war axe (a bearded blade of forged steel with runes,
the movable finger hooked over it); its left claw is a huge crusher it raises like a shield to parry.
Rideable: one rider on the carapace, on land (cobblemon:land/horse) and under water (cobblemon:liquid/submarine).
Shiny: a calico lobster (orange mottled with near-black), ice-blue eyes."""
from modelgen import Model, Cube, rgb
from crustacean import (shell, stripes, solid, serrated, ember_eye, barnacle, blade, shield_face, fan, CLeg, claw, antenna,
                        abdomen, crust_anims, crust_poser, SIDES)
from bovine import finalize

SID, DEX = "noroimard", 1041
FRAME_BONES = ("head", "eye_left", "eye_right", "rostrum")
HEIGHT_SKIP = ("antenna", "arm_", "wrist_", "claw_", "pincer_")     # height to the top of the carapace
SCALE_BOOST = 1.0                    # already a giant: 1.3 m tall is ~3.5 blocks long, roomy enough to ride

PAL = {
    "shell": rgb("#1A2A4C"), "shell_joint": rgb("#0A1228"), "shell_sheen": rgb("#55779F"),
    "crust": rgb("#9C9A90"), "patina": rgb("#3F6A5C"), "barnacle": rgb("#D6D1C4"), "barnacle_dark": rgb("#34312C"),
    "tooth": rgb("#9CB0C8"), "tip": rgb("#0A1020"), "mouth": rgb("#0C1430"), "ant_a": rgb("#24395F"), "ant_b": rgb("#3C5A86"),
    "eye_glow": rgb("#FF5A18"), "eye_glow_hot": rgb("#FFD27A"), "eye_glow_rim": rgb("#7A1204"), "eye_slit": rgb("#2A0603"),
    "blade": rgb("#A3B4C8"), "blade_dark": rgb("#5E6E86"), "blade_edge": rgb("#F2F8FF"), "rune": rgb("#22324E"),
}
SHINY = dict(PAL, **{
    "shell": rgb("#D2742A"), "shell_joint": rgb("#2A1A12"), "shell_sheen": rgb("#F2A860"),
    "crust": rgb("#3A2A22"), "patina": rgb("#7A4A26"), "tooth": rgb("#F6D2A2"), "ant_a": rgb("#C2601E"), "ant_b": rgb("#3A2418"),
    "eye_glow": rgb("#5ADCFF"), "eye_glow_hot": rgb("#E6FBFF"), "eye_glow_rim": rgb("#164E8A"), "eye_slit": rgb("#04101E"),
    "blade": rgb("#C8CCD2"), "blade_dark": rgb("#7A808A"), "rune": rgb("#4A2A16"),
})

CRUST = ("crust", 0.75, 0.5)
SHELL = shell(seed=7, crust=CRUST, barn="barnacle")
SHELL_X = shell(seed=9, axis="x", crust=CRUST)
SMOOTH = shell(seed=11)
LEG_PAINT = {"merus": SHELL_X, "foot": SHELL_X, "coxa": {"base": "shell_joint"}, "tip": {"fn": solid("tip")}}
BARN = {"fn": barnacle}
PIVOT = (0, 7, 0)
DROP = -2.0                          # squat: the whole shell sits 2 lower than drafted (legs stay planted)
LEG_Z = (-6, -3, 0, 3)
FOOT_Z = (-8, -3.5, 1, 5.5)
LEGS = [CLeg(i, side, s, (7 * s, 9 + DROP, LEG_Z[i]), (13 * s, FOOT_Z[i]), 4, 7, t1=3, t2=2, paints=LEG_PAINT)
        for side, s in SIDES for i in range(4)]
SEAT = (0, 19 + DROP, -1)

def build():
    m = Model(SID, DEX, (256, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 11, -1], cubes=[
        Cube([-7, 7, -9], [14, 10, 17], SHELL),                                    # fortress carapace
        Cube([-6, 17, -8], [12, 2, 15], SHELL),                                    # domed back
        Cube([-6, 6, -8], [12, 1, 15], {"base": "shell_joint"}),                   # underside
        Cube([7, 9, -7], [1, 6, 13], SHELL), Cube([-8, 9, -7], [1, 6, 13], SHELL),  # flank ridges
        # rocky spikes along the back ridge and barnacles
        Cube([-0.5, 19, -6], [1, 1, 2], SHELL), Cube([-0.5, 19, 2], [1, 1, 2], SHELL),
        Cube([3, 19, -3], [2, 1, 2], BARN), Cube([-5, 19, 1], [2, 1, 2], BARN), Cube([4, 17.5, 4], [1, 1, 1], BARN),
        Cube([-6.5, 16.5, -6], [1, 1, 1], BARN), Cube([7.5, 13, 0], [1, 1, 1], BARN), Cube([-8.5, 12, 3], [1, 1, 1], BARN),
        Cube([-3, 19, -7], [1, 1, 1], BARN)] +
        # battlements along both top edges: a living fortress
        [Cube([sx * 5.5 - 0.5, 19, zc], [1, 1, 1], SHELL) for sx in (1, -1) for zc in (-7.5, -4.5, -1.5, 1.5, 4.5)])
    m.bone("locator_seat_1", "torso", list(SEAT), locators={"seat_1": list(SEAT)})
    m.bone("head", "torso", [0, 12, -9], cubes=[
        Cube([-5, 7.5, -14], [10, 7, 5], SHELL),
        Cube([-1.5, 14.5, -14.5], [3, 1, 4], SHELL),                               # brow ridge over the nose
        Cube([-3, 7, -14.5], [6, 2, 1], {"base": "mouth"}),                        # mouthparts
        Cube([-4, 6.5, -13], [8, 1, 3], {"base": "shell_joint"})])
    m.bone("rostrum", "head", [0, 13, -14], rotation=[8, 0, 0], cubes=[            # rocky spur
        Cube([-1.5, 11.5, -19], [3, 3, 5], SHELL), Cube([-1, 12, -21], [2, 2, 2], SHELL)])
    for side, s in SIDES:
        # deep armoured socket, the ember eye set in it, and a heavy brow slanting down to the nose (frown)
        m.bone(f"stalk_{side}", "head", [3 * s, 13, -14], cubes=[
            Cube([3 * s - 2, 12, -14.4], [4, 3, 1], {"base": "shell_joint"})])
        m.bone(f"eye_{side}", f"stalk_{side}", [3 * s, 13.5, -14.6], cubes=[
            Cube([3 * s - 1.5, 12.5, -15.2], [3, 2, 2], {"fn": ember_eye(inner_left=s > 0), "glow": True, "shading": False})])
        bx = 1.5 if s > 0 else -5.5
        m.bone(f"brow_{side}", "head", [1.5 * s, 14.8, -14.5], rotation=[0, 0, -16 * s], cubes=[
            Cube([bx, 14.5, -15.8], [4, 1, 5], SHELL)])
        antenna(m, side, s, parent="head", base=(2.5 * s, 10.5, -14), segs=[3, 3, 3, 3], thick=[3, 2, 2, 1],
                paint=[SHELL, {"fn": stripes()}, {"fn": stripes()}, {"fn": stripes()}],
                rest=[(-25, -30, 0), (-5, -25, 0), (4, -28, 0), (6, -25, 0)])
    # right: Viking war-axe claw (haft + bearded blade, hooked movable finger); left: huge shield crusher
    xa = -6
    claw(m, "right", -1, parent="torso", shoulder=(xa, 12, -11), arm=(3, 3, 5), wrist=(3, 3, 4), palm=(3, 3, 7),
         finger=(2, 2, 2), pincer=(2, 2, 4), arm_rot=(-30, 55, 0), wrist_rot=(0, -30, 0), claw_rot=(-15, -10, 0),
         paints={"arm": SHELL, "wrist": SHELL, "palm": SMOOTH, "finger": SMOOTH, "pincer": {"fn": serrated(inner="west")}},
         extra_palm=[Cube([xa - 2.5, 4, -29], [1, 15, 9], {"fn": blade()}),       # bearded axe blade (outer side)
                     Cube([xa - 2, 9.5, -22], [1, 5, 2], {"fn": solid("rune")})])   # socket binding
    claw(m, "left", 1, parent="torso", shoulder=(6, 12, -11), arm=(4, 4, 5), wrist=(4, 4, 4), palm=(8, 7, 8),
         finger=(4, 4, 4), pincer=(4, 3, 4), arm_rot=(-20, -55, 0), wrist_rot=(0, 35, 0), claw_rot=(12, 10, 0),
         paints={"arm": SHELL, "wrist": SHELL, "palm": SHELL, "finger": {"fn": serrated(inner="west", tooth="crust")},
                 "pincer": {"fn": serrated(inner="east", tooth="crust")}},
         extra_palm=[Cube([6, 15.5, -25], [2, 1, 2], BARN), Cube([3, 15.5, -22], [1, 1, 1], BARN),
                     Cube([10, 8, -28], [1, 9, 9], {"fn": shield_face()})])                 # round shield face
    abdomen(m, parent="torso", start=(0, 12, 8), segs=[(12, 7, 3), (11, 6, 3), (10, 5, 3), (9, 4, 3)],
            paints=[SHELL], fan_size=(12, 5), fan_paint={"fn": fan()}, rest=-6)
    legs = {b for lg in LEGS for b in lg.bones}
    for b in m.bones:                                 # lower the shell (drafted 2 higher), not the planted legs
        if b.parent is None or b.name in legs or b.name in ("body", "locator_seat_1"):
            continue
        b.pivot[1] += DROP
        for c in b.cubes:
            c.origin[1] += DROP
    m.pack()
    return m

ANT = {side: [f"antenna_{side}{k}" for k in range(1, 5)] for side, _ in SIDES}
TAIL = ["tail1", "tail2", "tail3", "tail4", "tail_fan"]

def anims(m=None):
    m = m or build()
    out = crust_anims(SID, m, LEGS, pivot=PIVOT, cfg=dict(
        scale=1.2, body_h=5.0, antennae=ANT, tail=TAIL, snap=10, heavy=True, roll=70, battle_tail=4,
        portrait_claws=(25, -70, 0), portrait_yaw=25, portrait_ant=(-25, -25),
        walk=dict(T=1.4, stride=5.0, lift=2.2, yaw=0.0, stance=0.6, bob=0.25, ripple=0.04),
        battle=dict(dy=-1.2, pitch=-4, arm=(-28, 14, 0), open_=16),
        cry=dict(L=2.0, rear=-10, dy=0.8, arm=(-60, 20, 0), open_=24, clack=((0.7, 0.9), (1.05, 1.25))),
        sleep=dict(spread=1.15), swim_T=1.3))
    return finalize(out)

def poser():
    return crust_poser(SID, portrait=(1.2, [-0.6, 0.6, 0]), profile=(0.6, [0, 0.7, 0]), ride=True)
