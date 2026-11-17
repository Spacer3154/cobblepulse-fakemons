# -*- coding: utf-8 -*-
"""Build one species: python3 -I build_model.py <models_dir> <species_id> <out_pack_dir> <tmp_dir>
Writes the Cobblemon assets into the pack, updates the species' baseScale/hitbox from the model, and writes
Blockbench import helpers (geo, animation, textures, previews) into tmp_dir."""
import importlib.util, json, os, sys
models_dir, sid, out, tmp = sys.argv[1:5]
sys.path.insert(0, models_dir)
import modelgen  # noqa
spec = importlib.util.spec_from_file_location(sid, os.path.join(models_dir, "species", f"{sid}.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

model = mod.build()
anims = mod.anims()
poser = mod.poser()
if hasattr(mod, "FRAME_BONES"):          # portrait / summary framing computed from the geometry (portrait_sim)
    import portrait_sim
    bones = [b for b in model.geo()["minecraft:geometry"][0]["bones"] if not b["name"].startswith("wing_open")]
    pa = anims.get(f"animation.{sid}.portrait")
    if pa:                                   # a dedicated portrait pose: frame what the party screen will show
        from render3d import pose_at
        pz = pose_at(pa, 0.0)
        for b in bones:
            r = pz.get(b["name"], {}).get("rotation")
            if r:
                b["rotation"] = [x + y for x, y in zip(b.get("rotation", [0, 0, 0]), r)]
    portrait_sim.set_mode("portrait")
    ps, tx, ty = portrait_sim.auto_frame(bones, fill=13.5, below=0.5, names=mod.FRAME_BONES)
    qs, qx, qy = portrait_sim.auto_profile(bones)
    poser.update(portraitScale=ps, portraitTranslation=[tx, ty, 0], profileScale=qs, profileTranslation=[qx, qy, 0])
    print(f"{sid}: portrait {ps} [{tx}, {ty}] profile {qs} [{qx}, {qy}]")
modelgen.write_assets(model, out, anims, poser, {"": mod.PAL, "_shiny": mod.SHINY})

os.makedirs(tmp, exist_ok=True)
json.dump(model.geo(), open(os.path.join(tmp, f"{sid}.geo.json"), "w"))
from modelgen import clean_molang
json.dump({"format_version": "1.8.0", "animations": clean_molang(anims)}, open(os.path.join(tmp, f"{sid}.animation.json"), "w"))
for suffix, pal in (("", mod.PAL), ("_shiny", mod.SHINY)):
    img = model.texture(pal)
    img.save(os.path.join(tmp, f"{sid}{suffix}.png"))
    if model.has_glow():   # preview textures for Blockbench = base + first emissive frame
        prev = img.copy()
        prev.alpha_composite(model.glow_frames(pal)[0])
        prev.save(os.path.join(tmp, f"{sid}{suffix}_preview.png"))

# scale: baseScale makes the model match the Pokédex height; hitbox = unscaled model size
sp_path = os.path.join(out, "data/cobblemon/species/normandy", f"{sid}.json")
sp = json.load(open(sp_path, encoding="utf-8"))
hidden = {b.name for b in model.bones if b.name.startswith("wing_open")}     # spread wings: flight poses only
lo, hi = model.extent(skip=hidden)
solid = [b.name for b in model.bones if any(all(s > 0 for s in c.size) for c in b.cubes) and b.name not in hidden]
slo, shi = model.extent(skip=[b.name for b in model.bones if b.name not in solid])
top = hi[1]
if getattr(mod, "HEIGHT_SKIP", None):     # e.g. horns: the Pokédex height is taken to the top of the head
    _, hh = model.extent(skip=hidden | {b.name for b in model.bones if b.name.startswith(tuple(mod.HEIGHT_SKIP))})
    top = hh[1]
width_u = max(shi[0] - slo[0], min(16, shi[2] - slo[2]))
sp["baseScale"] = round(sp["height"] / 10 / (top / 16) * getattr(mod, "SCALE_BOOST", 1.0), 2)
sp["hitbox"] = {"width": round(min(width_u, top * 1.2) / 16, 2), "height": round(top / 16, 2), "fixed": False}
if hasattr(mod, "HITBOX_WIDTH"):          # long-bodied species: the default (body width) is too narrow
    sp["hitbox"]["width"] = mod.HITBOX_WIDTH
json.dump(sp, open(sp_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{sid}: texture {model.tex_size}, {sum(len(b.cubes) for b in model.bones)} cubes, {len(model.bones)} bones, "
      f"extent x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.2f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}] "
      f"-> baseScale {sp['baseScale']} hitbox {sp['hitbox']}")
