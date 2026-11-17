{
  onDamage(damage, target, source, effect) {
    if (effect && (effect.id === 'stealthrock' || effect.id === 'spikes')) {
      return false;
    }
  },
  onTryBoost(boost, target, source, effect) {
    if (effect && effect.id === 'stickyweb' && boost.spe) {
      delete boost.spe;
      this.add('-activate', target, 'ability: Sabots d\'Obsidienne');
    }
  },
  onTryHit(target, source, move) {
    if (target !== source && move.type === 'Fire') {
      this.add('-immune', target, '[from] ability: Sabots d\'Obsidienne');
      return null;
    }
  },
  flags: { breakable: 1 },
  name: "Sabots d'Obsidienne",
  rating: 3.5,
  num: 7805
}
