# CobblePulse-Ecology — contenu du mod (Cobblemon 1.8.4, Minecraft 1.21.1)

Anciennement « Normandy Fakemons » (jusqu'à la 2.3) : renommé en 3.0.0 (identifiant `cobblepulse_ecology`). Les
données gardent l'espace de noms `normandy` ; l'ancien objet `normandy_fakemons:deviljhonite` reste valable.

## Prérequis
- Minecraft 1.21.1 + Fabric (et Fabric API), **Cobblemon 1.8.4**
- **Mega Showdown** (version 1.3.3+1.8.4 ou plus récente) — obligatoire.
  C'est lui qui charge les 6 capacités signatures et les 4 talents custom
  (`data/normandy/mega_showdown/showdown/`). Sans lui, Alchibec, Archangelis,
  Sleipcheron et Guillopard ne se chargent pas.

## Installation (mod)
Un seul fichier `cobblepulse-ecology-<version>+mc1.21.1.jar` (mod Fabric, il remplace `normandy_fakemons-*.jar`) qui contient le code, les données (espèces,
apparitions, Pokédex, Showdown, recette…) et les ressources (modèles, textures, animations, langue).
- **Serveur** : `mods/` du serveur. **Clients** : `mods/` de chaque joueur (obligatoire : objets et modèles).
- Dépendances : Fabric API, Cobblemon 1.8.4, Mega Showdown (et ses propres dépendances).
- Retirer l'ancien datapack `Normandy_Fakemons_…zip` du dossier `world/datapacks/` et l'ancien resource pack,
  ainsi que les anciens fichiers Deviljho d'un autre pack : le mod les remplace.

## Contenu
- 22 espèces complètes (`data/cobblemon/species/normandy/`). Les lignées Clambert/Moulembert et
  Poireauval/Poiréthane ont été retirées du Pokédex et du pack (n° 1042 à 1045 laissés libres).
- 6 capacités + 4 talents en JavaScript Showdown
- 34 fichiers d'apparition (22 espèces + 12 hordes et Alphas) et 12 groupes de biomes (voir « Apparitions »)
- Pokédex régional « Normandie », ajouté au Pokédex national
- Catégorie **Monster Hunter** : Deviljho (méga : Deviljho Carnage, Deviljhonite), Glavenus (méga : Glavenus
  Lame-Chaos, Glavenusite), Zamtrios et la lignée Magala (3.1.0), voir plus bas ; Pokédex « Monster Hunter » ajouté
  au national
- Langue `fr_fr` (et `en_us`, identique, en solution de repli)

## Changements par rapport à la v1
- `gargoylbâtre.json` → `gargoylbatre.json` (le « â » est interdit dans un chemin Minecraft)
- Champs `name` sans accent (Cobblemon en dérive l'identifiant : « Étreroch » donnait `treroch`
  et cassait les évolutions). Les accents sont dans le fichier de langue.
- `alchemy` → `powerofalchemy` (talent inexistant, l'espèce ne se chargeait pas)
- Identifiants sans underscore : `jet_de_mout` → `jetdemout`, etc.
- Anciens dossiers `moves/` et `abilities/` (format JSON non lu par Cobblemon) remplacés par le Showdown JS
- Ajout de `implemented`, `catchRate`, `maleRatio`, `experienceGroup`, `eggGroups`, `height`/`weight`,
  `hitbox`, `evYield`, `labels`, `behaviour`, `drops`, `preEvolution`
- Movesets complets : capacités par niveau, CT (uniquement de vraies CT de Pokémon Écarlate/Violet) et capacités œuf
- Hache-Pince : `critRatio` 2 (+1 cran) et `ignoreDefensive` ; Lait Féerique : cible `allies`

## Choix à valider
- « Alchimie » n'existe pas dans Pokémon : le talent officiel le plus proche est Osmose
  (`powerofalchemy`), qui n'a d'effet qu'en combat double.
- Normanguer garde `naturalcure` (Médic Nature) en talent caché (le PDF indique « Cœur de Coq »).
- Noroimard garde `ironfist` (Poing de Fer), mais ce talent n'améliore aucune de ses capacités.
  Suggestion : `sharpness` (Incisif), qui renforcerait Hache-Pince (marquée « tranchante »).
- Aéroblast, Soin, Chute Glace, Chgt Vitesse, Pouvoir Lunaire, Fracass'Tête, Pince-Masse :
  listées en `tm:` dans la v1, ce ne sont pas des CT. Elles s'apprennent donc par niveau.
- Alchibec est de type Feu, donc il ne peut pas être brûlé : seule la partie
  « touché par une capacité Feu » de Combustion Distillée le concerne.
- Tailles, hitbox et `baseScale` sont provisoires, à ajuster avec les modèles.

## Modèles
- Fait (23/23, + Deviljho Carnage) : lignées Pomdraco, Drakflam, Meuhgousse, Étreroch, Rousselin, Homarbleu et Bolvados,
  Archangelis, Sleipcheron et Guillopard (modèle, textures normale et shiny, animations dont KO, poser, resolver). Flammes émissives animées pour la lignée Drakflam, yeux-braises
  émissifs pour Gargoylbâtre ; cidre, esprits et flammes émissifs pour la lignée Bolvados.
- Lignée Drakflam : squelette bipède digitigrade. La marche, le cri dressé et la mise en garde sont calculés
  par cinématique inverse : les pieds restent plantés au sol pendant l'appui.
- Lignée Étreroch (d'après le Grand Gravelot) : ailes repliées au sol et ailes déployées en vol, comme les
  oiseaux officiels de Cobblemon. Les ailes d'Archéolithe et de Gargoylbâtre sont percées d'une arche.
- Portraits d'équipe et du Résumé : cadrages calculés à partir de la géométrie, avec la même formule que
  Cobblemon.

- Lignée Rousselin (Roussin de la Hague) : Rousselin évolue en Roussinage en montant d'un niveau s'il connaît
  Glas de Soin (appris au niveau 25, ou par œuf / tuteur), comme Cochignon → Mammochon.

- Lignée Homarbleu : huit pattes marcheuses en cinématique inverse (les pointes restent plantées), pinces,
  antennes et queue animées ; poses à terre et sous l'eau. Homarbleu trottine de côté. Homarbleu apprend
  Hache-Pince au niveau 44 et évolue en Noroimard en montant d'un niveau s'il la connaît.

- Lignée Bolvados : tailles du Pokédex relevées (0,5 m / 1,3 m / 2,6 m) pour que chaque stade soit plus grand
  que le précédent en jeu. Toute la lignée lévite (environ un quart de bloc au-dessus du sol) et ne se pose qu'en
  dormant ou K.O. Bolvados (bolée de grès à vague bleue) sort ses mains de cidre ; Cruchevados (cruche vernissée,
  fêlure brûlante, sans pieds) a des yeux qui tourbillonnent ; Alchibec (alambic de cuivre, pieds ballants) titube
  en l'air, et son esprit de feu à six yeux rentre dans le dôme pour dormir.
  Shiny : faïence de Rouen et pommeau ; grès vert du Pré-d'Auge ; flammes bleues de calvados flambé.

- Archangelis (légendaire, 4,75 m) : dragon quadrupède doré, armure d'opale à spirales, cristaux irisés, deux paires
  d'ailes (grandes ailes de chauve-souris à membrane « nébuleuse » lumineuse, environ 10 blocs d'envergure, et
  petites ailes à plumes sous les épaules), gueule détaillée (crocs, langue, menton à épines), auréoles et
  sceaux lumineux qui flottent autour de lui. Au sol, les grandes ailes sont repliées ; en combat, elles se lèvent en
  V comme sur l'image ; il vole (vol stationnaire et vol battu). Shiny : platine, membrane nuit étoilée, cristaux saphir.

## Apparitions (format Cobblemon 1.8)
- Fichiers : `data/cobblemon/spawn_pool_world/` (hordes et Alphas dans `herds/`). Chaque apparition a des conditions
  (biomes, heure, météo, lumière, phase de lune, blocs proches) et des bonus ou malus de poids (`weightMultipliers`).
  Les Poké Snacks doublent le poids de la plupart des espèces (pas celui des légendaires).
- Hordes et Alphas : chaque lignée (sauf Bolvados et les légendaires) apparaît aussi en horde. Un Alpha (seau `boss`)
  mène sa horde et tient le Joyau de son type. Ces espèces ont la règle de troupeau de la 1.8 (`behaviour.herd`).
- Légendaires (Archangelis, Sleipcheron, Guillopard) : étiquette `legendary`, niveau 70, 3 IV parfaits, jamais dans les
  villages. Toutes les apparitions du pack portent aussi l'étiquette `normandy` (utile pour les règles d'apparition d'un
  serveur).

Groupes de biomes (`data/normandy/tags/worldgen/biome/`, à utiliser comme `#normandy:bocage`) :

| Groupe | Paysage |
|---|---|
| `bocage` | Prairies et pâturages tempérés |
| `vergers` | Vergers, bois d'automne, forêts fleuries |
| `cote_albatre` | Falaises de craie, plages de galets |
| `falaises` | Falaises, crêtes et collines venteuses |
| `landes_hague` | Landes et collines venteuses (La Hague) |
| `marais` | Marais, tourbières, rivières |
| `baie_du_mont` | Plages, galets et îlots tempérés |
| `plaines_givrees` | Plaines enneigées et toundra |
| `aurores` | Biomes à aurores boréales |
| `cieux_de_l_end` | Hautes terres de l'End |
| `nether_des_ames` | Vallées des âmes du Nether |
| `nether_brasier` | Deltas de basalte, terres de magma |

Mods de biomes couverts (biomes optionnels : le pack se charge sans eux) : Biomes O' Plenty, Oh The Biomes We've
Gone, Terralith, William Wythers' Overhauled Overworld, Better End et Better Nether. Les tags de Cobblemon, utilisés
en plus, couvrent déjà beaucoup de biomes moddés. Oh The Biomes You'll Go (BYG) n'existe pas en 1.21.1 : son
successeur, Oh The Biomes We've Gone, est couvert.

| Espèce | Où | Quand, bonus et malus |
|---|---|---|
| Pomdraco, Arboverger, Cidrac | Vergers, bocage, forêts (aussi dans les arbres) | ×2,5 en verger, ×1,5 le matin (Pomdraco), ×1,5 au crépuscule (Cidrac), ×0,5 la nuit |
| Drakflam, Vikinav | Côtes, Côte d'Albâtre, falaises | ×2 près d'un feu de camp (Drakflam), ×3 près d'une épave (Vikinav), malus sous la pluie |
| Drakkarthor | Côtes la nuit ; à la surface de la mer froide la nuit ; vallées des âmes du Nether | ×4 près d'une épave, ×2 sous la pluie, ×2 à la nouvelle lune en mer |
| Meuhgousse, Normanguer | Bocage, prairies, rivières | ×2 dans le bocage, ×2 près de bottes de foin, ×1,5 sous la pluie, ×0,25 la nuit, ×1,5 à la pleine lune (Normanguer) |
| Bovécume | Marais, rivières, plages | ×2,5 sous l'orage, ×1,5 sous la pluie, ×2 près de la boue |
| Étreroch, Archéolithe | Côte d'Albâtre, falaises, côtes, montagnes (de jour pour Étreroch) | ×2 sur la Côte d'Albâtre, ×0,5 sous la pluie (Étreroch), ×1,5 sous l'orage (Archéolithe) |
| Gargoylbâtre | Falaises, crêtes, sommets ; cités de l'End | ×2 sous l'orage, ×1,5 la nuit |
| Rousselin, Roussinage | Landes de La Hague, collines, hauts plateaux, côtes | ×2 dans les landes, ×1,5 sous l'orage, ×0,25 la nuit |
| Homarbleu | Fonds de mer froide ou tempérée, sur les côtes la nuit, à la pêche | ×2 près des ruines et épaves, ×1,5 la nuit, appât de pêche |
| Noroimard | Grands fonds froids, à la pêche, côtes les nuits d'orage | ×2 près des ruines et épaves, ×1,5 la nuit |
| Bolvados, Cruchevados | Caves et souterrains (sous Y 50 / Y 30), ruines de sentier (Cruchevados) | ×4 près de tonneaux, ×3 près de pots décorés, ×2 sous un verger ou le bocage |
| Alchibec | Profondeurs près de la lave, caves près de tonneaux, Nether brûlant | ×3 près de tonneaux |
| Archangelis | Baie du Mont : plages, galets, îlots ; hautes terres de l'End | ×2 à l'aube et au crépuscule, ×2,5 à la pleine et à la nouvelle lune (grandes marées) |
| Sleipcheron | Plaines gelées la nuit ; bocage à minuit sous l'orage | ×3 sous la neige, ×2 à la pleine lune, ×2 sous les aurores |
| Guillopard | Bocage, falaises, collines, seulement sous l'orage | ×3 près d'un paratonnerre, ×2 près d'une bannière |

## Monture : Noroimard
- Une place sur la carapace, entre les créneaux. Sur terre : `cobblemon:land/horse` ; dans l'eau :
  `cobblemon:liquid/submarine` (il plonge, comme Wailord et Sinistrail).

## Monture : Roussinage
- Une place sur le dos, comportement terrestre `cobblemon:land/horse` (marche, galop quand on sprinte).
- Affiché environ 25 % plus grand que sa taille du Pokédex (1,3 m) pour qu'on puisse le monter.
  Pour revenir à 1,3 m : `baseScale` 0,65.

- Sleipcheron (légendaire, 2,6 m au chignon) : étalon percheron de glace bleu-gris veiné de givre, yeux nacrés
  lumineux, cristaux de givre sur le front, le garrot, l'encolure et la croupe, crinière et queue XXL de brume
  polaire aux reflets d'aurore boréale (lumineuses), fanons givrés et sabots d'obsidienne cerclés de lueur bleue
  avec des éclats de givre. Tête sculptée (profil droit, arcades, crête faciale, ganaches, naseaux évasés, dents
  visibles quand il hennit, diadème de givre) et musculature de trait (poitrail, épaules, encolure en crête, croupe
  double, genoux et jarrets marqués), robe pommelée comme un percheron gris. Il broute, gratte le sol en combat et se cabre en hennissant pour son cri.
  Shiny : robe noire gelée, crinière et queue vert aurore.

- Guillopard (légendaire, 2,4 m au crâne) : léopard bleu nuit à rosettes, poitrail, ventre, gorge et joues dorés,
  arabesques d'or sur le front, les tempes et les épaules. Tête détaillée : sourcils froncés, grands yeux en amande
  bleu pâle lumineux à pupille fendue et liseré d'or, truffe en triangle, bouche de chat en Y, coussinets à
  moustaches électriques, petit menton en retrait, pointes des crocs qui dépassent, crocs et langue visibles quand
  il rugit. Crinière de flammes d'or parcourue d'éclairs, couronne de cinq éclairs d'or (diamant bleu sur celui de
  devant) sur un anneau de lumière, qui flotte bien au-dessus de la crinière. Jambières d'or gravées de violet,
  jarrets dorés, flammes autour des pattes. La queue pend, remonte puis s'enroule en une énorme touffe de flammes
  d'or (quatre nappes autour de la queue, langues de flamme au bout). Des arcs électriques crépitent autour de lui. Sa couronne est animée : elle
  tourne sur elle-même, ses anneaux tournent en sens inverse en pulsant et ses cinq pointes montent et descendent
  en vague (plus vite en combat, deux tours d'un coup quand il rugit, elle ralentit et s'éteint quand il est K.O.).
  En combat il tient sa position, une patte en avant, tête un peu basse et immobile, regard plissé sous des
  sourcils froncés, grondement sourd, queue basse dont seul le bout bat. Il rugit pour son cri et dort en sphinx.
  Shiny : les armes de la Normandie, un léopard d'or aux flammes et jambières de gueules (rouge).

## Monture : Archangelis
- Une place (`seat_1`) sur le dos, entre les racines des ailes. Au sol : `cobblemon:land/horse` (les ailes
  repliées s'écartent pour laisser la place au cavalier) ; en vol : `cobblemon:air/bird` (vol battu, plané,
  piqué ailes rabattues), avec les sons de vent officiels.
- Statistiques de monture (bloc `riding` de `archangelis.json`) : la meilleure monture volante du pack (rapide,
  très endurante), correcte au sol.
- Pas d'agrandissement : il fait déjà 4,75 m.

## Monture : Sleipcheron
- Une place (`seat_1`) sur le dos, entre le garrot et la croupe. Comportement terrestre `cobblemon:land/horse`.
- Au pas il marche comme d'habitude ; quand le cavalier sprinte, il part au grand galop (crinière et queue
  couchées par le vent, encolure qui pompe) ; en saut, antérieurs repliés et postérieurs lancés en arrière.
- Statistiques (bloc `riding` de `sleipcheron.json`) : la monture terrestre la plus rapide et la plus endurante du
  pack, moins agile.

## Monture : Guillopard
- Une place (`seat_1`) sur le dos, derrière les épaules. Comportement terrestre `cobblemon:land/horse`.
- Au sprint, galop bondissant de félin (dos qui se plie et se déplie, queue tendue en arrière, crinière et couronne
  qui flambent) ; en saut, il bondit pattes avant tendues et pattes arrière étirées.
- Statistiques (bloc `riding` de `guillopard.json`) : la meilleure accélération, le meilleur saut et la meilleure
  maniabilité du pack, endurance plus courte.

## Monture : Gargoylbâtre
- Une place (`seat_1`, sur le dos). Au sol : comportement `cobblemon:land/horse` ; en vol :
  `cobblemon:air/bird` (vol battu, plané, piqué), avec les sons de vent officiels.
- Statistiques de monture (bloc `riding` de `gargoylbatre.json`) : vol rapide et endurant, marche lente.
- Gargoylbâtre est affiché environ 20 % plus grand que sa taille du Pokédex (1,6 m), comme beaucoup de
  montures officielles. Sinon le dresseur paraît plus grand que lui. Pour revenir à 1,6 m : `baseScale` 0,87.

## Monster Hunter : Deviljho (n° 1052, Dragon / Ténèbres)
- Espèce : `data/cobblemon/species/monster_hunter/deviljho.json`. Talents : **Isograisse**, **Téméraire**,
  **Rage Poison** (caché). Taille du Pokédex : 5,5 m et 950 kg (le fichier d'origine indiquait 206,3 pour les deux) ;
  en jeu, environ 5,5 blocs de haut au dos (`baseScale` 1,73).
- Capacité signature **Souffle Carnage** (niveau 50) : Dragon, puissance 85, précision 100, 10 PP. Physique ou
  spéciale selon l'adversaire (comme la capacité signature de Flagadoss de Galar : la catégorie qui lui fait le plus de dégâts d'après sa Défense et
  sa Défense Spéciale) ; baisse toujours la Défense de la cible d'un cran.
- Modèle (d'après l'image de référence) : wyverne brute vert olive-brun, dos voûté, peau écailleuse à plaques,
  petites cicatrices rouges (émissives). **Tête** : les dents de Deviljho poussent hors de la bouche, en massue
  dorée — la mâchoire inférieure est une énorme masse arrondie hérissée de pointes (devant, côtés, dessous et
  couronne de dents sur le bord), la mâchoire supérieure porte un « nez » de pointes et une rangée de crocs pendants
  sur chaque côté ; gueule rose à palais rouge strié, grosse langue rose, tissus de la gueule visibles quand elle
  s'ouvre. **Yeux** : petits, jaune ambré à pupille fendue, bord rouge, sous une arcade épineuse. **Queue** : épaisse,
  relevée et recourbée vers le haut, épines dorsales brun-rouge de plus en plus longues vers le bout, pointes dorées
  sur les flancs, dessous dentelé, éventail de grandes pointes au bout. Griffes à pointe rouge. Shiny : noir obsidienne.
- Regard : petits yeux fendus enfoncés dans une orbite sombre, iris ambre qui accroche la lumière (émissif), pupille
  noire en fente, bord rouge, sous des arcades épineuses froncées en V qui pèsent sur le coin avant de l'œil.
  Filets de bave qui pendent de la mâchoire.
- Animations (toutes pensées pour un prédateur) :
  - **attente** : respiration lourde, tête basse qui balaie le terrain de gauche à droite en s'inclinant, reniflements
    rapides, gueule pendante qui bave, puis un claquement de mâchoire soudain (tête qui tressaute, griffes serrées) ;
  - **marche** : traque, tête basse tendue vers l'avant, gueule ouverte, arcades froncées ;
  - **garde de combat** : accroupi, poids qui roule d'un côté à l'autre, poitrail qui se soulève, grognement (mâchoire
    grande ouverte qui tremble), tête basse pointée sur l'adversaire, deux claquements de mâchoire et une violente
    secousse de tête par cycle, queue qui fouette, griffes qui se serrent, yeux plissés ;
  - **cri** : il inspire, se dresse, rugit en secouant la tête de gauche à droite, bras écartés, queue qui fouette ;
  - **attaque physique** : se cabre gueule ouverte, se jette en avant, mord deux fois puis secoue la tête comme pour
    déchiqueter sa proie, et recule en grognant ;
  - **attaque spéciale** : se cabre en tremblant pendant que l'énergie draconique bout dans sa gueule, puis crache le
    rayon en balayant ;
  - **attaque de statut** : parade d'intimidation (il se dresse, écarte les griffes et grogne en secouant la tête) ;
  - **coup reçu** : la tête est rejetée sur le côté, il recule… et revient aussitôt en grognant ;
  - **K.O.** : rejeté en arrière, il titube, pose la queue au sol, s'assoit puis se couche doucement ;
  - sommeil et clignement.

## Méga-évolution : Deviljho Carnage
- Forme `Mega` (Mega Showdown) : Dragon / Ténèbres, 700 de total (PV 110, Att 190, Déf 90, Att Spé 125,
  Déf Spé 100, Vit 85), 6,4 m. Talent signature **Rage Brûlante** : les autres Pokémon ne peuvent pas baisser
  ses statistiques (comme Corps Sain, Intimidation comprise ; ses propres baisses, Draco Météore par exemple,
  s'appliquent toujours) et son Attaque monte d'un cran chaque fois qu'il subit un coup critique ou une capacité
  super efficace. Le Pokédex affiche la forme « Carnage ».
- Modèle (d'après l'illustration) : posture plus dressée, muscles gonflés, dos et nuque rouge sang fendus de veines
  incandescentes, gueule qui brûle de l'intérieur, yeux chauffés à blanc (fente noire, halo rouge) qui laissent une
  traînée de lumière, bave d'énergie.
  **Aura draconique** : un miasme noir et rouge (plans croisés qui tourbillonnent, gonflent et montent) s'élève de
  la tête, de la nuque, des épaules et du dos, et huit grands éclairs rouge sang ramifiés crépitent autour de la
  tête (deux en couronne au-dessus du crâne), de la mâchoire, du cou, du dos et de la queue (ils s'allument et
  s'éteignent sans arrêt) ; le miasme sort aussi de la gueule, des braises incandescentes montent à travers la fumée
  et s'éteignent, et la fumée elle-même rougeoie de l'intérieur. L'aura s'embrase à chaque cri, attaque ou coup reçu
  (la fumée gonfle, les éclairs se déchaînent). Animations propres, plus violentes (tremblement de rage permanent) ;
  au K.O. l'aura s'éteint. Shiny : corps obsidienne et énergie violette.
- Fichiers : `models/1052_deviljho/deviljho_carnage.geo.json`, poser et animations `deviljho_carnage`,
  resolver `1_deviljho_carnage.json` (aspect `mega`), textures + couches émissives animées.

## Deviljhonite
- **Vrai objet du mod** : `cobblepulse_ecology:deviljhonite`, dans l'onglet créatif « CobblePulse-Ecology » et dans
  l'onglet des Méga-Gemmes de Mega Showdown, avec sa description. Le code lui pose par défaut les deux composants
  de Mega Showdown (`registry_type_component` = `mega`, `registry_location_component` = `normandy:deviljhonite`) :
  Mega Showdown la reconnaît comme la méga-gemme de Deviljho (`data/normandy/mega_showdown/mega/deviljhonite.json`
  + objet Showdown `held_items/deviljhonite.js`). Elle est aussi dans le tag `mega_showdown:mega_stone`.
- Fabrication (établi) : Croc Dragon en haut, Bloc d'os à gauche et à droite, Méga-Gemme brute de Mega Showdown
  (`mega_showdown:mega_stone`) au centre, Lunettes Noires en bas. La recette se débloque dans le livre en ramassant
  une Méga-Gemme.
- Commandes : `/give @s cobblepulse_ecology:deviljhonite` ou `/function normandy:give_deviljhonite`.
- Les Deviljhonites fabriquées avec les versions 2.0 à 2.2 (Éclats d'écho) et 2.3 (`normandy_fakemons:deviljhonite`)
  continuent de fonctionner.
- Utilisation : comme toutes les méga-gemmes de Mega Showdown (Deviljho la tient, le dresseur porte un
  Méga-Bracelet, bouton Méga en combat).

## Apparition de Deviljho
- Uniquement dans les **Wasteland** de Biomes O' Plenty (`biomesoplenty:wasteland` et `wasteland_steppe`, groupe
  `#normandy:wastelands`), en **ultra-rare**, niveau 50-70 ; ×1,5 la nuit, ×2 pendant les orages. Sans Biomes O'
  Plenty, il n'apparaît pas à l'état sauvage. Étiquette `monster_hunter`.

# Glavenus (n° 1053) et Glavenus Lame-Chaos

## Glavenus
- Feu / Acier, 4,8 m, 320,5 kg, 540 de total (PV 110, Att 130, Déf 65, Att Spé 75, Déf Spé 95, Vit 65). Talents :
  **Incisif** (Sharpness) et, caché, **Courroupace** (Anger Shell). Groupes d'œufs Monstre et Dragon, 40 cycles.
  Pokédex : « Une wyverne de terre qui manie sa queue puissante comme une épée. Elle chauffe à chaque coup jusqu'à
  devenir brûlante. »
- Capacités (fiche) : niveau 1 Griffe, Groz'Yeux, Flammèche, Affûtage ; 6 Taillade ; 10 Hurlement ; 14 Griffe Acier ;
  18 Crocs Feu ; 22 Brouillard ; 26 Tranche ; 30 Mur de Fer ; 32 Allègement ; 34 Calcination ; 38 Tranche-Nuit ;
  42 Danse-Lames ; 48 **Queue-Lame** ; 54 Boutefeu ; 60 Lame d'Air ; 66 Colère ; 72 Queue de Fer. CT, Maître des
  capacités et capacités œuf : celles de la fiche.
- **Queue-Lame** (signature) : Acier, physique, 80 de puissance, 100 % de précision, 5 PP (8 au maximum), tranchante
  et avec contact. Elle compte aussi comme du Feu : contre chaque type de la cible, c'est la meilleure efficacité
  entre Acier et Feu qui s'applique (super efficace sur tout ce qui craint le Feu ; Cizayox la subit ×4, Aquali la
  résiste). Boostée par Incisif (×1,5) et Lame du Chaos (×1,7).
- Apparition : **ultra-rare**, niveau 50-70, dans les jungles (`#cobblemon:is_jungle`, à ciel ouvert, ×1,5 le jour)
  et les terres volcaniques (`#cobblemon:is_volcanic`). Étiquette `monster_hunter`.
- Modèle (d'après les références du jeu) : wyverne brute longue et athlétique, écailles cramoisies bordées de bleu
  nuit, ventre crème, pattes et tête blindées de plaques bleu nuit, pointes bleu nuit à pointe turquoise.
  **Tête** massive et anguleuse, entièrement blindée, mâchoire profonde, barbe de pointes sous le menton, grandes
  cornes du crâne relevées vers l'arrière, pointes sur les arcades, les joues et le museau, yeux en fentes turquoise
  lumineuses enfoncés sous l'arcade. **Cornes de flanc** : sur chaque hanche, un bouclier d'écailles couvre
  l'articulation ; il en sort une corne gigantesque, large comme une lame, qui monte puis se courbe vers la tête, et
  deux cornes moyennes (6 en tout). Crête de grandes pointes recourbées le long du cou et du dos. **Queue** : longue,
  tendue vers l'arrière ; sa seconde moitié s'aplatit en un immense cimeterre (tranchant en dessous, bord pâle,
  plat bleu acier veiné de turquoise lumineux, cristaux dentelés sur le dos de la lame). Quand il frappe, la lame
  rougit (surcouche incandescente). Shiny : écailles sarcelle sombre et lame vert acide.
- Animations : **attente** (respiration, tête qui balaie, reniflements, petite bouffée de feu), **marche**, **garde**
  (lame dressée en arc au-dessus du dos, qui se balance comme une épée en garde, grognement), **cri** (droit devant,
  gueule grande ouverte, légers mouvements de tête, lame relevée qui vibre et rougit), **attaque physique : Queue-Lame**
  (il se ramasse, puis tournoie sur lui-même en sautant, queue tendue et lame couchée tranchant en avant ; la lame
  rougit), **attaque spéciale** (souffle de feu balayé), **statut : affûtage** (il s'enroule en C, ramène la lame le
  long du flanc, la prend en travers de la gueule et la fait aller et venir entre ses dents jusqu'à ce qu'elle
  rougisse), **coup reçu**, **sommeil** (couché, queue ramenée sur le côté, lame à plat au sol), **K.O.** (il recule
  légèrement puis tombe doucement sur le flanc, sans saut), clignement.

## Méga-évolution : Glavenus Lame-Chaos
- Forme `Mega` : Feu / Dragon, 5,5 m, 410 kg, 640 de total (PV 110, Att 140, Déf 95, Att Spé 85, Déf Spé 120,
  Vit 90). Talent signature **Lame du Chaos** : +70 % de puissance aux capacités tranchantes, et ses capacités
  tranchantes sont super efficaces sur les Pokémon de type Roche (la partie Roche de la cible compte comme faible,
  comme Lyophilisation sur l'Eau ; les capacités non tranchantes ne changent pas). Le Pokédex affiche « Lame-Chaos ».
- Modèle : carapace charbon fendue de fissures rouges incandescentes, plaques rouge sombre, pointes et cornes rouge
  rosé, brume rouge-rose qui monte du dos, yeux rouges brûlants qui laissent une traînée, gueule qui rougeoie comme une
  forge, **lame en fusion** (bord blanc, orange, rouge) léchée de flammes, braises qui s'en échappent. Animations
  propres (les flammes s'embrasent à chaque cri ou attaque, s'éteignent au K.O.). Shiny : corps obsidienne, flammes
  bleu-blanc.
- Fichiers : `models/1053_glavenus/glavenus.geo.json` et `glavenus_lame_chaos.geo.json`, posers, animations,
  resolvers `0_glavenus_base.json` et `1_glavenus_lame_chaos.json` (aspect `mega`), textures et couches émissives
  animées.

## Glavenusite
- Objet du mod `cobblepulse_ecology:glavenusite` (onglet « CobblePulse-Ecology » et onglet des Méga-Gemmes de Mega
  Showdown), composants Mega Showdown posés par défaut (`normandy:glavenusite`).
- Fabrication : Pierre Feu en haut, Bloc de fer à gauche et à droite, Méga-Gemme brute (`mega_showdown:mega_stone`)
  au centre, Peau Métal en bas. Débloquée dans le livre de recettes en ramassant une Méga-Gemme.
- Commandes : `/give @s cobblepulse_ecology:glavenusite` ou `/function normandy:give_glavenusite`.

## Blocs d'apparition
- Le preset `natural` de Cobblemon n'autorise l'apparition que sur les blocs du tag `#cobblemon:natural`. Le sol des
  Wasteland de Biomes O' Plenty (`biomesoplenty:dried_salt`) n'en faisait pas partie : le mod l'ajoute au tag
  (entrée facultative, sans effet sans Biomes O' Plenty), ce qui débloque Deviljho et toutes les apparitions
  « naturelles » des Wasteland.

# Zamtrios et la lignée Magala (3.1.0)

D'après le cahier des charges « CobblePulse-Ecology — 4 Fakemons ». Numéros 1054 à 1057 (à la suite de Deviljho et
Glavenus, catégorie Monster Hunter ; en 3.2.0 toute la catégorie Monster Hunter a été renumérotée 1052-1057, juste
après Guillopard, au lieu de 11231-11236). Écarts assumés avec le cahier : version 3.1.0 (le mod était déjà en 3.0.0),
identifiants Cobblemon sans tiret bas (`zamtrios`, `goremagala`, `chaoticgoremagala`, `shagarumagala`, comme toutes
les espèces ; les noms affichés restent « Gore Magala »…), pas de dépendance obligatoire à Cobblepulse-utils 1.2.0,
pas encore de cris sonores (animation de cri seulement), movepools refaits avec de vraies capacités (les capacités
inventées de la fiche — Jugement Céleste, Frénésie Impure… — sont remplacées par des capacités officielles proches),
textures en 1024x512 / 256x256 au lieu de 64/128 (le modèle fourni fait plus de 100 unités de long). Le biome
`terralith:shadow_lands` n'existe pas : Gore Magala utilise les Moonlight Grove / Valley de Terralith à la place.

## Zamtrios (n° 1054, Eau / Glace)
- 2,9 m, 215 kg, total 515 (PV 105, Att 100, Déf 95, Att Spé 75, Déf Spé 80, Vit 60), +2 PV. Talents **Toison
  Épaisse**, **Prognathe**, caché **Glissade**. Taux de capture 75, 50 % mâles, groupes Aquatique 1 et Monstre,
  20 cycles. Nage et respire sous l'eau.
- Trois formes (caractéristique d'espèce `zamtrios_form` = `normal` / `armor` / `inflated`) :
  - **Armure de Glace** (forme du monde et de combat) : PV 105, Att 120, Déf 125, Att Spé 70, Déf Spé 85, Vit 40.
    Dans le monde, le mod la met automatiquement à tout Zamtrios (sauvage ou sorti par un dresseur) qui se trouve dans
    un biome gelé — là où il neige à sa hauteur — et la retire ailleurs (vérification toutes les 2 s, hors combat).
    En combat, un Zamtrios normal la prend dès qu'il utilise une capacité Glace. Les pics de glace luisent la nuit
    (couche émissive), et s'éteignent quand il dort.
  - **Gonflée** (combat uniquement) : PV 105, Att 90, Déf 115, Att Spé 85, Déf Spé 115, Vit 25. Prise à mi-PV ou
    moins, ou après Stockage ; elle reste jusqu'à la fin du combat (même après un changement). Le modèle devient une
    énorme boule (sac gonflé), la tête et les pattes dépassent.
  - Mécanique : une condition d'espèce Showdown (`mega_showdown/showdown/conditions/zamtrios.js`, ses gestionnaires
    s'appliquent à tout Zamtrios quel que soit son talent) change la forme (changement permanent qui garde le talent
    du Pokémon) ; le registre `battle_form` de Mega Showdown en fait l'aspect côté Cobblemon, remis à `normal` à la
    fin du combat (puis le biome décide).
- Capacités par niveau (fortes, moyennes et faibles) : 1 Trempette, Charge, Poudreuse, Pistolet à O ; 5 Morsure ;
  9 Grincement ; 12 Armure ; 15 Vent Glace ; 18 Aqua-Jet ; 21 Stockage, Avale, Relâche ; 24 Crocs Givre ; 27 Buée
  Noire ; 30 Roulade ; 33 Aqua-Brèche ; 36 Laser Glace ; 39 Mâchouille ; 42 Tacle Lourd ; 45 Hydrocanon ; 48 Chute
  Glace ; 52 Séisme ; 56 Blizzard ; 60 Vague à Lame ; 64 Glaciation. CT, œufs et Maître des capacités dans le fichier.
- Apparitions (**rare**, niveau 35-55) : sous l'eau des océans gelés (en armure), des océans froids (normal), et à
  terre sur les plages enneigées, les pics de glace et les rivières gelées (en armure, ×1,5 sous la pluie).
  Butin : glace compactée, cabillaud, Glace Éternelle (15 %).
- Modèle (3.1.1, détaillé en 3.1.2 d'après la planche de concept) : refait d'après les images de référence de Kevin,
  sur le squelette du modèle fourni (mêmes os, mêmes pivots : ses animations s'appliquent toujours). Grosse tête
  ronde de requin (front haut, museau obtus, arcades sourcilières, œil blanc lumineux, ouïes, lèvre rose bordée de
  dents, mâchoire et gorge pâles prolongées par deux lames blanches vers l'arrière), crête dentelée de plaques à
  pointe brun-rouge sur le crâne, la nuque, le dos et toute la queue, double rangée de grandes écailles le long de
  l'échine, corps voûté à grande nageoire dorsale en faucille (bord d'attaque turquoise, moitié arrière
  vert-jaune-orange, nervures), pattes avant écartées portant une nageoire d'avant-bras en plumes d'écailles
  superposées, griffes noires, queue terminée par une nageoire caudale verticale et frangée dessous d'une nageoire
  dorée nervurée ; peau bleu-sarcelle couverte d'écailles en losange qui se chevauchent (reflets cyan, plus grandes
  sur le dos, dos plus sombre), flancs bas olive puis dorés, queue virant à l'olive doré, ventre crème lavande à
  plaques transversales. Armure de Glace : peau givrée (le turquoise reste visible, neige sur le dessus), masque de
  glace sur le crâne, énorme corne de glace en avant du museau, crête de glace sur la tête, collerettes de glace
  sur les joues, épines latérales, couronne de longues épines effilées sur le dos, nageoire dorsale gainée, épaules,
  avant-bras, cuisses et queue givrés ; chaque cristal est blanc bleuté à pointe blanche, veiné d'une strie bleu
  sombre, et la glace luit le long de ses veines (éteinte quand il dort). Forme Gonflée (refaite en 3.1.2 d'après
  la capture du jeu) : une énorme poche en forme de pouf, peau tendue brun-mauve (rides d'étirement, plis sous le
  corps, veines violettes, le rose de la gueule sous la mâchoire), plus large en bas et inclinée vers l'arrière ;
  Zamtrios est couché dessus, la tête posée sur la pente avant, les pattes avant ramenées vers l'avant avec les
  griffes à côté de la tête ; quand il est K.O., la poche se vide et le corps redescend au sol.
  Chromatique bleu-violet à nageoires dorées, glace lavande. Les yeux luisent aussi (éteints au sommeil). Animations
  fournies converties (attente, marche, course, sommeil, K.O. dressé en rugissant puis retourné, cri avec onde de
  choc de neige au sol) ; écrites : attente de combat, morsure (physique), jet de glace (spéciale), piétinement
  (statut), nage. Forme Gonflée : sa propre série (balancement, plaquage, jet d'eau, roulade, K.O. qui se dégonfle).
- 3.1.3 : le modèle était enfoncé dans le sol en jeu (environ 2 blocs : mâchoire, pattes et griffes sous terre,
  portrait d'équipe vide, résumé décalé vers le bas) parce que l'os racine `zamtrios` avait son pivot à 35 de haut,
  ce que Cobblemon ignore ; pivot ramené au sol (comme tous les autres modèles, le validateur le vérifie désormais).
  Animations revues avec un sol opaque : les pattes arrière et la queue ne passent plus sous terre pendant la
  morsure et le jet de glace (la tête se cabre au lieu du corps, la queue se lève), le plaquage de la forme Gonflée
  bascule moins vers l'avant.

## Gore Magala (n° 1055, Ténèbres / Dragon, légendaire)
- 4,2 m, 230 kg, total 580 (PV 95, Att 115, Déf 85, Att Spé 115, Déf Spé 85, Vit 85), +1 Att +1 Att Spé. Talents
  **Corps Maudit**, **Tension**, caché **Infiltration**. Capture 5, asexué, groupe Inconnu, 30 cycles. Nocturne
  (dort le jour).
- **Mode Furie** (forme de combat, aspect `magala_frenzy`) : à mi-PV ou moins, ses cornes (repliées le long de la
  face hors furie) se déploient vers le haut et luisent en violet, ses crocs s'écartent, des plaques et la fourrure
  virent au violet, les nervures des ailes luisent ; PV 95, Att 130, Déf 75, Att Spé 130, Déf Spé 75, Vit 95.
- Évolution au niveau 69 : en **Shagaru Magala** s'il n'y a pas de Shagaru Magala dans l'équipe, en **Gore Magala du
  Chaos** s'il y en a un (conditions `party_member`).
- Apparitions (**ultra-rare**, niveau 48-65, étiquettes `monster_hunter` et `legendary`) : forêts sombres, bosquets
  (grove), Moonlight Grove / Valley de Terralith, la nuit ou pendant un orage ; et dans les Deep Dark à toute heure.
- Modèle (refait en 3.2.0 d'après le rendu de Monster Hunter World et la description du wiki) : six membres comme
  dans le jeu, deux pattes avant sous le poitrail, deux pattes arrière, et deux grandes ailes-bras partant du dos dont
  les énormes griffes à pointe dorée (avec pouce opposable) se posent au sol devant les pattes avant ; allure de
  wyverne quadrupède à la Nargacuga ; exosquelette noir à reflets bleu nuit (écailles bordées de gris-bleu), aucun œil
  (masque lisse), cornes repliées le long de la face et crocs (plaques de l'exosquelette) repliés contre la mâchoire,
  qui passent pour l'armure du visage ; ailes repliées en cape de fourrure noire en lambeaux le long des flancs,
  crinière de fourrure sur le cou et les épaules, queue bordée d'épines pâles. En combat, il prend la pose du rendu :
  griffes des ailes levées à hauteur de tête, ailes de fourrure dressées. Chromatique gris cendre, furie sarcelle.
- 3.2.1 (Gore Magala seulement, d'après les rendus de MH Rise / World et une sculpture) : grandes écailles qui se
  chevauchent, bordées de gris-bleu ; cou plus arqué ; rangées de plaques sur le cou et le dos ; collerette de pointes
  derrière la mâchoire, crocs plus longs ; pattes plus épaisses (genouillère, griffes plus longues) ; arête de plaques
  sur l'avant-bras des ailes ; frange de pointes dentelée le long de la queue ; lambeaux de la cape plus irréguliers.
  En Mode Furie : cornes dressées qui se recourbent vers l'avant, pointes roses ; le bord des écailles du dessus et un
  réseau de nervures dans les ailes luisent en violet. Comportement (descriptions d'écologie et d'attaques) : au repos,
  aveugle, il balaie lentement l'air de la tête et ses ailes-cape frémissent (il sent ses proies avec les écailles de
  ses ailes) ; attaque physique = « Grand Écrasement » (cri, se dresse sur ses pattes arrière griffes en l'air, les
  abat devant lui) ; attaque spéciale = souffle explosif (tête levée sur sa droite, mâchoire ouverte balayée de droite
  à gauche). Gore Magala du Chaos et Shagaru Magala inchangés.
- 3.2.2 (Gore Magala seulement, d'après des captures du jeu) : tête longue et étroite en fer de lance, portée bas,
  carène de plaques au milieu de la face (reflet bleu sur le front), plaques étagées sur les côtés ; griffes rouge
  sombre (ailes et pattes) ; deux grandes griffes recourbées rouges à chaque coude ; les ailes-bras forment une arche
  au-dessus de lui, griffes posées loin de chaque côté, membrane repliée sous l'avant-bras (réseau violet lumineux en
  Furie) ; pattes avant écartées ; en Furie, antennes violettes dressées droites, à peine recourbées.
- 3.3.0 (Gore Magala seulement, refait d'après le modèle détaillé fourni par Kevin et ses précisions) : proportions
  relevées sur ce modèle (10 000 faces, ramené à l'échelle 0,43) : corps profond porté haut sur quatre pattes en
  colonnes, cou court et épais, grosse tête tenue en avant (abaissée quand il chasse), longue queue hérissée de pointes
  sur les côtés, le dessus et le dessous, barbe de pointes sous la mâchoire, cornes enracinées sur l'avant de la face
  (couchées le long de la tête au calme, dressées en Furie). Les ailes sont de vraies toiles : un bras à trois os
  (bras, avant-bras, main) et quatre doigts qui tendent la membrane de fourrure noire. Repliées (« il en fait des
  épaules »), le poignet repose sur l'épaule et ses quatre longues griffes rouges retombent par-dessus, comme sur
  le rendu de MH4, les doigts couchés vers l'arrière en cape sur le flanc ; en combat elles s'ouvrent en tente, les
  griffes plantées au sol loin de chaque côté ; au cri, déployées en grand comme sur le modèle (membrane du bras au
  flanc comprise) ; levées au-dessus de la tête pour le Grand Écrasement puis abattues devant lui ; à demi ouvertes,
  griffes au sol près de la tête, pour le souffle. Poses des ailes calculées (cinématique inverse) dans
  `tools/models/species/goremagala.py`, module propre au Gore Magala (le Chaos et Shagaru ne changent pas). Pose calme
  à part pour le portrait d'équipe et le résumé.
- 3.3.1 (Gore Magala) : ailes repliées corrigées (Kevin : « t'as mis les griffes en l'air ») : le bras replié forme
  l'épaule, le poignet se loge sur le côté de l'épaule sous la ligne du dos et les quatre longues griffes rouges
  pendent le long de l'épaule, pointes recourbées vers l'avant, comme sur le rendu de MH4.
- 3.4.0 (Gore Magala, ailes refaites d'après les indications et images de Kevin) : repliées, le poignet se pose sur
  l'épaule juste au-dessus de l'articulation de la patte avant, les trois grandes griffes rouges recourbées dessus
  (elles ne se lèvent que quand il s'en sert) ; la voile, rétractée (80 %), couvre tout le flanc comme une cape, du
  dos jusqu'à la ligne du ventre et jusqu'aux hanches, et se déploie au fur et à mesure qu'il ouvre les ailes. La
  voile longe toute l'aile en deux parties liées au coude : une entre le bras et le dos, une entre l'avant-bras et
  le bout de l'aile. Griffes posées (combat, Grand Écrasement, souffle) : plantées bien plus loin que la tête, bras
  tendus, voiles dressées vers le ciel. **Vol** activé : les bras restent repliés (griffes sur les épaules), seules
  les voiles s'étendent sur les côtés et battent. Membres et corps arrondis (sections octogonales), voile écailleuse
  (coutures sombres, violettes en Furie). Technique : la voile est découpée en bandes, chacune tournée entre ses
  deux bords, pour rester continue dans toutes les poses.
- 3.5.0 (Gore Magala, d'après la vidéo comparative Wilds / Sunbreak de Kevin) : voiles en cape de fourrure
  duveteuse (mèches de fourrure anthracite à reflets argentés superposées sur l'extérieur), dessous écailleux
  bleu-gris pâle visible quand elles s'ouvrent ; corps et membres moins cubiques (sections à 12 pans).
- 3.5.1 (Gore Magala, vidéo 0:17-0:24) : griffes posées en larges arches, bras d'aile partant à l'horizontale
  de l'épaule puis redescendant loin sur les côtés, griffes plantées un peu en avant de la tête, voiles dressées
  derrière ; crochets rouges empilés sur le dessus des coudes (visibles aussi ailes repliées).
- 3.6.0 (Gore Magala) : griffes posées = les 3 griffes de chaque main à plat au sol (main tenue de niveau), et elles
  y restent pendant toute la pose de combat. Animations plus vivantes : en combat les antennes se déploient et
  frémissent (aussi au cri, à l'attaque, au souffle et au statut), la tête balaie l'air bas d'un côté à l'autre
  avec un claquement de mâchoire, le poids passe d'une griffe à l'autre, les voiles ondulent, la queue fouette ;
  cri avec recul préparatoire puis cabrage, ailes déployées qui frémissent ; Grand Écrasement avec secousse à
  l'impact ; souffle avec la queue qui contrebalance la tête.
- 3.6.1 (Gore Magala) : quand il déploie ses antennes (combat, cri, attaques, statut), elles passent au rose-magenta
  lumineux et des lignes magenta s'allument sur le cou, le poitrail, les pattes avant et sous les bras des ailes (calque
  émissif ajouté à la forme normale) ; au calme, antennes sombres repliées et pas de lignes. Antennes de Furie aussi en
  magenta vif (images du jeu).
- 3.7.0 (Gore Magala, revu dans Blockbench avec Kevin) : grand os de la voile sur son bord extérieur, de
  l'articulation des griffes au bout de la voile, souple et articulé (4 segments à nœuds, chacun son os, qui ondulent
  en combat, au cri et en vol), terminé par un crochet. En combat, à l'attaque physique et au souffle, l'os part en
  longue diagonale vers le haut et l'extérieur et les voiles s'étendent sur les côtés en mur face au joueur ; griffes
  à plat au sol aussi au Grand Écrasement. K.O. : il lève la tête en criant, antennes sorties, puis les pattes
  cèdent, il s'écroule sur le ventre en roulant un peu sur le flanc, ailes affaissées, antennes toujours sorties.
  Sommeil : vraiment couché sur le ventre, pattes repliées, voiles drapées au sol, tête posée, queue enroulée.
  Correctif : angles des ailes rendus continus (plus de tour complet parasite entre deux images clés en vol et au K.O.,
  visible dans Blockbench et en jeu).
- 3.7.1 (Gore Magala) : les voiles en mur ne se séparent plus du corps : leur bord intérieur va du poignet au haut du
  dos, et elles se tendent du dos jusqu'au grand os en diagonale (combat, attaque physique, souffle).
- 3.8.0 (Gore Magala du Chaos et Shagaru Magala, d'après les images de Kevin) : refaits sur le modèle du Gore Magala
  (même corps, membres arrondis, ailes à voiles, grand os souple, mêmes animations : mur de voiles en combat, vol,
  K.O., sommeil). Shagaru : corps blanc-gris à touches dorées, couronne de cornes (grand croissant + deux cornes
  rabattues), deux yeux (clignent, se ferment au sommeil et au K.O.), voiles en étoile couvertes d'écailles plumeuses
  vert-crème, bords hérissés de pointes dorées, griffes violet-rose. Chaos : moitié gauche Gore en Furie (fourrure
  noire, lueur violette, antenne magenta dressée, croc ouvert), moitié droite Shagaru (corne en croissant, œil, voile
  dorée en étoile). Tailles recalées sur le nouveau modèle (hauteur et hitbox inchangées en jeu).
- 3.8.1 (d'après Kevin et la planche de concept du Gore Magala du Chaos) : le Chaos a raté sa mue. Son antenne Gore et
  le violet ne s'activent qu'en combat comme sur un Gore normal (antenne magenta qui sort en se dressant, lignes
  violettes). Son aile « blanche » garde surtout les couleurs du Gore (fourrure noire en lambeaux) avec une bande de
  fourrure dorée le long du bras ; bras d'aile sombre tacheté de jaune, rangée de pointes dorées, fissures dorées
  de la corne le long de la tête et du cou jusqu'au bras ; corne sombre à la racine plus basse. Les cornes (Chaos et
  Shagaru) s'arrondissent à la racine puis montent droit avec un léger arrondi vers l'avant ; cornes du Shagaru plus
  sombres. Gore Magala : l'antenne n'apparaît plus du tout au calme, elle sort en se dressant à l'activation.
- 3.8.2 (Shagaru et côté Shagaru du Chaos, capture du jeu) : une grande corne sombre et épaisse de chaque côté Shagaru,
  plantée à la place de l'antenne du Gore (les antennes sont devenues des cornes), qui s'arrondit à la racine puis monte
  droit ; yeux en petite fente orangée inclinée sous la corne, enfoncés sous une arcade ; collerette de pointes dorées
  derrière la tête et gueule violette du Shagaru.

## Gore Magala du Chaos (n° 1056, Ténèbres / Dragon, légendaire)
- 4,4 m, 245 kg, total 620 (PV 95, Att 150, Déf 80, Att Spé 110, Déf Spé 75, Vit 110), +3 Att. Talents **Corps
  Maudit**, **Téméraire**, caché **Infiltration**. Capture 3, 35 cycles. Pas d'apparition sauvage.
- Modèle asymétrique (même squelette à six membres) : moitié droite dorée de Shagaru (corne en croissant, seul œil),
  moitié gauche noire de Gore Magala en furie (corne dressée violette, croc ouvert, cape de fourrure, aveugle) ; lueur
  bicolore or / violet.

## Shagaru Magala (n° 1057, Dragon / Fée, légendaire)
- 4,6 m, 250 kg, total 650 (PV 105, Att 110, Déf 100, Att Spé 145, Déf Spé 105, Vit 85), +3 Att Spé. Capture 3,
  40 cycles. Diurne, vole. Pas d'apparition sauvage.
- Talents : **Écailles en furie dorée** (signature) — +25 % aux capacités Dragon et Fée, chances d'effet doublées
  pour ses attaques de lumière (Pouvoir Lunaire, Éclat Magique, Luminocanon, Lumière du Néant…), mais +25 % de dégâts
  subis des capacités Poison et de l'empoisonnement ; caché **Multiécaille**.
- Modèle (même squelette à six membres) : écailles or blanc, ailes dorées à nervures lumineuses, deux grandes cornes
  en croissant, deux yeux lumineux (fermés quand il dort), épines dorées sur le dos et la queue. Animations de vol (sur place et en déplacement). Chromatique platine
  et bleu pâle.

## Commun
- Animations de la lignée : attente, marche (griffes des ailes et pattes en diagonale, pattes avant avec la griffe de
  leur côté), attente de combat (griffes levées, ailes dressées), cri (cou dressé, griffes levées, ailes grandes
  ouvertes), attaque physique (se cabre griffes en l'air puis les abat et mord), spéciale (tête rejetée puis
  projection), statut (secoue ses ailes), K.O. (tête en l'air, dernier cri tremblant, s'effondre sur le flanc),
  sommeil (couché, pattes repliées, yeux fermés).
- Pokédex (3.2.0) : titre de la catégorie « Monster Hunter » et nom « Normal » de la forme de base des espèces à
  plusieurs formes (Deviljho, Glavenus, Zamtrios, Gore Magala) ajoutés ; le validateur vérifie ces clés.
- Icônes 32x32 : `assets/cobblepulse_ecology/textures/gui/sprites/<espèce>.png`.
- Tests Showdown : `tools/showdown/test_magala_zamtrios.js` (formes de Zamtrios, Mode Furie, Écailles en furie dorée).
