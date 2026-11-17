# -*- coding: utf-8 -*-
"""#1050 Sleipcheron — étalon percheron légendaire du blizzard (Glace / Sol).
The colossal build, powerful arched neck and massive frame of a Percheron stallion, with a crushing, menacing
presence. Its coat is a deep blue-grey, like frozen stone or clear ice, veined with frost cracks. Straight, proud
profile, sharp features, pearly white glowing eyes; frost crystals and icy cracks sculpted on the forehead and
muzzle; ice shards along the crest, the withers and the croup. An extra-long flowing mane like streams of polar
mist and packed snow, and a huge tail glowing like the northern lights. Four heavy Norman hooves of black glassy
obsidian, ringed with frost and a supernatural blue glow, frost shards bursting around them; icy feathering at the
fetlocks. Shiny: a midnight-black frozen coat with an aurora-green mane and tail."""
import math
from modelgen import Model, Cube, rgb, mix, apply
from bovine import (make_legs, bovine_anims, finalize, SIDES, bovine_poser, vnoise, put, light, side_cols)

SID, DEX = "sleipcheron", 1050
FRAME_BONES = ("head", "jaw")
HEIGHT_SKIP = ("ear", "mane", "forelock", "crystal")          # 2.6 m to the poll
HITBOX_WIDTH = 2.4                   # x baseScale 0.64 = about 1.5 blocks: a draught horse, wider than Minecraft's

PAL = {
    "coat": rgb("#5F7C98"), "coat_dark": rgb("#34475E"), "coat_light": rgb("#9FBCD6"), "frost": rgb("#D6F0FF"),
    "muzzle": rgb("#3C4E62"), "nostril": rgb("#141C26"), "mouth": rgb("#1C2633"), "teeth": rgb("#E4E0D0"),
    "hair": rgb("#F2F8FF"), "hair_blue": rgb("#B8D8F2"), "hair_shade": rgb("#86AACC"),
    "aurora_a": rgb("#6EF2C0"), "aurora_b": rgb("#5AC8F0"), "aurora_c": rgb("#B48CF2"),
    "ice": rgb("#A6D8F6"), "ice_tip": rgb("#F0FBFF"), "ice_dark": rgb("#5A98CC"), "ice_hi": rgb("#FFFFFF"),
    "obsidian": rgb("#121620"), "obsidian_hi": rgb("#3C4658"), "rune": rgb("#4FC8FF"), "rune_hot": rgb("#C8F4FF"),
    "eye": rgb("#F4FAFF"), "eye_glow": rgb("#BFE6FF"), "eye_dark": rgb("#24344A"),
}
SHINY = dict(PAL, **{
    "coat": rgb("#262E3C"), "coat_dark": rgb("#12161E"), "coat_light": rgb("#4E5C74"), "frost": rgb("#9AF2D8"),
    "muzzle": rgb("#1A202A"),
    "hair": rgb("#C8FFE8"), "hair_blue": rgb("#7AF0C8"), "hair_shade": rgb("#3AA88E"),
    "aurora_a": rgb("#5AF29A"), "aurora_b": rgb("#3AD8D0"), "aurora_c": rgb("#C86AF2"),
    "ice": rgb("#8AF0DA"), "ice_tip": rgb("#E8FFF8"), "ice_dark": rgb("#2E9A8A"),
    "rune": rgb("#5AF2B4"), "rune_hot": rgb("#D8FFF0"), "eye_glow": rgb("#A8FFE0"),
})
G = {"glow": True, "shading": False}

# ============================================================================ painters
def _hash2(a, b, seed):
    h = (int(a) * 73856093) ^ (int(b) * 19349663) ^ (seed * 83492791)
    return ((h * 2654435761) & 0xFFFFFFFF) / 0xFFFFFFFF

def dapple(u, v, seed, cell=3.2):
    """Worley-like dapples: 0 at a dapple centre .. ~1 on the darker net between dapples."""
    cu, cv = math.floor(u / cell), math.floor(v / cell)
    best = 9.0
    for du in (-1, 0, 1):
        for dv in (-1, 0, 1):
            a, b = cu + du, cv + dv
            px_ = (a + 0.2 + 0.6 * _hash2(a, b, seed)) * cell
            py_ = (b + 0.2 + 0.6 * _hash2(b, a, seed + 1)) * cell
            best = min(best, math.hypot(u - px_, v - py_))
    return min(1.0, best / (cell * 0.75))

def frozen(seed=3, frost_low=9.0, dapples=0.0, cracks=1.0):
    """Frozen-stone coat (fn3): deep blue-grey with lighter and darker drifts, dapples like a grey Percheron's
    (lighter rounds on a darker net), fine frost cracks (pale veins), rime speckles on top faces, the lower legs
    whitening with hoarfrost."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            p = apply(c.world, pl)
            fx, fy, fw, fh = faces[face]
            f = light(face, Y - fy, fh, 0.14)
            n = vnoise(p[0] * 0.16, p[1] * 0.16, p[2] * 0.16, seed)
            col = pal["coat"]
            col = mix(pal["coat_dark"], pal["coat_light"], max(0.0, min(1.0, 0.5 + (n - 0.5) * 1.3)))
            col = mix(pal["coat"], col, 0.45)
            if dapples:
                u, v = (p[2], p[1]) if face in ("east", "west") else (p[0], p[1] if face in ("north", "south") else p[2])
                d = dapple(u, v, seed, cell=4.2)
                col = mix(col, pal["coat_light"], dapples * (1 - d) * 0.8) if d < 0.6 else mix(col, pal["coat_dark"], dapples * (d - 0.6) * 1.2)
            cr = vnoise(p[0] * 0.33 + 5, p[1] * 0.33, p[2] * 0.33, seed + 3)
            cr2 = vnoise(p[0] * 0.6 + 9, p[1] * 0.6, p[2] * 0.6, seed + 4)
            if abs(cr - 0.5) < 0.008 * cracks:
                col = mix(col, pal["frost"], 0.55)                    # frost cracks
            if face == "up" and rnd.random() < 0.004:
                col = mix(col, pal["frost"], 0.4)
            if p[1] < frost_low:
                col = mix(col, pal["frost"], 0.35 * (1 - p[1] / frost_low))
            put(px, X, Y, col, f, rnd, 2)
    return {"fn3": fn3}

def hair_plane(z0, L, y1, h, seed=1, aurora=True, taper=0.45):
    """Flowing mane / tail hair on a vertical plane (faces east/west), in rest coordinates: root at z0 (top y1),
    flowing to z0 + L, h tall at the root and tapering; wavy strands of snow white and ice blue turning into
    northern-light colours towards the tips; ragged wisps at the end. Re-rolled on each emissive frame."""
    ramp = ("aurora_a", "aurora_b", "aurora_c")
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            if face not in ("east", "west"):
                px[X, Y] = (0, 0, 0, 0)
                continue
            z, y = pl[2], pl[1]
            t = (z - z0) / L                                   # 0 root .. 1 tip
            s = (y1 - y) / h                                   # 0 top .. 1 bottom
            wave = 0.08 * math.sin(t * 9 + seed) + 0.06 * math.sin(t * 17 + 2 * seed)
            bottom = 1 - taper * t + wave
            top = 0.18 * t * t + 0.04 * math.sin(t * 13 + seed)
            wisp = (math.floor(y * 1.0) * 7 + seed * 3) % 5
            if not (top < s < bottom) or t > 1 - 0.035 * wisp or t < 0:
                px[X, Y] = (0, 0, 0, 0)
                continue
            strand = math.sin(y * 0.9 + 1.4 * math.sin(t * 4 + seed) + seed)
            col = pal["hair"] if strand > -0.1 else pal["hair_blue"]
            if strand < -0.85:
                col = pal["hair_shade"]
            if aurora and t > 0.45:
                k = (t * 2.2 + s * 0.8 + seed * 0.37) % 1.0 * len(ramp)
                a0 = ramp[int(k) % len(ramp)]
                a1 = ramp[(int(k) + 1) % len(ramp)]
                ac = mix(pal[a0], pal[a1], k - int(k))
                col = mix(col, ac, min(0.85, (t - 0.45) * 2.0))
            if rnd.random() < 0.03:
                col = pal["hair"]
            put(px, X, Y, col, 1.0, rnd, 3)
    return {"fn3": fn3, **G}

def drape(z0, z1, y1, L, seed=1):
    """Mane falling down the side of the neck (vertical plane, faces east/west): locks hanging from the crest (y1)
    for about L, ragged ends, strands along the fall, northern-light tint towards the ends."""
    ramp = ("aurora_a", "aurora_b", "aurora_c")
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            if face not in ("east", "west"):
                px[X, Y] = (0, 0, 0, 0)
                continue
            z, y = pl[2], pl[1]
            u = (z - z0) / (z1 - z0)
            t = (y1 - y) / L
            lock = math.floor((z - z0) / 2.0)
            end = 1 - 0.28 * (((lock * 5 + seed) % 4) / 3) + 0.06 * math.sin(z * 0.9 + seed)
            if t < 0 or t > end or u < 0 or u > 1:
                px[X, Y] = (0, 0, 0, 0)
                continue
            strand = math.sin(z * 1.2 + 1.3 * math.sin(t * 5 + seed))
            col = pal["hair"] if strand > -0.1 else pal["hair_blue"]
            if strand < -0.85:
                col = pal["hair_shade"]
            if t > 0.55:
                k = (u * 2.0 + t + seed * 0.37) % 1.0 * len(ramp)
                ac = mix(pal[ramp[int(k) % 3]], pal[ramp[(int(k) + 1) % 3]], k - int(k))
                col = mix(col, ac, min(0.7, (t - 0.55) * 1.8))
            put(px, X, Y, col, 1.0, rnd, 3)
    return {"fn3": fn3, **G}

def frost_veins(seed=1, density=1.0):
    """Glowing frost cracks on a cutout plane laid on the face: branching icy lines (transparent elsewhere)."""
    def fn3(px, faces, pal, rnd, c):
        for face, X, Y, pl in c.texels():
            a, b = (pl[2], pl[1]) if face in ("east", "west") else (pl[0], pl[2])
            v1 = vnoise(a * 0.5 + seed, b * 0.5, 0.5, seed)
            v2 = vnoise(a * 1.0, b * 1.0 + seed, 1.5, seed + 2)
            on = abs(v1 - 0.5) < 0.022 * density or (abs(v2 - 0.5) < 0.014 * density and v1 > 0.5)
            if not on or face in ("up", "down") and pl[1] != pl[1]:
                px[X, Y] = (0, 0, 0, 0)
                continue
            px[X, Y] = pal["rune_hot"] if rnd.random() < 0.35 else pal["frost"]
    return {"fn3": fn3, **G}

def ear_inner(px, faces, pal, rnd):
    """Ear: coat outside, dark hollow with frosty hairs on the front face."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = pal["coat"]
                if fc == "north" and 0 < i < w - 1 and j > 0:
                    col = pal["coat_dark"] if (i + j) % 3 else pal["frost"]
                put(px, x + i, y + j, col, 1.0 if fc == "up" else 0.92, rnd, 3)

def hair_block(seed=2):
    """Packed snow hair on small cubes (forelock, fetlock feathering): white / ice-blue streaks, ragged lower edge."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                for i in range(w):
                    if fc in ("east", "west", "north", "south") and j == h - 1 and (i + seed) % 3 == 0:
                        px[x + i, y + j] = (0, 0, 0, 0)
                        continue
                    col = pal["hair"] if (i + seed) % 3 else pal["hair_blue"]
                    if j == h - 1:
                        col = mix(col, pal["hair_shade"], 0.4)
                    put(px, x + i, y + j, col, 1.0 if fc == "up" else 0.92, rnd, 3)
    return fn

def ice(seed=1):
    """Ice shard: clear blue deepening at the base, white tip, one bright facet and one shaded."""
    def fn(px, faces, pal, rnd):
        for fc, (x, y, w, h) in faces.items():
            for j in range(h):
                t = 1 - j / max(h - 1, 1)
                for i in range(w):
                    col = mix(pal["ice_dark"], pal["ice_tip"], t ** 1.3)
                    if fc == "up":
                        col = pal["ice_tip"]
                    elif i == 0 and fc in ("north", "west"):
                        col = mix(col, pal["ice_hi"], 0.6)
                    elif i == w - 1 and fc in ("south", "east"):
                        col = mix(col, pal["ice_dark"], 0.5)
                    if (i + j + seed) % 6 == 0:
                        col = mix(col, pal["ice"], 0.5)
                    px[x + i, y + j] = col
    return fn

def obsidian(px, faces, pal, rnd):
    """Obsidian hoof: glassy black with a cold sheen, glowing blue runes / cracks and a glowing rim at the sole."""
    for fc, (x, y, w, h) in faces.items():
        for j in range(h):
            for i in range(w):
                col = pal["obsidian"]
                if (i + 2 * j) % 7 == 0:
                    col = pal["obsidian_hi"]
                if fc not in ("up", "down") and (j == h - 1 or (i * 3 + j * 5 + rnd.randrange(3)) % 11 == 0):
                    col = pal["rune_hot"] if rnd.random() < 0.3 else pal["rune"]
                px[x + i, y + j] = col

def eye_plane(px, faces, pal, rnd):
    """Pearly glowing eye (side plane, columns from the front): dark lid line on top, white glowing core, pale
    blue halo, sharp dark corners."""
    rows = [".DDDD", "DEEEG", "DGEGD"]
    keys = {"E": "eye", "G": "eye_glow", "D": "eye_dark"}
    for fc, (x, y, w, h) in faces.items():
        if not (w and h):
            continue
        cols = side_cols(fc, w) if fc in ("east", "west") else list(range(w))
        for j in range(h):
            for k in range(w):
                ch = rows[min(j, len(rows) - 1)][min(k, len(rows[0]) - 1)]
                px[x + cols[k], y + j] = pal[keys[ch]] if (fc in ("east", "west") and ch != ".") else (0, 0, 0, 0)

COAT = frozen(dapples=0.55)
COAT2 = frozen(seed=7, dapples=0.55)
MUSCLE = frozen(seed=9, dapples=0.35)
HEADC = frozen(seed=11, frost_low=-1, cracks=0.6)
EAR = {"fn": ear_inner}
ICE = {"fn": ice(), **G}
FEATHER = {"fn": hair_block(), **G}
HOOF = {"fn": obsidian, **G}
MUZ = {"fn3": frozen(seed=13, frost_low=-1)["fn3"]}

# ============================================================================ legs: draught-horse columns
FRONT = dict(x=5.0, z=-11.0, L=(9, 9, 8), a=(18, -4, 0), th=3, thigh=(8, 9, 4), shin=(6, 6), meta=(5, 5), foot=(6, 6, 2))
BACK = dict(x=5.0, z=12.0, L=(10, 9, 8), a=(-22, 30, -4), th=3, thigh=(9, 11, 5), shin=(6, 7), meta=(5, 5), foot=(6, 6, 2))
LEG_PAINT = {"thigh": COAT, "shin": COAT2, "meta": COAT, "foot": HOOF}
LEGS = make_legs(FRONT, BACK, LEG_PAINT, LEG_PAINT)
PIVOT = (0, 28.3, 0)
MANE = [(-34, 34, 12, 6, 0.0), (-31, 38, 13, 0, 1.6), (-28, 40, 14, -4, -1.6), (-25, 40, 14, -8, 0.0),
        (-22, 38, 13, -12, 1.8), (-19, 34, 12, -16, -1.8), (-16, 28, 10, -20, 0.0)]   # (z, L, h, net droop, x)
TAIL = ("tail", "tail2", "tail3", "tail4")

HEAD_SHIFT = (0, 1.5, -6.5)
SEAT = (0, 40.2, -2.0)            # the head hangs in front of the neck's end instead of sinking into it

def shift_head(m, d):
    names = {"head"} | {b.name for b in m.bones if b.parent == "head"}
    for b in m.bones:
        if b.name in names:
            if b.name != "head" or True:
                b.pivot = [p + q for p, q in zip(b.pivot, d)]
            for c in b.cubes:
                c.origin = [p + q for p, q in zip(c.origin, d)]
                if c.pivot:
                    c.pivot = [p + q for p, q in zip(c.pivot, d)]

def build():
    m = Model(SID, DEX, (512, 256))
    m.bone(SID, None, [0, 0, 0])
    m.bone("body", SID, list(PIVOT))
    for lg in LEGS:
        lg.build(m)
        x, z = lg.x, lg.hip_z
        # icy feathering over the fetlock, and frost shards bursting around the hoof
        m.get(lg.bones[2]).cubes.append(Cube([x - 3.5, 2, z - 3.5], [7, 4, 7], FEATHER))
        H, (L1, L2, L3) = lg.H, lg.L
        knee = H - L1 - L2                                                       # joint between shin and cannon
        if lg.side.startswith("front"):
            m.get(lg.bones[1]).cubes.extend([Cube([x - 3.5, H - L1 - 4, z - 3.5], [7, 4, 7], MUSCLE),    # forearm
                                             Cube([x - 3.5, knee - 1, z - 3.5], [7, 3, 6], COAT2)])      # knee
        else:
            m.get(lg.bones[1]).cubes.extend([Cube([x - 3.5, H - L1 - 4, z - 4], [7, 4, 8], MUSCLE),      # gaskin
                                             Cube([x - 3, knee - 1, z + 2.5], [6, 3, 2], COAT2)])        # point of hock
        m.get(lg.bones[3]).cubes.extend([
            Cube([x + 3, 0.4, z - 2], [1, 3, 1], ICE, rotation=[0, 0, -25], pivot=[x + 3, 0.4, z - 2]),
            Cube([x - 4, 0.4, z - 1], [1, 2, 1], ICE, rotation=[0, 0, 30], pivot=[x - 3.5, 0.4, z - 1]),
            Cube([x - 0.5, 0.4, z - 5], [1, 2, 1], ICE, rotation=[30, 0, 0], pivot=[x, 0.4, z - 4.5]),
            Cube([x + 1, 0.4, z + 2.5], [1, 2, 1], ICE, rotation=[-30, 0, 10], pivot=[x + 1, 0.4, z + 2.5])])
    m.bone("torso", "body", [0, 31, 0], cubes=[
        Cube([-8, 22, -14], [16, 17, 29], COAT),
        Cube([-7, 21, -11], [14, 1, 22], COAT), Cube([-6, 20, -7], [12, 1, 14], COAT),   # deep belly
        Cube([-7, 39, -12], [14, 1, 18], COAT),
        Cube([8, 25, -10], [1, 11, 15], MUSCLE), Cube([-9, 25, -10], [1, 11, 15], MUSCLE),   # rounded ribcage
        Cube([-8.5, 24, 6], [17, 15, 12], COAT2),                                # massive haunches
        Cube([8.5, 26, 7], [1, 11, 9], MUSCLE), Cube([-9.5, 26, 7], [1, 11, 9], MUSCLE),     # hindquarter muscles
        Cube([-7, 39, 6], [14, 2, 11], COAT2), Cube([-5.5, 41, 8], [11, 1, 7], COAT2),       # round, split croup
        Cube([-2, 38, 17], [4, 3, 2], COAT)])                                    # tail head
    m.bone("locator_seat_1", "torso", list(SEAT), locators={"seat_1": list(SEAT)})   # rider between withers and croup
    m.bone("chest", "torso", [0, 31, -12], cubes=[
        Cube([-8.5, 23, -19], [17, 16, 8], COAT2),                               # shoulders
        Cube([-7, 22, -20], [14, 13, 1], MUSCLE),                                # breast
        Cube([0.5, 24, -21], [6, 10, 1], MUSCLE), Cube([-6.5, 24, -21], [6, 10, 1], MUSCLE),   # pectorals
        Cube([8.5, 27, -19], [1, 11, 7], MUSCLE), Cube([-9.5, 27, -19], [1, 11, 7], MUSCLE),   # shoulder muscles
        Cube([-6, 39, -16], [12, 2, 9], COAT), Cube([-4, 41, -14], [8, 1, 5], COAT)])          # withers
    # ice shards on the withers and the croup
    m.bone("crystal_withers", "chest", [0, 41, -12], cubes=[
        Cube([1, 40, -13], [2, 10, 2], ICE, rotation=[-35, 0, 20], pivot=[2, 41, -12]),
        Cube([-3, 40, -11], [2, 8, 2], ICE, rotation=[-40, 0, -22], pivot=[-2, 41, -10]),
        Cube([-0.5, 40, -9], [1, 5, 1], ICE, rotation=[-45, 0, 6], pivot=[0, 41, -8]),
        Cube([2.5, 40, -8], [1, 4, 1], ICE, rotation=[-50, 0, 40], pivot=[3, 41, -8])])
    m.bone("crystal_croup", "torso", [0, 41, 8], cubes=[
        Cube([0.5, 40, 6], [2, 9, 2], ICE, rotation=[-40, 0, 18], pivot=[1.5, 41, 7]),
        Cube([-2.5, 40, 9], [2, 7, 2], ICE, rotation=[-45, 0, -20], pivot=[-1.5, 41, 10]),
        Cube([1.5, 40, 11], [1, 4, 1], ICE, rotation=[-50, 0, 30], pivot=[2, 41, 12]),
        Cube([-1, 40, 3], [1, 4, 1], ICE, rotation=[-35, 0, -8], pivot=[-0.5, 41, 3.5])])

    # ---------------------------------------------------------------- arched neck, mane of polar mist
    m.bone("neck", "chest", [0, 37, -16], rotation=[-58, 0, 0], cubes=[
        Cube([-5.5, 36, -36], [11, 9, 20], COAT2),                               # upper neck (crest muscle)
        Cube([-4.5, 30, -35], [9, 6, 19], MUSCLE),                               # throat, narrower
        Cube([-4, 45, -35], [8, 2, 19], COAT), Cube([-3, 47, -31], [6, 1, 13], COAT),   # arched crest
        Cube([-6, 31, -24], [12, 13, 8], COAT2),                                 # thick base of the neck
        Cube([5.5, 35, -33], [1, 8, 14], MUSCLE), Cube([-6.5, 35, -33], [1, 8, 14], MUSCLE)])   # neck muscles
    for k, (z, L, h, droop, xo) in enumerate(MANE):                              # XXL mane streaming back like mist
        planes = [Cube([xo + d, 49 - h, z], [0, h, L], hair_plane(z, L, 49, h, seed=2 * k + j + 1))
                  for j, d in enumerate((0.9, -0.9))]
        m.bone(f"mane{k + 1}", "neck", [xo, 48, z], rotation=[58 + droop, 4 * xo, 0], cubes=planes)
    for j, (cz, rx) in enumerate(((-32, 0), (-25, 10))):                         # shards along the crest
        m.bone(f"crystal_crest{j + 1}", "neck", [0, 47, cz], rotation=[rx, 0, 0], cubes=[
            Cube([2, 46.5, cz - 1], [1, 4, 2], ICE, rotation=[0, 0, 25], pivot=[2, 47, cz]),
            Cube([-3, 46.5, cz + 1], [1, 3, 1], ICE, rotation=[0, 0, -30], pivot=[-2, 47, cz + 1])])
    # head: modelled level in the neck's unrotated frame, pitched nose-down at the poll
    m.bone("head", "neck", [0, 38, -35], rotation=[95, 0, 0], cubes=[
        Cube([-5, 34, -43], [10, 9, 9], HEADC),                                  # skull
        Cube([-4.5, 43, -42], [9, 1, 7], HEADC),                                 # broad flat forehead
        Cube([-4, 35, -55], [8, 7, 12], HEADC),                                  # straight nasal profile
        Cube([-3, 42, -54], [6, 1, 11], HEADC),                                  # nasal bone ridge
        Cube([-3.5, 33, -55], [7, 2, 12], HEADC),                                # lower face
        Cube([-4.5, 32, -60], [9, 9, 5], MUZ),                                   # big flaring muzzle
        Cube([-4, 31, -59], [8, 1, 4], MUZ),                                     # upper lip
        Cube([-3.5, 37, -60.04], [2, 3, 0], {"base": "nostril"}), Cube([1.5, 37, -60.04], [2, 3, 0], {"base": "nostril"}),
        Cube([-4.8, 37, -59.5], [1, 3, 2], MUZ), Cube([3.8, 37, -59.5], [1, 3, 2], MUZ),   # flared nostril rims
        # frost crystals sculpted on the forehead (a frost diadem) and down the nose
        Cube([-0.5, 43.5, -46], [1, 3, 1], ICE, rotation=[-20, 0, 0], pivot=[0, 43.5, -45.5]),
        Cube([-2, 43.5, -44], [1, 2, 1], ICE, rotation=[-25, 0, 25], pivot=[-1.5, 43.5, -43.5]),
        Cube([1, 43.5, -44], [1, 2, 1], ICE, rotation=[-25, 0, -25], pivot=[1.5, 43.5, -43.5]),
        Cube([-3, 43.5, -42], [1, 1, 1], ICE), Cube([2, 43.5, -42], [1, 1, 1], ICE),
        Cube([-0.5, 43, -50], [1, 1, 1], ICE), Cube([-0.5, 43, -53], [1, 1, 1], ICE),
        # glowing frost cracks laid on the face
        Cube([-3, 43.05, -54], [6, 0, 11], frost_veins(seed=3)),
        Cube([4.05, 35, -55], [0, 7, 12], frost_veins(seed=5, density=0.8)),
        Cube([-4.05, 35, -55], [0, 7, 12], frost_veins(seed=7, density=0.8)),
        Cube([-2.5, 31.02, -58], [5, 0, 8], {"base": "mouth"}),                  # palate, seen when it neighs
        Cube([-2, 31.4, -58.3], [4, 1, 1], {"base": "teeth"})])                  # upper incisors
    m.bone("jaw", "head", [0, 33, -46], cubes=[
        Cube([-3, 31, -58.5], [6, 2, 10], {"fn3": MUZ["fn3"]}),                 # lower lip and chin
        Cube([-3.5, 31, -50], [7, 3, 8], HEADC),                                 # jaw branches up to the hinge
        Cube([-2.5, 32.99, -58], [5, 0, 8], {"base": "mouth"}),
        Cube([-2, 32.6, -58.3], [4, 1, 1], {"base": "teeth"})])                  # lower incisors
    m.bone("forelock", "head", [0, 43, -40], cubes=[
        Cube([-2.5, 43.2, -46], [1, 1, 6], FEATHER), Cube([-0.5, 43.4, -48], [1, 1, 8], FEATHER),
        Cube([1.5, 43.2, -45], [1, 1, 5], FEATHER), Cube([-1.5, 43.3, -47], [1, 1, 3], FEATHER)])         # locks
    for side, s in SIDES:
        X = lambda x0, w: x0 if s > 0 else -x0 - w
        xe = 5.03 * s
        m.bone(f"eye_{side}", "head", [xe, 39.5, -40.5], cubes=[Cube([xe, 38, -43], [0, 3, 5], {"fn": eye_plane, **G})])
        m.bone(f"cheek_{side}", "head", [5 * s, 35, -38], cubes=[
            Cube([X(5, 1), 32, -41], [1, 6, 6], MUSCLE),                         # round cheek (ganache)
            Cube([X(4, 1), 35, -52], [1, 2, 9], HEADC),                          # facial crest
            Cube([X(4.6, 1), 41, -44], [1, 1, 5], HEADC)])                       # brow ridge over the eye
        m.bone(f"ear_{side}", "head", [2.5 * s, 43, -37], rotation=[-40, 0, 12 * s], cubes=[
            Cube([X(1.5, 3), 43, -38.5], [3, 5, 2], EAR), Cube([X(2, 2), 48, -38], [2, 2, 1], EAR),
            Cube([X(2.5, 1), 50, -37.8], [1, 1, 1], HEADC)])

    shift_head(m, HEAD_SHIFT)

    # ---------------------------------------------------------------- huge tail like the aurora
    tail = (("tail", "torso", 38, 17, -62, 10, 13), ("tail2", "tail", 38, 27, 14, 12, 15),
            ("tail3", "tail2", 38, 37, 14, 12, 16), ("tail4", "tail3", 38, 47, 12, 13, 14))
    for k, (name, par, py, pz, rx, L, h) in enumerate(tail):
        cubes = []
        if k == 0:
            cubes.append(Cube([-1.5, py - 2, pz - 1], [3, 4, 5], COAT))          # dock
        for j, xo in enumerate((0.8, -0.8)):
            cubes.append(Cube([xo, py + 1 - h, pz], [0, h + 2, L], hair_plane(pz, L, py + 3, h + 2, seed=20 + 3 * k + j,
                                                                                   taper=0.25)))
        m.bone(name, par, [0, py, pz], rotation=[rx, 0, 0], cubes=cubes)
    m.pack()
    return m

# ============================================================================ animations
Q = "q.anim_time"

def hair_wind(f, amp=1.0, lag=35, tail_amp=1.0):
    """Mane and tail streaming in the wind (Molang, f in deg/s)."""
    out = {}
    for k in range(len(MANE)):
        out[f"mane{k + 1}"] = {"rotation": [f"math.sin({Q}*{f}-{lag * k})*{2.5 * amp}", f"math.sin({Q}*{f / 2:.2f}-{lag * k})*{5 * amp}",
                                            f"math.sin({Q}*{f}-{lag * k + 60})*{3 * amp}"]}
    for i, tb in enumerate(TAIL):
        out[tb] = {"rotation": [f"math.sin({Q}*{f}-{lag * i})*{(2 + i) * tail_amp}", f"math.sin({Q}*{f / 2:.2f}-{lag * i + 20})*{(4 + 2 * i) * tail_amp}", 0]}
    out["forelock"] = {"rotation": [f"math.sin({Q}*{f}+30)*{2 * amp}", 0, f"math.sin({Q}*{f / 2:.2f})*{3 * amp}"]}
    return out

def anims(m=None):
    m = m or build()
    q = "q.anim_time"
    skip = tuple(b.name for b in m.bones if b.name.startswith(("mane", "forelock", "crystal", "tail")))
    W = 360 / 1.3
    idle_x = hair_wind(45)
    walk_x = hair_wind(2 * W, amp=1.5, lag=40, tail_amp=1.3)
    def battle_wind(bone, ch, idx):
        return lambda t: [math.sin(math.radians(t * 180 - 40 * idx)) * 3, math.sin(math.radians(t * 90 - 40 * idx)) * 7, 0]
    battle_x = {b: {"rotation": battle_wind(b, "rotation", i)} for i, b in enumerate([f"mane{k + 1}" for k in range(len(MANE))] + list(TAIL))}
    out = bovine_anims(SID, m, LEGS, pivot=PIVOT, skip=skip, tail=TAIL, chew=0.6, torso=(0.8, 1.4, 1.8),
                       walk_kw=dict(T=1.3, stride=14, lift=4.5, stance=0.66, bob=0.6, toe_off=20, fold=60, curl=40),
                       battle=dict(theta=-1.0, dy=-0.6, neck=-8, head=-10, paw="front_right", paw_t=1.0, ears_back=26,
                                   tail_up=6),
                       cry=dict(L=2.2, t_in=0.3, t_open=0.6, t_close=1.6, neck=-20, head=-24, jaw=14, tremble=3.0, yaw=8),
                       idle_extra=idle_x, walk_extra=walk_x, battle_extra=battle_x,
                       graze_kw=dict(L=5.0, theta=3.0))
    a = f"animation.{SID}."
    out[a + "cry"] = rear(m)
    for name in ("graze", "sleep", "faint", "cry"):
        keep_mane_back(out[a + name])
    out.update(ride_anims(m, out))
    return finalize(out)

def ride_anims(m, out):
    """Mount: a calm idle under the rider, a thundering gallop when sprinting (transverse gallop, mane and tail
    streaming back, the neck pumping) and a jump with the forelegs tucked and the hind legs stretched out."""
    from biped import walk
    a = f"animation.{SID}."
    res = {}
    res[a + "mount_ground_idle"] = {"loop": True, "animation_length": 8,
                                    "bones": {k: v for k, v in out[a + "ground_idle"]["bones"].items() if k != "jaw"}}
    T = 0.6
    gf = round(360 / T, 3)
    ex = hair_wind(2 * gf, amp=2.0, lag=45, tail_amp=1.6)
    for k in range(len(MANE)):                       # streaming flat behind the neck
        r = ex[f"mane{k + 1}"]["rotation"]
        ex[f"mane{k + 1}"]["rotation"] = [f"-10+{r[0]}", r[1], r[2]]
    for i, tb in enumerate(TAIL):                    # the tail lifts and streams back
        r = ex[tb]["rotation"]
        ex[tb]["rotation"] = [f"{40 if i == 0 else 8}+{r[0]}", r[1], 0]
    ex["neck"] = {"rotation": [f"-4+math.sin({Q}*{gf}+70)*5", 0, 0]}
    ex["head"] = {"rotation": [f"6-math.sin({Q}*{gf}+100)*4", 0, 0]}
    ex["jaw"] = {"rotation": [f"2+math.sin({Q}*{gf})*2", 0, 0]}
    for side, s in SIDES:
        ex[f"ear_{side}"] = {"rotation": [0, 0, -12 * s]}
    res[a + "ground_run"] = walk(LEGS, T=T, stride=20, lift=6.0, stance=0.36, bob=1.1, samples=32, toe_off=26, fold=80,
                                 curl=50, phases={"back_left": 0.0, "back_right": 0.1, "front_left": 0.5, "front_right": 0.6},
                                 torso=(3.0, 1.0, 1.0), tail=(), neck=True, arms=(), extra=ex)
    jump = {"body": {"rotation": [-8, 0, 0], "position": [0, 1.5, 0]},
            "neck": {"rotation": [-6, 0, 0]}, "head": {"rotation": [10, 0, 0]}}
    for lg in LEGS:
        front = lg.side.startswith("front")
        ang = (-45, 55, 95, 95) if front else (25, 60, 45, 45)       # forelegs tucked up, hind legs flung back
        for b, d in zip(lg.bones, lg.deltas(ang)):
            jump[b] = {"rotation": [d, 0, 0]}
    jump.update(hair_wind(2 * gf, amp=2.0, lag=45, tail_amp=1.5))
    for k in range(len(MANE)):
        r = jump[f"mane{k + 1}"]["rotation"]
        jump[f"mane{k + 1}"]["rotation"] = [f"-12+{r[0]}", r[1], r[2]]
    for i, tb in enumerate(TAIL):
        r = jump[tb]["rotation"]
        jump[tb]["rotation"] = [f"{45 if i == 0 else 10}+{r[0]}", r[1], 0]
    res[a + "ride_jump"] = {"loop": True, "animation_length": T, "bones": jump}
    return res

STREAMS = [f"mane{k + 1}" for k in range(len(MANE))]

def keep_mane_back(anim, factor=0.85):
    """The mane streams follow the neck; when the neck bows (grazing, sleeping, knocked out) they would stand up
    like a crest. Counter-rotate them so they keep flowing back."""
    from biped import kf
    neck = anim["bones"].get("neck", {}).get("rotation")
    if neck is None:
        return
    if isinstance(neck, dict):
        keys_ = {}
        for t, v in neck.items():
            val = v["post"] if isinstance(v, dict) else v
            x = val[0] if isinstance(val[0], (int, float)) else 0.0
            keys_[t] = kf([round(-factor * x, 2), 0, 0])
        for b in STREAMS:
            anim["bones"][b] = {"rotation": dict(keys_)}
    else:
        x = neck[0]
        if isinstance(x, str):                  # Molang: strip to its constant part if any
            try:
                x = float(x.split("+")[0])
            except ValueError:
                x = 0.0
        for b in STREAMS:
            anim["bones"][b] = {"rotation": [round(-factor * x, 2), 0, 0]}

def rear(m, L=2.6):
    """Cry: the stallion rears on its hind legs, forelegs folded and pawing the air, neck up and a ringing neigh,
    mane and tail streaming; it lands heavily with a stamp."""
    from bovine import plant, legs_pose, sampled, lerp_keys
    from biped import smooth
    back = [lg for lg in LEGS if lg.side.startswith("back")]
    front = [lg for lg in LEGS if lg.side.startswith("front")]
    def pose(t):
        e = lerp_keys([(0, 0.0), (0.25, 0.0), (0.75, 1.0), (1.7, 1.0), (2.15, 0.0), (L, 0.0)], t)
        th = -34 * e
        dy = 3.0 * e
        ang = {lg.side: plant(lg, th, dy, PIVOT) for lg in back}
        for lg in front:
            k = 1 if lg.side.endswith("left") else -1
            paw = math.sin(t * 9 + (0 if k > 0 else 1.6)) * e
            ang[lg.side] = (lg.a[0] + (-60 - 15 * paw) * e, lg.a[1] + (95 + 20 * paw) * e, lg.a[2] + (40 + 15 * paw) * e,
                            (50 + 10 * paw) * e)
        p = legs_pose(LEGS, ang)
        stamp = math.exp(-((t - 2.15) / 0.06) ** 2)
        p["body"] = {"rotation": [th, 0, 0], "position": [0, dy - 0.6 * stamp, 0]}
        neigh = 1.0 if 0.8 < t < 1.75 else 0.0
        trem = math.sin(t * 40) * 3 * neigh
        p["neck"] = {"rotation": [-10 * e + 4 * stamp, 0, 0]}
        p["head"] = {"rotation": [-18 * e + trem * 0.4, 6 * math.sin(t * 3) * e, 0]}
        p["jaw"] = {"rotation": [15 * neigh * e + trem * 0.6, 0, 0]}
        for i, tb in enumerate(TAIL):
            p[tb] = {"rotation": [30 * e if i == 0 else 6 * e, 8 * math.sin(t * 4 - 0.6 * i) * e, 0]}
        for side, sg in SIDES:
            p[f"ear_{side}"] = {"rotation": [0, 0, -10 * sg * e]}
        return p
    bones = sampled(L, 0.05, pose)
    for i, b in enumerate(STREAMS):
        bones.setdefault(b, {})
    return {"animation_length": L, "bones": bones}

def poser():
    from templates import land_mount_poses
    ps = bovine_poser(SID, portrait=(1.0, [-0.6, 1.5, 0]), profile=(0.5, [0, 1.0, 0]))
    return land_mount_poses(ps, SID, first=(0, 0.5, 0), third=(0, 0.7, 0.5))
