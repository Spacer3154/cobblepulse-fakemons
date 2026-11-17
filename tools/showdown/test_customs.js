// Loads the custom moves/abilities exactly like Mega Showdown does
// (newlines -> spaces, then eval of "(" + content + ")"), then runs battle checks.
const fs = require('fs');
const path = require('path');
const { Dex, Battle, Teams } = require('pokemon-showdown');

const root = process.argv[2];
const base = path.join(root, 'data/normandy/mega_showdown/showdown');
const loaded = { moves: [], abilities: [] };
for (const kind of ['moves', 'abilities']) {
  for (const f of fs.readdirSync(path.join(base, kind))) {
    const id = f.replace('.js', '');
    const js = fs.readFileSync(path.join(base, kind, f), 'utf8').split('\n').join(' ');
    const obj = eval(`(${js})`);
    if (kind === 'moves') Dex.data.Moves[id] = obj; else Dex.data.Abilities[id] = obj;
    // Same JSON round-trip Mega Showdown uses to build the Cobblemon MoveTemplate
    if (kind === 'moves') {
      const j = JSON.parse(JSON.stringify(obj));
      for (const k of ['num', 'type', 'category', 'basePower', 'target', 'accuracy', 'pp', 'priority']) {
        if (j[k] === undefined) throw new Error(`${id}: missing ${k} for MoveTemplate`);
      }
    }
    if (Dex.toID(obj.name) !== id) throw new Error(`${id}: toID(name)=${Dex.toID(obj.name)} != file id`);
    loaded[kind].push(id);
  }
}
console.log('Loaded', loaded);

let failures = 0;
function check(label, cond, extra = '') {
  console.log(`${cond ? 'PASS' : 'FAIL'}  ${label}${extra ? '  -> ' + extra : ''}`);
  if (!cond) failures++;
}
function mon(species, ability, moves, extra = {}) {
  return { species, ability, moves, level: 50, evs: { hp: 0, atk: 0, def: 0, spa: 0, spd: 0, spe: 0 }, ivs: { hp: 31, atk: 31, def: 31, spa: 31, spd: 31, spe: 31 }, nature: 'Hardy', ...extra };
}
function battle(p1team, p2team, seed = [1, 2, 3, 4], format = 'gen9customgame') {
  const b = new Battle({ formatid: format, seed });
  b.setPlayer('p1', { name: 'A', team: Teams.pack(p1team) });
  b.setPlayer('p2', { name: 'B', team: Teams.pack(p2team) });
  if (b.requestState === 'teampreview') b.makeChoices('default', 'default');
  return b;
}
const log = b => b.log.join('\n');
const after = (b, start) => b.log.slice(start).join('\n');

// 1. Every custom move can be used without crashing
for (const id of loaded.moves) {
  const b = battle([mon('Mew', 'Synchronize', [id])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  b.makeChoices('move 1', 'move 1');
  check(`move ${id} runs`, !log(b).includes('|error|') && log(b).includes(`|move|p1a: Mew|${Dex.moves.get(id).name}`));
}

// 2. Jet de Mout: 85 BP, 110 in rain / grassy terrain
{
  const b = battle([mon('Mew', 'Synchronize', ['jetdemout', 'raindance', 'grassyterrain'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const m = Dex.moves.get('jetdemout');
  const p = b.p1.active[0], t = b.p2.active[0];
  check('Jet de Mout BP normal = 85', m.basePowerCallback.call(b, p, t, m) === 85);
  b.makeChoices('move 2', 'move 1');
  check('Jet de Mout BP under rain = 110', m.basePowerCallback.call(b, p, t, m) === 110);
  const b2 = battle([mon('Mew', 'Synchronize', ['grassyterrain'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  b2.makeChoices('move 1', 'move 1');
  check('Jet de Mout BP on grassy terrain = 110', m.basePowerCallback.call(b2, b2.p1.active[0], b2.p2.active[0], m) === 110);
}

// 3. Sillage Ardent: neutral on Water, still resisted by Rock
{
  const b = battle([mon('Mew', 'Synchronize', ['sillageardent'])], [mon('Vaporeon', 'Water Absorb', ['splash'])]);
  b.makeChoices('move 1', 'move 1');
  check('Sillage Ardent neutral vs pure Water', !log(b).includes('|-resisted|') && !log(b).includes('|-supereffective|'));
  const b2 = battle([mon('Mew', 'Synchronize', ['sillageardent'])], [mon('Omastar', 'Swift Swim', ['splash'])]);
  b2.makeChoices('move 1', 'move 1');
  check('Sillage Ardent resisted by Water/Rock (Rock only)', log(b2).includes('|-resisted|'));
}

// 4. Lait Feerique: heals 15% (nerfed from 50%) and cures status
{
  const b = battle([mon('Mew', 'Synchronize', ['laitfeerique'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const p = b.p1.active[0];
  const start = Math.floor(p.maxhp * 0.3);
  p.sethp(start); p.setStatus('par');
  b.makeChoices('move 1', 'move 1');
  const gained = p.hp - start, want = Math.floor(p.maxhp * 0.15);
  check('Lait Feerique heals 15%', Math.abs(gained - want) <= 1, `+${gained} (want ~${want}) ${p.hp}/${p.maxhp}`);
  check('Lait Feerique cures status', !p.status, p.status);
  const b2 = battle([mon('Mew', 'Synchronize', ['laitfeerique'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const q = b2.p1.active[0];
  q.sethp(Math.floor(q.maxhp * 0.9)); q.setStatus('brn');
  b2.makeChoices('move 1', 'move 1');
  check('Lait Feerique cures status even near full HP', !q.status && !log(b2).includes('|-fail|'), q.status);
}

// 4b. Starter signature moves: 5 PP, 8 with max PP Ups
for (const id of ['jetdemout', 'sillageardent', 'laitfeerique']) {
  const b = battle([mon('Mew', 'Synchronize', [id])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const slot = b.p1.active[0].moveSlots[0];
  check(`${id}: 5 PP, max 8`, Dex.moves.get(id).pp === 5 && slot.maxpp === 8, `pp ${Dex.moves.get(id).pp}, max ${slot.maxpp}`);
}

// 5. Hache-Pince: crit ratio and ignoreDefensive kept by Showdown
{
  const m = Dex.moves.get('hachepince');
  check('Hache-Pince critRatio 2 (+1 stage)', m.critRatio === 2);
  check('Hache-Pince ignoreDefensive', m.ignoreDefensive === true);
}

// 6. Flambee d'Eau-de-Vie: super effective vs Water and Ground, 4x vs Water/Ground
{
  for (const [sp, ab] of [['Vaporeon', 'Water Absorb'], ['Sandaconda', 'Shed Skin'], ['Quagsire', 'Oblivious']]) {
    const b = battle([mon('Mew', 'Synchronize', ['flambeedeaudevie'])], [mon(sp, ab, ['splash'])], [5, 6, 7, 8]);
    b.makeChoices('move 1', 'move 1');
    const hit = !log(b).includes('|-miss|');
    if (hit) check(`Flambee super effective vs ${sp}`, log(b).includes('|-supereffective|'));
    else console.log(`(missed vs ${sp}, re-run seed)`);
  }
  const t = new Battle({ formatid: 'gen9customgame' });
  const m = Dex.moves.get('flambeedeaudevie');
  let mod = 0;
  for (const type of ['Water', 'Ground']) {
    const r = m.onEffectiveness.call(t, Dex.getEffectiveness('Fire', type), null, type, m);
    mod += (r === undefined ? Dex.getEffectiveness('Fire', type) : r);
  }
  check('Flambee 4x vs Water/Ground', mod === 2, `typeMod=${mod}`);
}

// 7. Eclair Souverain: recoil + SpA drop
{
  const b = battle([mon('Mew', 'Synchronize', ['eclairsouverain'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  b.makeChoices('move 1', 'move 1');
  check('Eclair Souverain recoil', log(b).includes('[from] Recoil'));
  check('Eclair Souverain SpA -1', b.p2.active[0].boosts.spa === -1);
}

// 10. Combustion Distillee: no burn damage, SpA x1.5 when burned or hit by Fire
{
  const b = battle([mon('Mew', 'combustiondistillee', ['splash'])], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const p = b.p1.active[0];
  const spa0 = p.getStat('spa');
  p.setStatus('brn');
  const hp0 = p.hp;
  b.makeChoices('move 1', 'move 1');
  check('Combustion Distillee: no burn damage', p.hp === hp0, `${hp0} -> ${p.hp}`);
  const spa1 = b.runEvent('ModifySpA', p, null, null, spa0);
  check('Combustion Distillee: SpA x1.5 when burned', spa1 === Math.floor(spa0 * 1.5), `${spa0} -> ${spa1}`);
  const b2 = battle([mon('Volcanion', 'combustiondistillee', ['splash'])], [mon('Arcanine', 'Intimidate', ['ember'])]);
  b2.makeChoices('move 1', 'move 1');
  const q = b2.p1.active[0];
  const spa2 = b2.runEvent('ModifySpA', q, null, null, q.getStat('spa'));
  check('Combustion Distillee: SpA x1.5 after a Fire hit', spa2 === Math.floor(q.getStat('spa') * 1.5), `${q.getStat('spa')} -> ${spa2}`);
}

// 11. Gardien des Marees: weather suppressed + damage x1.3
{
  const b = battle([mon('Togekiss', 'gardiendesmarees', ['hurricane'])], [mon('Pelipper', 'Drizzle', ['splash'])]);
  b.makeChoices('move 1', 'move 1');
  check('Gardien des Marees suppresses weather', b.field.isWeather('raindance') === false && b.field.weather === 'raindance');
  const dmg = b.runEvent('ModifyDamage', b.p1.active[0], b.p2.active[0], b.dex.getActiveMove('hurricane'), 100);
  check('Gardien des Marees damage x1.3', dmg === 130, `100 -> ${dmg}`);
}

// 12. Sabots d'Obsidienne: hazards + Fire immunity
{
  const b = battle(
    [mon('Snorlax', 'Thick Fat', ['stealthrock', 'spikes', 'stickyweb', 'flamethrower'])],
    [mon('Mew', 'Synchronize', ['splash']), mon('Mamoswine', 'sabotsdobsidienne', ['splash'])]
  );
  b.makeChoices('move 1', 'move 1');
  b.makeChoices('move 2', 'move 1');
  b.makeChoices('move 3', 'move 1');
  b.makeChoices('move 1', 'switch 2');
  const p = b.p2.active[0];
  check('Sabots: no Stealth Rock / Spikes damage on switch-in', p.hp === p.maxhp, `${p.hp}/${p.maxhp}`);
  check('Sabots: Sticky Web blocked', p.boosts.spe === 0, `spe=${p.boosts.spe}`);
  const start = b.log.length;
  b.makeChoices('move 4', 'move 1');
  check('Sabots: immune to Fire moves', after(b, start).includes('|-immune|p2a: Mamoswine|[from] ability: Sabots') && p.hp === p.maxhp);
}

// 13. Aureole Royale: Intimidate + Motor Drive
{
  const b = battle([mon('Magnezone', 'aureoleroyale', ['splash'])], [mon('Jolteon', 'Volt Absorb', ['thunderbolt'])]);
  check('Aureole Royale: foe Atk -1 on entry', b.p2.active[0].boosts.atk === -1);
  b.makeChoices('move 1', 'move 1');
  const p = b.p1.active[0];
  check('Aureole Royale: Electric immunity + Spe +1', p.hp === p.maxhp && p.boosts.spe === 1, `hp ${p.hp}/${p.maxhp} spe ${p.boosts.spe}`);
}

console.log(failures ? `\n${failures} FAILURE(S)` : '\nALL CHECKS PASSED');
process.exit(failures ? 1 : 0);
