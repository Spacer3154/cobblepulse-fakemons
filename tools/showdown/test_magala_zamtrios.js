// Zamtrios (forme changes), Gore Magala (Frenzy) and Shagaru Magala (Golden Frenzy) through Pokemon Showdown:
// the species conditions and the ability are loaded like Mega Showdown loads them (newlines -> spaces, evaluated in a
// scope where Dex exists, as in Showdown's index.js), the species injected like Cobblemon's ShowdownSpecies.
const fs = require('fs'), path = require('path');
const { Dex, Battle, Teams } = require('pokemon-showdown');
const pack = process.argv[2];
const base = path.join(pack, 'data/normandy/mega_showdown/showdown');
const load = f => eval('(' + fs.readFileSync(f, 'utf8').split('\n').join(' ') + ')');
Dex.data.Abilities.goldenfrenzy = load(path.join(base, 'abilities/goldenfrenzy.js'));
const T = t => t[0].toUpperCase() + t.slice(1);
const st = s => ({ hp: s.hp, atk: s.attack, def: s.defence, spa: s.special_attack, spd: s.special_defence, spe: s.speed });
const abil = list => { const o = {}; let i = 0; for (const a of list) { if (a.startsWith('h:')) o.H = Dex.abilities.get(a.slice(2)).name || a.slice(2); else o[i++] = Dex.abilities.get(a).name || a; } return o; };
const inject = sid => {
  const sp = JSON.parse(fs.readFileSync(path.join(pack, `data/cobblemon/species/monster_hunter/${sid}.json`)));
  const types = d => [T(d.primaryType)].concat(d.secondaryType ? [T(d.secondaryType)] : []);
  const names = sp.forms.map(f => `${sp.name}-${f.name}`);
  Dex.data.Pokedex[sid] = { num: sp.nationalPokedexNumber, name: sp.name, types: types(sp), baseStats: st(sp.baseStats),
    abilities: abil(sp.abilities), heightm: sp.height / 10, weightkg: sp.weight / 10, gender: sp.maleRatio < 0 ? 'N' : undefined,
    otherFormes: names.length ? names : undefined, formeOrder: names.length ? [sp.name, ...names] : undefined };
  for (const f of sp.forms) {
    const id = Dex.toID(`${sp.name}-${f.name}`);
    Dex.data.Pokedex[id] = { num: sp.nationalPokedexNumber, name: `${sp.name}-${f.name}`, baseSpecies: sp.name, forme: f.name,
      types: types(f), baseStats: st(f.baseStats), abilities: abil(f.abilities), heightm: f.height / 10, weightkg: f.weight / 10,
      gender: sp.maleRatio < 0 ? 'N' : undefined, battleOnly: f.battleOnly ? sp.name : undefined };
    Dex.data.FormatsData[id] = { tier: 'OU' };
  }
  Dex.data.FormatsData[sid] = { tier: 'OU' };
  const cond = path.join(base, `conditions/${sid}.js`);
  if (fs.existsSync(cond)) Dex.data.Conditions[sid] = load(cond);
  return sp;
};
const Z = inject('zamtrios'), G = inject('goremagala'), C = inject('chaoticgoremagala'), S = inject('shagarumagala');
let fails = 0; const check = (l, c, x = '') => { console.log(`${c ? 'PASS' : 'FAIL'}  ${l}${x ? '  -> ' + x : ''}`); if (!c) fails++; };
const mon = (species, ability, moves, extra = {}) => ({ species, ability, moves, level: 50, evs: {}, ivs: { hp: 31, atk: 31, def: 31, spa: 31, spd: 31, spe: 31 }, nature: 'Hardy', ...extra });
const battle = (a, b, seed = [1, 2, 3, 4]) => { const x = new Battle({ formatid: 'gen9customgame', seed });
  x.setPlayer('p1', { name: 'A', team: Teams.pack(a) }); x.setPlayer('p2', { name: 'B', team: Teams.pack(b) });
  if (x.requestState === 'teampreview') x.makeChoices('default', 'default'); return x; };
const noError = b => !b.log.some(l => l.startsWith('|error|'));

// ---------------------------------------------------------------- data
check('Zamtrios: Water/Ice, abilities Fur Coat / Strong Jaw / H: Swift Swim',
  Dex.species.get('zamtrios').types.join('/') === 'Water/Ice' &&
  JSON.stringify(Dex.species.get('zamtrios').abilities) === JSON.stringify({ 0: 'Fur Coat', 1: 'Strong Jaw', H: 'Swift Swim' }));
check('Zamtrios formes: Armor (world + battle) and Inflated (battle only)',
  Dex.species.get('zamtriosarmor').exists && Dex.species.get('zamtriosinflated').battleOnly === 'Zamtrios');
check('Gore Magala: Dark/Dragon, genderless; Frenzy is battle only',
  Dex.species.get('goremagala').types.join('/') === 'Dark/Dragon' && Dex.species.get('goremagala').gender === 'N' &&
  Dex.species.get('goremagalafrenzy').battleOnly === 'Gore Magala');
check('Shagaru Magala: Dragon/Fairy, only Golden Frenzy and H: Multiscale',
  Dex.species.get('shagarumagala').types.join('/') === 'Dragon/Fairy' &&
  JSON.stringify(Dex.species.get('shagarumagala').abilities) === JSON.stringify({ 0: 'Golden Frenzy', H: 'Multiscale' }));
check('BSTs 515 / 580 / 620 / 650', [Z, G, C, S].map(s => Object.values(s.baseStats).reduce((a, b) => a + b)).join() === '515,580,620,650');

// ---------------------------------------------------------------- Zamtrios
{
  const b = battle([mon('Zamtrios', 'Strong Jaw', ['tackle', 'icefang', 'stockpile'])], [mon('Blissey', 'Natural Cure', ['splash'])]);
  const p = b.p1.active[0];
  b.makeChoices('move 1', 'move 1');
  check('Zamtrios: a non-Ice move keeps the normal forme', p.species.name === 'Zamtrios');
  b.makeChoices('move 2', 'move 1');
  check('Zamtrios: an Ice move (Ice Fang) -> Ice Armor forme', p.species.name === 'Zamtrios-Armor', p.species.name);
  check('  ... it keeps its own ability (Strong Jaw)', p.ability === 'strongjaw', p.ability);
  check('  ... Armor stats: higher Defense, lower Speed', p.storedStats.def > 120 && p.storedStats.spe < 70, JSON.stringify(p.storedStats));
  check('  ... detailschange sent (Cobblemon -> FormeChangeEvent "armor")', b.log.some(l => l.startsWith('|detailschange|p1a: Zamtrios|Zamtrios-Armor')));
  b.makeChoices('move 3', 'move 1');
  check('Zamtrios: Stockpile -> Inflated forme', p.species.name === 'Zamtrios-Inflated', p.species.name);
  b.makeChoices('move 2', 'move 1');
  check('  ... an Ice move does not bring the armour back once inflated', p.species.name === 'Zamtrios-Inflated');
  check('  ... no error in the log', noError(b));
}
{
  const b = battle([mon('Zamtrios', 'Fur Coat', ['tackle']), mon('Snorlax', 'Thick Fat', ['splash'])],
    [mon('Machamp', 'No Guard', ['closecombat'], { level: 70 })]);
  const p = b.p1.active[0];
  for (let i = 0; i < 4 && p.hp > p.maxhp / 2; i++) b.makeChoices('move 1', 'move 1');
  check('Zamtrios: at half HP or less -> Inflated', !p.hp || p.species.name === 'Zamtrios-Inflated', `${p.hp}/${p.maxhp} ${p.species.name}`);
  if (p.hp) {
    b.makeChoices('switch 2', 'move 1'); b.makeChoices('switch 2', 'move 1');
    check('  ... still Inflated after switching out and back in (permanent forme change)', b.p1.active[0].species.name === 'Zamtrios-Inflated', b.p1.active[0].species.name);
  }
  check('  ... no error in the log', noError(b));
}
{
  const b = battle([mon('Zamtrios-Armor', 'Fur Coat', ['icefang'])], [mon('Blissey', 'Natural Cure', ['splash'])]);
  const p = b.p1.active[0];
  b.makeChoices('move 1', 'move 1');
  check('Zamtrios sent out armoured (frozen biome) stays Armor and still has the handlers', p.species.name === 'Zamtrios-Armor' && !!Dex.species.get('zamtriosarmor').onUpdate);
}
// ---------------------------------------------------------------- Gore Magala
{
  const b = battle([mon('Gore Magala', 'Infiltrator', ['darkpulse'])], [mon('Machamp', 'No Guard', ['brickbreak'], { level: 38 })]);
  const p = b.p1.active[0];
  b.makeChoices('move 1', 'move 1');
  check('Gore Magala: above half HP, normal forme', p.hp <= p.maxhp / 2 || p.species.name === 'Gore Magala', `${p.hp}/${p.maxhp}`);
  for (let i = 0; i < 4 && p.hp > p.maxhp / 2; i++) b.makeChoices('move 1', 'move 1');
  check('Gore Magala: at half HP or less -> Frenzy (Mode Furie)', p.hp > 0 && p.species.name === 'Gore Magala-Frenzy', `${p.hp}/${p.maxhp} ${p.species.name}`);
  check('  ... keeps Infiltrator', !p.hp || p.ability === 'infiltrator', p.ability);
  check('  ... detailschange "Gore Magala-Frenzy"', !p.hp || b.log.some(l => l.includes('|detailschange|p1a: Gore Magala|Gore Magala-Frenzy')));
  check('  ... no error in the log', noError(b));
}
// ---------------------------------------------------------------- Golden Frenzy
const hit = (species, ability, move, foe, foeMoves = ['splash'], seed = [1, 2, 3, 4], extra = {}) => {
  const b = battle([mon(species, ability, [move], extra)], [mon(foe, 'Pressure', foeMoves, { level: 100, evs: { hp: 252, def: 252, spd: 252 } })], seed);
  const t = b.p2.active[0]; const hp0 = t.hp; b.makeChoices('move 1', 'move 1');
  return { dmg: hp0 - t.hp, b };
};
{ const a = hit('Shagaru Magala', 'Pressure', 'dragonpulse', 'Snorlax').dmg, b = hit('Shagaru Magala', 'Golden Frenzy', 'dragonpulse', 'Snorlax').dmg;
  check('Golden Frenzy: Dragon moves ~x1.25', b / a > 1.18 && b / a < 1.32, `${a} -> ${b}`); }
{ const a = hit('Shagaru Magala', 'Pressure', 'moonblast', 'Snorlax').dmg, b = hit('Shagaru Magala', 'Golden Frenzy', 'moonblast', 'Snorlax').dmg;
  check('Golden Frenzy: Fairy moves ~x1.25', b / a > 1.18 && b / a < 1.32, `${a} -> ${b}`); }
{ const a = hit('Shagaru Magala', 'Pressure', 'psychic', 'Snorlax').dmg, b = hit('Shagaru Magala', 'Golden Frenzy', 'psychic', 'Snorlax').dmg;
  check('Golden Frenzy: other moves unchanged', a === b, `${a} -> ${b}`); }
{ // Poison moves hit it 25 % harder
  const taken = ability => { const b = battle([mon('Shagaru Magala', ability, ['splash'], { evs: { hp: 252 } })], [mon('Nidoking', 'Pressure', ['sludgebomb'])]);
    const p = b.p1.active[0]; const h0 = p.hp; b.makeChoices('move 1', 'move 1'); return h0 - p.hp; };
  const a = taken('Pressure'), b = taken('Golden Frenzy');
  check('Golden Frenzy: Poison moves hurt it ~x1.25', b / a > 1.18 && b / a < 1.32, `${a} -> ${b}`);
}
{ // poison damage at the end of the turn
  const resid = ability => { const b = battle([mon('Shagaru Magala', ability, ['splash'])], [mon('Nidoking', 'Pressure', ['splash'])]);
    const p = b.p1.active[0]; p.setStatus('psn'); if (p.status !== 'psn') return -1;
    const h0 = p.hp; b.makeChoices('move 1', 'move 1'); return { d: h0 - p.hp, max: p.maxhp }; };
  const a = resid('Pressure'), b = resid('Golden Frenzy');
  check('Golden Frenzy: poison damage x1.25', a !== -1 && b !== -1 && b.d === Math.floor(Math.floor(b.max / 8) * 1.25), `${JSON.stringify(a)} -> ${JSON.stringify(b)}`);
}
{ // Moonblast: 30 % chance to lower SpA, doubled to 60 %
  const rate = ability => { let n = 0; const N = 300;
    for (let i = 0; i < N; i++) { const r = hit('Shagaru Magala', ability, 'moonblast', 'Snorlax', ['splash'], [i + 1, 7, 9, 11]);
      if (r.b.log.some(l => l.startsWith('|-unboost|p2a: Snorlax|spa'))) n++; }
    return n / N; };
  const a = rate('Pressure'), b = rate('Golden Frenzy');
  check('Golden Frenzy: Moonblast secondary effect twice as likely (light move)', a > 0.2 && a < 0.4 && b > 0.5 && b < 0.7, `${a.toFixed(2)} -> ${b.toFixed(2)}`);
}
{ const r = hit('Shagaru Magala', 'Multiscale', 'moonblast', 'Snorlax'); check('Multiscale available as H', Dex.species.get('shagarumagala').abilities.H === 'Multiscale' && r.dmg > 0); }
console.log(fails ? `${fails} FAILURES` : 'ALL CHECKS PASSED');
process.exit(fails ? 1 : 0);
