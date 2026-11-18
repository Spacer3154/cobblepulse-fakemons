{
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
