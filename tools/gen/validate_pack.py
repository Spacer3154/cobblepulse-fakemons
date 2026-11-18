# -*- coding: utf-8 -*-
"""Independent validation of the finished pack (does not import the generator data).
Usage: python3 -I validate_pack.py <pack_dir> <showdown_dump_dir>"""
import json, os, re, sys, glob
pack, sd = sys.argv[1:3]
errors, info = [], []
E = errors.append

# Reference table transcribed from the PDF (section 2): dex -> (display name, types, BST)
PDF = {
 1026: ("Pomdraco", ["grass"], 310), 1027: ("Arboverger", ["grass", "ground"], 405), 1028: ("Cidrac", ["grass", "dragon"], 530),
 1029: ("Drakflam", ["fire"], 310), 1030: ("Vikinav", ["fire", "steel"], 405), 1031: ("Drakkarthor", ["fire", "ghost"], 530),
 1032: ("Meuhgousse", ["water"], 310), 1033: ("Bovécume", ["water", "ground"], 405), 1034: ("Normanguer", ["water", "fairy"], 530),
 1035: ("Étreroch", ["rock", "flying"], 275), 1036: ("Archéolithe", ["rock", "flying"], 375), 1037: ("Gargoylbâtre", ["rock", "flying"], 495),
 1038: ("Rousselin", ["rock", "normal"], 290), 1039: ("Roussinage", ["rock", "normal"], 480), 1040: ("Homarbleu", ["water", "steel"], 310),
 1041: ("Noroimard", ["water", "steel"], 500), 1046: ("Bolvados", ["water", "fire"], 320),
 1047: ("Cruchevados", ["water", "fire"], 450), 1048: ("Alchibec", ["water", "fire"], 600), 1049: ("Archangelis", ["flying", "fairy"], 580),
 1050: ("Sleipcheron", ["ice", "ground"], 580), 1051: ("Guillopard", ["steel", "electric"], 680),
 # Monster Hunter category (not in the PDF): data given with the original Deviljho files
 11231: ("Deviljho", ["dragon", "dark"], 600),
 11232: ("Glavenus", ["fire", "steel"], 540),          # Fiche Fakemon - Glavenus & Méga-Glavenus
 # Cahier des Charges - CobblePulse-Ecology, 4 Fakemons (dex numbers 11233-11236 chosen with the user)
 11233: ("Zamtrios", ["water", "ice"], 515), 11234: ("Gore Magala", ["dark", "dragon"], 580),
 11235: ("Gore Magala du Chaos", ["dark", "dragon"], 620), 11236: ("Shagaru Magala", ["dragon", "fairy"], 650),
}
CATEGORY = {n: "monster_hunter" for n in range(11231, 11237)}
NO_SPAWN = {11235, 11236}          # obtained only by evolving Gore Magala (cahier des charges: "aucun spawn naturel")

for f in glob.glob(os.path.join(pack, "**/*"), recursive=True):
    if os.path.isdir(f): continue
    rel = os.path.relpath(f, pack)
    if rel.startswith(("data/", "assets/")) and not re.fullmatch(r"[a-z0-9_.\-/]+", rel):
        E(f"invalid resource path: {rel}")
    if f.endswith((".json", ".mcmeta")):
        try: json.load(open(f, encoding="utf-8"))
        except Exception as e: E(f"bad JSON {rel}: {e}")

ps_moves = json.load(open(os.path.join(sd, "moves.json")))
ps_abil = json.load(open(os.path.join(sd, "abilities.json")))
tags = set(open(os.path.join(sd, "biome_tags.txt")).read().split())
presets = set(open(os.path.join(sd, "presets.txt")).read().split())
custom_moves = {os.path.basename(p)[:-3] for p in glob.glob(f"{pack}/data/*/mega_showdown/showdown/moves/*.js")}
custom_abil = {os.path.basename(p)[:-3] for p in glob.glob(f"{pack}/data/*/mega_showdown/showdown/abilities/*.js")}
lang = json.load(open(f"{pack}/assets/cobblemon/lang/fr_fr.json", encoding="utf-8"))
if lang != json.load(open(f"{pack}/assets/cobblemon/lang/en_us.json", encoding="utf-8")):
    E("fr_fr and en_us differ")

species = {}
for f in glob.glob(f"{pack}/data/cobblemon/species/**/*.json", recursive=True):
    species[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
if len(species) != len(PDF): E(f"expected {len(PDF)} species, got {len(species)}")
REQ = ["implemented", "nationalPokedexNumber", "name", "primaryType", "maleRatio", "height", "weight", "pokedex",
       "labels", "abilities", "eggGroups", "baseStats", "evYield", "baseExperienceYield", "experienceGroup",
       "catchRate", "eggCycles", "baseFriendship", "baseScale", "hitbox", "moves"]
used_moves = set()
for sid, d in species.items():
    for k in REQ:
        if k not in d: E(f"{sid}: missing {k}")
    if d.get("implemented") is not True: E(f"{sid}: implemented != true")
    if re.sub(r"[^a-z0-9]+", "", d["name"].lower()) != sid: E(f"{sid}: showdownId mismatch")
    ref = PDF.get(d["nationalPokedexNumber"])
    if not ref: E(f"{sid}: unexpected dex number"); continue
    if lang.get(f"cobblemon.species.{sid}.name") != ref[0]: E(f"{sid}: lang name != PDF {ref[0]}")
    if f"cobblemon.species.{sid}.desc" not in lang: E(f"{sid}: no Pokédex entry in lang")
    types = [d["primaryType"]] + ([d["secondaryType"]] if "secondaryType" in d else [])
    if types != ref[1]: E(f"{sid}: types {types} != PDF {ref[1]}")
    if sum(d["baseStats"].values()) != ref[2]: E(f"{sid}: BST != PDF {ref[2]}")
    if not (0.1 <= d["baseScale"] <= 3): E(f"{sid}: odd baseScale {d['baseScale']}")
    for a in d["abilities"]:
        aid = a[2:] if a.startswith("h:") else a
        if aid in custom_abil:
            if f"cobblemon.ability.{aid}" not in lang: E(f"{sid}: no lang for custom ability {aid}")
        elif aid not in ps_abil: E(f"{sid}: unknown ability {aid}")
    lvl = 0
    for mv in d["moves"]:
        method, mid = mv.split(":")
        if method.isdigit(): lvl += 1
        elif method not in ("egg", "tm", "tutor"): E(f"{sid}: bad learn method {mv}")
        used_moves.add(mid)
        if mid in custom_moves:
            if f"cobblemon.move.{mid}" not in lang: E(f"{sid}: no lang for {mid}")
        elif mid not in ps_moves: E(f"{sid}: unknown move {mid}")
    if lvl < 8: E(f"{sid}: only {lvl} level-up moves")
    for e in d.get("evolutions", []):
        if e["result"] not in species: E(f"{sid}: evolution target {e['result']} missing")
        elif species[e["result"]].get("preEvolution") != sid: E(f"{e['result']}: preEvolution should be {sid}")
if custom_moves - used_moves: E(f"custom moves never learnable: {custom_moves - used_moves}")

# ---------------------------------------------------------------- spawns (Cobblemon 1.8 format)
known_biomes = set(open(os.path.join(sd, "known_biomes.txt")).read().split())   # vanilla 1.21.1 + mods' biome ids
pack_tags = {}
for f in glob.glob(f"{pack}/data/*/tags/worldgen/biome/**/*.json", recursive=True):
    ns = os.path.relpath(f, f"{pack}/data").split(os.sep)[0]
    pack_tags[f"{ns}:" + os.path.relpath(f, f"{pack}/data/{ns}/tags/worldgen/biome")[:-5]] = json.load(open(f))

def check_biome_ref(where, b):
    if b.startswith("#cobblemon:"):
        if b[11:] not in tags: E(f"{where}: unknown Cobblemon biome tag {b}")
    elif b.startswith("#") and ":" in b and b[1:] in pack_tags: pass
    elif b.startswith("#"): E(f"{where}: unknown biome tag {b}")
    elif b not in known_biomes or not b.startswith("minecraft:"):
        E(f"{where}: biome {b} should be vanilla (put modded biomes in an optional tag)")

for t, d in pack_tags.items():
    if d.get("replace"): E(f"tag {t}: replace must be false")
    for v in d["values"]:
        if isinstance(v, str):
            check_biome_ref(f"tag {t}", v)
        else:
            if v.get("required") is not False: E(f"tag {t}: {v} should be optional")
            i = v["id"]
            if i.startswith("#c:"): continue
            if i.startswith("#") or i not in known_biomes: E(f"tag {t}: unknown modded biome {i}")

TIME = {"any", "day", "night", "morning", "noon", "afternoon", "evening", "midnight", "predawn", "dawn", "dusk", "twilight"}
MOON = {"crescent", "gibbous", "full", "new", "quarter", "waxing", "waning"}
COND_KEYS = {"dimensions", "biomes", "moonPhase", "canSeeSky", "minX", "minY", "minZ", "maxX", "maxY", "maxZ",
             "minLight", "maxLight", "minSkyLight", "maxSkyLight", "isRaining", "isThundering", "timeRange",
             "structures", "isSlimeChunk", "markers", "isPokeSnack", "minHeight", "maxHeight", "neededNearbyBlocks",
             "neededBaseBlocks", "minDepth", "maxDepth", "fluid", "fluidIsSource", "minLureLevel", "maxLureLevel",
             "rod", "bait", "rodType"}
STRUCTS = {"#minecraft:shipwreck", "#minecraft:ocean_ruin", "#minecraft:village", "minecraft:trail_ruins",
           "minecraft:end_city"}
BLOCKS = {"minecraft:barrel", "minecraft:hay_block", "minecraft:decorated_pot", "minecraft:mud", "minecraft:lava",
          "minecraft:lightning_rod", "#minecraft:campfires", "#minecraft:banners"}
GEMS = {f"cobblemon:{t}_gem" for t in ("bug dark dragon electric fairy fighting fire flying ghost grass ground ice "
                                        "normal poison psychic rock steel water").split()}
POS = {"grounded", "seafloor", "lavafloor", "submerged", "surface", "fishing"}
BUCKETS = {"common", "uncommon", "rare", "ultra-rare", "boss"}

def check_cond(where, c):
    for k, v in c.items():
        if k not in COND_KEYS: E(f"{where}: unknown condition key {k}")
    for b in c.get("biomes", []): check_biome_ref(where, b)
    if "timeRange" in c and c["timeRange"] not in TIME: E(f"{where}: bad timeRange {c['timeRange']}")
    if "moonPhase" in c and c["moonPhase"] not in MOON: E(f"{where}: bad moonPhase {c['moonPhase']}")
    for s_ in c.get("structures", []):
        if s_ not in STRUCTS: E(f"{where}: unverified structure {s_}")
    for b in c.get("neededNearbyBlocks", []):
        if b not in BLOCKS: E(f"{where}: unverified block {b}")

features = {}
for f in glob.glob(f"{pack}/data/cobblemon/species_features/*.json"):
    fd = json.load(open(f))
    for k in fd["keys"]:
        features[k] = fd
assigned = {}
for f in glob.glob(f"{pack}/data/cobblemon/species_feature_assignments/*.json"):
    fd = json.load(open(f))
    for sp_ in fd["pokemon"]:
        assigned.setdefault(sp_, set()).update(fd["features"])

def check_props(where, props):
    toks = props.split()
    if toks[0] not in species: E(f"{where}: unknown pokemon {toks[0]}")
    for t in toks[1:]:
        k, _, v = t.partition("=")
        if k in features:                      # a species feature of the pack (e.g. zamtrios_form=armor)
            fd = features[k]
            if k not in assigned.get(toks[0], ()): E(f"{where}: feature {k} not assigned to {toks[0]}")
            if fd["type"] == "choice" and v not in fd["choices"]: E(f"{where}: {k}={v} not a choice")
            if fd["type"] == "flag" and v not in ("true", "false"): E(f"{where}: {k}={v}")
        elif k == "held_item":
            if v not in GEMS: E(f"{where}: unknown held item {v}")
        elif k == "alpha":
            if v != "true": E(f"{where}: alpha={v}")
        elif k == "min_perfect_ivs":
            if not v.isdigit() or not 0 < int(v) <= 6: E(f"{where}: min_perfect_ivs={v}")
        else: E(f"{where}: unknown property {t}")
    return toks[0], "alpha=true" in toks

RANGE = re.compile(r"\d+(-\d+)?$")
spawned, spawned_any, ids, herd_members = set(), set(), set(), set()
for f in glob.glob(f"{pack}/data/cobblemon/spawn_pool_world/**/*.json", recursive=True):
    rel = os.path.relpath(f, pack)
    d = json.load(open(f))
    if set(d) - {"enabled", "neededInstalledMods", "neededUninstalledMods", "spawns"}: E(f"{rel}: unknown top-level key")
    enabled = d.get("enabled", True)
    for s in d["spawns"]:
        w = f"{rel}:{s.get('id')}"
        if s["id"] in ids: E(f"{w}: duplicate id")
        ids.add(s["id"])
        for k in ("id", "type", "bucket", "weight", "spawnablePositionType", "condition"):
            if k not in s: E(f"{w}: missing {k}")
        if s.get("bucket") not in BUCKETS: E(f"{w}: bad bucket {s.get('bucket')}")
        if s.get("spawnablePositionType") not in POS: E(f"{w}: bad position type")
        if not s.get("weight", 0) > 0: E(f"{w}: weight must be > 0")
        for p in s.get("presets", []):
            if p not in presets: E(f"{w}: unknown preset {p}")
        check_cond(w, s["condition"])
        if "anticondition" in s: check_cond(w + " (anti)", s["anticondition"])
        for m in s.get("weightMultipliers", []):
            if set(m) - {"multiplier", "condition", "anticondition"} or not m.get("multiplier", 0) > 0:
                E(f"{w}: bad weight multiplier {m}")
            for part in ("condition", "anticondition"):
                if part in m: check_cond(w + " (multiplier)", m[part])
        if s["type"] == "pokemon":
            sid, is_alpha = check_props(w, s["pokemon"])
            if not RANGE.match(s.get("level", "")): E(f"{w}: bad level {s.get('level')}")
            members = [sid]
        elif s["type"] == "pokemon-herd":
            if not RANGE.match(s.get("levelRange", "")): E(f"{w}: bad levelRange")
            leaders = [hm for hm in s["herdablePokemon"] if hm.get("isLeader")]
            if len(leaders) > 1: E(f"{w}: several leaders")
            members = []
            for hm in s["herdablePokemon"]:
                sid, is_alpha = check_props(w, hm["pokemon"])
                members.append(sid)
                herd_members.add(sid)
                if is_alpha != bool(hm.get("isLeader")): E(f"{w}: alpha must be the (only) leader")
                if hm.get("isLeader") == hm.get("isFollower"): E(f"{w}: leader/follower flags")
                if not RANGE.match(hm.get("levelRange", "")): E(f"{w}: bad member levelRange")
                if "levelRangeOffset" in hm and not re.match(r"-?\d+--?\d+$", hm["levelRangeOffset"]):
                    E(f"{w}: bad levelRangeOffset")
            if (s["bucket"] == "boss") != bool(leaders): E(f"{w}: Alpha herds go in the boss bucket, with a leader")
        else:
            E(f"{w}: unknown type {s['type']}"); continue
        for sid in members:
            if sid not in species: continue
            cat = CATEGORY.get(species[sid]["nationalPokedexNumber"], "normandy")
            if cat not in s.get("labels", []): E(f"{w}: missing label {cat}")
            if "legendary" in species[sid]["labels"] and "legendary" not in s.get("labels", []):
                E(f"{w}: legendary spawn without the legendary label")
            spawned_any.add(sid)
            if enabled: spawned.add(sid)
for sid in herd_members:
    if sid in species and "herd" not in species[sid].get("behaviour", {}): E(f"{sid}: in a herd but no behaviour.herd")
for sid, d in species.items():
    for l in d.get("behaviour", {}).get("herd", {}).get("toleratedLeaders", []):
        if l["pokemon"].split()[0] not in species: E(f"{sid}: unknown herd leader {l['pokemon']}")
for sid in species:
    if species[sid]["nationalPokedexNumber"] in NO_SPAWN:
        if sid in spawned_any: E(f"{sid}: should not spawn (evolution only)")
        if not species[sid].get("preEvolution"): E(f"{sid}: no spawn and no pre-evolution")
    elif sid not in spawned_any: E(f"{sid}: no spawn at all")
# forms: aspects come from an assigned species feature, battle forms have a Mega Showdown battle_form entry
choice_aspects = {}
for k, fd in features.items():
    if fd["type"] == "choice":
        for c in fd["choices"]:
            choice_aspects[fd.get("aspectFormat", "{{choice}}").replace("{{choice}}", c)] = k
    else:
        choice_aspects[k] = k
battle_forms = {}
for f in glob.glob(f"{pack}/data/*/mega_showdown/battle_form/*.json"):
    bf = json.load(open(f))
    for p_ in bf["pokemons"]:
        battle_forms.setdefault(p_, set()).add(bf["showdown_form_change_id"])
        for part in ("apply", "revert"):
            for a in bf["aspect_conditions"].get(part, {}).get("aspects", []):
                fk, _, fv = a.partition("=")
                if fk not in features: E(f"battle_form {f}: unknown feature {fk}")
for sid, d in species.items():
    for form in d.get("forms", []):
        if form["name"] == "Mega":
            continue
        for a in form.get("aspects", []):
            if a not in choice_aspects: E(f"{sid} form {form['name']}: aspect {a} comes from no species feature")
            elif choice_aspects[a] not in assigned.get(sid, ()): E(f"{sid}: feature {choice_aspects[a]} not assigned")
        if form["name"].lower() not in battle_forms.get(d["name"], ()):
            E(f"{sid} form {form['name']}: no Mega Showdown battle_form entry")
info.append(f"species with wild spawns: {len(spawned)}/{len(PDF)} (prepared but disabled: "
            f"{sorted(spawned_any - spawned)}), biome groups: {len(pack_tags)}, spawn ids: {len(ids)}")

dex = json.load(open(f"{pack}/data/cobblemon/dexes/normandy.json"))
for e in dex["entries"]:
    sid = e.split(":")[1]
    if sid not in species: E(f"dex entry {e} has no species")
    if not os.path.exists(f"{pack}/data/cobblemon/dex_entries/pokemon/normandy/{sid}.json"): E(f"no dex_entry for {sid}")

A = f"{pack}/assets/cobblemon"
modeled = []
def check_model(sid, folder, base):
    geo_p = f"{A}/bedrock/pokemon/models/{folder}/{base['model'].split(':')[1]}.json"
    if not os.path.exists(geo_p): E(f"{sid}: model file missing"); return
    geo = json.load(open(geo_p))["minecraft:geometry"][0]
    bones = {b["name"] for b in geo["bones"]}
    for b in geo["bones"]:
        if b.get("parent") and b["parent"] not in bones: E(f"{sid}: bone {b['name']} has missing parent {b['parent']}")
        for c in b.get("cubes", []):
            if any(abs(s - round(s)) > 1e-9 for s in c["size"]): E(f"{sid}: non-integer cube size {c['size']} in {b['name']}")
            if not all(isinstance(v, int) for v in c["uv"]): E(f"{sid}: uv must be integers")
            if c["uv"][0] + 2 * (c["size"][0] + c["size"][2]) > geo["description"]["texture_width"] or \
               c["uv"][1] + c["size"][1] + c["size"][2] > geo["description"]["texture_height"]:
                E(f"{sid}: cube UV outside the texture in {b['name']}")
    poser_p = f"{A}/bedrock/pokemon/posers/{folder}/{base['poser'].split(':')[1]}.json"
    if not os.path.exists(poser_p): E(f"{sid}: poser missing"); return
    poser = json.load(open(poser_p))
    if poser["rootBone"] not in bones: E(f"{sid}: rootBone {poser['rootBone']} not in model")
    riding = species[sid].get("riding")
    if riding:                                     # mounts: seats exist as locators, known behaviours and stats
        locs = {k for bb in geo["bones"] for k in bb.get("locators", {})}
        for seat in riding.get("seats", []):
            if seat["locator"] not in locs: E(f"{sid}: seat locator {seat['locator']} not in the model")
            if seat["locator"] not in poser.get("thirdPersonCameraOffset", {}): E(f"{sid}: no camera offset for {seat['locator']}")
        for kind, beh in riding["behaviours"].items():
            if kind not in ("LAND", "AIR", "LIQUID"): E(f"{sid}: riding behaviour {kind}")
            if set(beh["stats"]) != {"ACCELERATION", "JUMP", "SKILL", "SPEED", "STAMINA"}: E(f"{sid}: riding stats")
        if not any("is_ridden" in p.get("condition", "") for p in poser["poses"].values()):
            E(f"{sid}: mount without a ridden pose")
    txt = json.dumps(poser)
    groups = set(re.findall(r"q\.bedrock(?:_quirk|_stateful|_primary)?\('([a-z0-9_]+)'", txt))
    anims = {}
    for g in groups:
        af = f"{A}/bedrock/pokemon/animations/{folder}/{g}.animation.json"
        if not os.path.exists(af): E(f"{sid}: animation file {g} missing"); return
        anims.update(json.load(open(af))["animations"])
    for name, a in anims.items():
        for bn, chans in a.get("bones", {}).items():
            if bn not in bones: E(f"{sid}: animation {name} targets missing bone {bn}")
            for ch, val in chans.items():
                if ch not in ("rotation", "position", "scale"): E(f"{sid}: {name}/{bn} bad channel {ch}")
                if isinstance(val, dict):
                    for t, kv in val.items():
                        float(t)
                        vec = kv["post"] if isinstance(kv, dict) else kv
                        if len(vec) != 3: E(f"{sid}: {name}/{bn} bad keyframe {t}")
                        if isinstance(kv, dict) and kv.get("lerp_mode", "linear") not in ("linear", "catmullrom", "step"):
                            E(f"{sid}: {name}/{bn} bad lerp_mode")
    for grp, an in re.findall(r"q\.bedrock(?:_quirk|_stateful|_primary)?\('([a-z0-9_]+)', '([a-z0-9_]+)'", txt):
        if f"animation.{grp}.{an}" not in anims: E(f"{sid}: poser references missing animation.{grp}.{an}")
    for bn in re.findall(r"q\.look\('([a-z0-9_]+)'\)", txt):
        if bn not in bones: E(f"{sid}: q.look bone {bn} missing")

for rf in glob.glob(f"{A}/bedrock/pokemon/resolvers/*/*.json"):
    r = json.load(open(rf))
    sid = r["species"].split(":")[1]
    folder = os.path.basename(os.path.dirname(rf))
    if sid not in species: E(f"resolver for unknown species {sid}"); continue
    if sid not in modeled: modeled.append(sid)
    for v in r["variations"]:
        tex = v["texture"].split(":")[1] if "texture" in v else None
        if tex and not os.path.exists(f"{A}/{tex}"): E(f"{sid}: texture missing {tex}")
        for layer in v.get("layers", []):
            t = layer["texture"]
            for ref in (t["frames"] if isinstance(t, dict) else [t]):
                if not os.path.exists(f"{A}/{ref.split(':')[1]}"): E(f"{sid}: layer frame missing {ref}")
    for base in [v for v in r["variations"] if "model" in v]:     # every model (base form, mega form...)
        check_model(sid, folder, base)
info.append(f"species with a model: {len(modeled)}/{len(PDF)} {sorted(modeled)}")

for old in ("data/cobblemon/moves", "data/cobblemon/abilities"):
    if os.path.exists(os.path.join(pack, old)): E(f"old non-functional folder still present: {old}")
if json.load(open(f"{pack}/pack.mcmeta"))["pack"]["pack_format"] != 48: E("pack_format should be 48 (MC 1.21.1)")

print("\n".join("INFO  " + i for i in info))
print("\n".join("ERROR " + e for e in errors) if errors else "VALIDATION OK - 0 error")
sys.exit(1 if errors else 0)
