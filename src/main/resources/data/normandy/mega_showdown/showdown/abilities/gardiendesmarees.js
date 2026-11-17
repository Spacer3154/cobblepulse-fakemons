{
  onStart(pokemon) {
    this.add('-ability', pokemon, 'Gardien des Marees');
    pokemon.abilityState.ending = false;
    this.eachEvent('WeatherChange', this.effect);
  },
  onEnd(pokemon) {
    pokemon.abilityState.ending = true;
    this.eachEvent('WeatherChange', this.effect);
  },
  suppressWeather: true,
  onModifyDamage(damage, source, target, move) {
    return this.chainModify([5324, 4096]);
  },
  flags: {},
  name: "Gardien des Marees",
  rating: 4,
  num: 7804
}
