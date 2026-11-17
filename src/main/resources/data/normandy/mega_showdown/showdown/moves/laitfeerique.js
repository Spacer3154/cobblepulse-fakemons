{
  num: 7703,
  accuracy: true,
  basePower: 0,
  category: "Status",
  name: "Lait Feerique",
  pp: 5,
  priority: 0,
  flags: { heal: 1, bypasssub: 1, allyanim: 1, metronome: 1 },
  onHit(pokemon) {
    const healed = !!this.heal(this.modify(pokemon.maxhp, 0.15));
    return pokemon.cureStatus() || healed;
  },
  secondary: null,
  target: "allies",
  type: "Fairy"
}
