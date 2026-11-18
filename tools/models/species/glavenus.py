# -*- coding: utf-8 -*-
"""#11232 Glavenus — Wyverne brute de Monster Hunter (Feu / Acier), et sa méga-évolution Glavenus Lame-Chaos.

Silhouette of a lean, athletic brute wyvern: long horizontal body on powerful digitigrade legs (red scaled thighs, dark
grey shins and feet with black claws), small clawed arms, a long crocodile-like head carried low with a pink gape full
of teeth and a crown of dark spikes at the back of the skull, a fringe of big slate-blue spikes curving back along the
neck and the back. Crimson scales edged with dark navy, cream belly. Its tail rises from the hips and arcs up and over
the body like a scorpion's, ending in a colossal curved sword blade (laterally flat, the cutting edge on the outer side
of the arc): steel blue with glowing teal veins and a pale edge, a crusty dark rim along the inner side. When it fights
the blade heats up until it glows red-hot.

Glavenus Lame-Chaos (mega, "Hellblade"): the Mega Gem burns it from the inside — charcoal hide cracked with glowing red
fissures, dark red armour plates, red-pink spiky dorsal fins trailing a red-pink mist, burning red eyes, a mouth
glowing like a furnace, and a molten blade (white-hot edge, orange, red) licked by flames, embers drifting off it.
Shiny: Acidic-like dark teal hide with an acid-green blade (shiny Lame-Chaos: blue-white flames)."""
import math, os, importlib.util
from modelgen import Model, Cube, rgb, apply
from biped import (Leg, leg_pose, timeline, keys, kf, lowest, standard_anims, lie_legs, pose_sequence,
                   search, descendants, pose_to_bones, smooth)
from bovine import vnoise, put, light, side_cols
from templates import poser as make_poser, tremble

_spec = importlib.util.spec_from_file_location("_deviljho_shared",
                                               os.path.join(os.path.dirname(os.path.abspath(__file__)), "deviljho.py"))
DJ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DJ)
_dir_rot, grad_fn, _hpt, _veins = DJ._dir_rot, DJ.grad_fn, DJ._hpt, DJ._veins
mouth_fn, throat_fn, claw_fn, smoke_fn, breath_fn, eye_fn, trail_fn = (DJ.mouth_fn, DJ.throat_fn, DJ.claw_fn,
                                                                       DJ.smoke_fn, DJ.breath_fn, DJ.eye_fn, DJ.trail_fn)
S, bump, ramp, sampled, ik_track = DJ.S, DJ.bump, DJ.ramp, DJ.sampled, DJ.ik_track

SID, DEX = "glavenus", 11232
MEGA_SID = "glavenus_lame_chaos"
FRAME_BONES = ("head", "jaw", "neck")
HEIGHT_SKIP = ("blade", "spk", "crest", "aura", "flame", "breath", "ember", "heat", "teeth")
HITBOX_WIDTH = 1.8
SPECIES_DIR = "monster_hunter"

# ---------------------------------------------------------------------------------------------------- palettes
PAL = {
    # crimson scales edged with dark navy, cream belly, dark grey legs
    "skin": rgb("#8E2632"), "skin_dark": rgb("#64182A"), "skin_light": rgb("#B03A44"), "skin_edge": rgb("#2E1626"),
    "armor": rgb("#2A2C44"), "armor_light": rgb("#45486A"),
    "plate": rgb("#2E3050"), "plate_dark": rgb("#1C1D34"), "plate_light": rgb("#474C74"), "plate_edge": rgb("#12121E"),
    "belly": rgb("#D4C49C"), "belly_dark": rgb("#A8966E"), "belly_light": rgb("#EADCB6"),
    "leg": rgb("#2E3050"), "leg_dark": rgb("#1C1D34"), "leg_light": rgb("#464A72"), "leg_edge": rgb("#12121E"),
    "spike": rgb("#343C6C"), "spike_dark": rgb("#1C1E3C"), "spike_tip": rgb("#5ECCC4"),
    "claw": rgb("#1E1E26"), "claw_tip": rgb("#70707C"),
    "tooth": rgb("#E8E2CC"), "tooth_dark": rgb("#A89E84"),
    "mouth": rgb("#8A2A3A"), "gum": rgb("#D06A7A"), "tongue": rgb("#E0909A"), "palate": rgb("#B84A5C"),
    "throat": rgb("#3A0C14"), "nostril": rgb("#14141C"),
    "eye": rgb("#7AF0C8"), "eye_rim": rgb("#4A1018"), "pupil": rgb("#020404"), "socket": rgb("#08080E"),
    "eye_glint": rgb("#B0FFE0"), "eye_glow": rgb("#5AE8B8"), "eye_hot": rgb("#E4FFF2"),
    # the blade: steel blue, teal glowing veins, pale edge, dark crusty rim
    "rim": rgb("#1C2A50"), "rim_light": rgb("#2E4478"), "rim_dark": rgb("#101830"),
    "blade_dark": rgb("#183A74"), "blade": rgb("#2A5EAA"), "blade_light": rgb("#4486D2"), "blade_pale": rgb("#76B4EA"),
    "blade_edge": rgb("#B4F0FF"), "blade_vein": rgb("#4ED8FF"), "blade_vein_hot": rgb("#C8F8FF"),
    "blade_glow": rgb("#6AE0FF"), "blade_bronze": rgb("#6E6650"),
    # heat (red-hot blade), fire breath, embers
    "heat_dim": rgb("#A0201A"), "heat": rgb("#FF4A1A"), "heat_hot": rgb("#FFB040"), "heat_white": rgb("#FFF0B0"),
    "breath_core": rgb("#FFF2C0"), "breath": rgb("#FFA028"), "breath_mid": rgb("#E8401A"), "breath_edge": rgb("#5A0A08"),
    "mouth_glow": rgb("#FF8A1E"), "mouth_hot": rgb("#FFE6A0"),
    "ember": rgb("#FF8A2A"), "ember_hot": rgb("#FFE0A0"),
    "vein": rgb("#FF3A18"), "vein_hot": rgb("#FFB070"),
    "smoke": rgb("#7A1A2E"), "smoke_dark": rgb("#3A0A16"), "smoke_red": rgb("#C02A48"), "smoke_glow": rgb("#FF4A6A"),
    "fire_core": rgb("#FFF6D0"), "fire": rgb("#FFB030"), "fire_mid": rgb("#FF5A18"), "fire_edge": rgb("#B01A10"),
}
SHINY = dict(PAL, **{        # Acidic-like: dark teal hide, acid green blade
    "skin": rgb("#1E4A48"), "skin_dark": rgb("#123232"), "skin_light": rgb("#2E6460"), "skin_edge": rgb("#0A1418"),
    "armor": rgb("#162226"), "armor_light": rgb("#2A3A3E"),
    "plate": rgb("#18282A"), "plate_dark": rgb("#0E1A1C"), "plate_light": rgb("#28403E"), "plate_edge": rgb("#081012"),
    "rim": rgb("#1A2E1C"), "rim_light": rgb("#2C4A2C"), "rim_dark": rgb("#0E1A10"),
    "belly": rgb("#B8C0A0"), "belly_dark": rgb("#8C9478"), "belly_light": rgb("#D2D8BC"),
    "spike": rgb("#2A3A3A"), "spike_dark": rgb("#141E20"), "spike_tip": rgb("#9AC0A8"),
    "blade_dark": rgb("#2E5A1A"), "blade": rgb("#4E8A26"), "blade_light": rgb("#72B436"), "blade_pale": rgb("#A4D85A"),
    "blade_edge": rgb("#EAFFB0"), "blade_vein": rgb("#C8FF3A"), "blade_vein_hot": rgb("#F4FFC8"),
    "blade_glow": rgb("#B0FF40"), "blade_bronze": rgb("#4A5A30"),
})
MEGA = dict(PAL, **{         # Lame-Chaos: charcoal hide, red cracks, red-pink fins, molten blade
    "skin": rgb("#2E2A2E"), "skin_dark": rgb("#1C191C"), "skin_light": rgb("#463F44"), "skin_edge": rgb("#0E0B0E"),
    "armor": rgb("#5E1620"), "armor_light": rgb("#8A2430"),
    "plate": rgb("#3A1418"), "plate_dark": rgb("#22090C"), "plate_light": rgb("#5A1E24"), "plate_edge": rgb("#120406"),
    "belly": rgb("#A8A09A"), "belly_dark": rgb("#7E7670"), "belly_light": rgb("#C4BCB4"),
    "leg": rgb("#2A272C"), "leg_dark": rgb("#18161A"), "leg_light": rgb("#3E3A40"), "leg_edge": rgb("#0A090C"),
    "spike": rgb("#5E1A30"), "spike_dark": rgb("#22080F"), "spike_tip": rgb("#FF6A50"),
    "smoke": rgb("#B01E3C"), "smoke_dark": rgb("#6A0E24"), "smoke_red": rgb("#F0406A"), "smoke_glow": rgb("#FF8AAA"),
    "eye": rgb("#FF3A14"), "eye_rim": rgb("#7A0A08"), "eye_glow": rgb("#FF2A10"), "eye_hot": rgb("#FFE6A0"),
    "mouth": rgb("#A0381A"), "palate": rgb("#E06A1E"), "tongue": rgb("#FF9A3A"), "gum": rgb("#C04A2A"),
    "throat": rgb("#FFB040"),
    "rim": rgb("#2A1414"), "rim_light": rgb("#4A2020"), "rim_dark": rgb("#160A0A"),
    "blade_dark": rgb("#B01A10"), "blade": rgb("#FF5A18"), "blade_light": rgb("#FFA030"), "blade_pale": rgb("#FFD870"),
    "blade_edge": rgb("#FFFBE8"), "blade_vein": rgb("#FFF0A0"), "blade_vein_hot": rgb("#FFFFFF"),
    "blade_glow": rgb("#FFD060"), "blade_bronze": rgb("#8A2A10"),
})
MEGA_SHINY = dict(MEGA, **{  # obsidian body, blue-white flames
    "skin": rgb("#24262E"), "skin_dark": rgb("#14161C"), "skin_light": rgb("#383C48"), "skin_edge": rgb("#08090E"),
    "armor": rgb("#1A2A5E"), "armor_light": rgb("#2A428A"),
    "plate": rgb("#1A2448"), "plate_dark": rgb("#0E1430"), "plate_light": rgb("#2A3A6A"), "plate_edge": rgb("#060A18"),
    "spike": rgb("#3A5AC0"), "spike_dark": rgb("#14205A"), "spike_tip": rgb("#A0D0FF"),
    "eye": rgb("#4AA0FF"), "eye_rim": rgb("#0A1A5A"), "eye_glow": rgb("#3A8AFF"), "eye_hot": rgb("#E8F6FF"),
    "mouth": rgb("#1A3A8A"), "palate": rgb("#2A6AE0"), "tongue": rgb("#6AB0FF"), "gum": rgb("#2A4AA0"),
    "throat": rgb("#A0D8FF"), "mouth_glow": rgb("#4A9AFF"), "mouth_hot": rgb("#E0F4FF"),
    "rim": rgb("#141A2A"), "rim_light": rgb("#24304A"), "rim_dark": rgb("#0A0E18"),
    "blade_dark": rgb("#1A3AE0"), "blade": rgb("#3A86FF"), "blade_light": rgb("#7ABEFF"), "blade_pale": rgb("#BCE4FF"),
    "blade_edge": rgb("#FFFFFF"), "blade_vein": rgb("#E8F8FF"), "blade_vein_hot": rgb("#FFFFFF"),
    "blade_glow": rgb("#9AD4FF"), "blade_bronze": rgb("#1A2A8A"),
    "breath_core": rgb("#F4FAFF"), "breath": rgb("#7AC0FF"), "breath_mid": rgb("#2A60F0"), "breath_edge": rgb("#0A1650"),
    "ember": rgb("#6AB4FF"), "ember_hot": rgb("#E8F6FF"), "vein": rgb("#3A7AFF"), "vein_hot": rgb("#C0E0FF"),
    "smoke": rgb("#1A2A6A"), "smoke_dark": rgb("#0A1030"), "smoke_red": rgb("#2A4AC0"), "smoke_glow": rgb("#6AA0FF"),
    "fire_core": rgb("#FFFFFF"), "fire": rgb("#9AD0FF"), "fire_mid": rgb("#3A7AFF"), "fire_edge": rgb("#1A2A9A"),
    "heat_dim": rgb("#1A3AA0"), "heat": rgb("#3A86FF"), "heat_hot": rgb("#A0D8FF"), "heat_white": rgb("#F4FAFF"),
})
SHINY_FIRE = {k: PAL[k] for k in ("breath_core", "breath", "breath_mid", "breath_edge", "mouth_glow", "mouth_hot")}
SHINY.update(SHINY_FIRE)

GLOW = {"glow": True, "shading": False}


# ---------------------------------------------------------------------------------------------------- painters
def scales(*, belly=0, back=True, tone="skin", ps=(4, 4), cracks=None, armor=True, post=None, post_glow=None, rib=2.0,
           **extra):
    """Overlapping scales painted in world space (patterns run across cubes): every scale is shaded from a lighter top
    to a darker bottom and edged with dark navy; the top of the back is armoured with navy plates; belly: the bottom
    rows of the side faces (and the down face) are a cream ribbed belly; cracks (mega): glowing red fissures above
    this height."""
    pw, ph = ps

    def classify(c, face, pl, p):
        x0, y0, z0 = c.origin
        w, h, d = c.size
        if face in ("east", "west"):
            u, v = p[2], p[1]
        elif face in ("north", "south"):
            u, v = p[0], p[1]
        else:
            u, v = p[0], p[2]
        row = math.floor(v / ph)
        fu = (u / pw + 0.5 * (row % 2) + 0.15 * vnoise(1.0, row * 0.7, 2.0, 13)) % 1.0
        fv = (v / ph) % 1.0
        m = vnoise(p[0] * 0.22, p[1] * 0.22, p[2] * 0.22, 3)
        key = tone if 0.3 < m < 0.66 else (tone + "_dark" if m >= 0.66 else tone + "_light")
        f = 0.84 + 0.3 * fv
        if (fv < 1.0 / ph and fu > 0.28) or (fu < 0.75 / pw and fv < 0.6):
            key, f = tone + "_edge" if tone != "belly" else "belly_dark", 1.0
        top = face == "up" or (face in ("east", "west", "north", "south") and pl[1] > y0 + h - 1.01)
        if back and armor and top and tone == "skin":
            a = vnoise(p[0] * 0.5, 2.0, p[2] * 0.35, 8)
            if a > 0.42:
                key = "armor_light" if fv > 0.7 and key != "skin_edge" else ("skin_edge" if key == "skin_edge" else "armor")
        if belly and (face == "down" or (face in ("east", "west", "north", "south") and pl[1] < y0 + belly)):
            key, f = "belly", 1.0
            zz = p[2] if face != "north" else p[1]
            if (zz % rib) < 0.6:
                key = "belly_dark"
            elif (zz % rib) > rib - 0.6:
                key = "belly_light"
        if cracks is not None and p[1] > cracks and _veins(p, seed=11, cell=5.5, width=0.42):
            key = "vein"
        return key, f

    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            key, f2 = classify(c, face, pl, p)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.12) * f2
            put(px, X, Y, pal[key], 1.0 if key == "vein" else f, rnd, 5)
        if post:
            post(px, faces, pal, rnd)

    def glow_fn(px, faces, pal, rnd, c):
        if post_glow:
            post_glow(px, faces, pal, rnd)
        if cracks is None:
            return
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            key, _ = classify(c, face, pl, p)
            if key == "vein":
                hot = vnoise(p[0] * 0.9, p[1] * 0.9, p[2] * 0.9, 12) > 0.64
                put(px, X, Y, pal["vein_hot"] if hot else pal["vein"], 1.0, rnd, 8)

    d = {"base": tone, "fn3": fn3, "glow_fn": glow_fn}
    d.update(extra)
    return d


SPIKE_ROOT = grad_fn(("spike_dark", "spike_dark", "spike"))
SPIKE_MID = grad_fn(("spike_dark", "spike", "spike"))
SPIKE_TIP = grad_fn(("spike", "spike", "spike_tip"))
TOOTH = grad_fn(("tooth_dark", "tooth", "tooth"))
CLAW = {"fn": claw_fn, "base": "claw"}
CRYSTAL_ROOT = grad_fn(("rim_dark", "rim", "blade_dark"))
CRYSTAL_TIP = grad_fn(("blade_dark", "blade", "blade_light"))


def horn(p, dirs, lens, widths=(3, 2, 1), paints=(SPIKE_ROOT, SPIKE_MID, SPIKE_TIP)):
    """Tapered, curved spike rooted at p: a chain of cubes (widths[i] x lens[i] x widths[i]) each along dirs[i], every
    piece starting where the previous one ends (the root is half sunk into the surface)."""
    out = []
    x, y, z = p
    for i, (d, L, w) in enumerate(zip(dirs, lens, widths)):
        n = math.sqrt(sum(v * v for v in d))
        dh = [v / n for v in d]
        wx, wz = w if isinstance(w, tuple) else (w, w)       # (thickness, breadth): flat plate-like horns
        sunk = min(wx, wz) / 2 if i == 0 else 0.5
        out.append(Cube([x - wx / 2, y - sunk, z - wz / 2], [wx, int(L + sunk), wz], paints[min(i, len(paints) - 1)],
                        rotation=_dir_rot(d), pivot=[x, y, z]))
        x, y, z = x + dh[0] * (L - 0.5), y + dh[1] * (L - 0.5), z + dh[2] * (L - 0.5)
    return out


def bend(d, k):
    """Direction d tilted further back (toward +Z) and down by factor k (curved spikes)."""
    return (d[0], d[1] - 0.35 * k, d[2] + 0.6 * k)


def tooth(p, d, L=2):
    return [Cube([p[0] - 0.5, p[1] - 0.5, p[2] - 0.5], [1, L, 1], TOOTH, rotation=_dir_rot(d), pivot=list(p))]


# ---------------------------------------------------------------------------------------------------- the blade
BLADE_R = 120.0         # radius of curvature of the blade (gentle upward sweep toward the tip)
BLADE_LEN = 56          # length of the spine line
BLADE_DS = 4            # step length (one cube every 4 px along the arc, overlapping by 1)
FLAME_S = (4, 12, 20, 28, 36, 44)


def blade_width(s):
    """Depth of the blade (from the spine line down to the cutting edge) at arc length s: it grows out of the tail,
    is broadest in the middle (a cleaver-like scimitar) and the edge sweeps up to the point."""
    if s < 16:
        return 5 + 9 * smooth(s / 16)
    if s < 36:
        return 14 + 3 * smooth((s - 16) / 20)
    return max(1.0, 17 * (1 - ((s - 36) / (BLADE_LEN - 36)) ** 1.4))


def rim_height(s):
    return max(2, round(6 - 3 * s / BLADE_LEN))


def blade_point(y0, z0, s):
    phi = s / BLADE_R
    return y0 + BLADE_R * (1 - math.cos(phi)), z0 + BLADE_R * math.sin(phi), phi


def blade_paint(mega):
    """Flat of the blade, shaded by depth t (0 = spine, 1 = edge): dark near the rim, lighter toward the edge,
    mottled; a network of glowing veins (teal; mega: white-hot cracks in the molten metal)."""
    def tone(t, p):
        n = vnoise(p[0] * 0.12 + 5, p[1] * 0.12, p[2] * 0.12, 17)
        tt = t + (n - 0.5) * 0.3
        if tt < 0.4 and vnoise(p[0] * 0.2 + 9, p[1] * 0.35, p[2] * 0.2, 31) > 0.66:
            return "blade_bronze"
        if tt < 0.22:
            return "blade_dark"
        if tt < 0.55:
            return "blade"
        if tt < 0.82:
            return "blade_light"
        return "blade_pale"

    def depth(c, pl):
        y0, h = c.origin[1], c.size[1]
        return max(0.0, min(1.0, (y0 + h - pl[1]) / max(h, 1)))

    def vein(p, t):
        return t > 0.12 and _veins(p, seed=23, cell=4.6, width=0.34 if not mega else 0.42)

    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            t = depth(c, pl)
            key = tone(t, p)
            if face in ("up", "north", "south"):
                key = "blade_dark" if face == "up" else key
            if vein(p, t) and face in ("east", "west"):
                key = "blade_vein"
            fx, fy, fw, fh = faces[face]
            put(px, X, Y, pal[key], 1.0 if mega else light(face, Y - fy, fh, 0.08), rnd, 3)

    def glow_fn(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            t = depth(c, pl)
            if face in ("east", "west") and vein(p, t):
                hot = _hpt(int(p[0] * 3), int(p[1] * 3), int(p[2] * 3), 5)[0] > 0.7
                put(px, X, Y, pal["blade_vein_hot" if hot else "blade_vein"], 1.0, rnd, 6)
            elif mega and t > 0.18:
                put(px, X, Y, pal[tone(t, p)], 1.0, rnd, 6)

    return {"base": "blade", "fn3": fn3, "glow_fn": glow_fn}


def rim_paint(px, faces, pal, rnd):
    """Crusty dark rim along the inner side of the blade (the tail's armoured back)."""
    for face, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                r = _hpt(x + i, y + j, 3, 41)[0]
                k = "rim_dark" if r < 0.3 else ("rim_light" if r > 0.82 else "rim")
                put(px, x + i, y + j, pal[k], light(face, j, h), rnd, 6)


def edge_paint(mega):
    def fn(px, faces, pal, rnd):
        for face, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    put(px, x + i, y + j, pal["blade_edge"], 1.0, rnd, 4)
    return {"fn": fn, "base": "blade_edge", **GLOW}


def heat_fn(px, faces, pal, rnd):
    """Red-hot overlay of the blade (transparent near the rim, white-hot at the edge)."""
    for face, (x, y, w, h) in faces.items():
        if not (w and h) or face not in ("east", "west"):
            continue
        for j in range(h):
            t = (j + 0.5) / h
            for i in range(w):
                r = _hpt(x + i, y + j, 7, 53)
                if r[0] > smooth((t - 0.22) / 0.4):          # dithered fade toward the rim
                    continue
                tt = t + (r[1] - 0.5) * 0.18
                k = "heat_white" if tt > 0.9 else ("heat_hot" if tt > 0.74 else ("heat" if tt > 0.5 else "heat_dim"))
                put(px, x + i, y + j, pal[k], 1.0, rnd, 6)


def flame_fn(seed):
    """Tongues of fire rising from the root of a transparent plane (white core, yellow, orange, red tips)."""
    def fn(px, faces, pal, rnd):
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face in ("up", "down"):
                continue
            for i in range(w):
                u = (i + 0.5) / w
                n = vnoise(i * 0.45 + seed, seed * 0.7, 1.0, seed)
                top = h * (0.35 + 0.65 * n) * (1 - 0.6 * abs(u - 0.5) * 2)
                for j in range(h):
                    hh = h - j - 0.5           # height above the root (row 0 = top of the plane)
                    if hh > top:
                        continue
                    t = hh / max(top, 1e-3)
                    k = "fire_core" if t < 0.25 and abs(u - 0.5) < 0.3 else (
                        "fire" if t < 0.55 else ("fire_mid" if t < 0.85 else "fire_edge"))
                    put(px, x + i, y + j, pal[k], 1.0, rnd, 6)
    return {"fn": fn, **GLOW}


# Narrow, slanted, glowing eye set deep under the horn base (columns from the FRONT): the front corner is crushed down
# by the brow (angry V), a black slit pupil in a burning iris.
GEYE = ["SSSRGG", "GGHPHG", ".GGGSS"]
GEYE_KEYS = {"S": "socket", "R": "eye_rim", "G": "eye_glow", "H": "eye_hot", "P": "pupil"}


def _geye_paint(glow):
    def fn(px, faces, pal, rnd, *_):
        for face, (x, y, w, h) in faces.items():
            if not (w and h) or face not in ("east", "west"):
                continue
            cols = side_cols(face, w)
            for j, row in enumerate(GEYE[:h]):
                for fi, ch in enumerate(row[:w]):
                    if ch == "." or (glow and ch not in "GHP"):
                        continue
                    put(px, x + cols[fi], y + j, pal[GEYE_KEYS[ch]], 1.0, rnd, 2)
    return fn


def geye_fn():
    return {"fn": _geye_paint(False), "glow_fn": _geye_paint(True), "shading": False}


def nostril_fn(px, faces, pal, rnd):
    x, y, w, h = faces["up"]
    for sx in (1, w - 2):
        put(px, x + sx, y + h - 2, pal["nostril"], 1.0, rnd, 2)


# ---------------------------------------------------------------------------------------------------- legs
def leg_paints(mega):
    return {"thigh": scales(back=False, armor=False, cracks=20 if mega else None),
            "shin": scales(tone="leg", back=False, ps=(3, 2)),
            "meta": scales(tone="leg", back=False, ps=(3, 2)), "foot": scales(tone="leg", back=False, ps=(3, 2)),
            "claw": CLAW}


def make_legs(mega):
    th = (10, 13, 5) if mega else (9, 12, 5)
    return [Leg(side, 8 * sx, 6, (13, 12, 9), (-28, 38, -18), 3, thigh=th, shin=(6, 6) if mega else (6, 5),
                meta=(5, 5), foot=(8, 10, 3), claws=(-2.5, 0, 2.5), paints=leg_paints(mega), claw_len=4, dewclaw=True)
            for side, sx in (("left", 1), ("right", -1))]


LEGS = make_legs(False)
H = LEGS[0].H                     # hip height
TAIL = ("tail", "tail2", "tail3")
TAIL_ALL = TAIL + ("blade",)


# ---------------------------------------------------------------------------------------------------- model
def build(mega=False):
    legs = make_legs(mega)
    m = Model(MEGA_SID if mega else SID, DEX, (256, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, [0, H, 6])
    cy = (H + 2) if mega else None            # glowing cracks above this height (mega)
    for lg in legs:
        lg.build(m)
        x = lg.x
        sx = 1 if x > 0 else -1
        tw = lg.thigh[0]
        # powerful thigh: a rounded muscle mass on the outside and the back
        m.get(lg.bones[0]).cubes += [
            Cube([x - tw / 2 + 0.5 * sx, H - 12, 6 - 7], [tw, 14, 13], scales(back=False, armor=False, cracks=cy and H - 8),
                 inflate=0.1)]
        # the hip joint is covered by a shield of armour scales, from which rise the three horns of the flank: a
        # gigantic one in the middle, broad as a blade, rising and curving forward toward the head, and a medium one
        # before and behind it, swept back
        g = 2 if mega else 0
        ox = x + (tw / 2 + 0.5) * sx                       # outer face of the thigh
        m.get(lg.bones[0]).cubes += [
            Cube([ox - (0 if sx > 0 else 2), H - 7, -1], [2, 10, 13], scales(tone="plate", back=False, ps=(3, 3))),
            Cube([ox - (0 if sx > 0 else 2) + 0.6 * sx, H - 4, 1], [2, 8, 9], scales(tone="plate", back=False, ps=(3, 3)),
                 inflate=0.05),
            Cube([ox - (1 if sx > 0 else 0) - 1.5 * sx, H + 1, -1], [1, 3, 13], scales(tone="plate", back=False, ps=(3, 3)))]
        fh = m.bone(f"spk_flank_{lg.side}", lg.bones[0], [x, H, 6])        # (own bone: not counted in the height)
        fh.cubes += horn(
            [ox - 1.5 * sx, H + 2, 6], [(0.3 * sx, 1, 0.1), (0.25 * sx, 1, -0.12), (0.15 * sx, 1, -0.4),
                                       (0.05 * sx, 0.8, -0.8)],
            [9, 9, 8, 7 + g], widths=((5, 8), (4, 7), (3, 5), (1, 3)))
        for z, L in ((0, 12), (10.5, 11)):
            L += g
            d0 = (0.45 * sx, 1, 0.1)
            fh.cubes += horn([ox - 1.5 * sx, H + 2, z], [d0, bend(d0, 0.5), bend(d0, 1.0)],
                                             [round(L * 0.4), round(L * 0.3), L - round(L * 0.4) - round(L * 0.3)],
                                             widths=((3, 4), (2, 3), (1, 1)))
        # spur of navy plates on the knee, calf at the back of the shin
        m.get(lg.bones[1]).cubes += [Cube([x - 2.5, H - 13 - 8, 6 + 1], [5, 7, 2], scales(tone="leg", back=False, ps=(3, 2)))]
        m.get(lg.bones[1]).cubes += horn([x + 0.5 * sx, H - 13.5, 6 - 3], [(0.3 * sx, 0.2, -1), (0.3 * sx, 0.6, -1)],
                                         [2, 2], widths=(2, 1))
    # ------------------------------------------------------------------ trunk: long, horizontal, athletic
    m.bone("torso", "body", [0, H, 6], rotation=[-4, 0, 0], cubes=[
        Cube([-7, H - 7, -6], [14, 15, 22], scales(belly=4, cracks=cy)),
        Cube([-5, H + 8, -4], [10, 2, 18], scales(cracks=cy)),
        Cube([-6, H - 9, -4], [12, 2, 15], scales(belly=2)),
    ])
    cw = 16 if mega else 15
    m.bone("chest", "torso", [0, H + 2, -5], rotation=[7, 0, 0], cubes=[
        Cube([-cw / 2, H - 8, -20], [cw, 17, 16], scales(belly=5, cracks=cy)),
        Cube([-(cw - 4) / 2, H + 9, -18], [cw - 4, 2, 12], scales(cracks=cy)),
        Cube([-(cw - 3) / 2, H - 10, -18], [cw - 3, 2, 12], scales(belly=2)),
    ] + [Cube([(cw / 2 - 0.5) * sx - (1 if sx < 0 else 0), H - 2, -18], [2, 9, 10], scales(cracks=cy))
         for sx in (1, -1)])                                                     # shoulder muscles
    # ------------------------------------------------------------------ dorsal fringe: big slate-blue curved spikes
    def fringe(bone, items):
        cubes = m.get(bone).cubes
        for x, y, z, L in items:
            sx = 1 if x > 0 else (-1 if x < 0 else 0)
            d0 = (0.25 * sx, 1, 0.7)
            L = L + (2 if mega else 0)
            l1, l2 = max(2, round(L * 0.4)), max(2, round(L * 0.35))
            cubes += horn([x, y, z], [d0, bend(d0, 0.6), bend(d0, 1.3)], [l1, l2, max(2, L - l1 - l2)])
    fringe("chest", [(1.5, H + 10, -18, 9), (-1.5, H + 10.5, -14, 11), (1.5, H + 10.5, -10, 13), (-1.5, H + 10.5, -6, 14)])
    fringe("torso", [(1.5, H + 9.5, -2, 15), (-1.5, H + 9.5, 2, 14), (1.5, H + 9.5, 6, 12), (-1.5, H + 9, 10, 10),
                     (1.5, H + 9, 14, 8)])
    for sx in (1, -1):
        d0 = (0.9 * sx, 0.6, 0.6)            # a small spike on each shoulder
        m.get("chest").cubes += horn([(cw / 2 - 0.5) * sx, H + 3, -13], [d0, bend(d0, 0.8)], [3, 3], widths=(2, 1))
    # ------------------------------------------------------------------ arms (small, three claws)
    for side, sx in (("left", 1), ("right", -1)):
        ax = 6.5 * sx
        m.bone(f"arm_{side}", "chest", [ax, H - 3, -15], rotation=[30, 0, -10 * sx], cubes=[
            Cube([ax - 1.5, H - 10, -16.5], [3, 8, 3], scales(back=False, armor=False))] +
            horn([ax + 1.2 * sx, H - 5, -15], [(0.8 * sx, 0.3, 1), (0.5 * sx, 0.1, 1.4)], [3, 3], widths=(2, 1)))
        m.bone(f"forearm_{side}", f"arm_{side}", [ax, H - 9.5, -15], rotation=[-75, 0, 0], cubes=[
            Cube([ax - 1, H - 15, -16], [2, 6, 2], scales(tone="leg", back=False, ps=(3, 2)))] +
            [Cube([ax + ox - 0.5, H - 17, -16], [1, 3, 1], CLAW, rotation=[-25, 0, 0], pivot=[ax, H - 15, -15.5])
             for ox in (-0.8, 0.8)])
    # ------------------------------------------------------------------ neck (thick, spiked)
    nw = 13 if mega else 12
    m.bone("neck", "chest", [0, H + 2, -18], rotation=[24, 0, 0], cubes=[
        Cube([-nw / 2, H - 6, -30], [nw, 14, 13], scales(belly=4, cracks=cy)),
        Cube([-(nw - 4) / 2, H + 8, -28], [nw - 4, 2, 10], scales(cracks=cy)),
    ])
    fringe("neck", [(2, H + 8.5, -27, 6), (-2, H + 8.5, -24.5, 7), (2, H + 9, -22, 8)])
    for sx in (1, -1):
        m.get("neck").cubes += horn([(nw / 2) * sx, H + 3, -25], [(1 * sx, 0.4, 0.7), (0.8 * sx, 0.2, 1.3)], [3, 3],
                                    widths=(2, 1))
    # ------------------------------------------------------------------ head: massive, angular, spiked skull
    hd = lambda **kw: scales(ps=(3, 3), **kw)               # no cracks on the head: the burning eyes stand out
    pl = lambda **kw: scales(ps=(3, 3), tone="plate", **kw)
    m.bone("head", "neck", [0, H + 1, -29], rotation=[-24, 0, 0], cubes=[
        Cube([-5.5, H - 4, -40], [11, 12, 12], pl()),                                                # cranium
        Cube([-4.5, H - 4, -50], [9, 7, 10], pl(post=mouth_fn("upper"),
                                               post_glow=mouth_fn("upper", True) if mega else None)),  # upper jaw
        Cube([-4, H - 4, -54], [8, 6, 4], pl(post=nostril_fn)),                                      # snout tip
        Cube([-3, H + 2, -53], [6, 3, 14], pl(), rotation=[10, 0, 0], pivot=[0, H + 3.5, -39]),     # sloping snout ridge
        Cube([-3.5, H + 7, -40], [7, 2, 11], pl()),                                                 # skull plate
        Cube([-2, H + 9, -38], [4, 1, 8], pl()),                                                    # mid-crest ridge
    ] + [Cube([3 * sx - (3 if sx < 0 else 0), H + 6, -46], [3, 3, 12], pl(), rotation=[0, 0, -10 * sx],
              pivot=[3 * sx, H + 7, -40]) for sx in (1, -1)]
      + [Cube([5.5 * sx - (1 if sx < 0 else 0), H - 3, -40], [1, 4, 7], pl()) for sx in (1, -1)])   # brows, cheek plates
    m.bone("throat", "head", [0, H - 4, -36], cubes=[
        Cube([-3.5, H - 9, -48], [7, 5, 14], {"fn": throat_fn(), "base": "palate",
                                              **({"glow_fn": lambda px, faces, pal, rnd, c: throat_fn(True)(px, faces, pal, rnd)}
                                                 if mega else {})})])
    up = []
    for sx in (1, -1):                          # upper teeth along both sides, pointing down; fangs in front
        for k, z in enumerate((-53, -50.5, -48, -45.5, -43, -40.5)):
            up += tooth([(3.6 if z < -50 else 4.0) * sx, H - 4, z], (0.12 * sx, -1, -0.15), L=4 if k == 1 else (3 if k < 4 else 2))
    for x in (-1.5, 1.5):
        up += tooth([x, H - 4, -53.6], (x * 0.1, -1, -0.4), L=3)
    m.bone("teeth_upper", "head", [0, H - 4, -46], cubes=up)
    # crown of great horns at the back of the skull, spiked brows, cheeks and snout
    cr = []
    big = 1 if mega else 0
    # Lame-Chaos: a far more imposing crown (longer, thicker horns, an extra pair)
    gh = ([7, 7, 9], (5, 4, 2)) if mega else ([5, 5, 6], (4, 3, 2))
    sh = ([5, 5, 6], (4, 3, 2)) if mega else ([4, 3, 4], (3, 2, 1))
    for sx in (1, -1):
        cr += horn([4.6 * sx, H + 7, -32.5], [(0.7 * sx, 1, 0.1), (0.45 * sx, 1, 0.55), (0.2 * sx, 0.6, 1)],
                   gh[0], widths=gh[1])                                                                  # great horns
        cr += horn([2.5 * sx, H + 8.5, -31.5], [(0.4 * sx, 1, 0.8), (0.3 * sx, 0.6, 1.3)], [3 + big, 3 + 2 * big],
                   widths=(2 + big, 1))
        d = (1 * sx, 0.45, 0.9)
        cr += horn([5.2 * sx, H + 6, -30.5], [d, bend(d, 0.4), bend(d, 0.9)], sh[0], widths=sh[1])     # side horns
        if mega:                                                                                     # extra front pair
            d = (0.8 * sx, 1, -0.2)
            cr += horn([4.4 * sx, H + 8, -38], [d, bend(d, 0.6), bend(d, 1.3)], [4, 4, 5], widths=(3, 2, 1))
        d = (0.6 * sx, 0.0, 1)
        cr += horn([4.6 * sx, H + 1, -29], [d, bend(d, 0.5)], [3, 3 + big], widths=(2, 1))              # nape spikes
        for z, L in ((-42.5, 4), (-38.5, 5)):                                                         # brow spikes
            d = (0.5 * sx, 1, 0.8)
            cr += horn([5 * sx, H + 8.5, z], [d, bend(d, 0.8)], [2, L - 2 + 2 * big], widths=(2, 1))
        d = (1 * sx, -0.1, 0.9)
        cr += horn([5.4 * sx, H - 1, -37.5], [d, bend(d, 0.5)], [3, 3 + big], widths=(2, 1))            # cheek spikes
        cr += horn([4.6 * sx, H - 2.5, -45], [(1 * sx, 0, 0.6)], [3 + big], widths=(1,))
        cr += horn([2 * sx, H + 4, -48], [(0.3 * sx, 1, 0.5)], [2 + big], widths=(1,))                   # snout bumps
    d = (0, 0.5, 1)
    cr += horn([0, H + 9, -30], [d, bend(d, 0.5), bend(d, 1.0)], [5, 4, 5] if mega else [4, 3, 4],
               widths=(4, 3, 1) if mega else (3, 2, 1))
    cr += horn([0, H + 4.5, -45], [(0, 1, 0.5)], [2 + big], widths=(1,))
    m.bone("crest", "head", [0, H + 7, -32], cubes=cr)
    # eyes: under the brow ridges
    m.bone("eyes", "head", [0, H + 3.5, -34])
    for side, sx in (("left", 1), ("right", -1)):
        ex = 5.55 * sx
        cubes = [Cube([ex, H + 2.5, -38], [0, 3, 6], geye_fn())]
        if mega:
            cubes.append(Cube([ex + 0.05 * sx, H + 3.5, -33], [0, 2, 10], {"fn": trail_fn, **GLOW}))
        m.bone(f"eye_{side}", "eyes", [ex, H + 4, -34.5], cubes=cubes)
    for sx in (1, -1):                         # heavy brow overhanging the eye, cheekbone under it
        m.get("head").cubes += [Cube([5.5 * sx - (1 if sx < 0 else 0), H + 5.5, -39.5], [1, 2, 9], pl()),
                                Cube([5.5 * sx - (1 if sx < 0 else 0), H + 0.5, -39], [1, 2, 8], pl())]
    # fire in the throat (stretched into a jet by the special attack)
    m.bone("breath", "head", [0, H - 5, -48], cubes=[Cube([-2, H - 7, -49], [4, 4, 1], {"fn": breath_fn, **GLOW})])
    # ------------------------------------------------------------------ lower jaw: long and deep, jagged underneath
    jp = dict(ps=(3, 3), tone="plate", back=False, post=mouth_fn("jaw"), post_glow=mouth_fn("jaw", True) if mega else None)
    m.bone("jaw", "head", [0, H - 4, -31], cubes=[
        Cube([-5, H - 10, -50], [10, 6, 20], scales(**jp)),
        Cube([-4.5, H - 10, -54], [9, 6, 4], scales(**jp)),
        Cube([-4.5, H - 12, -42], [9, 2, 10], scales(tone="plate", back=False, ps=(3, 3))),
    ])
    lo = []
    for sx in (1, -1):
        for k, z in enumerate((-52.5, -50, -47.5, -45, -42.5, -40)):
            lo += tooth([(3.4 if z < -50 else 4.2) * sx, H - 4.5, z], (0.12 * sx, 1, -0.15), L=3 if k == 1 else 2)
        for z, L in ((-50, 3), (-45, 3)):                                                             # jagged underside
            lo += horn([3.5 * sx, H - 10, z], [(0.3 * sx, -1, 0.6)], [L], widths=(1,))
        for x0, L in ((1.8, 4), (4, 3)):                                                              # chin beard
            lo += horn([x0 * sx, H - 10, -53], [(0.15 * sx, -1, 0.2), (0.1 * sx, -0.8, 0.8)], [2, L - 1],
                       widths=(2, 1))
        lo += horn([3.5 * sx, H - 12, -36], [(0.3 * sx, -1, 0.7)], [4], widths=(1,))
        lo += horn([5 * sx, H - 7, -33], [(1 * sx, -0.4, 0.9), (0.7 * sx, -0.5, 1.3)], [3, 3], widths=(2, 1))
    m.bone("teeth_lower", "jaw", [0, H - 4.5, -46], cubes=lo)
    # ------------------------------------------------------------------ tail: long, held out behind, its second half
    # flattened into a colossal scimitar (cutting edge underneath, jagged crystals along its back)
    segs = [(11, 11, 10, 6), (10, 10, 9, 0), (8, 8, 8, -2)]
    parent, z, yc = "torso", 15, H + 2
    for i, (w, hgt, ln, rot) in enumerate(segs):
        name = TAIL[i]
        m.bone(name, parent, [0, yc, z], rotation=[rot, 0, 0], cubes=[
            Cube([-w / 2, yc - hgt / 2, z - 0.5], [w, hgt, ln + 1], scales(belly=max(2, hgt // 4), cracks=cy and yc - 2,
                                                                         ps=(3, 3)))])
        cubes = m.get(name).cubes
        for k in range(ln // 3):                    # two rows of dorsal spikes, shrinking toward the blade
            zz = z + 1.5 + 3 * k
            sxk = 1 if k % 2 == 0 else -1
            L = 8 - 2 * i + big
            d0 = (0.35 * sxk, 1, 0.9)
            cubes += horn([1.5 * sxk, yc + hgt / 2 - 0.5, zz], [d0, bend(d0, 0.8)], [max(2, L // 2), max(2, L - L // 2)],
                          widths=(2, 1))
        if i == 2:                                  # the blade begins: a keel growing under the tail
            for k in range(4):
                kh = 1 + k
                cubes.append(Cube([-1, yc - hgt / 2 - kh + 0.5, z + 2 * k], [2, kh, 3], blade_paint(mega)))
        parent, z = name, z + ln
    ch0 = rim_height(0)
    y0 = yc + hgt / 2 - ch0                         # spine line: the rim continues the tail's back
    m.bone("blade", "tail3", [0, y0, z], rotation=[-4, 0, 0])
    bl, heat = [], []
    n = int(BLADE_LEN / BLADE_DS)
    for k in range(n):
        s = k * BLADE_DS
        py, pz, phi = blade_point(y0, z, s)
        rot = [round(math.degrees(phi), 2), 0, 0]
        piv = [0, py, pz]
        wd = max(1, round(blade_width(s + BLADE_DS / 2)))
        ch = rim_height(s)
        L = BLADE_DS + 1 if k < n - 1 else BLADE_DS
        inf = 0.02 if k % 2 else None
        rw = 5 if s < 16 else (4 if s < 36 else 3)
        bl.append(Cube([-rw / 2, py, pz], [rw, ch, L], {"fn": rim_paint, "base": "rim"}, rotation=rot, pivot=piv,
                       inflate=inf))
        bl.append(Cube([-1, py - wd, pz], [2, wd, L], blade_paint(mega), rotation=rot, pivot=piv, inflate=inf))
        if wd >= 6:
            bl.append(Cube([-1.5, py - round(wd * 0.45), pz], [3, round(wd * 0.45), L], blade_paint(mega), rotation=rot,
                           pivot=piv, inflate=inf))
        bl.append(Cube([-0.5, py - wd - 1, pz], [1, 1, L], edge_paint(mega), rotation=rot, pivot=piv, inflate=inf))
        if s < BLADE_LEN - 6:                          # jagged crystals along the back of the blade
            Lc = (5 if k % 2 else 8) + (2 if 6 < s < 40 and k % 2 == 0 else 0) + big
            d = (0, 1, 1.3)
            cm = math.radians(rot[0])
            dd = (0, d[1] * math.cos(cm) + d[2] * math.sin(cm), -d[1] * math.sin(cm) + d[2] * math.cos(cm))
            bl += horn([0, py + ch - 0.5, pz + 1.5], [dd, bend(dd, 0.5), bend(dd, 1.0)],
                       [max(2, Lc // 3), max(2, Lc // 3), max(2, Lc - 2 * (Lc // 3))],
                       widths=(3, 2, 1) if k % 2 == 0 else (2, 2, 1), paints=(CRYSTAL_ROOT, CRYSTAL_TIP, CRYSTAL_TIP))
        if not mega:
            for sx in (1, -1):
                heat.append(Cube([1.06 * sx, py - wd - 1, pz], [0, wd + 1, L], {"fn": heat_fn, **GLOW}, rotation=rot,
                                 pivot=piv))
    m.get("blade").cubes = bl
    if heat:
        m.bone("blade_heat", "blade", [0, y0, z], cubes=heat)
    # ------------------------------------------------------------------ mega: red-pink mist, flames and embers
    if mega:
        mist = [("aura_neck", "neck", [0, H + 11, -23], [0, 12, 14]),
                ("aura_chest", "chest", [0, H + 17, -10], [0, 16, 20]),
                ("aura_back", "torso", [0, H + 18, 6], [0, 18, 24]),
                ("aura_tail", "tail2", [0, H + 14, 30], [0, 14, 18])]
        for k, (name, par, pv, size) in enumerate(mist):
            x0, yy, z0 = pv
            w, h, d = size
            m.bone(name, par, pv, cubes=[
                Cube([x0, yy - 5, z0 - d / 2], [0, h, d], smoke_fn(70 + 3 * k)),
                Cube([x0 - d * 0.35, yy - 5, z0], [int(d * 0.7), h - 2, 0], smoke_fn(71 + 3 * k))])
        # flames rising from the back of the blade, between the crystals
        for j, sf in enumerate(FLAME_S):
            py, pz, phi = blade_point(y0, z, sf)
            ry = py + rim_height(sf) - 1
            fh = 7 + (j % 3) * 2
            m.bone(f"flame_{j}", "blade", [0, ry, pz], rotation=[round(math.degrees(phi), 1) - 20, 0, 0], cubes=[
                Cube([0, ry, pz - 3], [0, fh, 7], flame_fn(90 + j)),
                Cube([-2.5, ry, pz], [5, fh - 2, 0], flame_fn(120 + j))])
        for k, (par, pv) in enumerate((("blade", (0, y0 + 4, z + 6)), ("blade", (2, y0 + 5, z + 16)),
                                       ("blade", (-2, y0 + 5, z + 26)), ("blade", (1, y0 + 6, z + 36)),
                                       ("blade", (-1, y0 - 6, z + 12)), ("blade", (2, y0 - 8, z + 30)),
                                       ("torso", (5, H + 12, 2)), ("torso", (-5, H + 12, 8)), ("chest", (4, H + 14, -12)),
                                       ("chest", (-4, H + 13, -8)), ("jaw", (3, H - 4, -50)), ("jaw", (-3, H - 4, -46)))):
            x0, yy, z0 = pv
            m.bone(f"ember_{k}", par, list(pv), cubes=[Cube([x0 - 0.5, yy - 0.5, z0 - 0.5], [1, 1, 1],
                                                            {"base": "ember_hot" if k % 3 == 0 else "ember", **GLOW})])
    m.pack()
    return m


MEGA_ONLY = ("aura_", "flame_", "ember_")
AURA = ("aura_neck", "aura_chest", "aura_back", "aura_tail")
EMBERS = tuple(f"ember_{k}" for k in range(12))
FLAMES = tuple(f"flame_{j}" for j in range(len(FLAME_S)))
SPIN_DIR = 1            # the tail-blade spin turns the body to its left
RAISED = {"tail": 28, "tail2": 32, "tail3": 30, "blade": 34}     # threat pose: the blade arched over the back


# ---------------------------------------------------------------------------------------------------- animation helpers
def heat(pts):
    """Red-hot blade (base form): the overlay is switched on and off at once (linear keys, a jump of 0.02 s; a growing
    scale would show a shrunken copy of the glow near the blade's root), from (time, 0|1) points."""
    out = {}
    prev = None
    for t, v in pts:
        v = 1 if v >= 0.5 else 0
        if prev is not None and v != prev and t > 0.02:
            out[str(round(t - 0.02, 3))] = [prev, prev, prev]
        out[str(round(t, 3))] = [v, v, v]
        prev = v
    return {"blade_heat": {"scale": out}}


def mist_flare(pts):
    """The red-pink mist swells (mega)."""
    return {name: keys(scale={t: [1 + (f - 1) * 0.7, f, 1 + (f - 1) * 0.7] for t, f in pts}) for name in AURA}


def fx_loop(L, mega, intensity=1.0, hot=0.0):
    """Sampled loop of the effect bones for a looping animation of length L: the blade's heat overlay stays off (base)
    or the mist swirls, the flames flicker along the edge and embers drift off the blade (mega)."""
    f = 360.0 / L
    if not mega:
        return heat([(0, hot), (L, hot)])
    fns = {}
    for k, name in enumerate(AURA):
        fns[name] = {"rotation": lambda t, k=k: [5 * S(f * t + 70 * k), 8 * S(f * t + 45 * k), 0],
                     "scale": lambda t, k=k: [intensity * (1 + 0.1 * S(f * 2 * t + 50 * k)),
                                              intensity * (1 + 0.18 * S(f * 3 * t + 40 * k)),
                                              intensity * (1 + 0.1 * S(f * 2 * t + 50 * k))],
                     "position": lambda t, k=k: [0, 0.8 * S(f * 2 * t + 30 * k), 0]}
    for j, name in enumerate(FLAMES):
        fns[name] = {"scale": lambda t, j=j: [intensity * (1 + 0.15 * S(f * 5 * t + 77 * j)),
                                              intensity * (0.85 + 0.35 * abs(S(f * 4 * t + 53 * j))),
                                              intensity * (1 + 0.15 * S(f * 5 * t + 31 * j))]}
    out = sampled(L, fns, step=0.1)
    out.update(DJ.embers(L))
    return out


def flames_flare(L, pts):
    """Flames on the edge flare up (mega): (time, factor) points."""
    return {name: keys(scale={t: [1 + (v - 1) * 0.6, v, 1 + (v - 1) * 0.6] for t, v in pts}) for name in FLAMES}


def blade_sway(t, f, amp=1.0, ph=0):
    return [1.5 * amp * S(f * t + ph), 0, 0]


# ---------------------------------------------------------------------------------------------------- animations
def idle_anim(mega):
    """Calm predator: slow heavy breathing, the head carried low swinging and tilting as it scans, a few sniffs, the
    great blade rocking gently over its back; once per loop it snorts a puff of fire and gnashes its teeth."""
    L, k = 8.0, (1.3 if mega else 1.0)
    f = 360 / L

    def jaw(t):
        base = 3 * k + 2.5 * S(2 * f * t - 60)
        return ramp(t, [(0, base), (5.0, base), (5.3, 22), (5.45, 0), (5.6, 14), (5.75, 0), (6.1, base), (8, base)]) \
            if 4.9 < t < 6.2 else base

    def sniff(t):
        return 2.4 * S(1440 * (t - 2.3)) * bump(t, 2.7, 0.45)
    fns = {
        "torso": {"rotation": lambda t: [1.0 * k * S(2 * f * t), 0, 1.4 * k * S(f * t + 20)]},
        "chest": {"rotation": lambda t: [-0.8 * k * S(2 * f * t - 20) + 1.5 * bump(t, 5.4, 0.4), 0, -0.8 * S(f * t + 20)],
                  "scale": lambda t: [1, 1 + 0.016 * k * S(2 * f * t), 1 + 0.012 * k * S(2 * f * t)]},
        "neck": {"rotation": lambda t: [1.5 * S(2 * f * t - 40) + 3 * bump(t, 2.7, 0.6) - 4 * bump(t, 5.35, 0.35),
                                        10 * k * S(f * t) + 3 * S(3 * f * t + 30), 2 * S(f * t + 60)]},
        "head": {"rotation": lambda t: [-1 * S(2 * f * t - 60) + sniff(t) - 6 * bump(t, 5.4, 0.3),
                                        5 * S(f * t + 40), 4 * k * S(f * t + 80)]},
        "jaw": {"rotation": lambda t: [jaw(t), 0, 0]},
        "eye_left": {"scale": lambda t: [1, 1 - 0.3 * bump(t, 5.4, 0.35), 1]},
        "eye_right": {"scale": lambda t: [1, 1 - 0.3 * bump(t, 5.4, 0.35), 1]},
        "arm_left": {"rotation": lambda t: [3 * S(2 * f * t), 0, 0]},
        "arm_right": {"rotation": lambda t: [3 * S(2 * f * t + 40), 0, 0]},
        "breath": {"scale": lambda t: [1 + 0.15 * S(2 * f * t) + 1.2 * bump(t, 5.3, 0.25),
                                       1 + 0.15 * S(2 * f * t) + 1.2 * bump(t, 5.3, 0.25), 1 + 7 * bump(t, 5.3, 0.22)]},
        "blade": {"rotation": lambda t: blade_sway(t, f, 1.2, 200)},
    }
    for i, tb in enumerate(TAIL):
        fns[tb] = {"rotation": lambda t, i=i: [1.2 * S(2 * f * t - 40 * i) - 2 * bump(t, 5.5 + 0.08 * i, 0.4),
                                               (3 + 1.5 * i) * S(f * t - 35 * i), 0]}
    b = sampled(L, fns, step=0.1, extra_steps=[5.25, 5.3, 5.35, 5.4, 5.45, 5.55, 5.6, 5.65, 5.7, 5.75])
    b.update(fx_loop(L, mega))
    return {"loop": True, "animation_length": L, "bones": b}


def battle_anim(mega):
    """Battle stance: crouched low, weight rolling from side to side, head low and thrust at the foe with the jaws
    open in a growl; the blade is raised higher and swings menacingly from side to side, like a sword held at guard;
    twice per loop it snaps its jaws and flicks the blade."""
    L, k = 4.0, (1.3 if mega else 1.0)
    legs = make_legs(mega)
    crouch = -3.5

    def jaw(t):
        base = 14 * k + 1.5 * S(2000 * t)
        for t0 in (1.0, 3.0):
            if t0 - 0.3 < t < t0 + 0.4:
                return ramp(t, [(t0 - 0.3, base), (t0 - 0.1, 32), (t0, 2), (t0 + 0.4, base)])
        return base
    fns = {
        "torso": {"rotation": lambda t: [5 + 1.5 * k * S(180 * t), 0, 3 * k * S(90 * t)]},
        "chest": {"rotation": lambda t: [3 + 1.5 * S(180 * t + 40), 0, -2 * S(90 * t)],
                  "scale": lambda t: [1, 1 + 0.025 * k * S(180 * t), 1 + 0.02 * S(180 * t)]},
        "neck": {"rotation": lambda t: [-1 + 3 * S(180 * t - 30) - 3 * bump(t, 1.0, 0.3) - 3 * bump(t, 3.0, 0.3),
                                        10 * k * S(90 * t + 20), 3 * S(90 * t)]},
        "head": {"rotation": lambda t: [-21 + 2 * S(180 * t - 60) + 2 * bump(t, 1.0, 0.18) + 2 * bump(t, 3.0, 0.18),
                                        6 * S(90 * t + 60), 5 * S(90 * t + 90)]},
        "jaw": {"rotation": lambda t: [jaw(t), 0, 0]},
        "eye_left": {"scale": lambda t: [1.05, 0.75, 1]}, "eye_right": {"scale": lambda t: [1.05, 0.75, 1]},
        "arm_left": {"rotation": lambda t: [-20 + 6 * S(180 * t), 0, -10]},
        "arm_right": {"rotation": lambda t: [-20 + 6 * S(180 * t + 60), 0, 10]},
        "forearm_left": {"rotation": lambda t: [-15 + 12 * S(360 * t), 0, 0]},
        "forearm_right": {"rotation": lambda t: [-15 + 12 * S(360 * t + 90), 0, 0]},
        "breath": {"scale": lambda t: [1.2 + 0.2 * S(360 * t), 1.2 + 0.2 * S(360 * t), 1]},
        "blade": {"rotation": lambda t: [RAISED["blade"] + 3 * S(180 * t + 120) + 5 * bump(t, 1.15, 0.25)
                                         + 5 * bump(t, 3.15, 0.25), 0, 0]},
    }
    for i, tb in enumerate(TAIL):
        fns[tb] = {"rotation": lambda t, i=i, tb=tb: [RAISED[tb] + 2 * S(180 * t - 40 * i) - 3 * bump(t, 1.05, 0.25),
                                                      (4 + 2 * i) * k * S(90 * t - 50 * i), 0]}
    b = sampled(L, fns, step=0.05)
    for bn, r in leg_pose(legs, crouch).items():
        b[bn] = {"rotation": r}
    b["body"] = {"position": [0, crouch, 0]}
    b.update(fx_loop(L, mega, intensity=1.15))
    return {"loop": True, "animation_length": L, "bones": b}


def cry(mega=False):
    """Roar: it draws breath (chest swelling, head dipping a little), braces on its legs and roars straight ahead, head
    level and jaws gaping, the head shaking slightly from side to side; the blade is lifted and quivers (base: it
    flashes red-hot), the flames roar up (mega); it closes its jaws with a snort."""
    L = 2.8
    k = 1.3 if mega else 1.0
    b = timeline(LEGS, L, [(0, 0, 0), (0.45, -1.2, 0), (0.75, -2.4, 0), (2.2, -2.2, 0), (2.6, 0, 0), (L, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.45: [3, 0, 0], 0.75: [1, 0, 0], 1.2: [1, 0, 1.5], 1.7: [1, 0, -1.5],
                                2.2: [1, 0, 0], L: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.45: [-3, 0, 0], 0.75: [2, 0, 0], 2.2: [2, 0, 0], L: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.45: [1.05, 1.07, 1.04], 0.75: [1, 1, 1], L: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.45: [3, 0, 0], 0.75: [-13, 0, 0], 1.1: [-13, 5 * k, 0], 1.5: [-13, -5 * k, 0],
                               1.9: [-13, 4 * k, 0], 2.2: [-10, 0, 0], 2.6: [0, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.45: [4, 0, 0], 0.75: [-2, 0, 0], 0.8: [tremble(-2, 2200, 1.6 * k), 0, 3],
                               1.2: [tremble(-2, 2200, 1.6 * k), 3, -4], 1.6: [tremble(-2, 2200, 1.6 * k), -3, 4],
                               2.0: [tremble(-1, 2200, 1.6 * k), 2, -2], 2.35: [0, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.45: [6, 0, 0], 0.75: [44, 0, 0], 0.8: [tremble(46, 1900, 3), 0, 0],
                              2.1: [tremble(44, 1900, 3), 0, 0], 2.4: [3, 0, 0], L: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.45: [10, 0, 0], 0.75: [-35, 0, -16 * sx], 2.2: [-32, 0, -14 * sx], L: [0, 0, 0]})
        b[f"forearm_{side}"] = keys(rotation={0: [0, 0, 0], 0.75: [-30, 0, 0], 1.3: [-12, 0, 0], 1.8: [-28, 0, 0],
                                              2.2: [-18, 0, 0], L: [0, 0, 0]})
    for i, tb in enumerate(("tail", "tail2", "tail3")):
        r = RAISED[tb] * 0.6
        b[tb] = keys(rotation={0: [0, 0, 0], 0.5 + 0.05 * i: [-3, 0, 0], 0.9 + 0.05 * i: [r, 0, 0],
                               2.2: [r - 2, 0, 0], 2.65: [-1, 0, 0], L: [0, 0, 0]})
    b["blade"] = keys(rotation={0: [0, 0, 0], 0.75: [-4, 0, 0], 1.0: [tremble(10, 2600, 2.5), 0, 0],
                                2.2: [tremble(8, 2600, 2.5), 0, 0], 2.7: [-1, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.7: [1, 1, 1], 0.8: [1.15, 0.5, 1], 2.2: [1.15, 0.5, 1], 2.4: [1, 1, 1], L: [1, 1, 1]})
    b["breath"] = keys(scale={0: [1, 1, 1], 0.75: [1, 1, 1], 0.9: [1.8, 1.8, 1], 2.1: [1.6, 1.6, 1], 2.4: [1, 1, 1],
                              2.5: [2.0, 2.0, 5], 2.65: [1, 1, 1], L: [1, 1, 1]})
    if mega:
        b.update(mist_flare([(0, 1), (0.45, 0.9), (0.9, 1.6), (2.2, 1.5), (2.6, 1.0), (L, 1)]))
        b.update(flames_flare(L, [(0, 1), (0.75, 1), (0.95, 1.8), (2.2, 1.6), (2.6, 1), (L, 1)]))
        b.update(DJ.embers(L, loop=False))
    else:
        b.update(heat([(0, 0), (0.85, 0), (0.9, 1), (2.2, 1), (2.6, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


def physical(mega=False):
    """Queue-Lame: crouches and coils, turning away, then whirls around on itself in a full circle with the tail
    unrolled and the blade swept flat along the ground like a scythe (edge first), the body leaving the ground; it
    lands, the blade glowing red-hot from the blow (mega: the flames burst), and raises it back over its back."""
    L = 2.0
    k = 1.25 if mega else 1.0
    t0, t1 = 0.4, 1.0                         # the spin
    b = ik_track(LEGS, L, [(0, 0, 0), (0.3, -4.0, 0), (t0, -3.5, 0), (0.55, 1.5, 0), (0.85, 1.5, 0), (t1, -3.0, 0),
                           (1.35, -1.5, 0), (L, 0, 0)])

    def spin(t):
        if t <= t0:
            return -30 * SPIN_DIR * smooth(t / t0)
        if t <= t1:
            return SPIN_DIR * (-30 + 390 * smooth((t - t0) / (t1 - t0)))
        return SPIN_DIR * 360

    def lift(t):                              # hop during the spin
        return 4.5 * bump(t, (t0 + t1) / 2, (t1 - t0) / 2 + 0.05)
    hips = b["body"]["position"]
    for ts, v in hips.items():
        t = float(ts)
        hips[ts] = kf([0, round(v["post"][1] + lift(t), 3), 0])
    b["body"]["rotation"] = {}
    n = int(round(L / 0.025))
    for i in range(n + 1):
        t = round(i * 0.025, 3)
        b["body"]["rotation"][str(t)] = kf([0, round(spin(t), 2), 0])
    # the spin ends a full turn round and holds 360 to the end (same orientation as 0 when the idle takes over)
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.3: [12, -20 * SPIN_DIR, 0], t0: [12, -24 * SPIN_DIR, 0],
                               0.5: [-2, 10 * SPIN_DIR, -75 * SPIN_DIR], 0.9: [-2, 10 * SPIN_DIR, -75 * SPIN_DIR],
                               t1: [2, 0, -30 * SPIN_DIR], 1.3: [6, -8 * SPIN_DIR, 0], 1.6: [2, 0, 0], L: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.3: [8, -12 * SPIN_DIR, 0], t0: [8, -14 * SPIN_DIR, 0],
                                0.5: [0, 8 * SPIN_DIR, 0], 0.9: [0, 8 * SPIN_DIR, 0], t1: [2, 0, 0], 1.35: [4, -6 * SPIN_DIR, 0],
                                1.65: [1, 0, 0], L: [0, 0, 0]})
    b["tail3"] = keys(rotation={0: [0, 0, 0], t0: [6, -8 * SPIN_DIR, 0], 0.5: [0, 6 * SPIN_DIR, 0], 0.9: [0, 6 * SPIN_DIR, 0],
                                t1: [2, 0, 0], 1.4: [3, -4 * SPIN_DIR, 0], 1.7: [0, 0, 0], L: [0, 0, 0]})
    b["blade"] = keys(rotation={0: [0, 0, 0], t0: [4, 0, 0], 0.5: [0, 0, 0], 0.9: [0, 0, 0], t1: [2, 0, 0],
                                1.45: [-3, 0, 0], 1.75: [1, 0, 0], L: [0, 0, 0]})
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.3: [6, 0, -4 * SPIN_DIR], t0: [6, 0, -4 * SPIN_DIR], 0.55: [2, 0, 8 * SPIN_DIR],
                                0.9: [2, 0, 8 * SPIN_DIR], t1: [6, 0, 0], 1.4: [2, 0, 0], L: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.3: [-6, -14 * SPIN_DIR, 0], t0: [-6, -16 * SPIN_DIR, 0],
                               0.55: [-4, 20 * SPIN_DIR, 0], 0.9: [-4, 20 * SPIN_DIR, 0], t1: [-8, 0, 0], 1.5: [-4, 0, 0],
                               L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.3: [-8, -10 * SPIN_DIR, 0], t0: [-8, -10 * SPIN_DIR, 0],
                               0.55: [-4, 12 * SPIN_DIR, 0], 0.9: [-4, 12 * SPIN_DIR, 0], t1: [-10, 0, 0],
                               1.15: [tremble(-8, 2200, 2.5), 0, 0], 1.5: [-6, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.3: [14, 0, 0], t0: [20, 0, 0], 0.55: [6, 0, 0], 0.9: [6, 0, 0],
                              t1: [30, 0, 0], 1.15: [tremble(30, 1900, 3), 0, 0], 1.5: [10, 0, 0], L: [0, 0, 0]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], t0: [-30, 0, -10 * sx], t1: [-35, 0, -14 * sx], 1.5: [-10, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.3: [1.1, 0.55, 1], 1.4: [1.1, 0.55, 1], L: [1, 1, 1]})
    if mega:
        b.update(flames_flare(L, [(0, 1), (t0, 1.2), (0.55, 1.9), (0.95, 1.9), (1.4, 1.3), (L, 1)]))
        b.update(mist_flare([(0, 1), (t0, 1.2), (0.7, 1.6), (1.3, 1.2), (L, 1)]))
        b.update(DJ.embers(L, loop=False))
    else:
        b.update(heat([(0, 0), (0.6, 0), (0.75, 1), (1.6, 1), (1.85, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


def special(mega=False):
    """Fire breath: rears up and draws in (the fire glows in its throat, the chest swells), then thrusts the head
    forward and spews a jet of flame that sweeps from side to side, the body braced; the flames die down."""
    L = 2.6
    reach = 44 if mega else 36
    b = timeline(LEGS, L, [(0, 0, 0), (0.7, 1.2, 0), (0.95, -1.0, 0), (2.1, -0.8, 0), (L, 0, 0)], step=0.05)
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.7: [-10, 0, 0], 0.95: [5, 0, 0], 2.1: [4, 0, 0], L: [0, 0, 0]})
    b["chest"] = keys(rotation={0: [0, 0, 0], 0.7: [-7, 0, 0], 0.95: [4, 0, 0], 2.1: [4, 0, 0], L: [0, 0, 0]},
                      scale={0: [1, 1, 1], 0.7: [1.06, 1.08, 1.04], 0.95: [1, 1, 1], L: [1, 1, 1]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.7: [-24, 0, 0], 0.95: [-15, 0, 0], 1.3: [-15, 14, 0], 1.7: [-15, -14, 0],
                               2.1: [-15, 0, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.7: [-20, 0, 0], 0.95: [tremble(-4, 2400, 1.6), 0, 0],
                               2.1: [tremble(-4, 2400, 1.6), 0, 0], 2.35: [-3, 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.45: [10, 0, 0], 0.7: [18, 0, 0], 0.95: [30, 0, 0], 2.1: [28, 0, 0],
                              2.3: [tremble(12, 1900, 3), 0, 0], 2.5: [3, 0, 0], L: [0, 0, 0]})
    b["breath"] = keys(scale={0: [1, 1, 1], 0.3: [1.4, 1.4, 1], 0.45: [1.1, 1.1, 1], 0.6: [1.7, 1.7, 1], 0.75: [1.3, 1.3, 1],
                              0.9: [2.0, 2.0, 2], 1.05: [2.2, 2.2, reach], 1.95: [2.0, 2.0, reach],
                              2.15: [0.7, 0.7, reach * 0.6], 2.25: [0.4, 0.4, 1], L: [1, 1, 1]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.7: [-30, 0, -14 * sx], 2.1: [-28, 0, -12 * sx], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.7: [1.1, 0.5, 1], 2.1: [1.1, 0.5, 1], L: [1, 1, 1]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.7: [6, 0, 0], 0.95: [-4, 0, 0], 1.3: [-4, 8, 0], 1.7: [-4, -8, 0], L: [0, 0, 0]})
    b["blade"] = keys(rotation={0: [0, 0, 0], 0.7: [6, 0, 0], 1.0: [-3, 0, 0], 2.1: [-3, 0, 0], L: [0, 0, 0]})
    if mega:
        b.update(mist_flare([(0, 1), (0.7, 1.4), (0.95, 1.7), (2.0, 1.5), (2.4, 1), (L, 1)]))
        b.update(flames_flare(L, [(0, 1), (0.7, 1.4), (1.0, 1.8), (2.0, 1.6), (2.4, 1), (L, 1)]))
        b.update(DJ.embers(L, loop=False))
    else:
        b.update(heat([(0, 0), (0.8, 0), (0.95, 1), (2.1, 1), (2.35, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


SHARPEN = {"torso": [2, -21, 0], "chest": [0, -21, 0], "neck": [-4, -31, 0], "head": [4, -30, 19], "jaw": [22, 0, 0],
           "tail": [-6, 50, 0], "tail2": [-6, 50, 0], "tail3": [-6, 50, 0], "blade": [0, 15, 0]}
"""Sharpening pose (found by a search): the body curls into a C, the tail sweeps round along the left flank (+X) and
the head turns back to take the middle of the blade crosswise between its jaws."""


def status(mega=False):
    """Sharpening (status moves, Affûtage / Danse-Lames): it curls its body, sweeps the tail round along its flank and
    takes the blade crosswise between its jaws; then it draws the blade back and forth through its clenched teeth,
    the head grinding along, sparks flying; the blade turns red-hot; it lets go and swings the tail back."""
    L = 3.0
    b = timeline(LEGS, L, [(0, 0, 0), (0.6, -1.5, 0), (2.4, -1.2, 0), (L, 0, 0)], step=0.05)
    t_in, t_out = 0.7, 2.4
    for bn, r in SHARPEN.items():
        if bn == "jaw":
            continue
        d = 0.06 * ("tail", "tail2", "tail3", "blade").index(bn) if bn.startswith(("tail", "blade")) else 0
        b[bn] = keys(rotation={0: [0, 0, 0], 0.35 + d: [v * 0.45 for v in r], t_in + d: r, t_out: r,
                               t_out + 0.35 + d: [v * 0.25 for v in r], L: [0, 0, 0]})
    # grinding: the tail draws the blade back and forth through the jaws, the head follows a little
    saw = lambda amp, ph=0: f"math.sin((q.anim_time-{t_in})*720+{ph})*{amp}"
    for bn in ("tail", "tail2", "tail3"):
        r = SHARPEN[bn]
        b[bn]["rotation"][str(round(t_in + 0.2, 2))] = kf([r[0], f"{r[1]}+{saw(5)}", r[2]])
        b[bn]["rotation"][str(round(t_out - 0.15, 2))] = kf([r[0], f"{r[1]}+{saw(5)}", r[2]])
    r = SHARPEN["head"]
    b["head"]["rotation"][str(round(t_in + 0.2, 2))] = kf([f"{r[0]}+{saw(2, 90)}", f"{r[1]}+{saw(3)}", r[2]])
    b["head"]["rotation"][str(round(t_out - 0.15, 2))] = kf([f"{r[0]}+{saw(2, 90)}", f"{r[1]}+{saw(3)}", r[2]])
    for bn in b:
        if isinstance(b[bn].get("rotation"), dict):
            b[bn]["rotation"] = dict(sorted(b[bn]["rotation"].items(), key=lambda kv: float(kv[0])))
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.4: [22, 0, 0], t_in: [22, 0, 0], 0.85: [16, 0, 0],
                              t_out - 0.1: [16, 0, 0], t_out + 0.1: [26, 0, 0], 2.7: [4, 0, 0], L: [0, 0, 0]})
    b["jaw"]["rotation"]["1.0"] = kf([f"16+math.sin(q.anim_time*1440)*2", 0, 0])
    b["jaw"]["rotation"]["2.2"] = kf([f"16+math.sin(q.anim_time*1440)*2", 0, 0])
    b["jaw"]["rotation"] = dict(sorted(b["jaw"]["rotation"].items(), key=lambda kv: float(kv[0])))
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.5: [-20, 0, -10 * sx], t_out: [-20, 0, -10 * sx], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.6: [1, 0.55, 1], t_out: [1, 0.55, 1], 2.6: [1, 1, 1], L: [1, 1, 1]})
    b["breath"] = keys(scale={0: [1, 1, 1], 2.5: [1, 1, 1], 2.62: [2.2, 2.2, 6], 2.8: [1, 1, 1], L: [1, 1, 1]})
    if mega:
        b.update(flames_flare(L, [(0, 1), (t_in, 1.2), (1.6, 1.7), (t_out, 2.0), (2.8, 1.2), (L, 1)]))
        b.update(mist_flare([(0, 1), (1.0, 1.3), (t_out, 1.6), (L, 1)]))
        b.update(DJ.embers(L, loop=False))
    else:
        b.update(heat([(0, 0), (1.2, 0), (1.25, 1), (1.4, 0), (1.6, 1), (2.75, 1), (2.9, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


def recoil(mega=False):
    """Hit: head knocked back and aside, the body jolts back over its feet, the blade lurches; it snarls back."""
    L = 0.95
    b = ik_track(LEGS, L, [(0, 0, 0), (0.12, 0.4, 2.0), (0.38, -0.8, -0.8), (L, 0, 0)])
    b["torso"] = keys(rotation={0: [0, 0, 0], 0.12: [-7, 0, 6], 0.38: [4, 0, -2], L: [0, 0, 0]})
    b["neck"] = keys(rotation={0: [0, 0, 0], 0.12: [-14, 12, 0], 0.38: [-4, -4, 0], L: [0, 0, 0]})
    b["head"] = keys(rotation={0: [0, 0, 0], 0.12: [-14, 0, 14], 0.38: [-6, 0, -4], 0.45: [tremble(-6, 2200, 2.5), 0, 0],
                               0.7: [tremble(-6, 2200, 2.5), 0, 0], L: [0, 0, 0]})
    b["jaw"] = keys(rotation={0: [0, 0, 0], 0.12: [18, 0, 0], 0.38: [28, 0, 0], 0.45: [tremble(26, 1900, 3), 0, 0],
                              0.7: [tremble(22, 1900, 3), 0, 0], 0.85: [4, 0, 0], L: [0, 0, 0]})
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.1: [1, 0.25, 1], 0.3: [1.1, 0.6, 1], 0.8: [1.1, 0.6, 1], L: [1, 1, 1]})
    for side, sx in (("left", 1), ("right", -1)):
        b[f"arm_{side}"] = keys(rotation={0: [0, 0, 0], 0.12: [-20, 0, -10 * sx], 0.4: [-30, 0, 0], L: [0, 0, 0]})
    b["tail"] = keys(rotation={0: [0, 0, 0], 0.12: [6, -10, 0], 0.4: [3, 8, 0], L: [0, 0, 0]})
    b["tail2"] = keys(rotation={0: [0, 0, 0], 0.2: [3, -10, 0], 0.5: [2, 8, 0], L: [0, 0, 0]})
    b["blade"] = keys(rotation={0: [0, 0, 0], 0.18: [4, 0, 0], 0.45: [6, 0, 0], 0.7: [1, 0, 0], L: [0, 0, 0]})
    if mega:
        b.update(mist_flare([(0, 1), (0.15, 1.4), (0.4, 1.2), (L, 1)]))
        b.update(flames_flare(L, [(0, 1), (0.15, 1.6), (0.5, 1.2), (L, 1)]))
        b.update(DJ.embers(L, loop=False))
    else:
        b.update(heat([(0, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


SLEEP_TAIL = {"tail": {"rotation": [-33, -16, -64]}, "tail2": {"rotation": [-38, 9, 0]},
              "tail3": {"rotation": [-22, 21, 0]}, "blade": {"rotation": [-17, 0, 0]}}

TRUNK = ({"torso", "chest"} | {b for lg in LEGS for b in lg.bones[:2]}
         | {"arm_left", "arm_right", "forearm_left", "forearm_right"})


def _skip(m):
    return tuple(b.name for b in m.bones if b.name.startswith(MEGA_ONLY + ("breath", "eye_", "blade_heat")))


def sleep_pose(m, mega=False):
    """Belly on the ground, legs folded under, the long head laid flat on the ground turned aside, the tail lowered
    and curled forward around the body, rolled over so that the blade lies flat on the ground beside it."""
    skip = _skip(m)
    base = {"torso": {"rotation": [4, 0, 0]}, "chest": {"rotation": [2, 0, 0]},
            "arm_left": {"rotation": [45, 0, -8]}, "arm_right": {"rotation": [45, 0, 8]},
            "forearm_left": {"rotation": [40, 0, 0]}, "forearm_right": {"rotation": [40, 0, 0]}}
    pose = {k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()}
    legs = make_legs(mega)
    lie_legs(m, legs, pose, TRUNK, hip_range=(7.0, 18.0))
    pose.update({k: {kk: list(vv) for kk, vv in d.items()} for k, d in base.items()})
    head = descendants(m, "head") - set(skip)
    pose["head"] = {"rotation": [8, 12, 4]}
    search(m, pose, "neck", [[nx, 20, 0] for nx in range(-40, 36, 2)], 0.5, head, keep={"neck"}, skip=skip)
    search(m, pose, "head", [[hx, 12, 4] for hx in range(-24, 40, 2)], 0.3, head, keep={"neck"}, skip=skip)
    # tail: lowered, swung round to the right and rolled so that the blade lies flat on the ground (found by a search:
    # blade plane horizontal, lowest point on the ground, nothing inside the body)
    pose.update(SLEEP_TAIL)
    return pose


def sleep_anim(m, mega=False):
    q = "q.anim_time"
    b = pose_to_bones(sleep_pose(m, mega))
    b["chest"]["position"] = [0, f"0.3+math.sin({q}*45)*0.35", 0]
    b["torso"]["position"] = [0, f"0.15+math.sin({q}*45-30)*0.2", 0]
    b["jaw"] = {"rotation": [f"1+math.sin({q}*45-60)*1", 0, 0]}
    for e in ("eye_left", "eye_right"):
        b[e] = {"scale": [1, 0.02, 1]}
    b["breath"] = {"scale": [f"0.8+math.sin({q}*45)*0.15", f"0.8+math.sin({q}*45)*0.15", 1]}
    if mega:
        for k, name in enumerate(AURA):           # asleep, the mist smoulders low
            b[name] = {"scale": [0.7, f"0.45+math.sin({q}*45+{40 * k})*0.06", 0.7]}
        for j, name in enumerate(FLAMES):
            b[name] = {"scale": [0.6, f"0.4+math.sin({q}*90+{53 * j})*0.1", 0.6]}
        for e in EMBERS:
            b[e] = {"scale": [0, 0, 0]}
    else:
        b["blade_heat"] = {"scale": [0, 0, 0]}
    return {"loop": True, "animation_length": 8, "bones": b}


def ko_anim(m, mega=False):
    """Death: the blow pushes it back a little — it leans back over its planted feet, head jerking up and jaws
    gaping — then its legs give way and it topples slowly onto its left flank, legs limp, the neck and the long head
    coming to rest on the ground, the tail sinking with the blade lying flat; a last breath, the eyes close (mega: the
    flames and the mist die out). The body is settled on the ground at every frame: no jump."""
    skip = _skip(m)
    legs = make_legs(mega)

    def stand(h, bz):
        p = {b: {"rotation": r} for b, r in leg_pose(legs, h, -bz).items()}
        p["body"] = {"rotation": [0, 0, 0], "position": [0, h, bz]}
        return p

    def P(*parts):
        out = {}
        for part in parts:
            for k, v in part.items():
                out[k] = {kk: list(vv) for kk, vv in v.items()}
        return out
    R = lambda **kw: {k: {"rotation": v} for k, v in kw.items()}
    head_grp = descendants(m, "head") - set(skip)
    tail_grp = descendants(m, "tail") - set(skip)
    k0 = P(stand(0, 0))
    k1 = P(stand(-0.4, 2.0), R(torso=[-5, 0, 0], chest=[-3, 0, 0], neck=[-8, 0, 0], head=[-8, 0, 0], jaw=[26, 0, 0],
                              tail=[4, 0, 0]))
    k2 = P(stand(-4.5, 2.5), R(torso=[-2, 0, 0], chest=[-1, 0, 0], neck=[-4, -6, 0], head=[-2, 0, 0], jaw=[18, 0, 0],
                              tail=[0, -4, 0]))
    k2["body"]["rotation"] = [0, 0, 14]
    # on its flank: body rolled onto the +X side (positive Z lowers +X), limp legs, head and tail lying down
    k3 = {"body": {"rotation": [0, 0, 78], "position": [0, -4.5, 2.5]}}
    for lg in legs:
        for bn, dd in zip(lg.bones, lg.deltas((-40, 8, -30, 12))):
            k3[bn] = {"rotation": [dd, 0, 0]}
    k3.update(R(torso=[2, 0, 0], chest=[2, 0, 0], neck=[-6, 0, 0], head=[4, 0, 0], jaw=[14, 0, 0],
                arm_left=[20, 0, 0], arm_right=[30, 0, 20], forearm_left=[10, 0, 0], forearm_right=[15, 0, 0],
                tail2=[0, 6, 0], tail3=[0, 6, 0]))
    k3["body"]["position"][1] = 0
    k3["body"]["position"][1] = -lowest(m, k3, skip=skip) + 0.05
    search(m, k3, "neck", [[-6, 0, z] for z in range(-40, 42, 2)], 0.4, head_grp, keep={"neck"}, skip=skip)
    search(m, k3, "tail", [[0, 0, z] for z in range(-40, 42, 2)], 0.3, tail_grp, skip=skip)
    k4 = P(k3)
    k4["chest"]["rotation"][0] += 3                                   # last breath out
    k4["jaw"]["rotation"][0] = 8
    for kp in (k3, k4):
        kp["body"]["position"][1] = 0
    L = 3.2
    b = pose_sequence(m, [(0, k0), (0.45, k1), (1.05, k2), (2.0, k3), (2.6, k4), (L, k4)], length=L, step=0.05, skip=skip)
    for e in ("eye_left", "eye_right"):
        b[e] = keys(scale={0: [1, 1, 1], 0.3: [1, 0.55, 1], 0.6: [1, 1, 1], 2.0: [1, 0.8, 1], 2.5: [1, 0.1, 1],
                           2.8: [1, 0.02, 1], L: [1, 0.02, 1]})
    b["breath"] = keys(scale={0: [1, 1, 1], 1.2: [1, 1, 1], 2.2: [0.2, 0.2, 1], L: [0.2, 0.2, 1]})
    if mega:
        b.update(mist_flare([(0, 1), (0.45, 1.4), (1.2, 1), (2.2, 0.4), (2.9, 0.05), (L, 0.05)]))
        b.update(flames_flare(L, [(0, 1), (0.45, 1.5), (1.2, 1), (2.2, 0.4), (2.9, 0.1), (L, 0.1)]))
        for e in EMBERS:
            b[e] = keys(scale={0: [0, 0, 0], L: [0, 0, 0]})
    else:
        b.update(heat([(0, 0), (L, 0)]))
    return {"animation_length": L, "bones": b}


def anims(m=None, mega=False):
    m = m or build(mega)
    sid = MEGA_SID if mega else SID
    k = 1.3 if mega else 1.0
    q = "q.anim_time"
    T = 1.3 if not mega else 1.2
    out = standard_anims(sid, m, make_legs(mega), tail=TAIL, flames=(), sway=lambda f, mul=1.0: {},
                         crouch=-3.0, level=(4, 2), skip=_skip(m), battle_head=-8, idle_amp=1.0 * k,
                         walk_kw=dict(T=T, stride=16, lift=4.5, stance=0.62, bob=0.8,
                                      torso=(1.5, 3.5, 3.5 * k), tail_amp=(3, 4, 5), arm_amp=5))
    a = f"animation.{sid}."
    out[a + "ground_idle"] = idle_anim(mega)
    out[a + "battle_idle"] = battle_anim(mega)
    wk = out[a + "ground_walk"]["bones"]
    f = round(360 / T, 3)
    wk["neck"] = {"rotation": [f"5+math.cos({q}*{2 * f}+60)*2", f"math.sin({q}*{f}+90)*5", f"-math.sin({q}*{f})*2"]}
    wk["head"] = {"rotation": [f"-3-math.cos({q}*{2 * f}+90)*2", f"-math.sin({q}*{f}+30)*4", f"-math.sin({q}*{f})*3"]}
    wk["jaw"] = {"rotation": [f"{4 * k}+math.sin({q}*{2 * f})*3", 0, 0]}
    wk["blade"] = {"rotation": [f"math.cos({q}*{2 * f}-200)*2", 0, 0]}
    wk.update(fx_loop(T, mega))
    out[a + "cry"] = cry(mega)
    out[a + "physical"] = physical(mega)
    out[a + "special"] = special(mega)
    out[a + "recoil"] = recoil(mega)
    out[a + "status"] = status(mega)
    out[a + "sleep"] = sleep_anim(m, mega)
    out[a + "faint"] = ko_anim(m, mega)
    for name, an in out.items():
        bn = an["bones"]
        bn.setdefault("breath", {"scale": [1, 1, 1]})
        if not mega:
            bn.setdefault("blade_heat", {"scale": [0, 0, 0]})
        elif not name.endswith(("blink", "sleep")):
            bn.update({e: v for e, v in DJ.embers(an["animation_length"], an.get("loop", False)).items() if e not in bn})
    return out


def poser(mega=False):
    sid = MEGA_SID if mega else SID
    p = make_poser(sid, portrait=(0.9, [-0.6, 1.0, 0]), profile=(0.4, [0.0, 1.0, 0]))
    p["rootBone"] = SID
    qp = lambda n: f"q.bedrock_primary('{sid}', '{n}', q.curve('symmetrical_wide'))"
    p["animations"].update(physical=qp("physical"), special=qp("special"), status=qp("status"),
                           recoil=f"q.bedrock_stateful('{sid}', 'recoil')")
    return p
