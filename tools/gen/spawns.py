# -*- coding: utf-8 -*-
"""Spawn data for the Normandy Fakemons pack (Cobblemon 1.8.x format, checked against the 1.8.2 sources).

Writes into <pack>:
  data/normandy/tags/worldgen/biome/*.json          biome groups ("#normandy:bocage", ...). Every modded biome is
                                                     optional ("required": false), so the pack loads without the mods.
  data/cobblemon/spawn_pool_world/<dex>_<id>.json   single spawns
  data/cobblemon/spawn_pool_world/herds/*.json      herds ("pokemon-herd") and Alphas (bucket "boss")
and adds the 1.8 herd behaviour ("behaviour.herd") to the species that live in herds.

Usage: python3 gen/spawns.py <pack_dir>"""
import json, os, sys, glob

pack = sys.argv[1]
SPECIES = f"{pack}/data/cobblemon/species/normandy"
POOL = f"{pack}/data/cobblemon/spawn_pool_world"
TAGS = f"{pack}/data/normandy/tags/worldgen/biome"

# ------------------------------------------------------------------ biome groups
def mod(ns, *names):
    return [f"{ns}:{n}" for n in names]

GROUPS = {
    # Pastures and hedged meadows of the bocage (temperate grassland, no snow, no savanna)
    "bocage": mod("minecraft", "plains", "sunflower_plains", "meadow")
    + mod("biomesoplenty", "field", "forested_field", "pasture", "grassland", "prairie", "overgrown_greens")
    + mod("biomeswevegone", "prairie", "rose_fields", "temperate_grove", "pumpkin_valley", "coconino_meadow")
    + mod("terralith", "valley_clearing", "lush_valley", "temperate_highlands", "shield_clearing", "blooming_valley")
    + mod("wythers", "harvest_fields", "cool_plains", "cold_plains", "autumnal_plains", "forest_edge",
          "cool_forest_edge", "autumnal_forest_edge", "spring_flower_fields", "highland_plains"),
    # Apple orchards and autumn woods (cider country: Pays d'Auge, Domfrontais)
    "vergers": mod("minecraft", "flower_forest")
    + mod("biomesoplenty", "orchard", "seasonal_forest")
    + mod("biomeswevegone", "orchard")
    + mod("terralith", "blooming_valley", "blooming_plateau")
    + mod("wythers", "harvest_fields", "autumnal_plains", "autumnal_forest", "autumnal_forest_edge",
          "autumnal_flower_forest"),
    # Côte d'Albâtre: chalk cliffs and shingle beaches (Étretat, Fécamp)
    "cote_albatre": ["minecraft:stony_shore", "#c:is_stony_shores"]
    + mod("terralith", "white_cliffs", "gravel_beach")
    + mod("wythers", "calcite_coast", "gravelly_beach", "cold_stony_shore")
    + mod("biomesoplenty", "gravel_beach")
    + mod("biomeswevegone", "dacite_shore"),
    # Cliffs, crags and windswept hills, inland or by the sea
    "falaises": ["#normandy:cote_albatre"]
    + mod("minecraft", "windswept_hills", "windswept_gravelly_hills")
    + mod("terralith", "granite_cliffs", "basalt_cliffs", "yosemite_cliffs", "stony_spires")
    + mod("wythers", "stony_canyon", "cool_stony_canyons", "andesite_crags", "autumnal_crags")
    + mod("biomesoplenty", "crag")
    + mod("biomeswevegone", "dacite_ridges"),
    # Windswept heaths and moors of La Hague
    "landes_hague": mod("minecraft", "windswept_hills", "windswept_gravelly_hills", "meadow")
    + mod("biomesoplenty", "moor", "highland", "rocky_shrubland", "shrubland")
    + mod("terralith", "highlands", "rocky_shrubland", "cold_shrubland", "shield")
    + mod("wythers", "highlands", "highland_plains", "berry_bog")
    + mod("biomeswevegone", "allium_shrubland", "skyris_vale"),
    # Marshes, wet meadows and estuaries (Marais du Cotentin et du Bessin)
    "marais": mod("minecraft", "swamp", "river")
    + mod("biomesoplenty", "marsh", "wetland", "bog")
    + mod("biomeswevegone", "cypress_wetlands", "pale_bog")
    + mod("terralith", "orchid_swamp")
    + mod("wythers", "marsh", "fen", "birch_swamp", "autumnal_swamp", "ancient_oak_swamp"),
    # The bay of Mont-Saint-Michel: beaches, shingle, rocky islets (temperate)
    "baie_du_mont": ["#normandy:cote_albatre"]
    + mod("minecraft", "beach")
    + mod("biomesoplenty", "dune_beach")
    + mod("terralith", "alpha_islands")
    + mod("wythers", "temperate_island", "cold_island", "deepslate_shore"),
    # Frozen plains and tundra for Sleipcheron's winter gallops
    "plaines_givrees": ["#cobblemon:is_snowy_plains", "#cobblemon:is_tundra"]
    + mod("minecraft", "snowy_plains", "ice_spikes")
    + mod("biomesoplenty", "snowy_fir_clearing", "muskeg", "tundra", "auroral_garden")
    + mod("terralith", "wintry_lowlands", "snowy_shield", "ice_marsh")
    + mod("wythers", "snowy_tundra", "snowy_bog", "ice_cap", "crimson_tundra", "tundra")
    + mod("biomeswevegone", "shattered_glacier"),
    # Biomes where the sky lights up with auroras
    "aurores": mod("biomesoplenty", "auroral_garden"),
    # Celestial End (vanilla outer islands, Better End, Biomes O' Plenty)
    "cieux_de_l_end": mod("minecraft", "end_highlands", "end_midlands")
    + mod("betterend", "crystal_mountains", "ice_starfield", "blossoming_spires", "glowing_grasslands",
          "megalake_grove")
    + mod("biomesoplenty", "end_wilds"),
    # Soul-fire Nether: blue flames of the ghost drakkar
    "nether_des_ames": ["#cobblemon:nether/is_soul_fire"]
    + mod("minecraft", "soul_sand_valley")
    + mod("betternether", "soul_plain"),
    # Burning Nether: basalt, magma, eruptions (Alchibec's furnace)
    "nether_brasier": ["#cobblemon:nether/is_basalt"]
    + mod("minecraft", "basalt_deltas")
    + mod("betternether", "magma_land", "flooded_deltas")
    + mod("biomesoplenty", "erupting_inferno"),
}

def tag_entry(v):
    # vanilla biomes and Cobblemon / pack tags are always present; everything else is optional
    if v.startswith(("minecraft:", "#cobblemon:", "#normandy:")):
        return v
    return {"id": v, "required": False}

# ------------------------------------------------------------------ helpers
SKY = {"minSkyLight": 8, "maxSkyLight": 15}
LEGEND = {"archangelis", "sleipcheron", "guillopard"}

def species_json(sid):
    return json.load(open(f"{SPECIES}/{sid}.json", encoding="utf-8"))

def labels_for(sid):
    lab = ["normandy"]
    for l in species_json(sid).get("labels", []):
        if l in ("legendary", "semi_legendary", "restricted") and l not in lab:
            lab.append(l)
    return lab

def B(*biomes):
    return {"biomes": list(biomes)}

def C(*parts, **kw):
    d = {}
    for p in parts:
        d.update(p)
    d.update(kw)
    return d

def M(mult, cond=None, anti=None):
    m = {"multiplier": mult}
    if cond: m["condition"] = cond
    if anti: m["anticondition"] = anti
    return m

NIGHT = lambda x: M(x, {"timeRange": "night"})
RAIN = lambda x: M(x, {"isRaining": True})
STORM = lambda x: M(x, {"isThundering": True})
SNACK = M(2.0, {"isPokeSnack": True})
NEAR = lambda x, *blocks: M(x, {"neededNearbyBlocks": list(blocks)})
IN = lambda x, *biomes: M(x, {"biomes": list(biomes)})

def spawn(sid, n, bucket, level, weight, cond, *, pokemon=None, pos="grounded", presets=("natural",), anti=None,
          mult=()):
    s = {"id": f"{sid}-{n}", "pokemon": pokemon or sid}
    if presets:
        s["presets"] = list(presets)
    s.update({"type": "pokemon", "spawnablePositionType": pos, "bucket": bucket, "level": level, "weight": weight})
    if mult:
        s["weightMultipliers"] = list(mult)
    s["condition"] = cond
    if anti:
        s["anticondition"] = anti
    s["labels"] = labels_for(sid)
    return s

def member(pokemon, weight, level, offset=None, max_times=7, leader=False):
    m = {"pokemon": pokemon, "weight": weight, "levelRange": level}
    if offset:
        m["levelRangeOffset"] = offset
    m.update({"maxTimes": max_times, "isLeader": leader, "isFollower": not leader})
    return m

def herd(hid, sid, bucket, level, weight, size, cond, members, *, pos="grounded", presets=("natural",), anti=None,
         mult=()):
    h = {"id": hid, "presets": list(presets), "type": "pokemon-herd", "bucket": bucket, "spawnablePositionType": pos,
         "maxHerdSize": size, "levelRange": level, "weight": weight}
    if mult:
        h["weightMultipliers"] = list(mult)
    h["condition"] = cond
    if anti:
        h["anticondition"] = anti
    h["herdablePokemon"] = members
    h["labels"] = labels_for(sid)
    return h

def alpha(sid, gem):
    return f"{sid} held_item=cobblemon:{gem}_gem alpha=true"

# ------------------------------------------------------------------ spawns, line by line
FILES = {}       # path -> list of spawns
ENABLED = {}     # path -> bool
HERD_BEHAVIOUR = {}

def add(path, *spawns, enabled=True):
    FILES.setdefault(path, []).extend(spawns)
    ENABLED[path] = enabled

# --- Pomdraco line: apple orchards and hedged woods of the bocage
ORCHARD = C(SKY, B("#normandy:vergers", "#normandy:bocage", "#cobblemon:is_forest"))
NO_ORCHARD = B("#cobblemon:is_freezing", "#cobblemon:is_jungle", "#cobblemon:is_taiga", "#cobblemon:is_spooky",
               "#cobblemon:is_arid")
add("1026_pomdraco.json",
    spawn("pomdraco", 1, "ultra-rare", "5-30", 14.0, ORCHARD, presets=("natural", "treetop"), anti=NO_ORCHARD,
          mult=[IN(2.5, "#normandy:vergers"), M(1.5, {"timeRange": "morning"}), NIGHT(0.5), SNACK]))
add("herds/1026_pomdraco_herd.json",
    herd("pomdraco-herd-1", "pomdraco", "ultra-rare", "5-50", 20.0, 4, ORCHARD, [
        member("pomdraco", 80.0, "8-27", "-3-3", 7),
        member("arboverger", 18.0, "18-37", "-2-4", 2),
        member("cidrac", 2.0, "36-48", "-1-5", 1)], anti=NO_ORCHARD,
        mult=[IN(2.0, "#normandy:vergers"), NIGHT(0.5)]))
add("1027_arboverger.json",
    spawn("arboverger", 1, "ultra-rare", "16-40", 7.0, ORCHARD, anti=NO_ORCHARD,
          mult=[IN(2.5, "#normandy:vergers"), NIGHT(0.5), SNACK]))
add("1028_cidrac.json",
    spawn("cidrac", 1, "ultra-rare", "36-60", 3.0, ORCHARD, anti=NO_ORCHARD,
          mult=[IN(2.5, "#normandy:vergers"), M(1.5, {"timeRange": "dusk"}), SNACK]))
add("herds/1028_cidrac_alpha.json",
    herd("cidrac-alpha-1", "cidrac", "boss", "36-100", 30.0, 7, ORCHARD, [
        member(alpha("cidrac", "grass"), 30.0, "1-100", None, 1, leader=True),
        member("pomdraco", 80.0, "8-27", "-3-3", 7),
        member("arboverger", 70.0, "18-37", "-2-4", 5),
        member("cidrac", 50.0, "36-48", "-1-5", 3)], anti=NO_ORCHARD,
        mult=[IN(2.0, "#normandy:vergers"), NIGHT(0.5)]))
HERD_BEHAVIOUR.update({
    "pomdraco": (4, ["pomdraco", "arboverger", "cidrac"]),
    "arboverger": (5, ["arboverger", "cidrac"]),
    "cidrac": (7, ["cidrac"]),
})

# --- Drakflam line: Viking dragons of the Channel coast; the ghost drakkar sails at night and haunts soul valleys
COAST = C(SKY, B("#normandy:cote_albatre", "#cobblemon:is_coast"))
NO_COAST = B("#cobblemon:is_freezing", "#cobblemon:is_tropical_island")
WRECK = lambda x: M(x, {"structures": ["#minecraft:shipwreck"]})
add("1029_drakflam.json",
    spawn("drakflam", 1, "ultra-rare", "5-30", 14.0, COAST, anti=NO_COAST,
          mult=[IN(2.0, "#normandy:cote_albatre"), NEAR(2.0, "#minecraft:campfires"), RAIN(0.4), SNACK]))
add("herds/1029_drakflam_herd.json",
    herd("drakflam-herd-1", "drakflam", "ultra-rare", "5-50", 20.0, 4, COAST, [
        member("drakflam", 80.0, "8-27", "-3-3", 7),
        member("vikinav", 18.0, "18-37", "-2-4", 2),
        member("drakkarthor", 2.0, "36-48", "-1-5", 1)], anti=NO_COAST,
        mult=[IN(2.0, "#normandy:cote_albatre"), RAIN(0.4)]))
add("1030_vikinav.json",
    spawn("vikinav", 1, "ultra-rare", "16-40", 7.0,
          C(SKY, B("#normandy:cote_albatre", "#normandy:falaises", "#cobblemon:is_coast")), anti=NO_COAST,
          mult=[WRECK(3.0), IN(1.5, "#normandy:falaises"), RAIN(0.5), SNACK]))
add("1031_drakkarthor.json",
    spawn("drakkarthor", 1, "ultra-rare", "36-60", 4.0, C(COAST, timeRange="night"), anti=NO_COAST,
          mult=[WRECK(4.0), RAIN(2.0), SNACK]),
    spawn("drakkarthor", 2, "ultra-rare", "36-60", 3.0,
          C(B("#cobblemon:is_cold_and_temperate_ocean", "#cobblemon:is_cold_ocean"), canSeeSky=True, timeRange="night"),
          pos="surface", presets=("water",), mult=[RAIN(2.0), M(2.0, {"moonPhase": "new"})]),
    spawn("drakkarthor", 3, "ultra-rare", "36-60", 6.0, B("#normandy:nether_des_ames"), presets=()))
add("herds/1031_drakkarthor_alpha.json",
    herd("drakkarthor-alpha-1", "drakkarthor", "boss", "36-100", 25.0, 7, C(COAST, timeRange="night"), [
        member(alpha("drakkarthor", "fire"), 30.0, "1-100", None, 1, leader=True),
        member("drakflam", 80.0, "8-27", "-3-3", 7),
        member("vikinav", 70.0, "18-37", "-2-4", 5),
        member("drakkarthor", 50.0, "36-48", "-1-5", 3)], anti=NO_COAST, mult=[WRECK(3.0)]))
HERD_BEHAVIOUR.update({
    "drakflam": (4, ["drakflam", "vikinav", "drakkarthor"]),
    "vikinav": (5, ["vikinav", "drakkarthor"]),
    "drakkarthor": (7, ["drakkarthor"]),
})

# --- Meuhgousse line: Normande cattle of the bocage, the estuaries and the marshes
PASTURE = C(SKY, B("#normandy:bocage", "#normandy:marais", "#cobblemon:is_plains", "#cobblemon:is_river"))
NO_PASTURE = B("#cobblemon:is_freezing", "#cobblemon:is_arid", "#cobblemon:is_savanna", "#cobblemon:is_jungle")
HAY = lambda x: NEAR(x, "minecraft:hay_block")
add("1032_meuhgousse.json",
    spawn("meuhgousse", 1, "ultra-rare", "5-30", 14.0, PASTURE, anti=NO_PASTURE,
          mult=[IN(2.0, "#normandy:bocage"), HAY(2.0), RAIN(1.5), NIGHT(0.25), SNACK]))
add("herds/1032_meuhgousse_herd.json",
    herd("meuhgousse-herd-1", "meuhgousse", "ultra-rare", "5-50", 24.0, 5, PASTURE, [
        member("meuhgousse", 80.0, "8-27", "-3-3", 7),
        member("bovecume", 18.0, "18-37", "-2-4", 2),
        member("normanguer", 2.0, "36-48", "-1-5", 1)], anti=NO_PASTURE,
        mult=[IN(2.0, "#normandy:bocage"), HAY(2.0), RAIN(1.5), NIGHT(0.25)]))
add("1033_bovecume.json",
    spawn("bovecume", 1, "ultra-rare", "16-40", 7.0,
          C(SKY, B("#normandy:marais", "#cobblemon:is_swamp", "#cobblemon:is_river", "#cobblemon:is_beach")),
          anti=NO_PASTURE,
          mult=[IN(2.0, "#normandy:marais"), STORM(2.5), RAIN(1.5), NEAR(2.0, "minecraft:mud"), SNACK]))
add("1034_normanguer.json",
    spawn("normanguer", 1, "ultra-rare", "36-60", 3.0, C(SKY, B("#normandy:bocage", "#cobblemon:is_plains")),
          anti=NO_PASTURE,
          mult=[IN(2.0, "#normandy:bocage"), HAY(2.0), M(1.5, {"moonPhase": "full"}), NIGHT(0.5), SNACK]))
add("herds/1034_normanguer_alpha.json",
    herd("normanguer-alpha-1", "normanguer", "boss", "36-100", 30.0, 8, PASTURE, [
        member(alpha("normanguer", "water"), 30.0, "1-100", None, 1, leader=True),
        member("meuhgousse", 80.0, "8-27", "-3-3", 7),
        member("bovecume", 70.0, "18-37", "-2-4", 5),
        member("normanguer", 50.0, "36-48", "-1-5", 2)], anti=NO_PASTURE,
        mult=[IN(2.0, "#normandy:bocage"), NIGHT(0.25)]))
HERD_BEHAVIOUR.update({
    "meuhgousse": (7, ["meuhgousse", "bovecume", "normanguer"]),
    "bovecume": (7, ["bovecume", "normanguer"]),
    "normanguer": (9, ["normanguer"]),
})

# --- Étreroch line: birds of the chalk cliffs; the gargoyle also guards End cities
CLIFFS = C(SKY, B("#normandy:cote_albatre", "#normandy:falaises", "#cobblemon:is_coast"))
NO_CLIFFS = B("#cobblemon:is_freezing", "#cobblemon:is_tropical_island")
add("1035_etreroch.json",
    spawn("etreroch", 1, "common", "2-20", 22.0, C(CLIFFS, timeRange="day"), presets=("natural", "treetop"),
          anti=NO_CLIFFS, mult=[IN(2.0, "#normandy:cote_albatre"), RAIN(0.5), SNACK]),
    spawn("etreroch", 2, "common", "2-20", 8.0, C(SKY, B("#cobblemon:is_hills", "#cobblemon:is_mountain"),
          timeRange="day"), presets=("natural", "treetop"), anti=B("#cobblemon:is_freezing", "#cobblemon:is_volcanic"),
          mult=[RAIN(0.5), SNACK]))
add("herds/1035_etreroch_herd.json",
    herd("etreroch-herd-1", "etreroch", "common", "2-40", 30.0, 6, C(CLIFFS, timeRange="day"), [
        member("etreroch", 80.0, "5-24", "-3-3", 7),
        member("archeolithe", 20.0, "20-35", "-2-4", 2)], anti=NO_CLIFFS,
        mult=[IN(2.0, "#normandy:cote_albatre"), RAIN(0.5)]))
add("1036_archeolithe.json",
    spawn("archeolithe", 1, "uncommon", "18-36", 14.0, CLIFFS, presets=("natural", "treetop"), anti=NO_CLIFFS,
          mult=[IN(2.0, "#normandy:cote_albatre"), STORM(1.5), SNACK]),
    spawn("archeolithe", 2, "uncommon", "18-36", 6.0, C(SKY, B("#cobblemon:is_peak", "#cobblemon:is_mountain")),
          presets=("natural", "treetop"), anti=B("#cobblemon:is_volcanic"), mult=[STORM(1.5), SNACK]))
add("1037_gargoylbatre.json",
    spawn("gargoylbatre", 1, "rare", "34-55", 40.0,
          C(SKY, B("#normandy:falaises", "#normandy:cote_albatre", "#cobblemon:is_peak", "#cobblemon:is_mountain")),
          presets=("natural", "treetop"), anti=B("#cobblemon:is_volcanic", "#cobblemon:is_tropical_island"),
          mult=[IN(2.0, "#normandy:cote_albatre"), STORM(2.0), NIGHT(1.5), SNACK]),
    spawn("gargoylbatre", 2, "rare", "40-60", 25.0, C(B("#cobblemon:is_end"), structures=["minecraft:end_city"])))
add("herds/1037_gargoylbatre_alpha.json",
    herd("gargoylbatre-alpha-1", "gargoylbatre", "boss", "34-100", 30.0, 7, CLIFFS, [
        member(alpha("gargoylbatre", "rock"), 30.0, "1-100", None, 1, leader=True),
        member("etreroch", 80.0, "5-24", "-3-3", 7),
        member("archeolithe", 70.0, "20-35", "-2-4", 5),
        member("gargoylbatre", 40.0, "36-48", "-1-5", 2)], anti=NO_CLIFFS,
        mult=[IN(2.0, "#normandy:cote_albatre"), STORM(2.0)]))
HERD_BEHAVIOUR.update({
    "etreroch": (6, ["etreroch", "archeolithe", "gargoylbatre"]),
    "archeolithe": (6, ["archeolithe", "gargoylbatre"]),
    "gargoylbatre": (6, ["gargoylbatre"]),
})

# --- Rousselin line: Roussin sheep of the windswept heaths and cliffs of La Hague
HEATH = C(SKY, B("#normandy:landes_hague", "#normandy:cote_albatre", "#cobblemon:is_highlands", "#cobblemon:is_hills",
                 "#cobblemon:is_coast"))
NO_HEATH = B("#cobblemon:is_freezing", "#cobblemon:is_arid", "#cobblemon:is_jungle", "#cobblemon:is_tropical_island",
             "#cobblemon:is_volcanic")
add("1038_rousselin.json",
    spawn("rousselin", 1, "common", "3-24", 20.0, HEATH, anti=NO_HEATH,
          mult=[IN(2.0, "#normandy:landes_hague"), IN(1.5, "#normandy:cote_albatre"), STORM(1.5), NIGHT(0.25), SNACK]))
add("herds/1038_rousselin_herd.json",
    herd("rousselin-herd-1", "rousselin", "common", "3-45", 40.0, 7, HEATH, [
        member("rousselin", 80.0, "5-24", "-3-3", 7),
        member("roussinage", 20.0, "28-42", "-2-4", 2)], anti=NO_HEATH,
        mult=[IN(2.0, "#normandy:landes_hague"), NIGHT(0.25)]))
add("1039_roussinage.json",
    spawn("roussinage", 1, "uncommon", "28-45", 12.0, HEATH, anti=NO_HEATH,
          mult=[IN(2.0, "#normandy:landes_hague"), STORM(1.5), NIGHT(0.25), SNACK]))
add("herds/1039_roussinage_alpha.json",
    herd("roussinage-alpha-1", "roussinage", "boss", "28-100", 40.0, 8, HEATH, [
        member(alpha("roussinage", "rock"), 30.0, "1-100", None, 1, leader=True),
        member("rousselin", 80.0, "5-24", "-3-3", 7),
        member("roussinage", 60.0, "28-42", "-2-4", 3)], anti=NO_HEATH,
        mult=[IN(2.0, "#normandy:landes_hague"), NIGHT(0.25)]))
HERD_BEHAVIOUR.update({
    "rousselin": (9, ["rousselin", "roussinage"]),
    "roussinage": (9, ["roussinage"]),
})

# --- Homarbleu line: blue lobsters of the cold rocky seabed; they come ashore at night and bite at lines
SEA = B("#cobblemon:is_cold_and_temperate_ocean", "#cobblemon:is_cold_ocean", "#normandy:cote_albatre",
        "#cobblemon:is_coast")
NO_WARM = B("#cobblemon:is_warm_ocean", "#cobblemon:is_lukewarm_ocean", "#cobblemon:is_frozen_ocean",
            "#cobblemon:is_tropical_island")
DEEP = B("#cobblemon:is_deep_ocean", "#cobblemon:is_cold_ocean", "#cobblemon:is_cold_and_temperate_ocean")
RUINS = lambda x: M(x, {"structures": ["#minecraft:ocean_ruin", "#minecraft:shipwreck"]})
LURE = [M(2.0, {"minLureLevel": 2, "maxLureLevel": 2}), M(3.0, {"minLureLevel": 3})]
add("1040_homarbleu.json",
    spawn("homarbleu", 1, "common", "5-28", 14.0, C(SEA, canSeeSky=True), pos="seafloor", presets=("water",),
          anti=NO_WARM, mult=[RUINS(2.0), NIGHT(1.5), SNACK]),
    spawn("homarbleu", 2, "uncommon", "5-28", 10.0, C(SKY, B("#normandy:cote_albatre", "#cobblemon:is_coast"),
          timeRange="night"), anti=B("#cobblemon:is_freezing", "#cobblemon:is_tropical_island"), mult=[RAIN(1.5), SNACK]),
    spawn("homarbleu", 3, "common", "5-28", 30.0, C(SEA, canSeeSky=True), pos="fishing", presets=(), anti=NO_WARM,
          mult=LURE))
add("herds/1040_homarbleu_herd.json",
    herd("homarbleu-herd-1", "homarbleu", "common", "5-48", 12.0, 4, C(SEA, canSeeSky=True), [
        member("homarbleu", 80.0, "8-27", "-3-3", 5),
        member("noroimard", 5.0, "32-44", "-2-4", 1)], pos="seafloor", presets=("water",), anti=NO_WARM,
        mult=[RUINS(2.0), NIGHT(1.5)]))
add("1041_noroimard.json",
    spawn("noroimard", 1, "rare", "32-50", 30.0, C(DEEP, canSeeSky=True), pos="seafloor", presets=("water",),
          anti=NO_WARM, mult=[RUINS(2.0), NIGHT(1.5), SNACK]),
    spawn("noroimard", 2, "rare", "32-50", 20.0, C(DEEP, canSeeSky=True), pos="fishing", presets=(), anti=NO_WARM,
          mult=LURE),
    spawn("noroimard", 3, "rare", "32-50", 15.0, C(SKY, B("#normandy:cote_albatre", "#cobblemon:is_coast"),
          timeRange="night", isThundering=True), anti=B("#cobblemon:is_freezing", "#cobblemon:is_tropical_island")))
add("herds/1041_noroimard_alpha.json",
    herd("noroimard-alpha-1", "noroimard", "boss", "32-100", 30.0, 6, C(DEEP, canSeeSky=True), [
        member(alpha("noroimard", "water"), 30.0, "1-100", None, 1, leader=True),
        member("homarbleu", 80.0, "8-27", "-3-3", 7),
        member("noroimard", 40.0, "32-44", "-2-4", 2)], pos="seafloor", presets=("water",), anti=NO_WARM,
        mult=[RUINS(2.0)]))
HERD_BEHAVIOUR.update({
    "homarbleu": (4, ["homarbleu", "noroimard"]),
    "noroimard": (5, ["noroimard"]),
})

# --- Bolvados line: calvados vessels of dark cellars; they gather near barrels, pottery and lava.
# No "natural" preset underground, so that they also appear in cellars built by players (plank floors).
CELLAR = lambda max_y: {"canSeeSky": False, "maxY": max_y, "biomes": ["#cobblemon:is_overworld"]}
NO_DARK = B("#cobblemon:is_deep_dark")
BARRELS = lambda x: NEAR(x, "minecraft:barrel")
UNDER_ORCHARD = IN(2.0, "#normandy:vergers", "#normandy:bocage")
add("1046_bolvados.json",
    spawn("bolvados", 1, "rare", "15-30", 40.0, CELLAR(50), presets=(), anti=NO_DARK, mult=[BARRELS(4.0), UNDER_ORCHARD, SNACK]))
add("1047_cruchevados.json",
    spawn("cruchevados", 1, "ultra-rare", "30-50", 10.0, CELLAR(30), presets=(), anti=NO_DARK,
          mult=[BARRELS(4.0), NEAR(3.0, "minecraft:decorated_pot"), UNDER_ORCHARD, SNACK]),
    spawn("cruchevados", 2, "ultra-rare", "30-50", 15.0, B("#cobblemon:is_overworld"), presets=("trail_ruins",)))
add("1048_alchibec.json",
    spawn("alchibec", 1, "ultra-rare", "54-65", 4.0, C(CELLAR(0), neededNearbyBlocks=["minecraft:lava"]),
          presets=(), anti=NO_DARK, mult=[BARRELS(3.0)]),
    spawn("alchibec", 2, "ultra-rare", "54-65", 3.0, C(CELLAR(50), neededNearbyBlocks=["minecraft:barrel"]),
          presets=(), anti=NO_DARK, mult=[UNDER_ORCHARD]),
    spawn("alchibec", 3, "ultra-rare", "54-65", 5.0, B("#normandy:nether_brasier"), presets=()))

# --- Legendaries ("legendary" label, 3 perfect IVs, never inside villages)
LEG = ("natural", "wild")
add("1049_archangelis.json",
    spawn("archangelis", 1, "ultra-rare", "70", 5.0, C(SKY, B("#normandy:baie_du_mont"), canSeeSky=True),
          pokemon="archangelis min_perfect_ivs=3", presets=LEG,
          anti=B("#cobblemon:is_freezing", "#cobblemon:is_tropical_island"),
          mult=[M(2.0, {"timeRange": "twilight"}), M(2.5, {"moonPhase": "full"}), M(2.5, {"moonPhase": "new"})]),
    spawn("archangelis", 2, "ultra-rare", "70", 4.0, B("#normandy:cieux_de_l_end"),
          pokemon="archangelis min_perfect_ivs=3", presets=("wild",)))
add("1050_sleipcheron.json",
    spawn("sleipcheron", 1, "ultra-rare", "70", 5.0, C(SKY, B("#normandy:plaines_givrees"), canSeeSky=True,
          timeRange="night"), pokemon="sleipcheron min_perfect_ivs=3", presets=LEG,
          mult=[RAIN(3.0), M(2.0, {"moonPhase": "full"}), IN(2.0, "#normandy:aurores")]),
    spawn("sleipcheron", 2, "ultra-rare", "70", 3.0, C(SKY, B("#normandy:bocage"), canSeeSky=True,
          timeRange="midnight", isThundering=True), pokemon="sleipcheron min_perfect_ivs=3", presets=LEG))
# Guillopard: the sovereign appears only under thunderstorms
add("1051_guillopard.json",
    spawn("guillopard", 1, "ultra-rare", "70", 4.0,
          C(SKY, B("#normandy:bocage", "#normandy:falaises", "#cobblemon:is_hills"), canSeeSky=True,
            isThundering=True), pokemon="guillopard min_perfect_ivs=3", presets=LEG,
          mult=[NEAR(3.0, "minecraft:lightning_rod"), NEAR(2.0, "#minecraft:banners")]))

# ------------------------------------------------------------------ write
def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")

# only the Normandie files are regenerated here (the Monster Hunter ones come from monster_hunter.py)
for old in glob.glob(f"{POOL}/**/*.json", recursive=True):
    if not os.path.basename(old).startswith("11231_"):
        os.remove(old)
for old in glob.glob(f"{TAGS}/*.json"):
    if os.path.basename(old) != "wastelands.json":
        os.remove(old)

for name, values in GROUPS.items():
    dump(f"{TAGS}/{name}.json", {"replace": False, "values": [tag_entry(v) for v in values]})

for path, spawns in FILES.items():
    obj = {"enabled": ENABLED[path], "neededInstalledMods": [], "neededUninstalledMods": [], "spawns": spawns}
    dump(f"{POOL}/{path}", obj)

for sid, (size, leaders) in HERD_BEHAVIOUR.items():
    p = f"{SPECIES}/{sid}.json"
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("behaviour", {})["herd"] = {
        "maxSize": size, "toleratedLeaders": [{"pokemon": l, "tier": i + 1} for i, l in enumerate(leaders)]}
    dump(p, d)

n_sp = sum(1 for v in FILES.values() for s in v if s["type"] == "pokemon")
n_h = sum(1 for v in FILES.values() for s in v if s["type"] == "pokemon-herd")
print(f"{len(GROUPS)} biome groups, {len(FILES)} spawn files, {n_sp} spawns, {n_h} herds/alphas, "
      f"{len(HERD_BEHAVIOUR)} species with herd behaviour")
