# -*- coding: utf-8 -*-
"""Builds Deviljho + Deviljho Carnage (mega): python3 -I build_deviljho.py <models_dir> <out_pack_dir> <tmp_dir>"""
import json, os, sys
models_dir, out, tmp = sys.argv[1:4]
sys.path.insert(0, models_dir)
import importlib.util, modelgen
from modelgen import clean_molang
spec = importlib.util.spec_from_file_location("deviljho", os.path.join(models_dir, "species", "deviljho.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import portrait_sim

folder = f"{mod.DEX}_{mod.SID}"
A = os.path.join(out, "assets/cobblemon")
tdir = f"{A}/textures/pokemon/{folder}"
os.makedirs(tdir, exist_ok=True); os.makedirs(tmp, exist_ok=True)
for sub in ("models", "animations", "posers", "resolvers"):
    os.makedirs(f"{A}/bedrock/pokemon/{sub}/{folder}", exist_ok=True)

def emit(mega):
    name = "deviljho_carnage" if mega else "deviljho"
    m = mod.build(mega)
    an = mod.anims(m, mega)
    ps = mod.poser(mega)
    bones = m.geo()["minecraft:geometry"][0]["bones"]
    portrait_sim.set_mode("portrait")
    s, tx, ty = portrait_sim.auto_frame(bones, fill=13.5, below=0.5, names=mod.FRAME_BONES)
    qs, qx, qy = portrait_sim.auto_profile(bones)
    ps.update(portraitScale=s, portraitTranslation=[tx, ty, 0], profileScale=qs, profileTranslation=[qx, qy, 0])
    geo = m.geo()
    json.dump(geo, open(f"{A}/bedrock/pokemon/models/{folder}/{name}.geo.json", "w"), indent=2)
    json.dump({"format_version": "1.8.0", "animations": clean_molang(an)},
              open(f"{A}/bedrock/pokemon/animations/{folder}/{name}.animation.json", "w"), indent=2)
    json.dump(ps, open(f"{A}/bedrock/pokemon/posers/{folder}/{name}.json", "w"), indent=2)
    json.dump(geo, open(f"{tmp}/{name}.geo.json", "w"))
    json.dump({"format_version": "1.8.0", "animations": clean_molang(an)}, open(f"{tmp}/{name}.animation.json", "w"))
    pals = (("", mod.MEGA if mega else mod.PAL), ("_shiny", mod.MEGA_SHINY if mega else mod.SHINY))
    layers = {}
    for suf, pal in pals:
        img = m.texture(pal)
        img.save(f"{tdir}/{name}{suf}.png"); img.save(f"{tmp}/{name}{suf}.png")
        frames = m.glow_frames(pal)
        prev = img.copy(); prev.alpha_composite(frames[0]); prev.save(f"{tmp}/{name}{suf}_preview.png")
        kind = "shiny" if suf else "normal"
        refs = []
        os.makedirs(f"{tdir}/glow/{name}_{kind}", exist_ok=True)
        for k, fr in enumerate(frames, 1):
            fr.save(f"{tdir}/glow/{name}_{kind}/{k}.png")
            refs.append(f"cobblemon:textures/pokemon/{folder}/glow/{name}_{kind}/{k}.png")
        layers[suf] = [{"name": "emissive", "texture": {"frames": refs, "fps": 8, "loop": True}, "emissive": True}]
    lo, hi = m.extent(skip=[b.name for b in m.bones if b.name.startswith(mod.HEIGHT_SKIP)])
    print(f"{name}: texture {m.tex_size}, {sum(len(b.cubes) for b in m.bones)} cubes, {len(m.bones)} bones, "
          f"x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.2f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}] portrait {s} {tx} {ty}")
    return name, layers, hi[1]

n0, L0, top0 = emit(False)
n1, L1, top1 = emit(True)
tex = lambda n, s="": f"cobblemon:textures/pokemon/{folder}/{n}{s}.png"
json.dump({"species": "cobblemon:deviljho", "order": 0, "variations": [
    {"aspects": [], "poser": "cobblemon:deviljho", "model": "cobblemon:deviljho.geo", "texture": tex(n0), "layers": L0[""]},
    {"aspects": ["shiny"], "texture": tex(n0, "_shiny"), "layers": L0["_shiny"]}]},
    open(f"{A}/bedrock/pokemon/resolvers/{folder}/0_deviljho_base.json", "w"), indent=2)
json.dump({"species": "cobblemon:deviljho", "order": 1, "variations": [
    {"aspects": ["mega"], "poser": "cobblemon:deviljho_carnage", "model": "cobblemon:deviljho_carnage.geo",
     "texture": tex(n1), "layers": L1[""]},
    {"aspects": ["mega", "shiny"], "texture": tex(n1, "_shiny"), "layers": L1["_shiny"]}]},
    open(f"{A}/bedrock/pokemon/resolvers/{folder}/1_deviljho_carnage.json", "w"), indent=2)
json.dump({"top_base": top0, "top_mega": top1}, open(f"{tmp}/deviljho_tops.json", "w"))
