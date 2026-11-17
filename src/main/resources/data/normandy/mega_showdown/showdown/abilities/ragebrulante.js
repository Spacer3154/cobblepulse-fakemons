{
  onTryBoost(boost, target, source, effect) {
    if (source && target === source) return;
    let showMsg = false;
    let i;
    for (i in boost) {
      if (boost[i] < 0) {
        delete boost[i];
        showMsg = true;
      }
    }
    if (showMsg && !effect.secondaries && effect.id !== 'octolock') {
      this.add('-fail', target, 'unboost', '[from] ability: Rage Brulante', '[of] ' + target);
    }
  },
  onDamagingHit(damage, target, source, move) {
    if (!target.hp) return;
    const hit = target.getMoveHitData(move);
    if (hit.crit || hit.typeMod > 0) {
      this.boost({ atk: 1 }, target, target);
    }
  },
  flags: { breakable: 1 },
  name: "Rage Brulante",
  rating: 4,
  num: 7807
}
