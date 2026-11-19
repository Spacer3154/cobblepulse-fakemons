# -*- coding: utf-8 -*-
"""#11233 Zamtrios (Monster Hunter), rebuilt on the skeleton of the supplied remaster model (same bones, same pivots:
its GeckoLib animations still drive it), with the shapes and colours of the reference pictures:

* a big rounded shark head (high crown, blunt bullet snout, white eye, a pink-lipped mouth lined with teeth, a pale
  lower jaw and throat), a hunched body with a tall swept shark dorsal fin (teal leading edge, the trailing half
  green-yellow-orange), sprawled fore limbs carrying a ribbed fin on the forearm, crouched hind legs, long black
  claws, a long tail ending in a vertical caudal fin (bigger upper lobe), deep teal hide with darker cracks, pale
  cream-lavender belly;
* Ice Armour: the hide frosted, a huge ice horn growing forward from the snout, an ice cap on the skull and spikes
  along its sides, a crown of long ice spikes on the shoulders and back, the dorsal fin sheathed in ice, iced forearm
  fins, shoulders, thighs and tail fin; every ice bone has a glow shell (emissive layer only, hidden asleep);
* Inflated: the giant sac (built at half size, scaled x2 by every animation).

Front = -Z, ground = y 0, left = +X (Blockbench shows +X on the screen's right)."""
import math
from modelgen import Model, Cube, rgb, shade, mix, apply

DEX, SID = 11233, "zamtrios"
FOLDER = "11233_zamtrios"
BALLOON_C = (0.0, 40.0, 6.0)          # centre and radii of the inflated sac (full size, model units)
BALLOON_R = (44.0, 40.0, 46.0)
BALLOON_K = 2.0                       # built at 1/K size, scaled xK by the animations

# ---------------------------------------------------------------------------------------------------- palettes
NORMAL = {
    "skin": rgb("#3E7C88"), "skin_d": rgb("#2E6270"), "skin_l": rgb("#5592A0"), "crack": rgb("#21505C"),
    "belly": rgb("#D2CCC6"), "belly_d": rgb("#B2AAB4"),
    "fin": [rgb("#3E7C88"), rgb("#5C9478"), rgb("#9DB45A"), rgb("#DDB24E"), rgb("#D9743C"), rgb("#C2523A")],
    "claw": rgb("#16161C"), "claw_l": rgb("#4C4C5A"),
    "tooth": rgb("#EEE8DA"), "lip": rgb("#A87684"), "mouth": rgb("#5E2632"), "tongue": rgb("#9A4A5A"),
    "eye": rgb("#F2F8FF"), "eye_glow": rgb("#E8F6FF"),
    "ice": rgb("#F4F8FA"), "ice_m": rgb("#D8E4EA"), "ice_d": rgb("#9CB4C6"), "ice_b": rgb("#3E6688"),
    "ice_y": rgb("#DCCB92"), "ice_glow": rgb("#B8ECFF"), "frost": rgb("#C4D6DC"),
    "fx": rgb("#E8EEF2"), "fx_d": rgb("#B4C0C8"),
}
SHINY = dict(NORMAL, **{   # blue-violet hide, gold fins, lavender ice
    "skin": rgb("#5A5290"), "skin_d": rgb("#463E74"), "skin_l": rgb("#7268AA"), "crack": rgb("#2C2650"),
    "belly": rgb("#DCD6E4"), "belly_d": rgb("#B8B0CC"),
    "fin": [rgb("#5A5290"), rgb("#8A6CB0"), rgb("#C08AB0"), rgb("#E8BE62"), rgb("#F0CC58"), rgb("#E6A23E")],
    "ice": rgb("#F2EEF8"), "ice_m": rgb("#D6CCE6"), "ice_d": rgb("#A898C8"), "ice_b": rgb("#5E4C96"),
    "ice_y": rgb("#E8D2A0"), "ice_glow": rgb("#E0C8FF"), "frost": rgb("#CCC6DC"), "eye_glow": rgb("#F4ECFF")})

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
def skin(belly=True, crown=False):
    """teal hide with darker crack lines, pale belly below the belly line, frost in the armoured form"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            x, y, z = w
            under = face == "down" or (belly and y < belly_line(z) + (vnoise(x * .3, 0, z * .3) - .5) * 2.0)
            if under:
                col = mix(pal["belly"], pal["belly_d"], vnoise(x * .25, y * .25, z * .25) * 0.8)
            else:
                n = vnoise(x * .08, y * .08, z * .08) * 0.7 + vnoise(x * .3, y * .3, z * .3) * 0.3
                col = mix(pal["skin_d"], pal["skin_l"], max(0.0, min(1.0, 0.15 + 0.7 * n + 0.010 * (y - 30))))
                cr = vnoise(x * .085 + 7, y * .085, z * .085)
                if abs(cr - 0.5) < 0.012:
                    col = mix(col, pal["crack"], 0.85)
                if pal.get("_frost"):
                    f = vnoise(x * .15 + 11, y * .15, z * .15) + (0.25 if face == "up" else 0) + 0.008 * (y - 30)
                    col = mix(col, pal["frost"], 0.5)
                    if f > 0.55:
                        col = mix(col, pal["ice"], min(1.0, (f - 0.55) * 3))
            px[X, Y] = shade(col, LIGHT[face] * (1 + (_h(X, Y) - .5) * 0.03))
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
                if face != "down" and y > 23.5:
                    col = mix(col, pal["lip"], 0.6)
            px[X, Y] = shade(col, LIGHT[face])
    return {"fn3": fn3, "base": None}

def headpaint():
    """the upper head: hide, a pink lip band along the mouth, the palate dark"""
    sk = skin(belly=False)["fn3"]
    def fn3(px, faces, pal, rnd, c):
        sk(px, faces, pal, rnd, c)
        for face, X, Y, p in c.texels():
            x, y, z = apply(c.world, p)
            if face == "down":
                px[X, Y] = shade(pal["mouth"], LIGHT[face])
            elif face != "up" and y < 27.2:
                px[X, Y] = shade(pal["lip"], LIGHT[face])
    return {"fn3": fn3, "base": None}

def fin(tfun):
    """fins: teal at the root, green, yellow then orange toward the edge (tfun: model point -> 0..1), fine ribs"""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            t = tfun(p, w, c)
            col = ramp(pal["fin"], t)
            if (_h(int(w[2] * 0.7), int(w[1] * 0.25), 5) > 0.82) or int(math.floor(w[2] + w[1] * 0.3)) % 4 == 0:
                col = shade(col, 0.88)
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

def ice():
    """crystalline ice: white with pale blue, dark blue streaks along the spike, a warm tint here and there"""
    def colour(pal, p, w, c, face):
        x, y, z = w
        t = along(p, w, c)
        s = vnoise(x * .35, y * .1 + t * 2, z * .35)
        col = mix(pal["ice_m"], pal["ice"], min(1.0, 0.55 + 0.6 * t + 0.4 * (s - .5)))
        if abs(s - 0.5) < 0.025:
            col = mix(col, pal["ice_b"], 0.8)
        elif abs(s - 0.5) < 0.06:
            col = mix(col, pal["ice_d"], 0.35)
        if face == "down":
            col = mix(col, pal["ice_d"], 0.3)
        if vnoise(x * .12 + 40, y * .12, z * .12) > 0.8:
            col = mix(col, pal["ice_y"], 0.4)
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
            w = apply(c.world, p)
            x, y, z = w
            t = along(p, w, c)
            sv = vnoise(x * .35, y * .1 + t * 2, z * .35)
            d = abs(sv - 0.5)
            if 0.025 <= d < 0.07:                                  # light running along the ice's inner streaks
                g = pal["ice_glow"]
                px[X, Y] = g[:3] + (int(170 - 1800 * (d - 0.025)),)
    return {"fn3": fn3, "base": None, "glow_fn": glow_fn}

def sac():
    """inflated sac: teal back with cracks and stretched stripes, pale belly, painted at full size"""
    def fn3(px, faces, pal, rnd, c):
        cx, cy, cz = BALLOON_C
        for face, X, Y, p in c.texels():
            w = apply(c.world, p)
            x, y, z = (cx + BALLOON_K * (w[0] - cx), cy + BALLOON_K * (w[1] - cy), cz + BALLOON_K * (w[2] - cz))
            hgt = (y - cy) / BALLOON_R[1]
            edge = -0.18 + 0.12 * math.sin(z * 0.15) + 0.06 * math.sin(x * 0.3)
            if hgt > edge:
                n = vnoise(x * .1, y * .1, z * .1)
                col = mix(pal["skin_d"], pal["skin_l"], 0.2 + 0.6 * n)
                if abs(vnoise(x * .07 + 5, y * .07, z * .07) - .5) < 0.02:
                    col = pal["crack"]
            else:
                col = mix(pal["belly"], pal["belly_d"], vnoise(x * .15, y * .15, z * .15))
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
    """a tapering ice spike: 3 segments"""
    w1 = max(1, round(w0 * 0.6)); w2 = 1
    d2 = (d[0], d[1] + 0.15, d[2])
    return chain(p, [d, d, d2], [round(L * .45), round(L * .33), round(L * .25)],
                 [(w0, w0), (w1, w1), (w2, w2)], paint)

def mx(p, s):
    return (p[0] * s, p[1], p[2])

def md(d, s):
    return (d[0] * s, d[1], d[2])

# ---------------------------------------------------------------------------------------------------- model
FX = ("specialfx1",)
SKIN, SKIN_TOP = skin(), skin(belly=False)
LIMB = skin(belly=False)
HEAD, JAW, CLAW = headpaint(), jawpaint(), claw()

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
    m.bone("zamtrios", None, [0, 35, 0])
    # ------------------------------------------------------------------ body (shoulder hump, hips, dorsal fin)
    body = m.bone("body", "zamtrios", [0, 31, -27])
    body.cubes += [sbox(14, 16, 52, -30, -14, SKIN), sbox(16, 17, 58, -14, 2, SKIN), sbox(15, 19, 54, 2, 16, SKIN),
                   sbox(13, 21, 47, 16, 28, SKIN), sbox(9.5, 23, 41, 28, 36, SKIN),
                   sbox(10, 52, 55, -29, -15, SKIN_TOP), sbox(11, 58, 60, -13, 1, SKIN_TOP),
                   sbox(10, 54, 57, 3, 15, SKIN_TOP), sbox(8, 47, 49, 17, 27, SKIN_TOP),
                   sbox(17, 24, 48, -12, 0, SKIN), sbox(16, 24, 46, 4, 14, SKIN)]          # flanks bulging
    body.cubes += dorsal()
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
    for s in (1, -1):
        for z in range(-64, -42, 3):
            hw = 6.0 if z < -61 else (8.0 if z < -52 else 9.5)
            jaw.cubes.append(box(s * hw - 0.5, s * hw + 0.5, 25, 27, z + 1, z + 2, flat("tooth")))
    # ------------------------------------------------------------------ fore limbs (sprawled) with forearm fins
    for s, side in ((1, "left"), (-1, "right")):
        arm = m.bone(f"{side}arm", "body", [14 * s, 31, -14])
        arm.cubes += [box(*sorted((8 * s, 24 * s)), 25, 43, -23, -5, LIMB),
                      seg(mx((18, 34, -14), s), mx((33, 27, -10), s), 14, 13, LIMB)]
        low = m.bone(f"lower{side}arm", f"{side}arm", [32 * s, 29, -9])
        low.cubes += [box(*sorted((26 * s, 38 * s)), 22, 34, -16, -4, LIMB),
                      seg(mx((33, 28, -10), s), mx((37, 7, -17), s), 12, 11, LIMB)]
        for k in range(5):                     # the ribbed forearm fin, fanning up and back
            r = mx((38.5, 27 - 4.5 * k, -6 - 1.6 * k), s)
            dd = md((0.25, 0.55, 0.8), s)
            L = 23 - 3.5 * k
            n = math.sqrt(sum(v * v for v in dd))
            low.cubes.append(seg(r, tuple(a + L * b / n for a, b in zip(r, dd)), 1, 7, fin(along)))
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
        leg.cubes += [box(*sorted((6 * s, 24 * s)), 13, 38, 1, 25, LIMB), box(*sorted((8 * s, 22 * s)), 38, 41, 4, 22, SKIN_TOP)]
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
        cx, cy, cz = BALLOON_C
        rx, ry, rz = (v / BALLOON_K for v in BALLOON_R)
        bal = m.bone("balloon", "body", list(BALLOON_C))
        n = 12
        SAC = sac()
        for k in range(n):
            y0 = cy - ry + 2 * ry * k / n
            y1 = cy - ry + 2 * ry * (k + 1) / n
            fct = math.sqrt(max(0.0, 1 - (((y0 + y1) / 2 - cy) / ry) ** 2))
            a, c = max(1, round(rx * fct)), max(1, round(rz * fct))
            h = max(1, round(y1 - y0))
            for ax, az in ((a, round(c * 0.72)), (round(a * 0.72), c)):
                bal.cubes.append(Cube([cx - ax, round(y0, 2), cz - az], [2 * ax, h, 2 * az], SAC))
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
    for s_ in (1, -1):
        ia.cubes += spike(mx((11, 44, -46), s_), md((0.5, 0.8, 0.6), s_), 20, 6)
        ia.cubes += spike(mx((12, 46, -34), s_), md((0.45, 0.9, 0.75), s_), 24, 7)
    bones.append(ia)
    ba = m.bone("bodyicearmor", "body", [0, 49, -12])
    ba.cubes += [sbox(13, 55, 60, -26, 8, ICE, 0.3), sbox(10, 48, 52, 8, 28, ICE, 0.3)]
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
