# -*- coding: utf-8 -*-
"""Builds the Magala line (species/magala.py): Gore Magala + its Frenzy form, Chaotic Gore Magala, Shagaru Magala
(models, animations, posers, resolvers, textures normal / shiny, emissive layers).
python3 -I build_magala.py <models_dir> <out_pack_dir> <tmp_dir>   (writes <tmp>/<species>_tops.json)"""
import json, os, sys
models_dir, out, tmp = sys.argv[1:4]
sys.path.insert(0, models_dir)
import importlib.util
from modelgen import clean_molang
import portrait_sim
spec = importlib.util.spec_from_file_location("magala", os.path.join(models_dir, "species", "magala.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

A = os.path.join(out, "assets/cobblemon")
os.makedirs(tmp, exist_ok=True)
GLOW = {"goremagala": {"_antenna": True}, "goremagala_frenzy": {"_antenna": True, "_veins": True, "_fglow": True},
        "chaoticgoremagala": {"_antenna": True},
        "shagarumagala": {"_veins": True}}

def emit(name):
    folder = mod.FOLDER[name]
    for sub in ("models", "animations", "posers", "resolvers"):
        os.makedirs(f"{A}/bedrock/pokemon/{sub}/{folder}", exist_ok=True)
    tdir = f"{A}/textures/pokemon/{folder}"
    os.makedirs(tdir, exist_ok=True)
    m = mod.build(name)
    an = mod.anims(name, m)
    ps = mod.poser(name, name)
    geo = m.geo()
    bones = geo["minecraft:geometry"][0]["bones"]
    portrait_sim.set_mode("portrait")
    s, tx, ty = portrait_sim.auto_frame(bones, fill=11.0, below=0.5, names=mod.FRAME_BONES)
    from render3d import pose_at                       # the profile (summary, Pokédex) shows portrait_idle: wings
    qs, qx, qy = portrait_sim.auto_profile(bones, pose=pose_at(an["portrait_idle"], 0.0))   # folded, not the rest fan
    ps = dict({"portraitScale": s, "portraitTranslation": [tx, ty, 0], "profileScale": qs,
               "profileTranslation": [qx, qy, 0]}, **ps)
    anim = {"format_version": "1.8.0", "animations": clean_molang({f"animation.{name}.{k}": v for k, v in an.items()})}
    json.dump(geo, open(f"{A}/bedrock/pokemon/models/{folder}/{name}.geo.json", "w"), indent=1)
    json.dump(anim, open(f"{A}/bedrock/pokemon/animations/{folder}/{name}.animation.json", "w"), indent=1)
    json.dump(ps, open(f"{A}/bedrock/pokemon/posers/{folder}/{name}.json", "w"), indent=2)
    json.dump(geo, open(f"{tmp}/{name}.geo.json", "w")); json.dump(anim, open(f"{tmp}/{name}.animation.json", "w"))
    layers = {}
    for suf, pal in zip(("", "_shiny"), mod.PALETTES[name]):
        img = m.texture(pal)
        img.save(f"{tdir}/{name}{suf}.png"); img.save(f"{tmp}/{name}{suf}.png")
        prev = img.copy()
        if GLOW[name]:
            g = m.texture(dict(pal, _only_glow=True, **GLOW[name]), seed=101)
            g.save(f"{tdir}/{name}{suf}_glow.png"); g.save(f"{tmp}/{name}{suf}_glow.png")
            prev.alpha_composite(g)
            layers[suf] = [{"name": "emissive", "texture": f"cobblemon:textures/pokemon/{folder}/{name}{suf}_glow.png",
                            "emissive": True}]
        prev.save(f"{tmp}/{name}{suf}_preview.png")
    lo, hi = m.extent(skip=[b.name for b in m.bones if b.name.startswith(mod.HEIGHT_SKIP)])
    lo2, hi2 = m.extent()
    print(f"{name}: texture {m.tex_size}, {sum(len(b.cubes) for b in m.bones)} cubes, {len(m.bones)} bones, "
          f"x[{lo2[0]:.1f},{hi2[0]:.1f}] y[{lo2[1]:.1f},{hi2[1]:.1f}] z[{lo2[2]:.1f},{hi2[2]:.1f}] top {hi[1]:.1f}")
    return folder, layers, round(hi[1], 2)

tex = lambda folder, n: f"cobblemon:textures/pokemon/{folder}/{n}.png"
def variation(aspects, name, folder, layers, suf, model=True):
    v = {"aspects": aspects}
    if model:
        v.update(poser=f"cobblemon:{name}", model=f"cobblemon:{name}.geo")
    v["texture"] = tex(folder, name + suf)
    if suf in layers:
        v["layers"] = layers[suf]
    return v

tops = {}
for name in ("goremagala", "goremagala_frenzy", "chaoticgoremagala", "shagarumagala"):
    folder, layers, top = emit(name)
    tops[name] = top
    res = f"{A}/bedrock/pokemon/resolvers/{folder}"
    sid = "goremagala" if name.startswith("goremagala") else name
    if name == "goremagala_frenzy":
        json.dump({"species": f"cobblemon:{sid}", "order": 1, "variations": [
            variation(["magala_frenzy"], name, folder, layers, ""),
            variation(["magala_frenzy", "shiny"], name, folder, layers, "_shiny", model=False)]},
            open(f"{res}/1_goremagala_frenzy.json", "w"), indent=2)
    else:
        json.dump({"species": f"cobblemon:{sid}", "order": 0, "variations": [
            variation([], name, folder, layers, ""), variation(["shiny"], name, folder, layers, "_shiny", model=False)]},
            open(f"{res}/0_{name}_base.json", "w"), indent=2)
json.dump({"top_base": tops["goremagala"], "top_frenzy": tops["goremagala_frenzy"]}, open(f"{tmp}/goremagala_tops.json", "w"))
for n in ("chaoticgoremagala", "shagarumagala"):
    json.dump({"top_base": tops[n]}, open(f"{tmp}/{n}_tops.json", "w"))
