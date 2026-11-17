{
  num: 7706,
  accuracy: 85,
  basePower: 110,
  category: "Special",
  name: "Flambee d'Eau-de-Vie",
  pp: 5,
  priority: 0,
  flags: { protect: 1, mirror: 1, metronome: 1 },
  onEffectiveness(typeMod, target, type) {
    if (type === 'Water' || type === 'Ground') return 1;
  },
  secondary: {
    chance: 15,
    status: "brn"
  },
  target: "normal",
  type: "Fire"
}
