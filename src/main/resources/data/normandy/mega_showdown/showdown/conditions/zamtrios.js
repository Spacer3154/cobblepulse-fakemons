(function () {
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
