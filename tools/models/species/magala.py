# -*- coding: utf-8 -*-
"""#1055-1057 The Magala line (Monster Hunter): Gore Magala (+ Frenzy form), Chaotic Gore Magala, Shagaru Magala.

Rebuilt in 3.2.0 after the Monster Hunter World render and the wiki description. One skeleton for the three dragons,
SIX limbs: two front legs under the chest, two digitigrade hind legs, and two great wing-arms rising from the back.
At rest the wing-arms stand like stilts on each side (elbow high above the back, the huge wing-claws planted on the
ground ahead of the front legs) and the wings, folded, hang along the flanks like a cloak; they rise for the battle
stance (claws raised forward, as on the render), the roar, the attacks and flight. A short thick neck, an angular
eyeless head, a long tail lined with pale spikes.

* Gore Magala: dark exoskeleton (black with a navy sheen, blue-grey scale rims), wings covered in ragged black fur
  like a torn cape, a fur mane on the neck and shoulders; NO eyes; its horns lie folded along the sides of its face
  and its fangs (plates of the exoskeleton) folded against the jaw: they look like part of the armoured face.
  Frenzy (Mode Furie, battle form): the horns unfold upward and glow purple, the fangs open outward, purple patches
  on the plates and the fur, faint purple veins in the wings.
* Shagaru Magala: white-gold scales, pale gold membranes with gold veins, two great crescent horns, two glowing eyes,
  gold spikes along the back and the tail; it glows (golden aura).
* Chaotic Gore Magala: the moult stopped half-way: its right half (Bedrock -X) is Shagaru (gold scales, a crescent
  horn, the only eye), its left half Gore (black, fur, a raised horn, blind); bicolour glow (gold / purple).

Front = -Z, ground = y 0, the creature's right side is Bedrock -X (Blockbench shows +X on the screen's right)."""
import math
from modelgen import Model, Cube, rgb, shade, mix

DEX = {"goremagala": 1055, "goremagala_frenzy": 1055, "chaoticgoremagala": 1056, "shagarumagala": 1057}
FOLDER = {"goremagala": "1055_goremagala", "goremagala_frenzy": "1055_goremagala",
          "chaoticgoremagala": "1056_chaoticgoremagala", "shagarumagala": "1057_shagarumagala"}
FRAME_BONES = ("head", "jaw")

# ---------------------------------------------------------------------------------------------------- palettes
GORE = {
    "scale": rgb("#2C2A3A"), "scale_dark": rgb("#121119"), "scale_light": rgb("#525A74"), "scale_sheen": rgb("#7684A4"),
    "belly": rgb("#34323F"), "belly_dark": rgb("#22202B"),
    "plate": rgb("#22202C"), "plate_light": rgb("#5C6480"),
    "membrane": rgb("#24212C"), "membrane_dark": rgb("#0C0B10"), "vein": rgb("#2E2A3C"), "vein_glow": rgb("#B060FF"),
    "fur": rgb("#141218"), "fur_tip": rgb("#3C3846"),
    "claw": rgb("#2A2632"), "claw_tip": rgb("#D2AA5A"),
    "horn": rgb("#2A2236"), "horn_tip": rgb("#7A60A0"),
    "antenna": rgb("#6A3A9A"), "antenna_tip": rgb("#D8A0FF"), "antenna_glow": rgb("#D070FF"),
    "frenzy": rgb("#6E3A9E"),
    "spike": rgb("#5A6078"), "spike_tip": rgb("#A8B0C8"),
    "mouth": rgb("#4A1E36"), "tooth": rgb("#C8C2CC"),
    "eye": rgb("#FFE8A0"), "eye_glow": rgb("#FFD860"), "lid": rgb("#22202E"), "pupil": rgb("#2A1A08"),
}
GORE_SHINY = dict(GORE, **{           # ash grey with teal frenzy
    "scale": rgb("#3A3E44"), "scale_dark": rgb("#24272C"), "scale_light": rgb("#6A7078"), "scale_sheen": rgb("#6EA6AC"),
    "belly": rgb("#4C5056"), "belly_dark": rgb("#34373C"), "plate": rgb("#2E3136"), "plate_light": rgb("#6A7280"),
    "membrane": rgb("#34373C"), "membrane_dark": rgb("#1C1E22"), "vein": rgb("#3E5E64"), "vein_glow": rgb("#50F0E0"),
    "fur": rgb("#26292E"), "fur_tip": rgb("#5A6268"), "antenna": rgb("#2E7A80"), "antenna_tip": rgb("#90F0E8"),
    "antenna_glow": rgb("#60FFF0"), "frenzy": rgb("#2E8A8E"), "horn": rgb("#33373C"), "horn_tip": rgb("#6A9096"),
    "claw_tip": rgb("#C8D4DA"), "spike": rgb("#6A7078"), "spike_tip": rgb("#C8D0D4")})
SHAGARU = {
    "scale": rgb("#E4D6A8"), "scale_dark": rgb("#BFAA70"), "scale_light": rgb("#FAF2D6"), "scale_sheen": rgb("#E0C060"),
    "belly": rgb("#F0E8CC"), "belly_dark": rgb("#CFC096"),
    "plate": rgb("#D6BC72"), "plate_light": rgb("#FAE8A8"),
    "membrane": rgb("#F2E8C0"), "membrane_dark": rgb("#CDB678"), "vein": rgb("#C89A3A"), "vein_glow": rgb("#FFD050"),
    "fur": rgb("#F2E6B8"), "fur_tip": rgb("#D4AE50"),
    "claw": rgb("#8A7448"), "claw_tip": rgb("#F8F0D8"),
    "horn": rgb("#C8A450"), "horn_tip": rgb("#FFF4C8"),
    "antenna": rgb("#6A3A9A"), "antenna_tip": rgb("#D8A0FF"), "antenna_glow": rgb("#D070FF"),
    "frenzy": rgb("#D8B060"),
    "spike": rgb("#D4AE50"), "spike_tip": rgb("#FFF6D0"),
    "mouth": rgb("#8A4A3A"), "tooth": rgb("#FFFFF0"),
    "eye": rgb("#FFF6C0"), "eye_glow": rgb("#FFE070"), "lid": rgb("#D8C690"), "pupil": rgb("#3A240A"),
}
SHAGARU_SHINY = dict(SHAGARU, **{     # platinum and pale blue
    "scale": rgb("#D4DCE4"), "scale_dark": rgb("#A8B4C2"), "scale_light": rgb("#F2F6FA"), "scale_sheen": rgb("#9CC4E8"),
    "belly": rgb("#E8EEF4"), "belly_dark": rgb("#B8C2CC"), "plate": rgb("#A8BCD0"), "plate_light": rgb("#E4EEF8"),
    "membrane": rgb("#E0E8F0"), "membrane_dark": rgb("#A8B4C4"), "vein": rgb("#6A9AD0"), "vein_glow": rgb("#80D0FF"),
    "fur": rgb("#E4ECF4"), "fur_tip": rgb("#80A8D8"), "claw": rgb("#6A7484"), "horn": rgb("#9CB0C8"),
    "horn_tip": rgb("#F4FAFF"), "eye": rgb("#E8F8FF"), "eye_glow": rgb("#90E0FF"), "lid": rgb("#B8C4D0"),
    "spike": rgb("#8CA8C8"), "spike_tip": rgb("#F4FAFF")})
CHAOS = dict(GORE, _R=SHAGARU)
CHAOS_SHINY = dict(GORE_SHINY, _R=SHAGARU_SHINY)
PALETTES = {"goremagala": (GORE, GORE_SHINY),
            "goremagala_frenzy": (dict(GORE, _frenzy=True), dict(GORE_SHINY, _frenzy=True)),
            "chaoticgoremagala": (dict(CHAOS, _frenzy=True), dict(CHAOS_SHINY, _frenzy=True)),
            "shagarumagala": (SHAGARU, SHAGARU_SHINY)}

# ---------------------------------------------------------------------------------------------------- painting
LIGHT = {"up": 1.12, "north": 1.0, "south": 0.92, "east": 0.96, "west": 0.96, "down": 0.72}

def _h(*v):
    x = 0
    for a in v:
        x = (x * 1000003 + int(math.floor(a * 7.0)) * 92821) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 1274126177) & 0xFFFFFFFF; x ^= x >> 16
    return (x & 0xFFFF) / 65535.0

def _frac(v):
    return v - math.floor(v)

def _diamond(a, b, S):
    """overlapping diamond scales, free edge toward +a: (edge, t root..free edge, scale id)"""
    u, v = a / S + b / S, a / S - b / S
    p, q = _frac(u / 2 + .25), _frac(v / 2 + .25)
    return (p > 1 - 0.55 / S or q > 1 - 0.55 / S), (p + q) / 2, (math.floor(u / 2 + .25), math.floor(v / 2 + .25))

def _ab(face, p):
    x, y, z = p
    if face in ("east", "west"):
        return z, y
    if face in ("up", "down"):
        return z, x
    return -y, x

def _vein(y, z):
    """the wing's veins: a fan running from the elbow (y 43, z -8) down and back"""
    a = math.atan2(43 - y, z + 8)
    return any(abs(a - k) < 0.035 for k in (0.35, 0.65, 0.95, 1.25)) and 14 < y < 42

def side_pal(pal, p):
    """the chaotic one: the creature's right half (Bedrock -X) has Shagaru's colours"""
    r = pal.get("_R")
    return r if (r is not None and p[0] < -0.01) else pal

def _along(p, c):
    return (p[1] - c.origin[1]) / max(c.size[1], 1)

def surf(kind, *, belly_below=None, ragged=0, glow=None, S=2.5):
    """paint dict: every texel coloured from its model-space position (asymmetric palettes, scales...)
    kind: scale | belly | plate | fold | fang | spike | membrane | fur | claw | horn | antenna | mouth | tooth | eye |
    lid. belly_below: texels below this height use the belly colour; ragged: the bottom `ragged` rows of the side
    faces get torn (transparent) edges; glow: emissive key ('vein', 'antenna', 'eye', 'horn')."""
    def colour(pal, face, p, i, j, w, h, c):
        P = side_pal(pal, p)
        fr = bool(pal.get("_frenzy")) and P is pal                       # frenzy tints (never on the gold side)
        x, y, z = p
        n = (_h(x, y, z) - 0.5) * 0.06
        if kind == "scale":
            if belly_below is not None and y < belly_below and face != "up":
                return (P["belly_dark"] if int(math.floor(y)) % 3 == 0 else P["belly"]), n
            a, b = _ab(face, p)
            e, t, sid = _diamond(a, b, S)
            if e:
                return mix(P["scale"], P["scale_dark"], 0.75), n
            col = mix(P["scale_dark"], P["scale"], 0.35 + 0.65 * t)
            if t > 0.78:
                col = mix(col, P["scale_light"], 0.4)
            if _h(sid[0], sid[1], 3) > 0.96:
                col = mix(col, P["scale_sheen"], 0.25)
            if fr and _h(sid[0] * 2, sid[1], 11) > 0.88:
                col = mix(col, P["frenzy"], 0.4)
            return col, n
        if kind == "belly":
            return (P["belly_dark"] if int(math.floor(y)) % 3 == 0 else P["belly"]), n
        if kind in ("plate", "fold"):
            rim = i == 0 or j == 0 or i == w - 1 or j == h - 1
            g = j / max(h - 1, 1) if face not in ("up", "down") else 0.3
            col = mix(P["plate"], P["plate_light"], 0.25 * (1 - g))
            if rim:
                col = mix(col, P["frenzy"] if fr else P["plate_light"], 0.6)
            return col, n
        if kind == "fang":
            t = _along(p, c)
            tip = P["antenna_tip"] if fr else P["tooth"]
            return mix(P["plate"], tip, max(0.0, t - 0.25) ** 1.2), n * 0.5
        if kind == "spike":
            t = _along(p, c)
            return mix(P["spike"], P["spike_tip"], t ** 1.3), n * 0.5
        if kind in ("membrane", "fur"):
            if kind == "membrane" and _vein(y, z):
                return P["vein"], n * 0.3
            strand = _h(math.floor((z + x) * 1.4), 5)                  # fur strands running down the cape
            low = max(0.0, min(1.0, (34 - y) / 18)) if kind == "membrane" else _along(p, c)
            col = mix(P["membrane_dark" if kind == "membrane" else "fur"], P["membrane" if kind == "membrane" else "fur"],
                      0.25 + 0.75 * strand)
            col = mix(col, P["fur_tip"], 0.45 * low * (0.5 + 0.5 * strand))
            if fr and _h(math.floor((z + x) * 0.7), math.floor(y / 6), 21) > 0.82:
                col = mix(col, P["frenzy"], 0.5)
            return col, n * 0.3
        if kind in ("claw", "horn", "antenna"):
            t = _along(p, c)
            return mix(P[kind], P[kind + "_tip"], t ** 1.5), n * 0.5
        if kind == "eye" and face in ("east", "west") and abs(z - (c.origin[2] + c.size[2] / 2)) < 0.6:
            return P["pupil"], 0.0
        if kind in ("mouth", "tooth", "eye", "lid"):
            return P[kind], n * 0.4
        raise ValueError(kind)

    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            fx, fy, fw, fh = faces[face]
            i, j = X - fx, Y - fy
            if ragged and face in ("east", "west", "north", "south") and j >= fh - ragged:
                if _h(p[0] * 3 + p[2] * 3, 1, 0) < 0.3 + 0.55 * (j - (fh - ragged)) / max(ragged, 1):
                    px[X, Y] = (0, 0, 0, 0)
                    continue
            col, n = colour(pal, face, p, i, j, fw, fh, c)
            px[X, Y] = shade(col, LIGHT[face] * (1 + n))

    def glow_fn(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            P = side_pal(pal, p)
            fx, fy, fw, fh = faces[face]
            j = Y - fy
            x, y, z = p
            if glow == "vein":
                if not pal.get("_veins") or (pal.get("_R") is not None and P is not pal and P.get("vein_glow") is None):
                    continue
                if ragged and face in ("east", "west", "north", "south") and j >= fh - ragged:
                    continue
                if _vein(y, z):
                    px[X, Y] = P["vein_glow"][:3] + (140,)
            elif glow == "antenna":
                if not pal.get("_antenna"):
                    continue
                t = _along(p, c)
                if t > 0.2:
                    px[X, Y] = P["antenna_glow"][:3] + (int(90 + 165 * t),)
            elif glow == "eye":
                if face in ("east", "west") and abs(z - (c.origin[2] + c.size[2] / 2)) < 0.6:
                    continue
                px[X, Y] = P["eye_glow"][:3] + (255,)
            elif glow == "horn":
                if not pal.get("_horn"):
                    continue
                t = _along(p, c)
                if t > 0.55:
                    px[X, Y] = P["horn_tip"][:3] + (int(200 * (t - 0.55) / 0.45),)
    d = {"fn3": fn3, "base": None}
    if glow:
        d["glow_fn"] = glow_fn
    return d

SCALE = surf("scale")
SCALE_BIG = surf("scale", S=3.2)
PLATE = surf("plate")
FOLD = surf("fold")
CLAW = surf("claw")
HORN = surf("horn", glow="horn")
SPIKE = surf("spike")
TOOTH = surf("tooth")
MOUTH = surf("mouth")
FUR = surf("fur")

# ---------------------------------------------------------------------------------------------------- shapes
def dir_rot(d):
    """cube rotation turning the cube's +Y axis toward d"""
    n = math.sqrt(sum(v * v for v in d))
    dx, dy, dz = (v / n for v in d)
    return [round(math.degrees(math.asin(max(-1.0, min(1.0, -dz)))), 1), 0, round(math.degrees(math.atan2(dx, dy)), 1)]

def seg(p0, p1, w, d, paint, sunk=1.0, inflate=None):
    """a cube of section w x d running from p0 to p1 (its +Y axis along the segment)"""
    v = [b - a for a, b in zip(p0, p1)]
    L = math.sqrt(sum(x * x for x in v))
    x, y, z = p0
    return Cube([x - w / 2, y - sunk, z - d / 2], [w, max(1, int(round(L + sunk))), d], paint,
                rotation=dir_rot(v), pivot=list(p0), inflate=inflate)

def chain(p, dirs, lens, widths, paint):
    out = []
    x, y, z = p
    for i, (dd, L, w) in enumerate(zip(dirs, lens, widths)):
        n = math.sqrt(sum(v * v for v in dd))
        dh = [v / n for v in dd]
        wx, wz = w if isinstance(w, tuple) else (w, w)
        sunk = min(wx, wz) / 2 if i == 0 else 0.5
        pt = paint[i] if isinstance(paint, list) else paint
        out.append(Cube([x - wx / 2, y - sunk, z - wz / 2], [wx, int(round(L + sunk)), wz], pt,
                        rotation=dir_rot(dd), pivot=[x, y, z]))
        x, y, z = x + dh[0] * (L - 0.5), y + dh[1] * (L - 0.5), z + dh[2] * (L - 0.5)
    return out

def box(x0, x1, y0, y1, z0, z1, paint, inflate=None):
    return Cube([x0, y0, z0], [x1 - x0, y1 - y0, z1 - z0], paint, inflate=inflate)

def sbox(hw, y0, y1, z0, z1, paint):
    return box(-hw, hw, y0, y1, z0, z1, paint)

def xs(x0, x1, sx):
    """the x range [x0, x1] (left side) mirrored to the side sx"""
    return (x0, x1) if sx > 0 else (-x1, -x0)

def mx(p, sx):
    return (p[0] * sx, p[1], p[2])

def crescent(sx, p, big=True):
    """Shagaru's great horn: rises from the skull, bends back, then sweeps forward like a crescent"""
    k = 1.0 if big else 0.7
    return chain(p, [(0.25 * sx, 1, 0.45), (0.2 * sx, 1, 0.1), (0.1 * sx, 0.9, -0.35), (0.05 * sx, 0.5, -1)],
                 [round(9 * k), round(9 * k), round(8 * k), round(7 * k)], [(3, 4), (3, 3), (2, 2), (1, 1)], HORN)

# key joints (left side; the right one mirrored)
SHOULDER = (9, 34, -16)          # wing-arm root, on top of the chest
ELBOW = (17, 43, -8)             # the wing's elbow, above the back
WRIST = (21, 5, -31)             # the wing-claws rest on the ground ahead of the front legs
ELBOW_M = (17.5, 43, -8)         # pivot of the folded wing (cape)

# ---------------------------------------------------------------------------------------------------- model
def build(name):
    gold = name == "shagarumagala"
    chaos = name == "chaoticgoremagala"
    frenzy = name == "goremagala_frenzy"
    m = Model(name, DEX[name], (256, 256))
    m.bone("magala", None, [0, 0, 0])
    m.bone("body", "magala", [0, 26, 0])
    BELLY = 19
    m.bone("torso", "body", [0, 26, 4], cubes=[
        sbox(8, 15, 33, -8, 20, surf("scale", belly_below=BELLY)),
        sbox(6, 33, 36, -6, 18, SCALE_BIG),
        sbox(10, 19, 31, 4, 18, surf("scale", belly_below=BELLY))])
    m.bone("chest", "body", [0, 27, -8], cubes=[
        sbox(9, 13, 34, -28, -6, surf("scale", belly_below=BELLY - 1)),
        sbox(7, 34, 37, -26, -6, SCALE_BIG),
        sbox(11, 23, 33, -22, -10, surf("scale", belly_below=BELLY))])
    # back: a ridge of dark plates (Gore) / gold spikes (Shagaru) along the spine; mane of fur on neck and shoulders
    mane = m.bone("mane", "body", [0, 37, -10])
    for k, z in enumerate(range(-24, 18, 5)):
        top = 37 if z < -6 else 36
        for sx in (1, -1):
            gs = gold or (chaos and sx < 0)
            if gs:
                mane.cubes += chain([2.5 * sx, top - 0.5, z], [(0.2 * sx, 1, 0.5), (0, 0.6, 1)], [3, 3], [(2, 2), (1, 1)],
                                    SPIKE)
            else:
                mane.cubes.append(seg([2.5 * sx, top - 0.5, z], [3.5 * sx, top + 2.5, z + 4], 3, 2, PLATE))
    if not gold:                                                          # fur mane (Gore side)
        for k, (z, y, L) in enumerate([(-30, 36, 8), (-25, 38, 9), (-20, 38, 9), (-15, 38, 8), (-10, 37, 7)]):
            for sx in ((1, -1) if not chaos else (1,)):
                mane.cubes.append(seg([5 * sx, y - 1, z], [9 * sx, y + L * 0.45, z + L * 0.85], 3, 3, FUR))
    # ------------------------------------------------------------------ neck and head
    m.bone("neck1", "chest", [0, 30, -26], rotation=[-10, 0, 0], cubes=[
        box(-6, 6, 22, 35, -38, -24, surf("scale", belly_below=25)), box(-4, 4, 35, 37, -37, -25, PLATE)])
    m.bone("neck2", "neck1", [0, 31, -36], rotation=[6, 0, 0], cubes=[
        box(-5, 5, 24, 35, -47, -35, surf("scale", belly_below=26)), box(-3.5, 3.5, 35, 37, -46, -36, PLATE)])
    head = m.bone("head", "neck2", [0, 30, -45], rotation=[14, 0, 0], cubes=[
        box(-6, 6, 25, 36, -60, -44, SCALE),                                 # skull
        box(-4, 4, 24, 31, -70, -58, SCALE),                                 # snout
        box(-3, 3, 31, 33, -69, -56, PLATE),                                 # nose ridge
        box(-7, 7, 35, 38, -58, -43, PLATE),                                 # hood
        box(-5, 5, 33, 35, -62, -56, PLATE)])                                # brow (no eyes: a smooth armoured mask)
    for sx in (1, -1):
        gs = gold or (chaos and sx < 0)
        head.cubes.append(box(*xs(6, 7, sx), 27, 34, -58, -46, PLATE))          # cheek armour
        head.cubes += chain([3.5 * sx, 37.5, -47], [(0.25 * sx, 0.55, 1), (0.1 * sx, 0.2, 1)], [5, 4], [(2, 3), (1, 2)],
                            SPIKE if gs else PLATE)                         # crest plates at the back of the skull
    m.bone("jaw", "head", [0, 25, -46], cubes=[
        box(-4.5, 4.5, 20, 25, -68, -46, surf("scale", belly_below=22)),
        box(-3.5, 3.5, 24.6, 25.6, -67, -48, MOUTH)])
    jaw = m.get("jaw")
    for k in range(5):                                                       # teeth
        for sx in (1, -1):
            z = -67 + 4 * k
            head.cubes.append(box(3.0 * sx - 0.5, 3.0 * sx + 0.5, 22.5, 24.5, z, z + 1, TOOTH))
            jaw.cubes.append(box(3.4 * sx - 0.5, 3.4 * sx + 0.5, 25, 27, z + 2, z + 3, TOOTH))
    # horns: Gore folds them along the sides of its face (they look like cheek armour), unfolds them in frenzy;
    # fangs: exoskeleton plates folded against the jaw, open outward in frenzy. Shagaru's side: crescent horn + eye.
    for sx, side in ((1, "left"), (-1, "right")):
        gs = gold or (chaos and sx < 0)
        if gs:
            hb = m.bone(f"horn_{side}", "head", [4 * sx, 37, -50])
            hb.cubes += crescent(sx, [4 * sx, 37, -50])
            hb.cubes += chain([6 * sx, 35, -46], [(0.6 * sx, 0.5, 1), (0.4 * sx, 0.2, 1)], [5, 5], [(2, 2), (1, 1)], HORN)
            eb = m.bone(f"eye_{side}", "head", [6 * sx, 31, -54])
            eb.cubes.append(box(*xs(6, 7, sx), 30, 32, -57, -52, surf("eye", glow="eye")))
            m.bone(f"lid_{side}", "head", [6 * sx, 31, -54], cubes=[
                Cube([6 * sx - (1 if sx < 0 else 0), 30, -57], [1, 2, 5], surf("lid"), inflate=0.05)])
        else:
            up = frenzy or chaos
            ab = m.bone(f"antenna_{side}", "head", [6 * sx, 35, -45])
            if up:                       # unfolded: rising up and back from the back of the skull, glowing
                ab.cubes += chain([6 * sx, 35, -45], [(0.3 * sx, 1, 0.45), (0.3 * sx, 0.9, 0.75), (0.2 * sx, 0.5, 1)],
                                  [8, 8, 7], [(2, 3), (2, 2), (1, 1)], surf("antenna", glow="antenna"))
            else:                        # folded: a blade lying forward along the side of the face
                ab.cubes += chain([7 * sx, 34.5, -45], [(0.02 * sx, -0.06, -1), (-0.02 * sx, -0.1, -1), (-0.06 * sx, -0.12, -1)],
                                  [7, 6, 5], [(1, 4), (1, 3), (1, 2)], FOLD)
            fb = m.bone(f"fang_{side}", "head", [4 * sx, 25, -64])
            if up:                       # opened: splayed outward and forward like mandibles
                fb.cubes += chain([4.5 * sx, 25.5, -64], [(0.7 * sx, -0.5, -0.5), (0.3 * sx, -0.6, -0.8)], [5, 4],
                                  [(2, 2), (1, 1)], surf("fang", glow="antenna"))
            else:                        # folded down and back against the jaw
                fb.cubes += chain([4.6 * sx, 25.5, -64], [(0.05 * sx, -0.7, 0.6), (0.0, -0.4, 1)], [4, 3],
                                  [(1, 2), (1, 1)], surf("fang"))
    # ------------------------------------------------------------------ front legs (under the chest)
    for sx, side in ((1, "left"), (-1, "right")):
        gs = gold or (chaos and sx < 0)
        A0, A1, A2 = mx((8, 22, -20), sx), mx((10, 12, -24), sx), mx((10, 3, -22), sx)
        m.bone(f"arm_{side}", "chest", list(A0), cubes=[seg(A0, A1, 6, 6, SCALE), box(*xs(5, 11, sx), 17, 25, -24, -16, SCALE)])
        m.bone(f"arm_{side}_low", f"arm_{side}", list(A1), cubes=[seg(A1, A2, 5, 5, SCALE)])
        foot = m.bone(f"arm_{side}_foot", f"arm_{side}_low", list(A2), cubes=[box(*xs(7, 13, sx), 0, 4, -28, -19, SCALE)])
        for dx in (-2, 0, 2):
            foot.cubes += chain([(10 + dx) * sx, 2, -28], [(0, 0.2, -1), (0, -0.7, -1)], [3, 3], [(2, 2), (1, 1)], CLAW)
    # ------------------------------------------------------------------ wing-arms and folded wings (the cape)
    for sx, side in ((1, "left"), (-1, "right")):
        gs = gold or (chaos and sx < 0)
        S, E, W = mx(SHOULDER, sx), mx(ELBOW, sx), mx(WRIST, sx)
        m.bone(f"wing_{side}", "chest", list(S), cubes=[seg(S, E, 7, 7, SCALE)])
        fore = m.bone(f"wing_{side}_fore", f"wing_{side}", list(E), cubes=[
            seg(E, W, 6, 6, SCALE), box(E[0] - 4, E[0] + 4, E[1] - 4, E[1] + 4, E[2] - 4, E[2] + 4, SCALE)])
        fore.cubes += chain([E[0], E[1] + 3, E[2] - 2], [(0.2 * sx, 1, -0.4), (0.1 * sx, 0.4, -1)], [5, 4],
                            [(2, 2), (1, 1)], CLAW)                       # the elbow's hooked claw
        hand = m.bone(f"wing_{side}_hand", f"wing_{side}_fore", list(W), cubes=[
            box(W[0] - 4, W[0] + 4, 0, 7, W[2] - 5, W[2] + 4, SCALE)])
        for dx in (-3, 0, 3):                                             # three great hooked talons, forward
            hand.cubes += chain([W[0] + dx, 4, W[2] - 5], [(0, 0.5, -1), (0, -0.3, -1), (0, -0.9, -0.4)], [4, 4, 3],
                                [(2, 3), (2, 2), (1, 1)], CLAW)
        hand.cubes += chain([W[0] - 3 * sx, 6, W[2] - 1], [(-0.5 * sx, 1, -0.4), (-0.6 * sx, 0.3, -1)], [5, 4],
                            [(2, 2), (1, 1)], CLAW)                       # the opposable thumb, hooking inward
        # the folded wing: hangs from the elbow along the flank to the hips like a ragged fur cloak
        wm = m.bone(f"wingm_{side}", f"wing_{side}", list(mx(ELBOW_M, sx)), rotation=[0, 0, -12 * sx])
        mem = surf("membrane", ragged=5, glow="vein")
        for k, z in enumerate(range(-12, 42, 6)):
            top = round(44 - max(0, z + 8) * 0.25)
            bot = round(18 - (z + 12) * 0.1)
            wm.cubes.append(box(*xs(17, 19, sx), bot, top, z, z + 6, mem))
        if not gs:                                                        # long fur tatters at the hem
            for k, z in enumerate(range(-10, 42, 4)):
                bot = 18 - (z + 12) * 0.1
                L = 4 + 4 * _h(k, 3)
                wm.cubes.append(seg(mx((18, bot + 1, z), sx), mx((18.6, bot - L, z + 2), sx), 2, 2, surf("fur")))
        wm.cubes.append(seg(mx((17.5, 43, -10), sx), mx((17.5, 32, 42), sx), 3, 3, SCALE))   # the wing's finger bone
        for z in (2, 14, 26, 36):                                         # small spikes along it
            y = 43 - (z + 10) * 0.21
            wm.cubes += chain([17.5 * sx, y + 1, z], [(0.3 * sx, 1, 0.6)], [3], [(1, 2)], SPIKE)
    # ------------------------------------------------------------------ hind legs
    for sx, side in ((1, "left"), (-1, "right")):
        m.bone(f"leg_{side}", "torso", list(mx((9, 27, 12), sx)), cubes=[
            box(*xs(4, 14, sx), 13, 32, 4, 22, surf("scale", belly_below=None))])
        K, Hk = mx((10, 14, 18), sx), mx((10, 7, 26), sx)
        m.bone(f"leg_{side}_shin", f"leg_{side}", list(K), cubes=[seg(K, Hk, 7, 7, SCALE)])
        Ft = mx((10, 1, 22), sx)
        foot = m.bone(f"leg_{side}_foot", f"leg_{side}_shin", list(Hk), cubes=[
            seg(Hk, Ft, 5, 5, SCALE), box(*xs(7, 13, sx), 0, 4, 12, 23, SCALE)])
        for dx in (-2, 0, 2):
            foot.cubes += chain([(10 + dx) * sx, 2, 12], [(0, 0.2, -1), (0, -0.7, -1)], [3, 3], [(2, 2), (1, 1)], CLAW)
    # ------------------------------------------------------------------ tail (spiked)
    prev, z, y = "torso", 18, 27
    for k, (L, w) in enumerate([(16, 10), (16, 8), (15, 6), (15, 4)]):
        tb = m.bone(f"tail{k + 1}", prev, [0, y, z], rotation=[-4, 0, 0], cubes=[
            box(-w / 2, w / 2, y - w / 2 - 1, y + w / 2 - 1, z - 1, z + L, surf("scale", belly_below=y - w / 2 + 1))])
        for jj in range(3):
            zz = z + 2 + 5 * jj
            for sx in (1, -1):
                gs = gold or (chaos and sx < 0)
                L2 = max(2, 5 - k)
                tb.cubes += chain([(w / 2 - 0.5) * sx, y + w / 2 - 2, zz], [(0.8 * sx, 0.6, 0.7)], [L2], [(1, 2)],
                                  SPIKE)
        if gold:
            tb.cubes += chain([0, y + w / 2 - 1, z + 6], [(0, 1, 0.6)], [3 + (3 - k)], [(2, 2)], SPIKE)
        prev, z, y = f"tail{k + 1}", z + L, y - 1
    m.get("tail4").cubes += chain([0, y + 1, z - 2], [(0, 0.2, 1), (0, 0, 1)], [5, 4], [(3, 3), (1, 1)], SPIKE)
    m.pack()
    return m

HEIGHT_SKIP = ("horn", "antenna", "mane")

# ---------------------------------------------------------------------------------------------------- animation kit
def kf(points):
    return {(f"{t:g}" if t else "0.0"): [round(x, 3) for x in v] for t, v in sorted(points.items())}

def wave(amp, period, length, phase=0.0, axis=0, base=(0, 0, 0), steps=16):
    pts = {}
    for i in range(steps + 1):
        t = length * i / steps
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (t / period) + phase)
        pts[round(t, 4)] = v
    return kf(pts)

def track(fn, length, steps=24):
    """channel from a function of time -> [x, y, z]"""
    return kf({round(length * i / steps, 4): fn(length * i / steps) for i in range(steps + 1)})

def merge(*ds):
    out = {}
    for d in ds:
        for b, ch in d.items():
            out.setdefault(b, {}).update(ch)
    return out

def anim(length, bones, loop=None):
    a = {"animation_length": round(length, 4), "bones": bones}
    if loop is True:
        a["loop"] = True
    elif loop == "hold":
        a["loop"] = "hold_on_last_frame"
    return a

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def seq(keys):
    """piecewise smooth interpolation through {t: value} (value float or list)"""
    ts = sorted(keys)
    def f(t):
        if t <= ts[0]:
            return keys[ts[0]]
        for a, b in zip(ts, ts[1:]):
            if a <= t <= b:
                u = ease((t - a) / (b - a))
                va, vb = keys[a], keys[b]
                if isinstance(va, (int, float)):
                    return va + (vb - va) * u
                return [x + (y - x) * u for x, y in zip(va, vb)]
        return keys[ts[-1]]
    return f

SIDES = (("left", 1), ("right", -1))

def spread(f, sx):
    """folded wing (cape) opening outward (f = 0 folded .. 1 horizontal .. 1.6 raised)"""
    return [0, -10 * f * sx, -80 * f * sx]

def cape(fc, fs, sx):
    """the folded wing raised and spread (fs) while the wing-arm is lifted (fc): the arm's tilt is undone so the cape
    rises up and back like the render's ragged wings instead of dragging on the ground"""
    return [30 * fc, -12 * fs * sx, -100 * fs * sx]

def raise_claws(f, sx):
    """the wing-arms lifted, claws held forward at head height (the render's threat pose): (arm, forearm, hand)"""
    return [-30 * f, 0, -8 * f * sx], [-22 * f, 0, 4 * f * sx], [40 * f, 0, 0]

BONES = {}

def anims(name, m):
    BONES[name] = {b.name for b in m.bones}
    gold = name == "shagarumagala"
    S = {}
    eyes = [b for b in BONES[name] if b.startswith("eye_")]
    lids = [b for b in BONES[name] if b.startswith("lid_")]
    def eyes_open(d):
        for e in lids:
            d[e] = {"scale": [0, 0, 0]}
        return d
    def eyes_shut(d):
        for e in eyes:
            d[e] = {"scale": [0, 0, 0]}
        return d
    def claws(fn, L, steps=24):
        """wing-arm channels from f(t) (0 resting .. 1 raised)"""
        d = {}
        for s, sx in SIDES:
            d[f"wing_{s}"] = {"rotation": track(lambda t, sx=sx: raise_claws(fn(t), sx)[0], L, steps)}
            d[f"wing_{s}_fore"] = {"rotation": track(lambda t, sx=sx: raise_claws(fn(t), sx)[1], L, steps)}
            d[f"wing_{s}_hand"] = {"rotation": track(lambda t, sx=sx: raise_claws(fn(t), sx)[2], L, steps)}
        return d

    # ground_idle: breathing, a slow sway of the neck and tail, the cape ripples
    L = 3.0
    idle = merge(
        {"body": {"position": wave(0.4, L, L, axis=1)}},
        {"chest": {"rotation": wave(1.0, L, L, axis=0)}},
        {"neck1": {"rotation": wave(2.5, L, L, phase=0.5, axis=0)}, "head": {"rotation": wave(3, L, L, phase=1.0, axis=1)},
         "jaw": {"rotation": wave(1.5, L, L, phase=2.0, axis=0, base=(2, 0, 0))}},
        {f"wingm_{s}": {"rotation": wave(2.0, L, L, phase=0.3, axis=2)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": wave(3 + k, L, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)})
    S["ground_idle"] = anim(L, eyes_open(idle), loop=True)

    # walk: the wing-claws and the hind legs in diagonal pairs, the front legs with the claw of their side
    T = 1.4
    w = {}
    for s, sx in SIDES:
        ph = 0 if sx > 0 else math.pi
        a = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph)
        b = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph))
        a2 = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph + math.pi)
        b2 = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph + math.pi))
        w[f"wing_{s}"] = {"rotation": track(lambda t, a=a: [9 * a(t), 0, 0], T)}
        w[f"wing_{s}_fore"] = {"rotation": track(lambda t, b=b: [-10 * b(t), 0, 0], T)}
        w[f"wing_{s}_hand"] = {"rotation": track(lambda t, a=a, b=b: [-9 * a(t) + 10 * b(t), 0, 0], T)}
        w[f"arm_{s}"] = {"rotation": track(lambda t, a=a: [14 * a(t), 0, 0], T)}
        w[f"arm_{s}_low"] = {"rotation": track(lambda t, b=b: [-16 * b(t), 0, 0], T)}
        w[f"arm_{s}_foot"] = {"rotation": track(lambda t, a=a, b=b: [-14 * a(t) + 16 * b(t), 0, 0], T)}
        w[f"leg_{s}"] = {"rotation": track(lambda t, a=a2: [18 * a(t), 0, 0], T)}
        w[f"leg_{s}_shin"] = {"rotation": track(lambda t, b=b2: [16 * b(t), 0, 0], T)}
        w[f"leg_{s}_foot"] = {"rotation": track(lambda t, a=a2, b=b2: [-18 * a(t) - 16 * b(t), 0, 0], T)}
        w[f"wingm_{s}"] = {"rotation": wave(3, T, T, phase=ph, axis=2)}
    walkd = merge(w,
        {"body": {"position": track(lambda t: [0, 0.6 * abs(math.sin(2 * math.pi * t / T)), 0], T),
                  "rotation": wave(2, T, T, axis=2)}},
        {"neck1": {"rotation": wave(2, T / 2, T, axis=0)}, "head": {"rotation": wave(2, T / 2, T, phase=math.pi, axis=0)}},
        {f"tail{k}": {"rotation": wave(4 + 2 * k, T, T, phase=-0.6 * k, axis=1)} for k in range(1, 5)})
    S["ground_walk"] = anim(T, eyes_open(walkd), loop=True)

    # battle_idle: the threat pose of the render: wing-claws raised forward at head height, cape thrown open, head low
    L = 2.0
    bi = merge(
        claws(lambda t: 1.0 + 0.06 * math.sin(2 * math.pi * t / L), L),
        {"body": {"position": wave(0.6, L, L, axis=1, base=(0, -1.5, 0))}},
        {"chest": {"rotation": wave(1.5, L, L, axis=0, base=(4, 0, 0))}},
        {"neck1": {"rotation": wave(2, L, L, axis=0, base=(8, 0, 0))}, "neck2": {"rotation": [2, 0, 0]},
         "head": {"rotation": wave(3, L, L, phase=1, axis=0, base=(-6, 0, 0))},
         "jaw": {"rotation": wave(4, L / 2, L, axis=0, base=(8, 0, 0))}},
        {f"wingm_{s}": {"rotation": wave(4, L, L, axis=2, base=cape(1.0, 1.25, sx))} for s, sx in SIDES},
        {f"tail{k}": {"rotation": wave(5 + k, L, L, phase=-0.7 * k, axis=1, base=(4 if k == 1 else 0, 0, 0))}
         for k in range(1, 5)})
    S["battle_idle"] = anim(L, eyes_open(bi), loop=True)

    # cry: rears its neck, raises the claws, throws the cape wide open and roars, head shaking
    L = 2.2
    shake = lambda t: 4 * math.sin(t * 40) if 0.6 < t < 1.6 else 0
    up = seq({0: 0, .55: 1, 1.7: 1, 2.2: 0})
    cry = merge(
        claws(up, L),
        {"neck1": {"rotation": track(lambda t: [-22 * up(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-14 * up(t), shake(t), 0], L, 44)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .45: 38, 1.6: 38, 2.0: 2, 2.2: 2})(t), 0, 0], L)},
         "chest": {"rotation": track(lambda t: [-6 * up(t), 0, 0], L)}},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: cape(up(t), 1.1 * up(t), sx), L)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [6 * up(t), 0, 0], L)} for k in (1, 2)})
    S["cry"] = anim(L, eyes_open(cry))

    # physical (1.1 s): rears up, claws high, then slams both wing-claws down and bites
    L = 1.1
    rear = seq({0: 0, .35: 1, .55: 1, .7: -0.25, 1.1: 0})
    pos = lambda t: max(0.0, rear(t))
    neg = lambda t: max(0.0, -rear(t)) / .25
    phys = merge(
        {"body": {"rotation": track(lambda t: [-12 * pos(t) + 5 * neg(t), 0, 0], L),
                  "position": track(lambda t: [0, 4 * pos(t), -8 * seq({0: 0, .35: 0, .7: 1, 1.1: 0})(t)], L)}},
        claws(lambda t: 1.3 * pos(t) - 0.2 * neg(t), L),
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: cape(1.3 * pos(t) - 0.2 * neg(t), 0.9 * pos(t), sx), L)}
         for s, sx in SIDES},
        {f"arm_{s}": {"rotation": track(lambda t: [-20 * pos(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [14 * pos(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [-6 * pos(t), 0, 0], L)} for s, sx in SIDES},
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .35: -10, .62: 20, 1.1: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .35: -8, .62: 12, 1.1: 0})(t), 0, 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .4: 30, .6: 32, .68: 0, 1.1: 2})(t), 0, 0], L)}})
    S["physical"] = anim(L, eyes_open(phys))

    # special (1.4 s): draws its head back, cape flared, and spits a ball of frenzy virus / light
    L = 1.4
    o = seq({0: 0, .4: 1, 1.1: 1, 1.4: 0})
    sp = merge(
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .4: -24, .65: 14, 1.1: 10, 1.4: 0})(t), 0, 0], L)},
         "neck2": {"rotation": track(lambda t: [seq({0: 0, .4: -6, .65: 6, 1.4: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .4: -14, .65: 8, 1.1: 6, 1.4: 0})(t), 0, 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .4: 8, .62: 38, 1.05: 38, 1.3: 2, 1.4: 2})(t), 0, 0], L)},
         "chest": {"rotation": track(lambda t: [seq({0: 0, .4: -5, .7: 3, 1.4: 0})(t), 0, 0], L)},
         "body": {"position": track(lambda t: [0, 0, seq({0: 0, .4: 3, .7: -2, 1.4: 0})(t)], L)}},
        claws(lambda t: 0.6 * o(t), L),
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: cape(0.6 * o(t), 0.95 * o(t), sx), L)} for s, sx in SIDES})
    S["special"] = anim(L, eyes_open(sp))

    # status (1.3 s): shakes its cape to scatter scales, head held high
    L = 1.3
    o = seq({0: 0, .3: 1, 1.0: 1, 1.3: 0})
    st = merge(
        {"neck1": {"rotation": track(lambda t: [-16 * o(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-6 * o(t), 5 * math.sin(t * 22) * (0.3 < t < 1.0), 0], L, 32)},
         "jaw": {"rotation": track(lambda t: [2 + 16 * o(t), 0, 0], L)}},
        claws(lambda t: 0.35 * o(t), L),
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: [10.5 * o(t), 0, cape(0.35 * o(t), 0.8 * o(t), sx)[2]
                                                              + 10 * sx * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}
         for s, sx in SIDES},
        {"body": {"rotation": track(lambda t: [0, 0, 3 * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}})
    S["status"] = anim(L, eyes_open(st))

    # faint: head thrown up, a last trembling cry, then it collapses on its flank, the cape limp over it
    L = 2.6
    up = seq({0: 0, .45: 1, 1.15: 1, 1.6: 0})
    fall = seq({0: 0, 1.1: 0, 1.9: 1, 2.6: 1})
    tremble = lambda t: (math.sin(t * 55) * 3 if 0.45 < t < 1.2 else 0)
    fa = merge(
        {"neck1": {"rotation": track(lambda t: [-28 * up(t) + 20 * fall(t), tremble(t) * 0.5, 0], L, 52)},
         "neck2": {"rotation": track(lambda t: [-8 * up(t) + 10 * fall(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-20 * up(t) + 12 * fall(t), tremble(t), 0], L, 52)},
         "jaw": {"rotation": track(lambda t: [2 + 36 * up(t) + 14 * fall(t) * (1 - up(t)), 0, 0], L)},
         "magala": {"rotation": track(lambda t: [0, 0, -70 * fall(t)], L),
                    "position": track(lambda t: [-8 * fall(t), -1 * fall(t), 0], L)},
         "chest": {"rotation": track(lambda t: [-8 * up(t), 0, 0], L)}},
        claws(lambda t: 0.5 * up(t) - 0.3 * fall(t), L),
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: cape(0.5 * up(t) - 0.3 * fall(t),
                                                                0.5 * up(t) + (0.15 if sx > 0 else 0.4) * fall(t), sx), L)}
         for s, sx in SIDES},
        {f"arm_{s}": {"rotation": track(lambda t: [-30 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [-30 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [40 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [0, 8 * fall(t), 0], L)} for k in range(1, 5)})
    fa = eyes_open(fa)
    for e in eyes:                      # eyes close as it falls
        fa[e] = {"scale": kf({0: [1, 1, 1], 1.8: [1, 1, 1], 1.85: [0, 0, 0], 2.6: [0, 0, 0]})}
    for e in lids:
        fa[e] = {"scale": kf({0: [0, 0, 0], 1.8: [0, 0, 0], 1.85: [1, 1, 1], 2.6: [1, 1, 1]})}
    S["faint"] = anim(L, fa, loop="hold")

    # sleep: lying down, legs folded under it, the wing-arms folded along the body, head on the ground
    L = 4.0
    sl = merge(
        {"magala": {"position": [0, -10, 0]}},
        {f"leg_{s}": {"rotation": [-40, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [62, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": [-20, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}": {"rotation": [60, 0, 0]} for s, sx in SIDES},
        {f"arm_{s}_low": {"rotation": [-70, 0, 0]} for s, sx in SIDES},
        {f"wing_{s}": {"rotation": [-10, 0, 10 * sx]} for s, sx in SIDES},
        {f"wing_{s}_fore": {"rotation": [30, 0, 0]} for s, sx in SIDES},
        {f"wing_{s}_hand": {"rotation": [-20, 0, 0]} for s, sx in SIDES},
        {"neck1": {"rotation": [26, 0, 0]}, "neck2": {"rotation": [8, -14, 0]}, "head": {"rotation": [6, -12, 0]},
         "jaw": {"rotation": [0, 0, 0]}, "chest": {"rotation": wave(1.0, L, L, axis=0, base=(4, 0, 0))}},
        {f"tail{k}": {"rotation": [6 if k == 1 else 0, -14 - 4 * k, 0]} for k in range(1, 5)})
    sl = eyes_shut(sl)
    S["sleep"] = anim(L, sl, loop=True)

    if gold:
        # flight: wings spread, slow powerful beats, legs tucked, tail streaming
        def fly(T, beat, pitch):
            d = merge(
                {"body": {"rotation": [pitch, 0, 0], "position": wave(1.5, T, T, phase=math.pi / 2, axis=1)}},
                {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: [0, -10 * sx, -sx * (58 + beat * math.sin(2 * math.pi * t / T))], T)}
                 for s, sx in SIDES},
                {f"wing_{s}": {"rotation": track(lambda t, sx=sx: [-20, 0, -sx * (40 + beat * 0.4 * math.sin(2 * math.pi * t / T))], T)}
                 for s, sx in SIDES},
                {f"wing_{s}_fore": {"rotation": [-60, 0, 0]} for s, sx in SIDES},
                {f"wing_{s}_hand": {"rotation": [40, 0, 0]} for s, sx in SIDES},
                {f"arm_{s}": {"rotation": [50, 0, 0]} for s, sx in SIDES},
                {f"arm_{s}_low": {"rotation": [-60, 0, 0]} for s, sx in SIDES},
                {f"leg_{s}": {"rotation": [40, 0, 0]} for s, sx in SIDES},
                {f"leg_{s}_shin": {"rotation": [20, 0, 0]} for s, sx in SIDES},
                {f"leg_{s}_foot": {"rotation": [30, 0, 0]} for s, sx in SIDES},
                {"neck1": {"rotation": [-pitch * 0.5 - 4, 0, 0]}, "head": {"rotation": [-pitch * 0.4, 0, 0]}},
                {f"tail{k}": {"rotation": wave(3 + k, T, T, phase=-0.6 * k, axis=0, base=(-pitch * 0.3, 0, 0))} for k in range(1, 5)})
            return anim(T, eyes_open(d), loop=True)
        S["air_idle"] = fly(1.6, 30, 4)
        S["air_fly"] = fly(1.0, 42, 18)
    return S

def poser(name, group):
    q = lambda a: f"q.bedrock('{group}', '{a}')"
    prim = lambda a: f"q.bedrock_primary('{group}', '{a}', q.curve('symmetrical_wide'))"
    poses = {
        "battle-standing": {"poseTypes": ["STAND"], "isBattle": True, "animations": ["q.look('head')", q("battle_idle")]},
        "standing": {"poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"], "isBattle": False,
                     "animations": ["q.look('head')", q("ground_idle")]},
        "walking": {"poseTypes": ["WALK", "SWIM"], "animations": ["q.look('head')", q("ground_walk")]},
        "sleep": {"poseTypes": ["SLEEP"], "animations": [q("sleep")]}}
    if name == "shagarumagala":
        poses["hovering"] = {"poseTypes": ["HOVER"], "animations": ["q.look('head')", q("air_idle")]}
        poses["flying"] = {"poseTypes": ["FLY"], "animations": ["q.look('head')", q("air_fly")]}
    return {"rootBone": "magala",
            "animations": {"cry": f"q.bedrock_stateful('{group}', 'cry')",
                           "faint": f"q.bedrock_primary('{group}', 'faint', q.curve('one'))",
                           "physical": prim("physical"), "special": prim("special"), "status": prim("status")},
            "poses": poses}
