# -*- coding: utf-8 -*-
"""Monster Hunter category data: Deviljho (species, mega form Deviljho Carnage, Pokédex, spawn) and the
Deviljhonite (Mega Showdown datapack mega stone). Usage: python3 monster_hunter.py <pack_dir> <tops_json> <icon_png>"""
import json, os, shutil, sys

# defaults: run from the repository root
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:] + [None] * 3
pack = args[0] or os.path.join(HERE, "..", "..", "src", "main", "resources")
tops_path = args[1] or os.path.join(HERE, "deviljho_tops.json")
icon = args[2] or os.path.join(HERE, "deviljhonite.png")
tops = json.load(open(tops_path))
D = os.path.join(pack, "data")
A = os.path.join(pack, "assets")

def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

# ------------------------------------------------------------------------------------------------ species
HEIGHT, HEIGHT_MEGA = 55, 64            # decimetres: 5.5 m at the top of the back; Carnage stands taller (6.4 m)
HITBOX_W = 2.0
top, top_m = tops["top_base"], tops["top_mega"]
scale = round(HEIGHT / 10 / (top / 16), 2)
scale_m = round(HEIGHT_MEGA / 10 / (top_m / 16), 2)

MOVES = ["50:soufflecarnage", "1:dragonrage", "1:tackle", "1:poisonfang", "1:focusenergy", "1:dragonbreath", "1:bite", "8:roar",
         "12:assurance", "16:headbutt", "20:hyperfang", "28:workup", "32:jawlock", "36:brutalswing", "40:crunch",
         "44:scaryface", "48:dragonpulse", "52:bodyslam", "54:dracometeor", "58:dragonrush", "60:darkpulse",
         "64:nastyplot", "68:outrage", "72:stompingtantrum",
         "tm:takedown", "tm:scaryface", "tm:protect", "tm:firefang", "tm:thunderfang", "tm:icefang", "tm:thief",
         "tm:firespin", "tm:facade", "tm:bulldoze", "tm:snarl", "tm:mudshot", "tm:rocktomb", "tm:dragontail",
         "tm:endure", "tm:sunnyday", "tm:raindance", "tm:sandstorm", "tm:dig", "tm:zenheadbutt", "tm:bodyslam",
         "tm:reflect", "tm:stompingtantrum", "tm:rockslide", "tm:bodypress", "tm:taunt", "tm:darkpulse",
         "tm:ironhead", "tm:gunkshot", "tm:dragondance", "tm:substitute", "tm:crunch", "tm:heavyslam", "tm:heatwave",
         "tm:earthpower", "tm:nastyplot", "tm:earthquake", "tm:gigaimpact", "tm:outrage", "tm:focusblast",
         "tm:dracometeor"]

species = {
    "implemented": True,
    "nationalPokedexNumber": 11231,
    "name": "Deviljho",
    "primaryType": "dragon",
    "secondaryType": "dark",
    "maleRatio": 0.5,
    "height": HEIGHT,
    "weight": 9500,
    "pokedex": ["cobblemon.species.deviljho.desc"],
    "labels": ["monster_hunter", "custom"],
    "aspects": [],
    "abilities": ["thickfat", "reckless", "h:toxicboost"],          # Isograisse, Téméraire, Rage Poison (caché)
    "eggGroups": ["dragon", "monster"],
    "baseStats": {"hp": 110, "attack": 150, "defence": 70, "special_attack": 110, "special_defence": 90, "speed": 70},
    "evYield": {"hp": 0, "attack": 3, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 270,
    "experienceGroup": "slow",
    "catchRate": 45,
    "eggCycles": 40,
    "baseFriendship": 35,
    "shoulderMountable": False,
    "baseScale": scale,
    "hitbox": {"width": HITBOX_W, "height": round(top / 16, 2), "fixed": False},
    "behaviour": {
        "resting": {"canSleep": True, "light": "0-4", "drowsyChance": 0.02, "rouseChance": 0.006},
        "moving": {"canLook": True, "walk": {"walkSpeed": 0.3},
                   "swim": {"canSwimInWater": True, "canBreatheUnderwater": False, "canSwimInLava": False,
                            "swimSpeed": 0.15}},
        "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False},
    },
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:bone", "quantityRange": "1-3"},
        {"item": "minecraft:beef", "quantityRange": "0-2"},
        {"item": "cobblemon:dragon_fang", "percentage": 8.0},
        {"item": "cobblemon:black_glasses", "percentage": 3.0}]},
    "moves": MOVES,
    "evolutions": [],
    "forms": [{
        "name": "Mega",
        "primaryType": "dragon",
        "secondaryType": "dark",
        "maleRatio": 0.5,
        "height": HEIGHT_MEGA,
        "weight": 9999,
        "pokedex": ["cobblemon.species.deviljho-mega.desc"],
        "labels": ["monster_hunter", "custom", "mega"],
        "aspects": ["mega"],
        "abilities": ["ragebrulante"],
        "baseStats": {"hp": 110, "attack": 190, "defence": 90, "special_attack": 125, "special_defence": 100,
                      "speed": 85},
        "baseExperienceYield": 320,
        "baseScale": scale_m,
        "hitbox": {"width": round(HITBOX_W * 1.05, 2), "height": round(top_m / 16, 2), "fixed": False},
        "battleOnly": True,
        "dynamaxBlocked": True,
        "lightingData": {"lightLevel": 9, "liquidGlowMode": "LAND"},
    }],
}
dump(f"{D}/cobblemon/species/monster_hunter/deviljho.json", species)
# Mega Showdown's "mega_evolution" choice feature (aspect mega_evolution=mega -> aspect "mega" -> form "Mega")
dump(f"{D}/cobblemon/species_feature_assignments/monster_hunter_mega.json",
     {"pokemon": ["deviljho"], "features": ["mega_evolution"]})

# ------------------------------------------------------------------------------------------------ Pokédex
dump(f"{D}/cobblemon/dex_entries/pokemon/monster_hunter/deviljho.json", {
    "id": "cobblemon:deviljho", "speciesId": "cobblemon:deviljho", "displayAspects": [], "conditionAspects": [],
    "forms": [{"displayForm": "Normal", "unlockForms": ["Normal"]},
              {"displayForm": "Mega", "unlockForms": ["Mega"]}],
    "variations": []})
dump(f"{D}/cobblemon/dexes/monster_hunter.json", {
    "type": "cobblemon:simple_pokedex_def", "id": "cobblemon:monster_hunter", "sortOrder": 13,
    "entries": ["cobblemon:deviljho"]})
dump(f"{D}/cobblemon/dex_additions/monster_hunter_national.json",
     {"dexId": "cobblemon:national", "entries": ["cobblemon:monster_hunter"]})

# ------------------------------------------------------------------------------------------------ spawn
# Biomes O' Plenty wastelands (Wasteland + Wasteland Steppe), ultra-rare. The tag lists them as optional entries,
# so the spawn simply never happens without Biomes O' Plenty.
dump(f"{D}/normandy/tags/worldgen/biome/wastelands.json", {"replace": False, "values": [
    {"id": "biomesoplenty:wasteland", "required": False},
    {"id": "biomesoplenty:wasteland_steppe", "required": False}]})
spawn = {
    "enabled": True, "neededInstalledMods": ["biomesoplenty"], "neededUninstalledMods": [],
    "spawns": [
        {"id": "deviljho-1", "pokemon": "deviljho", "presets": ["natural", "wild"], "type": "pokemon",
         "spawnablePositionType": "grounded", "bucket": "ultra-rare", "level": "50-70", "weight": 1.0,
         "condition": {"biomes": ["#normandy:wastelands"], "canSeeSky": True},
         "weightMultipliers": [
             {"multiplier": 1.5, "condition": {"timeRange": "night"}},
             {"multiplier": 2.0, "condition": {"isThundering": True}}],
         "labels": ["monster_hunter"]},
    ]}
dump(f"{D}/cobblemon/spawn_pool_world/11231_deviljho.json", spawn)

# ------------------------------------------------------------------------------------------------ Mega Showdown
dump(f"{D}/normandy/mega_showdown/mega/deviljhonite.json", {
    "showdown_id": "deviljhonite", "pokemons": ["Deviljho"],
    "aspect_conditions": {"apply": {"aspects": ["mega_evolution=mega"]},
                          "revert": {"aspects": ["mega_evolution=none"]}}})
write(f"{D}/normandy/mega_showdown/showdown/held_items/deviljhonite.js", """({
  name: "Deviljhonite",
  spritenum: 0,
  megaStone: { "Deviljho": "Deviljho-Mega" },
  itemUser: ["Deviljho"],
  onTakeItem(item, source) {
    return !item.megaStone?.[source.baseSpecies.baseSpecies];
  },
  num: 7901,
  gen: 9,
  isNonstandard: "Past",
})
""")
old = f"{D}/normandy/mega_showdown/showdown/abilities/faimdevorante.js"
if os.path.exists(old):
    os.remove(old)
# Rage Brulante (mega): stat drops from other Pokemon are blocked (like Clear Body, Intimidate included);
# +1 Attack every time it takes a critical hit or a super-effective hit.
write(f"{D}/normandy/mega_showdown/showdown/abilities/ragebrulante.js", """{
  onTryBoost(boost, target, source, effect) {
    if (source && target === source) return;
    let showMsg = false;
    let i;
    for (i in boost) {
      if (boost[i] < 0) {
        delete boost[i];
        showMsg = true;
      }
    }
    if (showMsg && !effect.secondaries && effect.id !== 'octolock') {
      this.add('-fail', target, 'unboost', '[from] ability: Rage Brulante', '[of] ' + target);
    }
  },
  onDamagingHit(damage, target, source, move) {
    if (!target.hp) return;
    const hit = target.getMoveHitData(move);
    if (hit.crit || hit.typeMod > 0) {
      this.boost({ atk: 1 }, target, target);
    }
  },
  flags: { breakable: 1 },
  name: "Rage Brulante",
  rating: 4,
  num: 7807
}
""")
# Souffle Carnage (signature): Dragon, 85 power; physical or special like Shell Side Arm (whichever would hurt the
# target more, given its Defense and Special Defense); always lowers the target's Defense.
write(f"{D}/normandy/mega_showdown/showdown/moves/soufflecarnage.js", """{
  num: 7708,
  accuracy: 100,
  basePower: 85,
  category: "Special",
  name: "Souffle Carnage",
  pp: 10,
  priority: 0,
  flags: { protect: 1, mirror: 1, metronome: 1 },
  onModifyMove(move, pokemon, target) {
    if (!target) return;
    const atk = pokemon.getStat('atk', false, true);
    const spa = pokemon.getStat('spa', false, true);
    const def = target.getStat('def', false, true);
    const spd = target.getStat('spd', false, true);
    const physical = Math.floor(Math.floor(Math.floor(Math.floor(2 * pokemon.level / 5 + 2) * 85 * atk) / def) / 50);
    const special = Math.floor(Math.floor(Math.floor(Math.floor(2 * pokemon.level / 5 + 2) * 85 * spa) / spd) / 50);
    if (physical > special || (physical === special && this.random(2) === 0)) {
      move.category = 'Physical';
    }
  },
  secondary: {
    chance: 100,
    boosts: { def: -1 }
  },
  target: "normal",
  type: "Dragon",
  contestType: "Tough"
}
""")

# The Deviljhonite is a real item of the mod: normandy_fakemons:deviljhonite, registered in code
# (src/main/java/fr/cobblepulse/fakemons) with Mega Showdown's two components set by default
# (registry_type_component = "mega", registry_location_component = normandy:deviljhonite).
# Legacy: the Deviljhonites crafted with mod 2.0 - 2.2 were echo shards carrying those components; they still work and
# keep their icon (custom_model_data 31231 on the echo shard model).
CMD = 31231
ITEM = "normandy_fakemons:deviljhonite"
dump(f"{D}/normandy/recipe/deviljhonite.json", {
    "type": "minecraft:crafting_shaped", "category": "misc",
    "pattern": [" f ", "bmb", " g "],
    "key": {"f": {"item": "cobblemon:dragon_fang"}, "b": {"item": "minecraft:bone_block"},
            "m": {"item": "mega_showdown:mega_stone"}, "g": {"item": "cobblemon:black_glasses"}},
    "result": {"id": ITEM, "count": 1}})
write(f"{D}/normandy/function/give_deviljhonite.mcfunction",
      "# /function normandy:give_deviljhonite  - gives a Deviljhonite to the player running it\n"
      f"give @s {ITEM} 1\n")
# unlock the recipe in the recipe book as soon as a Mega Stone is picked up
dump(f"{D}/normandy/advancement/recipes/deviljhonite.json", {
    "parent": "minecraft:recipes/root",
    "criteria": {"has_mega_stone": {"trigger": "minecraft:inventory_changed",
                                    "conditions": {"items": [{"items": "mega_showdown:mega_stone"}]}},
                 "has_the_recipe": {"trigger": "minecraft:recipe_unlocked", "conditions": {"recipe": "normandy:deviljhonite"}}},
    "requirements": [["has_mega_stone", "has_the_recipe"]],
    "rewards": {"recipes": ["normandy:deviljhonite"]}})
# a Mega Stone for every mod that looks at Mega Showdown's tag
dump(f"{D}/mega_showdown/tags/item/mega_stone.json", {"replace": False, "values": [ITEM]})

# item model + icon
dump(f"{A}/normandy_fakemons/models/item/deviljhonite.json",
     {"parent": "minecraft:item/generated", "textures": {"layer0": "normandy_fakemons:item/deviljhonite"}})
os.makedirs(f"{A}/normandy_fakemons/textures/item", exist_ok=True)
shutil.copy(icon, f"{A}/normandy_fakemons/textures/item/deviljhonite.png")
# legacy echo-shard Deviljhonites (mod 2.0 - 2.2)
dump(f"{A}/minecraft/models/item/echo_shard.json", {
    "parent": "minecraft:item/generated", "textures": {"layer0": "minecraft:item/echo_shard"},
    "overrides": [{"predicate": {"custom_model_data": CMD}, "model": "normandy:item/deviljhonite"}]})
dump(f"{A}/normandy/models/item/deviljhonite.json",
     {"parent": "minecraft:item/generated", "textures": {"layer0": "normandy_fakemons:item/deviljhonite"}})
old_png = f"{A}/normandy/textures/item/deviljhonite.png"
if os.path.exists(old_png):
    os.remove(old_png)
    try:
        os.removedirs(os.path.dirname(old_png))
    except OSError:
        pass

# ------------------------------------------------------------------------------------------------ lang
LANG = {
    "fr_fr": {
        "cobblemon.species.deviljho.name": "Deviljho",
        "cobblemon.species.deviljho.desc": "Une wyverne brute à l'appétit insatiable qui erre de territoire en territoire et dévore tout ce qui bouge. Sa mâchoire colossale broie la roche et ses muscles brûlent tant d'énergie qu'il doit chasser sans relâche.",
        "cobblemon.species.deviljho-mega.desc": "Deviljho Carnage. La Deviljhonite pousse sa rage à son paroxysme : ses muscles enflent, son dos se fend de veines incandescentes et une énergie draconique rouge sang crépite autour de lui. Plus rien ne peut rassasier sa faim.",
        "cobblemon.ui.pokedex.info.form.deviljho-mega": "Carnage",
        "cobblemon.ability.ragebrulante": "Rage Brûlante",
        "cobblemon.ability.ragebrulante.desc": "Les autres Pokémon ne peuvent pas baisser ses statistiques. Son Attaque augmente chaque fois qu'il subit un coup critique ou une capacité super efficace.",
        "cobblemon.move.soufflecarnage": "Souffle Carnage",
        "cobblemon.move.soufflecarnage.desc": "Le lanceur crache un torrent d'énergie draconique qui baisse la Défense de la cible. Physique ou spéciale : la catégorie qui fait le plus de dégâts à la cible.",
        "item.normandy_fakemons.deviljhonite": "Deviljhonite",
        "item.normandy_fakemons.deviljhonite.lore": "Permet à Deviljho de méga-évoluer en Deviljho Carnage.",
        "item.normandy_fakemons.deviljhonite.lore2": "Elle palpite d'une faim sans fin.",
        "itemGroup.normandy_fakemons.fakemons": "Normandy Fakemons",
        "item.normandy.deviljhonite": "Deviljhonite",
        "item.normandy.deviljhonite.lore": "Permet à Deviljho de méga-évoluer en Deviljho Carnage.",
        "item.normandy.deviljhonite.lore2": "Elle palpite d'une faim sans fin.",
    },
    "en_us": {
        "cobblemon.species.deviljho.name": "Deviljho",
        "cobblemon.species.deviljho.desc": "A brute wyvern with an insatiable appetite that roams from territory to territory, devouring anything that moves. Its colossal jaw grinds rock, and its muscles burn so much energy that it must hunt without rest.",
        "cobblemon.species.deviljho-mega.desc": "Deviljho Carnage. The Deviljhonite drives its rage to the limit: its muscles swell, its back splits with glowing veins and blood-red dragon energy crackles around it. Nothing can sate its hunger any more.",
        "cobblemon.ui.pokedex.info.form.deviljho-mega": "Carnage",
        "cobblemon.ability.ragebrulante": "Burning Rage",
        "cobblemon.ability.ragebrulante.desc": "Other Pokémon can't lower its stats. Its Attack rises whenever it takes a critical hit or a super-effective move.",
        "cobblemon.move.soufflecarnage": "Carnage Breath",
        "cobblemon.move.soufflecarnage.desc": "The user spews a torrent of dragon energy that lowers the target's Defense. Physical or special: whichever deals more damage to the target.",
        "item.normandy.deviljhonite": "Deviljhonite",
        "item.normandy.deviljhonite.lore": "Allows Deviljho to Mega Evolve into Deviljho Carnage.",
        "item.normandy.deviljhonite.lore2": "It throbs with an endless hunger.",
    },
}
LANG["en_us"] = LANG["fr_fr"]          # this pack shows the French texts on every client
for lang, entries in LANG.items():
    p = f"{A}/cobblemon/lang/{lang}.json"
    cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    for gone in ("cobblemon.ability.faimdevorante", "cobblemon.ability.faimdevorante.desc"):
        cur.pop(gone, None)
    cur.update(entries)
    dump(p, cur)
print(f"deviljho: baseScale {scale} (mega {scale_m}), hitbox height {round(top / 16, 2)}")
print("deviljhonite:", ITEM)
