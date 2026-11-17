{
  onStart(pokemon) {
    let activated = false;
    for (const target of pokemon.adjacentFoes()) {
      if (!activated) {
        this.add('-ability', pokemon, 'Aureole Royale', 'boost');
        activated = true;
      }
      if (target.volatiles['substitute']) {
        this.add('-immune', target);
      } else {
        this.boost({ atk: -1 }, target, pokemon, null, true);
      }
    }
  },
  onTryHit(target, source, move) {
    if (target !== source && move.type === 'Electric') {
      if (!this.boost({ spe: 1 })) {
        this.add('-immune', target, '[from] ability: Aureole Royale');
      }
      return null;
    }
  },
  flags: { breakable: 1 },
  name: "Aureole Royale",
  rating: 4,
  num: 7806
}
