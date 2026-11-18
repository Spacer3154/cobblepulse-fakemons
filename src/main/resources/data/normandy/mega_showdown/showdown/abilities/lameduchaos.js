{
  onBasePowerPriority: 19,
  onBasePower(basePower, attacker, defender, move) {
    if (move.flags['slicing']) {
      return this.chainModify([6963, 4096]);
    }
  },
  onModifyMove(move) {
    if (!move.flags['slicing']) return;
    const previous = move.onEffectiveness;
    move.onEffectiveness = function (typeMod, target, type, m) {
      let mod = typeMod;
      if (previous) {
        const r = previous.call(this, typeMod, target, type, m);
        if (typeof r === 'number') mod = r;
      }
      if (type === 'Rock') return 1;
      return mod;
    };
  },
  flags: {},
  name: "Lame du Chaos",
  rating: 4,
  num: 7808
}
