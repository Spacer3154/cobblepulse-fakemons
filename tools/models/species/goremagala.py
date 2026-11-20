# -*- coding: utf-8 -*-
"""#1055 Gore Magala (+ Frenzy form): its own model and animations (3.3.0, wings redone in 3.4.0).

Proportions taken from the detailed Gore Magala mesh Kevin supplied (a 10 000-face model in T-pose, 2.3x our size):
a long body carried on four tall legs, a short thick neck with the head held forward, a long tail lined with spikes
above and below. Limbs and body are rounded (octagonal sections).
The wings (Kevin, 3.4.0): folded, the wrist rests on the shoulder just above the front leg's joint with its three
great red claws hooked over it (they only rise when it uses them), and the retracted sail covers the whole flank like
a cloak; the sail runs along the whole wing in two parts linked at the elbow (upper arm to back, forearm to the
wing's end) and stretches as the wing opens. Claws planted: set down well beyond the head, arms stretched, sails
rising to the sky. Flight: the arms stay folded, only the sails stretch out sideways and beat.
The sail is cut in strips, each strip bone turned part-way between its two edges, so it stays whole in every pose;
the geometry's rest layout is the stretched (flight) sail, every animation sets the wing pose.

Front = -Z, ground = y 0, the creature's right side is Bedrock -X. Helpers come from species/magala.py (as M)."""
import math
import re

M = None          # set by magala._gore(): magala's helpers (surf, seg, chain, box, ...)

# key points (left side, mirrored with mx). Kevin: folded, the wing claws rest on the shoulder just above the
# joint of the front legs (they only go up when it uses them), and the sails cover its flanks even folded, so from
# behind only the tail shows; the sails retract or stretch as it unfolds (a great sail); in flight it does not unfold
# its arms, only the sails stretch out.
S_ = (10, 55, -14)                       # shoulder (wing root), on the back above the front legs
E_ = (14, 66, 16)                        # elbow, folded back high above the back (the gif's peak behind the shoulders)
W_ = (20, 44, -25)                       # wrist, resting on the shoulder just above the front leg's joint
UP_LEN = math.dist(S_, E_)
FORE_LEN = math.dist(E_, W_)
SAIL_REST = 0.8                          # folded, the sail is retracted to 80 % (it stretches to 100 % as it opens)
# folded finger tips as shown (sail retracted): the sail drapes over the flank like a cloak, its top edge running up
# over the back to the hips, its lower edge along the belly line down to the thighs
FOLD_TIPS = [(4, 64, 50), (17, 52, 58), (23, 34, 54), (25, 12, 44)]
FOLD_FRONT = (22, 18, -12)               # the hem, hanging down the shoulder behind the front leg
# the geometry's own (rest) layout is the sail stretched out sideways, as in flight: the widest fan any pose uses, so
# the membrane never tears open between the fingers; every other pose (folded included) closes the fan
REST_DIRS = [(0.259, 0.03, 0.966), (0.643, 0.03, 0.766), (0.906, 0.03, 0.423), (1.0, 0.03, 0.0)]   # f1 along the body ... f4 straight out
REST_FRONT = (0.766, -0.1, -0.643)            # the hem, the leading edge forward of the last finger
FINGER_LEN = [math.dist(W_, t) / SAIL_REST for t in FOLD_TIPS]
FRONT_LEN = math.dist(W_, FOLD_FRONT) / SAIL_REST
UPPER_BODY = (0.08, -0.02, 1)            # the upper sail's inner edge: along the back from the shoulder to the hips
UPPER_BODY_LEN = 46
UPPER_SUBS = 10                          # strip bones of the upper sail (between the upper arm and the back)
SUBS = [7, 3, 3, 3]
SPAR = [0.3, 0.55, 0.78, 1.0]            # the great bone's joints, as fractions of its length                      # membrane bones per sector (forearm-f1, f1-f2, f2-f3, f3-f4), each turned
                                         # part-way between its two edges so the sail stays whole as the fan moves

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

def rbox(x0, x1, y0, y1, z0, z1, paint, k=0.3):
    """a rounded box long along z: three stacked cores (a 12-sided section) instead of one block"""
    w, h = x1 - x0, y1 - y0
    dx, dy = max(1, round(k * w)), max(1, round(k * h))
    return [M.box(x0 + dx, x1 - dx, y0, y1, z0, z1, paint), M.box(x0, x1, y0 + dy, y1 - dy, z0, z1, paint),
            M.box(x0 + dx / 2, x1 - dx / 2, y0 + dy / 2, y1 - dy / 2, z0, z1, paint)]

def rboxv(x0, x1, y0, y1, z0, z1, paint, k=0.3):
    """a rounded box standing upright (12-sided section in x/z)"""
    w, d = x1 - x0, z1 - z0
    dx, dz = max(1, round(k * w)), max(1, round(k * d))
    return [M.box(x0 + dx, x1 - dx, y0, y1, z0, z1, paint), M.box(x0, x1, y0, y1, z0 + dz, z1 - dz, paint),
            M.box(x0 + dx / 2, x1 - dx / 2, y0, y1, z0 + dz / 2, z1 - dz / 2, paint)]

def rseg(p0, p1, w, paint):
    """a rounded limb segment: three crossed boxes (a 12-sided section)"""
    w2 = w - 2 * max(1, round(0.25 * w))
    w3 = (w + w2) // 2 if (w + w2) % 2 == 0 else w - 1
    return [M.seg(p0, p1, w, w2, paint), M.seg(p0, p1, w2, w, paint), M.seg(p0, p1, w3, w3, paint)]

def build(name):
    from modelgen import Model, Cube
    surf, seg, chain, box, sbox, xs, mx = M.surf, M.seg, M.chain, M.box, M.sbox, M.xs, M.mx
    shingle, PLATE, FOLD, CLAW, SPIKE, TOOTH, MOUTH, FUR, _h = M.shingle, M.PLATE, M.FOLD, M.CLAW, M.SPIKE, M.TOOTH, \
        M.MOUTH, M.FUR, M._h
    frenzy = name == "goremagala_frenzy"
    chaos = name == "chaoticgoremagala"
    # Shagaru Magala and the chaotic Gore's right half (Bedrock -X) are built on Gore's model with Shagaru's parts
    gold = lambda sx: name == "shagarumagala" or (chaos and sx < 0)
    shag = name == "shagarumagala"
    HORN = M.HORN
    m = Model(name, M.DEX[name], (512, 512))
    def gs(bb=None, S=4.2):
        return surf("gscale", belly_below=bb, S=S, glow="gscale")
    SC, SL = gs(), gs(S=3.2)
    m.bone("magala", None, [0, 0, 0])
    m.bone("body", "magala", [0, 40, 0])
    BELLY = 33
    # ------------------------------------------------------------------ chest and torso (deep, carried high)
    m.bone("chest", "body", [0, 42, -14], cubes=[
        *rbox(-11, 11, 28, 54, -30, -6, gs(BELLY)), sbox(8, 54, 57, -28, -6, SC),
        *rbox(-14, 14, 44, 56, -26, -12, SC)])                               # shoulder hump (wing roots)
    m.bone("torso", "body", [0, 40, 12], cubes=[
        *rbox(-10, 10, 30, 52, -7, 30, gs(BELLY)), sbox(7, 52, 55, -5, 26, SC)])
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
    n1 = m.bone("neck1", "chest", [0, 44, -28], cubes=rbox(-7.5, 7.5, 33, 53, -34, -26, gs(36)))
    n2 = m.bone("neck2", "neck1", [0, 44, -33], cubes=rbox(-7, 7, 34, 52, -39, -32, gs(37)))
    for z in (-34, -30):
        n1.cubes.append(shingle(0, 53.3, z, 6, 6, tilt=18))
    n2.cubes.append(shingle(0, 52.3, -39, 6, 6, tilt=18))
    head = m.bone("head", "neck2", [0, 44, -37], cubes=[
        *rbox(-7, 7, 36, 50, -50, -36, SC),                                  # skull
        *rbox(-5.5, 5.5, 37, 47, -56, -50, SL),                              # face
        *rbox(-3.5, 3.5, 37, 44, -60, -56, SL),                              # snout
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
        if gold(sx):
            # Shagaru: a crown of horns (the great crescent rising from the brow and sweeping forward, two swept back
            # behind it) and an eye on each side of the face
            hy = 50 if shag else 46                                        # the chaotic one: the horn's root set lower
            hb = m.bone(f"horn_{side}", "head", [4.5 * sx, hy, -46])
            # Kevin: the horn curves round at its root, then rises straight up without bending, only a light curve forward
            hb.cubes += chain([(4.5 if shag else 6) * sx, hy, -46], [(0.45 * sx, 0.55, 0.6), (0.15 * sx, 1, 0.12),
                                                                    (0.05 * sx, 1, -0.06), (0.0, 1, -0.22)],
                              [6, 11, 10, 8], [(3, 4), (3, 3), (2, 3), (1, 2)], HORN)
            if not shag:
                # concept sheet: golden cracks from the horn's root along the side of the head and down the neck, joined
                # to the cracks of the wing arm
                CR = surf("spike", alt=True)
                hb.cubes += chain([6.6 * sx, 45, -44], [(0.05 * sx, 0.6, 1), (0.1 * sx, 0.3, 1)], [5, 4], [(1, 1), (1, 1)], CR)
                head.cubes += [seg((7.2 * sx, 44, -54), (7.6 * sx, 47, -38), 1, 1, CR),
                               seg((7.2 * sx, 41, -50), (7.6 * sx, 44, -38), 1, 1, CR)]
                n1.cubes.append(seg((7.9 * sx, 47, -26), (7.9 * sx, 44, -34), 1, 1, CR))
                n2.cubes.append(seg((7.4 * sx, 46, -32), (7.4 * sx, 44, -39), 1, 1, CR))
            for (y, z, d, L) in (((50, -40, (0.45 * sx, 0.45, 1), 11), (48, -37, (0.6 * sx, 0.15, 1), 9)) if shag else ()):
                hb.cubes += chain([5.5 * sx, y, z], [d, (d[0] * 0.7, d[1] - 0.25, d[2])], [L, L * 0.6],
                                  [(2, 3), (1, 2)], HORN)
            eb = m.bone(f"eye_{side}", "head", [5.6 * sx, 43, -53])
            eb.cubes.append(box(*xs(5.4, 6.4, sx), 42, 45, -56, -51, surf("eye", glow="eye")))
            m.bone(f"lid_{side}", f"eye_{side}", [5.6 * sx, 43, -53],
                   cubes=[box(*xs(5.6, 6.6, sx), 42, 45, -56, -51, surf("lid"), inflate=0.2)])
            continue
        ab = m.bone(f"antenna_{side}", "head", [3 * sx, 46, -54])
        if frenzy:
            ab.cubes += chain([3 * sx, 46, -54], [(0.12 * sx, 1, 0.1), (0.1 * sx, 1, -0.1), (0.05 * sx, 0.8, -0.5),
                                                   (0.0, 0.35, -0.95)],
                              [6, 6, 5, 3], [(2, 3), (2, 2), (2, 2), (1, 1)], surf("antenna", glow="antenna"))
        else:
            # calm: dark, folded along the face; when it raises them (battle) they turn glowing purple (Kevin): a dark
            # copy and a lit copy, the animations swap them by scale
            args = ([3.5 * sx, 46.5, -54], [(0.32 * sx, 0.22, 1), (0.25 * sx, 0.12, 1), (0.15 * sx, 0.05, 1)],
                    [7, 6, 5], [(2, 3), (1, 3), (1, 2)])
            m.bone(f"antenna_{side}_dark", f"antenna_{side}", [3 * sx, 46, -54], cubes=chain(*args, FOLD))
            m.bone(f"antenna_{side}_lit", f"antenna_{side}", [3 * sx, 46, -54],
                   cubes=chain(*args, surf("antenna", glow="antenna")))
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
        m.bone(f"arm_{side}", "chest", list(A0), cubes=[*rseg(A0, A1, 9, SL), *rboxv(*xs(7, 18, sx), 26, 42, -28, -14, SC)])
        m.bone(f"arm_{side}_low", f"arm_{side}", list(A1), cubes=[
            *rseg(A1, A2, 7, SL), box(*xs(11, 17, sx), 14, 20, -28, -22, PLATE)])          # knee plate
        foot = m.bone(f"arm_{side}_foot", f"arm_{side}_low", list(A2), cubes=rbox(*xs(11, 21, sx), 0, 5, -32, -18, SL))
        for dx in (-3, 0, 3):
            foot.cubes += chain([(16 + dx) * sx, 2.5, -32], [(0, 0.2, -1), (0, -0.7, -1)], [4, 3], [(2, 2), (1, 1)], M.CLAW)
    # ------------------------------------------------------------------ the wings: webs folded on the shoulders
    for sx, side in ((1, "left"), (-1, "right")):
        S, E, W = mx(S_, sx), mx(E_, sx), mx(W_, sx)
        ARM = surf("gscale", S=3.2, alt=True) if (chaos and sx < 0) else SL         # the chaotic one: golden wing arm
        m.bone(f"wing_{side}", "chest", list(S), cubes=rseg(S, E, 9, ARM))
        fore = m.bone(f"wing_{side}_fore", f"wing_{side}", list(E), cubes=[
            *rseg(E, W, 8, ARM), *rbox(E[0] - 4, E[0] + 4, E[1] - 4, E[1] + 4, E[2] - 4, E[2] + 4, SC)])
        if chaos and sx < 0:
            GSP = surf("spike", alt=True)
            for q in [0.1 + 0.11 * k for k in range(8)]:                   # golden spikes along the forearm (MH4U)
                P0 = [E[i] + (W[i] - E[i]) * q for i in range(3)]
                fore.cubes += chain([P0[0] + 2 * sx, P0[1] + 3, P0[2]], [(0.5 * sx, 0.8, 0.35)], [5 - 2 * abs(q - 0.5)],
                                    [(1, 2)], GSP)
            for q in (0.3, 0.6, 0.9):
                P0 = [S[i] + (E[i] - S[i]) * q for i in range(3)]
                m.get(f"wing_{side}").cubes += chain([P0[0] + 2 * sx, P0[1] + 3, P0[2]], [(0.5 * sx, 0.8, 0.4)], [4],
                                                     [(1, 2)], GSP)
            # the arm's golden cracks, continuing those of the neck
            m.get(f"wing_{side}").cubes.append(seg((S[0] + 4.7 * sx, S[1], S[2]), (E[0] + 4.7 * sx, E[1], E[2]), 1, 1, GSP))
            fore.cubes.append(seg((E[0] + 4.2 * sx, E[1], E[2]), (W[0] + 4.2 * sx, W[1], W[2]), 1, 1, GSP))
        for k in range(4):                                                # a ridge of plates down the forearm
            f = 0.15 + 0.2 * k
            P0 = [E[i] + (W[i] - E[i]) * f for i in range(3)]
            fore.cubes += chain([P0[0] + 3 * sx, P0[1] + 2, P0[2]], [(0.4 * sx, 1, 0.3)], [4], [(1, 3)], PLATE)
        fore.cubes += chain([E[0], E[1] + 3, E[2] + 3], [(0.1 * sx, 0.6, 1), (0.05 * sx, 0.1, 1)], [5, 4],
                            [(3, 3), (1, 1)], PLATE)                      # the elbow's spur, back (dark, not a claw)
        fdir = _norm([W[i] - E[i] for i in range(3)])                     # the video (0:17): red hooks stacked on the
        for k, L0 in enumerate((8, 7, 6)):                                # top of the elbow, curling forward over the arch
            P0 = [E[i] + fdir[i] * (2 + 5 * k) for i in range(3)]
            up = [fdir[0] * 0.5 + 0.15 * sx, fdir[1] * 0.5 + 0.85, fdir[2] * 0.5]
            fore.cubes += chain([P0[0], P0[1] + 3.5, P0[2]], [up, fdir, (fdir[0], fdir[1] - 0.9, fdir[2])], [L0 * 0.5, L0 * 0.6, 4],
                                [(3, 3), (2, 2), (1, 1)], CLAW)
        hand = m.bone(f"wing_{side}_hand", f"wing_{side}_fore", list(W), cubes=rbox(W[0] - 5, W[0] + 5, W[1] - 5, W[1] + 4,
                                                                               W[2] - 5, W[2] + 5, SC))
        # the wing's three great claws, side by side: folded, they rest on the shoulder above the front leg's joint,
        # hooked forward and down over it (Kevin's gif)
        for dx, L0 in ((-3.5, 9), (0.5, 10), (4.5, 9)):
            r = [W[0] + dx * sx, W[1] - 1, W[2] - 4]
            hand.cubes += chain(r, [(0.1 * sx, -0.1, -1), (0.08 * sx, -0.8, -0.6), (0.0, -1, 0.25)],
                                [L0, 7, 4], [(3, 3), (2, 2), (1, 1)], CLAW)
        hand.cubes += chain([W[0] - 4 * sx, W[1] - 3, W[2] - 1], [(-0.35 * sx, -0.75, -0.55), (-0.1 * sx, -1, 0.1)], [5, 3],
                            [(2, 2), (1, 1)], CLAW)                       # the opposable thumb, hooking down inside
        # fingers and membrane, laid out in the rest (stretched) fan
        dirs = [mx(_norm(d), sx) for d in REST_DIRS]
        tips = [[W[i] + L * d[i] for i in range(3)] for d, L in zip(dirs, FINGER_LEN)]
        fa = _norm([E[i] - W[i] for i in range(3)])
        bounds = [(fa, FORE_LEN - 6)] + list(zip(dirs, FINGER_LEN)) + [(mx(_norm(REST_FRONT), sx), FRONT_LEN)]
        mem = surf("gmembrane", glow="net", ragged_end=5)
        def sector(bone, a, La, b, Lb, kk, t0=0.0, t1=1.0, tatters=True, O=W):
            om = _angle(a, b)
            n = max(2, int(math.ceil(math.degrees(om) / 4.5)))
            nrm = _cross(a, b)
            for j in range(n):
                t = (j + 0.5) / n
                if not t0 <= t < t1:
                    continue
                d = _slerp(a, b, t)
                L = La + (Lb - La) * t
                if shag and kk != 7:                                       # Shagaru: a star, pointed at every finger
                    L *= 1 - 0.2 * math.sin(math.pi * t)
                wdt = max(2, int(round(L * om / n * 1.25 + 1)))
                p0 = [O[i] + 3 * d[i] for i in range(3)]
                p1 = [O[i] + L * d[i] for i in range(3)]
                bone.cubes.append(web(p0, p1, _cross(nrm, d), wdt, mem))
                nv = [v * sx for v in _norm(nrm)]                          # the outer side (fur), see magala.surf
                for q in (0.45, 0.78):                                     # fur tufts shingled on the outside
                    if _h(kk, j * 3 + int(q * 10), 17) < 0.75:
                        Lq = L * (0.22 + 0.12 * _h(kk, j, int(q * 20)))
                        s0 = [O[i] + L * q * d[i] + 0.9 * nv[i] for i in range(3)]
                        tilt = _norm([d[i] + 0.22 * nv[i] for i in range(3)])
                        s1 = [s0[i] + Lq * tilt[i] for i in range(3)]
                        bone.cubes.append(web(s0, s1, _cross(nrm, d), max(2, int(round(wdt * 0.6))), FUR))
                if tatters and _h(kk, j, 9) < 0.6:                         # torn fur tatters past the trailing edge
                    Lt = 2 + 5 * _h(kk, j, 5)
                    off = (_h(kk, j, 7) - 0.5) * wdt * 0.6
                    wv = _norm(_cross(nrm, d))
                    q0 = [p1[i] - d[i] + off * wv[i] for i in range(3)]
                    q1 = [q0[i] + Lt * d[i] for i in range(3)]
                    bone.cubes.append(web(q0, q1, wv, 2 + int(2 * _h(kk, j, 3)), SPIKE if shag else FUR))
        for k in range(4):
            fb = m.bone(f"wing_{side}_f{k + 1}", f"wing_{side}_hand", list(W))
            if k == 3:
                # the wing's great bone (Kevin): from the claws' joint at the wrist to the very end of the sail, on its
                # outer edge; a supple bone that bends like several, so it is built in four jointed segments (each
                # segment its own bone, flexed by the animations), rounded and scaly, tapering to a hooked point
                n = len(SPAR)
                pts = [[W[i] + (tips[k][i] - W[i]) * q for i in range(3)] for q in [0.0] + SPAR]
                parent = fb
                for jj in range(n):
                    bone = fb if jj == 0 else m.bone(f"wing_{side}_f4_j{jj}", parent.name, list(pts[jj]))
                    wd = 5 - jj if jj < 3 else 3
                    bone.cubes += rseg(pts[jj], pts[jj + 1], wd, SL)
                    kn = 4 - 0.5 * jj
                    bone.cubes += rbox(pts[jj][0] - kn, pts[jj][0] + kn, pts[jj][1] - kn, pts[jj][1] + kn,
                                       pts[jj][2] - kn, pts[jj][2] + kn, SC)            # the joint knob
                    mid = [(pts[jj][i] + pts[jj + 1][i]) / 2 for i in range(3)]
                    bone.cubes += chain(mid, [_norm([dirs[k][0] * 0.5 + 0.2 * sx, 0.8, dirs[k][2] * 0.5])], [3], [(1, 2)], PLATE)
                    parent = bone
                parent.cubes += chain([tips[k][0], tips[k][1], tips[k][2]], [dirs[k], _norm([dirs[k][0], dirs[k][1] - 0.7, dirs[k][2]])],
                                      [6, 4], [(2, 2), (1, 1)], CLAW)      # the hooked tip of the sail
            else:
                fb.cubes.append(seg(W, tips[k], 2, 2, SL))                 # the finger bone
                fb.cubes += chain([tips[k][0], tips[k][1], tips[k][2]], [dirs[k]], [4], [(1, 1)], SPIKE)
        (a, La), (b, Lb) = bounds[4], bounds[5]
        sector(m.get(f"wing_{side}_f4"), a, La, b, Lb, 4)                  # the hem rides on the last finger
        for k in range(4):                                                 # the sail between two edges, in strips
            (a, La), (b, Lb) = bounds[k], bounds[k + 1]
            for jj in range(SUBS[k]):
                sector(m.bone(f"wing_{side}_s{k}{jj}", f"wing_{side}_hand", list(W)), a, La, b, Lb, k,
                       jj / SUBS[k], (jj + 1) / SUBS[k], tatters=k > 0)
        # the upper sail (Kevin: the sail runs along the whole wing, two parts linked at the elbow): from the shoulder,
        # between the upper arm and the back; laid out at its widest, each strip bone turned to follow the arm
        a0, b0 = mx(upper_open(), sx), mx(_norm(UPPER_BODY), sx)
        for jj in range(UPPER_SUBS):
            sector(m.bone(f"wing_{side}_a{jj}", "chest", list(S)), b0, UPPER_BODY_LEN, a0, UP_LEN - 3, 7,
                   jj / UPPER_SUBS, (jj + 1) / UPPER_SUBS, O=S)
    # ------------------------------------------------------------------ hind legs: tall columns
    for sx, side in ((1, "left"), (-1, "right")):
        m.bone(f"leg_{side}", "torso", list(mx((11, 38, 20), sx)), cubes=rbox(*xs(5, 17, sx), 20, 44, 10, 30, SC))
        K, Hk = mx((11, 20, 22), sx), mx((11, 7, 26), sx)
        m.bone(f"leg_{side}_shin", f"leg_{side}", list(K), cubes=rseg(K, Hk, 8, SL))
        Ft = mx((11, 2, 22), sx)
        foot = m.bone(f"leg_{side}_foot", f"leg_{side}_shin", list(Hk), cubes=[
            *rseg(Hk, Ft, 6, SL), *rbox(*xs(6, 16, sx), 0, 5, 12, 28, SL)])
        for dx in (-3, 0, 3):
            foot.cubes += chain([(11 + dx) * sx, 2.5, 12], [(0, 0.2, -1), (0, -0.7, -1)], [4, 3], [(2, 2), (1, 1)], M.CLAW)
    # ------------------------------------------------------------------ the long tail: spikes on the sides, top and below
    prev, z, y = "torso", 28, 43
    for k, (L, w) in enumerate([(18, 13), (18, 10), (18, 7), (18, 4)]):
        tb = m.bone(f"tail{k + 1}", prev, [0, y, z], rotation=[-3, 0, 0], cubes=[
            *rbox(-w / 2, w / 2, y - w / 2, y + w / 2, z - 1, z + L, gs(y - w / 2 + 2, 2.8))])
        for jj in range(4):
            zz = z + 1 + 4.2 * jj
            L2 = max(2, round(8 - 1.5 * k - 0.3 * jj))
            for sx in (1, -1):
                tb.cubes += chain([(w / 2 - 0.5) * sx, y + w / 2 - 1.5, zz], [(0.9 * sx, 0.35, 0.65)], [L2], [(1, 2)], SPIKE)
            tb.cubes += chain([0, y + w / 2 - 0.5, zz + 1], [(0, 0.7, 1)], [max(2, L2 - 2)], [(1, 2)], PLATE)
            tb.cubes += chain([0, y - w / 2 + 0.5, zz + 2], [(0, -0.8, 0.7)], [max(2, L2 - 1)], [(1, 2)], SPIKE)
        prev, z, y = f"tail{k + 1}", z + L, y - 1
    m.get("tail4").cubes += chain([0, y + 1, z - 2], [(0, 0.2, 1), (0, 0, 1)], [6, 5], [(3, 3), (1, 1)], SPIKE)
    if name in ("goremagala", "chaoticgoremagala"):
        # the purple veins that light up on its body when it raises its antennas (Kevin; the video's frenzy lines
        # along the neck, the chest, the front legs and under the wing arms); hidden (scale 0) unless in battle
        LIT = surf("antenna", glow="antenna")
        def veins(parent, pivot, lines):
            m.bone(f"veins_{parent}", parent, list(pivot),
                   cubes=[seg(p0, p1, 1, 1, LIT) for p0, p1 in lines])
        veins("neck1", [0, 44, -28], [((7.9 * sx, 46, -26), (7.9 * sx, 40, -34)) for sx in (1, -1)] +
              [((7.9 * sx, 38, -26), (7.9 * sx, 42, -33)) for sx in (1, -1)])
        veins("neck2", [0, 44, -33], [((7.4 * sx, 44, -32), (7.4 * sx, 40, -39)) for sx in (1, -1)])
        veins("chest", [0, 42, -14], [((11.6 * sx, 48, -28), (11.6 * sx, 38, -14)) for sx in (1, -1)] +
              [((11.6 * sx, 44, -24), (11.6 * sx, 34, -10)) for sx in (1, -1)])
        for sx, side in ((1, "left"), (-1, "right")):
            A0, A1 = mx((13, 36, -21), sx), mx((15, 17, -24), sx)
            veins(f"arm_{side}", A0, [((A0[0] + 4.9 * sx, A0[1] + 2, A0[2]), (A1[0] + 3.9 * sx, A1[1] + 2, A1[2]))])
            S, E, W = mx(S_, sx), mx(E_, sx), mx(W_, sx)
            veins(f"wing_{side}", S, [((S[0], S[1] - 4.8, S[2]), (E[0], E[1] - 4.8, E[2]))])
            veins(f"wing_{side}_fore", E, [((E[0] + 0.5 * sx, E[1] - 4.3, E[2]), (W[0] + 0.5 * sx, W[1] - 4.3, W[2]))])
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

def _R(e):
    from scipy.spatial.transform import Rotation
    return Rotation.from_euler("ZYX", [-e[2], e[1], -e[0]], degrees=True)

def _E(R):
    a, b, c = R.as_euler("ZYX", degrees=True)
    return [round(float(-c), 2), round(float(b), 2), round(float(-a), 2)]

def _rest_dirs():
    import numpy as np
    return [np.array(_norm(d)) for d in REST_DIRS] + [np.array(_norm(REST_FRONT))]

def solve_wing(pose):
    """local rotations (left side) of the wing bones for a pose given as world targets:
    pose = {"wrist": (x, y, z), "pole": dir, "claws": dir, "fingers": [dir1..dir4]}, or {"keep_arm": True, "fingers": ...}
    (the arm stays folded, only the fingers move)"""
    import numpy as np
    from scipy.optimize import minimize
    S, E, W = (np.array(v, float) for v in (S_, E_, W_))
    claw0 = np.array([0.1, -0.45, -0.89]); claw0 /= np.linalg.norm(claw0)   # the claws' main direction (rest)
    out = {}
    def fit(fun, x0=(0, 0, 0)):
        best = None
        for x in (x0, (40, 0, 0), (-40, 0, 0), (0, 0, 60), (0, 0, -60), (0, 60, 0), (0, -60, 0), (0, 90, 0), (0, -90, 0)):
            r = minimize(fun, x, method="Nelder-Mead", options={"xatol": 1e-3, "fatol": 1e-8, "maxiter": 8000})
            if best is None or r.fun < best.fun:
                best = r
        return [round(float(v), 2) for v in best.x]
    if pose.get("keep_arm"):
        out.update({"wing_left": [0, 0, 0], "wing_left_fore": [0, 0, 0], "wing_left_hand": [0, 0, 0]})
        return _fingers(pose, np.eye(3), out, fit)
    tE, tW = (np.array(v, float) for v in ik(pose["wrist"], pose["pole"]))
    def f_up(a):
        e = S + _rot(a) @ (E - S)
        return np.sum((e - tE) ** 2) + 1e-6 * np.sum(np.square(a))
    a_up = fit(f_up)
    R1 = _rot(a_up)
    E1 = S + R1 @ (E - S)
    a_fo = fit(lambda a: np.sum((E1 + R1 @ _rot(a) @ (W - E) - tW) ** 2) + 1e-6 * np.sum(np.square(a)))
    R2 = R1 @ _rot(a_fo)
    out["wing_left"], out["wing_left_fore"] = a_up, a_fo
    cd = np.array(pose.get("claws", (0, -0.3, -1)), float); cd /= np.linalg.norm(cd)
    fd0 = np.array(pose["fingers"][1], float); fd0 /= np.linalg.norm(fd0)
    d1 = _rest_dirs()[1]
    if pose.get("flat"):        # the three claws set down side by side on the ground: claws aimed, the hand level
        upv = np.array([0.0, 1.0, 0.0])
        a_ha = fit(lambda a: -np.dot(R2 @ _rot(a) @ claw0, cd) - np.dot(R2 @ _rot(a) @ upv, upv)
                   + 1e-6 * np.sum(np.square(a)))
    else:
        a_ha = fit(lambda a: -np.dot(R2 @ _rot(a) @ claw0, cd) - 0.6 * np.dot(R2 @ _rot(a) @ d1, fd0)
                   + 1e-6 * np.sum(np.square(a)))
    out["wing_left_hand"] = a_ha
    return _fingers(pose, R2 @ _rot(a_ha), out, fit)

def _fingers(pose, R3, out, fit):
    """each finger: its direction onto the target, and its web's plane onto the plane of the fan in that pose (roll)"""
    import numpy as np
    rd = _rest_dirs()
    pf = [np.array(v, float) / np.linalg.norm(v) for v in pose["fingers"]]
    for k, fd in enumerate(pf):
        n0 = np.cross(rd[k], rd[k + 1]); n0 /= np.linalg.norm(n0)
        j = k if k < 3 else 2
        npz = np.cross(pf[j], pf[j + 1]); npz /= np.linalg.norm(npz)
        out[f"wing_left_f{k + 1}"] = fit(lambda a: -np.dot(R3 @ _rot(a) @ rd[k], fd) - 0.5 * np.dot(R3 @ _rot(a) @ n0, npz)
                                         + 1e-6 * np.sum(np.square(a)))
    return _membrane(out)

def upper_open():
    """the upper arm's direction when the wing is open widest (the largest angle to the back over all poses): the
    upper sail is laid out at that opening, so no pose tears it"""
    import numpy as np
    b0 = np.array(_norm(UPPER_BODY)); best = None
    for pose in WING_POSES.values():
        if "wrist" not in pose:
            continue
        tE, _ = ik(pose["wrist"], pose["pole"])
        u = np.array(_norm([tE[i] - S_[i] for i in range(3)]))
        ang = math.acos(max(-1.0, min(1.0, float(np.dot(u, b0)))))
        if best is None or ang > best[0]:
            best = (ang, u)
    return [float(v) for v in best[1]]

def _upper_sheet(out):
    """the upper sail's strip bones (children of the chest): a flat fan from the back edge to the upper arm as it
    stands in that pose"""
    import numpy as np
    from scipy.spatial.transform import Rotation
    b0 = np.array(_norm(UPPER_BODY)); a0 = np.array(upper_open())
    u = _R(out["wing_left"]).as_matrix() @ np.array(_norm([E_[i] - S_[i] for i in range(3)]))
    n0 = np.array(_norm(list(np.cross(b0, a0)))); n1 = np.array(_norm(list(np.cross(b0, u))))
    for j in range(UPPER_SUBS):
        t = (j + 0.5) / UPPER_SUBS
        d0, d1 = np.array(_slerp(list(b0), list(a0), t)), np.array(_slerp(list(b0), list(u), t))
        F0 = np.column_stack([d0, n0, np.cross(d0, n0)]); F1 = np.column_stack([d1, n1, np.cross(d1, n1)])
        out[f"wing_left_a{j}"] = _E(Rotation.from_matrix(F1 @ F0.T))
    return out

def _membrane(out):
    """the sail's strip bones (children of the hand): each turned part-way between the two edges of its sector
    (the forearm and the first finger, then finger k and finger k+1)"""
    from scipy.spatial.transform import Rotation
    Rh = _R(out["wing_left_hand"])
    edges = [Rh.inv()] + [_R(out[f"wing_left_f{k}"]) for k in range(1, 5)]   # in the hand's frame
    for k in range(4):
        A, B = edges[k], edges[k + 1]
        rv = (A.inv() * B).as_rotvec()
        for j in range(SUBS[k]):
            out[f"wing_left_s{k}{j}"] = _E(A * Rotation.from_rotvec(rv * (j + 0.5) / SUBS[k]))
    return _upper_sheet(out)

def mirror(rots):
    """left-side rotations -> both sides"""
    out = {}
    for b, r in rots.items():
        out[b] = r
        out[b.replace("left", "right")] = [r[0], -r[1], -r[2]]
    return out

def _rotz(d, deg):
    c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (d[0] * c - d[1] * s_, d[0] * s_ + d[1] * c, d[2])

def _wall(wrist, back, bone):
    """the sail as a wall facing the player but joined to the body (Kevin): its inner edge (first finger) runs from the
    wrist to the top of the back, the great bone (last finger) a diagonal up and out, the fingers between evenly"""
    f1 = _norm([back[i] - wrist[i] for i in range(3)])
    f4 = _norm(bone)
    return [_slerp(f1, f4, q) for q in (0.0, 1 / 3, 2 / 3, 1.0)]

WING_POSES = {
    # folded (Kevin): the arm folded on the shoulder, the claws resting just above the front leg's joint, the sail
    # draped over the flank down to the belly line and back to the hips
    "fold": {"keep_arm": True, "fingers": [[t[i] - W_[i] for i in range(3)] for t in FOLD_TIPS]},
    # claws planted (Kevin + the video 0:17-0:24): the wing arms arch wide, elbows high, the claws set down far out
    # to each side a little ahead of the head, the sails rising behind the arms
    "planted": {"wrist": (48, 14, -50), "pole": (0.1, 1, -0.05), "claws": (0.1, -0.45, -0.89), "flat": True,
                # Kevin: the great bone spreads the sails out to the sides like a wall facing the hunter
                # the great bone (last finger) a long diagonal up and out, the sail stretched from it back to the
                # arm and the body: a wall facing the hunter
                "fingers": _wall((48, 14, -50), (8, 64, -6), (0.72, 0.69, 0.0))},
    # wide open (the reference's T-pose): the arm out, the fingers fanned back
    "spread": {"wrist": (70, 62, -16), "pole": (0, 0.3, 1), "claws": (0.4, 0.0, -1),
               "fingers": [(-0.7, -0.05, 0.71), (-0.35, -0.05, 0.94), (0.0, -0.05, 1), (0.35, -0.05, 0.94)]},
    # the threat display of the concept sheet (its roar): the arms raised high, the claws on top, the sails towering
    "display": {"wrist": (40, 76, -14), "pole": (1, 0.3, 0.6), "claws": (0.2, 0.5, -1),
                "fingers": [(-0.3, -0.3, 0.9), (-0.1, 0.05, 0.99), (0.1, 0.38, 0.92), (0.25, 0.6, 0.76)]},
    # raised high and forward (the Giant Slam's wind-up): claws over its head, the sails half open behind
    "raised": {"wrist": (34, 72, -40), "pole": (0.6, 0.3, 1), "claws": (0, 0.3, -1),
               "fingers": _wall((34, 72, -40), (8, 66, 4), (0.78, 0.53, 0.33))},
    # slammed down in front of it
    "slam": {"wrist": (26, 22, -66), "pole": (0.5, 1, 0.2), "claws": (0.1, -0.45, -0.89), "flat": True,
             "fingers": _wall((26, 22, -66), (8, 64, -6), (0.72, 0.69, 0.02))},
    # the claws set down ahead of its head, the sails half raised behind (exploding breath)
    "half": {"wrist": (46, 20, -52), "pole": (0.3, 1, 0), "claws": (0.1, -0.45, -0.89), "flat": True,
             "fingers": _wall((46, 20, -52), (8, 64, -6), (0.72, 0.67, 0.16))},
    # flight (Kevin: it does not unfold its arms, only the sails stretch out): the arm stays folded on the shoulder,
    # the sail stretched sideways (the rest layout) beats up and down
    # lying (sleep, faint): the arm folded, the sail draped out over the ground on each side like a blanket
    "lie": {"keep_arm": True, "fingers": [[t[i] - W_[i] for i in range(3)] for t in
                                         [(6, 62, 50), (26, 52, 58), (40, 44, 50), (50, 38, 34)]]},
    "fly_up": {"keep_arm": True, "fingers": [_rotz(d, 26) for d in REST_DIRS]},
    "fly_down": {"keep_arm": True, "fingers": [_rotz(d, -18) for d in REST_DIRS]},
}
WING_BONES = [f"wing_{s}{p}" for s in ("left", "right") for p in
              ["", "_fore", "_hand", "_f1", "_f2", "_f3", "_f4"] + [f"_s{k}{j}" for k in range(4) for j in range(SUBS[k])]
              + [f"_a{j}" for j in range(UPPER_SUBS)]]
SAIL_BONES = [b for b in WING_BONES if re.fullmatch(r"wing_(left|right)_(f\d|s\d\d|a\d+)", b)]
_CACHE = {}

def pose_euler(pose):
    """bone -> local rotation (both wings) at a pose; "rest" is the geometry's own layout (the stretched sail)"""
    if pose not in _CACHE:
        _CACHE[pose] = {b: [0, 0, 0] for b in WING_BONES} if pose == "rest" else mirror(solve_wing(WING_POSES[pose]))
    return _CACHE[pose]

def blend(parts, base="fold"):
    """the wings at [(pose, weight), ...] on top of a base pose (rotations averaged around the base)"""
    import numpy as np
    from scipy.spatial.transform import Rotation
    B = pose_euler(base)
    out = {}
    for b in WING_BONES:
        Rb = _R(B[b])
        v = np.zeros(3)
        for p, w in parts:
            if w:
                v = v + w * (Rb.inv() * _R(pose_euler(p)[b])).as_rotvec()
        out[b] = _E(Rb * Rotation.from_rotvec(v))
    return out

# ---------------------------------------------------------------------------------------------- animations
def anims(name, m):
    kf, wave, track, merge, anim, seq, SIDES = M.kf, M.wave, M.track, M.merge, M.anim, M.seq, M.SIDES
    S = {}
    def wings(fn, L, steps=24, base="fold"):
        """wing channels from fn(t) -> [(pose, weight), ...] over a base pose; the sails stretch as the wings open
        (fold = retracted)"""
        samples = [(L * i / steps, blend(fn(L * i / steps), base)) for i in range(steps + 1)]
        for b in WING_BONES:                              # keep each angle continuous in time (no +180 -> -180 jumps,
            prev = None                                   # which the game and Blockbench interpolate as a full spin)
            for t, bl in samples:
                v = list(bl[b])
                if prev is not None:
                    for c in range(3):
                        while v[c] - prev[c] > 180:
                            v[c] -= 360
                        while v[c] - prev[c] < -180:
                            v[c] += 360
                bl[b] = v
                prev = v
        out = {b: {"rotation": kf({round(t, 4): bl[b] for t, bl in samples})} for b in WING_BONES}
        b_ext = 0.0 if base == "fold" else 1.0
        ext = lambda t: max(0.0, min(1.0, b_ext * (1 - sum(w for p, w in fn(t))) +
                                     sum(w * (0.0 if p == "fold" else 1.0) for p, w in fn(t))))
        for b in SAIL_BONES:
            out[b]["scale"] = track(lambda t: [round(SAIL_REST + (1 - SAIL_REST) * ext(t), 4)] * 3, L, steps)
        return out
    frenzy = name.endswith("frenzy")         # (the chaotic one raises its antenna and lights up like a plain Gore)
    HAVE = {b.name for b in m.bones}
    LIT_BONES = [b.name for b in m.bones if b.name.startswith("veins_")]
    def antennas(fn, L, steps=24, quiver=0.0):
        """the horns (antennas) unfolding from along the face to straight up (fn 0..1); in Frenzy they already stand,
        so they only quiver"""
        out = {}
        if not frenzy:
            # Kevin: the antenna and the purple only appear when the Gore activates them: the antenna grows out as it
            # rises (hidden when calm), the purple lines light up with it
            grow = lambda t: [round(max(0.0, min(1.0, fn(t) * 1.6)), 3)] * 3
            lit = lambda t: [1.0 if fn(t) > 0.35 else 0.0] * 3
            for s, sx in SIDES:
                out[f"antenna_{s}_lit"] = {"scale": track(grow, L, steps)}
                out[f"antenna_{s}_dark"] = {"scale": [0, 0, 0]}
            for b in LIT_BONES:
                out[b] = {"scale": track(lit, L, steps)}
        for s, sx in SIDES:
            out[f"antenna_{s}"] = {"rotation": track(
                lambda t, sx=sx: [(0 if frenzy else 92 * fn(t)) + quiver * math.sin(t * 37 + sx), 0,
                                  (0 if frenzy else -8 * sx * fn(t))], L, steps)}
        return {k: v for k, v in out.items() if k in HAVE}               # Shagaru has horns, not antennas
    def flex(fn, L, steps=24):
        """the great bone bending at its joints, in the sail's plane (fn(t, j) in degrees for joint j = 1..3)"""
        import numpy as np
        from scipy.spatial.transform import Rotation
        d = np.array(_norm(REST_DIRS[3])); F = np.array(_norm(REST_FRONT))
        ax = np.cross(d, F); ax /= np.linalg.norm(ax)
        out = {}
        for j in range(1, len(SPAR)):
            def e(t, j=j):
                return _E(Rotation.from_rotvec(ax * math.radians(fn(t, j))))
            out[f"wing_left_f4_j{j}"] = {"rotation": track(lambda t, j=j: e(t, j), L, steps)}
            out[f"wing_right_f4_j{j}"] = {"rotation": track(lambda t, j=j: [e(t, j)[0], -e(t, j)[1], -e(t, j)[2]], L, steps)}
        return out
    def ripple(ch, L, amp=2.5, period=None):
        """the sails rippling (fingers and strips together, so the sail stays whole), on top of wing channels"""
        period = period or L
        for b in SAIL_BONES:
            k = 0.4 * (sum(map(ord, b[-3:])) % 7)
            rot = ch[b]["rotation"]
            base = {float(t): v for t, v in rot.items()} if isinstance(rot, dict) else {0.0: rot}
            n = 24
            keys = {}
            for i in range(n + 1):
                t = L * i / n
                tt = min(base, key=lambda q: abs(q - t))
                v = base[tt]
                keys[round(t, 4)] = [round(v[0] + amp * math.sin(2 * math.pi * t / period + k), 2), v[1], v[2]]
            ch[b]["rotation"] = kf(keys)
        return ch
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
        wings(lambda t: [("rest", 0.1 * max(0.0, tw(t)))], L, 60),
        {f"tail{k}": {"rotation": wave(3 + k, 3.0, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)})
    S["ground_idle"] = anim(L, idle, loop=True)

    # walk: the four legs in diagonal pairs, the folded wings (claws behind the head) rocking a little
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
    walkd = merge(w,
        {"body": {"position": track(lambda t: [0, 0.7 * abs(math.sin(2 * math.pi * t / T)), 0], T),
                  "rotation": wave(2, T, T, axis=2)}},
        {"neck1": {"rotation": wave(2, T / 2, T, axis=0, base=(10, 0, 0))}, "neck2": {"rotation": [4, 0, 0]},
         "head": {"rotation": wave(2, T / 2, T, phase=math.pi, axis=0, base=(-4, 0, 0))}},
        {f"tail{k}": {"rotation": wave(4 + 2 * k, T, T, phase=-0.6 * k, axis=1)} for k in range(1, 5)})
    S["ground_walk"] = anim(T, walkd, loop=True)

    # battle_idle (3 s): claws planted wide (they stay on the ground), sails raised and rippling, antennas up and
    # quivering; blind, the head sweeps low from side to side tasting the air, the weight rocks from claw to claw
    L = 3.0
    sweep = seq({0: 0, .6: 18, 1.2: 18, 1.7: -18, 2.4: -18, 3.0: 0})
    snap = lambda t: math.sin((t - 1.3) * math.pi / 0.25) if 1.3 < t < 1.55 else 0
    bi = merge(
        ripple(wings(lambda t: [("planted", 1.0)], L, 4), L, amp=2.5, period=L / 2),
        flex(lambda t, j: 3 * math.sin(4 * math.pi * t / L - 0.9 * j), L, 36),
        antennas(lambda t: 1.0, L, 36, quiver=4),
        {"body": {"position": track(lambda t: [0.4 * math.sin(2 * math.pi * t / L), 1.2 + 0.3 * math.sin(4 * math.pi * t / L), 0], L, 24),
                  "rotation": track(lambda t: [0, 0, 0.5 * math.sin(2 * math.pi * t / L)], L, 24)}},
        {"chest": {"rotation": track(lambda t: [5 + 0.6 * math.sin(4 * math.pi * t / L), sweep(t) * 0.06, 0], L, 24)}},
        {f"arm_{s}": {"rotation": [-8, 0, 6 * sx]} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": [-6, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [8, 0, 0]} for s, sx in SIDES},
        {"neck1": {"rotation": track(lambda t: [14 + 3 * math.sin(4 * math.pi * t / L) - 8 * snap(t), sweep(t) * 0.45, 0], L, 48)},
         "neck2": {"rotation": track(lambda t: [4, sweep(t) * 0.25, 0], L, 48)},
         "head": {"rotation": track(lambda t: [2 + 6 * snap(t), sweep(t) * 0.3, -sweep(t) * 0.25], L, 48)},
         "jaw": {"rotation": track(lambda t: [6 + 3 * math.sin(4 * math.pi * t / L) + 26 * max(0.0, snap(t)), 0, 0], L, 48)}},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [(5 if k == 1 else 2), 12 * math.sin(2 * math.pi * t / L - 0.8 * k), 0], L, 24)}
         for k in range(1, 5)})
    S["battle_idle"] = anim(L, bi, loop=True)

    # cry (2.4 s): crouches and draws back, then rears, the antennas snap up, the wings flare wide with a shudder and
    # it roars at the sky, the tail lashing
    L = 2.4
    dip = seq({0: 0, .35: 1, .6: 0, 2.4: 0})
    up = seq({0: 0, .35: 0, .75: 1, 1.9: 1, 2.4: 0})
    shake = lambda t: math.sin(t * 42) if 0.8 < t < 1.8 else 0
    cry = merge(
        ripple(wings(lambda t: [("display", up(t))], L, 30), L, amp=3, period=0.3),
        flex(lambda t, j: up(t) * (4 + 3 * math.sin(t * 30 - j)), L, 48),
        antennas(seq({0: 0, .5: 0, .7: 1, 2.0: 1, 2.4: 0}), L, 48, quiver=6),
        {"neck1": {"rotation": track(lambda t: [14 * dip(t) - 26 * up(t), 0, 0], L, 48)},
         "neck2": {"rotation": track(lambda t: [6 * dip(t) - 8 * up(t), 0, 0], L, 48)},
         "head": {"rotation": track(lambda t: [8 * dip(t) - 20 * up(t) + 3 * shake(t), 5 * shake(t), 0], L, 48)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .35: 2, .7: 42, 1.8: 42, 2.2: 2, 2.4: 2})(t) + 3 * shake(t), 0, 0], L, 48)},
         "chest": {"rotation": track(lambda t: [2 * dip(t) - 10 * up(t), 0, 0], L, 48)},
         "body": {"position": track(lambda t: [0, 3 * up(t), 2 * dip(t)], L, 48)}},
        {f"arm_{s}": {"rotation": track(lambda t: [-10 * up(t), 0, 0], L)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [8 * up(t), 18 * shake(t) * (k / 4), 0], L, 48)} for k in range(1, 5)})
    S["cry"] = anim(L, cry)

    # physical: Giant Slam (1.3 s): screech, rears up on its hind legs with the wings raised, slams the claws down
    L = 1.3
    rear = seq({0: 0, .45: 1, .62: 1, .78: 0, 1.0: 0, 1.3: 0})
    slam = seq({0: 0, .62: 0, .76: 1, 1.0: 1, 1.3: 0})
    hit = lambda t: math.exp(-((t - 0.8) / 0.06) ** 2)                   # the impact jolt
    phys = merge(
        antennas(seq({0: 0, .2: 1, 1.05: 1, 1.3: 0}), L, 26, quiver=5),
        {"chest": {"rotation": track(lambda t: [2.5 * hit(t), 0, 0], L, 39)}},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [10 * rear(t) if k < 3 else 0, 14 * hit(t) * k / 4, 0], L, 39)}
         for k in range(1, 5)},
        wings(lambda t: [("raised", rear(t)), ("slam", slam(t) * (1 - rear(t)))], L, 26),
        {"body": {"rotation": track(lambda t: [-22 * rear(t) + 3 * slam(t), 0, 0], L, 26),
                  "position": track(lambda t: [0, 8 * rear(t) + 1 * slam(t), 3 * rear(t) - 6 * slam(t)], L, 26)}},
        {f"arm_{s}": {"rotation": track(lambda t: [-35 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": track(lambda t: [40 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [24 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [-10 * rear(t), 0, 0], L, 26)} for s, sx in SIDES},
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
        antennas(o, L, 32, quiver=4),
        {f"tail{k}": {"rotation": track(lambda t, k=k: [0, -yaw(t) * 0.25 * k / 2, 0], L, 32)} for k in range(1, 5)},
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .45: -18, .7: -6, 1.25: -6, 1.6: 0})(t), yaw(t) * 0.45, 0], L, 48)},
         "neck2": {"rotation": track(lambda t: [0, yaw(t) * 0.3, 0], L, 48)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .45: -14, .7: 6, 1.25: 6, 1.6: 0})(t), yaw(t) * 0.3,
                                               -yaw(t) * 0.2], L, 48)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .45: 10, .65: 38, 1.25: 38, 1.45: 2, 1.6: 2})(t), 0, 0], L, 48)},
         "chest": {"rotation": track(lambda t: [-4 * o(t), yaw(t) * 0.1, 0], L, 48)},
         "body": {"position": track(lambda t: [0, 0.5 * o(t), 2 * o(t)], L, 48)}})
    S["special"] = anim(L, sp)

    # status (1.3 s): half opens its wings and shakes them to scatter its scales, head high
    L = 1.3
    o = seq({0: 0, .3: 1, 1.0: 1, 1.3: 0})
    st = merge(
        wings(lambda t: [("spread", 0.55 * o(t) + (0.08 * math.sin(t * 30) if 0.3 < t < 1.0 else 0))], L, 39),
        antennas(o, L, 39, quiver=7),
        {"neck1": {"rotation": track(lambda t: [-16 * o(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-6 * o(t), 5 * math.sin(t * 22) * (0.3 < t < 1.0), 0], L, 32)},
         "jaw": {"rotation": track(lambda t: [2 + 16 * o(t), 0, 0], L)},
         "body": {"rotation": track(lambda t: [0, 0, 3 * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}})
    S["status"] = anim(L, st)

    # faint (2.8 s): it raises its head screaming, antennas out, the wings flaring; then the legs buckle, the body sinks onto its belly
    # and rolls a little onto its flank, the head drops to the ground, the wings slump closed, the tail falls
    L = 2.8
    up = seq({0: 0, .45: 1, 1.15: 1, 1.6: 0})
    fall = seq({0: 0, 1.2: 0, 1.75: 0.7, 2.05: 1, 2.25: 0.95, 2.8: 1})          # a small bounce on landing
    tremble = lambda t: (math.sin(t * 55) * 3 if 0.45 < t < 1.2 else 0)
    fa = merge(
        wings(lambda t: [("spread", 0.6 * up(t)), ("lie", fall(t))], L, 28),
        antennas(seq({0: 0, .3: 1, 2.8: 1}), L, 28, quiver=6),             # Kevin: it collapses with its antennas out
        {"neck1": {"rotation": track(lambda t: [-36 * up(t) + 12 * fall(t), tremble(t) * 0.5 + 10 * fall(t), 0], L, 56)},
         "neck2": {"rotation": track(lambda t: [-12 * up(t) + 4 * fall(t), 8 * fall(t), 0], L, 28)},
         "head": {"rotation": track(lambda t: [-26 * up(t) - 8 * fall(t), tremble(t), -14 * fall(t)], L, 56)},
         "jaw": {"rotation": track(lambda t: [2 + 42 * up(t) + 16 * fall(t) * (1 - up(t)), 0, 0], L, 28)},
         "magala": {"rotation": track(lambda t: [0, 0, -20 * fall(t)], L, 28),
                    "position": track(lambda t: [-3 * fall(t), -20 * fall(t), 0], L, 28)},
         "chest": {"rotation": track(lambda t: [-8 * up(t), 0, 0], L, 28)}},
        {f"arm_{s}": {"rotation": track(lambda t: [80 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": track(lambda t: [-140 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"arm_{s}_foot": {"rotation": track(lambda t: [60 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [-70 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [120 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": track(lambda t: [-50 * fall(t), 0, 0], L, 28)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [(-10 if k == 1 else -3) * fall(t), 6 * fall(t), 0], L, 28)}
         for k in range(1, 5)})
    for b in SAIL_BONES:                                  # the sails sag, pulled in, as it falls
        fa[b]["scale"] = track(lambda t: [round(SAIL_REST + (1 - SAIL_REST) * 0.6 * up(t) - 0.12 * fall(t), 4)] * 3, L, 28)
    S["faint"] = anim(L, fa, loop="hold")

    # sleep (4 s): lying on its belly, legs folded under it, the wings folded over it like a blanket, the head resting
    # on the ground turned aside, the tail curled round; slow breathing
    L = 4.0
    sl = merge(
        wings(lambda t: [("lie", 1.0)], L, 2),
        {"magala": {"position": [0, -20, 0]}},
        {f"leg_{s}": {"rotation": [-70, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [120, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": [-50, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}": {"rotation": [80, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": [-140, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}_foot": {"rotation": [60, 0, 0]} for s, sx in SIDES},
        {"neck1": {"rotation": [22, 0, 0]}, "neck2": {"rotation": [6, -16, 0]}, "head": {"rotation": [-4, -14, 0]},
         "jaw": {"rotation": [0, 0, 0]}, "chest": {"rotation": wave(1.2, L, L, axis=0, base=(0, 0, 0))},
         "body": {"position": wave(0.4, L, L, axis=1)}},
        {f"tail{k}": {"rotation": [-8 if k == 1 else -2, -18 - 4 * k, 0]} for k in range(1, 5)})
    S["sleep"] = anim(L, sl, loop=True)
    # portrait_idle: the party portrait and the summary (head at rest, not lowered like the hunting idle)
    L = 3.0
    S["portrait_idle"] = anim(L, merge(
        {"body": {"position": wave(0.4, L, L, axis=1)}, "chest": {"rotation": wave(1.0, L, L, axis=0)},
         "jaw": {"rotation": wave(1.5, L, L, phase=2.0, axis=0, base=(2, 0, 0))}},
        {f"tail{k}": {"rotation": wave(3 + k, L, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)}), loop=True)
    # flight: the arms stay folded (claws behind the head), only the sails stretch out and beat; legs tucked
    def fly(T, pitch, lift):
        beat = lambda t: 0.5 + 0.5 * math.sin(2 * math.pi * t / T)
        d = merge(
            wings(lambda t: [("fly_up", beat(t)), ("fly_down", 1 - beat(t))], T, 24, base="rest"),
            flex(lambda t, j: 5 * math.cos(2 * math.pi * t / T - 0.5 * j), T, 24),
            {"magala": {"position": wave(lift, T, T, phase=math.pi / 2, axis=1, base=(0, 8, 0))},
             "body": {"rotation": [pitch, 0, 0]}},
            {f"arm_{s}": {"rotation": [50, 0, 0]} for s, sx in SIDES},
            {f"arm_{s}_low": {"rotation": [-70, 0, 0]} for s, sx in SIDES},
            {f"leg_{s}": {"rotation": [45, 0, 0]} for s, sx in SIDES},
            {f"leg_{s}_shin": {"rotation": [20, 0, 0]} for s, sx in SIDES},
            {f"leg_{s}_foot": {"rotation": [35, 0, 0]} for s, sx in SIDES},
            {"neck1": {"rotation": [-pitch * 0.6, 0, 0]}, "head": {"rotation": [-pitch * 0.3, 0, 0]}},
            {f"tail{k}": {"rotation": wave(3 + k, T, T, phase=-0.6 * k, axis=0, base=(-pitch * 0.3, 0, 0))} for k in range(1, 5)})
        return anim(T, d, loop=True)
    S["air_idle"] = fly(1.6, 4, 1.5)
    S["air_fly"] = fly(1.0, 16, 2.5)
    fold = pose_euler("fold")
    for a in S.values():                                  # calm: dark folded antennas, no lit veins
        if not frenzy:
            for b in LIT_BONES + ["antenna_left_lit", "antenna_right_lit"]:
                if b in HAVE:
                    a["bones"].setdefault(b, {}).setdefault("scale", [0, 0, 0])
            for b in ("antenna_left_dark", "antenna_right_dark"):
                if b in HAVE:
                    a["bones"].setdefault(b, {}).setdefault("scale", [0, 0, 0])
    lids = [b for b in ("lid_left", "lid_right") if b in HAVE]   # Shagaru's eyes: open, blinking now and then, shut asleep
    if lids:
        blink = lambda t: [1.0 if (2.0 < t < 2.12) or (4.6 < t < 4.72) else 0.0] * 3
        for k, a in S.items():
            for b in lids:
                if k == "sleep":
                    a["bones"][b] = {"scale": [1, 1, 1]}
                elif k == "faint":
                    a["bones"][b] = {"scale": {"0.0": [0, 0, 0], "2.0": [0, 0, 0], "2.3": [1, 1, 1]}}
                elif k in ("ground_idle", "portrait_idle"):
                    a["bones"][b] = {"scale": track(blink, a["animation_length"], 60)}
                else:
                    a["bones"][b] = {"scale": [0, 0, 0]}
    for a in S.values():                                  # without wing channels the wings hold the fold, sails retracted
        for b in WING_BONES:
            a["bones"].setdefault(b, {})
            a["bones"][b].setdefault("rotation", fold[b])
        for b in SAIL_BONES:
            a["bones"][b].setdefault("scale", [SAIL_REST] * 3)
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
                "hovering": {"poseTypes": ["HOVER"], "animations": ["q.look('head')", q("air_idle")]},
                "flying": {"poseTypes": ["FLY"], "animations": ["q.look('head')", q("air_fly")]},
                "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]}}}
