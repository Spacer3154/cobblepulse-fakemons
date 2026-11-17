({
  name: "Deviljhonite",
  spritenum: 0,
  megaStone: { "Deviljho": "Deviljho-Mega" },
  itemUser: ["Deviljho"],
  onTakeItem(item, source) {
    return !item.megaStone?.[source.baseSpecies.baseSpecies];
  },
  num: 7901,
  gen: 9,
  isNonstandard: "Past",
})
