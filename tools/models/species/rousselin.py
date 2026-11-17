# -*- coding: utf-8 -*-
"""#1038 Rousselin — agneau Roussin de la Hague, né sur les falaises schisteuses (Roche / Normal).
A cute, chubby lamb: big round head with the breed's dark russet face and ears held straight out to the sides,
large glossy eyes, a little wool topknot, a round cream fleece with a grey-brown cast low on the body and a few
salt crystals from the sea spray, dark legs on slate (schist) hooves, a stubby woolly tail, and a small bronze bell
on a red ribbon (it learns Heal Bell before becoming the flock's protector). Shiny: a russet ('roux') lamb."""
from modelgen import Model, Cube, rgb
from bovine import make_legs, add_eye, closed_lids, bovine_anims, finalize, SIDES, bovine_poser
from ovine import curled_sleep, fleece, face_hair, slate_hoof, bronze_bell, strap, sheep_ear, muzzle

SID, DEX = "rousselin", 1038
FRAME_BONES = ("head", "jaw")

PAL = {
    "wool": rgb("#EEE8DC"), "wool_dark": rgb("#B4A796"), "wool_shade": rgb("#C9BFAF"), "wool_light": rgb("#FBF8F1"),
    "salt": rgb("#FFFFFF"),
    "face": rgb("#3E2E28"), "face_light": rgb("#6A4A3A"), "muzzle": rgb("#7A6358"), "nostril": rgb("#1E1614"),
    "mouth": rgb("#2A1E1A"), "ear_in": rgb("#8E5E50"), "ear_in_light": rgb("#B07A68"),
    "leg": rgb("#3A2C26"), "slate": rgb("#5E6874"), "slate_dark": rgb("#3E4650"), "slate_mica": rgb("#A9B6C4"),
    "eye": rgb("#120C0A"), "eye_shine": rgb("#FFFFFF"), "eye_iris": rgb("#B07A36"), "eye_iris2": rgb("#E2B266"),
    "eye_white": rgb("#F2EEE8"), "eye_dark": rgb("#21160F"), "lash": rgb("#0E0907"), "lunette": rgb("#33251F"),
    "bronze": rgb("#C8923E"), "bronze_light": rgb("#F2CF7A"), "bronze_dark": rgb("#7A5420"),
    "ribbon": rgb("#C8323A"), "ribbon_dark": rgb("#8A1E26"),
}
SHINY = dict(PAL, **{
    "wool": rgb("#D49464"), "wool_dark": rgb("#9A5A34"), "wool_shade": rgb("#B4764A"), "wool_light": rgb("#EEC09A"),
    "face": rgb("#2C1E1A"), "face_light": rgb("#5A3A2C"), "ribbon": rgb("#2E6EB4"), "ribbon_dark": rgb("#1C4680"),
    "bronze": rgb("#C9CED6"), "bronze_light": rgb("#F4F7FA"), "bronze_dark": rgb("#7C838E"),
})

# ---------------------------------------------------------------- legs: short and sturdy, woolly to the knee
FRONT = dict(x=2.2, z=-3.8, L=(2, 3, 2), a=(22, -6, 0), th=1, thigh=(4, 4, 1), shin=(2, 2), meta=(2, 2), foot=(2, 2, 1))
BACK = dict(x=2.2, z=4.2, L=(2, 3, 2), a=(-18, 34, -4), th=1, thigh=(4, 5, 1), shin=(2, 2), meta=(2, 2), foot=(2, 2, 1))
WOOL = fleece(seed=2, low=(9.0, 4.0), salt=0.015, curl=0.9)
LEG_PAINT = {"thigh": WOOL, "shin": {"base": "leg"}, "meta": {"base": "leg"}, "foot": {"fn": slate_hoof}}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 7.6, 0)
D = -2.0                           # body block placed 2 lower than first drafted (shorter legs)

# head: modelled level in the neck's unrotated frame, poll at the head pivot (PY, PZ)
PY, PZ = 15.0, -9.5
EYE = dict(x_edge=3.5, w=2, y0=PY - 3.8, h=3, z_face=PZ - 6.0, d=2, lash_row=1,
           front=["HD",                 # outer lash flick, upper lid
                  "SE",                 # big catch-light, pupil
                  "IJ"],                # warm brown iris, glint
           side_rows=["DH", "ES", "JI"])
_lids = closed_lids(**EYE)
FACE = face_hair()
FACE_LIDS = {"fn3": None}
def _face_fn3(px, faces, pal, rnd, c):
    from bovine import light, put
    FACE["fn3"](px, faces, pal, rnd, c)
    for face, X, Y, pl in c.texels():
        k = _lids(pl, face, None)
        if k:
            fx, fy, fw, fh = faces[face]
            put(px, X, Y, pal[k], light(face, Y - fy, fh), rnd, 2)
FACE_LIDS["fn3"] = _face_fn3

def build():
    m = Model(SID, DEX, (128, 128))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    y = lambda v: v + D
    m.bone("torso", "body", [0, y(11), 0], cubes=[
        Cube([-4.5, y(8), -5], [9, 8, 11], WOOL),
        Cube([-3.5, y(7), -4], [7, 1, 9], WOOL),                                   # round belly
        Cube([-3.5, y(16), -4], [7, 1, 9], WOOL),                                  # round back
        Cube([4.5, y(9), -3.5], [1, 6, 8], WOOL), Cube([-5.5, y(9), -3.5], [1, 6, 8], WOOL),   # plump flanks
        Cube([-3.5, y(9), 6], [7, 6, 1], WOOL)])                                   # rump
    m.bone("chest", "torso", [0, y(11), -5], cubes=[
        Cube([-4, y(8.5), -7.5], [8, 7, 3], WOOL),
        Cube([-3, y(7.8), -7], [6, 1, 2], WOOL)])
    m.bone("neck", "chest", [0, y(13.5), -6.5], rotation=[-45, 0, 0], cubes=[
        Cube([-2.5, y(11.5), -10], [5, 5, 4], WOOL),
        Cube([-3, y(11), -8.5], [6, 6, 1], {"fn": strap("ribbon", "ribbon_dark")})])     # red ribbon collar
    m.bone("bell", "neck", [0, y(11), -8], cubes=[
        Cube([-0.5, y(10), -8.5], [1, 1, 1], {"fn": bronze_bell}),
        Cube([-1, y(8), -9], [2, 2, 2], {"fn": bronze_bell})])
    m.bone("head", "neck", [0, PY, PZ], rotation=[45, 0, 0], cubes=[
        Cube([-3.5, PY - 5, PZ - 6], [7, 6, 6], FACE_LIDS),                        # big round head
        Cube([-1.5, PY - 5, PZ - 7], [3, 3, 1], {"fn": muzzle}),                   # short lamb muzzle
        Cube([-2.5, PY + 1, PZ - 5], [5, 1, 4], fleece(seed=5)),                   # wool topknot
        Cube([-1.5, PY + 2, PZ - 4.5], [3, 1, 2], fleece(seed=6)),
        Cube([-1, PY + 0.5, PZ - 6.4], [2, 1, 1], fleece(seed=7))])                # forelock curl
    m.bone("jaw", "head", [0, PY - 5, PZ - 5], cubes=[
        Cube([-1, PY - 6, PZ - 7], [2, 1, 3], {"base": "muzzle", "up": "mouth"})])
    for side, sx in SIDES:
        add_eye(m, "head", side, sx, **EYE)
        eo = 3.5 if sx > 0 else -6.5
        m.bone(f"ear_{side}", "head", [3.5 * sx, PY - 1, PZ - 2.5], rotation=[0, -12 * sx, 12 * sx], cubes=[
            Cube([eo, PY - 1.5, PZ - 3.5], [3, 1, 2], {"fn": sheep_ear})])
    m.bone("tail", "torso", [0, y(15), 6.5], rotation=[18, 0, 0], cubes=[
        Cube([-1, y(11.5), 6], [2, 4, 2], fleece(seed=9))])
    m.pack()
    return m

def anims(m=None):
    m = m or build()
    q = "q.anim_time"
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=(), tail=("tail",), chew=0.8,
                       walk_kw=dict(T=0.7, stride=4.5, lift=1.6, stance=0.64, bob=0.3, toe_off=20, fold=55, curl=30),
                       battle=dict(theta=2.0, dy=-0.4, neck=8, head=-6, paw="front_right", paw_t=1.2, ears_back=16,
                                   tail_up=12),
                       cry=dict(L=1.2, t_in=0.15, t_open=0.3, t_close=0.9, neck=-10, head=-18, jaw=16, tremble=3.0,
                                extra={"bell": {"rotation": lambda t, e: [10 * e * __import__("math").sin(t * 9.0), 0, 0]}}),
                       idle_extra={"bell": {"rotation": [f"math.sin({q}*90+60)*2", 0, f"math.sin({q}*45)*2"]}},
                       walk_extra={"bell": {"rotation": [f"math.sin({q}*{2 * 360 / 0.7:.3f}+60)*10", 0, f"math.sin({q}*{360 / 0.7:.3f})*6"]}})
    # sleep curled up: head turned back along the flank instead of the bovine chin-on-the-ground
    sk = f"animation.{SID}."
    sp = out[sk + "_sleep_pose"]
    trunk = {"torso", "chest"}
    curled_sleep(m, sp, trunk=trunk)
    out[sk + "sleep"]["bones"]["neck"] = sp["neck"]
    out[sk + "sleep"]["bones"]["head"] = sp["head"]
    return finalize(out)

def poser():
    return bovine_poser(SID, portrait=(1.5, [-0.5, 0.2, 0]), profile=(0.97, [-0.15, 0.28, 0]))
