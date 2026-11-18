// Glavenus through Pokemon Showdown: custom held item (Glavenusite), ability (Lame du Chaos) and move (Queue-Lame)
// loaded like Mega Showdown, species injected like Cobblemon's ShowdownSpecies.
const fs = require('fs'), path = require('path');
const { Dex, Battle, Teams } = require('pokemon-showdown');
const base = path.join(process.argv[2], 'data/normandy/mega_showdown/showdown');
const load = f => eval('(' + fs.readFileSync(f, 'utf8').split('\n').join(' ') + ')');
Dex.data.Items.glavenusite = load(path.join(base, 'held_items/glavenusite.js'));
Dex.data.Abilities.lameduchaos = load(path.join(base, 'abilities/lameduchaos.js'));
Dex.data.Moves.queuelame = load(path.join(base, 'moves/queuelame.js'));
const sp = JSON.parse(fs.readFileSync(path.join(process.argv[2], 'data/cobblemon/species/monster_hunter/glavenus.json')));
const st = s => ({ hp: s.hp, atk: s.attack, def: s.defence, spa: s.special_attack, spd: s.special_defence, spe: s.speed });
const T = t => t[0].toUpperCase() + t.slice(1);
const abil = a => Dex.abilities.get(a.replace('h:', '')).name;
Dex.data.Pokedex.glavenus = { num: sp.nationalPokedexNumber, name: 'Glavenus', types: [T(sp.primaryType), T(sp.secondaryType)],
  baseStats: st(sp.baseStats), abilities: { 0: abil(sp.abilities[0]), H: abil(sp.abilities[1]) },
  heightm: sp.height / 10, weightkg: sp.weight / 10, otherFormes: ['Glavenus-Mega'], formeOrder: ['Glavenus', 'Glavenus-Mega'] };
const f = sp.forms[0];
Dex.data.Pokedex.glavenusmega = { num: sp.nationalPokedexNumber, name: 'Glavenus-Mega', baseSpecies: 'Glavenus', forme: 'Mega',
  types: [T(f.primaryType), T(f.secondaryType)], baseStats: st(f.baseStats), abilities: { 0: abil(f.abilities[0]) },
  heightm: f.height / 10, weightkg: f.weight / 10 };
for (const id of ['glavenus', 'glavenusmega']) Dex.data.FormatsData[id] = { tier: 'OU' };
let fails = 0; const check = (l, c, x = '') => { console.log(`${c ? 'PASS' : 'FAIL'}  ${l}${x ? '  -> ' + x : ''}`); if (!c) fails++; };
const mon = (species, ability, moves, extra = {}) => ({ species, ability, moves, level: 50, evs: {}, ivs: { hp: 31, atk: 31, def: 31, spa: 31, spd: 31, spe: 31 }, nature: 'Hardy', ...extra });
const battle = (a, b, seed = [1, 2, 3, 4]) => { const x = new Battle({ formatid: 'gen9customgame', seed });
  x.setPlayer('p1', { name: 'A', team: Teams.pack(a) }); x.setPlayer('p2', { name: 'B', team: Teams.pack(b) });
  if (x.requestState === 'teampreview') x.makeChoices('default', 'default'); return x; };
// one hit of `move` from (species, ability) on a level 100 bulky foe: returns damage dealt and the log
const hit = (species, ability, move, foe, seed = [1, 2, 3, 4]) => {
  const b = battle([mon(species, ability, [move])], [mon(foe, 'Pressure', ['splash'], { level: 100, evs: { hp: 252, def: 252, spd: 252 } })], seed);
  const t = b.p2.active[0]; const hp0 = t.hp; const s = b.log.length; b.makeChoices('move 1', 'move 1');
  return { dmg: hp0 - t.hp, log: b.log.slice(s).join('\n') }; };

check('base abilities = Sharpness / H: Anger Shell',
  JSON.stringify(Dex.species.get('glavenus').abilities) === JSON.stringify({ 0: 'Sharpness', H: 'Anger Shell' }));
check('Fire/Steel, mega Fire/Dragon', Dex.species.get('glavenus').types.join('/') === 'Fire/Steel' && Dex.species.get('glavenusmega').types.join('/') === 'Fire/Dragon');
check('item megaStone maps Glavenus -> Glavenus-Mega', Dex.items.get('glavenusite').megaStone.Glavenus === 'Glavenus-Mega');
{
  const b = battle([mon('Glavenus', 'Sharpness', ['queuelame', 'scratch'], { item: 'Glavenusite' })], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const p = b.p1.active[0];
  check('Glavenus can mega evolve', p.canMegaEvo === 'Glavenus-Mega', String(p.canMegaEvo));
  b.makeChoices('move 2 mega', 'move 1');
  const log = b.log.join('\n');
  check('-mega message', log.includes('|-mega|p1a: Glavenus'));
  check('now Glavenus-Mega with Lame du Chaos', p.species.name === 'Glavenus-Mega' && p.ability === 'lameduchaos');
  check('no error in log', !log.includes('|error|'));
}
// Queue-Lame
const q = Dex.moves.get('queuelame');
check('Queue-Lame: Steel, physical, 80 BP, 100 acc, 5 PP, slicing + contact',
  q.type === 'Steel' && q.category === 'Physical' && q.basePower === 80 && q.accuracy === 100 && q.pp === 5 && q.flags.slicing && q.flags.contact);
{ const r = hit('Glavenus', 'Pressure', 'queuelame', 'Venusaur'); check('vs Venusaur (Grass, weak to Fire): super effective', r.log.includes('-supereffective'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus', 'Pressure', 'queuelame', 'Scizor'); check('vs Scizor (4x weak to Fire): super effective', r.log.includes('-supereffective'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus', 'Pressure', 'queuelame', 'Vaporeon'); check('vs Vaporeon (resists Steel and Fire): resisted', r.log.includes('-resisted'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus', 'Pressure', 'queuelame', 'Snorlax'); check('vs Snorlax: neutral', !r.log.includes('-supereffective') && !r.log.includes('-resisted') && r.dmg > 0, `dmg ${r.dmg}`); }
{ const a = hit('Glavenus', 'Pressure', 'queuelame', 'Snorlax').dmg, b = hit('Glavenus', 'Sharpness', 'queuelame', 'Snorlax').dmg;
  check('Sharpness (Incisif) boosts Queue-Lame ~x1.5', b / a > 1.4 && b / a < 1.6, `${a} -> ${b}`); }
// Lame du Chaos
{ const a = hit('Glavenus-Mega', 'Pressure', 'queuelame', 'Snorlax').dmg, b = hit('Glavenus-Mega', 'Lame du Chaos', 'queuelame', 'Snorlax').dmg;
  check('Lame du Chaos boosts slicing moves ~x1.7', b / a > 1.6 && b / a < 1.8, `${a} -> ${b}`); }
{ const a = hit('Glavenus-Mega', 'Pressure', 'flamethrower', 'Snorlax').dmg, b = hit('Glavenus-Mega', 'Lame du Chaos', 'flamethrower', 'Snorlax').dmg;
  check('Lame du Chaos: non-slicing moves unchanged', a === b, `${a} -> ${b}`); }
{ const r = hit('Glavenus-Mega', 'Lame du Chaos', 'slash', 'Golem'); check('Lame du Chaos: Slash (Normal) super effective on Golem (Rock/Ground)', r.log.includes('-supereffective'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus-Mega', 'Pressure', 'slash', 'Golem'); check('without it: Slash resisted by Golem', r.log.includes('-resisted'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus-Mega', 'Lame du Chaos', 'flamethrower', 'Golem'); check('Lame du Chaos: Flamethrower (not slicing) still resisted by Golem', r.log.includes('-resisted'), `dmg ${r.dmg}`); }
{ const r = hit('Glavenus-Mega', 'Lame du Chaos', 'queuelame', 'Vaporeon'); check('Lame du Chaos keeps Queue-Lame\'s own effectiveness (Vaporeon resists)', r.log.includes('-resisted'), `dmg ${r.dmg}`); }
console.log(fails ? `${fails} FAILURES` : 'ALL CHECKS PASSED');
process.exit(fails ? 1 : 0);
