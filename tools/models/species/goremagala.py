# -*- coding: utf-8 -*-
"""#1055 Gore Magala (+ Frenzy form): its own model and animations (3.3.0).

Proportions taken from the detailed Gore Magala mesh Kevin supplied (a 10 000-face model in T-pose, 2.3x our size):
a long body carried on four tall legs, a short thick neck with the head held forward, a long tail lined with spikes
above and below, and two great wings whose arm runs out from the shoulder to a clawed wrist, with long fingers
spreading the membrane back to the hips.
Kevin: "the wings act like webs, and Gore can fold them and make shoulders of them (at the claws)". So at rest the
wings are folded: the arm goes back from the shoulder to the elbow above the back, the forearm comes forward and
down again and the wrist sits on the outside of the shoulder, below the line of the back, its four long dark-red
claws hanging down along the shoulder (MH4 render; Kevin: the claws must not stick up); the fingers lie back along
the flank and the membrane (ragged black fur) hangs over it like a
cloak. In battle it unfolds them and plants the wrist claws far out on each side (the wings make a tent over it,
the game's frenzy capture); for its roar and when it rises it spreads them wide like the model's T-pose.

Front = -Z, ground = y 0, the creature's right side is Bedrock -X. Helpers come from species/magala.py (as M)."""
import math

M = None          # set by magala._gore(): magala's helpers (surf, seg, chain, box, ...)

# key points (left side, mirrored with mx), measured on the reference mesh (x 0.43, z shifted +22)
S_ = (10, 55, -18)                       # shoulder, on top of the chest
E_ = (23, 61, 14)                        # elbow, folded back: the folded arm makes the shoulder
W_ = (23, 49, -20)                       # wrist, on the outside of the shoulder (below the line of the back)
UP_LEN, FORE_LEN = 35.06, 36.06
FINGERS = [(24, 60, 52), (27, 42, 46), (28, 28, 30), (28, 20, 4)]   # finger tips, folded back over the flank
FRONT = (27, 24, -12)                    # front edge of the folded membrane (falls from the wrist)

def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]

def _angle(a, b):
    return math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)))))

def _slerp(a, b, t):
    om = _angle(a, b)
    if om < 1e-6:
        return a
    s = math.sin(om)
    return _norm([math.sin((1 - t) * om) / s * x + math.sin(t * om) / s * y for x, y in zip(a, b)])

def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

def frame_rot(ydir, zdir):
    """Bedrock cube rotation turning the cube's +Y axis to ydir and its +Z axis to zdir"""
    import numpy as np
    from scipy.spatial.transform import Rotation
    y = np.array(_norm(ydir)); z = np.array(zdir, float); z = z - np.dot(z, y) * y; z /= np.linalg.norm(z)
    x = np.cross(y, z)
    a, b, c = Rotation.from_matrix(np.column_stack([x, y, z])).as_euler("ZYX", degrees=True)
    return [round(-c, 2), round(b, 2), round(-a, 2)]

def web(p0, p1, wdir, width, paint, sunk=0.5):
    """a flat strip of web (1 thick) from p0 to p1, its width lying along wdir (in the membrane's plane)"""
    from modelgen import Cube
    v = [b - a for a, b in zip(p0, p1)]
    L = math.sqrt(sum(x * x for x in v))
    x, y, z = p0
    return Cube([x - 0.5, y - sunk, z - width / 2], [1, max(1, int(round(L + sunk))), width], paint,
                rotation=frame_rot(v, wdir), pivot=list(p0))

def build(name):
    from modelgen import Model, Cube
    surf, seg, chain, box, sbox, xs, mx = M.surf, M.seg, M.chain, M.box, M.sbox, M.xs, M.mx
    shingle, PLATE, FOLD, CLAW, SPIKE, TOOTH, MOUTH, FUR, _h = M.shingle, M.PLATE, M.FOLD, M.CLAW, M.SPIKE, M.TOOTH, \
        M.MOUTH, M.FUR, M._h
    frenzy = name == "goremagala_frenzy"
    m = Model(name, M.DEX[name], (512, 512))
    def gs(bb=None, S=4.2):
        return surf("gscale", belly_below=bb, S=S, glow="gscale")
    SC, SL = gs(), gs(S=3.2)
    m.bone("magala", None, [0, 0, 0])
    m.bone("body", "magala", [0, 40, 0])
    BELLY = 33
    # ------------------------------------------------------------------ chest and torso (deep, carried high)
    m.bone("chest", "body", [0, 42, -14], cubes=[
        sbox(11, 28, 54, -30, -6, gs(BELLY)), sbox(9, 54, 57, -28, -6, SC),
        box(-14, 14, 44, 56, -26, -12, SC)])                                 # shoulder hump (wing roots)
    m.bone("torso", "body", [0, 40, 12], cubes=[
        sbox(10, 30, 52, -7, 30, gs(BELLY)), sbox(8, 52, 55, -5, 26, SC)])
    def btop(z):
        return 57 if z < -6 else 55 if z < 26 else 52
    mane = m.bone("mane", "body", [0, 56, -10])                             # plates down the spine, fur mane
    for z in range(-28, 30, 5):
        top = btop(z)
        mane.cubes.append(shingle(0, top, z, 5, 7, tilt=16))
        for sx in (1, -1):
            mane.cubes.append(shingle(5.5 * sx, top - 0.8, z + 2, 5, 6, sx, tilt=12, roll=28))
    for z, y, L in [(-38, 53, 8), (-33, 55, 9), (-28, 57, 10), (-23, 58, 9), (-18, 58, 8), (-13, 57, 6)]:
        for sx in (1, -1):
            mane.cubes.append(seg([6 * sx, y - 1, z], [10 * sx, y + L * 0.45, z + L * 0.85], 3, 3, FUR))
    # ------------------------------------------------------------------ short thick neck, big head held forward
    n1 = m.bone("neck1", "chest", [0, 44, -28], cubes=[box(-7.5, 7.5, 33, 53, -34, -26, gs(36))])
    n2 = m.bone("neck2", "neck1", [0, 44, -33], cubes=[box(-7, 7, 34, 52, -39, -32, gs(37))])
    for z in (-34, -30):
        n1.cubes.append(shingle(0, 53.3, z, 6, 6, tilt=18))
    n2.cubes.append(shingle(0, 52.3, -39, 6, 6, tilt=18))
    head = m.bone("head", "neck2", [0, 44, -37], cubes=[
        box(-7, 7, 36, 50, -50, -36, SC),                                    # skull
        box(-5.5, 5.5, 37, 47, -56, -50, SL),                                # face
        box(-3.5, 3.5, 37, 44, -60, -56, SL),                                # snout
        box(-2, 2, 35, 39, -63, -59, PLATE),                                 # the hooked tip of the upper jaw
        box(-7.5, 7.5, 49, 52, -48, -36, PLATE)])                            # hood
    KEEL = surf("keel")
    for z in range(-62, -38, 4):                                             # the keel down the middle of the face
        top = 44 + min(7.5, (z + 62) * 0.32)
        head.cubes.append(shingle(0, top, z, 3 if z < -54 else 4, 6, tilt=10, paint=KEEL))
    for sx in (1, -1):
        for z in range(-58, -38, 5):                                         # layered plates along the sides
            y0 = 43 + (z + 58) * 0.15
            hw = 3.5 if z < -55 else (5.5 if z < -49 else 7)
            head.cubes.append(shingle(hw * sx, y0, z, 3, 6, sx, tilt=8, roll=70))
        head.cubes += chain([4 * sx, 51, -38], [(0.25 * sx, 0.55, 1), (0.1 * sx, 0.2, 1)], [6, 5],
                            [(2, 3), (1, 2)], PLATE)                         # crest plates at the back of the skull
        for y, L in ((46, 6), (42, 6), (38, 5)):                             # frill of spikes behind the jaw
            head.cubes += chain([6.5 * sx, y, -37], [(0.5 * sx, 0.1, 1)], [L], [(1, 2)], PLATE)
    m.bone("jaw", "head", [0, 37, -38], cubes=[
        box(-5, 5, 31, 37, -55, -38, gs(33, 2.6)), box(-3, 3, 32, 37, -61, -55, gs(33, 2.6)),
        box(-3.5, 3.5, 36.6, 37.6, -59, -40, MOUTH)])
    jaw = m.get("jaw")
    for k, z in enumerate(range(-56, -38, 4)):                               # the beard of spikes under the jaw
        jaw.cubes += chain([0, 31.5, z], [(0, -0.75, 0.65)], [5 - k * 0.5], [(2, 2)], SPIKE)
        for sx in (1, -1):
            jaw.cubes += chain([3.5 * sx, 31.5, z + 2], [(0.3 * sx, -0.7, 0.65)], [4], [(1, 2)], SPIKE)
    for k in range(6):                                                       # teeth (long fangs in front)
        for sx in (1, -1):
            z = -60 + 3.6 * k
            xw = 2.4 if z < -55 else 4.2
            h = 3 if k < 2 else 2
            head.cubes.append(box(xw * sx - 0.5, xw * sx + 0.5, 37 - h, 37, z, z + 1, TOOTH))
            jaw.cubes.append(box((xw + 0.3) * sx - 0.5, (xw + 0.3) * sx + 0.5, 37, 37 + h, z + 2, z + 3, TOOTH))
    # horns: rooted on the front of the face (as on the reference and the frenzy capture); calm they lie folded back
    # along the sides of the head, in frenzy they rise straight up, curving forward at the tip, pink and glowing
    for sx, side in ((1, "left"), (-1, "right")):
        ab = m.bone(f"antenna_{side}", "head", [3 * sx, 46, -54])
        if frenzy:
            ab.cubes += chain([3 * sx, 46, -54], [(0.12 * sx, 1, 0.1), (0.1 * sx, 1, -0.1), (0.05 * sx, 0.8, -0.5),
                                                   (0.0, 0.35, -0.95)],
                              [6, 6, 5, 3], [(2, 3), (2, 2), (2, 2), (1, 1)], surf("antenna", glow="antenna"))
        else:
            ab.cubes += chain([3.5 * sx, 46.5, -54], [(0.32 * sx, 0.22, 1), (0.25 * sx, 0.12, 1), (0.15 * sx, 0.05, 1)],
                              [7, 6, 5], [(2, 3), (1, 3), (1, 2)], FOLD)
        fb = m.bone(f"fang_{side}", "head", [3 * sx, 37, -58])
        if frenzy:
            fb.cubes += chain([3.4 * sx, 37.5, -58], [(0.7 * sx, -0.5, -0.5), (0.3 * sx, -0.6, -0.8)], [6, 4],
                              [(2, 2), (1, 1)], surf("fang", glow="antenna"))
        else:
            fb.cubes += chain([3.5 * sx, 37.5, -58], [(0.05 * sx, -0.7, 0.6), (0.0, -0.4, 1)], [4, 3],
                              [(1, 2), (1, 1)], surf("fang"))
    # ------------------------------------------------------------------ front legs: tall columns under the chest
    for sx, side in ((1, "left"), (-1, "right")):
        A0, A1, A2 = mx((13, 36, -21), sx), mx((15, 17, -24), sx), mx((16, 4, -22), sx)
        m.bone(f"arm_{side}", "chest", list(A0), cubes=[seg(A0, A1, 9, 9, SL), box(*xs(7, 18, sx), 26, 42, -28, -14, SC)])
        m.bone(f"arm_{side}_low", f"arm_{side}", list(A1), cubes=[
            seg(A1, A2, 7, 7, SL), box(*xs(10, 18, sx), 14, 20, -29, -21, PLATE)])          # knee plate
        foot = m.bone(f"arm_{side}_foot", f"arm_{side}_low", list(A2), cubes=[box(*xs(11, 21, sx), 0, 5, -32, -18, SL)])
        for dx in (-3, 0, 3):
            foot.cubes += chain([(16 + dx) * sx, 2.5, -32], [(0, 0.2, -1), (0, -0.7, -1)], [4, 3], [(2, 2), (1, 1)], M.CLAW)
    # ------------------------------------------------------------------ the wings: webs folded on the shoulders
    for sx, side in ((1, "left"), (-1, "right")):
        S, E, W = mx(S_, sx), mx(E_, sx), mx(W_, sx)
        m.bone(f"wing_{side}", "chest", list(S), cubes=[seg(S, E, 9, 9, SL)])
        fore = m.bone(f"wing_{side}_fore", f"wing_{side}", list(E), cubes=[
            seg(E, W, 8, 8, SL), box(E[0] - 4, E[0] + 4, E[1] - 4, E[1] + 4, E[2] - 4, E[2] + 4, SC)])
        for k in range(4):                                                # a ridge of plates down the forearm
            f = 0.15 + 0.2 * k
            P0 = [E[i] + (W[i] - E[i]) * f for i in range(3)]
            fore.cubes += chain([P0[0] + 3 * sx, P0[1] + 2, P0[2]], [(0.4 * sx, 1, 0.3)], [4], [(1, 3)], PLATE)
        fore.cubes += chain([E[0], E[1] + 3, E[2] + 3], [(0.1 * sx, 0.6, 1), (0.05 * sx, 0.1, 1)], [5, 4],
                            [(3, 3), (1, 1)], PLATE)                      # the elbow's spur, back (dark, not a claw)
        hand = m.bone(f"wing_{side}_hand", f"wing_{side}_fore", list(W), cubes=[
            box(W[0] - 5, W[0] + 5, W[1] - 5, W[1] + 4, W[2] - 5, W[2] + 5, SC)])
        # the wing's great claws (folded, as on the MH4 render: the wrist sits on the outside of the shoulder, below the
        # line of the back, and its four long red claws hang down along the shoulder, tips curling forward and in)
        for k, (dz, L0) in enumerate(((-4.5, 13), (-1.5, 15), (1.5, 14), (4.5, 12))):
            r = [W[0] + 4.5 * sx, W[1] + 1, W[2] + dz]
            hand.cubes += chain(r, [(0.5 * sx, -0.3, -0.35), (0.12 * sx, -1, -0.15), (-0.1 * sx, -0.8, -0.6)],
                                [3, L0, 6], [(3, 3), (2, 3), (1, 2)], CLAW)
        hand.cubes += chain([W[0] - 3 * sx, W[1] + 2, W[2] - 1], [(-0.4 * sx, -0.7, -0.45), (-0.2 * sx, -1, -0.3)], [5, 4],
                            [(2, 2), (1, 1)], CLAW)                       # the opposable thumb, hanging inward
        # fingers and membrane: finger k carries the strips of membrane between it and the next one
        tips = [mx(t, sx) for t in FINGERS]
        dirs = [_norm([t[i] - W[i] for i in range(3)]) for t in tips]
        lens = [math.sqrt(sum((t[i] - W[i]) ** 2 for i in range(3))) for t in tips]
        fr = _norm([mx(FRONT, sx)[i] - W[i] for i in range(3)])
        frl = math.sqrt(sum((mx(FRONT, sx)[i] - W[i]) ** 2 for i in range(3)))
        bounds = list(zip(dirs, lens)) + [(fr, frl)]
        mem = surf("gmembrane", glow="net", ragged_end=5)
        for k in range(4):
            fb = m.bone(f"wing_{side}_f{k + 1}", f"wing_{side}_hand", list(W))
            fb.cubes.append(seg(W, tips[k], 2, 2, SL))                     # the finger bone
            fb.cubes += chain([tips[k][0], tips[k][1], tips[k][2]], [dirs[k]], [4], [(1, 1)], SPIKE)
            (a, La), (b, Lb) = bounds[k], bounds[k + 1]
            om = _angle(a, b)
            n = max(2, int(math.ceil(math.degrees(om) / 4.5)))
            for j in range(n):
                t = (j + 0.5) / n
                d = _slerp(a, b, t)
                L = La + (Lb - La) * t
                wdt = max(2, int(round(L * om / n * 1.25 + 1)))
                p0 = [W[i] + 3 * d[i] for i in range(3)]
                p1 = [W[i] + L * d[i] for i in range(3)]
                nrm = _cross(a, b)
                fb.cubes.append(web(p0, p1, _cross(nrm, d), wdt, mem))
                if _h(k, j, 9) < 0.6:                                      # torn fur tatters past the trailing edge
                    Lt = 2 + 5 * _h(k, j, 5)
                    off = (_h(k, j, 7) - 0.5) * wdt * 0.6
                    wv = _norm(_cross(nrm, d))
                    q0 = [p1[i] - d[i] + off * wv[i] for i in range(3)]
                    q1 = [q0[i] + Lt * d[i] for i in range(3)]
                    fb.cubes.append(web(q0, q1, wv, 2 + int(2 * _h(k, j, 3)), FUR))
    # the inner web between the outstretched arm and the flank: laid out in the spread pose (shoulder -> wrist,
    # back to the hip), shown only when the wings open (its scale follows the spread weight in the animations)
    import numpy as np
    sp = WING_POSES["spread"]
    for sx, side in ((1, "left"), (-1, "right")):
        S = np.array(mx(S_, sx), float)
        Wp = np.array(mx(sp["wrist"], sx), float)
        a = _norm(list(Wp - S)); b = _norm([0.35 * sx, -0.06, 1])
        La, Lb = float(np.linalg.norm(Wp - S)) - 2, 52.0
        wb = m.bone(f"wing_{side}_web", "chest", list(S))
        om = _angle(a, b)
        n = max(2, int(math.ceil(math.degrees(om) / 4.5)))
        nrm = _cross(a, b)
        for j in range(n):
            t = (j + 0.5) / n
            d = _slerp(a, b, t)
            L = La + (Lb - La) * t
            wdt = max(2, int(round(L * om / n * 1.25 + 1)))
            p0 = [S[i] + 2 * d[i] for i in range(3)]
            p1 = [S[i] + L * d[i] for i in range(3)]
            wb.cubes.append(web(p0, p1, _cross(nrm, d), wdt, surf("gmembrane", glow="net", ragged_end=4)))
    # ------------------------------------------------------------------ hind legs: tall columns
    for sx, side in ((1, "left"), (-1, "right")):
        m.bone(f"leg_{side}", "torso", list(mx((11, 38, 20), sx)), cubes=[box(*xs(5, 17, sx), 20, 44, 10, 30, SC)])
        K, Hk = mx((11, 20, 22), sx), mx((11, 7, 26), sx)
        m.bone(f"leg_{side}_shin", f"leg_{side}", list(K), cubes=[seg(K, Hk, 8, 8, SL)])
        Ft = mx((11, 2, 22), sx)
        foot = m.bone(f"leg_{side}_foot", f"leg_{side}_shin", list(Hk), cubes=[
            seg(Hk, Ft, 6, 6, SL), box(*xs(6, 16, sx), 0, 5, 12, 28, SL)])
        for dx in (-3, 0, 3):
            foot.cubes += chain([(11 + dx) * sx, 2.5, 12], [(0, 0.2, -1), (0, -0.7, -1)], [4, 3], [(2, 2), (1, 1)], M.CLAW)
    # ------------------------------------------------------------------ the long tail: spikes on the sides, top and below
    prev, z, y = "torso", 28, 43
    for k, (L, w) in enumerate([(18, 13), (18, 10), (18, 7), (18, 4)]):
        tb = m.bone(f"tail{k + 1}", prev, [0, y, z], rotation=[-3, 0, 0], cubes=[
            box(-w / 2, w / 2, y - w / 2, y + w / 2, z - 1, z + L, gs(y - w / 2 + 2, 2.8))])
        for jj in range(4):
            zz = z + 1 + 4.2 * jj
            L2 = max(2, round(8 - 1.5 * k - 0.3 * jj))
            for sx in (1, -1):
                tb.cubes += chain([(w / 2 - 0.5) * sx, y + w / 2 - 1.5, zz], [(0.9 * sx, 0.35, 0.65)], [L2], [(1, 2)], SPIKE)
            tb.cubes += chain([0, y + w / 2 - 0.5, zz + 1], [(0, 0.7, 1)], [max(2, L2 - 2)], [(1, 2)], PLATE)
            tb.cubes += chain([0, y - w / 2 + 0.5, zz + 2], [(0, -0.8, 0.7)], [max(2, L2 - 1)], [(1, 2)], SPIKE)
        prev, z, y = f"tail{k + 1}", z + L, y - 1
    m.get("tail4").cubes += chain([0, y + 1, z - 2], [(0, 0.2, 1), (0, 0, 1)], [6, 5], [(3, 3), (1, 1)], SPIKE)
    m.pack()
    return m

# ---------------------------------------------------------------------------------------------- wing poses
def _rot(r):
    import numpy as np
    ax, ay, az = (math.radians(v) for v in r)
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, sx], [0, -sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, sz, 0], [-sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def ik(wrist, pole):
    """elbow position for the wrist target (2-bone IK, the elbow bending toward the pole direction)"""
    import numpy as np
    S = np.array(S_, float); Wt = np.array(wrist, float)
    a, b = UP_LEN, FORE_LEN
    d = Wt - S; L = np.linalg.norm(d)
    L = min(L, a + b - 0.5)
    u = d / np.linalg.norm(d)
    x = (a * a - b * b + L * L) / (2 * L)
    h = math.sqrt(max(0.0, a * a - x * x))
    pv = np.array(pole, float); pv = pv - np.dot(pv, u) * u; pv /= np.linalg.norm(pv)
    return tuple(S + x * u + h * pv), tuple(S + L * u)

def solve_wing(pose):
    """rotations (left side) of the wing bones for a pose given as world targets:
    pose = {"wrist": (x, y, z), "pole": dir, "claws": dir, "fingers": [dir1..dir4]}"""
    import numpy as np
    from scipy.optimize import minimize
    S, E, W = (np.array(v, float) for v in (S_, E_, W_))
    tips = [np.array(t, float) for t in FINGERS]
    claw0 = np.array([0.12, -1.0, -0.15]); claw0 /= np.linalg.norm(claw0)   # the claws' main direction (folded)
    out = {}
    def fit(fun, x0=(0, 0, 0)):
        best = None
        for x in (x0, (40, 0, 0), (-40, 0, 0), (0, 0, 60), (0, 0, -60), (0, 60, 0), (0, -60, 0)):
            r = minimize(fun, x, method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-7, "maxiter": 6000})
            if best is None or r.fun < best.fun:
                best = r
        return [round(float(v), 2) for v in best.x]
    tE, tW = (np.array(v, float) for v in ik(pose["wrist"], pose["pole"]))
    # upper arm: orient S->E onto S->tE and the forearm plane (E->W) toward tW, both at once
    def f_up(a):
        R = _rot(a)
        e = S + R @ (E - S)
        return np.sum((e - tE) ** 2) + 1e-6 * np.sum(np.square(a))
    a_up = fit(f_up)
    R1 = _rot(a_up)
    E1 = S + R1 @ (E - S)
    a_fo = fit(lambda a: np.sum((E1 + R1 @ _rot(a) @ (W - E) - tW) ** 2) + 1e-6 * np.sum(np.square(a)))
    R2 = R1 @ _rot(a_fo)
    out["wing_left"], out["wing_left_fore"] = a_up, a_fo
    cd = np.array(pose.get("claws", (0, -0.3, -1)), float); cd /= np.linalg.norm(cd)
    fd0 = np.array(pose["fingers"][1], float); fd0 /= np.linalg.norm(fd0)
    d1 = (tips[1] - W) / np.linalg.norm(tips[1] - W)
    a_ha = fit(lambda a: -np.dot(R2 @ _rot(a) @ claw0, cd) - 0.6 * np.dot(R2 @ _rot(a) @ d1, fd0)
               + 1e-6 * np.sum(np.square(a)))
    R3 = R2 @ _rot(a_ha)
    out["wing_left_hand"] = a_ha
    for k, fd in enumerate(pose.get("fingers") or []):
        d0 = (tips[k] - W) / np.linalg.norm(tips[k] - W)
        fd = np.array(fd, float); fd /= np.linalg.norm(fd)
        out[f"wing_left_f{k + 1}"] = fit(lambda a: -np.dot(R3 @ _rot(a) @ d0, fd) + 1e-6 * np.sum(np.square(a)))
    return out

def mirror(rots):
    """left-side rotations -> both sides"""
    out = {}
    for b, r in rots.items():
        out[b] = r
        out[b.replace("left", "right")] = [r[0], -r[1], -r[2]]
    return out

WING_POSES = {
    # the game's frenzy stance: the arms arch out and down, the wrist claws planted far out, the webs a tent over it
    "planted": {"wrist": (38, 23, -30), "pole": (0.4, 1, 0.3), "claws": (0.15, -1, -0.35),
                "fingers": [(-0.35, 0.62, 0.7), (-0.42, 0.45, 0.78), (-0.5, 0.28, 0.82), (-0.6, 0.1, 0.8)]},
    # wide open (its roar, the reference's T-pose): the arm straight out, the fingers fanned back
    "spread": {"wrist": (79, 60, -20), "pole": (0, 0.3, 1), "claws": (0.3, -0.1, -1),
               "fingers": [(0.15, 0.0, 1), (-0.15, -0.02, 1), (-0.45, -0.05, 0.9), (-0.75, -0.08, 0.65)]},
    # raised high and forward (the Giant Slam's wind-up): claws over its head, the webs half open behind
    "raised": {"wrist": (24, 104, -34), "pole": (0.6, 0.2, 1), "claws": (0, 0.2, -1),
               "fingers": [(0.35, 0.25, 0.9), (0.3, -0.05, 0.95), (0.25, -0.3, 0.92), (0.2, -0.55, 0.8)]},
    # slammed down in front of it
    "slam": {"wrist": (24, 25, -50), "pole": (0.5, 0.6, 0.2), "claws": (0, -1, -0.45),
             "fingers": [(-0.15, 0.75, 0.6), (-0.2, 0.55, 0.8), (-0.25, 0.3, 0.9), (-0.3, 0.05, 0.95)]},
    # half open, the claws on the ground by its head (exploding breath)
    "half": {"wrist": (30, 18, -42), "pole": (0.6, 0.6, 0.2), "claws": (0.05, -1, -0.4),
             "fingers": [(-0.1, 0.62, 0.78), (-0.15, 0.42, 0.88), (-0.2, 0.22, 0.95), (-0.28, 0.02, 0.95)]},
}
_CACHE = {}

def wing(pose, f=1.0):
    """bone -> rotation for both wings at a pose, scaled by f (0 = folded)"""
    if pose not in _CACHE:
        _CACHE[pose] = mirror(solve_wing(WING_POSES[pose]))
    return {b: [v * f for v in r] for b, r in _CACHE[pose].items()}

WING_BONES = [f"wing_{s}{p}" for s in ("left", "right") for p in ("", "_fore", "_hand", "_f1", "_f2", "_f3", "_f4")]

def blend(*parts):
    """sum of weighted wing poses: blend(("planted", w1), ("spread", w2), ...) -> bone -> rotation"""
    out = {b: [0.0, 0.0, 0.0] for b in WING_BONES}
    for pose, w in parts:
        if w == 0:
            continue
        for b, r in wing(pose, w).items():
            out[b] = [a + c for a, c in zip(out[b], r)]
    return out

# ---------------------------------------------------------------------------------------------- animations
def anims(name, m):
    kf, wave, track, merge, anim, seq, SIDES = M.kf, M.wave, M.track, M.merge, M.anim, M.seq, M.SIDES
    S = {}
    def wings(fn, L, steps=24):
        """wing channels from fn(t) -> [(pose, weight), ...]; the inner webs open with the "spread" weight"""
        samples = [(L * i / steps, blend(*fn(L * i / steps))) for i in range(steps + 1)]
        out = {b: {"rotation": kf({round(t, 4): bl[b] for t, bl in samples})} for b in WING_BONES}
        sw = lambda t: sum(w for p, w in fn(t) if p == "spread")
        for s in ("left", "right"):
            out[f"wing_{s}_web"] = {"scale": track(lambda t: [max(0.0, min(1.0, sw(t)))] * 3, L, steps)}
        return out
    def flutter(t, amp, period=0.5):
        """the membrane fingers rippling"""
        out = {}
        for k in range(1, 5):
            for s, sx in SIDES:
                out[f"wing_{s}_f{k}"] = [amp * math.sin(2 * math.pi * t / period + k), 0, 0]
        return out

    # ground_idle (6 s): wings folded on its shoulders, breathing; blind, the head sweeps low side to side and the
    # membrane twitches now and then (it senses with the scales of its wings)
    L = 6.0
    look = seq({0: 0, 1.2: 22, 2.6: 22, 3.6: -20, 5.0: -20, 6.0: 0})
    tw = lambda t: (math.sin((t - 2.6) * math.pi / 0.5) if 2.6 < t < 3.1 else 0) + \
        (math.sin((t - 5.0) * math.pi / 0.4) if 5.0 < t < 5.4 else 0)
    idle = merge(
        {"body": {"position": wave(0.4, 3.0, L, axis=1)}},
        {"chest": {"rotation": wave(1.0, 3.0, L, axis=0)}},
        {"neck1": {"rotation": track(lambda t: [14 + 2 * math.sin(2 * math.pi * t / 3), look(t) * 0.45, 0], L, 48)},
         "neck2": {"rotation": track(lambda t: [6, look(t) * 0.25, 0], L, 48)},
         "head": {"rotation": track(lambda t: [-4 + 3 * math.sin(2 * math.pi * t / 1.5), look(t) * 0.3, -look(t) * 0.15],
                                    L, 48)},
         "jaw": {"rotation": wave(1.5, 3.0, L, phase=2.0, axis=0, base=(2, 0, 0))}},
        {f"wing_{s}_f{k}": {"rotation": track(lambda t, k=k, sx=sx: [-4 * max(0.0, tw(t)) * k, 0,
                                                                     -sx * 6 * max(0.0, tw(t))], L, 60)}
         for s, sx in SIDES for k in range(1, 5)},
        {f"tail{k}": {"rotation": wave(3 + k, 3.0, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)})
    S["ground_idle"] = anim(L, idle, loop=True)

    # walk: the four legs in diagonal pairs, the folded wings rocking a little
    T = 1.4
    w = {}
    for s, sx in SIDES:
        ph = 0 if sx > 0 else math.pi
        a = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph)
        b = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph))
        a2 = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph + math.pi)
        b2 = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph + math.pi))
        w[f"arm_{s}"] = {"rotation": track(lambda t, a=a: [16 * a(t), 0, 0], T)}
        w[f"arm_{s}_low"] = {"rotation": track(lambda t, b=b: [-20 * b(t), 0, 0], T)}
        w[f"arm_{s}_foot"] = {"rotation": track(lambda t, a=a, b=b: [-16 * a(t) + 20 * b(t), 0, 0], T)}
        w[f"leg_{s}"] = {"rotation": track(lambda t, a=a2: [18 * a(t), 0, 0], T)}
        w[f"leg_{s}_shin"] = {"rotation": track(lambda t, b=b2: [18 * b(t), 0, 0], T)}
        w[f"leg_{s}_foot"] = {"rotation": track(lambda t, a=a2, b=b2: [-18 * a(t) - 18 * b(t), 0, 0], T)}
        w[f"wing_{s}"] = {"rotation": wave(2.5, T, T, phase=ph, axis=0)}
        for k in range(1, 5):
            w[f"wing_{s}_f{k}"] = {"rotation": wave(2 + k, T, T, phase=ph + 0.4 * k, axis=0)}
    walkd = merge(w,
        {"body": {"position": track(lambda t: [0, 0.7 * abs(math.sin(2 * math.pi * t / T)), 0], T),
                  "rotation": wave(2, T, T, axis=2)}},
        {"neck1": {"rotation": wave(2, T / 2, T, axis=0, base=(10, 0, 0))}, "neck2": {"rotation": [4, 0, 0]},
         "head": {"rotation": wave(2, T / 2, T, phase=math.pi, axis=0, base=(-4, 0, 0))}},
        {f"tail{k}": {"rotation": wave(4 + 2 * k, T, T, phase=-0.6 * k, axis=1)} for k in range(1, 5)})
    S["ground_walk"] = anim(T, walkd, loop=True)

    # battle_idle: the game's frenzy stance: wings unfolded, the wrist claws planted far out on each side, low head
    L = 2.0
    bi = merge(
        wings(lambda t: [("planted", 1.0)], L, 4),
        {f"wing_{s}_f{k}": {"rotation": track(lambda t, k=k: [wing("planted")[f"wing_left_f{k}"][0] +
                                                                 3 * math.sin(2 * math.pi * t / L + k),
                                                                 (1 if s == "left" else -1) * wing("planted")[f"wing_left_f{k}"][1],
                                                                 (1 if s == "left" else -1) * wing("planted")[f"wing_left_f{k}"][2]], L)}
         for s, sx in SIDES for k in range(1, 5)},
        {"body": {"position": wave(0.6, L, L, axis=1, base=(0, -1, 0))}},
        {"chest": {"rotation": wave(1.5, L, L, axis=0, base=(5, 0, 0))}},
        {f"arm_{s}": {"rotation": [-8, 0, 6 * sx]} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": [-6, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [8, 0, 0]} for s, sx in SIDES},
        {"neck1": {"rotation": wave(2, L, L, axis=0, base=(12, 0, 0))},
         "head": {"rotation": wave(3, L, L, phase=1, axis=0, base=(4, 0, 0))},
         "jaw": {"rotation": wave(4, L / 2, L, axis=0, base=(6, 0, 0))}},
        {f"tail{k}": {"rotation": wave(5 + k, L, L, phase=-0.7 * k, axis=1, base=(4 if k == 1 else 0, 0, 0))}
         for k in range(1, 5)})
    S["battle_idle"] = anim(L, bi, loop=True)

    # cry (2.2 s): rears its neck, throws its wings wide open and roars, the membrane quivering
    L = 2.2
    up = seq({0: 0, .55: 1, 1.7: 1, 2.2: 0})
    shake = lambda t: 4 * math.sin(t * 40) if 0.6 < t < 1.6 else 0
    cry = merge(
        wings(lambda t: [("spread", up(t))], L),
        {"neck1": {"rotation": track(lambda t: [-22 * up(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-16 * up(t), shake(t), 0], L, 44)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .45: 38, 1.6: 38, 2.0: 2, 2.2: 2})(t), 0, 0], L)},
         "chest": {"rotation": track(lambda t: [-6 * up(t), 0, 0], L)},
         "body": {"position": track(lambda t: [0, 2 * up(t), 0], L)}},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [6 * up(t), 0, 0], L)} for k in (1, 2)})
    S["cry"] = anim(L, cry)

    # physical: Giant Slam (1.3 s): screech, rears up on its hind legs with the wings raised, slams the claws down
    L = 1.3
    rear = seq({0: 0, .45: 1, .62: 1, .78: 0, 1.0: 0, 1.3: 0})
    slam = seq({0: 0, .62: 0, .76: 1, 1.0: 1, 1.3: 0})
    phys = merge(
        wings(lambda t: [("raised", rear(t)), ("slam", slam(t) * (1 - rear(t)))], L, 26),
        {"body": {"rotation": track(lambda t: [-22 * rear(t) + 3 * slam(t), 0, 0], L, 26),
                  "position": track(lambda t: [0, 8 * rear(t) - 2 * slam(t), 3 * rear(t) - 6 * slam(t)], L, 26)}},
        {f"arm_{s}": {"rotation": track(lambda t: [-35 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": track(lambda t: [40 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [24 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [-10 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t: [10 * rear(t), 0, 0], L, 26)} for k in (1, 2)},
        {"neck1": {"rotation": track(lambda t: [-18 * rear(t) + 18 * slam(t), 0, 0], L, 26)},
         "head": {"rotation": track(lambda t: [-16 * rear(t) + 10 * slam(t), 0, 0], L, 26)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .3: 36, .6: 30, .76: 8, 1.3: 2})(t), 0, 0], L, 26)}})
    S["physical"] = anim(L, phys)

    # special: exploding breath (1.6 s): wings half open, claws planted by its head, the open jaws sweep right to left
    L = 1.6
    yaw = seq({0: 0, .45: 34, .7: 34, 1.25: -34, 1.6: 0})
    o = seq({0: 0, .4: 1, 1.3: 1, 1.6: 0})
    sp = merge(
        wings(lambda t: [("half", o(t))], L),
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .45: -18, .7: -6, 1.25: -6, 1.6: 0})(t), yaw(t) * 0.45, 0], L, 48)},
         "neck2": {"rotation": track(lambda t: [0, yaw(t) * 0.3, 0], L, 48)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .45: -14, .7: 6, 1.25: 6, 1.6: 0})(t), yaw(t) * 0.3,
                                               -yaw(t) * 0.2], L, 48)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .45: 10, .65: 38, 1.25: 38, 1.45: 2, 1.6: 2})(t), 0, 0], L, 48)},
         "chest": {"rotation": track(lambda t: [-4 * o(t), yaw(t) * 0.1, 0], L, 48)},
         "body": {"position": track(lambda t: [0, -2 * o(t), 2 * o(t)], L, 48)}})
    S["special"] = anim(L, sp)

    # status (1.3 s): half opens its wings and shakes them to scatter its scales, head high
    L = 1.3
    o = seq({0: 0, .3: 1, 1.0: 1, 1.3: 0})
    st = merge(
        wings(lambda t: [("spread", 0.55 * o(t))], L, 26),
        {f"wing_{s}_f{k}": {"rotation": track(lambda t, k=k, s=s: [a + (8 * math.sin(t * 30 + k) * (0.3 < t < 1.0) if i == 0 else 0)
                                                                   for i, a in enumerate(wing("spread", 0.55 * o(t))[f"wing_{s}_f{k}"])],
                                              L, 39)}
         for s, sx in SIDES for k in range(1, 5)},
        {"neck1": {"rotation": track(lambda t: [-16 * o(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-6 * o(t), 5 * math.sin(t * 22) * (0.3 < t < 1.0), 0], L, 32)},
         "jaw": {"rotation": track(lambda t: [2 + 16 * o(t), 0, 0], L)},
         "body": {"rotation": track(lambda t: [0, 0, 3 * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}})
    S["status"] = anim(L, st)

    # faint (2.6 s): a last trembling cry with the wings flaring, then it collapses on its flank, wings limp
    L = 2.6
    up = seq({0: 0, .45: 1, 1.15: 1, 1.6: 0})
    fall = seq({0: 0, 1.1: 0, 1.9: 1, 2.6: 1})
    tremble = lambda t: (math.sin(t * 55) * 3 if 0.45 < t < 1.2 else 0)
    fa = merge(
        wings(lambda t: [("spread", 0.6 * up(t))], L, 26),
        {"neck1": {"rotation": track(lambda t: [-28 * up(t) + 20 * fall(t), tremble(t) * 0.5, 0], L, 52)},
         "neck2": {"rotation": track(lambda t: [-8 * up(t) + 10 * fall(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-20 * up(t) + 12 * fall(t), tremble(t), 0], L, 52)},
         "jaw": {"rotation": track(lambda t: [2 + 36 * up(t) + 14 * fall(t) * (1 - up(t)), 0, 0], L)},
         "magala": {"rotation": track(lambda t: [0, 0, -70 * fall(t)], L),
                    "position": track(lambda t: [-8 * fall(t), -1 * fall(t), 0], L)},
         "chest": {"rotation": track(lambda t: [-8 * up(t), 0, 0], L)}},
        {f"arm_{s}": {"rotation": track(lambda t: [-30 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [-30 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [40 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [0, 8 * fall(t), 0], L)} for k in range(1, 5)})
    S["faint"] = anim(L, fa, loop="hold")

    # sleep: lying down, legs folded, wings folded over it, head on the ground
    L = 4.0
    sl = merge(
        {"magala": {"position": [0, -16, 0]}},
        {f"leg_{s}": {"rotation": [-40, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [70, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": [-55, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}": {"rotation": [65, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": [-95, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}_foot": {"rotation": [30, 0, 0]} for s, sx in SIDES},
        {f"wing_{s}_f{k}": {"rotation": [-2 * k, 0, 0]} for s, sx in SIDES for k in range(1, 5)},
        {"neck1": {"rotation": [26, 0, 0]}, "neck2": {"rotation": [8, -14, 0]}, "head": {"rotation": [6, -12, 0]},
         "jaw": {"rotation": [0, 0, 0]}, "chest": {"rotation": wave(1.0, L, L, axis=0, base=(4, 0, 0))}},
        {f"tail{k}": {"rotation": [6 if k == 1 else 0, -14 - 4 * k, 0]} for k in range(1, 5)})
    S["sleep"] = anim(L, sl, loop=True)
    # portrait_idle: the party portrait and the summary (head at rest, not lowered like the hunting idle)
    L = 3.0
    S["portrait_idle"] = anim(L, merge(
        {"body": {"position": wave(0.4, L, L, axis=1)}, "chest": {"rotation": wave(1.0, L, L, axis=0)},
         "jaw": {"rotation": wave(1.5, L, L, phase=2.0, axis=0, base=(2, 0, 0))}},
        {f"tail{k}": {"rotation": wave(3 + k, L, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)}), loop=True)
    for a in S.values():                                  # the inner webs stay folded away unless an animation opens them
        for s in ("left", "right"):
            a["bones"].setdefault(f"wing_{s}_web", {"scale": [0, 0, 0]})
    return S

def poser(name, group):
    """magala's poser, with the party portrait and the summary on their own calm pose (portrait_idle)"""
    q = lambda a: f"q.bedrock('{group}', '{a}')"
    prim = lambda a: f"q.bedrock_primary('{group}', '{a}', q.curve('symmetrical_wide'))"
    return {"rootBone": "magala",
            "animations": {"cry": f"q.bedrock_stateful('{group}', 'cry')",
                           "faint": f"q.bedrock_primary('{group}', 'faint', q.curve('one'))",
                           "physical": prim("physical"), "special": prim("special"), "status": prim("status")},
            "poses": {
                "battle-standing": {"poseTypes": ["STAND"], "isBattle": True,
                                    "animations": ["q.look('head')", q("battle_idle")]},
                "standing": {"poseTypes": ["STAND", "NONE", "FLOAT"], "isBattle": False,
                             "animations": ["q.look('head')", q("ground_idle")]},
                "portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "animations": [q("portrait_idle")]},
                "walking": {"poseTypes": ["WALK", "SWIM"], "animations": ["q.look('head')", q("ground_walk")]},
                "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]}}}
