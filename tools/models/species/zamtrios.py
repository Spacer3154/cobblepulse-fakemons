# -*- coding: utf-8 -*-
"""#1054 Zamtrios (Monster Hunter), rebuilt on the skeleton of the supplied remaster model (same bones, same pivots:
its GeckoLib animations still drive it), with the shapes and colours of the reference pictures:

* a big rounded shark head (high crown, blunt bullet snout, white eye, a pink-lipped mouth lined with teeth, a pale
  lower jaw and throat), a hunched body with a tall swept shark dorsal fin (teal leading edge, the trailing half
  green-yellow-orange), sprawled fore limbs carrying a ribbed fin on the forearm, crouched hind legs, long black
  claws, a long tail ending in a vertical caudal fin (bigger upper lobe), deep teal hide with darker cracks, pale
  cream-lavender belly;
* details from the concept sheet (3.1.2): overlapping diamond scales (bigger on the back, a few bright glints), the
  lower flanks olive then gold, the tail turning olive-gold, a serrated crest of red-tipped plates on the skull, the
  neck, the back and the whole tail, a double row of spine plates, brow ridges, gill slits, white mandible blades
  pointing back, feather-like overlapping plates on the forearm fins, a ribbed golden fringe under the tail;
* Ice Armour: the hide lightly frosted (snow on the top faces), a huge ice horn growing forward from the snout, an ice cap on the skull and spikes
  along its sides, an ice crest and cheek frills, a crown of long tapering ice spikes on the shoulders and back, the dorsal fin sheathed in ice, iced forearm
  fins, shoulders, thighs and tail fin; every ice bone has a glow shell (emissive layer only, hidden asleep);
* Inflated (after the in-game picture): a huge bean bag of stretched mauve-brown skin (wrinkles, folds near the top,
  dark veins, the pink of the mouth under the jaw), widest low down and slanting back so its front slopes under the
  head; the creature is lifted onto it (the sac is built at half size around its pivot on the ground and scaled x2 by
  every animation; it empties when the creature faints and the body sinks back to the ground).

Front = -Z, ground = y 0, left = +X (Blockbench shows +X on the screen's right)."""
import math
from modelgen import Model, Cube, rgb, shade, mix, apply

DEX, SID = 1054, "zamtrios"
FOLDER = "1054_zamtrios"
# the inflated sac (a bean bag of stretched mauve-brown skin; the creature lies on it, its head on the front slope)
BALLOON_P = (0.0, 0.0, -14.0)         # pivot: the middle of the sac on the ground (the scale origin)
BALLOON_K = 2.0                       # built at 1/K size, scaled xK by the animations
SAC_H, SAC_RX, SAC_RZ, SAC_SLANT = 66.0, 56.0, 70.0, 50.0
LIFT = 34                             # the inflated creature is lifted this much, onto the top of its sac

def sac_profile(u):
    """footprint of the sac at the height fraction u: (half width, half length, centre z), full size; widest a
    third of the way up, flat on the ground, its top sliding back so the front slopes down under the head"""
    if u >= 0.38:
        f = math.sqrt(max(0.0, 1 - ((u - 0.38) / 0.62) ** 2))
    else:
        f = math.sqrt(max(0.0, 1 - ((0.38 - u) / 0.5) ** 2))
    return SAC_RX * f, SAC_RZ * f, -14 + SAC_SLANT * (u - 0.38)

def lift(m, dy=LIFT, keep=("zamtrios", "specialfx1", "balloon")):
    """moves every bone of the creature (not the root, the sac nor the effects) up by dy: call it after painting"""
    for b in m.bones:
        if b.name in keep:
            continue
        b.pivot[1] += dy
        for c in b.cubes:
            c.origin[1] += dy
            if c.pivot is not None:
                c.pivot = [c.pivot[0], c.pivot[1] + dy, c.pivot[2]]

# ---------------------------------------------------------------------------------------------------- palettes
NORMAL = {
    "skin": rgb("#3E7C88"), "skin_d": rgb("#2E6270"), "skin_l": rgb("#5592A0"), "crack": rgb("#21505C"),
    "scale_edge": rgb("#1E4652"), "scale_hi": rgb("#6AA6AE"), "olive": rgb("#8C9A5C"), "gold": rgb("#C8A44C"),
    "plate": rgb("#2A5866"), "plate_hi": rgb("#5E9AA4"), "crest": rgb("#7C4034"), "glint": rgb("#A6D2D4"),
    "belly": rgb("#D2CCC6"), "belly_d": rgb("#B2AAB4"),
    "fin": [rgb("#3E7C88"), rgb("#5C9478"), rgb("#9DB45A"), rgb("#DDB24E"), rgb("#D9743C"), rgb("#C2523A")],
    "claw": rgb("#16161C"), "claw_l": rgb("#4C4C5A"),
    "tooth": rgb("#EEE8DA"), "lip": rgb("#A87684"), "mouth": rgb("#5E2632"), "tongue": rgb("#9A4A5A"),
    "eye": rgb("#F2F8FF"), "eye_glow": rgb("#E8F6FF"),
    "ice": rgb("#F4F8FA"), "ice_m": rgb("#D8E4EA"), "ice_d": rgb("#9CB4C6"), "ice_b": rgb("#3E6688"),
    "ice_y": rgb("#DCCB92"), "ice_glow": rgb("#B8ECFF"), "frost": rgb("#C4D6DC"),
    "fx": rgb("#E8EEF2"), "fx_d": rgb("#B4C0C8"),
    "sac": rgb("#8E7670"), "sac_l": rgb("#B09890"), "sac_d": rgb("#5E4A48"), "vein": rgb("#56384A"),
    "sac_pink": rgb("#C08A92"),
}
SHINY = dict(NORMAL, **{   # blue-violet hide, gold fins, lavender ice
    "skin": rgb("#5A5290"), "skin_d": rgb("#463E74"), "skin_l": rgb("#7268AA"), "crack": rgb("#2C2650"),
    "scale_edge": rgb("#2A2452"), "scale_hi": rgb("#8C82C4"), "olive": rgb("#9A80B0"), "gold": rgb("#E0B65A"),
    "plate": rgb("#3E3670"), "plate_hi": rgb("#8478BC"), "crest": rgb("#B0783C"), "glint": rgb("#C8BCEC"),
    "belly": rgb("#DCD6E4"), "belly_d": rgb("#B8B0CC"),
    "fin": [rgb("#5A5290"), rgb("#8A6CB0"), rgb("#C08AB0"), rgb("#E8BE62"), rgb("#F0CC58"), rgb("#E6A23E")],
    "ice": rgb("#F2EEF8"), "ice_m": rgb("#D6CCE6"), "ice_d": rgb("#A898C8"), "ice_b": rgb("#5E4C96"),
    "ice_y": rgb("#E8D2A0"), "ice_glow": rgb("#E0C8FF"), "frost": rgb("#CCC6DC"), "eye_glow": rgb("#F4ECFF"),
    "sac": rgb("#8A7E98"), "sac_l": rgb("#ADA2BC"), "sac_d": rgb("#5A506C"), "vein": rgb("#4A3460"),
    "sac_pink": rgb("#C690B4")})

# ---------------------------------------------------------------------------------------------------- noise
def _h(*v):
    x = 0
    for a in v:
        x = (x * 1000003 + (int(a) & 0xFFFFFFFF) * 92821) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 1274126177) & 0xFFFFFFFF; x ^= x >> 16
    return (x & 0xFFFF) / 65535.0

def vnoise(x, y, z):
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - xi, y - yi, z - zi
    fx, fy, fz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    def c(a, b, d):
        return _h(xi + a, yi + b, zi + d)
    x00 = c(0, 0, 0) + (c(1, 0, 0) - c(0, 0, 0)) * fx
    x10 = c(0, 1, 0) + (c(1, 1, 0) - c(0, 1, 0)) * fx
    x01 = c(0, 0, 1) + (c(1, 0, 1) - c(0, 0, 1)) * fx
    x11 = c(0, 1, 1) + (c(1, 1, 1) - c(0, 1, 1)) * fx
    y0 = x00 + (x10 - x00) * fy
    y1 = x01 + (x11 - x01) * fy
    return y0 + (y1 - y0) * fz

def ramp(cols, t):
    t = max(0.0, min(0.999, t)) * (len(cols) - 1)
    i = int(t)
    return mix(cols[i], cols[i + 1], t - i)

LIGHT = {"up": 1.08, "north": 1.0, "south": 0.94, "east": 0.97, "west": 0.97, "down": 0.80}

def belly_line(z):
    """height under which the hide turns to the pale belly (throat low, rising toward the tail)"""
    if z < -24:
        return 25.0
    if z < 30:
        return 24.0 + (z + 24) * 0.04
    return 26.5

# ---------------------------------------------------------------------------------------------------- painters
def _frac(v):
    return v - math.floor(v)

def scales(face, x, y, z, big=1.0):
    """overlapping diamond scales, their free edge toward the tail (down on the front and back faces): returns
    (edge 0/1, t 0 at the root .. 1 at the free edge, scale id)"""
    if face in ("east", "west"):
        a, b = z, y
    elif face in ("up", "down"):
        a, b = z, x
    else:
        a, b = -y, x
    S = 3.5 * big
    u, v = a / S + b / S, a / S - b / S
    p, q = _frac(u / 2 + .25), _frac(v / 2 + .25)
    edge = 1 if (p > 1 - 0.55 / S or q > 1 - 0.55 / S) else 0
    return edge, (p + q) / 2, (math.floor(u / 2 + .25), math.floor(v / 2 + .25))

def skin(belly=True, big=1.0):
    """teal hide of overlapping scales (larger on the back), an olive-gold band above the pale belly, frost when
    armoured"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            x, y, z = w
            bl = belly_line(z) + (vnoise(x * .3, 0, z * .3) - .5) * 2.0
            under = face == "down" or (belly and y < bl)
            if under:
                col = mix(pal["belly"], pal["belly_d"], vnoise(x * .25, y * .25, z * .25) * 0.8)
                if int(math.floor(z / 2.5)) % 2 == 0 and face == "down":
                    col = mix(col, pal["belly_d"], 0.35)          # transverse belly plates
            else:
                n = vnoise(x * .08, y * .08, z * .08) * 0.7 + vnoise(x * .3, y * .3, z * .3) * 0.3
                col = mix(pal["skin_d"], pal["skin_l"], max(0.0, min(1.0, 0.15 + 0.7 * n + 0.010 * (y - 30))))
                if y > 46 and face != "down":                      # darker along the spine
                    col = mix(col, pal["skin_d"], min(0.45, (y - 46) * 0.06))
                if belly:                                          # olive then gold on the lower flanks
                    k = (y - bl) + (vnoise(x * .2 + 7, y * .1, z * .2) - .5) * 4
                    if k < 15:
                        col = mix(col, pal["olive"], min(0.8, 1.1 * (1 - k / 15)))
                    if k < 6:
                        col = mix(col, pal["gold"], 0.6 * (1 - k / 6))
                if z > 34:                                         # the tail turns olive then gold toward its tip
                    col = mix(col, pal["olive"], min(0.55, (z - 34) / 50))
                    if z > 58:
                        col = mix(col, pal["gold"], min(0.5, (z - 58) / 30))
                e, t, sid = scales(face, x, y, z, big * (1.25 if y > 46 else 1.0))
                if e:
                    col = mix(col, pal["scale_edge"], 0.6)
                else:
                    hi = pal["glint"] if _h(sid[0], sid[1], 31) > 0.86 else pal["scale_hi"]
                    col = mix(mix(col, pal["scale_edge"], 0.22 * (1 - t)), hi, 0.42 * t * t)
                if pal.get("_frost"):                              # hoarfrost on the hide, snow on the top faces
                    f = vnoise(x * .15 + 11, y * .15, z * .15) + (0.3 if face == "up" else 0) + 0.006 * (y - 30)
                    col = mix(col, pal["frost"], 0.18)
                    if f > 0.62:
                        col = mix(col, pal["ice"], min(0.85, (f - 0.62) * 3))
            px[X, Y] = shade(col, LIGHT[face] * (1 + (_h(X, Y) - .5) * 0.03))
    return {"fn3": fn3, "base": None}

def plate(flat=False):
    """big scale plates and crest teeth: dark with a light front edge and a dark rim; crest teeth turn red-brown
    toward their tips, flat shingles darken toward their free (back) edge"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            fx_, fy_, fw, fh = faces[face]
            i, j = X - fx_, Y - fy_
            if flat:
                t = (p[2] - c.origin[2]) / max(c.size[2], 1)
                col = mix(pal["plate_hi"], pal["plate"], 0.3 + 0.7 * t)
            else:
                t = along(p, None, c)
                col = mix(pal["plate"], pal["plate_hi"], 0.5 * (1 - t))
                if t > 0.45:
                    col = mix(col, pal["crest"], min(0.85, (t - 0.45) * 2.2))
            if i == 0 or i == fw - 1 or j == 0 or j == fh - 1:
                col = mix(col, pal["scale_edge"], 0.45)
            if pal.get("_frost"):
                col = mix(col, pal["frost"], 0.3)
            px[X, Y] = shade(col, LIGHT[face])
    return {"fn3": fn3, "base": None}

def jawpaint():
    """lower jaw / throat: pale, lavender shading, the mouth floor dark pink"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            x, y, z = apply(c.world, p)
            if face == "up":
                col = pal["tongue"] if abs(x) < 4 else pal["mouth"]
            else:
                col = mix(pal["belly"], pal["belly_d"], vnoise(x * .3, y * .3, z * .3))
                if int(math.floor(z / 2.0)) % 2 == 0 and (face == "down" or y < 20):
                    col = mix(col, pal["belly_d"], 0.4)           # ridged throat
                if face != "down" and y > 23.5:
                    col = mix(col, pal["lip"], 0.6)
            px[X, Y] = shade(col, LIGHT[face])
    return {"fn3": fn3, "base": None}

def headpaint():
    """the upper head: hide, a pink lip band along the mouth, the palate dark"""
    sk = skin(belly=False, big=0.75)["fn3"]
    def fn3(px, faces, pal, rnd, c):
        sk(px, faces, pal, rnd, c)
        for face, X, Y, p in c.texels():
            x, y, z = apply(c.world, p)
            if face == "down":
                px[X, Y] = shade(pal["mouth"], LIGHT[face])
            elif face != "up" and y < 27.2:
                px[X, Y] = shade(pal["lip"], LIGHT[face])
            elif face in ("east", "west") and -38 < z < -27 and 28 < y < 40 and abs((z + 37) % 3.5 - 1) < 0.5:
                px[X, Y] = shade(pal["crack"], 0.9)               # gill slits
            elif face in ("east", "west") and -59.5 < z < -51.5 and 33 < y < 39.5:
                px[X, Y] = shade(mix(pal["skin_d"], pal["crack"], 0.6), LIGHT[face])   # eye socket
            elif face == "north" and abs(abs(x) - 3.5) < 1.5 and 32 < y < 33:
                px[X, Y] = shade(pal["crack"], 0.8)               # nostrils
    return {"fn3": fn3, "base": None}

def fin(tfun):
    """fins: teal at the root, green, yellow then orange toward the edge (tfun: model point -> 0..1), fine ribs"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            t = tfun(p, w, c)
            col = ramp(pal["fin"], t)
            if int(math.floor(w[2] + w[1] * 0.3)) % 4 == 0:
                col = shade(col, 0.78)                             # ribs
            elif (_h(int(w[2] * 0.7), int(w[1] * 0.5), 5) > 0.85):
                col = shade(col, 0.9)
            if t > 0.92:
                col = mix(col, pal["fin"][-1], 0.5)                # darker torn edge
            if pal.get("_frost"):
                col = mix(col, pal["frost"], 0.25)
            px[X, Y] = shade(col, LIGHT[face] * (1 + (_h(X, Y, 2) - .5) * 0.05))
    return {"fn3": fn3, "base": None}

def along(p, w, c):
    """0 at the root of a segment cube, 1 at its far end (segments run along their local +Y)"""
    return (p[1] - c.origin[1]) / max(c.size[1], 1)

def claw():
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            t = along(p, None, c)
            col = mix(pal["claw"], pal["claw_l"], 0.5 if (face in ("up",) or (face == "north" and t > .6)) else 0.0)
            px[X, Y] = shade(col, LIGHT[face])
    return {"fn3": fn3, "base": None}

def flat(key, glow=None):
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            px[X, Y] = shade(pal[key], LIGHT[face])
    d = {"fn3": fn3, "base": None}
    if glow:
        def glow_fn(px, faces, pal, rnd, c):
            for face, X, Y, p in c.texels():
                px[X, Y] = pal[glow][:3] + (255,)
        d["glow_fn"] = glow_fn
    return d

def _ice_local(p, c, face):
    """(across 0..1, along 0..1, streak offset) of a texel of an ice cube, the streak offsets hashed per cube"""
    t = along(p, None, c)
    if face in ("east", "west"):
        u = (p[2] - c.origin[2]) / max(c.size[2], 1)
    else:
        u = (p[0] - c.origin[0]) / max(c.size[0], 1)
    k = _h(int(c.origin[0] * 7), int(c.origin[1] * 7), int(c.origin[2] * 7), len(face))
    return u, t, k

def _ice_streak(p, c, face):
    """distance (texels) to the crystal's dark inner streak on this face; large on caps"""
    if face in ("up", "down"):
        return 99.0
    u, t, k = _ice_local(p, c, face)
    w = c.size[2] if face in ("east", "west") else c.size[0]
    if w < 3:
        return 99.0
    s0 = 0.25 + 0.5 * k + (0.18 if k > 0.5 else -0.18) * t
    return abs(u - s0) * w

def ice():
    """crystalline ice: pale blue at the root to white at the tip, one long dark-blue streak per face, one face of
    each crystal a little bluer (facets), a warm tint here and there"""
    def colour(pal, p, w, c, face):
        x, y, z = w
        t = along(p, w, c)
        col = mix(pal["ice_m"], pal["ice"], min(1.0, 0.35 + 0.75 * t))
        if face in ("east", "south"):
            col = mix(col, pal["ice_d"], 0.22)
        d = _ice_streak(p, c, face)
        if d < 0.6:
            col = mix(col, pal["ice_b"], 0.7)
        elif d < 1.6:
            col = mix(col, pal["ice_d"], 0.45)
        if face == "down":
            col = mix(col, pal["ice_d"], 0.3)
        if vnoise(x * .1 + 40, y * .1, z * .1) > 0.78:
            col = mix(col, pal["ice_y"], 0.3)
        return col
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            px[X, Y] = shade(colour(pal, p, w, c, face), LIGHT[face])
    return {"fn3": fn3, "base": None, "_colour": colour}

ICE = ice()

def glow_shell(src):
    """glow shell of an ice cube: transparent in the base texture, its glow in the emissive layer"""
    def fn3(px, faces, pal, rnd, c):
        return
    def glow_fn(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            d = _ice_streak(p, c, face)
            if 0.6 <= d < 2.2:                                     # light running beside the ice's inner streaks
                g = pal["ice_glow"]
                px[X, Y] = g[:3] + (int(170 - 60 * (d - 0.6)),)
    return {"fn3": fn3, "base": None, "glow_fn": glow_fn}

def sac():
    """inflated sac: stretched mauve-brown skin, lighter on top, darker toward the ground, fine stretch wrinkles,
    deeper folds near the top where it gathers under the body, dark purple veins, the pink of the mouth showing
    under the jaw; painted at full size"""
    def fn3(px, faces, pal, rnd, c):
        px_, py_, pz_ = BALLOON_P
        K = BALLOON_K
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            x, y, z = px_ + K * (w[0] - px_), py_ + K * (w[1] - py_), pz_ + K * (w[2] - pz_)
            u = y / SAC_H
            n = vnoise(x * .06, y * .06, z * .06)
            col = mix(pal["sac_d"], pal["sac_l"], max(0.0, min(1.0, 0.15 + 0.7 * u + 0.3 * (n - .5))))
            col = mix(col, pal["sac"], 0.35)
            if face == "down" or u < 0.06:
                col = mix(col, pal["sac_d"], 0.5)
            ph = y * 0.85 + 5.0 * vnoise(x * .03 + 3, z * .03, 1) + 0.6 * math.sin(z * 0.11 + x * 0.07)
            wr = math.sin(ph)
            if wr > 0.93:                                          # fine stretch wrinkles
                col = mix(col, pal["sac_d"], 0.35)
            elif wr < -0.97:
                col = mix(col, pal["sac_l"], 0.35)
            if u > 0.72 and math.sin(y * 0.45 + 2.0 * vnoise(x * .05, z * .05, 7)) > 0.8:
                col = mix(col, pal["sac_d"], 0.45)                 # deeper folds where the skin gathers
            v = abs(vnoise(x * .045 + 5, y * .045, z * .045) - .5)
            if v < 0.009 and vnoise(x * .02 + 1, y * .02, z * .02) > 0.4:
                col = mix(col, pal["vein"], 0.75)                  # veins
            if z < -40 and abs(x) < 15 and 0.6 < u < 0.78:
                col = mix(col, pal["sac_pink"], 0.55)              # the mouth's lining under the jaw
            if _h(X, Y, 77) > 0.9:
                col = shade(col, 0.93)
            px[X, Y] = shade(col, LIGHT[face])
    return {"fn3": fn3, "base": None}

def fx():
    """the roar's shock wave on the ground: a thin ring of snow on the ground, jagged spray rising around it"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            x, y, z = p
            if c.rotation is None:
                r = math.hypot(x, z)
                keep = 17 < r < 23.5 and vnoise(x * .5, 0, z * .5) > 0.5
            else:
                d = abs(z - c.pivot[2])                       # distance from the hinge on the ring
                u = x if c.rotation[1] == 0 else -z
                tip = 3 + 15 * vnoise(x * .45 + z * .45, 1, 2) ** 2
                keep = d < tip and vnoise(x * .9 + 3, z * .9, 4) > 0.35
            if keep:
                col = mix(pal["fx_d"], pal["fx"], vnoise(x * .3, z * .3, 9))
                px[X, Y] = col[:3] + (255,)
    return {"fn3": fn3, "base": None}

# ---------------------------------------------------------------------------------------------------- shapes
def dir_rot(d):
    n = math.sqrt(sum(v * v for v in d))
    dx, dy, dz = (v / n for v in d)
    return [round(math.degrees(math.asin(max(-1.0, min(1.0, -dz)))), 2), 0, round(math.degrees(math.atan2(dx, dy)), 2)]

def seg(p0, p1, w, d, paint, sunk=1.0, inflate=None):
    v = [b - a for a, b in zip(p0, p1)]
    L = math.sqrt(sum(x * x for x in v))
    x, y, z = p0
    return Cube([x - w / 2, y - sunk, z - d / 2], [w, max(1, int(round(L + sunk))), d], paint,
                rotation=dir_rot(v), pivot=list(p0), inflate=inflate)

def chain(p, dirs, lens, widths, paints):
    out = []
    x, y, z = p
    for i, (dd, L, w) in enumerate(zip(dirs, lens, widths)):
        n = math.sqrt(sum(v * v for v in dd))
        dh = [v / n for v in dd]
        wx, wz = w if isinstance(w, tuple) else (w, w)
        sunk = min(wx, wz) / 2 if i == 0 else 0.5
        pt = paints[i] if isinstance(paints, list) else paints
        out.append(Cube([x - wx / 2, y - sunk, z - wz / 2], [wx, int(round(L + sunk)), wz], pt,
                        rotation=dir_rot(dd), pivot=[x, y, z]))
        x, y, z = x + dh[0] * (L - 0.5), y + dh[1] * (L - 0.5), z + dh[2] * (L - 0.5)
    return out

def box(x0, x1, y0, y1, z0, z1, paint, inflate=None):
    return Cube([x0, y0, z0], [x1 - x0, y1 - y0, z1 - z0], paint, inflate=inflate)

def sbox(hw, y0, y1, z0, z1, paint, inflate=None):
    """symmetric box around x = 0"""
    return box(-hw, hw, y0, y1, z0, z1, paint, inflate)

def spike(p, d, L, w0, paint=ICE):
    """a tapering ice spike: 3 segments (4 for the thick ones)"""
    d2 = (d[0], d[1] + 0.15, d[2])
    if w0 >= 6:
        ws = [w0, max(2, round(w0 * 0.7)), max(2, round(w0 * 0.42)), 1]
        return chain(p, [d, d, d, d2], [round(L * .34), round(L * .28), round(L * .24), round(L * .2)],
                     [(w, w) for w in ws], paint)
    w1 = max(1, round(w0 * 0.6)); w2 = 1
    return chain(p, [d, d, d2], [round(L * .45), round(L * .33), round(L * .25)],
                 [(w0, w0), (w1, w1), (w2, w2)], paint)

def shingle(x, y, z, w, L, s=0, tilt=10, roll=0):
    """a flat scale plate lying on the hide (front edge at x, y, z), its back edge lifted by `tilt` degrees and
    rolled outward by `roll` degrees on the side s"""
    return Cube([x - w / 2, y - 0.5, z], [w, 1, L], PLATE_FLAT, rotation=[tilt, 0, roll * s], pivot=[x, y, z])

def tooth_row(zs, top, L0, L1, x=0.0, w=2):
    """a serrated crest of small plates pointing up and back along the midline"""
    out = []
    n = max(1, len(zs) - 1)
    for k, z in enumerate(zs):
        L = L0 + (L1 - L0) * k / n
        y = top(z)
        out.append(seg((x, y - 0.5, z), (x, y + L, z + 0.8 * L), w, 2, PLATE, sunk=1.0))
    return out

def mx(p, s):
    return (p[0] * s, p[1], p[2])

def md(d, s):
    return (d[0] * s, d[1], d[2])

# ---------------------------------------------------------------------------------------------------- model
FX = ("specialfx1",)
SKIN, SKIN_TOP = skin(), skin(belly=False)
LIMB = skin(belly=False, big=0.8)
PLATE, PLATE_FLAT = plate(), plate(flat=True)
HEAD, JAW, CLAW = headpaint(), jawpaint(), claw()
FIN_A = fin(lambda p, w, c: 0.1 + 0.55 * along(p, w, c))
FIN_B = fin(lambda p, w, c: 0.62 + 0.38 * along(p, w, c))

def dorsal(t_eval=False):
    """the tall swept dorsal fin: slabs 2 units thick from the hump (y 57) to the tip (y 83)"""
    def zf(t):
        return -10 + 34 * t ** 1.6
    def zb(t):
        return 16 + 8 * t - 6 * math.sin(math.pi * t)
    def tf(p, w, c):
        t = (w[1] - 59) / 26
        u = (w[2] - zf(t)) / max(1.0, zb(t) - zf(t))
        return 0.15 + 0.55 * max(0.0, u) + 0.40 * t
    cubes = []
    n = 13
    for i in range(n):
        t = i / n
        a, b = round(zf(t)), round(max(zb(t), zf(t) + 2))
        cubes.append(box(-1, 1, 59 + 2 * i, 61 + 2 * i, a, b, fin(tf)))
    return cubes

def caudal():
    """vertical tail fin: a big upper lobe swept up-back, a smaller lower lobe"""
    def tf(p, w, c):
        return min(1.0, 0.1 + math.hypot(w[1] - 28, w[2] - 75) / 22)
    cubes = [box(-1, 1, 24, 32, 73, 83, fin(tf))]
    for i in range(11):
        t = i / 11
        a = round(75 + 15 * t ** 1.3); b = round(max(84 + 9 * t - 4 * math.sin(math.pi * t), a + 2))
        cubes.append(box(-1, 1, 32 + 2 * i, 34 + 2 * i, a, b, fin(tf)))
    for i in range(6):
        t = i / 6
        a = round(77 + 10 * t ** 1.2); b = round(max(84 + 4 * t - 3 * math.sin(math.pi * t), a + 2))
        cubes.append(box(-1, 1, 22 - 2 * i, 24 - 2 * i, a, b, fin(tf)))
    return cubes

def build(form):
    """form: normal | armor | inflated"""
    name = {"normal": "zamtrios", "armor": "zamtrios_armor", "inflated": "zamtrios_inflated"}[form]
    m = Model(name, DEX, (512, 512))
    m.bone("zamtrios", None, [0, 0, 0])                 # root pivot on the ground: Cobblemon ignores a root pivot
    # ------------------------------------------------------------------ body (shoulder hump, hips, dorsal fin)
    body = m.bone("body", "zamtrios", [0, 31, -27])
    body.cubes += [sbox(14, 16, 52, -30, -14, SKIN), sbox(16, 17, 58, -14, 2, SKIN), sbox(15, 19, 54, 2, 16, SKIN),
                   sbox(13, 21, 47, 16, 28, SKIN), sbox(9.5, 23, 41, 28, 36, SKIN),
                   sbox(10, 52, 55, -29, -15, SKIN_TOP), sbox(11, 58, 60, -13, 1, SKIN_TOP),
                   sbox(10, 54, 57, 3, 15, SKIN_TOP), sbox(8, 47, 49, 17, 27, SKIN_TOP),
                   sbox(17, 24, 48, -12, 0, SKIN), sbox(16, 24, 46, 4, 14, SKIN)]          # flanks bulging
    body.cubes += dorsal()
    # crest teeth along the spine (before and after the fin), two rows of large scale plates on each side
    def btop(z):
        return 55 if z < -14 else 60 if z < 2 else 57 if z < 16 else 49 if z < 28 else 41
    body.cubes += tooth_row([-29, -25, -21, -17, -13], btop, 5, 7)
    body.cubes += tooth_row([18, 22, 26, 30, 34], btop, 6, 4)
    for s_ in (1, -1):
        for z in range(-28, 26, 6):
            body.cubes.append(shingle(6.5 * s_, btop(z), z, 5, 7, s_, tilt=-8, roll=8))
    # ------------------------------------------------------------------ head and jaw
    head = m.bone("head", "zamtrios", [0, 31, -27])
    segs = [(-40, -24, 25, 48, 12.5), (-50, -40, 25, 47, 13.5), (-58, -50, 25, 44, 12.5), (-64, -58, 26, 40, 11),
            (-68, -64, 27, 36, 8.5), (-71, -68, 28, 33, 6)]
    for z0, z1, y0, y1, hw in segs:
        head.cubes.append(sbox(hw, y0, y1, z0, z1, HEAD))
    for z0, z1, y0, y1, hw in segs[:4]:
        head.cubes.append(sbox(hw - 4, y1, y1 + (2 if z0 > -60 else 1), z0 + 1, z1 - 1, SKIN_TOP))
    for z0, z1, y0, y1, hw in segs[1:4]:                                            # rounded cheeks
        head.cubes.append(sbox(hw + 1, y0 + 4, y1 - 5, z0 + 1, z1 - 1, SKIN_TOP))
    head.cubes.append(sbox(11, 17, 25, -42, -26, JAW))                              # throat
    def htop(z):
        return 50 if z >= -40 else 49 if z >= -50 else 46 if z >= -58 else 41
    head.cubes += tooth_row([-61, -56, -51, -46, -41, -36, -31], htop, 2.5, 7.5)  # rugged crest, red-brown tips
    for s in (1, -1):                                                               # a row of spikes behind each eye
        for k, z in enumerate((-48, -42, -36, -30)):
            r = (10.5 * s, 47.5 - 0.3 * k, z)
            head.cubes.append(seg(r, (r[0] + 2 * s, r[1] + 3.5 + k, z + 4 + k), 2, 2, PLATE, sunk=1.0))
    for s in (1, -1):                                                               # brow ridges over the eyes
        head.cubes.append(box(*sorted((10.5 * s, 13.5 * s)), 38, 40, -60, -50, SKIN_TOP))
        for z in (-48, -42, -36):                                                   # cheek plates
            head.cubes.append(shingle(12.5 * s, 41, z, 4, 6, s, tilt=-4, roll=40))
    for s in (1, -1):                                                               # upper teeth
        for k, z in enumerate(range(-65, -43, 3)):
            hw = 7.5 if z < -63 else (10.0 if z < -57 else 11.5)
            head.cubes.append(box(s * hw - 0.5, s * hw + 0.5, 23, 25, z, z + 1, flat("tooth")))
    for x in (-4.5, -1.5, 1.5, 4.5):
        head.cubes.append(box(x - 0.5, x + 0.5, 24, 26, -68, -67, flat("tooth")))
    eyes = m.bone("eyes", "head", [0, 37, -55])
    for s in (1, -1):
        eyes.cubes.append(box(s * 13.5 - (1 if s < 0 else 0), s * 13.5 + (0 if s < 0 else 1), 35, 37, -57, -54,
                              flat("eye", glow="eye_glow")))
    jaw = m.bone("jaw", "head", [0, 25.25, -39.5])
    jaw.cubes += [sbox(11, 16, 25, -52, -38, JAW), sbox(9.5, 17, 25, -61, -52, JAW), sbox(7, 19, 25, -67, -61, JAW)]
    for s in (1, -1):                                       # the white mandible blades, pointing back and down
        jaw.cubes += chain(mx((9, 17, -53), s), [(0.03 * s, -0.1, 1), (0.03 * s, -0.45, 1)], [14, 4],
                           [(3, 3), (2, 2)], [JAW, JAW])
    for s in (1, -1):
        for z in range(-64, -42, 3):
            hw = 6.0 if z < -61 else (8.0 if z < -52 else 9.5)
            jaw.cubes.append(box(s * hw - 0.5, s * hw + 0.5, 25, 27, z + 1, z + 2, flat("tooth")))
    # ------------------------------------------------------------------ fore limbs (sprawled) with forearm fins
    for s, side in ((1, "left"), (-1, "right")):
        arm = m.bone(f"{side}arm", "body", [14 * s, 31, -14])
        arm.cubes += [box(*sorted((8 * s, 24 * s)), 25, 43, -23, -5, LIMB),
                      seg(mx((18, 34, -14), s), mx((33, 27, -10), s), 14, 13, LIMB),
                      shingle(13 * s, 43, -22, 6, 8, s, tilt=-8, roll=18), shingle(20 * s, 42, -21, 6, 8, s, tilt=-8, roll=34)]
        low = m.bone(f"lower{side}arm", f"{side}arm", [32 * s, 29, -9])
        low.cubes += [box(*sorted((26 * s, 38 * s)), 22, 34, -16, -4, LIMB),
                      seg(mx((33, 28, -10), s), mx((37, 7, -17), s), 12, 11, LIMB)]
        for k in range(6):                     # the forearm fin: overlapping feather-like plates fanning up and back
            r = mx((38.5 - 0.3 * k, 27 - 3.8 * k, -6 - 1.4 * k), s)
            L = 23 - 3.0 * k
            low.cubes += chain(r, [md((0.25, 0.55, 0.8), s), md((0.25, 0.75, 0.75), s)],
                               [round(L * 0.68), round(L * 0.42)], [(1, 9), (1, 5)], [FIN_A, FIN_B])
        hand = m.bone(f"{side}hand", f"lower{side}arm", [39 * s, 11, -13])
        hand.cubes.append(box(*sorted((28 * s, 43 * s)), 0, 7, -28, -8, SKIN_TOP))
        for x in (30.5, 35.5, 40.5):           # three fingers ending in long black claws
            hand.cubes += chain(mx((x, 3.5, -27), s), [(0, 0.1, -1), (0, -0.45, -1)], [6, 7], [(4, 4), (2, 3)],
                                [SKIN_TOP, CLAW])
        hand.cubes += chain(mx((29.5, 4, -12), s), [md((-0.7, 0.2, -0.7), s), md((-0.4, -0.5, -0.8), s)], [4, 4],
                            [(3, 3), (2, 2)], [SKIN_TOP, CLAW])
    # ------------------------------------------------------------------ hind legs
    for s, side in ((1, "left"), (-1, "right")):
        leg = m.bone(f"{side}leg", "body", [11 * s, 25, 15])
        leg.cubes += [box(*sorted((6 * s, 24 * s)), 13, 38, 1, 25, LIMB), box(*sorted((8 * s, 22 * s)), 38, 41, 4, 22, SKIN_TOP),
                      shingle(15 * s, 41, 4, 7, 8, s, tilt=-6, roll=20), shingle(16 * s, 40.5, 12, 7, 8, s, tilt=-6, roll=26)]
        low = m.bone(f"lower{side}leg", f"{side}leg", [15 * s, 17, 20])
        low.cubes.append(seg(mx((15, 18, 22), s), mx((16.5, 6, 32), s), 11, 11, LIMB))
        foot = m.bone(f"{side}foot", f"lower{side}leg", [17.8354 * s, 9, 32.36612], rotation=[0, 12.5 * s, 0])
        foot.cubes.append(box(*sorted((11 * s, 24 * s)), 0, 6, 11, 35, SKIN_TOP))
        for x in (13, 17.5, 22):
            foot.cubes += chain(mx((x, 3, 12.5), s), [(0, 0.1, -1), (0, -0.5, -1)], [4, 5], [(3, 3), (2, 2)],
                                [SKIN_TOP, CLAW])
    # ------------------------------------------------------------------ tail and caudal fin
    t1 = m.bone("tail1", "body", [0, 27, 29])
    t1.cubes += [sbox(9, 22, 38, 30, 45, SKIN), sbox(7, 23, 36, 45, 56, SKIN)]
    t2 = m.bone("tail2", "tail1", [0, 26, 52], rotation=[6, 0, 0])               # the tip held a little up
    t2.cubes += [sbox(5.5, 23, 34, 54, 64, SKIN), sbox(4, 24, 32, 64, 72, SKIN), sbox(3, 25, 31, 72, 77, SKIN)]
    t2.cubes += caudal()
    t1.cubes += tooth_row([32, 37, 42, 47, 52], lambda z: 38 if z < 45 else 36, 4, 3.5)
    t2.cubes += tooth_row([57, 62, 67, 71], lambda z: 34 if z < 64 else 32, 3.5, 2.5)
    for s in (1, -1):
        for z in (31, 38, 45):
            t1.cubes.append(shingle(6.5 * s, 37.5 if z < 45 else 35.5, z, 4, 7, s, tilt=-6, roll=30))
    def vtf(p, w, c):
        return min(1.0, 0.35 + (23 - w[1]) / 10)
    for i, z in enumerate(range(56, 74, 2)):                 # golden fringe fin under the tail
        depth = round(3 + 5 * math.sin(math.pi * (i + 1) / 10))
        t2.cubes.append(box(-0.5, 0.5, 24 - depth, 24, z, z + 2, fin(vtf)))
    # ------------------------------------------------------------------ the roar's shock wave (hidden by default)
    f = m.bone("specialfx1", None, [0, 0, 0])
    FXP = fx()
    f.cubes += [Cube([-24, 0, -24], [48, 0, 48], FXP),
                Cube([-24, 0, -48], [48, 0, 24], FXP, rotation=[-60, 0, 0], pivot=[0, 0, -24]),
                Cube([-48, 0, -24], [48, 0, 24], FXP, rotation=[0, 90, 60], pivot=[-24, 0, 0]),
                Cube([0, 0, -24], [48, 0, 24], FXP, rotation=[0, -90, -60], pivot=[24, 0, 0]),
                Cube([-24, 0, 24], [48, 0, 24], FXP, rotation=[60, 0, 0], pivot=[0, 0, 24])]
    if form == "armor":
        armour(m)
    if form == "inflated":
        # the sac, built at 1/K size around its pivot on the ground: 18 slices, each a 12-sided footprint (3 boxes)
        px_, py_, pz_ = BALLOON_P
        K = BALLOON_K
        bal = m.bone("balloon", "zamtrios", list(BALLOON_P))
        SAC = sac()
        n, hs = 33, int(SAC_H / K / 33)
        for k in range(n):
            u = (k + 0.5) / n
            rx, rz, zc = sac_profile(u)
            if rx < 1:
                continue
            y0 = py_ + k * hs
            zc = pz_ + (zc - pz_) / K
            for cth, sth in ((0.906, 0.423), (0.643, 0.766), (0.259, 0.966)):
                ax, az = max(1, round(rx * cth / K)), max(1, round(rz * sth / K))
                bal.cubes.append(Cube([px_ - ax, y0, round(zc - az, 1)], [2 * ax, hs, 2 * az], SAC))
    m.pack()
    return m

ICE_BONES = []

def armour(m):
    """the Ice Armour: an ice mask and a huge horn on the head, a crown of long spikes on the back, the dorsal fin
    sheathed, iced shoulders, forearm fins, thighs and tail; a glow shell for each ice bone"""
    bones = []
    ia = m.bone("icearmor", "head", [0, 39, -68])
    for z0, z1, y0, y1, hw in ((-40, -26, 29, 47, 12.5), (-50, -40, 29, 47, 13), (-58, -50, 29, 45, 12),
                               (-64, -58, 30, 42, 10.5), (-68, -64, 30, 39, 8)):
        ia.cubes.append(sbox(hw, y0, y1, z0, z1, ICE, 0.35))                       # ice mask (mouth left free)
    ia.cubes += chain((0, 41, -66), [(0, 0.25, -1), (0, 0.35, -1), (0, 0.5, -1)], [16, 14, 12],
                      [(10, 10), (7, 7), (3, 3)], ICE)                              # the great horn
    ia.cubes += spike((0, 46, -54), (0, 1, -0.35), 18, 7)
    for z, top, L in ((-46, 47, 9), (-40, 47.5, 10), (-34, 47.5, 11), (-28, 47.5, 10)):   # ice crest
        ia.cubes += spike((0, top, z), (0, 1, 0.75), L, 4)
    for s_ in (1, -1):                                                                 # ice frills on the cheeks
        ia.cubes += spike(mx((13, 33, -50), s_), md((0.45, 0.1, 1), s_), 12, 4)
        ia.cubes += spike(mx((13.5, 31, -42), s_), md((0.5, 0.0, 1), s_), 14, 4)
    for s_ in (1, -1):
        ia.cubes += spike(mx((11, 44, -46), s_), md((0.5, 0.8, 0.6), s_), 20, 6)
        ia.cubes += spike(mx((12, 46, -34), s_), md((0.45, 0.9, 0.75), s_), 24, 7)
    bones.append(ia)
    ba = m.bone("bodyicearmor", "body", [0, 49, -12])
    ba.cubes += [sbox(13, 55, 60, -26, 8, ICE, 0.3), sbox(10, 48, 52, 8, 28, ICE, 0.3)]
    for z, L in ((-27, 9), (-22, 11), (-17, 12)):
        ba.cubes += spike((0, 58, z), (0, 1, 0.6), L, 4)
    ba.cubes += chain((0, 59, -9), [(0, 1, 0.4), (0, 1, 0.55), (0, 1, 0.8)], [16, 13, 10], [(5, 10), (3, 6), (1, 2)], ICE)
    for s_ in (1, -1):
        for root, dd, L, w in (((6, 57, -20), (0.2, 1, 0.25), 34, 9), ((12, 55, -8), (0.5, 1, 0.45), 32, 8),
                               ((13, 52, 6), (0.6, 0.9, 0.6), 26, 7), ((10, 47, 20), (0.5, 0.8, 0.8), 18, 5)):
            ba.cubes += spike(mx(root, s_), md(dd, s_), L, w)
    bones.append(ba)
    for s_, side in ((1, "left"), (-1, "right")):
        sh = m.bone(f"{side}armicearmor", f"{side}arm", [14 * s_, 31, -14])
        sh.cubes += spike(mx((18, 41, -16), s_), md((0.7, 1, 0.2), s_), 20, 7)
        bones.append(sh)
        fa = m.bone(f"lower{side}armicearmor", f"lower{side}arm", [32 * s_, 29, -9])
        fa.cubes += spike(mx((38.5, 25, -6), s_), md((0.3, 0.55, 0.8), s_), 26, 6)
        fa.cubes += spike(mx((38.5, 17, -9), s_), md((0.3, 0.45, 0.85), s_), 20, 5)
        fa.cubes += spike(mx((37, 12, -14), s_), md((0.9, 0.2, -0.3), s_), 10, 4)
        bones.append(fa)
        lg = m.bone(f"{side}legicearmor", f"{side}leg", [11 * s_, 25, 15])
        lg.cubes += spike(mx((18, 36, 10), s_), md((0.5, 1, 0.6), s_), 16, 6)
        bones.append(lg)
    ta = m.bone("tailicearmor", "tail2", [0, 26, 52])
    for z, L in ((56, 13), (64, 11)):
        ta.cubes += spike((0, 33, z), (0, 1, 0.8), L, 6)
    ta.cubes += spike((0, 50, 87), (0, 1, 0.6), 16, 5) + spike((0, 14, 85), (0, -1, 0.7), 12, 4)
    ta.cubes += [box(-1.5, 1.5, 34, 48, 77, 90, ICE, 0.25)]
    bones.append(ta)
    t1a = m.bone("tail1icearmor", "tail1", [0, 27, 29])
    t1a.cubes += spike((0, 36, 34), (0, 1, 0.6), 15, 7) + spike((0, 35, 46), (0, 1, 0.7), 13, 6)
    bones.append(t1a)
    # glow shells (children of each ice bone), hidden while asleep
    ICE_BONES.clear()
    for b in bones:
        g = m.bone(b.name + "_glow", b.name, list(b.pivot))
        for c in b.cubes:
            g.cubes.append(Cube(list(c.origin), list(c.size), glow_shell(c), rotation=c.rotation, pivot=c.pivot,
                                inflate=(c.inflate or 0) + 0.15))
        ICE_BONES.append(b.name)
