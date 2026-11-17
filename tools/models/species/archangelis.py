# -*- coding: utf-8 -*-
"""#1049 Archangelis — dragon archange gardien de la baie (Vol / Fée), légendaire.
A great four-legged dragon of gold, the archangel of the Mont: golden scales, pearl-opal armour plates engraved with
spirals (breastplate, pauldrons, thigh plates, forearm bracers), iridescent quartz crystals growing from its
shoulders, back and brow (crystal horns), a golden spiked crest and cheek fins, a long tail ending in a tuft of
pastel feathers. Two pairs of wings: huge bat wings with golden bones and a nebula membrane (pastel rainbow
strewn with twinkling stars) and, at the shoulders, a smaller pair of feathered angel wings. Golden halos float
above its head, at its wing tips and its tail, and luminous sigils hover around it.
On the ground the great wings are folded along its flanks; in battle they rise, half spread, like the statue of
Saint Michael on the spire. Shiny: platinum with a midnight-blue starry membrane and sapphire crystals."""
import math
from modelgen import Model, Cube, rgb, mix, apply
from biped import Leg
from bovine import vnoise, put, light, side_cols, plane_pattern, finalize, SIDES

SID, DEX = "archangelis", 1049
FRAME_BONES = ("head", "jaw")
HEIGHT_SKIP = ("horn", "halo", "sigil", "crest", "ear")          # 4.75 m to the top of the skull

PAL = {
    "gold": rgb("#D8B456"), "gold_dark": rgb("#9C7A2E"), "gold_light": rgb("#F6E0A0"), "gold_edge": rgb("#6E5420"),
    "opal": rgb("#F2EEF6"), "opal_shade": rgb("#C6BEDA"), "opal_pink": rgb("#F7CDE4"), "opal_cyan": rgb("#C9EEF6"),
    "opal_lilac": rgb("#D9CCF6"), "opal_rim": rgb("#C49E46"), "opal_line": rgb("#B0A2D2"),
    "neb_pink": rgb("#F4B4D6"), "neb_lilac": rgb("#C6B2F2"), "neb_blue": rgb("#A0C6F4"), "neb_cyan": rgb("#A8EEEA"),
    "neb_mint": rgb("#C2F2C6"), "neb_peach": rgb("#FADCAE"), "star": rgb("#FFFFFF"), "star_gold": rgb("#FFF0A8"),
    "crystal_base": rgb("#A08AE6"), "crystal_mid": rgb("#C8BAF6"), "crystal_tip": rgb("#E2F6FF"), "crystal_pink": rgb("#F2B2DC"),
    "crystal_hi": rgb("#FFFFFF"), "crystal_dark": rgb("#7462B8"),
    "feather_a": rgb("#F8E6F2"), "feather_b": rgb("#DCEAFA"), "feather_c": rgb("#E6F6E2"), "feather_d": rgb("#EEE2FA"),
    "feather_edge": rgb("#A88CD2"), "feather_shaft": rgb("#E2C270"),
    "eye_gold": rgb("#FFD24A"), "eye_slit": rgb("#3A2406"), "eye_dark": rgb("#6E4A10"), "eye_shine": rgb("#FFFFFF"),
    "halo": rgb("#FFE07A"), "halo_core": rgb("#FFF8D8"),
    "claw": rgb("#F4E6BC"), "claw_tip": rgb("#B8964A"), "mouth": rgb("#7A2E36"), "tooth": rgb("#FFFFF0"),
    "tongue": rgb("#D27A8C"),
    "nostril": rgb("#5A4214"),
}
SHINY = dict(PAL, **{
    "gold": rgb("#C9CED9"), "gold_dark": rgb("#7C8296"), "gold_light": rgb("#F4F6FA"), "gold_edge": rgb("#4A5064"),
    "opal": rgb("#EAF0FA"), "opal_shade": rgb("#AEB8D6"), "opal_pink": rgb("#D6D8F6"), "opal_cyan": rgb("#C6E4FA"),
    "opal_lilac": rgb("#C8C6F2"), "opal_rim": rgb("#D9B860"), "opal_line": rgb("#8E9ACC"),
    "neb_pink": rgb("#5A2A78"), "neb_lilac": rgb("#3E2C86"), "neb_blue": rgb("#1E3A86"), "neb_cyan": rgb("#24668E"),
    "neb_mint": rgb("#2A2A64"), "neb_peach": rgb("#6E3A8A"), "star": rgb("#FFFFFF"), "star_gold": rgb("#FFE8A0"),
    "crystal_base": rgb("#3E5ED0"), "crystal_mid": rgb("#6E9CF0"), "crystal_tip": rgb("#CFF0FF"), "crystal_pink": rgb("#8AB4FF"),
    "crystal_dark": rgb("#24388E"),
    "feather_a": rgb("#E6ECFA"), "feather_b": rgb("#C8D8F6"), "feather_c": rgb("#D6E2F6"), "feather_d": rgb("#D0CCF4"),
    "feather_edge": rgb("#7A86C2"), "feather_shaft": rgb("#E0C470"),
    "claw": rgb("#EEF2FA"), "claw_tip": rgb("#7C8296"),
})
G = {"glow": True, "shading": False}

# ============================================================================ painters
def scales(base="gold", dark="gold_dark", light_key="gold_light", belly=None, belly_faces=("down",), seed=3):
    """Golden scales (fn3): staggered rows of small scales (darker lower rim), lighter on top faces; `belly`:
    pearl ventral plates on the given faces (horizontal bands)."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.14)
            if belly and face in belly_faces:          # pearly ventral plates with an iridescent sheen
                band = (p[2] if face in ("up", "down") else p[1]) % 2.0
                n1 = vnoise(p[0] * 0.25 + 3, p[1] * 0.25, p[2] * 0.25, seed + 7)
                tint = "opal_pink" if n1 > 0.6 else ("opal_cyan" if n1 < 0.38 else "opal_lilac")
                col = mix(pal[belly], pal[tint], 0.55)
                if band < 0.55:
                    col = mix(col, pal["opal_line"], 0.55)
                put(px, X, Y, col, f * 0.97, rnd, 2)
                continue
            h = p[0] if face in ("north", "south", "up", "down") else p[2]
            v = p[1] if face not in ("up", "down") else p[2]
            row = math.floor(v / 1.5)
            u = h / 2.0 + 0.5 * (row % 2)
            fu, fv = u - math.floor(u), v / 1.5 - row
            col = pal[base]
            if fv < 0.34 or (fv < 0.6 and (fu < 0.18 or fu > 0.82)):
                col = mix(pal[base], pal[dark], 0.55)          # scale rims
            elif fv > 0.75 and 0.3 < fu < 0.7:
                col = mix(pal[base], pal[light_key], 0.45)     # glint on each scale
            if face == "up":
                col = mix(col, pal[light_key], 0.2)
            n = vnoise(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3, seed)
            if n > 0.72:
                col = mix(col, pal[light_key], 0.25)
            put(px, X, Y, col, f, rnd, 3)
    return {"fn3": fn3}

def opal(spiral=False, rim=True, seed=5, rim_faces=("north", "south", "east", "west")):
    """Pearl-opal armour plate (fn3): milky white with drifting iridescent tints (pink / cyan / lilac), a golden
    rim and, on the larger faces, an engraved spiral."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            i, j = X - fx, Y - fy
            n1 = vnoise(p[0] * 0.22 + 3, p[1] * 0.22, p[2] * 0.22, seed)
            n2 = vnoise(p[0] * 0.3, p[1] * 0.3 + 7, p[2] * 0.3, seed + 1)
            tint = "opal_pink" if n1 > 0.58 else ("opal_cyan" if n2 > 0.58 else "opal_lilac")
            col = mix(pal["opal"], pal[tint], 0.35 + 0.3 * abs(n1 - n2))
            f = light(face, j, fh, 0.1)
            if rim and face in rim_faces and fw >= 3 and fh >= 3 and (i in (0, fw - 1) or j in (0, fh - 1)):
                put(px, X, Y, pal["opal_rim"], f, rnd, 3)
                continue
            if spiral and fw >= 5 and fh >= 5 and face not in ("up", "down"):
                cx, cy = (fw - 1) / 2, (fh - 1) / 2
                dx, dy = i - cx, cy - j
                r = math.hypot(dx, dy)
                rmax = min(fw, fh) / 2 - 1.0
                if r < rmax:
                    th = math.atan2(dy, dx) % (2 * math.pi)
                    ph = r / 1.9 - th / (2 * math.pi)
                    if min(ph % 1.0, 1 - ph % 1.0) < 0.17 or r < 0.7:
                        col = mix(col, pal["opal_line"], 0.75)
            put(px, X, Y, col, f, rnd, 2)
    return {"fn3": fn3}

def crystal(seed=1):
    """Iridescent quartz prism (per face): lilac base deepening to a clear pale tip, one bright facet edge and one
    shaded one, faint pink / cyan internal colour."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                t = 1 - j / max(h - 1, 1)                          # 1 at the top
                for i in range(w):
                    col = mix(pal["crystal_base"], pal["crystal_tip"], t ** 1.7)
                    if (i + j + seed) % 5 == 0:
                        col = mix(col, pal["crystal_pink"], 0.5)
                    if fc in ("up",):
                        col = pal["crystal_tip"]
                    elif i == 0 and fc in ("north", "west"):
                        col = mix(col, pal["crystal_hi"], 0.7)
                    elif i == w - 1 and fc in ("south", "east"):
                        col = mix(col, pal["crystal_dark"], 0.5)
                    px[x + i, y + j] = col
    return fn

def membrane(inside, *, rim_key="gold_edge", seed=9):
    """Nebula wing membrane on a horizontal plane (fn3): `inside(x, z)` (rest model coordinates, x >= 0 on the
    left wing) says where the skin is (else transparent). Pastel rainbow drifting like a nebula, light rays
    fanning from the wrist, a fine golden rim and twinkling stars (re-rolled on every emissive frame)."""
    ramp = ("neb_pink", "neb_lilac", "neb_blue", "neb_cyan", "neb_mint", "neb_peach", "neb_pink")
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            if face not in ("up", "down"):
                px[X, Y] = (0, 0, 0, 0)
                continue
            x, z = abs(pl[0]), pl[2]
            if not inside(x, z):
                px[X, Y] = (0, 0, 0, 0)
                continue
            if not all(inside(x + ox, z + oz) for ox, oz in ((0.9, 0), (-0.9, 0), (0, 0.9), (0, -0.9))):
                put(px, X, Y, pal[rim_key], 1.0, rnd, 3)
                continue
            n = vnoise(x * 0.09, 1.0, z * 0.09, seed) * 0.7 + vnoise(x * 0.25, 2.0, z * 0.25, seed + 3) * 0.3
            ray = math.sin(math.atan2(z + 9, x - 34) * 9 + x * 0.05)
            v = (n * 1.6 + 0.12 * ray + x * 0.012) % 1.0 * (len(ramp) - 1)
            k = int(v)
            col = mix(pal[ramp[k]], pal[ramp[k + 1]], v - k)
            if ray > 0.85:
                col = mix(col, pal["star"], 0.18)
            if face == "down":
                col = mix(col, pal["neb_lilac"], 0.15)
            r = rnd.random()
            if r < 0.03:
                col = pal["star"]
            elif r < 0.045:
                col = pal["star_gold"]
            put(px, X, Y, col, 1.0, rnd, 2)
    return {"fn3": fn3, **G}

def feather_fan(n=5, root=(0.0, 1.0), spread=(0.15, 0.95), length=1.0, used=("east", "west"), seed=2):
    """Fan of pastel feathers on a plane (per face, in face-local 0..1 coordinates): feathers radiate from `root`
    (u, v; v=1 is the top) between angles spread (fractions of a quarter turn, from 'back' to 'down'), each with
    a golden shaft, iridescent vane and a soft rounded tip; transparent between the tips."""
    keys = ("feather_a", "feather_b", "feather_c", "feather_d")
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            if fc not in used:
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            cols = side_cols(fc, w) if fc in ("east", "west") else list(range(w))
            for j in range(h):
                for k in range(w):
                    u, vv = (k + 0.5) / w, 1 - (j + 0.5) / h
                    du, dv = u - root[0], root[1] - vv
                    r = math.hypot(du * w, dv * h) / max(w, h)
                    a = math.atan2(dv, du) / (math.pi / 2)          # 0 = back (along +u), 1 = straight down
                    best = None
                    for f in range(n):
                        af = spread[0] + (spread[1] - spread[0]) * f / max(n - 1, 1)
                        L = length * (0.75 + 0.25 * math.sin(math.pi * (f + 0.5) / n))
                        d = abs(a - af)
                        if best is None or d < best[0]:
                            best = (d, f, L, af)
                    d, f, L, af = best
                    width = 0.5 * (spread[1] - spread[0]) / max(n - 1, 1) + 0.02
                    tip = L * (1 - 0.35 * (d / width) ** 2)
                    if r > tip or d > width * 1.05 or r < 0.02:
                        px[x + cols[k], y + j] = (0, 0, 0, 0)
                        continue
                    col = pal[keys[(f + seed) % len(keys)]]
                    if d < width * 0.18:
                        col = pal["feather_shaft"]
                    elif d > width * 0.8 or r > tip - 0.06:
                        col = mix(col, pal["feather_edge"], 0.5)
                    put(px, x + cols[k], y + j, col, 1.0, rnd, 2)
    return fn

def plumes(root, angles, lengths, width=2.2, used=("east", "west"), keys_seed=0):
    """Overlapping lanceolate feathers on a plane, in texel units of the face: side faces (u from the front, v up),
    angles from 'back' toward 'down'; horizontal faces (u from -X, v toward the back), angles from 'back' toward
    +X. Each feather: golden shaft, pastel vane, lilac edge; transparent around them."""
    keys = ("feather_a", "feather_b", "feather_c", "feather_d")
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            if fc not in used:
                for j in range(h):
                    for i in range(w):
                        px[x + i, y + j] = (0, 0, 0, 0)
                continue
            horiz = fc in ("up", "down")
            cols = list(range(w)) if horiz else side_cols(fc, w)
            for j in range(h):
                for k in range(w):
                    u, v = k + 0.5, h - (j + 0.5)
                    hit = None
                    for f, (a, L) in enumerate(zip(angles, lengths)):
                        r = math.radians(a)
                        d = (math.sin(r), math.cos(r)) if horiz else (math.cos(r), -math.sin(r))
                        du, dv = u - root[0], v - root[1]
                        t = du * d[0] + dv * d[1]
                        e = abs(du * d[1] - dv * d[0])
                        if 0 < t < L:
                            wd = width * math.sin(math.pi * min(1.0, t / L * 0.92 + 0.08)) ** 0.6
                            if e < wd:
                                hit = (f, e, wd, t, L)               # later feathers lie on top
                    if hit is None:
                        px[x + cols[k], y + j] = (0, 0, 0, 0)
                        continue
                    f, e, wd, t, L = hit
                    col = pal[keys[(f + keys_seed) % len(keys)]]
                    if e < 0.45 and t < L * 0.85:
                        col = pal["feather_shaft"]
                    elif e > wd - 0.75:
                        col = mix(col, pal["feather_edge"], 0.65)
                    put(px, x + cols[k], y + j, col, 1.0, rnd, 2)
    return fn

def ring(r_out=None, width=1.0):
    """Halo: a glowing golden ring on a plane (both faces), transparent inside and out."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            R = r_out if r_out else min(w, h) / 2 - 0.3
            for j in range(h):
                for i in range(w):
                    d = math.hypot(i + 0.5 - w / 2, j + 0.5 - h / 2)
                    if R - width <= d <= R:
                        px[x + i, y + j] = pal["halo_core"] if (i + j) % 4 == 0 else pal["halo"]
                    else:
                        px[x + i, y + j] = (0, 0, 0, 0)
    return fn

SIGIL = ["...H...",
         "..HOH..",
         ".HO.OH.",
         "HO.C.OH",
         ".HO.OH.",
         "..HOH..",
         "...H..."]
SIGIL2 = ["...H...",
          ".HOOOH.",
          ".O...O.",
          "HO.C.OH",
          ".O...O.",
          ".HOOOH.",
          "...H..."]

def glyph(rows):
    def fn(px, faces, pal, rnd):
        keys = {"H": "halo", "O": "halo", "C": "halo_core"}
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            for j in range(h):
                for i in range(w):
                    ch = rows[min(j, len(rows) - 1)][min(i, len(rows[0]) - 1)]
                    ring_ = math.hypot(i - (w - 1) / 2, j - (h - 1) / 2)
                    if ch == "." :
                        px[x + i, y + j] = (0, 0, 0, 0)
                    else:
                        px[x + i, y + j] = pal[keys[ch]] if ring_ > 0.6 else pal["halo_core"]
    return fn

def solid(key, noise=3):
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    put(px, x + i, y + j, pal[key], 1.0 if fc == "up" else 0.9, rnd, noise)
    return fn

def claw(px, faces, pal, rnd):
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                put(px, x + i, y + j, pal["claw_tip"] if (fc == "north" or (fc in ("east", "west") and i == (0 if fc == "west" else w - 1))) else pal["claw"], 1.0, rnd, 2)

def eye_plane(rows):
    """Dragon eye on a side plane, columns counted from the front: gold iris, slit pupil, dark front corner."""
    keys = {"G": "eye_gold", "K": "eye_slit", "D": "eye_dark", "S": "eye_shine"}
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            if not (w and h):
                continue
            cols = side_cols(fc, w) if fc in ("east", "west") else list(range(w))
            for j in range(h):
                for k in range(w):
                    ch = rows[min(j, len(rows) - 1)][min(k, len(rows[0]) - 1)]
                    px[x + cols[k], y + j] = (0, 0, 0, 0) if (ch == "." or fc not in ("east", "west")) else pal[keys[ch]]
    return fn

from vessel import with_faces
GOLD = scales()
GOLD2 = scales(seed=4)
BELLYG = scales(belly="opal", belly_faces=("down",))
NECKG = scales(belly="opal", belly_faces=("north", "down"))
OPAL = opal()
OPALS = opal(spiral=True)
OPALP = opal(rim=False)
CRYS = {"fn": crystal()}
CLAW = {"fn": claw}
TOOTH = {"base": "tooth", "noise": 2}
SKULL = with_faces(scales(), {"down": "mouth"})
MUZZLE = with_faces(scales(seed=4), {"down": "mouth"})

# ============================================================================ wings (shapes in rest coordinates, |x|)
WRIST = (35.0, -8.0)
FINGERS = ((4, 32), (27, 29), (52, 25), (79, 19))            # (angle from outward toward the back, length)

def _tip(k):
    a, L = FINGERS[k]
    return WRIST[0] + L * math.cos(math.radians(a)), WRIST[1] + L * math.sin(math.radians(a))

def outer_skin(x, z):
    """Hand membrane: between the fingers, scalloped trailing edge."""
    dx, dz = x - WRIST[0], z - WRIST[1]
    r = math.hypot(dx, dz)
    a = math.degrees(math.atan2(dz, dx))
    if not (FINGERS[0][0] - 1 <= a <= FINGERS[-1][0] + 1) or r < 0.5:
        return False
    for (a0, L0), (a1, L1) in zip(FINGERS, FINGERS[1:]):
        if a0 - 1 <= a <= a1 + 1:
            t = min(1, max(0, (a - a0) / (a1 - a0)))
            return r < (L0 + (L1 - L0) * t) * (1 - 0.3 * math.sin(math.pi * t)) + 0.4
    return False

def inner_skin(x, z):
    """Arm membrane: from the leading edge back to a scalloped trailing edge running from the flank (z 15) to the
    last finger tip."""
    if x < 7 or x > WRIST[0] + 4.0 or z < -8.5:
        return False
    tx, tz = _tip(3)
    t = min(1, max(0, (x - 7) / (tx - 7)))
    te = 18.5 + (tz - 18.5) * t - 6.0 * math.sin(math.pi * t)
    return z < te

FOLD_WRIST = (3.0, 46.0)                                     # (z, y) of the folded wrist above the back
FOLD_FINGERS = ((35, 33), (44, 32), (57, 27), (77, 22))     # (angle below the horizontal, length)

def _ftip(a, L):
    return FOLD_WRIST[0] + L * math.cos(math.radians(a)), FOLD_WRIST[1] - L * math.sin(math.radians(a))

def folded_skin(z, y):
    """Folded wing on the flank (vertical plane): the skin draped like a cloak under the arm (shoulder -> wrist
    above the back) and the folded fingers, scalloped between the finger tips."""
    z1, y1 = _ftip(*FOLD_FINGERS[0])
    if z < -8.5 or z > z1 + 0.3:
        return False
    wz, wy = FOLD_WRIST
    top = 33 + (wy - 33) * (z + 8) / (wz + 8) if z < wz else wy - (wy - y1) * (z - wz) / (z1 - wz)
    pts = [(-8.5, 28.5)] + [_ftip(a, L) for a, L in reversed(FOLD_FINGERS)]
    bottom = pts[-1][1]
    for k, ((za, ya), (zb, yb)) in enumerate(zip(pts, pts[1:])):
        if za <= z <= zb:
            t = (z - za) / max(zb - za, 1e-6)
            bottom = ya + (yb - ya) * t + (2.2 * math.sin(math.pi * t) if k else 0)
            break
    return bottom < y < top

def folded_paint(seed=11):
    """membrane() for the vertical folded panel (faces east/west), same nebula, in (z, y)."""
    ramp = ("neb_pink", "neb_lilac", "neb_blue", "neb_cyan", "neb_mint", "neb_peach", "neb_pink")
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            if face not in ("east", "west"):
                px[X, Y] = (0, 0, 0, 0)
                continue
            z, y = pl[2], pl[1]
            if not folded_skin(z, y):
                px[X, Y] = (0, 0, 0, 0)
                continue
            if not all(folded_skin(z + oz, y + oy) for oz, oy in ((0.9, 0), (-0.9, 0), (0, 0.9), (0, -0.9))):
                put(px, X, Y, pal["gold_edge"], 1.0, rnd, 3)
                continue
            n = vnoise(z * 0.1, y * 0.1, 1.0, seed) * 0.7 + vnoise(z * 0.25, y * 0.25, 3.0, seed + 2) * 0.3
            v = (n * 1.6 + z * 0.01) % 1.0 * (len(ramp) - 1)
            k = int(v)
            col = mix(pal[ramp[k]], pal[ramp[k + 1]], v - k)
            r = rnd.random()
            if r < 0.03:
                col = pal["star"]
            elif r < 0.045:
                col = pal["star_gold"]
            put(px, X, Y, col, 1.0, rnd, 2)
    return {"fn3": fn3, **G}

# ============================================================================ legs
LEGP_F = {"thigh": GOLD, "shin": GOLD2, "meta": GOLD, "foot": GOLD2, "claw": CLAW}
LEGP_B = {"thigh": GOLD, "shin": GOLD2, "meta": GOLD, "foot": GOLD2, "claw": CLAW}
LEGS = []
for _side, _sx in SIDES:
    LEGS.append(Leg(f"front_{_side}", 6.5 * _sx, -11, (9, 9, 4), (18, -12, -35), 2, thigh=(5, 6, 5), shin=(4, 5),
                    meta=(4, 3), foot=(5, 5, 1), claws=(-1.6, 0, 1.6), paints=LEGP_F, claw_len=3, dewclaw=False, bend=-1))
for _side, _sx in SIDES:
    LEGS.append(Leg(f"back_{_side}", 6.5 * _sx, 12, (10, 9, 6), (-38, 40, -15), 2, thigh=(6, 8, 6), shin=(4, 5),
                    meta=(3, 3), foot=(5, 6, 2), claws=(-1.6, 0, 1.6), paints=LEGP_B, claw_len=3, dewclaw=True, bend=1))
PIVOT = (0, 22.6, 0)
SEAT = (0, 32, -2.5)                  # rider on the back, between the wing roots
EYE_ROWS = [".DDDD", "DGKGS", ".DGGD"]

def build():
    m = Model(SID, DEX, (512, 512))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
    for lg in LEGS:                                          # opal armour on the legs
        s = 1 if lg.x > 0 else -1
        x, H, z = lg.x, lg.H, lg.hip_z
        L1, L2, _ = lg.L
        if lg.side.startswith("back"):                       # spiral plate on the outer haunch
            px_ = x + 3 if s > 0 else x - 4
            m.get(lg.bones[0]).cubes.append(Cube([px_, H - 8, z - 3], [1, 8, 7], OPALS))
        else:                                                # bracer on the forearm, plate on the shoulder blade
            m.get(lg.bones[1]).cubes.append(Cube([x - 2.5, H - L1 - 7, z - 3], [5, 5, 6], OPAL))
    m.bone("torso", "body", [0, 24, 0], cubes=[
        Cube([-7, 18, -10], [14, 13, 23], BELLYG),
        Cube([-7.5, 18.5, 6], [15, 11, 11], BELLYG),                                # haunches
        Cube([-5.5, 31, -9], [11, 1, 22], GOLD), Cube([-6, 17, -8], [12, 1, 20], BELLYG)])
    m.bone("chest", "torso", [0, 25, -9], cubes=[
        Cube([-8, 18, -19], [16, 14, 10], BELLYG),
        Cube([-7, 32, -18], [14, 1, 9], GOLD), Cube([-7, 17, -18], [14, 1, 8], BELLYG),
        # shield-shaped pearl breastplate with a spiral medallion
        Cube([-6.5, 24, -20], [13, 8, 1], OPALP), Cube([-5, 21, -20], [10, 3, 1], OPALP), Cube([-3.5, 19, -20], [7, 2, 1], OPALP),
        Cube([-3.5, 23, -20.6], [7, 7, 1], OPALS)])
    for side, s in SIDES:
        X = lambda x0, w: x0 if s > 0 else -x0 - w
        m.bone(f"pauldron_{side}", "chest", [8 * s, 27, -13], cubes=[
            Cube([X(7.5, 2), 22.5, -16.5], [2, 8, 8], OPALS), Cube([X(7.5, 2), 21.5, -15.5], [2, 10, 6], OPALP),
            Cube([X(7.5, 2), 23.5, -17.5], [2, 6, 10], OPALP)])
        # lower pair: feathered angel wings behind the shoulders, half open, drooping back
        ang = tuple(s * a for a in (12, 26, 40, 54, 68, 82))
        m.bone(f"pinion_{side}", "chest", [9.5 * s, 25, -11], rotation=[-10, -s * 30, s * 28], cubes=[
            Cube([X(9, 7), 24, -12], [7, 2, 2], GOLD2),
            Cube([X(9.5, 17), 25, -12], [17, 0, 17], {"fn": plumes((0.8, 0.8) if s > 0 else (16.2, 0.8), ang,
                                                                     (10, 12, 13.5, 15, 16, 15.5), width=1.9,
                                                                     used=("up", "down"), keys_seed=0 if s > 0 else 2)})])
        # crystal clusters on the shoulders
        cx = 5 * s
        m.bone(f"crystal_{side}", "chest", [cx, 31, -14], cubes=[
            Cube([X(4, 2), 31, -15], [2, 9, 2], CRYS, rotation=[-25, 0, 18 * s], pivot=[cx, 31, -14]),
            Cube([X(5.5, 2), 31, -13], [2, 7, 2], CRYS, rotation=[-45, 0, 38 * s], pivot=[cx, 31, -14]),
            Cube([X(3, 1), 31, -12], [1, 5, 1], CRYS, rotation=[-10, 0, 6 * s], pivot=[cx, 31, -14]),
            Cube([X(6, 1), 31, -16], [1, 4, 1], CRYS, rotation=[-5, 0, 55 * s], pivot=[cx, 31, -14])])
    m.bone("crystal_back", "torso", [0, 31.5, 9], cubes=[                       # on the rump, behind the rider
        Cube([-1, 31, 8], [2, 6, 2], CRYS, rotation=[-30, 0, 0], pivot=[0, 31.5, 9]),
        Cube([-0.5, 31, 12], [1, 4, 1], CRYS, rotation=[-40, 0, 0], pivot=[0, 31.5, 13]),
        Cube([-0.5, 31, 5.5], [1, 4, 1], CRYS, rotation=[-20, 0, 0], pivot=[0, 31.5, 6])])
    m.bone("locator_seat_1", "torso", list(SEAT), locators={"seat_1": list(SEAT)})

    # ---------------------------------------------------------------- neck and head
    m.bone("neck", "chest", [0, 31, -15], rotation=[16, 0, 0], cubes=[
        Cube([-4.5, 30, -19], [9, 10, 8], NECKG),
        Cube([-0.5, 34, -11.5], [1, 2, 2], GOLD2), Cube([-0.5, 37.5, -11.5], [1, 2, 2], GOLD2)])       # dorsal spikes
    m.bone("neck2", "neck", [0, 39.5, -15], rotation=[-12, 0, 0], cubes=[
        Cube([-4, 39, -18.5], [8, 9, 7], NECKG),
        Cube([-0.5, 41, -12], [1, 2, 2], GOLD2), Cube([-0.5, 44.5, -12], [1, 2, 2], GOLD2)])
    m.bone("neck3", "neck2", [0, 47.5, -15], rotation=[-14, 0, 0], cubes=[
        Cube([-3.5, 47, -18], [7, 8, 6], NECKG),
        Cube([-0.5, 49, -12.5], [1, 2, 2], GOLD2), Cube([-0.5, 52, -12.5], [1, 2, 2], GOLD2)])
    m.bone("head", "neck3", [0, 54.5, -15], rotation=[12, 0, 0], cubes=[
        Cube([-5, 53, -24], [10, 8, 10], SKULL),                                   # skull
        Cube([-4, 61, -22], [8, 1, 7], GOLD),
        Cube([-4, 57, -26], [8, 3, 2], GOLD), Cube([-3.5, 58, -28], [7, 1, 2], GOLD),       # forehead sloping to the snout
        Cube([-3.5, 53, -33], [7, 4, 9], MUZZLE),                                  # upper jaw
        Cube([-3, 57, -32], [6, 1, 6], GOLD),                                      # nasal ridge
        Cube([-3, 53, -35], [6, 3, 2], MUZZLE), Cube([-2.5, 56, -35], [5, 1, 3], GOLD),     # nose
        Cube([-2.5, 54.5, -35.04], [1, 1, 0], {"base": "nostril"}), Cube([1.5, 54.5, -35.04], [1, 1, 0], {"base": "nostril"}),
        Cube([-1, 58, -31], [2, 1, 3], GOLD2), Cube([-0.5, 59, -30], [1, 1, 1], GOLD2),      # little nasal horn
        Cube([-2, 51, -34.5], [1, 2, 1], TOOTH), Cube([1, 51, -34.5], [1, 2, 1], TOOTH)] +  # fangs
        [Cube([2.4 * sx - (1 if sx < 0 else 0), 52, z], [1, 1, 1], TOOTH) for sx in (1, -1) for z in (-32, -29.5, -27, -24.5)])
    m.bone("jaw", "head", [0, 53, -17], cubes=[
        Cube([-2.5, 50, -33], [5, 3, 16], with_faces(NECKG, {"up": "mouth"})),
        Cube([-3.5, 50, -21], [7, 3, 5], with_faces(NECKG, {"up": "mouth"})),            # jaw muscles
        Cube([-2, 50.5, -35], [4, 2, 2], NECKG),                                   # chin
        Cube([-1.5, 52.6, -31], [3, 1, 12], {"base": "tongue"}),
        Cube([-0.5, 48.5, -28], [1, 2, 1], GOLD2), Cube([-2, 48, -24], [1, 2, 1], GOLD2), Cube([1, 48, -24], [1, 2, 1], GOLD2),
        Cube([-3, 48.5, -20], [1, 2, 1], GOLD2), Cube([2, 48.5, -20], [1, 2, 1], GOLD2)] +       # chin spikes
        [Cube([1.6 * sx - (1 if sx < 0 else 0), 53, z], [1, 1, 1], TOOTH) for sx in (1, -1) for z in (-31, -28, -25)])
    for side, s in SIDES:
        X = lambda x0, w: x0 if s > 0 else -x0 - w
        xe = 5.03 * s
        m.bone(f"eye_{side}", "head", [xe, 57.5, -21.5], cubes=[
            Cube([xe, 56, -24], [0, 3, 5], {"fn": eye_plane(EYE_ROWS), **G})])
        m.bone(f"brow_{side}", "head", [3.5 * s, 60, -19], rotation=[10, 0, 0], cubes=[
            Cube([X(2.5, 3), 59.5, -25], [3, 1, 6], GOLD2), Cube([X(4, 1), 60, -20], [1, 2, 1], GOLD2)])
        m.bone(f"cheek_{side}", "head", [5 * s, 56, -16], cubes=[Cube([X(5, 1), 53.5, -19], [1, 5, 5], GOLD2)])
        m.bone(f"ear_{side}", "head", [5.5 * s, 56, -16], rotation=[0, 22 * s, 0], cubes=[      # golden cheek fins
            Cube([X(5.5, 1), 54, -17], [1, 4, 8], GOLD2), Cube([X(5.5, 1), 58, -15], [1, 2, 1], GOLD2),
            Cube([X(5.5, 1), 57.5, -12], [1, 3, 1], GOLD2), Cube([X(5.5, 1), 56.5, -10], [1, 2, 1], GOLD2)])
        m.bone(f"horn_{side}", "head", [2.5 * s, 61, -18], rotation=[-38, 0, 14 * s], cubes=[    # crystal horns
            Cube([X(1.5, 2), 61, -19], [2, 11, 2], CRYS)])
        m.bone(f"horn2_{side}", "head", [4 * s, 60.5, -16], rotation=[-55, 0, 32 * s], cubes=[
            Cube([X(3.5, 1), 60.5, -16.5], [1, 7, 1], CRYS)])
    m.bone("crest", "head", [0, 61, -15], rotation=[-20, 0, 0], cubes=[                    # golden mane spikes
        Cube([-0.5, 61, -17], [1, 4, 2], GOLD2), Cube([-0.5, 60.5, -14], [1, 3, 2], GOLD2),
        Cube([-2.5, 60.5, -15.5], [1, 3, 2], GOLD2), Cube([1.5, 60.5, -15.5], [1, 3, 2], GOLD2),
        Cube([-3.5, 59.5, -14], [1, 2, 2], GOLD2), Cube([2.5, 59.5, -14], [1, 2, 2], GOLD2)])
    m.bone("halo", "head", [0, 68, -18], rotation=[-30, 0, 0], cubes=[Cube([-6, 68, -24], [12, 0, 12], {"fn": ring(), **G})])

    # ---------------------------------------------------------------- tail with a tuft of feathers
    tail = (("tail", "torso", 26, 16, 8, 7, 8, -24, 0), ("tail2", "tail", 25.5, 24, 6, 5, 8, -10, 14),
            ("tail3", "tail2", 25.5, 32, 5, 4, 8, 6, 18), ("tail4", "tail3", 25.5, 40, 4, 3, 8, 12, 8),
            ("tail5", "tail4", 25.5, 48, 3, 3, 7, 14, -16))
    for name, par, py, pz, w, h, L, rx, ry in tail:
        cubes = [Cube([-w / 2, py - h / 2, pz], [w, h, L], BELLYG)]
        cubes.append(Cube([-0.5, py + h / 2 - 0.5, pz + 2], [1, 2, 2], GOLD2))          # dorsal spikes
        if w >= 6:
            cubes.append(Cube([-0.5, py + h / 2 - 0.5, pz + 6], [1, 2, 2], GOLD2))
        m.bone(name, par, [0, py, pz], rotation=[rx, ry, 0], cubes=cubes)
    m.bone("tail6", "tail5", [0, 25.5, 55], rotation=[16, -18, 0], cubes=[
        Cube([-1, 24.5, 55], [2, 2, 4], GOLD),
        Cube([0, 19, 56], [0, 13, 13], {"fn": plumes((0.5, 6.5), (-38, -18, 0, 18, 38), (9, 11, 12.5, 11, 9), width=2.0)}),
        Cube([-6.5, 25.5, 56], [13, 0, 13], {"fn": plumes((6.5, 0.5), (-36, -14, 8, 30), (9, 12, 12, 9), width=2.0,
                                                           used=("up", "down"), keys_seed=1)})])
    m.bone("halo_tail", "tail6", [0, 31, 64], rotation=[-10, 0, 12], cubes=[Cube([-3.5, 31, 60.5], [7, 0, 7], {"fn": ring(), **G})])

    # ---------------------------------------------------------------- the great wings
    for side, s in SIDES:
        X = lambda x0, w: x0 if s > 0 else -x0 - w
        # folded along the flank: arm up to the wrist above the back, fingers back down to the hip, draped skin
        wz, wy = FOLD_WRIST
        m.bone(f"wing_closed_{side}", "torso", [7 * s, 32, -8], cubes=[
            Cube([X(7, 2), 32, -8], [2, 2, 17], GOLD, rotation=[51, 0, 0], pivot=[7 * s, 33, -8]),
            Cube([X(8, 2), wy - 1, wz - 1], [2, 2, 2], GOLD2), Cube([X(8.5, 1), wy + 1, wz - 1.5], [1, 2, 1], CLAW)] + [
            Cube([X(9, 1), wy - 0.5, wz], [1, 1, L], GOLD2, rotation=[-a, 0, 0], pivot=[9 * s, wy, wz]) for a, L in FOLD_FINGERS] + [
            Cube([10 * s, 21, -9], [0, 27, 40], folded_paint(seed=11 if s > 0 else 12))])
        # spread: arm along the leading edge with the inner skin, hand with four fingers and the outer skin
        m.bone(f"wing_open_{side}", "torso", [7 * s, 32, -8], cubes=[
            Cube([X(6, 29), 30.5, -9.5], [29, 3, 3], GOLD),
            Cube([X(7, 32), 31.5, -8.5], [32, 0, 28], membrane(inner_skin, seed=9 if s > 0 else 10))])
        fingers = [Cube([X(35, 1), 31, -8.5], [1, 1, 1], GOLD2)]
        for a, L in FINGERS:
            fingers.append(Cube([X(35, L), 31, -8.5], [L, 1, 1], GOLD2, rotation=[0, -s * a, 0], pivot=[35 * s, 31.5, -8]))
        m.bone(f"wing_open_{side}2", f"wing_open_{side}", [35 * s, 32, -8], cubes=[
            Cube([X(34, 3), 30, -9.5], [3, 3, 3], GOLD2), Cube([X(34.5, 1), 33, -10.5], [1, 3, 1], CLAW)] + fingers + [
            Cube([X(35, 33), 31.5, -9], [33, 0, 22], membrane(outer_skin, seed=13 if s > 0 else 14))])
        tx, tz = _tip(0)
        m.bone(f"wing_open_{side}_halo", f"wing_open_{side}2", [tx * s, 35, tz], rotation=[10, 0, -20 * s], cubes=[
            Cube([tx * s - 3, 35, tz - 3], [6, 0, 6], {"fn": ring(), **G})])
    # ---------------------------------------------------------------- sigils floating around
    for k, (x, y, z, rows) in enumerate(((19, 16, -25, SIGIL), (-21, 22, -18, SIGIL2), (17, 22, 28, SIGIL2), (-18, 13, 24, SIGIL))):
        g = {"fn": glyph(rows), **G}
        m.bone(f"sigil{k + 1}", SID, [x, y, z], cubes=[Cube([x - 3.5, y - 3.5, z], [7, 7, 0], g), Cube([x, y - 3.5, z - 3.5], [0, 7, 7], g)])
    m.pack()
    return m

# ============================================================================ animations
from biped import keys, smooth, pose_sequence, walk, lowest, descendants
from bovine import stance, legs_pose, copy_pose, merge, sampled, lerp_keys, sternal, lay_tail, knockout, rng, GAIT
from avian import flap, glide_wings, HIDE_OPEN, HIDE_CLOSED, bird_poser

Q = "q.anim_time"
TAIL = ("tail", "tail2", "tail3", "tail4", "tail5", "tail6")
NECK = ("neck", "neck2", "neck3")
EYES = ("eye_left", "eye_right")
EARS = ("ear_left", "ear_right")
FLOATERS = ("halo", "halo_tail", "sigil", "wing_open_left_halo", "wing_open_right_halo")

def fx(speed=1.0, spin=1.0):
    """Floating halos bob; the sigils turn and drift (Molang, periods dividing 8 s)."""
    out = {"halo": {"position": [0, f"math.sin({Q}*{45 * speed})*0.6", 0]},
           "halo_tail": {"position": [0, f"math.sin({Q}*{45 * speed}+90)*0.5", 0]}}
    for side, s in SIDES:
        out[f"wing_open_{side}_halo"] = {"position": [0, f"math.sin({Q}*{90 * speed}+{45 * s})*0.5", 0]}
    for k in range(4):
        out[f"sigil{k + 1}"] = {"rotation": [0, f"{Q}*{round(45 * spin * (1 + k % 2), 1)}", 0],
                                "position": [0, f"math.sin({Q}*{45 * speed * (1 + k % 2)}+{k * 80})*1.5", 0]}
    return out

def tail_wave(f, amp=(3, 4, 5, 6, 7, 6), lag=40, pitch=1.2):
    return {tb: {"rotation": [f"math.sin({Q}*{f}-{lag * i})*{pitch}", f"math.sin({Q}*{f}-{lag * i + 30})*{amp[i]}", 0]}
            for i, tb in enumerate(TAIL)}

def mantle(lift=38.0, sweep=16.0, hand=20.0, pitch=-60.0, breathe=0.0, t=0.0, hand_y=10.0):
    """Great wings raised in a V and half spread, membranes turned to the front, like the statue on the spire
    (battle). X turns the wing about its span (leading edge up), Y sweeps it back, Z raises it."""
    out = {}
    b = math.sin(2 * math.pi * t / 4) * breathe
    for side, s in SIDES:
        out[f"wing_open_{side}"] = {"rotation": [pitch + 2 * b, -s * (sweep + 2 * b), -s * (lift + 4 * b)]}
        out[f"wing_open_{side}2"] = {"rotation": [0, s * hand_y, -s * (hand - 3 * b)]}
    return out

def faint(m, *, trunk, skip, L=3.0):
    """Recoil, stagger, forelegs buckle onto the knees, it sinks onto its brisket, then rolls over onto its flank,
    legs out, neck and head laid on the ground, the tail lying behind (bovine knockout adapted to a long tail)."""
    from bovine import kneel_pose, lateral
    from biped import kf
    k0 = stance(LEGS, 0, 0, PIVOT)
    k1 = merge(stance(LEGS, -4, 0.3, PIVOT), {"neck": {"rotation": [-10, 0, 0]}, "head": {"rotation": [-14, 0, 0]},
                                               "jaw": {"rotation": [16, 0, 0]}})
    k2 = merge(stance(LEGS, 2, -0.6, PIVOT, body_rot=[0, 0, 5]),
               {"neck": {"rotation": [10, -8, 0]}, "neck3": {"rotation": [8, 0, 0]}, "head": {"rotation": [8, 0, 10]},
                "jaw": {"rotation": [6, 0, 0]}})
    k3 = merge(kneel_pose(m, LEGS, PIVOT), {"neck": {"rotation": [18, 4, 0]}, "neck3": {"rotation": [10, 0, 0]},
                                             "head": {"rotation": [10, 0, -6]}})
    k4 = merge(sternal(m, LEGS, trunk, lean=4), {"neck": {"rotation": [30, 0, 0]}, "neck2": {"rotation": [12, 0, 0]},
                                                  "head": {"rotation": [14, 0, 0]}})
    lay_tail(m, k4, TAIL[:5], yaw=(10, 15, 15, 10), skip=skip)
    k5 = lateral(m, LEGS, trunk, skip=skip)
    k5["neck2"] = {"rotation": [0, 12, 0]}
    for i, tb in enumerate(TAIL):                 # the tail laid on the ground: each segment swung (Y, sideways in
        grp = descendants(m, tb) - skip           # the rolled body) until it just rests on the ground
        best = None
        for ry in rng(-70, 70, 57):
            pp = copy_pose(k5)
            pp[tb] = {"rotation": [0, ry, 0]}
            lo = lowest(m, pp, only=grp)
            if lo < 0:
                continue
            sc = abs(lo - 0.3) + 0.002 * abs(ry)
            if best is None or sc < best[0]:
                best = (sc, ry)
        k5[tb] = {"rotation": [0, best[1] if best else 0, 0]}
    k5b = copy_pose(k5)
    k5b["jaw"] = {"rotation": [12, 0, 0]}
    for k, ev in ((k1, 0), (k2, 0), (k3, 0.4), (k4, 0.8)):
        for e_, sg in zip(EARS, (1, -1)):
            k[e_] = {"rotation": [0, -10 * sg, 0]}
    seq = [(0, k0), (0.3, k1), (0.7, k2), (1.15, k3), (1.6, k4), (2.1, k5), (2.6, k5b), (L, k5)]
    lay = skip | {b for b in TAIL} | descendants(m, "tail")
    bones = pose_sequence(m, seq, length=L, skip=lay)
    bp = bones["body"]["position"]
    y = bp["2.1"]["post"][1]
    bp["2.2"] = kf([0, round(y + 0.8, 2), 0])
    bp["2.35"] = kf([0, round(y, 2), 0])
    for e in EYES:
        bones[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.6, 1], 0.7: [1, 1, 1], 1.4: [1, 1, 1], 1.65: [1, 0.1, 1], L: [1, 0.1, 1]})
    return {"animation_length": L, "bones": bones}

def anims(m=None):
    m = m or build()
    a = f"animation.{SID}."
    out = {}
    names = {b.name for b in m.bones}
    skip = {n for n in names if n.startswith(("wing_open",) + FLOATERS) or n in ("mouth_line",)} | set(EYES)
    trunk = {"torso", "chest"} | {b for t in ("torso", "chest") for b in descendants(m, t)
                                   if not b.startswith(("neck", "head", "ear", "eye", "jaw", "horn", "tail", "crest", "halo",
                                                        "mouth", "wing_open"))}
    trunk -= skip

    # ---------------------------------------------------------------- idle: calm breathing, neck sway, tail S-curve
    idle = {"torso": {"rotation": [f"math.sin({Q}*45)*0.6", 0, 0]},
            "chest": {"position": [0, f"math.sin({Q}*45-30)*0.12", 0]},
            "jaw": {"rotation": [f"math.clamp(math.sin({Q}*45-60),0,1)*2", 0, 0]}}
    for i, nb in enumerate(NECK + ("head",)):
        idle[nb] = {"rotation": [f"math.sin({Q}*45-{40 * i})*1.6", f"math.sin({Q}*45-{30 * i + 20})*{3 + 1.5 * i}",
                                 f"math.sin({Q}*90-{30 * i})*{0.8 if nb != 'head' else 2}"]}
    idle.update(tail_wave(45))
    for side, s in SIDES:
        idle[f"pinion_{side}"] = {"rotation": [f"math.sin({Q}*90+{45 * s})*2", 0, f"{s}*math.sin({Q}*90)*3"]}
        idle[f"wing_closed_{side}"] = {"rotation": [0, 0, f"{-s}*math.sin({Q}*45)*1.2"]}
        idle[f"ear_{side}"] = {"rotation": [0, f"{s}*math.sin({Q}*90+20)*4", 0]}
    idle.update(fx()); idle.update(HIDE_OPEN)
    out[a + "ground_idle"] = {"loop": True, "animation_length": 8, "bones": idle}

    # ---------------------------------------------------------------- walk: 4-beat walk, head carried high, tail swinging
    T = 1.6
    f = round(360 / T, 3)
    ex = tail_wave(f, amp=(4, 6, 8, 9, 10, 8), lag=45, pitch=1.5)
    ex["neck2"] = {"rotation": [f"math.sin({Q}*{2 * f}+60)*1.5", f"-math.sin({Q}*{f}+40)*2", 0]}
    ex["neck3"] = {"rotation": [f"math.sin({Q}*{2 * f}+90)*1.5", f"-math.sin({Q}*{f}+70)*2", 0]}
    for side, s in SIDES:
        ex[f"pinion_{side}"] = {"rotation": [0, 0, f"{s}*math.sin({Q}*{2 * f})*4"]}
        ex[f"wing_closed_{side}"] = {"rotation": [0, 0, f"{-s}*math.sin({Q}*{2 * f})*1.5"]}
    ex.update(fx(2.0)); ex.update(HIDE_OPEN)
    out[a + "ground_walk"] = walk(LEGS, phases=GAIT, T=T, stride=11, lift=3.2, stance=0.62, bob=0.5, samples=32,
                                  toe_off=20, fold=25, curl=25, torso=(0.8, 1.5, 1.8), tail=(), neck=True, arms=(), extra=ex)

    # ---------------------------------------------------------------- battle: chest up, wings raised in a V, tail lashing
    def battle_pose(t):
        w = math.sin(2 * math.pi * t / 4)
        p = stance(LEGS, -3.0 + 0.4 * w, -0.4 + 0.15 * w, PIVOT)
        p["neck"] = {"rotation": [-8 + 1.5 * w, 0, 0]}
        p["neck2"] = {"rotation": [-2, 3 * math.sin(2 * math.pi * t / 4 + 1), 0]}
        p["neck3"] = {"rotation": [6, 0, 0]}
        p["head"] = {"rotation": [10 - 2 * w, 0, 2 * math.sin(2 * math.pi * t / 2)]}
        p["jaw"] = {"rotation": [6 + 3 * max(0.0, math.sin(2 * math.pi * t / 2)), 0, 0]}
        for i, tb in enumerate(TAIL):
            p[tb] = {"rotation": [4 if i == 0 else 2, (6 + 3 * i) * math.sin(2 * math.pi * t / 2 - 0.6 * i), 0]}
        for side, s in SIDES:
            p[f"ear_{side}"] = {"rotation": [0, s * 12, 0]}
        p.update(mantle(breathe=1.0, t=t))
        for side, s in SIDES:
            p[f"pinion_{side}"] = {"rotation": [-6, s * 14, -s * (48 + 5 * w)]}
        return p
    b = sampled(4, 0.1, battle_pose, loop=True)
    b.update(fx(2.0, 2.0)); b.update(HIDE_CLOSED)
    out[a + "battle_idle"] = {"loop": True, "animation_length": 4, "bones": b}

    # ---------------------------------------------------------------- cries: rearing roar
    def roar(open_wings):
        L = 2.4
        def pose(t):
            up = lerp_keys([(0, 0), (0.45, 1), (1.9, 1), (2.4, 0)], t)
            jaw = lerp_keys([(0, 0), (0.5, 0), (0.7, 28), (1.7, 24), (2.1, 0)], t)
            head = lerp_keys([(0, 0), (0.45, -16), (0.7, 6), (1.8, 4), (2.4, 0)], t)
            sh = math.sin(t * 60) * (1 if 0.7 < t < 1.7 else 0)
            p = stance(LEGS, (-3.0 if open_wings else 0.0) - 7 * up, -0.4 * up, PIVOT)
            p["neck"] = {"rotation": [-10 * up, 0, 0]}
            p["neck2"] = {"rotation": [-6 * up, 0, 0]}
            p["neck3"] = {"rotation": [4 * up + 0.8 * sh, 0, 0]}
            p["head"] = {"rotation": [head + 1.5 * sh, 0, 0]}
            p["jaw"] = {"rotation": [jaw, 0, 0]}
            for i, tb in enumerate(TAIL):
                p[tb] = {"rotation": [6 * up, 12 * up * math.sin(t * 4 - 0.7 * i), 0]}
            for side, s in SIDES:
                p[f"pinion_{side}"] = {"rotation": [-6 * up, s * 16 * up, -s * (55 * up)]}
                p[f"ear_{side}"] = {"rotation": [0, s * 18 * up, 0]}
                if not open_wings:
                    p[f"wing_closed_{side}"] = {"rotation": [-6 * up, 0, -s * 10 * up]}
            if open_wings:
                p.update(mantle(lift=40 + 18 * up, sweep=22 - 6 * up, hand=30 + 10 * up))
            return p
        bones = sampled(L, 0.05, pose)
        bones.update(fx(3.0, 3.0))
        bones.update(HIDE_CLOSED if open_wings else HIDE_OPEN)
        return {"animation_length": L, "bones": bones}
    out[a + "cry"] = roar(False)
    out[a + "battle_cry"] = roar(True)

    # ---------------------------------------------------------------- sleep: lying down, neck curled round, tail wrapped
    sp = sternal(m, LEGS, trunk, lean=2)
    head_grp = descendants(m, "head") - skip
    best = None
    for nx in rng(10, 70, 13):
        for hx in rng(-20, 40, 13):
            pp = copy_pose(sp)
            pp["neck"] = {"rotation": [nx, 26, 0]}
            pp["neck2"] = {"rotation": [nx * 0.5, 26, 0]}
            pp["neck3"] = {"rotation": [10, 22, 0]}
            pp["head"] = {"rotation": [hx, 10, 8]}
            lo = lowest(m, pp, only=head_grp)
            if lo < 0:
                continue
            sc = abs(lo - 0.2) + 0.01 * abs(hx)
            if best is None or sc < best[0]:
                best = (sc, nx, hx)
    _, nx, hx = best
    sp["neck"] = {"rotation": [nx, 26, 0]}
    sp["neck2"] = {"rotation": [nx * 0.5, 26, 0]}
    sp["neck3"] = {"rotation": [10, 22, 0]}
    sp["head"] = {"rotation": [hx, 10, 8]}
    lay_tail(m, sp, TAIL[:5], yaw=(10, 20, 25, 25, 20), skip=skip)
    sleep = {bn: dict(ch) for bn, ch in sp.items()}
    sleep["torso"] = {"rotation": [f"math.sin({Q}*45)*0.6", 0, 0]}
    sleep["chest"] = {"position": [0, f"0.05+math.sin({Q}*45-20)*0.08", 0]}
    sleep["tail6"] = {"rotation": [0, 20, 0]}
    for e in EYES:
        sleep[e] = {"scale": [1, 0.1, 1]}
    for side, s in SIDES:
        sleep[f"wing_closed_{side}"] = {"rotation": [0, 0, -s * 3]}
        sleep[f"pinion_{side}"] = {"rotation": [0, -s * 20, -s * 14]}
    sleep["jaw"] = {"rotation": [0, 0, 0]}
    fl = fx(0.5, 0.4)
    for k in range(4):
        fl[f"sigil{k + 1}"]["scale"] = 0.7
    sleep.update(fl); sleep.update(HIDE_OPEN)
    out[a + "sleep"] = {"loop": True, "animation_length": 8, "bones": sleep}

    # ---------------------------------------------------------------- faint: stagger, buckle, roll onto its flank
    soft = {n for n in names if n.startswith(("crystal", "pinion", "wing_closed", "pauldron", "horn", "halo", "crest"))}
    ko = faint(m, trunk={"torso", "chest"}, skip=skip | soft)
    kb = ko["bones"]
    for k in range(4):
        kb[f"sigil{k + 1}"] = keys(scale={0: [1, 1, 1], 1.2: [1, 1, 1], 2.4: [0, 0, 0], 3.0: [0, 0, 0]},
                                   position={0: [0, 0, 0], 2.4: [0, -6, 0], 3.0: [0, -6, 0]})
    for h in ("halo", "halo_tail"):
        kb[h] = keys(scale={0: [1, 1, 1], 1.6: [1, 1, 1], 2.6: [0, 0, 0], 3.0: [0, 0, 0]})
    for side, s in SIDES:
        kb[f"wing_closed_{side}"] = keys(rotation={0: [0, 0, 0], 1.0: [0, 0, -s * 8], 2.2: [0, 0, s * 6], 3.0: [0, 0, s * 6]})
    kb.update(HIDE_OPEN)
    out[a + "faint"] = ko

    out[a + "blink"] = {"animation_length": 0.2, "bones": {
        e: {"scale": {"0.0": [1, 1, 1], "0.1": [1, 0.1, 1], "0.2": [1, 1, 1]}} for e in EYES}}

    # ---------------------------------------------------------------- flight
    def tuck(front, back):
        return legs_pose(LEGS, {lg.side: (front if lg.side.startswith("front") else back) for lg in LEGS})
    FT = 1.4
    fq = round(360 / FT, 3)
    hover = {bn: dict(ch) for bn, ch in tuck((30, -55, -20, 20), (-30, 50, 10, 40)).items()}
    hover.update(flap(FT, amp=42, up=8, hand=1.2, lag=50, sweep=14))
    hover["body"] = {"rotation": [-24, 0, 0], "position": [0, f"12+math.sin({Q}*{fq}-90)*1.2", 0]}
    hover["neck"] = {"rotation": [18, 0, 0]}
    hover["neck2"] = {"rotation": [4, 0, 0]}
    hover["neck3"] = {"rotation": [0, 0, 0]}
    hover["head"] = {"rotation": [6, f"math.sin({Q}*{fq / 3:.2f})*6", 0]}
    for i, tb in enumerate(TAIL):
        hover[tb] = {"rotation": [f"{16 if i == 0 else 8}+math.sin({Q}*{fq}-{40 * i})*2", f"math.sin({Q}*{fq / 2:.2f}-{40 * i})*{3 + i}", 0]}
    for side, s in SIDES:
        hover[f"pinion_{side}"] = {"rotation": [-10, s * 12, f"{-s}*(42+math.sin({Q}*{fq}-60)*16)"]}
    hover.update(fx(1.5)); hover.update(HIDE_CLOSED)
    out[a + "air_idle"] = {"loop": True, "animation_length": FT, "bones": hover}

    FT2 = 1.8
    fq2 = round(360 / FT2, 3)
    fly = {bn: dict(ch) for bn, ch in tuck((70, 20, 70, 90), (-60, 120, 150, 100)).items()}
    fly.update(flap(FT2, amp=48, up=4, hand=1.25, lag=45, sweep=18))
    fly["body"] = {"rotation": [f"-2+math.sin({Q}*{fq2})*2", 0, 0], "position": [0, f"math.sin({Q}*{fq2}-90)*1.0", 0]}
    fly["neck"] = {"rotation": [f"48+math.sin({Q}*{fq2})*2", 0, 0]}
    fly["neck2"] = {"rotation": [14, 0, 0]}
    fly["neck3"] = {"rotation": [-6, 0, 0]}
    fly["head"] = {"rotation": [f"-36-math.sin({Q}*{fq2})*2", 0, 0]}
    for i, tb in enumerate(TAIL):
        fly[tb] = {"rotation": [f"{20 if i == 0 else 4 if i < 3 else -4}+math.sin({Q}*{fq2}-{45 * i})*2",
                                f"math.sin({Q}*{fq2 / 2:.2f}-{45 * i})*{2 + i}", 0]}
    for side, s in SIDES:
        fly[f"pinion_{side}"] = {"rotation": [-6, s * 4, f"{-s}*(30+math.sin({Q}*{fq2}-60)*12)"]}
    fly.update(fx(2.0)); fly.update(HIDE_CLOSED)
    out[a + "air_fly"] = {"loop": True, "animation_length": FT2, "bones": fly}

    def air_cry_pose(t):
        up = lerp_keys([(0, 0), (0.4, 1), (1.6, 1), (2.0, 0)], t)
        jaw = lerp_keys([(0, 0), (0.45, 30), (1.5, 26), (1.9, 0)], t)
        p = {"neck": {"rotation": [18 - 12 * up, 0, 0]}, "neck2": {"rotation": [4 - 6 * up, 0, 0]},
             "head": {"rotation": [6 - 10 * up + 2 * math.sin(t * 50) * up, 0, 0]}, "jaw": {"rotation": [jaw, 0, 0]}}
        for side, s in SIDES:
            p[f"ear_{side}"] = {"rotation": [0, s * 18 * up, 0]}
        return p
    ac = sampled(2.0, 0.05, air_cry_pose)
    out[a + "air_cry"] = {"animation_length": 2.0, "bones": ac}

    # ---------------------------------------------------------------- portrait
    pb = {"head": {"rotation": [4, -10, 0]}, "neck3": {"rotation": [0, -6, 0]}}
    pb.update(fx()); pb.update(HIDE_OPEN)
    out[a + "portrait"] = {"loop": True, "animation_length": 8, "bones": pb}

    # ---------------------------------------------------------------- ridden: folded wings eased out from the rider
    def clear_wings(d):
        for side, s in SIDES:
            d[f"wing_closed_{side}"] = {"rotation": [0, s * 6, s * 9]}
        return d
    mgi = {bn: dict(ch) for bn, ch in idle.items()}
    clear_wings(mgi)
    out[a + "mount_ground_idle"] = {"loop": True, "animation_length": 8, "bones": mgi}
    mw = walk(LEGS, phases=GAIT, T=1.2, stride=13, lift=3.6, stance=0.58, bob=0.7, samples=32, toe_off=22, fold=30,
              curl=28, torso=(1.0, 1.6, 2.0), tail=(), neck=True, arms=(), extra=clear_wings(dict(ex)))
    mw["bones"].update(clear_wings({}))
    out[a + "mount_ground_walk"] = mw
    out[a + "mount_air_idle"] = out[a + "air_idle"]
    mf = {bn: dict(ch) for bn, ch in fly.items()}
    mf["body"] = {"rotation": [f"math.sin({Q}*{fq2})*1.5", 0, 0], "position": [0, f"math.sin({Q}*{fq2}-90)*0.8", 0]}
    out[a + "mount_air_fly"] = {"loop": True, "animation_length": FT2, "bones": mf}
    glide = {bn: dict(ch) for bn, ch in tuck((70, 20, 70, 90), (-60, 120, 150, 100)).items()}
    glide.update(glide_wings(sway=3.0, T=8.0))
    glide["body"] = {"rotation": [f"2+math.sin({Q}*45)*1.5", 0, f"math.sin({Q}*45)*4"]}
    glide["neck"] = {"rotation": [46, 0, 0]}
    glide["neck2"] = {"rotation": [14, 0, 0]}
    glide["neck3"] = {"rotation": [-6, 0, 0]}
    glide["head"] = {"rotation": [-34, f"math.sin({Q}*45+40)*5", 0]}
    for i, tb in enumerate(TAIL):
        glide[tb] = {"rotation": [f"{20 if i == 0 else 4 if i < 3 else -4}", f"math.sin({Q}*45-{45 * i})*{2 + i}", 0]}
    for side, s in SIDES:
        glide[f"pinion_{side}"] = {"rotation": [-6, s * 4, -s * 34]}
    glide.update(fx(1.0)); glide.update(HIDE_CLOSED)
    out[a + "air_glide"] = {"loop": True, "animation_length": 8, "bones": glide}
    d = "math.clamp(q.r.dive(0),0,1)"                  # layered over air_glide: wings swept back into a stoop
    dive = {}
    for side, s in SIDES:
        dive[f"wing_open_{side}"] = {"rotation": [0, f"{-s * 38}*{d}", f"{s * 8}*{d}"]}
        dive[f"wing_open_{side}2"] = {"rotation": [0, f"{-s * 42}*{d}", f"{s * 6}*{d}"]}
        dive[f"pinion_{side}"] = {"rotation": [0, f"{-s * 30}*{d}", f"{s * 20}*{d}"]}
    dive["body"] = {"rotation": [f"18*{d}", 0, 0]}
    dive["neck"] = {"rotation": [f"-10*{d}", 0, 0]}
    dive["head"] = {"rotation": [f"-6*{d}", 0, 0]}
    dive.update(HIDE_CLOSED)
    out[a + "ride_dive"] = {"loop": True, "animation_length": 1, "bones": dive}
    return finalize(out)

def poser():
    ps = bird_poser(SID, portrait=(0.9, [-0.6, 2.8, 0]), profile=(0.3, [0, 1.29, 0]), menace=True, ride=True)
    ps["firstPersonCameraOffset"] = {"seat_1": [0, 0.5, 0]}
    ps["thirdPersonCameraOffset"] = {"seat_1": [0, 1.2, 3.0], "seat_1_reverse": [0, 1.2, 3.0]}
    ps["poses"]["standing"]["poseTypes"] = ["STAND", "NONE"]
    closed = ps["poses"]["standing"]["transformedParts"]
    ps["poses"] = {"portrait": {"poseTypes": ["PORTRAIT", "PROFILE"], "isBattle": False,
                                "animations": [f"q.bedrock('{SID}', 'portrait')"],
                                "quirks": [f"q.bedrock_quirk('{SID}', 'blink')"], "transformedParts": closed},
                   **ps["poses"]}
    return ps
