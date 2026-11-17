{
  onDamage(damage, target, source, effect) {
    if (effect && effect.id === 'brn') {
      return false;
    }
  },
  onDamagingHit(damage, target, source, move) {
    if (move.type === 'Fire' && !this.effectState.ignited) {
      this.effectState.ignited = true;
      this.add('-ability', target, 'Combustion Distillee');
    }
  },
  onModifySpAPriority: 5,
  onModifySpA(spa, pokemon) {
    if (pokemon.status === 'brn' || this.effectState.ignited) {
      return this.chainModify(1.5);
    }
  },
  flags: {},
  name: "Combustion Distillee",
  rating: 3,
  num: 7803
}
