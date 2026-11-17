# -*- coding: utf-8 -*-
"""Small toolkit to author Cobblemon (Bedrock) models in code:
geometry with box UV, packed + painted texture (normal and shiny), emissive layer frames, molang/keyframe
animations, poser and resolver. Coordinates are Bedrock model units (16 = 1 block), front = -Z, ground = y 0.

Rotation conventions (checked in Blockbench, Bedrock entity format):
  +X : the front (-Z) of the part goes down, points below the pivot go back (+Z)
  +Z : the +X side goes down, points below the pivot go to -X
  +Y : a point on the +X side goes forward (-Z), a point at the back (+Z) goes to +X
       (Cobblemon: ModelPart rotationZYX(z, y, x) in Java space, Y flipped; checked against Blockbench)"""
import json, math, os, random
from PIL import Image

# ---------------------------------------------------------------------------- colours
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)

def shade(c, f):
    """f>1 lighter, f<1 darker"""
    if f >= 1:
        return tuple(min(255, int(v + (255 - v) * (f - 1))) for v in c[:3]) + (c[3],)
    return tuple(max(0, int(v * f)) for v in c[:3]) + (c[3],)

def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)

# ---------------------------------------------------------------------------- model
class Cube:
    def __init__(self, origin, size, paint, rotation=None, pivot=None, inflate=None, name=None):
        self.origin, self.size, self.paint = list(origin), list(size), paint
        self.rotation, self.pivot, self.inflate, self.name = rotation, pivot, inflate, name
        self.uv = None
        # Cobblemon builds cubes with Java box UV using the raw float size: non-integer sizes
        # shift every face by a fraction of a texel, so sizes must be whole numbers (0 = plane).
        if any(abs(s - round(s)) > 1e-9 for s in self.size):
            raise ValueError(f"cube size must be integers, got {self.size}")
        self.size = [int(round(s)) for s in self.size]

    def uv_box(self):
        w, h, d = (int(math.ceil(s)) for s in self.size)
        return w, h, d, 2 * (w + d), h + d

    def texels(self):
        """Yields (face, px_x, px_y, (x, y, z)) for every texel: its centre in model space (Bedrock coordinates,
        rest, before bone rotations). Checked in Blockbench with a marker cube, remembering that Blockbench (like the
        game) displays Bedrock geometry mirrored in X: the 'east' box-UV region lands on the Bedrock -X face.
        Seen from outside every side face is unmirrored; east (-X face) col 0 = back (+Z), west (+X face)
        col 0 = front, north col 0 = -X (viewer's left), south col 0 = +X, row 0 = top; up/down col 0 = -X,
        row 0 = back (+Z)."""
        x0, y0, z0 = self.origin
        w, h, d = self.size
        x1, y1, z1 = x0 + w, y0 + h, z0 + d
        for face, (fx, fy, fw, fh) in self.faces().items():
            for j in range(fh):
                for i in range(fw):
                    u, v = i + 0.5, j + 0.5
                    p = {"north": (x0 + u, y1 - v, z0), "south": (x1 - u, y1 - v, z1),
                         "east": (x0, y1 - v, z1 - u), "west": (x1, y1 - v, z0 + u),
                         "up": (x0 + u, y1, z1 - v), "down": (x0 + u, y0, z1 - v)}[face]
                    yield face, fx + i, fy + j, p

    def faces(self):
        """Pixel rects (x, y, w, h) of each face in the texture, Bedrock box-UV layout."""
        u, v = self.uv
        w, h, d, _, _ = self.uv_box()
        return {
            "up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
            "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
            "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h),
        }

class Bone:
    def __init__(self, name, parent, pivot, rotation=None, cubes=(), locators=None):
        self.name, self.parent, self.pivot = name, parent, list(pivot)
        self.rotation, self.cubes, self.locators = rotation, list(cubes), locators

class Model:
    def __init__(self, sid, dex, tex_size=(64, 64)):
        self.sid, self.dex, self.tex_size = sid, dex, tex_size
        self.bones = []

    def bone(self, name, parent, pivot, rotation=None, cubes=(), locators=None):
        assert all(b.name != name for b in self.bones), f"duplicate bone {name}"
        b = Bone(name, parent, pivot, rotation, cubes, locators)
        self.bones.append(b)
        return b

    def get(self, name):
        return next(b for b in self.bones if b.name == name)

    # -- UV packing (shelf packer, tallest first) --
    def pack(self):
        cubes = [c for b in self.bones for c in b.cubes]
        W, H = self.tex_size
        while True:
            order = sorted(cubes, key=lambda c: (-c.uv_box()[4], -c.uv_box()[3]))
            x = y = shelf = 0
            ok = True
            for c in order:
                bw, bh = c.uv_box()[3:]
                bw, bh = max(bw, 1), max(bh, 1)
                if x + bw > W:
                    x, y, shelf = 0, y + shelf, 0
                if y + bh > H or bw > W:
                    ok = False
                    break
                c.uv = (x, y)
                x += bw
                shelf = max(shelf, bh)
            if ok:
                return
            W, H = (W, H * 2) if H < W else (W * 2, H)
            self.tex_size = (W, H)

    # -- forward kinematics (rest pose + optional per-bone extra rotation / translation) --
    def mats(self, pose=None):
        """World matrix of every bone for a pose (deltas on the rest pose)."""
        pose = pose or {}
        mats = {}
        for b in self.bones:                       # parents are always declared before children
            d = pose.get(b.name)
            rot = b.rotation or [0, 0, 0]
            pos = [0, 0, 0]
            if d:
                rot = [a + e for a, e in zip(rot, d.get("rotation", [0, 0, 0]))]
                pos = d.get("position", [0, 0, 0])
            local = compose(translate(*[p + q for p, q in zip(b.pivot, pos)]), rot_m(rot), translate(*[-p for p in b.pivot]))
            mats[b.name] = compose(mats[b.parent], local) if b.parent else local
        return mats

    def world_points(self, pose=None, only=None):
        """Returns {bone: [corner points of its cubes in world space]} for a pose
        {bone: {"rotation": [x,y,z], "position": [x,y,z]}} added on top of the rest pose."""
        mats = self.mats(pose)
        out = {}
        for b in self.bones:
            if only is not None and b.name not in only:
                continue
            pts = []
            for c in b.cubes:
                cm = mats[b.name]
                if c.rotation:
                    pv = c.pivot or b.pivot
                    cm = compose(cm, translate(*pv), rot_m(c.rotation), translate(*[-p for p in pv]))
                o, s = c.origin, c.size
                for dx in (0, s[0]):
                    for dy in (0, s[1]):
                        for dz in (0, s[2]):
                            pts.append(apply(cm, (o[0] + dx, o[1] + dy, o[2] + dz)))
            out[b.name] = pts
        return out

    def extent(self, pose=None, skip=()):
        pts = [p for n, ps in self.world_points(pose).items() if n not in skip for p in ps]
        return ([min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)])

    # -- exports --
    def geo(self):
        bones = []
        lo, hi = self.extent()
        for b in self.bones:
            jb = {"name": b.name, "pivot": [round(v, 4) for v in b.pivot]}
            if b.parent:
                jb["parent"] = b.parent
            if b.rotation:
                jb["rotation"] = [round(v, 3) for v in b.rotation]
            if b.cubes:
                jb["cubes"] = []
                for c in b.cubes:
                    jc = {"origin": [round(v, 4) for v in c.origin], "size": c.size, "uv": list(c.uv)}
                    if c.inflate:
                        jc["inflate"] = c.inflate
                    if c.rotation:
                        jc["rotation"] = c.rotation
                        jc["pivot"] = [round(v, 4) for v in (c.pivot or b.pivot)]
                    jb["cubes"].append(jc)
            if b.locators:
                jb["locators"] = b.locators
            bones.append(jb)
        width = max(hi[0] - lo[0], hi[2] - lo[2]) / 16
        height = (hi[1] - min(0, lo[1])) / 16
        return {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": f"geometry.{self.sid}", "texture_width": self.tex_size[0],
                            "texture_height": self.tex_size[1],
                            "visible_bounds_width": round(width * 1.6 + 1, 2),
                            "visible_bounds_height": round(height * 1.4 + 0.5, 2),
                            "visible_bounds_offset": [0, round(height / 2, 2), 0]},
            "bones": bones}]}

    def texture(self, palette, seed=7):
        W, H = self.tex_size
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rnd = random.Random(seed)
        mats = self.mats()
        for b in self.bones:
            for c in b.cubes:
                cm = mats[b.name]
                if c.rotation:
                    pv = c.pivot or b.pivot
                    cm = compose(cm, translate(*pv), rot_m(c.rotation), translate(*[-p for p in pv]))
                c.world = cm                       # rest-pose world matrix (for painters working in model space)
                paint_cube(img, c, palette, rnd)
        return img

    def has_glow(self):
        return any(isinstance(c.paint, dict) and (c.paint.get("glow") or c.paint.get("glow_fn"))
                   for b in self.bones for c in b.cubes)

    def glow_frames(self, palette, n=4):
        """Emissive layer frames: only glowing cubes, full flames, a different flicker per frame."""
        return [self.texture(dict(palette, _only_glow=True, _flame_full=True), seed=101 + k) for k in range(n)]

    def bounds(self):
        return self.extent()[1][1]

# ---------------------------------------------------------------------------- matrices (4x4 row-major)
def translate(x, y, z):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]

def rot_m(r):
    """Bedrock rotation (degrees) -> matrix. Applied X first, then Y, then Z (see module docstring)."""
    ax, ay, az = (math.radians(v) for v in r)
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = [[1, 0, 0, 0], [0, cx, sx, 0], [0, -sx, cx, 0], [0, 0, 0, 1]]
    Ry = [[cy, 0, sy, 0], [0, 1, 0, 0], [-sy, 0, cy, 0], [0, 0, 0, 1]]
    Rz = [[cz, sz, 0, 0], [-sz, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return compose(Rz, Ry, Rx)

def compose(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = [[sum(out[i][k] * m[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    return out

def apply(m, p):
    return tuple(m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3] for i in range(3))

# ---------------------------------------------------------------------------- painting
FACE_LIGHT = {"up": 1.12, "north": 1.0, "south": 0.94, "east": 0.97, "west": 0.97, "down": 0.78}

def paint_cube(img, c, pal, rnd):
    p = c.paint
    if callable(p):
        p = {"fn": p}
    if pal.get("_only_glow"):
        if p.get("glow_fn"):                # per-texel emissive (veins, scars) painted on an ordinary cube
            p["glow_fn"](img.load(), c.faces(), pal, rnd, c)
        if not p.get("glow"):
            return
    base_key = p.get("base")
    faces = c.faces()
    px = img.load()
    for face, (x, y, w, h) in faces.items():
        key = p.get(face, base_key)
        if key is None:
            continue
        col = pal[key] if isinstance(key, str) else key
        light = FACE_LIGHT[face] if p.get("shading", True) else 1.0
        grad = p.get("gradient", 0.12) if face in ("north", "south", "east", "west") else 0
        for j in range(h):
            for i in range(w):
                t = (j / max(h - 1, 1)) if h > 1 else 0
                f = light * (1 + grad / 2 - grad * t)
                cc = shade(col, f)
                n = p.get("noise", 5)
                if n:
                    k = rnd.randint(-n, n)
                    cc = tuple(max(0, min(255, v + k)) for v in cc[:3]) + (cc[3],)
                px[x + i, y + j] = cc
    if "belly" in p:
        bcol = pal[p["belly"]]
        rows = p.get("belly_rows", 1)
        x, y, w, h = faces["down"]
        fill(px, x, y, w, h, bcol, 0.92, rnd)
        for fc in ("north", "south", "east", "west"):
            x, y, w, h = faces[fc]
            if fc in p.get("belly_faces", ("east", "west", "north")):
                fill(px, x, y + h - rows, w, rows, bcol, 0.95, rnd)
    if "fn" in p:
        p["fn"](px, faces, pal, rnd)
    if "fn3" in p:                      # painter that also needs the cube (texel -> model-space position)
        p["fn3"](px, faces, pal, rnd, c)

def fill(px, x, y, w, h, col, f=1.0, rnd=None, noise=4):
    for j in range(max(h, 0)):
        for i in range(max(w, 0)):
            cc = shade(col, f)
            if rnd and noise:
                k = rnd.randint(-noise, noise)
                cc = tuple(max(0, min(255, v + k)) for v in cc[:3]) + (cc[3],)
            px[x + i, y + j] = cc

# ---------------------------------------------------------------------------- files
def clean_molang(o):
    """Normalise sign sequences in Molang strings ('+-90' -> '-90', '--1*' -> '1*'): Blockbench flags
    two adjacent operators, and stricter parsers may reject them."""
    import re
    if isinstance(o, str):
        prev = None
        while prev != o:
            prev = o
            o = o.replace("+-", "-").replace("-+", "-").replace("--", "+").replace("++", "+")
            o = re.sub(r"(^|[(,*/])\+", r"\1", o)
        return o
    if isinstance(o, dict):
        return {k: clean_molang(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean_molang(v) for v in o]
    return o

def write_assets(model, out_root, anims, poser, palettes):
    """palettes: {'': normal, '_shiny': shiny}"""
    sid, folder = model.sid, f"{model.dex}_{model.sid}"
    a = os.path.join(out_root, "assets/cobblemon")
    paths = {
        "geo": f"{a}/bedrock/pokemon/models/{folder}/{sid}.geo.json",
        "anim": f"{a}/bedrock/pokemon/animations/{folder}/{sid}.animation.json",
        "poser": f"{a}/bedrock/pokemon/posers/{folder}/{sid}.json",
        "resolver": f"{a}/bedrock/pokemon/resolvers/{folder}/0_{sid}_base.json",
    }
    for p in paths.values():
        os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(model.geo(), open(paths["geo"], "w"), indent=2)
    json.dump({"format_version": "1.8.0", "animations": clean_molang(anims)}, open(paths["anim"], "w"), indent=2)
    json.dump(poser, open(paths["poser"], "w"), indent=2)
    tdir = f"{a}/textures/pokemon/{folder}"
    os.makedirs(tdir, exist_ok=True)
    layers = {}
    for suffix, pal in palettes.items():
        model.texture(pal).save(f"{tdir}/{sid}{suffix}.png")
        if model.has_glow():
            kind = "shiny" if suffix else "normal"
            fdir = f"{tdir}/flame/{kind}"
            os.makedirs(fdir, exist_ok=True)
            refs = []
            for k, img in enumerate(model.glow_frames(pal), 1):
                img.save(f"{fdir}/{k}.png")
                refs.append(f"cobblemon:textures/pokemon/{folder}/flame/{kind}/{k}.png")
            layers[suffix] = [{"name": "emissive", "texture": {"frames": refs, "fps": 8, "loop": True},
                               "emissive": True}]
    variations = [{"aspects": [], "poser": f"cobblemon:{sid}", "model": f"cobblemon:{sid}.geo",
                   "texture": f"cobblemon:textures/pokemon/{folder}/{sid}.png", "layers": layers.get("", [])}]
    if "_shiny" in palettes:
        v = {"aspects": ["shiny"], "texture": f"cobblemon:textures/pokemon/{folder}/{sid}_shiny.png"}
        if "_shiny" in layers:
            v["layers"] = layers["_shiny"]
        variations.append(v)
    json.dump({"species": f"cobblemon:{sid}", "order": 0, "variations": variations},
              open(paths["resolver"], "w"), indent=2)
    paths["texture"] = f"{tdir}/{sid}.png"
    return paths
