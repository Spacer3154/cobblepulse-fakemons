# -*- coding: utf-8 -*-
"""#1039 Roussinage — bélier Roussin de la Hague aux cornes de granit, protecteur des Rousselins (Roche / Normal).
A big, stern ram: deep body under a dense fleece (salt-crusted by the sea spray), a thick woolly ruff over the
neck and shoulders, a long dark russet face with a Roman nose and golden eyes with horizontal pupils under heavy
lids, ears held out sideways, massive curled horns of speckled granite with growth ridges, dark legs on slate
hooves. As the flock's bellwether it wears a large bronze bell on a studded leather collar.
Rideable: one rider on its back (cobblemon:land/horse). Shiny: russet fleece and rose granite horns."""
import math
from modelgen import Model, Cube, rgb
from bovine import make_legs, add_eye, closed_lids, bovine_anims, finalize, SIDES, bovine_poser, GAIT
from biped import walk
from ovine import curled_sleep, fleece, face_hair, slate_hoof, bronze_bell, strap, sheep_ear, muzzle, granite

SID, DEX = "roussinage", 1039
FRAME_BONES = ("head", "jaw")
SCALE_BOOST = 1.25                   # mounts are shown a bit larger than their Pokédex height (as Cobblemon does)

PAL = {
    "wool": rgb("#E2DACB"), "wool_dark": rgb("#9E8F7E"), "wool_shade": rgb("#B7AB9B"), "wool_light": rgb("#F3EEE5"),
    "salt": rgb("#FFFFFF"),
    "face": rgb("#2F2420"), "face_light": rgb("#5E4234"), "muzzle": rgb("#5E4A42"), "nostril": rgb("#150F0D"),
    "mouth": rgb("#1E1512"), "ear_in": rgb("#7E5446"), "ear_in_light": rgb("#9E6C5A"),
    "leg": rgb("#2E2420"), "slate": rgb("#55606C"), "slate_dark": rgb("#363E48"), "slate_mica": rgb("#A5B3C2"),
    "eye": rgb("#100A08"), "eye_shine": rgb("#FFF6DC"), "eye_iris": rgb("#C8922C"), "eye_iris2": rgb("#E6BC5C"),
    "eye_white": rgb("#EEE8DE"), "eye_dark": rgb("#1C1310"), "lash": rgb("#0C0806"), "lunette": rgb("#2A1F1B"),
    "granite": rgb("#A9A39B"), "granite_dark": rgb("#3B3735"), "granite_light": rgb("#EAE6E0"), "granite_pink": rgb("#C7A090"),
    "bronze": rgb("#B98236"), "bronze_light": rgb("#EAC26C"), "bronze_dark": rgb("#6A4618"),
    "leather": rgb("#6A4128"), "leather_dark": rgb("#432816"),
}
SHINY = dict(PAL, **{
    "wool": rgb("#CC8C5E"), "wool_dark": rgb("#8A4E2E"), "wool_shade": rgb("#A86C44"), "wool_light": rgb("#E8B892"),
    "granite": rgb("#C98A78"), "granite_dark": rgb("#5A3430"), "granite_light": rgb("#F4DCD0"), "granite_pink": rgb("#E6A48E"),
    "face": rgb("#251A17"), "face_light": rgb("#52362A"),
})

# ---------------------------------------------------------------- legs: stout, woolly to the knee
FRONT = dict(x=3.6, z=-8.0, L=(4, 5, 4), a=(22, -6, 0), th=2, thigh=(6, 6, 2), shin=(4, 4), meta=(3, 3), foot=(4, 3, 1.5))
BACK = dict(x=3.6, z=8.5, L=(5, 4, 4), a=(-18, 34, -4), th=2, thigh=(6, 7, 2), shin=(4, 4), meta=(3, 3), foot=(4, 3, 1.5))
WOOL = fleece(seed=12, low=(17.0, 9.0), salt=0.015, curl=0.65)
RUFF = fleece(seed=14, salt=0.02, curl=0.8, tint=0.35)
LEG_PAINT = {"thigh": WOOL, "shin": {"base": "leg"}, "meta": {"base": "leg"}, "foot": {"fn": slate_hoof}}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 14.4, 0)
D = -3.0                                 # body block 3 lower than drafted (shorter, stouter legs)

PY, PZ = 25.0, -16.5                     # poll (head pivot), head modelled level in the neck's unrotated frame
# stern eyes: heavy dark lid, golden iris, horizontal pupil (rows top -> bottom; side columns from the front)
EYE = dict(x_edge=4.0, w=1, y0=PY - 4.5, h=4, z_face=PZ - 6.0, d=3, lash_row=1,
           front=["D", "I", "E", "J"],
           side_rows=["DDD", "JIS", "EEE", "IJI"])
_lids = closed_lids(**EYE)
_face = face_hair(seed=21)
def _face_fn3(px, faces, pal, rnd, c):
    from bovine import light, put
    _face["fn3"](px, faces, pal, rnd, c)
    for face, X, Y, pl in c.texels():
        k = _lids(pl, face, None)
        if k:
            fx, fy, fw, fh = faces[face]
            put(px, X, Y, pal[k], light(face, Y - fy, fh), rnd, 2)
FACE = {"fn3": _face_fn3}
FACE_PLAIN = face_hair(seed=22)

# ram horn: chain of granite segments growing back (+Z) and curling down, forward and up around the ear
HORN = [  # (length, thickness, rot X, rot Y (outward), rot Z)
    (4, 4, 34, 22, 0),
    (4, 3, -62, 8, 0),
    (4, 3, -62, 6, 0),
    (3, 2, -60, 10, 0),
    (3, 2, -48, 14, 0)]

def ram_horn(m, parent, side, sx, base):
    x, y, z = base
    prev = parent
    for i, (L, t, rx, ry, rz) in enumerate(HORN):
        name = f"horn{i + 1}_{side}"
        m.bone(name, prev, [x, y, z], rotation=[rx, ry * sx, rz * sx], cubes=[
            Cube([x - t / 2, y - t / 2, z - (1 if i else 0)], [t, t, L + (1 if i else 0)], {"fn": granite(rings=2, along="z")})])
        prev, z = name, z + L

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    y = lambda v: v + D
    m.bone("torso", "body", [0, y(19), 1], cubes=[
        Cube([-6.5, y(14), -7], [13, 12, 17], WOOL),
        Cube([-5.5, y(13), -6], [11, 1, 15], WOOL),                                # belly
        Cube([-5.5, y(26), -6], [11, 1, 15], WOOL),                                # broad back (saddle)
        Cube([6.5, y(15), -5.5], [1, 10, 14], WOOL), Cube([-7.5, y(15), -5.5], [1, 10, 14], WOOL),   # deep flanks
        Cube([-5.5, y(15), 10], [11, 10, 1], WOOL)])                               # rump
    m.bone("locator_seat_1", "torso", [0, y(27), 3], locators={"seat_1": [0, y(27), 3]})
    m.bone("chest", "torso", [0, y(19), -7], cubes=[
        Cube([-6, y(13.5), -12], [12, 13, 5], WOOL),
        Cube([-6.5, y(20), -13], [13, 8, 7], RUFF)])                               # woolly ruff over the shoulders
    m.bone("neck", "chest", [0, y(23), -11], rotation=[-50, 0, 0], cubes=[
        Cube([-4, y(19), -18], [8, 8, 7], RUFF),
        Cube([-4.5, y(18.5), -15.5], [9, 9, 1], {"fn": strap("leather", "leather_dark", stud="granite_light")})])
    m.bone("bell", "neck", [0, y(18.5), -15], cubes=[
        Cube([-0.5, y(16.5), -15.5], [1, 2, 1], {"fn": strap("leather", "leather_dark")}),
        Cube([-1.5, y(14.5), -16.5], [3, 2, 3], {"fn": bronze_bell}),
        Cube([-2, y(11.5), -17], [4, 3, 4], {"fn": bronze_bell}),
        Cube([-0.5, y(10.5), -15.5], [1, 1, 1], {"fn": bronze_bell})])             # clapper
    m.bone("head", "neck", [0, PY, PZ], rotation=[50, 0, 0], cubes=[
        Cube([-4, PY - 6, PZ - 6], [8, 7, 6], FACE),                               # broad skull
        Cube([-3, PY - 7, PZ - 10], [6, 6, 4], FACE_PLAIN),                        # long face, Roman nose
        Cube([-2.5, PY - 7, PZ - 11], [5, 3, 1], {"fn": muzzle}),
        Cube([-2.5, PY + 1, PZ - 4.5], [5, 1, 4], RUFF)])                          # wool on the poll
    m.bone("jaw", "head", [0, PY - 7, PZ - 6], cubes=[
        Cube([-2, PY - 8, PZ - 10.5], [4, 1, 5], {"base": "muzzle", "up": "mouth"})])
    for side, sx in SIDES:
        add_eye(m, "head", side, sx, **EYE)
        eo = 4 if sx > 0 else -7
        m.bone(f"ear_{side}", "head", [4 * sx, PY - 3, PZ - 1.5], rotation=[0, -10 * sx, 18 * sx], cubes=[
            Cube([eo, PY - 3.5, PZ - 2.5], [3, 1, 2], {"fn": sheep_ear})])
        ram_horn(m, "head", side, sx, (3.0 * sx, PY + 0.5, PZ - 4.0))
    m.bone("tail", "torso", [0, y(24), 10.5], rotation=[14, 0, 0], cubes=[
        Cube([-1.5, y(18), 10], [3, 6, 2], fleece(seed=19))])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    q = "q.anim_time"
    W = 360 / 1.1
    bell_idle = {"bell": {"rotation": [f"math.sin({q}*90+60)*2", 0, f"math.sin({q}*45)*2"]}}
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=(), tail=("tail",), chew=1.0, torso=(0.7, 1.4, 1.8),
                       walk_kw=dict(T=1.1, stride=10, lift=2.6, stance=0.68, bob=0.45, toe_off=18, fold=50, curl=28),
                       battle=dict(theta=3.0, dy=-0.9, neck=16, head=8, paw="front_right", paw_t=1.0, ears_back=18,
                                   tail_up=8),
                       cry=dict(L=1.9, t_in=0.3, t_open=0.55, t_close=1.4, neck=-10, head=-14, jaw=14, tremble=2.2,
                                extra={"bell": {"rotation": lambda t, e: [12 * e * math.sin(t * 8.0), 0, 6 * e * math.sin(t * 5.0)]}}),
                       idle_extra=bell_idle,
                       walk_extra={"bell": {"rotation": [f"math.sin({q}*{2 * W:.3f}+60)*9", 0, f"math.sin({q}*{W:.3f})*5"]}})
    # gallop for the rider's sprint (transverse gallop: hinds then fores, short contact)
    run = walk(LEGS, T=0.55, stride=14, lift=4.0, stance=0.38, bob=0.9, toe_off=24, fold=70, curl=40,
               phases={"back_left": 0.0, "back_right": 0.12, "front_left": 0.5, "front_right": 0.62},
               torso=(3.0, 1.2, 1.2), tail=(), neck=True, arms=(),
               extra={"bell": {"rotation": [f"math.sin({q}*{2 * 360 / 0.55:.3f}+40)*16", 0, f"math.sin({q}*{360 / 0.55:.3f})*6"]},
                      "head": {"rotation": [f"6-math.cos({q}*{360 / 0.55:.3f}+60)*4", 0, 0]},
                      "tail": {"rotation": [f"20+math.sin({q}*{360 / 0.55:.3f})*6", 0, 0]}})
    out[f"animation.{SID}.ground_run"] = run
    out[f"animation.{SID}.mount_ground_idle"] = {"loop": True, "animation_length": 8,
                                                 "bones": {k: v for k, v in out[f"animation.{SID}.ground_idle"]["bones"].items()
                                                           if k not in ("jaw",)}}
    # sleep: lying on the brisket, head still held up but lowered (the watchful protector dozes), eyes shut
    sk = f"animation.{SID}."
    sp = out[sk + "_sleep_pose"]
    sp["neck"] = {"rotation": [14, 10, 0]}
    sp["head"] = {"rotation": [12, 6, 5]}
    out[sk + "sleep"]["bones"]["neck"] = {"rotation": [f"14+math.sin(q.anim_time*45)*1.5", 10, 0]}
    out[sk + "sleep"]["bones"]["head"] = {"rotation": [f"12+math.sin(q.anim_time*45-40)*1.5", 6, 5]}
    from biped import lowest
    from bovine import copy_pose, rng
    best = 0.0
    for bx in rng(0, -90, 31):                     # the bell swings up onto the brisket instead of into the ground
        pp = copy_pose(sp)
        pp["bell"] = {"rotation": [bx, 0, 0]}
        if lowest(m, pp, only={"bell"}) >= 0.1:
            best = bx
            break
    out[f"animation.{SID}.sleep"]["bones"]["bell"] = {"rotation": [best, 0, 0]}
    return finalize(out)

def poser():
    ps = bovine_poser(SID, portrait=(1.2, [-0.6, 1.0, 0]), profile=(0.6, [0, 0.8, 0]))
    qb = lambda n: f"q.bedrock('{SID}', '{n}')"
    blink = [f"q.bedrock_quirk('{SID}', 'blink')"]
    P = ps["poses"]
    P["standing"]["condition"] = "!q.is_ridden"
    P["walking"]["condition"] = "!q.is_sprinting"
    P["running"] = {"poseTypes": ["WALK", "SWIM"], "condition": "q.is_sprinting",
                    "animations": ["q.look('head')", qb("ground_run")], "quirks": blink}
    P["mount_idle"] = {"poseTypes": ["STAND", "NONE", "FLOAT"], "isBattle": False, "condition": "q.is_ridden",
                       "animations": ["q.look('head')", qb("mount_ground_idle")], "quirks": blink}
    ps["firstPersonCameraOffset"] = {"seat_1": [0, 0.45, 0]}
    ps["thirdPersonCameraOffset"] = {"seat_1": [0, 0.5, 0], "seat_1_reverse": [0, 0.5, 0]}
    return ps
