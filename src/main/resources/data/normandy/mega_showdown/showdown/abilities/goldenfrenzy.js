{
  onBasePowerPriority: 21,
  onBasePower(basePower, attacker, defender, move) {
    if (move.type === 'Dragon' || move.type === 'Fairy') {
      return this.chainModify([5120, 4096]);
    }
  },
  onModifyMovePriority: -2,
  onModifyMove(move) {
    const light = ['moonblast', 'dazzlinggleam', 'flashcannon', 'mirrorshot', 'lusterpurge', 'mistball', 'aurorabeam',
      'chargebeam', 'signalbeam', 'psybeam', 'photongeyser', 'prismaticlaser', 'lightofruin', 'fleurcannon', 'solarbeam',
      'solarblade', 'moongeistbeam', 'sunsteelstrike', 'doomdesire', 'spiritbreak', 'mysticalfire', 'fierydance',
      'magicalleaf'];
    if (!light.includes(move.id)) return;
    if (move.secondaries) {
      for (const secondary of move.secondaries) {
        if (secondary.chance) secondary.chance = Math.min(100, secondary.chance * 2);
      }
    }
  },
  onSourceModifyDamage(damage, source, target, move) {
    if (move.type === 'Poison') {
      return this.chainModify([5120, 4096]);
    }
  },
  onDamage(damage, target, source, effect) {
    if (effect && (effect.id === 'psn' || effect.id === 'tox')) {
      return Math.floor(damage * 1.25);
    }
  },
  flags: {},
  name: "Golden Frenzy",
  rating: 3.5,
  num: 7809
}
