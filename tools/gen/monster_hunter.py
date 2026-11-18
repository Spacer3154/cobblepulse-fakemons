# -*- coding: utf-8 -*-
"""Monster Hunter category data: Deviljho (+ Deviljho Carnage) and Glavenus (+ Glavenus Lame-Chaos): species with their
mega form, Pokédex, spawns, Mega Showdown data (mega registry entries, mega stones, custom abilities and moves), the
mega stones' recipes, item models and texts.
Usage (from the repository root): python3 tools/gen/monster_hunter.py [pack_dir]
Reads tools/gen/<species>_tops.json (model heights, written by tools/models/build_mh.py) and <stone>.png (item icons)."""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
pack = (sys.argv[1:] or [None])[0] or os.path.join(HERE, "..", "..", "src", "main", "resources")
D = os.path.join(pack, "data")
A = os.path.join(pack, "assets")
MOD = "cobblepulse_ecology"            # item namespace (the mod id); data stays in the "normandy" namespace
LEGACY_MOD = "normandy_fakemons"       # mod id up to 2.3: its Deviljhonite id is still registered


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)


def tops(sid):
    return json.load(open(os.path.join(HERE, f"{sid}_tops.json")))


def scale_for(height_dm, top_px):
    return round(height_dm / 10 / (top_px / 16), 2)


LANG = {}          # fr_fr entries (en_us = the same texts: this pack shows French on every client)
SPECIES_IDS = []


def species_file(sid, d):
    dump(f"{D}/cobblemon/species/monster_hunter/{sid}.json", d)
    dump(f"{D}/cobblemon/dex_entries/pokemon/monster_hunter/{sid}.json", {
        "id": f"cobblemon:{sid}", "speciesId": f"cobblemon:{sid}", "displayAspects": [], "conditionAspects": [],
        "forms": [{"displayForm": "Normal", "unlockForms": ["Normal"]},
                  {"displayForm": "Mega", "unlockForms": ["Mega"]}],
        "variations": []})
    SPECIES_IDS.append(sid)


def mega_stone(stone, species_name, *, num, recipe, lore, lore2, legacy=False):
    """Mega Showdown registry entry + held item, the real item of the mod (model, icon, texts), recipe, function,
    recipe-book unlock."""
    sid = species_name.lower()
    dump(f"{D}/normandy/mega_showdown/mega/{stone}.json", {
        "showdown_id": stone, "pokemons": [species_name],
        "aspect_conditions": {"apply": {"aspects": ["mega_evolution=mega"]},
                              "revert": {"aspects": ["mega_evolution=none"]}}})
    write(f"{D}/normandy/mega_showdown/showdown/held_items/{stone}.js", f"""({{
  name: "{stone.capitalize()}",
  spritenum: 0,
  megaStone: {{ "{species_name}": "{species_name}-Mega" }},
  itemUser: ["{species_name}"],
  onTakeItem(item, source) {{
    return !item.megaStone?.[source.baseSpecies.baseSpecies];
  }},
  num: {num},
  gen: 9,
  isNonstandard: "Past",
}})
""")
    item = f"{MOD}:{stone}"
    pattern, key = recipe
    dump(f"{D}/normandy/recipe/{stone}.json", {"type": "minecraft:crafting_shaped", "category": "misc",
                                               "pattern": pattern, "key": {k: {"item": v} for k, v in key.items()},
                                               "result": {"id": item, "count": 1}})
    write(f"{D}/normandy/function/give_{stone}.mcfunction",
          f"# /function normandy:give_{stone}  - gives a {stone.capitalize()} to the player running it\n"
          f"give @s {item} 1\n")
    dump(f"{D}/normandy/advancement/recipes/{stone}.json", {
        "parent": "minecraft:recipes/root",
        "criteria": {"has_mega_stone": {"trigger": "minecraft:inventory_changed",
                                        "conditions": {"items": [{"items": "mega_showdown:mega_stone"}]}},
                     "has_the_recipe": {"trigger": "minecraft:recipe_unlocked", "conditions": {"recipe": f"normandy:{stone}"}}},
        "requirements": [["has_mega_stone", "has_the_recipe"]],
        "rewards": {"recipes": [f"normandy:{stone}"]}})
    dump(f"{A}/{MOD}/models/item/{stone}.json",
         {"parent": "minecraft:item/generated", "textures": {"layer0": f"{MOD}:item/{stone}"}})
    os.makedirs(f"{A}/{MOD}/textures/item", exist_ok=True)
    shutil.copy(os.path.join(HERE, f"{stone}.png"), f"{A}/{MOD}/textures/item/{stone}.png")
    LANG.update({f"item.{MOD}.{stone}": stone.capitalize(), f"item.{MOD}.{stone}.lore": lore,
                 f"item.{MOD}.{stone}.lore2": lore2})
    if legacy:            # same item under the 2.3 id (normandy_fakemons:<stone>)
        dump(f"{A}/{LEGACY_MOD}/models/item/{stone}.json",
             {"parent": "minecraft:item/generated", "textures": {"layer0": f"{MOD}:item/{stone}"}})
        LANG.update({f"item.{LEGACY_MOD}.{stone}": stone.capitalize(), f"item.{LEGACY_MOD}.{stone}.lore": lore,
                     f"item.{LEGACY_MOD}.{stone}.lore2": lore2})
    return item


BEHAVIOUR = lambda walk: {
    "resting": {"canSleep": True, "light": "0-4", "drowsyChance": 0.02, "rouseChance": 0.006},
    "moving": {"canLook": True, "walk": {"walkSpeed": walk},
               "swim": {"canSwimInWater": True, "canBreatheUnderwater": False, "canSwimInLava": False, "swimSpeed": 0.15}},
    "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False}}

# ================================================================================================ Deviljho
HEIGHT, HEIGHT_MEGA = 55, 64            # decimetres: 5.5 m at the top of the back; Carnage stands taller (6.4 m)
t = tops("deviljho")
species_file("deviljho", {
    "implemented": True, "nationalPokedexNumber": 11231, "name": "Deviljho",
    "primaryType": "dragon", "secondaryType": "dark", "maleRatio": 0.5,
    "height": HEIGHT, "weight": 9500, "pokedex": ["cobblemon.species.deviljho.desc"],
    "labels": ["monster_hunter", "custom"], "aspects": [],
    "abilities": ["thickfat", "reckless", "h:toxicboost"],          # Isograisse, Téméraire, Rage Poison (caché)
    "eggGroups": ["dragon", "monster"],
    "baseStats": {"hp": 110, "attack": 150, "defence": 70, "special_attack": 110, "special_defence": 90, "speed": 70},
    "evYield": {"hp": 0, "attack": 3, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 270, "experienceGroup": "slow", "catchRate": 45, "eggCycles": 40, "baseFriendship": 35,
    "shoulderMountable": False, "baseScale": scale_for(HEIGHT, t["top_base"]),
    "hitbox": {"width": 2.0, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": BEHAVIOUR(0.3),
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:bone", "quantityRange": "1-3"}, {"item": "minecraft:beef", "quantityRange": "0-2"},
        {"item": "cobblemon:dragon_fang", "percentage": 8.0}, {"item": "cobblemon:black_glasses", "percentage": 3.0}]},
    "moves": ["50:soufflecarnage", "1:dragonrage", "1:tackle", "1:poisonfang", "1:focusenergy", "1:dragonbreath", "1:bite",
              "8:roar", "12:assurance", "16:headbutt", "20:hyperfang", "28:workup", "32:jawlock", "36:brutalswing",
              "40:crunch", "44:scaryface", "48:dragonpulse", "52:bodyslam", "54:dracometeor", "58:dragonrush",
              "60:darkpulse", "64:nastyplot", "68:outrage", "72:stompingtantrum",
              "tm:takedown", "tm:scaryface", "tm:protect", "tm:firefang", "tm:thunderfang", "tm:icefang", "tm:thief",
              "tm:firespin", "tm:facade", "tm:bulldoze", "tm:snarl", "tm:mudshot", "tm:rocktomb", "tm:dragontail",
              "tm:endure", "tm:sunnyday", "tm:raindance", "tm:sandstorm", "tm:dig", "tm:zenheadbutt", "tm:bodyslam",
              "tm:reflect", "tm:stompingtantrum", "tm:rockslide", "tm:bodypress", "tm:taunt", "tm:darkpulse",
              "tm:ironhead", "tm:gunkshot", "tm:dragondance", "tm:substitute", "tm:crunch", "tm:heavyslam", "tm:heatwave",
              "tm:earthpower", "tm:nastyplot", "tm:earthquake", "tm:gigaimpact", "tm:outrage", "tm:focusblast",
              "tm:dracometeor"],
    "evolutions": [],
    "forms": [{
        "name": "Mega", "primaryType": "dragon", "secondaryType": "dark", "maleRatio": 0.5,
        "height": HEIGHT_MEGA, "weight": 9999, "pokedex": ["cobblemon.species.deviljho-mega.desc"],
        "labels": ["monster_hunter", "custom", "mega"], "aspects": ["mega"], "abilities": ["ragebrulante"],
        "baseStats": {"hp": 110, "attack": 190, "defence": 90, "special_attack": 125, "special_defence": 100, "speed": 85},
        "baseExperienceYield": 320, "baseScale": scale_for(HEIGHT_MEGA, t["top_mega"]),
        "hitbox": {"width": 2.1, "height": round(t["top_mega"] / 16, 2), "fixed": False},
        "battleOnly": True, "dynamaxBlocked": True, "lightingData": {"lightLevel": 9, "liquidGlowMode": "LAND"}}],
})
# Biomes O' Plenty wastelands (Wasteland + Wasteland Steppe), ultra-rare. The tag lists them as optional entries,
# so the spawn simply never happens without Biomes O' Plenty.
dump(f"{D}/normandy/tags/worldgen/biome/wastelands.json", {"replace": False, "values": [
    {"id": "biomesoplenty:wasteland", "required": False}, {"id": "biomesoplenty:wasteland_steppe", "required": False}]})
dump(f"{D}/cobblemon/spawn_pool_world/11231_deviljho.json", {
    "enabled": True, "neededInstalledMods": ["biomesoplenty"], "neededUninstalledMods": [],
    "spawns": [{"id": "deviljho-1", "pokemon": "deviljho", "presets": ["natural", "wild"], "type": "pokemon",
                "spawnablePositionType": "grounded", "bucket": "ultra-rare", "level": "50-70", "weight": 1.0,
                "condition": {"biomes": ["#normandy:wastelands"], "canSeeSky": True},
                "weightMultipliers": [{"multiplier": 1.5, "condition": {"timeRange": "night"}},
                                      {"multiplier": 2.0, "condition": {"isThundering": True}}],
                "labels": ["monster_hunter"]}]})
mega_stone("deviljhonite", "Deviljho", num=7901,
           recipe=([" f ", "bmb", " g "], {"f": "cobblemon:dragon_fang", "b": "minecraft:bone_block",
                                           "m": "mega_showdown:mega_stone", "g": "cobblemon:black_glasses"}),
           lore="Permet à Deviljho de méga-évoluer en Deviljho Carnage.", lore2="Elle palpite d'une faim sans fin.",
           legacy=True)
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
# legacy: the Deviljhonites crafted with mod 2.0 - 2.2 were echo shards carrying the components; they keep their icon
dump(f"{A}/minecraft/models/item/echo_shard.json", {
    "parent": "minecraft:item/generated", "textures": {"layer0": "minecraft:item/echo_shard"},
    "overrides": [{"predicate": {"custom_model_data": 31231}, "model": "normandy:item/deviljhonite"}]})
dump(f"{A}/normandy/models/item/deviljhonite.json",
     {"parent": "minecraft:item/generated", "textures": {"layer0": f"{MOD}:item/deviljhonite"}})
old_png = f"{A}/{LEGACY_MOD}/textures/item/deviljhonite.png"
if os.path.exists(old_png):
    os.remove(old_png)
    try:
        os.removedirs(os.path.dirname(old_png))
    except OSError:
        pass
LANG.update({
    "cobblemon.species.deviljho.name": "Deviljho",
    "cobblemon.species.deviljho.desc": "Une wyverne brute à l'appétit insatiable qui erre de territoire en territoire et dévore tout ce qui bouge. Sa mâchoire colossale broie la roche et ses muscles brûlent tant d'énergie qu'il doit chasser sans relâche.",
    "cobblemon.species.deviljho-mega.desc": "Deviljho Carnage. La Deviljhonite pousse sa rage à son paroxysme : ses muscles enflent, son dos se fend de veines incandescentes et une énergie draconique rouge sang crépite autour de lui. Plus rien ne peut rassasier sa faim.",
    "cobblemon.ui.pokedex.info.form.deviljho-mega": "Carnage",
    "cobblemon.ability.ragebrulante": "Rage Brûlante",
    "cobblemon.ability.ragebrulante.desc": "Les autres Pokémon ne peuvent pas baisser ses statistiques. Son Attaque augmente chaque fois qu'il subit un coup critique ou une capacité super efficace.",
    "cobblemon.move.soufflecarnage": "Souffle Carnage",
    "cobblemon.move.soufflecarnage.desc": "Le lanceur crache un torrent d'énergie draconique qui baisse la Défense de la cible. Physique ou spéciale : la catégorie qui fait le plus de dégâts à la cible.",
    "item.normandy.deviljhonite": "Deviljhonite",
    "item.normandy.deviljhonite.lore": "Permet à Deviljho de méga-évoluer en Deviljho Carnage.",
    "item.normandy.deviljhonite.lore2": "Elle palpite d'une faim sans fin.",
})

# ================================================================================================ Glavenus
G_HEIGHT, G_HEIGHT_MEGA = 48, 55        # 4.8 m; Lame-Chaos 5.5 m
t = tops("glavenus")
species_file("glavenus", {
    "implemented": True, "nationalPokedexNumber": 11232, "name": "Glavenus",
    "primaryType": "fire", "secondaryType": "steel", "maleRatio": 0.5,
    "height": G_HEIGHT, "weight": 3205, "pokedex": ["cobblemon.species.glavenus.desc"],
    "labels": ["monster_hunter", "custom"], "aspects": [],
    "abilities": ["sharpness", "h:angershell"],                     # Incisif, Courroupace (caché)
    "eggGroups": ["monster", "dragon"],
    "baseStats": {"hp": 110, "attack": 130, "defence": 65, "special_attack": 75, "special_defence": 95, "speed": 65},
    "evYield": {"hp": 0, "attack": 3, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 255, "experienceGroup": "slow", "catchRate": 45, "eggCycles": 40, "baseFriendship": 35,
    "shoulderMountable": False, "baseScale": scale_for(G_HEIGHT, t["top_base"]),
    "hitbox": {"width": 1.8, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": BEHAVIOUR(0.32),
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:bone", "quantityRange": "1-2"}, {"item": "minecraft:iron_ingot", "quantityRange": "1-3"},
        {"item": "minecraft:blaze_powder", "quantityRange": "0-2"}, {"item": "cobblemon:fire_stone", "percentage": 6.0},
        {"item": "cobblemon:metal_coat", "percentage": 4.0}]},
    "moves": ["1:scratch", "1:leer", "1:ember", "1:sharpen", "6:furycutter", "10:roar", "14:metalclaw", "18:firefang",
              "22:smokescreen", "26:slash", "30:irondefense", "32:autotomize", "34:incinerate", "38:nightslash",
              "42:swordsdance", "48:queuelame", "54:flareblitz", "60:airslash", "66:outrage", "72:irontail"]
             + [f"tm:{m}" for m in ("aerialace", "aircutter", "airslash", "xscissor", "cut", "ironhead", "crunch",
                                    "earthquake", "rockslide", "stoneedge", "dragonclaw", "closecombat", "brickbreak",
                                    "heavyslam", "flamethrower", "fireblast", "heatwave", "flashcannon", "dragonpulse",
                                    "dracometeor", "ancientpower", "focusblast", "bulldoze", "roar", "stealthrock",
                                    "spikes", "swordsdance", "irondefense", "autotomize", "protect", "substitute",
                                    "rest", "sleeptalk", "willowisp", "sunnyday", "howl", "scaryface", "taunt",
                                    "torment")]
             + [f"tutor:{m}" for m in ("ironhead", "heatwave", "dracometeor", "outrage", "willowisp", "stealthrock",
                                       "gyroball", "stompingtantrum", "doubleslap", "dragonpulse", "earthpower")]
             + [f"egg:{m}" for m in ("barrier", "acupressure", "filletaway", "suckerpunch", "counter", "irontail",
                                     "aircutter")],
    "evolutions": [],
    "forms": [{
        "name": "Mega", "primaryType": "fire", "secondaryType": "dragon", "maleRatio": 0.5,
        "height": G_HEIGHT_MEGA, "weight": 4100, "pokedex": ["cobblemon.species.glavenus-mega.desc"],
        "labels": ["monster_hunter", "custom", "mega"], "aspects": ["mega"], "abilities": ["lameduchaos"],
        "baseStats": {"hp": 110, "attack": 140, "defence": 95, "special_attack": 85, "special_defence": 120, "speed": 90},
        "baseExperienceYield": 300, "baseScale": scale_for(G_HEIGHT_MEGA, t["top_mega"]),
        "hitbox": {"width": 1.9, "height": round(t["top_mega"] / 16, 2), "fixed": False},
        "battleOnly": True, "dynamaxBlocked": True, "lightingData": {"lightLevel": 11, "liquidGlowMode": "LAND"}}],
})
# Tropical forests (dense jungles, at the edge of volcanic areas) and volcanic / magmatic lands, ultra-rare
dump(f"{D}/cobblemon/spawn_pool_world/11232_glavenus.json", {
    "enabled": True, "neededInstalledMods": [], "neededUninstalledMods": [],
    "spawns": [
        {"id": "glavenus-1", "pokemon": "glavenus", "presets": ["natural", "wild"], "type": "pokemon",
         "spawnablePositionType": "grounded", "bucket": "ultra-rare", "level": "50-70", "weight": 0.8,
         "condition": {"biomes": ["#cobblemon:is_jungle"], "canSeeSky": True},
         "weightMultipliers": [{"multiplier": 1.5, "condition": {"timeRange": "day"}}],
         "labels": ["monster_hunter"]},
        {"id": "glavenus-2", "pokemon": "glavenus", "presets": ["natural", "wild"], "type": "pokemon",
         "spawnablePositionType": "grounded", "bucket": "ultra-rare", "level": "50-70", "weight": 1.2,
         "condition": {"biomes": ["#cobblemon:is_volcanic"]},
         "labels": ["monster_hunter"]}]})
mega_stone("glavenusite", "Glavenus", num=7902,
           recipe=([" f ", "imi", " c "], {"f": "cobblemon:fire_stone", "i": "minecraft:iron_block",
                                           "m": "mega_showdown:mega_stone", "c": "cobblemon:metal_coat"}),
           lore="Permet à Glavenus de méga-évoluer en Glavenus Lame-Chaos.",
           lore2="Elle brûle d'une chaleur qui ne s'éteint jamais.")
# Lame du Chaos (mega): slicing moves +70% power, and slicing moves are super effective on Rock-type Pokemon
# (the Rock part of the target counts as weak, like Freeze-Dry on Water; the other move effects are kept).
write(f"{D}/normandy/mega_showdown/showdown/abilities/lameduchaos.js", """{
  onBasePowerPriority: 19,
  onBasePower(basePower, attacker, defender, move) {
    if (move.flags['slicing']) {
      return this.chainModify([6963, 4096]);
    }
  },
  onModifyMove(move) {
    if (!move.flags['slicing']) return;
    const previous = move.onEffectiveness;
    move.onEffectiveness = function (typeMod, target, type, m) {
      let mod = typeMod;
      if (previous) {
        const r = previous.call(this, typeMod, target, type, m);
        if (typeof r === 'number') mod = r;
      }
      if (type === 'Rock') return 1;
      return mod;
    };
  },
  flags: {},
  name: "Lame du Chaos",
  rating: 4,
  num: 7808
}
""")
# Queue-Lame (signature): Steel, physical, 80 power, 100%, 5 PP, slicing + contact; it also counts as Fire: against
# each type of the target the better of Steel and Fire is used (super effective on whatever is weak to Fire).
write(f"{D}/normandy/mega_showdown/showdown/moves/queuelame.js", """{
  num: 7709,
  accuracy: 100,
  basePower: 80,
  category: "Physical",
  name: "Queue-Lame",
  pp: 5,
  priority: 0,
  flags: { contact: 1, protect: 1, mirror: 1, metronome: 1, slicing: 1 },
  onEffectiveness(typeMod, target, type, move) {
    return Math.max(typeMod, this.dex.getEffectiveness('Fire', type));
  },
  secondary: null,
  target: "normal",
  type: "Steel",
  contestType: "Cool"
}
""")
LANG.update({
    "cobblemon.species.glavenus.name": "Glavenus",
    "cobblemon.species.glavenus.desc": "Une wyverne de terre qui manie sa queue puissante comme une épée. Elle chauffe à chaque coup jusqu'à devenir brûlante.",
    "cobblemon.species.glavenus-mega.desc": "L'énergie de la Méga-Gemme le consume de l'intérieur, le plongeant dans une frénésie sanguinaire perpétuelle. Sa queue-lame irradie une chaleur si destructrice qu'elle fond ses propres écailles, le poussant à trancher tout sur son passage pour apaiser sa rage.",
    "cobblemon.ui.pokedex.info.form.glavenus-mega": "Lame-Chaos",
    "cobblemon.ability.lameduchaos": "Lame du Chaos",
    "cobblemon.ability.lameduchaos.desc": "Augmente de 70 % la puissance des capacités tranchantes. Ses capacités tranchantes sont super efficaces sur les Pokémon de type Roche.",
    "cobblemon.move.queuelame": "Queue-Lame",
    "cobblemon.move.queuelame.desc": "Le lanceur assène un violent coup circulaire avec sa queue surchauffée à blanc. Super efficace aussi sur les Pokémon vulnérables au Feu.",
    f"itemGroup.{MOD}.fakemons": "CobblePulse-Ecology",
})

# ================================================================================================ shared
dump(f"{D}/cobblemon/species_feature_assignments/monster_hunter_mega.json",
     {"pokemon": SPECIES_IDS, "features": ["mega_evolution"]})
dump(f"{D}/cobblemon/dexes/monster_hunter.json", {
    "type": "cobblemon:simple_pokedex_def", "id": "cobblemon:monster_hunter", "sortOrder": 13,
    "entries": [f"cobblemon:{s}" for s in SPECIES_IDS]})
dump(f"{D}/cobblemon/dex_additions/monster_hunter_national.json",
     {"dexId": "cobblemon:national", "entries": ["cobblemon:monster_hunter"]})
# a Mega Stone for every mod that looks at Mega Showdown's tag
dump(f"{D}/mega_showdown/tags/item/mega_stone.json", {"replace": False, "values": [
    f"{MOD}:deviljhonite", f"{MOD}:glavenusite", f"{LEGACY_MOD}:deviljhonite"]})
GONE = ("cobblemon.ability.faimdevorante", "cobblemon.ability.faimdevorante.desc", "itemGroup.normandy_fakemons.fakemons")
for lang in ("fr_fr", "en_us"):
    p = f"{A}/cobblemon/lang/{lang}.json"
    cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    for gone in GONE:
        cur.pop(gone, None)
    cur.update(LANG)
    dump(p, cur)
for sid in SPECIES_IDS:
    d = json.load(open(f"{D}/cobblemon/species/monster_hunter/{sid}.json"))
    print(f"{sid}: baseScale {d['baseScale']} (mega {d['forms'][0]['baseScale']}), hitbox height {d['hitbox']['height']}")
