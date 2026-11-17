# -*- coding: utf-8 -*-
"""#1040 Homarbleu — homard bleu du Cotentin (Eau / Acier).
A small, compact, lively young lobster that trots sideways over sand and rocks: an electric-blue satin shell with
darker joints between the segments, big curious eyes on stalks ringed in deep navy, long thin antennae banded pale
blue and white that sway like seaweed, fine walking legs with small neat claw tips, and medium claws already
asymmetric - a broader crusher (left) and a slimmer cutter (right) - both with toothed edges.
Shiny: the very rare yellow lobster."""
from modelgen import Model, Cube, rgb
from crustacean import (shell, stripes, solid, serrated, eye_ball, fan, CLeg, claw, antenna, abdomen, crust_anims,
                        crust_poser, SIDES)
from bovine import finalize

SID, DEX = "homarbleu", 1040
FRAME_BONES = ("head", "eye_left", "eye_right", "stalk_left", "stalk_right")
HEIGHT_SKIP = ("antenna",)

PAL = {
    "shell": rgb("#1F6FEA"), "shell_joint": rgb("#0B3D9C"), "shell_sheen": rgb("#86C8FF"),
    "ant_a": rgb("#9FD8FF"), "ant_b": rgb("#FFFFFF"), "tooth": rgb("#D2EAFF"), "tip": rgb("#0A2A6A"),
    "mouth": rgb("#0E3474"),
    "eye_ring": rgb("#0A1838"), "eye_white": rgb("#F4FAFF"), "eye": rgb("#08101E"), "eye_shine": rgb("#FFFFFF"),
    "eye_iris": rgb("#3AA4FF"), "patina": rgb("#2A5A8A"),
}
SHINY = dict(PAL, **{
    "shell": rgb("#F2B21E"), "shell_joint": rgb("#B26A0A"), "shell_sheen": rgb("#FFE58A"),
    "ant_a": rgb("#FFD86A"), "ant_b": rgb("#FFFFFF"), "tooth": rgb("#FFF2C2"), "tip": rgb("#7A3E06"), "mouth": rgb("#9A5408"),
    "eye_iris": rgb("#FFB020"),
})

SHELL = shell(seed=3)
SHELL_X = shell(seed=5, axis="x")
LEG_PAINT = {"merus": SHELL_X, "foot": SHELL_X, "coxa": {"base": "shell_joint"}, "tip": {"fn": solid("tip")}}
PIVOT = (0, 5, -1)
LEG_Z = (-4.5, -2.5, -0.5, 1.5)
FOOT_Z = (-5.5, -2.5, 0.5, 3.5)
LEGS = [CLeg(i, side, s, (3 * s, 5, LEG_Z[i]), (7.5 * s, FOOT_Z[i]), 4, 5, paints=LEG_PAINT)
        for side, s in SIDES for i in range(4)]

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    m.bone("torso", "body", [0, 6, -2], cubes=[
        Cube([-3, 4, -6], [6, 5, 8], SHELL),                                       # carapace
        Cube([-2, 9, -5], [4, 1, 6], SHELL),                                       # rounded back
        Cube([-2.5, 3.5, -5.5], [5, 1, 7], {"base": "shell_joint"})])              # underside
    m.bone("head", "torso", [0, 7, -6], cubes=[
        Cube([-2.5, 5, -9], [5, 4, 3], SHELL),
        Cube([-0.5, 8, -11], [1, 1, 2], SHELL),                                    # little rostrum
        Cube([-1.5, 4.5, -9.5], [3, 1, 1], {"base": "mouth"})])                    # mouthparts
    for side, s in SIDES:
        m.bone(f"stalk_{side}", "head", [1.5 * s, 8.5, -8.5], rotation=[-10, 0, 0], cubes=[
            Cube([1.5 * s - 0.5, 8.5, -9], [1, 2, 1], SHELL)])
        m.bone(f"eye_{side}", f"stalk_{side}", [2.6 * s, 12.5, -9], cubes=[
            Cube([2.6 * s - 2.5, 10, -11], [5, 5, 4], {"fn": eye_ball(inner_left=s > 0)})])
        antenna(m, side, s, parent="head", base=(1.2 * s, 6.5, -9), segs=[3, 3, 3, 3, 3, 3], thick=1,
                paint={"fn": stripes()}, rest=[(-28, -35, 0), (-4, -22, 0), (2, -26, 0), (3, -28, 0), (3, -28, 0), (2, -26, 0)])
        m.bone(f"antennule_{side}", "head", [0.6 * s, 6, -9], rotation=[-15, -15 * s, 0], cubes=[
            Cube([0.6 * s - 0.5, 5.5, -12], [1, 1, 3], {"fn": stripes()})])
    # claws: crusher on the left (broader), cutter on the right (slimmer), both toothed
    claw(m, "left", 1, parent="torso", shoulder=(2.5, 6, -7), arm=(2, 2, 3), wrist=(2, 2, 2), palm=(4, 3, 5),
         finger=(2, 2, 3), pincer=(2, 2, 3), arm_rot=(8, -35, 0), wrist_rot=(0, 40, 0), claw_rot=(6, 8, 0),
         paints={"arm": SHELL, "wrist": SHELL, "palm": SHELL, "finger": {"fn": serrated(inner="west")},
                 "pincer": {"fn": serrated(inner="east")}})
    claw(m, "right", -1, parent="torso", shoulder=(-2.5, 6, -7), arm=(2, 2, 3), wrist=(2, 2, 2), palm=(3, 2, 5),
         finger=(1, 2, 4), pincer=(1, 2, 4), arm_rot=(8, 35, 0), wrist_rot=(0, -40, 0), claw_rot=(6, -8, 0),
         paints={"arm": SHELL, "wrist": SHELL, "palm": SHELL, "finger": {"fn": serrated(inner="east")},
                 "pincer": {"fn": serrated(inner="west")}})
    abdomen(m, parent="torso", start=(0, 6.5, 2), segs=[(5, 3, 2), (5, 3, 2), (4, 3, 2), (4, 2, 2), (3, 2, 2)],
            paints=[SHELL], fan_size=(7, 3), fan_paint={"fn": fan()}, rest=-5)
    m.pack()
    return m

ANT = {side: [f"antenna_{side}{k}" for k in range(1, 7)] for side, _ in SIDES}
TAIL = ["tail1", "tail2", "tail3", "tail4", "tail5", "tail_fan"]

def anims(m=None):
    m = m or build()
    out = crust_anims(SID, m, LEGS, pivot=PIVOT, cfg=dict(
        scale=0.6, body_h=4.0, antennae=ANT, tail=TAIL, snap=26,
        walk=dict(T=0.5, stride=3.0, lift=1.4, yaw=70.0, stance=0.55, bob=0.2, ripple=0.06),
        battle=dict(dy=-0.8, pitch=-6, arm=(-30, 20, 0), open_=28),
        cry=dict(L=1.3, rear=-12, dy=0.5, arm=(-55, 26, 0), open_=36, clack=((0.4, 0.55), (0.68, 0.83))),
        sleep=dict(spread=1.2)))
    return finalize(out)

def poser():
    return crust_poser(SID, portrait=(1.8, [-0.4, 0.0, 0]), profile=(1.0, [0, 0.25, 0]))
