(function () {
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
