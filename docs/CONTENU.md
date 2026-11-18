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
- Catégorie **Monster Hunter** : Deviljho (méga : Deviljho Carnage, Deviljhonite) et Glavenus (méga : Glavenus
  Lame-Chaos, Glavenusite), voir plus bas ; Pokédex « Monster Hunter » ajouté au national
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

## Monster Hunter : Deviljho (n° 11231, Dragon / Ténèbres)
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
- Fichiers : `models/11231_deviljho/deviljho_carnage.geo.json`, poser et animations `deviljho_carnage`,
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

# Glavenus (n° 11232) et Glavenus Lame-Chaos

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
- Fichiers : `models/11232_glavenus/glavenus.geo.json` et `glavenus_lame_chaos.geo.json`, posers, animations,
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
