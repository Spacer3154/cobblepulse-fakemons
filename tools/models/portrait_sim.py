# -*- coding: utf-8 -*-
"""Emulates Cobblemon's party-overlay portrait (PartyOverlay -> drawPosablePortrait, Cobblemon 1.8) for a Bedrock
model, and computes portraitScale / portraitTranslation that frame the head.

Transform chain (GUI pixels, y down), from the Cobblemon source:
  origin  = (frame_left + 10.5 - 1, frame_top - 12)
  translate(0, 28 + 2); scale(13); translate(0, -28/18)          (28 = BattleOverlay.PORTRAIT_DIAMETER)
  translate(tx, ty + 1.5*ps, tz - 4); scale(ps); rotY(-32 deg); rotX(5 deg); model (1 unit = 1/16 block)
=> a model point at height h appears at  Y = frame_top - 2.22 + 13*(ty + 1.5*ps) - 13*ps*h/16
Seen from the front, Bedrock +X is on the screen's right (the game, like Blockbench, mirrors Bedrock X); the yaw
turns the face towards the right of the screen.

Usage: python3 -I portrait_sim.py <geo.json> <texture.png> <out.png> [ps tx ty]   (no ps: auto-framing)"""
import json, math, sys
from PIL import Image, ImageDraw

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from modelgen import rot_m, compose, translate, apply

FRAME = 21
YAW = math.radians(32)
TILT = math.radians(5)

def load(geo_path):
    g = json.load(open(geo_path))["minecraft:geometry"][0]
    return g["bones"], (g["description"]["texture_width"], g["description"]["texture_height"])

def mats(bones):
    M = {}
    for b in bones:
        piv = b.get("pivot", [0, 0, 0])
        local = compose(translate(*piv), rot_m(b.get("rotation", [0, 0, 0])), translate(*[-p for p in piv]))
        M[b["name"]] = compose(M[b["parent"]], local) if b.get("parent") else local
    return M

def face_quads(bones):
    """[(bone, face, tex_rect(x,y,w,h), corners[4] in model space (u0v0, u1v0, u1v1, u0v1), normal)]"""
    M = mats(bones)
    out = []
    for b in bones:
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]
            inf = c.get("inflate", 0)
            x0, y0, z0 = o[0] - inf, o[1] - inf, o[2] - inf
            x1, y1, z1 = o[0] + s[0] + inf, o[1] + s[1] + inf, o[2] + s[2] + inf
            w, h, d = (int(math.ceil(v)) for v in s)
            u, v = c.get("uv", [0, 0])
            cm = M[b["name"]]
            if c.get("rotation"):
                pv = c.get("pivot", b.get("pivot", [0, 0, 0]))
                cm = compose(cm, translate(*pv), rot_m(c["rotation"]), translate(*[-p for p in pv]))
            rects = {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "east": (u, v + d, d, h),
                     "north": (u + d, v + d, w, h), "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}
            # texel (col, row) -> model point; corners at (0,0) (W,0) (W,H) (0,H) of each rect (see Cube.texels)
            def P(face, a, bb):
                return {"north": (x0 + a, y1 - bb, z0), "south": (x1 - a, y1 - bb, z1),
                        "east": (x0, y1 - bb, z1 - a), "west": (x1, y1 - bb, z0 + a),
                        "up": (x0 + a, y1, z1 - bb), "down": (x0 + a, y0, z1 - bb)}[face]
            normals = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (-1, 0, 0), "west": (1, 0, 0),
                       "up": (0, 1, 0), "down": (0, -1, 0)}
            for face, (fx, fy, fw, fh) in rects.items():
                if fw == 0 or fh == 0:
                    continue
                W = {"north": x1 - x0, "south": x1 - x0, "east": z1 - z0, "west": z1 - z0, "up": x1 - x0, "down": x1 - x0}[face]
                H = {"north": y1 - y0, "south": y1 - y0, "east": y1 - y0, "west": y1 - y0, "up": z1 - z0, "down": z1 - z0}[face]
                cs = [apply(cm, P(face, a, bb)) for a, bb in ((0, 0), (W, 0), (W, H), (0, H))]
                n0 = apply(cm, (0, 0, 0)); n1 = apply(cm, normals[face])
                n = tuple(q - p for p, q in zip(n0, n1))
                if face in ("north", "south", "east", "west", "up", "down") and 0 in s:
                    pass
                out.append((b["name"], face, (fx, fy, fw, fh), cs, n))
    return out

MODE = {"portrait": dict(yaw=32, tilt=0, ox=FRAME / 2 - 1, oy=-2.22, S=13, box=FRAME),
        # Summary screen (ModelWidget 66x66, baseScale 2 x profile scale 20, euler X 13 / Y 325)
        "profile": dict(yaw=35, tilt=13, ox=33, oy=-10, S=40, box=66)}
CUR = dict(MODE["portrait"])

def set_mode(name):
    CUR.clear(); CUR.update(MODE[name])

def view(p):
    """model point -> (sx right, sy up, depth toward the viewer) in model units"""
    x, y, z = p
    yaw, tilt = math.radians(CUR["yaw"]), math.radians(CUR["tilt"])
    sx, sy, dd = x, y, -z                        # front view: +X right, face toward the viewer
    sx, dd = sx * math.cos(yaw) + dd * math.sin(yaw), -sx * math.sin(yaw) + dd * math.cos(yaw)
    sy, dd = sy * math.cos(tilt) - dd * math.sin(tilt), dd * math.cos(tilt) + sy * math.sin(tilt)
    return sx, sy, dd

def to_gui(p, ps, tx, ty):
    sx, sy, dd = view(p)
    S = CUR["S"]
    X = CUR["ox"] + S * tx + S * ps * sx / 16
    Y = CUR["oy"] + S * (ty + 1.5 * ps) - S * ps * sy / 16
    return X, Y, dd

def head_box(bones, names=("head", "jaw")):
    M = mats(bones)
    pts = []
    for b in bones:
        if b["name"] not in names:
            continue
        for c in b.get("cubes", []):
            if 0 in c["size"]:
                continue
            o, s = c["origin"], c["size"]
            cm = M[b["name"]]
            for dx in (0, s[0]):
                for dy in (0, s[1]):
                    for dz in (0, s[2]):
                        pts.append(view(apply(cm, (o[0] + dx, o[1] + dy, o[2] + dz))))
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return lo, hi

def auto_frame(bones, fill=16.0, below=1.5, names=("head", "jaw")):
    """portraitScale so the head (skull + jaw, without horns/ears) spans `fill` GUI px, centred horizontally and
    `below` px above the frame centre (a little neck shows underneath)."""
    lo, hi = head_box(bones, names)
    span = max(hi[0] - lo[0], hi[1] - lo[1])
    ps = round(min(2.6, max(0.5, fill * 16 / (13 * span))), 2)
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    tx = round(1 / 13 - ps * cx / 16, 2)
    ty = round((FRAME / 2 - below + 2.22) / 13 - 1.5 * ps + ps * cy / 16, 2)
    return ps, tx, ty

def auto_profile(bones, height_fill=21.0, width_fill=58.0, pose=None):
    """profileScale/Translation: feet on the same line as Cobblemon's own models (ty + 1.5*ps = 1.74), model scaled
    to fit the 66 px summary box, centred horizontally. pose: the profile animation's pose ({bone: {rotation,
    position, scale}}, render3d.pose_at) when the geometry's rest layout differs from it (the Magala line's wings
    rest stretched out but the profile shows them folded)."""
    set_mode("profile")
    pts = []
    if pose is not None:
        from render3d import bone_mats
        M = bone_mats(bones, pose)
    else:
        M = mats(bones)
    for b in bones:
        for c in b.get("cubes", []):
            o, s_ = c["origin"], c["size"]
            cm = M[b["name"]]
            if pose is not None and c.get("rotation"):
                pv = c.get("pivot", b.get("pivot", [0, 0, 0]))
                cm = compose(cm, translate(*pv), rot_m(c["rotation"]), translate(*[-q for q in pv]))
            for dx in (0, s_[0]):
                for dy in (0, s_[1]):
                    for dz in (0, s_[2]):
                        pts.append(apply(cm, (o[0] + dx, o[1] + dy, o[2] + dz)))
    v = [view(p) for p in pts]
    h = max(p[1] for p in pts)
    wx = max(q[0] for q in v) - min(q[0] for q in v)
    ps = round(min(1.0, height_fill / h, width_fill * 16 / (40 * wx)), 2)
    cx = (max(q[0] for q in v) + min(q[0] for q in v)) / 2
    tx = round(-ps * cx / 16, 2)
    ty = round(1.74 - 1.5 * ps, 2)
    set_mode("portrait")
    return ps, tx, ty

def render(bones, tex, ps, tx, ty, up=8, frame=True):
    tex = tex.convert("RGBA")
    S = CUR["box"] * up
    canvas = Image.new("RGBA", (S, S), (58, 62, 70, 255) if frame else (0, 0, 0, 0))
    quads = []
    for bone, face, (fx, fy, fw, fh), cs, n in face_quads(bones):
        nv = view(n)
        if nv[2] <= 1e-6:                        # back-face culling (toward the viewer = +depth)
            continue
        g = [to_gui(p, ps, tx, ty) for p in cs]
        depth = sum(p[2] for p in g) / 4
        quads.append((depth, g, (fx, fy, fw, fh), nv))
    quads.sort(key=lambda q: q[0])
    import numpy as np                           # per-pixel depth buffer, as in the game
    cv = np.array(canvas, dtype=np.uint8)
    zbuf = np.full((S, S), -1e9)
    XX, YY = np.meshgrid(np.arange(S) + 0.5, np.arange(S) + 0.5)
    for depth, g, (fx, fy, fw, fh), nv in quads:
        P0, P1, P3 = [(p[0] * up, p[1] * up) for p in (g[0], g[1], g[3])]
        ax, ay = (P1[0] - P0[0]) / fw, (P1[1] - P0[1]) / fw
        bx, by = (P3[0] - P0[0]) / fh, (P3[1] - P0[1]) / fh
        det = ax * by - bx * ay
        if abs(det) < 1e-9:
            continue
        # output (X,Y) -> texel (u,v):  [X-P0] = u*a + v*b
        ia, ib, ic, id_ = by / det, -bx / det, -ay / det, ax / det
        a_ = ia; b_ = ib; c_ = -(ia * P0[0] + ib * P0[1]) + fx
        d_ = ic; e_ = id_; f_ = -(ic * P0[0] + id_ * P0[1]) + fy
        crop_mask = Image.new("L", tex.size, 0)
        ImageDraw.Draw(crop_mask).rectangle([fx, fy, fx + fw - 1, fy + fh - 1], fill=255)
        src = tex.copy()
        src.putalpha(Image.composite(tex.getchannel("A"), Image.new("L", tex.size, 0), crop_mask))
        warped = src.transform((S, S), Image.AFFINE, (a_, b_, c_, d_, e_, f_), resample=Image.NEAREST,
                               fillcolor=(0, 0, 0, 0))
        light = 0.62 + 0.38 * max(0.0, nv[2] * 0.6 + nv[1] * 0.5 + 0.3)
        wa = np.array(warped, dtype=np.float64)
        U = a_ * XX + b_ * YY + c_ - fx
        V = d_ * XX + e_ * YY + f_ - fy
        D = g[0][2] + U * (g[1][2] - g[0][2]) / fw + V * (g[3][2] - g[0][2]) / fh
        m = (wa[..., 3] > 0) & (D > zbuf - 1e-4)
        if not m.any():
            continue
        cv[m, :3] = np.minimum(255, wa[..., :3] * light).astype(np.uint8)[m]
        cv[m, 3] = 255
        zbuf[m] = D[m]
    return Image.fromarray(cv, "RGBA")

if __name__ == "__main__":
    geo, tex_p, out = sys.argv[1:4]
    bones, _ = load(geo)
    if len(sys.argv) > 6:
        ps, tx, ty = (float(v) for v in sys.argv[4:7])
    else:
        ps, tx, ty = auto_frame(bones)
    render(bones, Image.open(tex_p), ps, tx, ty).save(out)
    print(out, ps, tx, ty)
