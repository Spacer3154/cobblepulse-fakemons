({
  name: "Glavenusite",
  spritenum: 0,
  megaStone: { "Glavenus": "Glavenus-Mega" },
  itemUser: ["Glavenus"],
  onTakeItem(item, source) {
    return !item.megaStone?.[source.baseSpecies.baseSpecies];
  },
  num: 7902,
  gen: 9,
  isNonstandard: "Past",
})
