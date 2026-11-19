# -*- coding: utf-8 -*-
"""Monster Hunter category data: Deviljho (+ Deviljho Carnage), Glavenus (+ Glavenus Lame-Chaos), Zamtrios (Ice Armour
and Inflated forms), Gore Magala (+ Frenzy), Chaotic Gore Magala and Shagaru Magala: species and forms, Pokédex,
spawns, Mega Showdown data (mega and battle_form registry entries, mega stones, custom abilities, moves and species
conditions), species features, the mega stones' recipes, item models and texts.
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
MEGA_IDS = []      # species that mega-evolve (Mega Showdown's mega_evolution feature)


def species_file(sid, d, forms=("Normal", "Mega")):
    dump(f"{D}/cobblemon/species/monster_hunter/{sid}.json", d)
    dump(f"{D}/cobblemon/dex_entries/pokemon/monster_hunter/{sid}.json", {
        "id": f"cobblemon:{sid}", "speciesId": f"cobblemon:{sid}", "displayAspects": [], "conditionAspects": [],
        "forms": [{"displayForm": f, "unlockForms": [f]} for f in forms],
        "variations": []})
    SPECIES_IDS.append(sid)
    if "Mega" in forms:
        MEGA_IDS.append(sid)


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

# ================================================================================================ Zamtrios
# Water/Ice, three forms: Normal, Ice Armour (in frozen biomes, or in battle after using an Ice move) and Inflated
# (in battle, at half HP or less, or after Stockpile). The forms are an aspect of the zamtrios_form species feature:
# the mod sets it from the biome in the world, Showdown changes the forme in battle (species condition, below) and
# Mega Showdown's battle_form registry turns the forme change into the aspect (reverted at the end of the battle).
Z_HEIGHT = 29
t = tops("zamtrios")
Z_SCALE = scale_for(Z_HEIGHT, t["top_base"])
Z_ABIL = ["furcoat", "strongjaw", "h:swiftswim"]                     # Toison Épaisse, Prognathe, Glissade (caché)
species_file("zamtrios", {
    "implemented": True, "nationalPokedexNumber": 11233, "name": "Zamtrios",
    "primaryType": "water", "secondaryType": "ice", "maleRatio": 0.5,
    "height": Z_HEIGHT, "weight": 2150, "pokedex": ["cobblemon.species.zamtrios.desc"],
    "labels": ["monster_hunter", "custom"], "aspects": [], "abilities": Z_ABIL,
    "eggGroups": ["water_1", "monster"],
    "baseStats": {"hp": 105, "attack": 100, "defence": 95, "special_attack": 75, "special_defence": 80, "speed": 60},
    "evYield": {"hp": 2, "attack": 0, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 186, "experienceGroup": "slow", "catchRate": 75, "eggCycles": 20, "baseFriendship": 50,
    "shoulderMountable": False, "baseScale": Z_SCALE,
    "hitbox": {"width": 3.0, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": {
        "resting": {"canSleep": True, "light": "0-4", "drowsyChance": 0.02, "rouseChance": 0.006},
        "moving": {"canLook": True, "walk": {"walkSpeed": 0.26},
                   "swim": {"canSwimInWater": True, "canBreatheUnderwater": True, "canSwimInLava": False,
                            "swimSpeed": 0.42}},
        "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False}},
    "drops": {"amount": 2, "entries": [
        {"item": "minecraft:packed_ice", "quantityRange": "1-4"}, {"item": "minecraft:cod", "quantityRange": "0-2"},
        {"item": "cobblemon:never_melt_ice", "percentage": 15.0}]},
    # level-up: a few strong moves (Liquidation, Icicle Crash, Wave Crash...), average ones and some poor ones
    # (Splash, Harden, Rollout, Powder Snow...)
    "moves": ["1:splash", "1:tackle", "1:powdersnow", "1:watergun", "5:bite", "9:screech", "12:harden",
              "15:icywind", "18:aquajet", "21:stockpile", "21:swallow", "21:spitup", "24:icefang", "27:haze",
              "30:rollout", "33:liquidation", "36:icebeam", "39:crunch", "42:heavyslam", "45:hydropump",
              "48:iciclecrash", "52:earthquake", "56:blizzard", "60:wavecrash", "64:sheercold"]
             + [f"tm:{m}" for m in ("aquatail", "protect", "icebeam", "blizzard", "earthquake", "rocktomb", "scald",
                                    "icywind", "waterfall", "surf", "avalanche", "iciclespear", "bulldoze", "rest",
                                    "sleeptalk", "substitute", "facade", "snowscape", "raindance", "chillingwater",
                                    "takedown", "bodyslam", "endure", "liquidation", "hydropump", "icepunch",
                                    "whirlpool", "brine", "waterpulse", "amnesia", "snore", "ironhead", "icefang")]
             + [f"egg:{m}" for m in ("avalanche", "iciclespear", "ironhead", "flipturn", "mudbomb", "bounce",
                                     "aquatail", "psychicfangs", "jawlock")]
             + [f"tutor:{m}" for m in ("wavecrash", "stompingtantrum", "freezedry", "disable", "fishiousrend")],
    "evolutions": [],
    "forms": [
        {"name": "Armor", "primaryType": "water", "secondaryType": "ice", "maleRatio": 0.5, "height": Z_HEIGHT,
         "weight": 2600, "pokedex": ["cobblemon.species.zamtrios-armor.desc"], "labels": ["monster_hunter", "custom"],
         "aspects": ["zamtrios-armor"], "abilities": Z_ABIL,
         "baseStats": {"hp": 105, "attack": 120, "defence": 125, "special_attack": 70, "special_defence": 85, "speed": 40},
         "baseScale": Z_SCALE, "hitbox": {"width": 3.0, "height": round(t["top_armor"] / 16, 2), "fixed": False},
         "lightingData": {"lightLevel": 7, "liquidGlowMode": "BOTH"}},
        {"name": "Inflated", "primaryType": "water", "secondaryType": "ice", "maleRatio": 0.5, "height": 36,
         "weight": 3100, "pokedex": ["cobblemon.species.zamtrios-inflated.desc"], "labels": ["monster_hunter", "custom"],
         "aspects": ["zamtrios-inflated"], "abilities": Z_ABIL,
         "baseStats": {"hp": 105, "attack": 90, "defence": 115, "special_attack": 85, "special_defence": 115, "speed": 25},
         "baseScale": Z_SCALE, "hitbox": {"width": 6.5, "height": round(t["top_inflated"] / 16, 2), "fixed": False},
         "battleOnly": True, "dynamaxBlocked": True}],
}, forms=("Normal", "Armor", "Inflated"))
dump(f"{D}/cobblemon/species_features/zamtrios_form.json", {
    "type": "choice", "keys": ["zamtrios_form"], "default": "normal", "choices": ["normal", "armor", "inflated"],
    "isAspect": True, "aspectFormat": "zamtrios-{{choice}}"})
for forme, choice in (("armor", "armor"), ("inflated", "inflated")):
    dump(f"{D}/normandy/mega_showdown/battle_form/zamtrios_{forme}.json", {
        "pokemons": ["Zamtrios"], "showdown_form_change_id": forme,
        "aspect_conditions": {"apply": {"aspects": [f"zamtrios_form={choice}"]},
                              "revert": {"aspects": ["zamtrios_form=normal"]}}})
# frozen seas (armoured), cold seas, snowy shores and ice fields (armoured), rare
dump(f"{D}/cobblemon/spawn_pool_world/11233_zamtrios.json", {
    "enabled": True, "neededInstalledMods": [], "neededUninstalledMods": [],
    "spawns": [
        {"id": "zamtrios-1", "pokemon": "zamtrios zamtrios_form=armor", "presets": ["water"], "type": "pokemon",
         "spawnablePositionType": "submerged", "bucket": "rare", "level": "35-55", "weight": 6.0,
         "condition": {"biomes": ["#cobblemon:is_frozen_ocean"]}, "labels": ["monster_hunter"]},
        {"id": "zamtrios-2", "pokemon": "zamtrios", "presets": ["water"], "type": "pokemon",
         "spawnablePositionType": "submerged", "bucket": "rare", "level": "35-55", "weight": 3.0,
         "condition": {"biomes": ["#cobblemon:is_cold_ocean"]}, "labels": ["monster_hunter"]},
        {"id": "zamtrios-3", "pokemon": "zamtrios zamtrios_form=armor", "presets": ["natural", "wild"],
         "type": "pokemon", "spawnablePositionType": "grounded", "bucket": "rare", "level": "35-55", "weight": 2.5,
         "condition": {"biomes": ["minecraft:snowy_beach", "minecraft:ice_spikes", "minecraft:frozen_river"],
                       "canSeeSky": True},
         "weightMultipliers": [{"multiplier": 1.5, "condition": {"isRaining": True}}],
         "labels": ["monster_hunter"]}]})
# Zamtrios' forme changes in battle: a Showdown species condition (Conditions[toID(baseSpecies)] is merged into the
# species by Showdown, so these handlers run for every Zamtrios whatever its ability). The forme change is permanent
# (details change: it keeps it when switching) and keeps the Pokemon's own ability. The species cache is cleared in
# case the species was read before this file was loaded (MSD evaluates the file in Showdown's index.js scope).
write(f"{D}/normandy/mega_showdown/showdown/conditions/zamtrios.js", """(function () {
  try {
    const dexes = Dex.dexes || {};
    for (const k in dexes) {
      const s = dexes[k] && dexes[k].species;
      if (s && s.speciesCache) ['zamtrios', 'zamtriosarmor', 'zamtriosinflated'].forEach(id => s.speciesCache.delete(id));
    }
  } catch (e) {}
  const shift = function (battle, pokemon, forme) {
    if (!pokemon.hp || pokemon.transformed || pokemon.species.name === forme) return;
    const abilities = pokemon.species.abilities;
    let slot = '0';
    for (const k in abilities) if (battle.toID(abilities[k]) === pokemon.baseAbility) slot = k;
    pokemon.formeChange(forme, battle.effect, true, slot);
  };
  return {
    name: 'Zamtrios',
    onAfterMove(pokemon, target, move) {
      if (pokemon.species.name === 'Zamtrios-Inflated') return;
      if (move.id === 'stockpile') shift(this, pokemon, 'Zamtrios-Inflated');
      else if (move.type === 'Ice' && pokemon.species.name === 'Zamtrios') shift(this, pokemon, 'Zamtrios-Armor');
    },
    onUpdate(pokemon) {
      if (pokemon.species.name !== 'Zamtrios-Inflated' && pokemon.hp && pokemon.hp <= pokemon.maxhp / 2) {
        shift(this, pokemon, 'Zamtrios-Inflated');
      }
    }
  };
})()
""")
LANG.update({
    "cobblemon.species.zamtrios.name": "Zamtrios",
    "cobblemon.species.zamtrios.desc": "Un requin amphibie des mers glacées. Il gèle l'eau sur ses écailles pour se couvrir d'une armure de glace et peut gonfler son corps d'eau jusqu'à devenir une énorme boule qui écrase tout.",
    "cobblemon.species.zamtrios-armor.desc": "Zamtrios en Armure de Glace. Dans le froid ou après une attaque de glace, l'eau gèle sur sa peau en piques acérées qui luisent dans l'obscurité.",
    "cobblemon.species.zamtrios-inflated.desc": "Zamtrios gonflé. Blessé ou après avoir fait des réserves, il avale tant d'eau que son corps devient une boule géante qu'il fait rouler sur ses ennemis.",
    "cobblemon.ui.pokedex.info.form.zamtrios-armor": "Armure de Glace",
    "cobblemon.ui.pokedex.info.form.zamtrios-inflated": "Gonflée",
})

# ================================================================================================ the Magala line
# Gore Magala (Dark/Dragon, blind, wing-arms, antennae) evolves at level 69 into Shagaru Magala (Dragon/Fairy) or,
# when a Shagaru Magala is in the party, into Chaotic Gore Magala (Dark/Dragon, half moulted). All three are
# legendary (label "legendary"); only Gore Magala spawns. Gore Magala has a battle form, Frenzy (Mode Furie): at half
# HP or less its antennae unfold and glow purple.
M_LABELS = ["monster_hunter", "custom", "legendary"]
NO_EGG = ["undiscovered"]
def magala_behaviour(times, fly):
    b = {"resting": {"canSleep": True, "light": "0-15", "drowsyChance": 0.02, "rouseChance": 0.006, "times": times},
         "moving": {"canLook": True, "walk": {"walkSpeed": 0.32},
                    "swim": {"canSwimInWater": True, "canBreatheUnderwater": False, "canSwimInLava": False,
                             "swimSpeed": 0.15}},
         "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False}}
    if fly:
        b["moving"]["fly"] = {"canFly": True, "flySpeedHorizontal": 0.45}
    return b

def lv(*pairs):
    return [f"{l}:{m}" for l, ms in pairs for m in ms.split()]

GM_HEIGHT = 42
t = tops("goremagala")
GM_SCALE = scale_for(GM_HEIGHT, t["top_base"])
species_file("goremagala", {
    "implemented": True, "nationalPokedexNumber": 11234, "name": "Gore Magala",
    "primaryType": "dark", "secondaryType": "dragon", "maleRatio": -1,
    "height": GM_HEIGHT, "weight": 2300, "pokedex": ["cobblemon.species.goremagala.desc"],
    "labels": M_LABELS, "aspects": [], "abilities": ["cursedbody", "unnerve", "h:infiltrator"],
    "eggGroups": NO_EGG,
    "baseStats": {"hp": 95, "attack": 115, "defence": 85, "special_attack": 115, "special_defence": 85, "speed": 85},
    "evYield": {"hp": 0, "attack": 1, "defence": 0, "special_attack": 1, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 260, "experienceGroup": "slow", "catchRate": 5, "eggCycles": 30, "baseFriendship": 0,
    "shoulderMountable": False, "baseScale": GM_SCALE,
    "hitbox": {"width": 2.2, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": magala_behaviour("day", False),
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:black_dye", "quantityRange": "1-3"}, {"item": "minecraft:phantom_membrane", "quantityRange": "0-2"},
        {"item": "minecraft:bone", "quantityRange": "0-2"}, {"item": "cobblemon:spell_tag", "percentage": 6.0},
        {"item": "cobblemon:black_glasses", "percentage": 4.0}]},
    "moves": lv((1, "leer scratch bite growl"), (5, "ominouswind"), (9, "screech"), (13, "confuseray"),
                (17, "dragonbreath"), (21, "snarl"), (25, "dragonrush"), (29, "darkpulse"), (33, "nightslash"),
                (37, "spite"), (41, "dragonpulse"), (45, "dragonclaw"), (49, "shadowball"), (53, "meanlook"),
                (57, "nastyplot"), (61, "outrage"), (66, "hyperbeam"))
             + [f"tm:{m}" for m in ("dragonclaw", "taunt", "hyperbeam", "shadowball", "darkpulse", "gigaimpact",
                                    "dragontail", "uturn", "protect", "rest", "sleeptalk", "substitute", "facade",
                                    "roar", "scaryface", "snarl", "knockoff", "fly", "airslash", "aerialace",
                                    "tailwind", "dragonpulse", "outrage", "hex", "willowisp", "endure", "swift")]
             + [f"tutor:{m}" for m in ("stealthrock", "dragontail", "tailwind", "imprison", "fierywrath")],
    "evolutions": [
        {"id": "goremagala_shagarumagala", "variant": "level_up", "result": "shagarumagala", "consumeHeldItem": False,
         "learnableMoves": ["lightofruin"],
         "requirements": [{"variant": "level", "minLevel": 69},
                          {"variant": "party_member", "target": "shagarumagala", "contains": False}]},
        {"id": "goremagala_chaoticgoremagala", "variant": "level_up", "result": "chaoticgoremagala",
         "consumeHeldItem": False, "learnableMoves": ["closecombat"],
         "requirements": [{"variant": "level", "minLevel": 69},
                          {"variant": "party_member", "target": "shagarumagala", "contains": True}]}],
    "forms": [{
        "name": "Frenzy", "primaryType": "dark", "secondaryType": "dragon", "maleRatio": -1,
        "height": GM_HEIGHT, "weight": 2300, "pokedex": ["cobblemon.species.goremagala-frenzy.desc"],
        "labels": M_LABELS, "aspects": ["magala_frenzy"], "abilities": ["cursedbody", "unnerve", "h:infiltrator"],
        "baseStats": {"hp": 95, "attack": 130, "defence": 75, "special_attack": 130, "special_defence": 75, "speed": 95},
        "baseScale": GM_SCALE, "hitbox": {"width": 2.2, "height": round(t["top_frenzy"] / 16, 2), "fixed": False},
        "battleOnly": True, "dynamaxBlocked": True, "lightingData": {"lightLevel": 6, "liquidGlowMode": "LAND"}}],
}, forms=("Normal", "Frenzy"))
dump(f"{D}/cobblemon/species_features/magala_frenzy.json",
     {"type": "flag", "keys": ["magala_frenzy"], "default": False, "isAspect": True})
dump(f"{D}/normandy/mega_showdown/battle_form/goremagala_frenzy.json", {
    "pokemons": ["Gore Magala"], "showdown_form_change_id": "frenzy",
    "aspect_conditions": {"apply": {"aspects": ["magala_frenzy=true"]}, "revert": {"aspects": ["magala_frenzy=false"]}}})
write(f"{D}/normandy/mega_showdown/showdown/conditions/goremagala.js", """(function () {
  try {
    const dexes = Dex.dexes || {};
    for (const k in dexes) {
      const s = dexes[k] && dexes[k].species;
      if (s && s.speciesCache) ['goremagala', 'goremagalafrenzy'].forEach(id => s.speciesCache.delete(id));
    }
  } catch (e) {}
  return {
    name: 'Gore Magala',
    onUpdate(pokemon) {
      if (!pokemon.hp || pokemon.transformed || pokemon.species.name !== 'Gore Magala') return;
      if (pokemon.hp > pokemon.maxhp / 2) return;
      const abilities = pokemon.species.abilities;
      let slot = '0';
      for (const k in abilities) if (this.toID(abilities[k]) === pokemon.baseAbility) slot = k;
      pokemon.formeChange('Gore Magala-Frenzy', this.effect, true, slot);
    }
  };
})()
""")
# dark forests, groves and their Terralith cousins (night or thunderstorms); the Deep Dark at any hour; ultra-rare
dump(f"{D}/normandy/tags/worldgen/biome/magala_haunts.json", {"replace": False, "values": [
    "minecraft:dark_forest", "minecraft:grove",
    {"id": "terralith:moonlight_grove", "required": False}, {"id": "terralith:moonlight_valley", "required": False}]})
GM_SPAWN = {"pokemon": "goremagala", "type": "pokemon", "spawnablePositionType": "grounded", "bucket": "ultra-rare",
            "level": "48-65", "labels": ["monster_hunter", "legendary"]}
dump(f"{D}/cobblemon/spawn_pool_world/11234_goremagala.json", {
    "enabled": True, "neededInstalledMods": [], "neededUninstalledMods": [],
    "spawns": [
        dict(GM_SPAWN, id="goremagala-1", presets=["natural", "wild"], weight=8.0,
             condition={"biomes": ["#normandy:magala_haunts"], "timeRange": "night"}),
        dict(GM_SPAWN, id="goremagala-2", presets=["natural", "wild"], weight=8.0,
             condition={"biomes": ["#normandy:magala_haunts"], "isThundering": True}),
        dict(GM_SPAWN, id="goremagala-3", presets=["natural"], weight=4.0,
             condition={"biomes": ["minecraft:deep_dark"], "canSeeSky": False})]})

CG_HEIGHT = 44
t = tops("chaoticgoremagala")
species_file("chaoticgoremagala", {
    "implemented": True, "nationalPokedexNumber": 11235, "name": "Chaotic Gore Magala",
    "primaryType": "dark", "secondaryType": "dragon", "maleRatio": -1,
    "height": CG_HEIGHT, "weight": 2450, "pokedex": ["cobblemon.species.chaoticgoremagala.desc"],
    "labels": M_LABELS, "aspects": [], "abilities": ["cursedbody", "reckless", "h:infiltrator"],
    "eggGroups": NO_EGG, "preEvolution": "goremagala",
    "baseStats": {"hp": 95, "attack": 150, "defence": 80, "special_attack": 110, "special_defence": 75, "speed": 110},
    "evYield": {"hp": 0, "attack": 3, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 300, "experienceGroup": "slow", "catchRate": 3, "eggCycles": 35, "baseFriendship": 0,
    "shoulderMountable": False, "baseScale": scale_for(CG_HEIGHT, t["top_base"]),
    "hitbox": {"width": 2.3, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": magala_behaviour("day", False),
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:black_dye", "quantityRange": "1-2"}, {"item": "minecraft:gold_nugget", "quantityRange": "1-3"},
        {"item": "minecraft:phantom_membrane", "quantityRange": "0-2"}, {"item": "cobblemon:dragon_fang", "percentage": 8.0},
        {"item": "cobblemon:black_glasses", "percentage": 5.0}]},
    "moves": lv((1, "leer scratch bite growl"), (5, "ominouswind"), (9, "screech"),
                (13, "confuseray"), (17, "dragonbreath"), (21, "snarl"), (25, "dragonrush"), (29, "darkpulse"),
                (33, "nightslash"), (37, "spite"), (41, "dragonclaw"), (45, "doubleedge"), (49, "flareblitz"),
                (53, "outrage"), (57, "closecombat"), (61, "bravebird"), (66, "gigaimpact"), (72, "headsmash"))
             + [f"tm:{m}" for m in ("roar", "icebeam", "earthquake", "shadowball", "flamethrower", "scald", "dreameater",
                                    "dragonclaw", "taunt", "hyperbeam", "gigaimpact", "protect", "rest", "sleeptalk",
                                    "substitute", "facade", "knockoff", "uturn", "swordsdance", "bulkup",
                                    "wildcharge", "dragondance", "fly", "endure", "takedown", "brickbreak")]
             + [f"tutor:{m}" for m in ("lashout", "rocksmash", "furyattack", "eruption")],
    "evolutions": [], "forms": [],
}, forms=("Normal",))

SM_HEIGHT = 46
t = tops("shagarumagala")
species_file("shagarumagala", {
    "implemented": True, "nationalPokedexNumber": 11236, "name": "Shagaru Magala",
    "primaryType": "dragon", "secondaryType": "fairy", "maleRatio": -1,
    "height": SM_HEIGHT, "weight": 2500, "pokedex": ["cobblemon.species.shagarumagala.desc"],
    "labels": M_LABELS, "aspects": [], "abilities": ["goldenfrenzy", "h:multiscale"],
    "eggGroups": NO_EGG, "preEvolution": "goremagala",
    "baseStats": {"hp": 105, "attack": 110, "defence": 100, "special_attack": 145, "special_defence": 105, "speed": 85},
    "evYield": {"hp": 0, "attack": 0, "defence": 0, "special_attack": 3, "special_defence": 0, "speed": 0},
    "baseExperienceYield": 320, "experienceGroup": "slow", "catchRate": 3, "eggCycles": 40, "baseFriendship": 0,
    "shoulderMountable": False, "baseScale": scale_for(SM_HEIGHT, t["top_base"]),
    "hitbox": {"width": 2.3, "height": round(t["top_base"] / 16, 2), "fixed": False},
    "behaviour": magala_behaviour("night", True),
    "lightingData": {"lightLevel": 9, "liquidGlowMode": "LAND"},
    "drops": {"amount": 3, "entries": [
        {"item": "minecraft:gold_nugget", "quantityRange": "2-5"}, {"item": "minecraft:glowstone_dust", "quantityRange": "1-3"},
        {"item": "minecraft:gold_ingot", "percentage": 10.0}, {"item": "cobblemon:dragon_scale", "percentage": 6.0}]},
    "moves": lv((1, "leer fairywind dragonbreath ominouswind confuseray"), (5, "sweetkiss"), (9, "swift"),
                (13, "disarmingvoice"), (17, "aurorabeam"), (21, "darkpulse"), (25, "dragonpulse"),
                (29, "extrasensory"), (33, "dragonclaw"), (37, "charm"), (41, "moonblast"), (45, "dazzlinggleam"),
                (49, "calmmind"), (53, "airslash"), (57, "moonlight"), (61, "dracometeor"), (66, "hurricane"),
                (69, "lightofruin"), (75, "mistball"))
             + [f"tm:{m}" for m in ("dragonclaw", "calmmind", "lightscreen", "protect", "roost", "aerialace", "uturn",
                                    "dazzlinggleam", "reflect", "psychic", "fly", "hurricane", "tailwind",
                                    "mistyterrain", "rest", "sleeptalk", "substitute", "hyperbeam", "gigaimpact",
                                    "focusblast", "flamethrower", "dragonpulse", "airslash", "endure", "facade",
                                    "drainingkiss", "playrough")]
             + [f"tutor:{m}" for m in ("aromaticmist", "healpulse", "aeroblast", "mistball", "dracometeor")],
    "evolutions": [], "forms": [],
}, forms=("Normal",))
# Écailles en furie dorée: Dragon and Fairy moves +25 %; the secondary effects of its light moves are twice as likely;
# but Poison moves and poison / bad poison damage hurt it 25 % more.
write(f"{D}/normandy/mega_showdown/showdown/abilities/goldenfrenzy.js", """{
  onBasePowerPriority: 21,
  onBasePower(basePower, attacker, defender, move) {
    if (move.type === 'Dragon' || move.type === 'Fairy') {
      return this.chainModify([5120, 4096]);
    }
  },
  onModifyMovePriority: -2,
  onModifyMove(move) {
    const light = ['moonblast', 'dazzlinggleam', 'flashcannon', 'mirrorshot', 'lusterpurge', 'mistball', 'aurorabeam',
      'chargebeam', 'signalbeam', 'psybeam', 'photongeyser', 'prismaticlaser', 'lightofruin', 'fleurcannon', 'solarbeam',
      'solarblade', 'moongeistbeam', 'sunsteelstrike', 'doomdesire', 'spiritbreak', 'mysticalfire', 'fierydance',
      'magicalleaf'];
    if (!light.includes(move.id)) return;
    if (move.secondaries) {
      for (const secondary of move.secondaries) {
        if (secondary.chance) secondary.chance = Math.min(100, secondary.chance * 2);
      }
    }
  },
  onSourceModifyDamage(damage, source, target, move) {
    if (move.type === 'Poison') {
      return this.chainModify([5120, 4096]);
    }
  },
  onDamage(damage, target, source, effect) {
    if (effect && (effect.id === 'psn' || effect.id === 'tox')) {
      return Math.floor(damage * 1.25);
    }
  },
  flags: {},
  name: "Golden Frenzy",
  rating: 3.5,
  num: 7809
}
""")
LANG.update({
    "cobblemon.species.goremagala.name": "Gore Magala",
    "cobblemon.species.goremagala.desc": "Un dragon noir aveugle, drapé d'ailes qui lui servent aussi de pattes avant. Il ne voit rien : il perçoit le monde grâce aux écailles noires qu'il répand autour de lui, porteuses du virus de la Frénésie.",
    "cobblemon.species.goremagala-frenzy.desc": "Gore Magala en Mode Furie. Blessé, il déploie les antennes de son crâne qui luisent d'un violet malsain, et ses écailles noires tourbillonnent en un voile qui rend fou.",
    "cobblemon.ui.pokedex.info.form.goremagala-frenzy": "Mode Furie",
    "cobblemon.species.chaoticgoremagala.name": "Gore Magala du Chaos",
    "cobblemon.species.chaoticgoremagala.desc": "Un Gore Magala dont la mue s'est figée en présence d'un Shagaru Magala. Moitié noir et violet, moitié or, il n'a qu'un œil, du côté doré, et sa fureur instable fait trembler le sol.",
    "cobblemon.species.shagarumagala.name": "Shagaru Magala",
    "cobblemon.species.shagarumagala.desc": "Le Gore Magala parvenu au terme de sa mue. Ce dragon ancien aux écailles d'or blanc a enfin ouvert ses deux yeux ; il règne sur les hauteurs, entouré d'une aura dorée étincelante.",
    "cobblemon.ability.goldenfrenzy": "Écailles en furie dorée",
    "cobblemon.ability.goldenfrenzy.desc": "Augmente de 25 % la puissance des capacités Dragon et Fée et double les chances d'effet de ses attaques de lumière. Il subit 25 % de dégâts en plus des capacités Poison et de l'empoisonnement.",
})

# ================================================================================================ shared
dump(f"{D}/cobblemon/species_feature_assignments/monster_hunter_mega.json",
     {"pokemon": MEGA_IDS, "features": ["mega_evolution"]})
dump(f"{D}/cobblemon/dexes/monster_hunter.json", {
    "type": "cobblemon:simple_pokedex_def", "id": "cobblemon:monster_hunter", "sortOrder": 13,
    "entries": [f"cobblemon:{s}" for s in SPECIES_IDS]})
dump(f"{D}/cobblemon/dex_additions/monster_hunter_national.json",
     {"dexId": "cobblemon:national", "entries": ["cobblemon:monster_hunter"]})
# a Mega Stone for every mod that looks at Mega Showdown's tag
dump(f"{D}/mega_showdown/tags/item/mega_stone.json", {"replace": False, "values": [
    f"{MOD}:deviljhonite", f"{MOD}:glavenusite", f"{LEGACY_MOD}:deviljhonite"]})
dump(f"{D}/cobblemon/species_feature_assignments/zamtrios_form.json", {"pokemon": ["zamtrios"], "features": ["zamtrios_form"]})
dump(f"{D}/cobblemon/species_feature_assignments/magala_frenzy.json", {"pokemon": ["goremagala"], "features": ["magala_frenzy"]})
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
    forms = ", ".join(f"{f['name']} {f.get('baseScale', d['baseScale'])}" for f in d["forms"])
    print(f"{sid}: baseScale {d['baseScale']} ({forms or 'no form'}), hitbox height {d['hitbox']['height']}")
