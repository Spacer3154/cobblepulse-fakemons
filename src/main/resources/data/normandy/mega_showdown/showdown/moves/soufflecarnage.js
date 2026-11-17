{
  num: 7708,
  accuracy: 100,
  basePower: 85,
  category: "Special",
  name: "Souffle Carnage",
  pp: 10,
  priority: 0,
  flags: { protect: 1, mirror: 1, metronome: 1 },
  onModifyMove(move, pokemon, target) {
    if (!target) return;
    const atk = pokemon.getStat('atk', false, true);
    const spa = pokemon.getStat('spa', false, true);
    const def = target.getStat('def', false, true);
    const spd = target.getStat('spd', false, true);
    const physical = Math.floor(Math.floor(Math.floor(Math.floor(2 * pokemon.level / 5 + 2) * 85 * atk) / def) / 50);
    const special = Math.floor(Math.floor(Math.floor(Math.floor(2 * pokemon.level / 5 + 2) * 85 * spa) / spd) / 50);
    if (physical > special || (physical === special && this.random(2) === 0)) {
      move.category = 'Physical';
    }
  },
  secondary: {
    chance: 100,
    boosts: { def: -1 }
  },
  target: "normal",
  type: "Dragon",
  contestType: "Tough"
}
