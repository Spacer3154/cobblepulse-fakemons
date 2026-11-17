{
  num: 7702,
  accuracy: 100,
  basePower: 90,
  category: "Physical",
  name: "Sillage Ardent",
  pp: 5,
  priority: 0,
  flags: { contact: 1, protect: 1, mirror: 1, metronome: 1 },
  onEffectiveness(typeMod, target, type) {
    if (type === 'Water') return 0;
  },
  secondary: {
    chance: 20,
    status: "brn"
  },
  target: "normal",
  type: "Fire"
}
