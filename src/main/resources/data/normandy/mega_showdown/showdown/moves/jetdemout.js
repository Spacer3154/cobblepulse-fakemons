{
  num: 7701,
  accuracy: 100,
  basePower: 85,
  basePowerCallback(pokemon, target, move) {
    if (this.field.isTerrain('grassyterrain') || ['raindance', 'primordialsea'].includes(pokemon.effectiveWeather())) {
      return 110;
    }
    return move.basePower;
  },
  category: "Special",
  name: "Jet de Mout",
  pp: 5,
  priority: 0,
  flags: { protect: 1, mirror: 1, metronome: 1 },
  secondary: {
    chance: 30,
    volatileStatus: "confusion"
  },
  target: "normal",
  type: "Grass"
}
