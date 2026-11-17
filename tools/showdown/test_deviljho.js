// Deviljho through Pokemon Showdown: custom held item, ability and move loaded like Mega Showdown, species injected
// like Cobblemon's ShowdownSpecies; mega evolution, Rage Brulante, Souffle Carnage.
const fs = require('fs'), path = require('path');
const { Dex, Battle, Teams } = require('pokemon-showdown');
const base = path.join(process.argv[2], 'data/normandy/mega_showdown/showdown');
const load = f => eval('(' + fs.readFileSync(f, 'utf8').split('\n').join(' ') + ')');
Dex.data.Items.deviljhonite = load(path.join(base, 'held_items/deviljhonite.js'));
Dex.data.Abilities.ragebrulante = load(path.join(base, 'abilities/ragebrulante.js'));
Dex.data.Moves.soufflecarnage = load(path.join(base, 'moves/soufflecarnage.js'));
const sp = JSON.parse(fs.readFileSync(path.join(process.argv[2], 'data/cobblemon/species/monster_hunter/deviljho.json')));
const st = s => ({ hp: s.hp, atk: s.attack, def: s.defence, spa: s.special_attack, spd: s.special_defence, spe: s.speed });
const T = t => t[0].toUpperCase() + t.slice(1);
const abil = a => Dex.abilities.get(a.replace('h:', '')).name;
Dex.data.Pokedex.deviljho = { num: sp.nationalPokedexNumber, name: 'Deviljho', types: [T(sp.primaryType), T(sp.secondaryType)],
  baseStats: st(sp.baseStats), abilities: { 0: abil(sp.abilities[0]), 1: abil(sp.abilities[1]), H: abil(sp.abilities[2]) },
  heightm: sp.height / 10, weightkg: sp.weight / 10, otherFormes: ['Deviljho-Mega'], formeOrder: ['Deviljho', 'Deviljho-Mega'] };
const f = sp.forms[0];
Dex.data.Pokedex.deviljhomega = { num: sp.nationalPokedexNumber, name: 'Deviljho-Mega', baseSpecies: 'Deviljho', forme: 'Mega',
  types: [T(f.primaryType), T(f.secondaryType)], baseStats: st(f.baseStats), abilities: { 0: abil(f.abilities[0]) },
  heightm: f.height / 10, weightkg: f.weight / 10 };
for (const id of ['deviljho', 'deviljhomega']) Dex.data.FormatsData[id] = { tier: 'OU' };
let fails = 0; const check = (l, c, x = '') => { console.log(`${c ? 'PASS' : 'FAIL'}  ${l}${x ? '  -> ' + x : ''}`); if (!c) fails++; };
const mon = (species, ability, moves, extra = {}) => ({ species, ability, moves, level: 50, evs: {}, ivs: { hp: 31, atk: 31, def: 31, spa: 31, spd: 31, spe: 31 }, nature: 'Hardy', ...extra });
const battle = (a, b) => { const x = new Battle({ formatid: 'gen9customgame', seed: [1, 2, 3, 4] });
  x.setPlayer('p1', { name: 'A', team: Teams.pack(a) }); x.setPlayer('p2', { name: 'B', team: Teams.pack(b) });
  if (x.requestState === 'teampreview') x.makeChoices('default', 'default'); return x; };

check('base abilities = Thick Fat / Reckless / H: Toxic Boost',
  JSON.stringify(Dex.species.get('deviljho').abilities) === JSON.stringify({ 0: 'Thick Fat', 1: 'Reckless', H: 'Toxic Boost' }));
check('item megaStone maps Deviljho -> Deviljho-Mega', Dex.items.get('deviljhonite').megaStone.Deviljho === 'Deviljho-Mega');
{
  const b = battle([mon('Deviljho', 'Thick Fat', ['soufflecarnage', 'tackle'], { item: 'Deviljhonite' })], [mon('Snorlax', 'Thick Fat', ['splash'])]);
  const p = b.p1.active[0];
  check('Deviljho can mega evolve', p.canMegaEvo === 'Deviljho-Mega', String(p.canMegaEvo));
  b.makeChoices('move 2 mega', 'move 1');
  const log = b.log.join('\n');
  check('-mega message', log.includes('|-mega|p1a: Deviljho'));
  check('now Deviljho-Mega with Rage Brulante', p.species.name === 'Deviljho-Mega' && p.ability === 'ragebrulante');
  check('no error in log', !log.includes('|error|'));
}
// Rage Brulante
const rb = (foe, foeAbility, foeMove) => { const b = battle([mon('Deviljho-Mega', 'Rage Brulante', ['splash'], { level: 100, evs: { hp: 252, def: 252, spd: 252 } })],
  [mon(foe, foeAbility, [foeMove])]); const p = b.p1.active[0]; const s = b.log.length; b.makeChoices('move 1', 'move 1');
  return { atk: p.boosts.atk, def: p.boosts.def, log: b.log.slice(s).join('\n'), p }; };
{
  const b = battle([mon('Deviljho-Mega', 'Rage Brulante', ['splash'])], [mon('Gyarados', 'Intimidate', ['splash'])]);
  check('Intimidate blocked', b.p1.active[0].boosts.atk === 0 && b.log.join('\n').includes('[from] ability: Rage Brulante'));
}
{ const r = rb('Mew', 'Synchronize', 'screech'); check('Screech blocked (Def unchanged)', r.def === 0, `def ${r.def}`); }
{ const r = rb('Clefable', 'Magic Guard', 'moonblast'); check('super-effective hit: +1 Atk', r.atk === 1, `atk ${r.atk}`); }
{ const r = rb('Urshifu', 'Unseen Fist', 'wickedblow'); check('critical hit (resisted): +1 Atk', r.atk === 1 && r.log.includes('-crit'), `atk ${r.atk}`); }
{ const r = rb('Snorlax', 'Thick Fat', 'tackle'); check('neutral non-crit hit: no boost', r.atk === 0, `atk ${r.atk}`); }
{ const b = battle([mon('Deviljho-Mega', 'Rage Brulante', ['dracometeor'])], [mon('Blissey', 'Natural Cure', ['splash'], { level: 100, evs: { hp: 252 } })]);
  b.makeChoices('move 1', 'move 1'); check('own Draco Meteor still lowers its Sp. Atk', b.p1.active[0].boosts.spa === -2); }
// Souffle Carnage
const sc = (foe, extra = {}) => { const b = battle([mon('Deviljho', 'Thick Fat', ['soufflecarnage'])], [mon(foe, 'Pressure', ['splash'], { level: 100, ...extra })]);
  const m = Dex.getActiveMove('soufflecarnage'); const p = b.p1.active[0], t = b.p2.active[0];
  m.flags = { ...m.flags }; Dex.moves.get('soufflecarnage').onModifyMove.call(b, m, p, t);
  b.makeChoices('move 1', 'move 1'); return { cat: m.category, def: t.boosts.def, log: b.log.join('\n') }; };
{ const r = sc('Blissey'); check('vs Blissey (huge Sp. Def): physical', r.cat === 'Physical', r.cat); check('lowers Defense', r.def === -1); check('runs', r.log.includes('|move|p1a: Deviljho|Souffle Carnage')); }
{ const r = sc('Skarmory'); check('vs Skarmory (huge Def): special', r.cat === 'Special', r.cat); }
check('Dragon, 85 BP, 100 acc, 10 PP', (m => m.type === 'Dragon' && m.basePower === 85 && m.accuracy === 100 && m.pp === 10)(Dex.moves.get('soufflecarnage')));
console.log(fails ? `${fails} FAILURES` : 'ALL CHECKS PASSED');
