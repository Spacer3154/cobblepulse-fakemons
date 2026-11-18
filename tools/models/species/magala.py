# -*- coding: utf-8 -*-
"""#11234-11236 The Magala line (Monster Hunter): Gore Magala (+ Frenzy form), Chaotic Gore Magala, Shagaru Magala.

One skeleton for the three dragons, six limbs: digitigrade hind legs, and wing-arms that it walks on (the wrists
touch the ground with big hooked claws) while the wing membranes, folded, drape its flanks like a veil; they spread
for the roar, the attacks and flight. A long neck carrying an angular head, a long spiked tail.

* Gore Magala: blind (no eyes at all), black hide with purple sheen, ragged black feathered membranes, a mane of
  black feather tufts; two antennae lie folded along the skull. Frenzy (Mode Furie, battle form): the antennae
  unfold upward and glow purple, the membranes' veins glow faintly.
* Shagaru Magala: white-gold scales, pale gold membranes with gold veins, two great crescent horns rising from the
  skull and curving forward, two glowing eyes, gold spikes along the back and the tail; it glows (golden aura).
* Chaotic Gore Magala: the moult stopped half-way: its right half (Bedrock -X) is Shagaru (gold scales, a crescent
  horn, the only eye), its left half Gore (black-purple, an antenna, blind); bicolour glow (gold / purple).

Front = -Z, ground = y 0, the creature's right side is Bedrock -X (Blockbench shows +X on the screen's right)."""
import math, random
from modelgen import Model, Cube, rgb, shade, mix

DEX = {"goremagala": 11234, "goremagala_frenzy": 11234, "chaoticgoremagala": 11235, "shagarumagala": 11236}
FOLDER = {"goremagala": "11234_goremagala", "goremagala_frenzy": "11234_goremagala",
          "chaoticgoremagala": "11235_chaoticgoremagala", "shagarumagala": "11236_shagarumagala"}
FRAME_BONES = ("head", "jaw")

# ---------------------------------------------------------------------------------------------------- palettes
GORE = {
    "scale": rgb("#262030"), "scale_dark": rgb("#14111C"), "scale_light": rgb("#3E3254"), "scale_sheen": rgb("#5A3E80"),
    "belly": rgb("#3A3242"), "belly_dark": rgb("#262030"),
    "plate": rgb("#1C1826"), "plate_light": rgb("#3A3050"),
    "membrane": rgb("#1A1620"), "membrane_dark": rgb("#0C0A10"), "vein": rgb("#3A2A52"), "vein_glow": rgb("#B060FF"),
    "fur": rgb("#18141E"), "fur_tip": rgb("#4A3A62"),
    "claw": rgb("#4A3A50"), "claw_tip": rgb("#C8B8C8"),
    "horn": rgb("#2A2236"), "horn_tip": rgb("#7A60A0"),
    "antenna": rgb("#5E3A86"), "antenna_tip": rgb("#C890F0"), "antenna_glow": rgb("#D070FF"),
    "mouth": rgb("#5A2040"), "tooth": rgb("#D8D0C8"),
    "eye": rgb("#FFE8A0"), "eye_glow": rgb("#FFD860"), "lid": rgb("#262030"), "pupil": rgb("#2A1A08"),
}
GORE_SHINY = dict(GORE, **{           # ash grey with teal antennae
    "scale": rgb("#3A3E44"), "scale_dark": rgb("#24272C"), "scale_light": rgb("#5A6068"), "scale_sheen": rgb("#4E8A90"),
    "belly": rgb("#4C5056"), "belly_dark": rgb("#34373C"), "plate": rgb("#2E3136"), "plate_light": rgb("#525860"),
    "membrane": rgb("#2C2F34"), "membrane_dark": rgb("#1A1C20"), "vein": rgb("#3E6A70"), "vein_glow": rgb("#50F0E0"),
    "fur": rgb("#2A2D32"), "fur_tip": rgb("#6A8E94"), "antenna": rgb("#2E7A80"), "antenna_tip": rgb("#90F0E8"),
    "antenna_glow": rgb("#60FFF0"), "horn": rgb("#33373C"), "horn_tip": rgb("#6A9096")})
SHAGARU = {
    "scale": rgb("#E4D6A8"), "scale_dark": rgb("#CBB880"), "scale_light": rgb("#F2E8C6"), "scale_sheen": rgb("#D8B860"),
    "belly": rgb("#F0E8CC"), "belly_dark": rgb("#CFC096"),
    "plate": rgb("#D0B46A"), "plate_light": rgb("#F2DC90"),
    "membrane": rgb("#EEE2B0"), "membrane_dark": rgb("#C8B272"), "vein": rgb("#C89A3A"), "vein_glow": rgb("#FFD050"),
    "fur": rgb("#F2E6B8"), "fur_tip": rgb("#D4AE50"),
    "claw": rgb("#8A7448"), "claw_tip": rgb("#F8F0D8"),
    "horn": rgb("#C8A450"), "horn_tip": rgb("#FFF4C8"),
    "antenna": rgb("#5E3A86"), "antenna_tip": rgb("#C890F0"), "antenna_glow": rgb("#D070FF"),
    "mouth": rgb("#8A4A3A"), "tooth": rgb("#FFFFF0"),
    "eye": rgb("#FFF6C0"), "eye_glow": rgb("#FFE070"), "lid": rgb("#D8C690"), "pupil": rgb("#3A240A"),
}
SHAGARU_SHINY = dict(SHAGARU, **{     # platinum and pale blue
    "scale": rgb("#D4DCE4"), "scale_dark": rgb("#B0BCC8"), "scale_light": rgb("#EAF0F6"), "scale_sheen": rgb("#9CC4E8"),
    "belly": rgb("#E8EEF4"), "belly_dark": rgb("#B8C2CC"), "plate": rgb("#A8BCD0"), "plate_light": rgb("#DCE8F4"),
    "membrane": rgb("#E0E8F0"), "membrane_dark": rgb("#A8B4C4"), "vein": rgb("#6A9AD0"), "vein_glow": rgb("#80D0FF"),
    "fur": rgb("#E4ECF4"), "fur_tip": rgb("#80A8D8"), "claw": rgb("#6A7484"), "horn": rgb("#9CB0C8"),
    "horn_tip": rgb("#F4FAFF"), "eye": rgb("#E8F8FF"), "eye_glow": rgb("#90E0FF"), "lid": rgb("#B8C4D0")})
CHAOS = dict(GORE, _R=SHAGARU)
CHAOS_SHINY = dict(GORE_SHINY, _R=SHAGARU_SHINY)
PALETTES = {"goremagala": (GORE, GORE_SHINY), "goremagala_frenzy": (GORE, GORE_SHINY),
            "chaoticgoremagala": (CHAOS, CHAOS_SHINY), "shagarumagala": (SHAGARU, SHAGARU_SHINY)}

# ---------------------------------------------------------------------------------------------------- painting
LIGHT = {"up": 1.12, "north": 1.0, "south": 0.92, "east": 0.96, "west": 0.96, "down": 0.72}

def _h(*v):
    x = 0
    for a in v:
        x = (x * 1000003 + int(math.floor(a * 7.0)) * 92821) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 1274126177) & 0xFFFFFFFF; x ^= x >> 16
    return (x & 0xFFFF) / 65535.0

def _vein(y, z):
    """the wing's long veins: a fan running from the elbow down and back"""
    a = math.atan2(46 - y, z + 8)
    return any(abs(a - k) < 0.035 for k in (0.35, 0.75, 1.15, 1.55)) and y < 47

def side_pal(pal, p):
    """the chaotic one: the creature's right half (Bedrock -X) has Shagaru's colours"""
    r = pal.get("_R")
    return r if (r is not None and p[0] < -0.01) else pal

def _put(px, X, Y, col, f, n=0.0):
    c = shade(col, f * (1 + n))
    px[X, Y] = c

def surf(kind, *, belly_below=None, ragged=0, glow=None):
    """paint dict: every texel coloured from its model-space position (asymmetric palettes, scale rows...)
    kind: scale | belly | plate | membrane | fur | claw | horn | antenna | mouth | tooth | eye | lid
    belly_below: texels below this height use the belly colour; ragged: the bottom `ragged` rows of the side faces
    get torn (transparent) edges; glow: emissive painter key ('vein', 'antenna', 'eye', 'horn')."""
    def colour(pal, face, p, i, j, w, h):
        P = side_pal(pal, p)
        x, y, z = p
        n = (_h(x, y, z) - 0.5) * 0.10
        if kind == "scale":
            if belly_below is not None and y < belly_below and face != "up":
                row = int(math.floor(y)) % 3 == 0
                return (P["belly_dark"] if row else P["belly"]), n
            u = z if face in ("east", "west", "up", "down") else x
            sx, sy = int(math.floor(u / 2.0)), int(math.floor(y / 2.0))
            edge = (math.floor(y) % 2 == 0) and ((math.floor(u) + sy) % 2 == 0)
            c = P["scale_dark"] if edge else (P["scale_light"] if _h(sx, sy, 3) > 0.82 else P["scale"])
            if _h(sx * 3, sy, 9) > 0.9:
                c = mix(c, P["scale_sheen"], 0.6)
            return c, n
        if kind == "belly":
            return (P["belly_dark"] if int(math.floor(y)) % 3 == 0 else P["belly"]), n
        if kind == "plate":
            rim = i == 0 or j == 0 or i == w - 1 or j == h - 1
            return (P["plate_light"] if rim else P["plate"]), n
        if kind == "membrane":
            if _vein(y, z):
                return P["vein"], n * 0.3
            barb = 0.5 + 0.5 * math.sin(z * 2.2 + y * 0.9)              # feathery barbs running down-back
            low = max(0.0, min(1.0, (30 - y) / 20))                      # darker toward the torn hem
            c = mix(P["membrane"], P["membrane_dark"], 0.25 * barb + 0.45 * low)
            return c, n * 0.3
        if kind == "fur":
            t = 1 - j / max(h - 1, 1) if face not in ("up", "down") else 1
            return mix(P["fur"], P["fur_tip"], max(0.0, t - 0.35) / 0.65), n
        if kind in ("claw", "horn", "antenna"):
            t = 1 - j / max(h - 1, 1) if face not in ("up", "down") else (1.0 if face == "up" else 0.0)
            return mix(P[kind], P[kind + "_tip"], t ** 1.5), n * 0.5
        if kind == "eye" and abs(z + 56.5) < 0.6 and face in ("east", "west"):
            return P["pupil"], 0.0
        if kind in ("mouth", "tooth", "eye", "lid"):
            return P[kind], n * 0.4
        raise ValueError(kind)

    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            fx, fy, fw, fh = faces[face]
            i, j = X - fx, Y - fy
            col, n = colour(pal, face, p, i, j, fw, fh)
            if ragged and face in ("east", "west", "north", "south") and j >= fh - ragged:
                if _h(p[0] * 3, p[2] * 3, p[1]) < 0.35 + 0.25 * (j - (fh - ragged)) / max(ragged, 1):
                    px[X, Y] = (0, 0, 0, 0)
                    continue
            _put(px, X, Y, col, LIGHT[face], n)

    def glow_fn(px, faces, pal, rnd, c):
        if not glow:
            return
        for face, X, Y, p in c.texels():
            P = side_pal(pal, p)
            fx, fy, fw, fh = faces[face]
            j = Y - fy
            x, y, z = p
            if glow == "vein":
                if not pal.get("_veins"):
                    continue
                if ragged and face in ("east", "west", "north", "south") and j >= fh - ragged:
                    continue
                if not _vein(y, z):
                    continue
                col = P["vein_glow"]
                px[X, Y] = col[:3] + (150,)
            elif glow == "antenna":
                if not pal.get("_antenna"):
                    continue
                t = 1 - j / max(fh - 1, 1) if face not in ("up", "down") else 1
                col = P["antenna_glow"]
                px[X, Y] = col[:3] + (int(120 + 135 * t),)
            elif glow == "eye":
                if abs(z + 56.5) < 0.6 and face in ("east", "west"):
                    continue
                px[X, Y] = P["eye_glow"][:3] + (255,)
            elif glow == "horn":
                if not pal.get("_horn"):
                    continue
                t = 1 - j / max(fh - 1, 1) if face not in ("up", "down") else 1
                if t > 0.55:
                    px[X, Y] = P["horn_tip"][:3] + (int(200 * (t - 0.55) / 0.45),)
    d = {"fn3": fn3, "base": None}
    if glow:
        d["glow_fn"] = glow_fn
    return d

SCALE = surf("scale")
PLATE = surf("plate")
CLAW = surf("claw")
HORN = surf("horn", glow="horn")
TOOTH = surf("tooth")
MOUTH = surf("mouth")

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
        out.append(Cube([x - wx / 2, y - sunk, z - wz / 2], [wx, int(L + sunk), wz], paint,
                        rotation=dir_rot(dd), pivot=[x, y, z]))
        x, y, z = x + dh[0] * (L - 0.5), y + dh[1] * (L - 0.5), z + dh[2] * (L - 0.5)
    return out

H = 24                     # hip height
SH = (9, 36, -16)          # shoulder (left; the right one mirrored)

def crescent(sx, p, big=True):
    """Shagaru's great horn: rises from the skull, bends back, then sweeps forward like a crescent"""
    k = 1.0 if big else 0.7
    return chain(p, [(0.25 * sx, 1, 0.45), (0.2 * sx, 1, 0.1), (0.1 * sx, 0.9, -0.35), (0.05 * sx, 0.5, -1)],
                 [round(8 * k), round(8 * k), round(7 * k), round(6 * k)], [(3, 4), (3, 3), (2, 2), (1, 1)], HORN)

# ---------------------------------------------------------------------------------------------------- model
def build(name):
    gold = name == "shagarumagala"
    chaos = name == "chaoticgoremagala"
    frenzy = name == "goremagala_frenzy"
    m = Model(name, DEX[name], (256, 256))
    m.bone("magala", None, [0, 0, 0])
    m.bone("body", "magala", [0, H + 4, 2])
    belly = H + 1
    m.bone("torso", "body", [0, H + 4, 2], cubes=[
        Cube([-8, H - 4, -8], [16, 15, 26], surf("scale", belly_below=belly)),
        Cube([-6, H + 11, -6], [12, 2, 22], SCALE)])
    m.bone("chest", "body", [0, H + 6, -6], rotation=[-6, 0, 0], cubes=[
        Cube([-9, H - 2, -26], [18, 17, 20], surf("scale", belly_below=belly + 2)),
        Cube([-7, H + 15, -24], [14, 2, 16], SCALE)])
    # mane: feather tufts (Gore) / gold spikes (Shagaru) along the spine
    mane = m.bone("mane", "body", [0, H + 14, 0])
    for k, (z, y, L) in enumerate([(-24, H + 16, 7), (-19, H + 17, 9), (-13, H + 17, 10), (-7, H + 16, 10),
                                   (-1, H + 14, 9), (5, H + 13, 8), (11, H + 12, 7)]):
        for sx in ((-1, 1) if not gold else (0,)):
            x = 2.5 * sx
            if gold or (chaos and sx < 0):
                mane.cubes += chain([x, y, z], [(0, 1, 0.5), (0, 0.6, 1)], [round(L * 0.55), round(L * 0.45)],
                                    [(2, 3), (1, 1)], HORN)
            else:
                mane.cubes += [seg([x, y - 1, z], [x + 2 * sx, y + L * 0.7, z + L * 0.7], 3, 1, surf("fur"))]
    # ------------------------------------------------------------------ neck and head
    m.bone("neck1", "chest", [0, H + 10, -24], rotation=[-22, 0, 0], cubes=[
        Cube([-5, H + 4, -36], [10, 11, 14], surf("scale", belly_below=H + 6))])
    m.bone("neck2", "neck1", [0, H + 10, -35], rotation=[8, 0, 0], cubes=[
        Cube([-4.5, H + 4.5, -46], [9, 10, 13], surf("scale", belly_below=H + 6.5))])
    hp = [0, H + 10, -45]
    head = m.bone("head", "neck2", hp, rotation=[18, 0, 0], cubes=[
        Cube([-5.5, H + 4, -62], [11, 9, 18], SCALE),                     # skull
        Cube([-4, H + 4, -70], [8, 6, 9], SCALE),                          # snout
        Cube([-6, H + 12, -58], [12, 3, 15], PLATE),                       # brow hood
        Cube([-3, H + 9.5, -69], [6, 2, 8], PLATE)])                       # nose ridge
    # cheek armour (the blind face of Gore Magala is a smooth armoured mask)
    for sx in (1, -1):
        if not (gold or (chaos and sx < 0)):
            head.cubes += [Cube([5.0 * sx - (2 if sx < 0 else 0), H + 5, -60], [2, 7, 12], PLATE)]
    m.bone("jaw", "head", [0, H + 5, -47], cubes=[
        Cube([-4.5, H + 1, -68], [9, 4, 21], surf("scale", belly_below=H + 3)),
        Cube([-3.5, H + 4.6, -67], [7, 1, 18], MOUTH)])
    jaw = m.get("jaw")
    for k in range(5):                                                  # teeth
        for sx in (1, -1):
            z = -66 + 4 * k
            head.cubes += [Cube([3.0 * sx - 0.5, H + 3, z], [1, 2, 1], TOOTH)]
            jaw.cubes += [Cube([3.4 * sx - 0.5, H + 5, z + 2], [1, 2, 1], TOOTH)]
    # antennae (Gore, Frenzy, the dark side of the chaotic one) / crescent horns and eyes (Shagaru, its gold side)
    for sx, side in ((1, "left"), (-1, "right")):
        gold_side = gold or (chaos and sx < 0)
        if gold_side:
            hb = m.bone(f"horn_{side}", "head", [4 * sx, H + 14, -50])
            hb.cubes += crescent(sx, [4 * sx, H + 14, -50])
            hb.cubes += chain([5.5 * sx, H + 13, -46], [(0.6 * sx, 0.5, 1), (0.4 * sx, 0.2, 1)], [5, 5], [(2, 2), (1, 1)], HORN)
            eb = m.bone(f"eye_{side}", "head", [5.5 * sx, H + 9, -56])
            eb.cubes += [Cube([5.5 * sx - (1 if sx < 0 else 0), H + 8, -59], [1, 3, 5], surf("eye", glow="eye"))]
            m.bone(f"lid_{side}", "head", [5.5 * sx, H + 9, -56], cubes=[
                Cube([5.4 * sx - (1 if sx < 0 else 0), H + 8, -59], [1, 3, 5], surf("lid"), inflate=0.05)])
        else:
            ab = m.bone(f"antenna_{side}", "head", [3.5 * sx, H + 14.5, -52],
                        rotation=([62, 0, -24 * sx] if frenzy else None))
            ab.cubes += chain([3.5 * sx, H + 14.5, -52], [(0.15 * sx, 0.12, 1), (0.2 * sx, 0.0, 1), (0.25 * sx, -0.1, 1)],
                              [8, 8, 7], [(2, 2), (2, 2), (1, 1)], surf("antenna", glow="antenna"))
    # ------------------------------------------------------------------ wing-arms (front limbs) and membranes
    for sx, side in ((1, "left"), (-1, "right")):
        dark = not (gold or (chaos and sx < 0))
        S = (SH[0] * sx, SH[1], SH[2])
        E = (15 * sx, 43, -6)                 # the elbow stands high, above the back
        W = (18 * sx, 5, -31)                 # the wrist rests on the ground
        m.bone(f"wing_{side}", "chest", list(S), cubes=[seg(S, E, 7, 7, SCALE)])
        m.bone(f"wing_{side}_fore", f"wing_{side}", list(E), cubes=[
            seg(E, W, 6, 6, SCALE), Cube([E[0] - 3.5, E[1] - 3, E[2] - 4], [7, 7, 8], SCALE)])
        hand = m.bone(f"wing_{side}_hand", f"wing_{side}_fore", list(W), cubes=[
            Cube([W[0] - 4, 1, W[2] - 5], [8, 5, 9], SCALE)])
        for k, dx in enumerate((-2.5, 0, 2.5)):                          # hooked claws forward, a thumb hook upward
            hand.cubes += chain([W[0] + dx, 2.5, W[2] - 5], [(0, 0.3, -1), (0, -0.6, -1)], [4, 3], [(2, 2), (1, 1)], CLAW)
        hand.cubes += chain([W[0] + 3 * sx, 7, W[2] - 2], [(0.3 * sx, 1, -0.6), (0.2 * sx, 0.2, -1)], [6, 5],
                            [(2, 2), (1, 1)], CLAW)
        # membrane: folded, it hangs from the elbow along the flank to the hips like a ragged cloak, the top leaning
        # over the back, the torn hem outward
        wm = m.bone(f"wingm_{side}", f"wing_{side}", [15.5 * sx, 46, -6], rotation=[0, 0, -14 * sx])
        x0 = (15 if sx > 0 else -16)
        panels = [(-12, 16, 44, 4), (-3, 12, 47, 4), (6, 11, 48, 5), (15, 12, 48, 5), (24, 15, 47, 5), (33, 20, 44, 5)]
        for z, y0, y1, rg in panels:
            wm.cubes += [Cube([x0, y0, z], [1, y1 - y0, 10], surf("membrane", ragged=rg, glow="vein"))]
        # the wing's finger bones along the top edge of the folded membrane
        wm.cubes += [seg((15.5 * sx, 44, -8), (16 * sx, 49, 14), 3, 3, SCALE),
                     seg((16 * sx, 49, 14), (16 * sx, 46, 42), 2, 2, SCALE)]
        wm.cubes += chain([15.5 * sx, 44, -8], [(0.2 * sx, 0.6, -1), (0.1 * sx, 0.2, -1)], [4, 3], [(2, 2), (1, 1)], CLAW)
    # ------------------------------------------------------------------ hind legs
    for sx, side in ((1, "left"), (-1, "right")):
        x = 9.5 * sx
        m.bone(f"leg_{side}", "torso", [x, H + 2, 10], cubes=[
            Cube([x - 3.5, 12, 4], [7, 16, 11], surf("scale", belly_below=None))])
        m.bone(f"leg_{side}_shin", f"leg_{side}", [x, 13, 9], cubes=[
            seg((x, 14, 9), (x, 4, 15), 5, 5, SCALE)])
        foot = m.bone(f"leg_{side}_foot", f"leg_{side}_shin", [x, 4, 14], cubes=[
            Cube([x - 3, 0, 5], [6, 4, 11], SCALE)])
        for dx in (-2, 0, 2):
            foot.cubes += chain([x + dx, 1.5, 5], [(0, 0.2, -1), (0, -0.7, -1)], [3, 2], [(2, 2), (1, 1)], CLAW)
    # ------------------------------------------------------------------ tail (spiked)
    prev, z, y = "torso", 16, H + 6
    for k, (L, w) in enumerate([(16, 10), (16, 8), (15, 6), (15, 4)]):
        tb = m.bone(f"tail{k + 1}", prev, [0, y, z], rotation=[-5, 0, 0], cubes=[
            Cube([-w / 2, y - w / 2 - 1, z - 1], [w, w, L + 1], surf("scale", belly_below=y - w / 2 + 1))])
        for j in range(2):
            zz = z + 3 + 6 * j
            if gold:
                tb.cubes += chain([0, y + w / 2 - 1, zz], [(0, 1, 0.6)], [3 + (3 - k)], [(2, 2)], HORN)
            else:
                for sx in (1, -1):
                    if chaos and sx < 0:
                        tb.cubes += chain([w / 2 * sx, y, zz], [(sx, 0.4, 0.6)], [3], [(1, 1)], HORN)
                    else:
                        tb.cubes += [seg([w / 2 * sx * 0.6, y + w / 2 - 1, zz], [w / 2 * sx + sx, y + w / 2 + 3, zz + 3], 2, 1,
                                         surf("fur"))]
        prev, z, y = f"tail{k + 1}", z + L, y - 1
    m.get("tail4").cubes += chain([0, y + 1, z - 2], [(0, 0.2, 1)], [5], [(2, 2)], HORN)
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
FOLD = {"wingm": [0, 0, 0]}

def spread(f, sx):
    """membrane spread outward (f = 0 folded .. 1 horizontal .. 1.6 raised)"""
    return [0, -12 * f * sx, -88 * f * sx]

def arm_spread(f, sx):
    return [-10 * f, 0, -28 * f * sx]

def has(name, bone):
    return bone in BONES[name]

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

    # ground_idle: breathing, a slow sway of the neck and tail, the membranes ripple
    L = 3.0
    idle = merge(
        {"body": {"position": wave(0.4, L, L, axis=1)}},
        {"chest": {"rotation": wave(1.0, L, L, axis=0)}},
        {"neck1": {"rotation": wave(2.5, L, L, phase=0.5, axis=0)}, "head": {"rotation": wave(3, L, L, phase=1.0, axis=1)},
         "jaw": {"rotation": wave(1.5, L, L, phase=2.0, axis=0, base=(2, 0, 0))}},
        {f"wingm_{s}": {"rotation": wave(2.0, L, L, phase=0.3, axis=2, base=(0, 0, 0))} for s, sx in SIDES},
        {f"tail{k}": {"rotation": wave(3 + k, L, L, phase=-0.5 * k, axis=1)} for k in range(1, 5)})
    S["ground_idle"] = anim(L, eyes_open(idle), loop=True)

    # walk: diagonal pairs (front left with hind right), the head steady, the tail swinging
    T = 1.4
    w = {}
    for s, sx in SIDES:
        ph = 0 if sx > 0 else math.pi
        a = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph)
        b = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph))
        a2 = lambda t, ph=ph: math.sin(2 * math.pi * t / T + ph + math.pi)
        b2 = lambda t, ph=ph: max(0.0, math.cos(2 * math.pi * t / T + ph + math.pi))
        w[f"wing_{s}"] = {"rotation": track(lambda t, a=a: [16 * a(t), 0, 0], T)}
        w[f"wing_{s}_fore"] = {"rotation": track(lambda t, b=b: [-14 * b(t), 0, 0], T)}
        w[f"wing_{s}_hand"] = {"rotation": track(lambda t, a=a, b=b: [-16 * a(t) + 14 * b(t), 0, 0], T)}
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

    # battle_idle: low, wings half-open like a cloak thrown back, head low and forward, jaw working
    L = 2.0
    bi = merge(
        {"body": {"position": wave(0.6, L, L, axis=1, base=(0, -1.5, 0))}},
        {"chest": {"rotation": wave(1.5, L, L, axis=0, base=(4, 0, 0))}},
        {"neck1": {"rotation": wave(2, L, L, axis=0, base=(6, 0, 0))}, "neck2": {"rotation": [4, 0, 0]},
         "head": {"rotation": wave(3, L, L, phase=1, axis=0, base=(-10, 0, 0))},
         "jaw": {"rotation": wave(4, L / 2, L, axis=0, base=(8, 0, 0))}},
        {f"wingm_{s}": {"rotation": wave(4, L, L, axis=2, base=spread(0.35, sx))} for s, sx in SIDES},
        {f"wing_{s}": {"rotation": [6, 0, -4 * sx]} for s, sx in SIDES},
        {f"wing_{s}_hand": {"rotation": [-6, 0, 4 * sx]} for s, sx in SIDES},
        {f"tail{k}": {"rotation": wave(5 + k, L, L, phase=-0.7 * k, axis=1, base=(4 if k == 1 else 0, 0, 0))}
         for k in range(1, 5)})
    S["battle_idle"] = anim(L, eyes_open(bi), loop=True)

    # cry: rears its neck, spreads the wings wide and roars, head shaking
    L = 2.2
    shake = lambda t: [0, 4 * math.sin(t * 40) if 0.6 < t < 1.6 else 0, 0]
    cry = merge(
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .5: -24, 1.6: -24, 2.2: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .5: -12, 1.6: -12, 2.2: 0})(t), shake(t)[1], 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .45: 36, 1.6: 36, 2.0: 2, 2.2: 2})(t), 0, 0], L)},
         "chest": {"rotation": track(lambda t: [seq({0: 0, .5: -8, 1.6: -8, 2.2: 0})(t), 0, 0], L)}},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: spread(seq({0: 0, .55: 1.35, 1.7: 1.35, 2.2: 0})(t), sx), L)}
         for s, sx in SIDES},
        {f"wing_{s}": {"rotation": track(lambda t, sx=sx: arm_spread(seq({0: 0, .55: 0.6, 1.7: 0.6, 2.2: 0})(t), sx), L)}
         for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [seq({0: 0, .5: 6, 1.6: 6, 2.2: 0})(t), 0, 0], L)} for k in (1, 2)})
    S["cry"] = anim(L, eyes_open(cry))

    # physical (1.1 s): rears up on the hind legs, wings flared, then slams both wing-claws down and bites
    L = 1.1
    rear = seq({0: 0, .35: 1, .55: 1, .7: -0.25, 1.1: 0})
    phys = merge(
        {"body": {"rotation": track(lambda t: [-16 * max(0, rear(t)) + 6 * max(0, -rear(t)) / .25, 0, 0], L),
                  "position": track(lambda t: [0, 5 * max(0, rear(t)), -10 * seq({0: 0, .35: 0, .7: 1, 1.1: 0})(t)], L)}},
        {f"wing_{s}": {"rotation": track(lambda t, sx=sx: [-55 * max(0, rear(t)) + 15 * max(0, -rear(t)) / .25, 0,
                                                            -10 * sx * max(0, rear(t))], L)} for s, sx in SIDES},
        {f"wing_{s}_fore": {"rotation": track(lambda t: [-25 * max(0, rear(t)), 0, 0], L)} for s, sx in SIDES},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: spread(0.9 * max(0, rear(t)), sx), L)} for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t: [22 * max(0, rear(t)), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [-10 * max(0, rear(t)), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": track(lambda t: [4 * max(0, rear(t)), 0, 0], L)} for s, sx in SIDES},
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .35: -10, .62: 22, 1.1: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .35: -8, .62: 14, 1.1: 0})(t), 0, 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .4: 30, .6: 32, .68: 0, 1.1: 2})(t), 0, 0], L)}})
    S["physical"] = anim(L, eyes_open(phys))

    # special (1.4 s): draws its head back, wings flared, and spits a ball of frenzy / light
    L = 1.4
    sp = merge(
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .4: -26, .65: 14, 1.1: 10, 1.4: 0})(t), 0, 0], L)},
         "neck2": {"rotation": track(lambda t: [seq({0: 0, .4: -6, .65: 6, 1.4: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .4: -14, .65: 8, 1.1: 6, 1.4: 0})(t), 0, 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .4: 8, .62: 38, 1.05: 38, 1.3: 2, 1.4: 2})(t), 0, 0], L)},
         "chest": {"rotation": track(lambda t: [seq({0: 0, .4: -6, .7: 3, 1.4: 0})(t), 0, 0], L)},
         "body": {"position": track(lambda t: [0, 0, seq({0: 0, .4: 3, .7: -2, 1.4: 0})(t)], L)}},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: spread(seq({0: 0, .4: 1.1, 1.1: 1.1, 1.4: 0})(t), sx), L)}
         for s, sx in SIDES},
        {f"wing_{s}": {"rotation": track(lambda t, sx=sx: arm_spread(seq({0: 0, .4: 0.5, 1.1: 0.5, 1.4: 0})(t), sx), L)}
         for s, sx in SIDES})
    S["special"] = anim(L, eyes_open(sp))

    # status (1.3 s): shakes its wings to scatter scales, head held high
    L = 1.3
    st = merge(
        {"neck1": {"rotation": track(lambda t: [seq({0: 0, .3: -16, 1.0: -16, 1.3: 0})(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [seq({0: 0, .3: -6, 1.0: -6, 1.3: 0})(t), 5 * math.sin(t * 22) * (0.3 < t < 1.0), 0], L)},
         "jaw": {"rotation": track(lambda t: [seq({0: 2, .3: 18, 1.0: 18, 1.3: 2})(t), 0, 0], L)}},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: [0, 0, spread(seq({0: 0, .3: 0.8, 1.0: 0.8, 1.3: 0})(t), sx)[2]
                                                              + 10 * sx * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}
         for s, sx in SIDES},
        {"body": {"rotation": track(lambda t: [0, 0, 3 * math.sin(t * 30) * (0.3 < t < 1.0)], L, 32)}})
    S["status"] = anim(L, eyes_open(st))

    # faint: head thrown up, a last trembling cry, then it collapses on its flank, wings limp
    L = 2.6
    up = seq({0: 0, .45: 1, 1.15: 1, 1.6: 0})
    fall = seq({0: 0, 1.1: 0, 1.9: 1, 2.6: 1})
    tremble = lambda t: (math.sin(t * 55) * 3 if 0.45 < t < 1.2 else 0)
    fa = merge(
        {"neck1": {"rotation": track(lambda t: [-30 * up(t) + 20 * fall(t), tremble(t) * 0.5, 0], L, 52)},
         "neck2": {"rotation": track(lambda t: [-8 * up(t) + 10 * fall(t), 0, 0], L)},
         "head": {"rotation": track(lambda t: [-20 * up(t) + 12 * fall(t), tremble(t), 0], L, 52)},
         "jaw": {"rotation": track(lambda t: [2 + 36 * up(t) + 14 * fall(t) * (1 - up(t)), 0, 0], L)},
         "magala": {"rotation": track(lambda t: [0, 0, -68 * fall(t)], L),
                    "position": track(lambda t: [-6 * fall(t), -3 * fall(t), 0], L)},
         "chest": {"rotation": track(lambda t: [-10 * up(t), 0, 0], L)}},
        {f"wingm_{s}": {"rotation": track(lambda t, sx=sx: spread(0.6 * up(t) + (0.25 if sx > 0 else 0.5) * fall(t), sx), L)}
         for s, sx in SIDES},
        {f"wing_{s}": {"rotation": track(lambda t, sx=sx: [-14 * fall(t), 0, (20 if sx > 0 else 30) * fall(t) * -sx], L)}
         for s, sx in SIDES},
        {f"leg_{s}": {"rotation": track(lambda t, sx=sx: [-30 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": track(lambda t: [40 * fall(t), 0, 0], L)} for s, sx in SIDES},
        {f"tail{k}": {"rotation": track(lambda t, k=k: [0, 8 * fall(t), 0], L)} for k in range(1, 5)})
    fa = eyes_open(fa)
    for e in eyes:                      # eyes close as it falls
        fa[e] = {"scale": kf({0: [1, 1, 1], 1.8: [1, 1, 1], 1.85: [0, 0, 0], 2.6: [0, 0, 0]})}
    for e in lids:
        fa[e] = {"scale": kf({0: [0, 0, 0], 1.8: [0, 0, 0], 1.85: [1, 1, 1], 2.6: [1, 1, 1]})}
    S["faint"] = anim(L, fa, loop="hold")

    # sleep: lying down, the wings folded over it like a blanket, head on the ground, eyes closed
    L = 4.0
    sl = merge(
        {"magala": {"position": [0, -9, 0]}},
        {f"leg_{s}": {"rotation": [-40, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_shin": {"rotation": [62, 0, 0]} for s, sx in SIDES},
        {f"leg_{s}_foot": {"rotation": [-20, 0, 0]} for s, sx in SIDES},
        {f"wing_{s}": {"rotation": [-28, 0, -10 * sx]} for s, sx in SIDES},
        {f"wing_{s}_fore": {"rotation": [-50, 0, 0]} for s, sx in SIDES},
        {f"wing_{s}_hand": {"rotation": [76, 0, 0]} for s, sx in SIDES},
        {f"wingm_{s}": {"rotation": [0, 0, -14 * sx]} for s, sx in SIDES},
        {"neck1": {"rotation": [30, 0, 0]}, "neck2": {"rotation": [8, -14, 0]}, "head": {"rotation": [6, -12, 0]},
         "jaw": {"rotation": [0, 0, 0]}, "chest": {"rotation": wave(1.0, L, L, axis=0, base=(4, 0, 0))}},
        {f"tail{k}": {"rotation": [6 if k == 1 else 0, -14 - 4 * k, 0]} for k in range(1, 5)})
    sl = eyes_shut(sl)
    for a in BONES[name]:
        if a.startswith("antenna_") and name == "goremagala_frenzy":
            sl[a] = {"rotation": [-50, 0, 20 if a.endswith("left") else -20]}     # folded back while asleep
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
                {f"wing_{s}_fore": {"rotation": [-40, 0, 0]} for s, sx in SIDES},
                {f"wing_{s}_hand": {"rotation": [60, 0, 0]} for s, sx in SIDES},
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
