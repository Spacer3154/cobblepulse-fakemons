# -*- coding: utf-8 -*-
"""Software preview renderer for the generated Bedrock models (used when Blockbench is not reachable).
Orthographic, textured box-UV cubes, back-face culling, painter's algorithm, simple directional light, and an
animation evaluator (Molang subset + catmull-rom keyframes, rotation / position / scale).

Display convention = Blockbench / in game: Bedrock +X is shown on the screen's RIGHT when the model faces the camera.
Camera: yaw 0 = looking at the model's face (front, -Z), yaw 90 = its right flank... pitch > 0 = from above."""
import json, math
from PIL import Image, ImageDraw
from modelgen import rot_m, compose, translate, apply

# ----------------------------------------------------------------------------- animation evaluation
def molang(expr, t):
    if isinstance(expr, (int, float)):
        return float(expr)
    e = expr.replace("q.r.dive(0)", "1").replace("q.anim_time", "T").replace("math.sin", "S").replace("math.cos", "C")
    e = e.replace("math.clamp", "CL").replace("math.abs", "abs").replace("math.floor", "FL").replace("math.max", "MX") \
         .replace("math.min", "MN").replace("math.pow", "PW").replace("math.sqrt", "SQ")
    return float(eval(e, {"__builtins__": {}}, {"T": t, "S": lambda d: math.sin(math.radians(d)),
                                                 "C": lambda d: math.cos(math.radians(d)), "abs": abs,
                                                 "CL": lambda v, a, b: max(a, min(b, v)), "FL": math.floor, "MX": max,
                                                 "MN": min, "PW": pow, "SQ": math.sqrt}))

def _vec(v, t):
    v = v["post"] if isinstance(v, dict) else v
    return [molang(c, t) for c in v]

def channel(val, t, length, loop):
    if isinstance(val, (int, float, str)):          # uniform value (e.g. "scale": 0)
        v = molang(val, t)
        return [v, v, v]
    if isinstance(val, list):
        return [molang(c, t) for c in val]
    ks = sorted(((float(k), v) for k, v in val.items()), key=lambda kv: kv[0])
    if loop and length:
        t = t % length
    if t <= ks[0][0]:
        return _vec(ks[0][1], t)
    if t >= ks[-1][0]:
        return _vec(ks[-1][1], t)
    for i in range(len(ks) - 1):
        (t0, a), (t1, b) = ks[i], ks[i + 1]
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0
            p0 = _vec(ks[max(0, i - 1)][1], t); p1 = _vec(a, t); p2 = _vec(b, t); p3 = _vec(ks[min(len(ks) - 1, i + 2)][1], t)
            return [0.5 * ((2 * y1) + (-y0 + y2) * u + (2 * y0 - 5 * y1 + 4 * y2 - y3) * u * u + (-y0 + 3 * y1 - 3 * y2 + y3) * u ** 3)
                    for y0, y1, y2, y3 in zip(p0, p1, p2, p3)]

def pose_at(anim, t, layers=()):
    """pose {bone: {rotation, position, scale}} at time t (extra additive animations in `layers`)."""
    pose = {}
    for a in (anim,) + tuple(layers):
        for bone, chans in a["bones"].items():
            for ch in ("rotation", "position", "scale"):
                if ch in chans:
                    v = channel(chans[ch], t, a.get("animation_length", 0), a.get("loop", False))
                    cur = pose.setdefault(bone, {}).get(ch)
                    if cur is None:
                        pose[bone][ch] = v
                    elif ch == "scale":
                        pose[bone][ch] = [x * y for x, y in zip(cur, v)]
                    else:
                        pose[bone][ch] = [x + y for x, y in zip(cur, v)]
    return pose

# ----------------------------------------------------------------------------- geometry
def scale_m(s):
    return [[s[0], 0, 0, 0], [0, s[1], 0, 0], [0, 0, s[2], 0], [0, 0, 0, 1]]

def bone_mats(bones, pose=None, hidden=()):
    pose = pose or {}
    M = {}
    for b in bones:
        d = pose.get(b["name"], {})
        piv = b.get("pivot", [0, 0, 0])
        rot = [a + e for a, e in zip(b.get("rotation", [0, 0, 0]), d.get("rotation", [0, 0, 0]))]
        pos = d.get("position", [0, 0, 0])
        sc = d.get("scale", [1, 1, 1])
        local = compose(translate(*[p + q for p, q in zip(piv, pos)]), rot_m(rot), scale_m(sc), translate(*[-p for p in piv]))
        M[b["name"]] = compose(M[b["parent"]], local) if b.get("parent") else local
    return M

def quads(bones, pose=None, hidden=()):
    M = bone_mats(bones, pose)
    hide = set()
    for b in bones:                                   # hidden parts take their children with them
        if b["name"] in hidden or b.get("parent") in hide:
            hide.add(b["name"])
    out = []
    for b in bones:
        if b["name"] in hide:
            continue
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]
            x0, y0, z0 = o
            x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
            w, h, d = (int(math.ceil(v)) for v in s)
            u, v = c.get("uv", [0, 0])
            cm = M[b["name"]]
            if c.get("rotation"):
                pv = c.get("pivot", b.get("pivot", [0, 0, 0]))
                cm = compose(cm, translate(*pv), rot_m(c["rotation"]), translate(*[-p for p in pv]))
            rects = {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "east": (u, v + d, d, h),
                     "north": (u + d, v + d, w, h), "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}
            def P(face, a, bb):
                return {"north": (x0 + a, y1 - bb, z0), "south": (x1 - a, y1 - bb, z1),
                        "east": (x0, y1 - bb, z1 - a), "west": (x1, y1 - bb, z0 + a),
                        "up": (x0 + a, y1, z1 - bb), "down": (x0 + a, y0, z1 - bb)}[face]
            normals = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (-1, 0, 0), "west": (1, 0, 0),
                       "up": (0, 1, 0), "down": (0, -1, 0)}
            ext = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]),
                   "up": (s[0], s[2]), "down": (s[0], s[2])}
            for face, (fx, fy, fw, fh) in rects.items():
                if fw == 0 or fh == 0:
                    continue
                W, H = ext[face]
                cs = [apply(cm, P(face, a, bb)) for a, bb in ((0, 0), (W, 0), (W, H), (0, H))]
                n0 = apply(cm, (0, 0, 0)); n1 = apply(cm, normals[face])
                n = [q - p for p, q in zip(n0, n1)]
                ln = math.sqrt(sum(x * x for x in n)) or 1
                out.append(((fx, fy, fw, fh), cs, [x / ln for x in n]))
    return out

# ----------------------------------------------------------------------------- camera / raster
class Cam:
    def __init__(self, yaw=-35, pitch=18, scale=8.0, center=(0, 12, 0), size=(480, 360)):
        self.yaw, self.pitch, self.scale, self.center, self.size = yaw, pitch, scale, center, size

    def view(self, p):
        """model point -> (screen x right, screen y up, depth toward the camera)"""
        x, y, z = (p[i] - self.center[i] for i in range(3))
        sx, sy, d = x, y, -z                         # facing the model's front: +X right, front toward us
        ya, pa = math.radians(self.yaw), math.radians(self.pitch)
        sx, d = sx * math.cos(ya) + d * math.sin(ya), -sx * math.sin(ya) + d * math.cos(ya)
        sy, d = sy * math.cos(pa) - d * math.sin(pa), d * math.cos(pa) + sy * math.sin(pa)
        return sx, sy, d

    def screen(self, p):
        sx, sy, d = self.view(p)
        W, H = self.size
        return W / 2 + sx * self.scale, H / 2 - sy * self.scale, d

    def dir(self, n):
        sx, sy, d = n[0], n[1], -n[2]
        ya, pa = math.radians(self.yaw), math.radians(self.pitch)
        sx, d = sx * math.cos(ya) + d * math.sin(ya), -sx * math.sin(ya) + d * math.cos(ya)
        sy, d = sy * math.cos(pa) - d * math.sin(pa), d * math.cos(pa) + sy * math.sin(pa)
        return sx, sy, d

def render(bones, tex, cam, pose=None, hidden=(), bg=(255, 255, 255, 255), ground=True):
    tex = tex.convert("RGBA")
    W, H = cam.size
    img = Image.new("RGBA", (W, H), bg)
    if ground:                                         # soft ground line / shadow ellipse
        d = ImageDraw.Draw(img)
        gx, gy, _ = cam.screen((0, 0, 0))
        d.ellipse([gx - 14 * cam.scale, gy - 3 * cam.scale, gx + 14 * cam.scale, gy + 3 * cam.scale], fill=(232, 232, 236, 255))
    items = []
    for (fx, fy, fw, fh), cs, n in quads(bones, pose, hidden):
        nv = cam.dir(n)
        if nv[2] <= 1e-6:
            continue
        g = [cam.screen(p) for p in cs]
        items.append((sum(p[2] for p in g) / 4, g, (fx, fy, fw, fh), nv))
    items.sort(key=lambda q: q[0])
    # per-pixel depth buffer (as the game does): faces in any order, texels with alpha 0 are cut out
    import numpy as np
    canvas = np.array(img, dtype=np.uint8)
    zbuf = np.full((H, W), -1e9, dtype=np.float64)
    for depth, g, (fx, fy, fw, fh), nv in items:
        P0, P1, P3 = (g[0][0], g[0][1]), (g[1][0], g[1][1]), (g[3][0], g[3][1])
        ax, ay = (P1[0] - P0[0]) / fw, (P1[1] - P0[1]) / fw
        bx, by = (P3[0] - P0[0]) / fh, (P3[1] - P0[1]) / fh
        det = ax * by - bx * ay
        if abs(det) < 1e-9:
            continue
        ia, ib, ic, id_ = by / det, -bx / det, -ay / det, ax / det
        sub = tex.crop((fx, fy, fx + fw, fy + fh))
        a_, b_ = ia, ib
        c_ = -(ia * P0[0] + ib * P0[1])
        d_, e_ = ic, id_
        f_ = -(ic * P0[0] + id_ * P0[1])
        xs = [p[0] for p in g]; ys = [p[1] for p in g]
        bx0, by0 = max(0, int(min(xs)) - 1), max(0, int(min(ys)) - 1)
        bx1, by1 = min(W, int(max(xs)) + 2), min(H, int(max(ys)) + 2)
        if bx1 <= bx0 or by1 <= by0:
            continue
        bw, bh = bx1 - bx0, by1 - by0
        warped = sub.transform((bw, bh), Image.AFFINE,
                               (a_, b_, c_ + a_ * bx0 + b_ * by0, d_, e_, f_ + d_ * bx0 + e_ * by0),
                               resample=Image.NEAREST, fillcolor=(0, 0, 0, 0))
        lit = 0.55 + 0.45 * max(0.0, 0.35 * nv[2] + 0.75 * nv[1] + 0.25)
        lit = min(1.08, lit)
        wa = np.array(warped, dtype=np.float64)
        # depth at each pixel centre: texel coords (u, v) from the inverse map, depth affine in (u, v)
        X, Y = np.meshgrid(np.arange(bx0, bx1) + 0.5, np.arange(by0, by1) + 0.5)
        U = a_ * X + b_ * Y + c_
        V = d_ * X + e_ * Y + f_
        D = g[0][2] + U * (g[1][2] - g[0][2]) / fw + V * (g[3][2] - g[0][2]) / fh
        zb = zbuf[by0:by1, bx0:bx1]
        m = (wa[..., 3] > 0) & (D > zb - 1e-4)
        if not m.any():
            continue
        rgb = np.minimum(255, (wa[..., :3] * lit)).astype(np.uint8)
        cv = canvas[by0:by1, bx0:bx1]
        cv[m, :3] = rgb[m]
        cv[m, 3] = 255
        zb[m] = D[m]
    return Image.fromarray(canvas, "RGBA")

def load_geo(path):
    return json.load(open(path))["minecraft:geometry"][0]["bones"]

def sheet(images, cols, pad=6, bg=(255, 255, 255)):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    out = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), bg)
    for i, im in enumerate(images):
        out.paste(im.convert("RGB"), (pad + (i % cols) * (w + pad), pad + (i // cols) * (h + pad)))
    return out
